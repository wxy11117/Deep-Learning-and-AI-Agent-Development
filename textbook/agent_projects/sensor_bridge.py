"""Connect the saved sensor experiment, an explicit rule, a manual and a work-order proposal."""
from pathlib import Path
import sys,json,hashlib,tempfile
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'_ml_deps'))
import numpy as np
from core import Runner,ReplayModel,Reply,call
from knowledge import KnowledgeBase,check_answer
from workflow import WorkOrders

def main():
    path=ROOT/'projects/results/sensor.npz';data=np.load(path)
    disagreements=np.abs(data['raw']-data['pred'])
    threshold=10.0
    candidates=np.flatnonzero(disagreements>threshold)
    if not len(candidates):raise RuntimeError('No sample meets this teaching review rule')
    i=int(candidates[0])
    reading={'window_index':i,'measurement_cm':float(data['raw'][i]),'estimate_cm':float(data['pred'][i]),
             'difference_cm':float(disagreements[i]),'rule_threshold_cm':threshold,
             'source_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'data_kind':'simulated trajectories; saved trained-CNN predictions'}
    manual={'id':'S01','version':'2.0','title':'S1 估计差异复核',
            'text':'教学装置 S1 在测量与估计差异超过 10 cm 时进入复核队列。先检查原始轨迹和缺失标记，再检查安装与采样状态；确认原因后再决定处理动作。该阈值为教学配置。'}
    kb=KnowledgeBase([manual])
    final={'answer':'先检查原始轨迹和缺失标记，再检查安装与采样状态。','abstain':False,
           'citations':[{'id':'S01','version':'2.0','quote':'先检查原始轨迹和缺失标记，再检查安装与采样状态'}]}
    model=ReplayModel([call('search_manual',{'query':'估计差异复核','version':'2.0','top_k':1},'s1'),
                       call('read_manual',{'doc_id':'S01','version':'2.0'},'s2'),Reply(text=json.dumps(final,ensure_ascii=False))])
    result=Runner(model,kb.tools()).run('教学任务估计差异超过配置阈值，请查询复核步骤。')
    check_answer(json.loads(result['text']),result['history'])
    with tempfile.TemporaryDirectory() as folder:
        path_db=Path(folder)/'bridge.sqlite3';orders=WorkOrders(path_db)
        proposal=orders.propose('T001','resolved')
        state={'phase':'awaiting_approval','sensor_reading':reading,'proposal':proposal,'manual_evidence':final['citations']}
        orders.save('sensor-review-1',state);orders.close()
        resumed=WorkOrders(path_db);restored=resumed.load('sensor-review-1')
        unchanged=resumed.get('T001')['status']=='open'
        event_count=resumed.db.execute('SELECT COUNT(*) FROM events').fetchone()[0];resumed.close()
    report={'mode':'offline_replay','reading':reading,'manual':manual,'knowledge_trace':result,
            'checkpoint_restored':restored==state,'state':restored,'ticket_still_open':unchanged,'business_write_events':event_count,
            'meaning':'Draft and waiting state saved. Approval and status commit are exercised separately in chapter 42.'}
    out=ROOT/'agent_projects/results/sensor_bridge.json';out.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'reading':reading,'checkpoint_restored':report['checkpoint_restored'],'ticket_still_open':unchanged,'business_write_events':event_count},ensure_ascii=False))
if __name__=='__main__':main()
