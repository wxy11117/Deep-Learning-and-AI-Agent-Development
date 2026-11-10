"""Integration test: launch an actual stdio subprocess and exchange protocol messages."""
from pathlib import Path
import subprocess,sys,json
ROOT=Path(__file__).resolve().parent
messages=[
 {'jsonrpc':'2.0','id':0,'method':'tools/list'},
 {'jsonrpc':'2.0','id':1,'method':'initialize','params':{'protocolVersion':'2025-11-25','capabilities':{},'clientInfo':{'name':'textbook-test','version':'1.0'}}},
 {'jsonrpc':'2.0','method':'notifications/initialized'},
 {'jsonrpc':'2.0','id':2,'method':'tools/list'},
 {'jsonrpc':'2.0','id':3,'method':'tools/call','params':{'name':'search_manual','arguments':{'query':'日志保存','version':'2.0','top_k':2}}},
 {'jsonrpc':'2.0','id':4,'method':'tools/call','params':{'name':'read_manual','arguments':{'doc_id':'K01','version':'2.0'}}},
 {'jsonrpc':'2.0','id':5,'method':'tools/call','params':{'name':'read_manual','arguments':{'doc_id':'K01','version':'1.0'}}},
 {'jsonrpc':'2.0','id':6,'method':'tools/call','params':{'name':'search_manual','arguments':{'query':'日志','version':'2.0','top_k':99}}},
 {'jsonrpc':'2.0','id':7,'method':'erase_everything','params':{}},
 {'jsonrpc':'2.0','id':8,'method':'ping'}]
wire='\n'.join(json.dumps(m,ensure_ascii=False) for m in messages)+'\n'
proc=subprocess.run([sys.executable,str(ROOT/'mcp_server.py')],input=wire.encode('utf-8'),capture_output=True,timeout=15,check=True)
responses=[json.loads(line) for line in proc.stdout.decode('utf-8').splitlines()];by_id={r['id']:r for r in responses}
checks={
 'preinit_rejected':by_id[0]['error']['code']==-32002,
 'protocol_negotiated':by_id[1]['result']['protocolVersion']=='2025-11-25',
 'discovery_two_readonly_tools':{t['name'] for t in by_id[2]['result']['tools']}=={'search_manual','read_manual'},
 'version_filtered_search':all(d['version']=='2.0' for d in json.loads(by_id[3]['result']['content'][0]['text'])),
 'read_exact_evidence':json.loads(by_id[4]['result']['content'][0]['text'])['id']=='K01',
 'invalid_version_and_range_are_tool_errors':by_id[5]['result']['isError'] and by_id[6]['result']['isError'],
 'unknown_method_is_protocol_error':by_id[7]['error']['code']==-32601,
 'ping_and_no_notification_response':by_id[8]['result']=={} and len(responses)==9}
record={'protocol':'2025-11-25','mode':'actual local stdio subprocess; no model call','checks':checks,'passed':sum(checks.values()),'requests':messages,'responses':responses}
(ROOT/'results/mcp_verification.json').write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
assert all(checks.values()),checks
print(json.dumps({'passed':sum(checks.values()),'checks':checks},ensure_ascii=False,indent=2))
