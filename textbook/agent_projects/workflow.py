"""Local SQLite work-order demo with approval binding and atomic idempotent apply."""
import sqlite3,json,hashlib,secrets,time
from pathlib import Path
from core import ContractError,Tool,object_schema,TEXT

def action_hash(ticket_id,version,status):
    return hashlib.sha256(json.dumps([ticket_id,version,status],separators=(',',':')).encode()).hexdigest()

class WorkOrders:
    def __init__(self,path):
        self.db=sqlite3.connect(path)
        self.db.executescript('''
          CREATE TABLE IF NOT EXISTS tickets(id TEXT PRIMARY KEY,version INTEGER,status TEXT);
          CREATE TABLE IF NOT EXISTS approvals(token TEXT PRIMARY KEY,digest TEXT,expires REAL,used INTEGER DEFAULT 0);
          CREATE TABLE IF NOT EXISTS events(operation_id TEXT PRIMARY KEY,digest TEXT,result TEXT);
          CREATE TABLE IF NOT EXISTS checkpoints(run_id TEXT PRIMARY KEY,state TEXT);
        ''')
        self.db.execute("INSERT OR IGNORE INTO tickets VALUES ('T001',1,'open')");self.db.commit()
    def get(self,ticket_id):
        row=self.db.execute('SELECT id,version,status FROM tickets WHERE id=?',(ticket_id,)).fetchone()
        if not row:raise ContractError('ticket not found')
        return dict(zip(('id','version','status'),row))
    def propose(self,ticket_id,target_status):
        if target_status not in ('resolved','open'):raise ContractError('unsupported status')
        t=self.get(ticket_id)
        return {'ticket_id':ticket_id,'expected_version':t['version'],'target_status':target_status,
                'digest':action_hash(ticket_id,t['version'],target_status),'requires_approval':True}
    def approve(self,proposal,now=None):
        """Called by the human/application control plane, never registered as model tool."""
        now=time.time() if now is None else now;token=secrets.token_hex(16)
        digest=action_hash(proposal['ticket_id'],proposal['expected_version'],proposal['target_status'])
        if digest!=proposal['digest']:raise ContractError('proposal changed')
        self.db.execute('INSERT INTO approvals(token,digest,expires) VALUES (?,?,?)',(token,digest,now+300));self.db.commit()
        return token
    def apply(self,proposal,token,operation_id,now=None,simulate_crash=False):
        now=time.time() if now is None else now
        digest=action_hash(proposal['ticket_id'],proposal['expected_version'],proposal['target_status'])
        if proposal['digest']!=digest:raise ContractError('proposal changed')
        try:
            self.db.execute('BEGIN IMMEDIATE')
            previous=self.db.execute('SELECT digest,result FROM events WHERE operation_id=?',(operation_id,)).fetchone()
            if previous:
                if previous[0]!=digest:raise ContractError('operation id reused for another action')
                self.db.commit();return {**json.loads(previous[1]),'replayed':True}
            approval=self.db.execute('SELECT digest,expires,used FROM approvals WHERE token=?',(token,)).fetchone()
            if not approval or approval[0]!=digest or approval[1]<now or approval[2]:raise ContractError('approval invalid, expired or used')
            count=self.db.execute('UPDATE tickets SET status=?,version=version+1 WHERE id=? AND version=?',
                (proposal['target_status'],proposal['ticket_id'],proposal['expected_version'])).rowcount
            if count!=1:raise ContractError('stale proposal')
            if simulate_crash:raise RuntimeError('injected failure before commit')
            result={'ticket_id':proposal['ticket_id'],'version':proposal['expected_version']+1,'status':proposal['target_status'],'replayed':False}
            self.db.execute('UPDATE approvals SET used=1 WHERE token=?',(token,))
            self.db.execute('INSERT INTO events VALUES (?,?,?)',(operation_id,digest,json.dumps(result)))
            self.db.commit();return result
        except Exception:
            self.db.rollback();raise
    def save(self,run_id,state):
        self.db.execute('INSERT OR REPLACE INTO checkpoints VALUES (?,?)',(run_id,json.dumps(state,ensure_ascii=False)));self.db.commit()
    def load(self,run_id):
        row=self.db.execute('SELECT state FROM checkpoints WHERE run_id=?',(run_id,)).fetchone()
        return json.loads(row[0]) if row else None
    def tools(self):return [
        Tool('get_ticket','读取本地教学工单的当前状态和版本。',object_schema({'ticket_id':TEXT}),self.get),
        Tool('propose_status','生成待人审的状态变更提案；不会写入业务状态，也不会自行获得审批。',object_schema({'ticket_id':TEXT,'target_status':{'type':'string','enum':['resolved','open']}}),self.propose)]
    def close(self):self.db.close()
