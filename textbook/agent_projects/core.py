"""A bounded, observable tool loop. Replay policies are test doubles, not LLMs."""
from dataclasses import dataclass, field
from typing import Any, Protocol, Callable
import json,time,hashlib

class ContractError(ValueError): pass

def validate(value,schema,path='$'):
    """Deliberately small JSON Schema subset used by this book's tools."""
    kind=schema.get('type')
    checks={'object':lambda x:isinstance(x,dict),'array':lambda x:isinstance(x,list),
            'string':lambda x:isinstance(x,str),'integer':lambda x:type(x) is int,
            'number':lambda x:type(x) in (int,float),'boolean':lambda x:type(x) is bool}
    if kind not in checks or not checks[kind](value):raise ContractError(f'{path}: expected {kind}')
    if 'enum' in schema and value not in schema['enum']:raise ContractError(f'{path}: enum')
    if kind=='object':
        props=schema.get('properties',{})
        for k in schema.get('required',[]):
            if k not in value:raise ContractError(f'{path}.{k}: required')
        if schema.get('additionalProperties') is False and set(value)-set(props):raise ContractError(f'{path}: extra fields')
        for k,v in value.items():
            if k in props:validate(v,props[k],path+'.'+k)
    if kind=='array':
        if len(value)>schema.get('maxItems',100):raise ContractError(f'{path}: too many items')
        for i,v in enumerate(value):validate(v,schema['items'],f'{path}[{i}]')
    if kind=='string' and not schema.get('minLength',0)<=len(value)<=schema.get('maxLength',10000):raise ContractError(f'{path}: length')
    if kind in ('integer','number'):
        import math
        if not math.isfinite(value) or not schema.get('minimum',-float('inf'))<=value<=schema.get('maximum',float('inf')):raise ContractError(f'{path}: range')

@dataclass
class Tool:
    name:str
    description:str
    schema:dict
    function:Callable
    def public(self):return {'name':self.name,'description':self.description,'input_schema':self.schema}

@dataclass
class Reply:
    calls:list=field(default_factory=list)
    text:str=''
    native:Any=None
    usage:dict=field(default_factory=dict)

class Model(Protocol):
    mode:str
    def respond(self,history:list,tools:list)->Reply:...

class ReplayModel:
    """Author-written replies exercise the real runtime; no language understanding."""
    mode='offline_replay'
    def __init__(self,replies):self.replies=iter(replies)
    def respond(self,history,tools):return next(self.replies)

def call(name,args,call_id):return Reply(calls=[{'id':call_id,'name':name,'arguments':args}])

class Runner:
    def __init__(self,model,tools,max_turns=8,max_calls=12,result_limit=12000):
        self.model=model;self.tools={t.name:t for t in tools}
        if len(self.tools)!=len(tools):raise ValueError('duplicate tool names')
        self.max_turns=max_turns;self.max_calls=max_calls;self.result_limit=result_limit
        self.trace=[]
    def run(self,question):
        history=[{'role':'user','text':question}]; seen=set(); count=0
        self.history=history
        self.trace=[]
        for turn in range(self.max_turns):
            model_started=time.perf_counter()
            reply=self.model.respond(history,[t.public() for t in self.tools.values()])
            history.append({'role':'assistant','text':reply.text,'calls':reply.calls,'native':reply.native})
            self.trace.append({'event':'model','turn':turn,'usage':reply.usage,'mode':self.model.mode,
                'elapsed_ms':round((time.perf_counter()-model_started)*1000,3)})
            if not reply.calls:
                if not reply.text.strip():raise ContractError('empty final reply')
                return {'status':'completed','text':reply.text,'turns':turn+1,'calls':count,'history':history,'trace':self.trace}
            results=[]
            for action in reply.calls:
                count+=1
                if count>self.max_calls:raise ContractError('tool budget exhausted')
                cid=action.get('id')
                if not isinstance(cid,str) or not cid or cid in seen:raise ContractError('invalid or repeated call id')
                seen.add(cid);start=time.perf_counter()
                try:
                    tool=self.tools.get(action.get('name'))
                    if not tool:raise ContractError('unknown tool')
                    args=action.get('arguments');validate(args,tool.schema)
                    value=tool.function(**args)
                    serialized=json.dumps(value,ensure_ascii=False,allow_nan=False)
                    if len(serialized)>self.result_limit:raise ContractError('result too large; use a narrower query')
                    result={'id':cid,'ok':True,'value':value}
                except (ContractError,ValueError,KeyError,FileNotFoundError,PermissionError) as e:
                    result={'id':cid,'ok':False,'error':str(e)}
                results.append(result)
                self.trace.append({'event':'tool','turn':turn,'name':action.get('name'),'call_id':cid,
                    'ok':result['ok'],'elapsed_ms':round((time.perf_counter()-start)*1000,3),
                    'result_sha256':hashlib.sha256(json.dumps(result,ensure_ascii=False,sort_keys=True).encode()).hexdigest()})
            history.append({'role':'tool','results':results})
        raise ContractError('turn budget exhausted')

def object_schema(properties,required=None):
    return {'type':'object','properties':properties,'required':list(properties) if required is None else required,'additionalProperties':False}

TEXT={'type':'string','minLength':1,'maxLength':200}
