"""DeepSeek non-thinking tool calls. Secrets are never written into a trace."""
from pathlib import Path
import os,json,time,subprocess,urllib.request,urllib.error
from core import Reply,ContractError

ROOT=Path(__file__).resolve().parents[1]

def load_key():
    key=os.getenv('DEEPSEEK_API_KEY')
    if key:return key.strip()
    credential=ROOT/'_local/deepseek.credential.xml'
    if os.name=='nt' and credential.is_file():
        # PowerShell decrypts DPAPI data for this Windows user. Capture; never print.
        literal=str(credential).replace("'","''")
        command=f"$c=Import-Clixml -LiteralPath '{literal}'; [Console]::Write($c.GetNetworkCredential().Password)"
        response=subprocess.run(['powershell.exe','-NoProfile','-Command',command],capture_output=True,text=True,check=False)
        if response.returncode==0 and response.stdout.strip():return response.stdout.strip()
    raise RuntimeError('Configure DEEPSEEK_API_KEY or run configure_deepseek.ps1 locally.')

class DeepSeekModel:
    mode='live_api'
    def __init__(self,system,model=None,max_requests=100):
        self.key=load_key();self.system=system
        self.model=model or os.getenv('DEEPSEEK_MODEL','deepseek-flash')
        self.endpoint='https://api.deepseek.com/chat/completions'
        self.requests=[];self.max_requests=max_requests
    def payload(self,history,tools):
        messages=[{'role':'system','content':self.system}]
        for event in history:
            if event['role']=='user':messages.append({'role':'user','content':event['text']})
            elif event['role']=='assistant':
                message={'role':'assistant','content':event.get('text') or None}
                if event.get('calls'):
                    message['tool_calls']=[{'id':c['id'],'type':'function','function':{'name':c['name'],'arguments':json.dumps(c['arguments'],ensure_ascii=False)}} for c in event['calls']]
                messages.append(message)
            else:
                for result in event['results']:
                    messages.append({'role':'tool','tool_call_id':result['id'],'content':json.dumps(result,ensure_ascii=False,allow_nan=False)})
        return {'model':self.model,'messages':messages,
                'tools':[{'type':'function','function':{'name':t['name'],'description':t['description'],'parameters':t['input_schema']}} for t in tools],
                'temperature':0,'max_tokens':900,'thinking':{'type':'disabled'},'stream':False}
    @staticmethod
    def decode(data):
        choice=data['choices'][0]
        if choice['finish_reason'] not in ('stop','tool_calls'):
            raise ContractError('Incomplete model response: '+str(choice['finish_reason']))
        message=choice['message'];calls=[]
        for item in message.get('tool_calls') or []:
            calls.append({'id':item['id'],'name':item['function']['name'],'arguments':json.loads(item['function']['arguments'])})
        return Reply(calls=calls,text=message.get('content') or '',native=message,usage=data.get('usage',{}))
    def respond(self,history,tools):
        if len(self.requests)>=self.max_requests:raise ContractError('Provider request budget exhausted')
        payload=self.payload(history,tools)
        raw=json.dumps(payload,ensure_ascii=False,allow_nan=False).encode('utf-8')
        if len(raw)>65000:raise ContractError('Request exceeds teaching context budget')
        req=urllib.request.Request(self.endpoint,data=raw,headers={'Authorization':'Bearer '+self.key,'Content-Type':'application/json'},method='POST')
        start=time.perf_counter();record={'requested_model':self.model,'started_at':time.strftime('%Y-%m-%dT%H:%M:%S%z'),'request_bytes':len(raw)}
        self.requests.append(record)
        try:
            with urllib.request.urlopen(req,timeout=60) as response:data=json.load(response)
        except urllib.error.HTTPError as exc:
            record.update({'status':'http_error','http_status':exc.code,'elapsed_ms':round((time.perf_counter()-start)*1000,3)})
            raise RuntimeError('DeepSeek HTTP '+str(exc.code)) from None
        except (urllib.error.URLError,TimeoutError):
            record.update({'status':'network_error','elapsed_ms':round((time.perf_counter()-start)*1000,3)})
            raise RuntimeError('DeepSeek network error; request outcome unknown') from None
        record.update({'status':'received','response_id':data.get('id'),'returned_model':data.get('model'),
                       'usage':data.get('usage',{}),'elapsed_ms':round((time.perf_counter()-start)*1000,3),
                       'finish_reason':data.get('choices',[{}])[0].get('finish_reason')})
        return self.decode(data)
