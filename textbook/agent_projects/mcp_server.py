"""Minimal local stdio MCP teaching server, protocol 2025-11-25.

Supports initialization, ping, tools/list and two read-only tools.
Not a production server: no remote transport, auth, cancellation or conformance claim.
"""
import json,sys
from core import validate,ContractError
from knowledge import KnowledgeBase
VERSION='2025-11-25'

class Server:
    def __init__(self):
        self.tools={t.name:t for t in KnowledgeBase().tools()};self.initialized=False;self.ready=False
    def handle(self,message):
        if not isinstance(message,dict):return self.error(None,-32600,'Invalid Request')
        rid=message.get('id');method=message.get('method')
        if message.get('jsonrpc')!='2.0' or not isinstance(method,str):return self.error(rid,-32600,'Invalid Request')
        if 'id' not in message:
            if method=='notifications/initialized' and self.initialized:self.ready=True
            return None
        if type(rid) not in (str,int):return self.error(None,-32600,'Invalid id')
        params=message.get('params',{})
        if not isinstance(params,dict):return self.error(rid,-32602,'Invalid params')
        if method=='initialize':
            if self.initialized:return self.error(rid,-32600,'Already initialized')
            if not isinstance(params.get('protocolVersion'),str) or not isinstance(params.get('capabilities'),dict) or not isinstance(params.get('clientInfo'),dict):return self.error(rid,-32602,'Missing initialization fields')
            self.initialized=True
            return self.result(rid,{'protocolVersion':VERSION,'capabilities':{'tools':{'listChanged':False}},'serverInfo':{'name':'textbook-readonly-manual','version':'1.0.0'}})
        if method=='ping':return self.result(rid,{})
        if not self.ready:return self.error(rid,-32002,'Initialization required')
        if method=='tools/list':
            return self.result(rid,{'tools':[{'name':t.name,'description':t.description,'inputSchema':t.schema} for t in self.tools.values()]})
        if method=='tools/call':
            tool=self.tools.get(params.get('name'))
            if tool is None:return self.error(rid,-32602,'Unknown tool')
            args=params.get('arguments',{})
            try:
                validate(args,tool.schema)
                value=tool.function(**args)
                return self.result(rid,{'content':[{'type':'text','text':json.dumps(value,ensure_ascii=False)}],'isError':False})
            except (ContractError,ValueError,KeyError) as e:
                return self.result(rid,{'content':[{'type':'text','text':str(e)}],'isError':True})
        return self.error(rid,-32601,'Method not found')
    @staticmethod
    def result(rid,value):return {'jsonrpc':'2.0','id':rid,'result':value}
    @staticmethod
    def error(rid,code,message):return {'jsonrpc':'2.0','id':rid,'error':{'code':code,'message':message}}

def main():
    server=Server()
    for line in sys.stdin.buffer:
        try:reply=server.handle(json.loads(line))
        except (json.JSONDecodeError,UnicodeDecodeError):reply=server.error(None,-32700,'Parse error')
        if reply is not None:
            sys.stdout.buffer.write((json.dumps(reply,ensure_ascii=False)+'\n').encode('utf-8'));sys.stdout.buffer.flush()
if __name__=='__main__':main()
