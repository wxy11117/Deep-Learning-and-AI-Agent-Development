"""Behavioral tests for execution boundaries and reproducible project calculations."""
import unittest,tempfile,json,math
from pathlib import Path
from decimal import Decimal
from core import *
from knowledge import *
from analysis_tools import AnalysisStore,prepare
from workflow import WorkOrders
from live_provider import AnthropicModel

class ProjectTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):prepare()
    def test_01_schema_rejects_bool_as_int(self):
        with self.assertRaises(ContractError):validate(True,{'type':'integer'})
    def test_02_schema_rejects_extra_field(self):
        with self.assertRaises(ContractError):validate({'x':1,'y':2},object_schema({'x':{'type':'integer'}}))
    def test_03_nonfinite_number(self):
        with self.assertRaises(ContractError):validate(math.inf,{'type':'number'})
    def test_04_unknown_tool_cannot_execute(self):
        run=Runner(ReplayModel([call('erase_disk',{},'1'),Reply(text='stopped')]),[]).run('test')
        self.assertFalse(run['history'][2]['results'][0]['ok'])
    def test_05_invalid_args_do_not_reach_function(self):
        seen=[];t=Tool('x','x',object_schema({'n':{'type':'integer','minimum':0}}),lambda **k:seen.append(k))
        Runner(ReplayModel([call('x',{'n':-1},'1'),Reply(text='done')]),[t]).run('test');self.assertEqual(seen,[])
    def test_06_loop_stops_at_budget(self):
        kb=KnowledgeBase();reply=call('search_manual',{'query':'日志','version':'2.0','top_k':1},'1')
        with self.assertRaisesRegex(ContractError,'turn budget'):Runner(ReplayModel([reply]),kb.tools(),max_turns=1).run('test')
    def test_07_duplicate_call_ids_rejected(self):
        with self.assertRaisesRegex(ContractError,'call id'):Runner(ReplayModel([call('x',{},'1'),call('x',{},'1')]),[]).run('test')
    def test_08_version_filter(self):
        result=KnowledgeBase().search('日志保存','2.0',3)
        self.assertTrue(result);self.assertTrue(all(x['version']=='2.0' and x['id']!='K02' for x in result))
    def test_09_unread_citation_rejected(self):
        with self.assertRaises(ContractError):check_answer({'answer':'30天','abstain':False,'citations':[{'id':'K01','version':'2.0','quote':'30 天'}]},[])
    def test_10_fake_quote_rejected(self):
        h=[{'role':'tool','results':[{'ok':True,'value':DOCUMENTS[0]}]}]
        with self.assertRaises(ContractError):check_answer({'answer':'365天','abstain':False,'citations':[{'id':'K01','version':'2.0','quote':'365 天'}]},h)
    def test_11_abstention_allowed(self):
        self.assertTrue(check_answer({'answer':'资料不足','abstain':True,'citations':[]},[]))
    def test_12_data_quality_counts(self):
        x=AnalysisStore().inspect('orders');self.assertEqual((x['raw_rows'],x['accepted_rows'],len(x['issues'])),(13,10,3))
    def test_13_money_and_refunds(self):
        x=AnalysisStore().aggregate('orders','region')['rows']
        self.assertEqual(sum(Decimal(r['revenue']) for r in x),Decimal('1470'))
        self.assertEqual(sum(Decimal(r['profit']) for r in x),Decimal('557'))
    def test_14_path_is_not_dataset_id(self):
        with self.assertRaises(ContractError):AnalysisStore().load('../../private')
    def test_15_weighted_margin(self):
        x=AnalysisStore().aggregate('orders','region')['rows'];east=next(r for r in x if r['group']=='华东')
        self.assertAlmostEqual(east['margin'],200/530)
    def test_16_approval_bound_to_payload(self):
        w=WorkOrders(':memory:');p=w.propose('T001','resolved');token=w.approve(p,now=0)
        p['target_status']='open'
        with self.assertRaises(ContractError):w.apply(p,token,'x',now=1)
        self.assertEqual(w.get('T001')['status'],'open');w.close()
    def test_17_expired_approval(self):
        w=WorkOrders(':memory:');p=w.propose('T001','resolved');token=w.approve(p,now=0)
        with self.assertRaises(ContractError):w.apply(p,token,'x',now=301)
        w.close()
    def test_18_stale_version(self):
        w=WorkOrders(':memory:');p=w.propose('T001','resolved');t=w.approve(p,now=0)
        w.db.execute("UPDATE tickets SET version=2 WHERE id='T001'");w.db.commit()
        with self.assertRaisesRegex(ContractError,'stale'):w.apply(p,t,'x',now=1)
        w.close()
    def test_19_idempotence(self):
        w=WorkOrders(':memory:');p=w.propose('T001','resolved');t=w.approve(p,now=0)
        a=w.apply(p,t,'x',now=1);b=w.apply(p,t,'x',now=2)
        self.assertFalse(a['replayed']);self.assertTrue(b['replayed']);self.assertEqual(w.get('T001')['version'],2)
        self.assertEqual(w.db.execute('SELECT COUNT(*) FROM events').fetchone()[0],1);w.close()
    def test_20_transaction_rollback(self):
        w=WorkOrders(':memory:');p=w.propose('T001','resolved');t=w.approve(p,now=0)
        with self.assertRaises(RuntimeError):w.apply(p,t,'x',now=1,simulate_crash=True)
        self.assertEqual(w.get('T001')['version'],1)
        self.assertFalse(w.apply(p,t,'x',now=2)['replayed']);w.close()
    def test_21_checkpoint_survives_connection(self):
        with tempfile.TemporaryDirectory() as tmp:
            f=Path(tmp)/'w.db';w=WorkOrders(f);w.save('r',{'phase':'awaiting_approval'});w.close()
            v=WorkOrders(f);self.assertEqual(v.load('r'),{'phase':'awaiting_approval'});v.close()
    def test_22_control_plane_not_exposed(self):
        w=WorkOrders(':memory:');self.assertEqual({t.name for t in w.tools()},{'get_ticket','propose_status'});w.close()
    def test_23_api_response_translation(self):
        fixture={'stop_reason':'tool_use','content':[{'type':'tool_use','id':'c1','name':'search_manual','input':{'query':'日志'}}],'usage':{'input_tokens':10,'output_tokens':20}}
        r=AnthropicModel.decode(fixture);self.assertEqual(r.calls[0]['id'],'c1');self.assertEqual(r.native,fixture['content'])
    def test_24_truncated_api_response_rejected(self):
        with self.assertRaises(ContractError):AnthropicModel.decode({'stop_reason':'max_tokens','content':[]})
    def test_25_analysis_cannot_skip_tools(self):
        from run_projects import analysis_evidence
        with self.assertRaises(ContractError):analysis_evidence([{'role':'assistant','text':'done','calls':[]}])
    def test_26_workflow_cannot_claim_unmade_proposal(self):
        from run_projects import workflow_proposal
        with self.assertRaises(ContractError):workflow_proposal([{'role':'assistant','text':'approved','calls':[]}])
    def test_27_conflicting_duplicate_is_not_silently_excluded(self):
        with tempfile.TemporaryDirectory() as tmp:
            file=Path(tmp)/'conflict.csv'
            file.write_text('order_id,date,region,revenue,cost\nO1,2026-01-01,A,10,5\nO1,2026-01-01,A,20,5\n',encoding='utf-8')
            store=AnalysisStore();store.allowed={'orders':file}
            with self.assertRaisesRegex(ContractError,'conflicting duplicate'):store.inspect('orders')

if __name__=='__main__':
    suite=unittest.defaultTestLoader.loadTestsFromTestCase(ProjectTests)
    result=unittest.TextTestRunner(verbosity=2).run(suite)
    output={'tests':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),'mode':'offline engineering checks; no live LLM evaluation',
      'cases':[f'test_{i:02}' for i in range(1,28)]}
    Path(__file__).with_name('results').mkdir(exist_ok=True)
    Path(__file__).with_name('results').joinpath('verification.json').write_text(json.dumps(output,ensure_ascii=False,indent=2),encoding='utf-8')
    raise SystemExit(not result.wasSuccessful())
