"""Optional Anthropic Messages API adapter. Live calls require explicit CLI --live."""
import os,json,urllib.request,urllib.error
from core import Reply,ContractError

class AnthropicModel:
    mode='live_api'
    def __init__(self,system,model=None):
        self.key=os.environ.get('ANTHROPIC_API_KEY')
        self.model=model or os.environ.get('ANTHROPIC_MODEL')
        if not self.key or not self.model:raise ValueError('Set ANTHROPIC_API_KEY and ANTHROPIC_MODEL; never store keys in book files.')
        self.system=system
    def payload(self,history,tools):
        messages=[]
        for item in history:
            if item['role']=='user':messages.append({'role':'user','content':item['text']})
            elif item['role']=='assistant':
                blocks=item.get('native')
                if blocks is None:
                    blocks=([{'type':'text','text':item['text']}] if item['text'] else [])
                    blocks += [{'type':'tool_use','id':c['id'],'name':c['name'],'input':c['arguments']} for c in item.get('calls',[])]
                messages.append({'role':'assistant','content':blocks})
            else:
                blocks=[{'type':'tool_result','tool_use_id':r['id'],'is_error':not r['ok'],
                    'content':json.dumps(r.get('value') if r['ok'] else {'error':r['error']},ensure_ascii=False)} for r in item['results']]
                messages.append({'role':'user','content':blocks})
        return {'model':self.model,'max_tokens':1200,'system':self.system,'messages':messages,'tools':tools}
    @staticmethod
    def decode(data):
        if data.get('stop_reason') not in ('tool_use','end_turn'):raise ContractError('response incomplete: '+str(data.get('stop_reason')))
        blocks=data['content']
        calls=[{'id':b['id'],'name':b['name'],'arguments':b['input']} for b in blocks if b['type']=='tool_use']
        text='\n'.join(b['text'] for b in blocks if b['type']=='text')
        return Reply(calls=calls,text=text,native=blocks,usage=data.get('usage',{}))
    def respond(self,history,tools):
        req=urllib.request.Request('https://api.anthropic.com/v1/messages',
          data=json.dumps(self.payload(history,tools),ensure_ascii=False).encode('utf-8'),
          headers={'Content-Type':'application/json','x-api-key':self.key,'anthropic-version':'2023-06-01'},method='POST')
        try:
            with urllib.request.urlopen(req,timeout=60) as resp:data=json.load(resp)
        except urllib.error.HTTPError as e:
            # No secret-bearing request dump and no automatic potentially billed retry.
            raise RuntimeError(f'Model HTTP {e.code}; inspect provider request logs and retry policy.') from None
        return self.decode(data)
