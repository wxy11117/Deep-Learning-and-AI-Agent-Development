"""Auditable CSV calculations; filenames come from a registry, not model paths."""
from pathlib import Path
from decimal import Decimal,InvalidOperation
from collections import defaultdict
from datetime import date
import csv,json
from core import Tool,TEXT,object_schema,ContractError
ROOT=Path(__file__).resolve().parent
CSV_TEXT='''order_id,date,region,revenue,cost
O01,2026-01-01,华东,120.00,80.00
O02,2026-01-02,华南,200.00,140.00
O03,2026-01-03,华东,150.00,90.00
O03,2026-01-03,华东,150.00,90.00
O04,2026-01-04,华南,-20.00,-12.00
O05,2026-01-05,华北,300.00,180.00
O06,2026-01-06,华北,,70.00
O07,not-a-date,华东,50.00,25.00
O08,2026-02-01,华东,180.00,110.00
O09,2026-02-02,华南,220.00,130.00
O10,2026-02-03,华北,100.00,60.00
O11,2026-02-04,华东,80.00,50.00
O12,2026-02-05,华南,140.00,85.00
'''
def prepare():
    (ROOT/'data').mkdir(exist_ok=True)
    (ROOT/'data/orders.csv').write_text(CSV_TEXT,encoding='utf-8')
class AnalysisStore:
    def __init__(self):self.allowed={'orders':ROOT/'data/orders.csv'}
    def load(self,dataset):
        if dataset not in self.allowed:raise ContractError('unknown dataset')
        with self.allowed[dataset].open(encoding='utf-8',newline='') as f:raw=list(csv.DictReader(f))
        rows=[];issues=[];seen={}
        for line,r in enumerate(raw,2):
            try:
                if r['order_id'] in seen:
                    if seen[r['order_id']]!=r:raise ContractError('conflicting duplicate order id')
                    issues.append({'line':line,'reason':'exact_duplicate'});continue
                seen[r['order_id']]=r
                date.fromisoformat(r['date'])
                rev=Decimal(r['revenue']);cost=Decimal(r['cost'])
                if not rev.is_finite() or not cost.is_finite():raise ValueError('nonfinite')
                rows.append({**r,'revenue':rev,'cost':cost})
            except ContractError:raise
            except (ValueError,InvalidOperation):issues.append({'line':line,'reason':'invalid_date_or_money'})
        return rows,issues,len(raw)
    def inspect(self,dataset):
        rows,issues,n=self.load(dataset)
        return {'dataset':dataset,'raw_rows':n,'accepted_rows':len(rows),'issues':issues,'columns':['order_id','date','region','revenue','cost'],'source':'author-created simulated orders','policy':'remove exact duplicate; exclude invalid; keep refunds'}
    def aggregate(self,dataset,group_by):
        rows,issues,n=self.load(dataset);groups=defaultdict(lambda:{'revenue':Decimal(0),'cost':Decimal(0),'orders':0})
        for r in rows:
            key=r['region'] if group_by=='region' else r['date'][:7]
            v=groups[key];v['revenue']+=r['revenue'];v['cost']+=r['cost'];v['orders']+=1
        out=[]
        for k,v in sorted(groups.items()):
            profit=v['revenue']-v['cost']
            out.append({'group':k,'revenue':str(v['revenue']),'cost':str(v['cost']),'profit':str(profit),'orders':v['orders'],
                'margin':float(profit/v['revenue']) if v['revenue'] else None})
        return {'dataset':dataset,'group_by':group_by,'rows':out,'excluded_rows':len(issues)}
    def tools(self):return [
        Tool('inspect_dataset','检查已登记数据集的字段、行数和剔除原因；不接受磁盘路径。',object_schema({'dataset':{'type':'string','enum':['orders']}}),self.inspect),
        Tool('aggregate_orders','对已清洗教学订单按地区或月份计算收入、成本与利润；保留负数退款，金额用十进制定点计算。',object_schema({'dataset':{'type':'string','enum':['orders']},'group_by':{'type':'string','enum':['region','month']}}),self.aggregate)]
def render_report(store,out):
    quality=store.inspect('orders');region=store.aggregate('orders','region');month=store.aggregate('orders','month')
    lines=['# 教学订单分析报告','', '数据为人工构造，不代表真实经营表现。','',
      f"原始 {quality['raw_rows']} 行，接受 {quality['accepted_rows']} 行；剔除 {len(quality['issues'])} 行。退款保留，缺失金额不填成零。",'',
      '| 地区 | 收入 | 成本 | 利润 | 利润率 |','|---|---:|---:|---:|---:|']
    for r in region['rows']:lines.append(f"| {r['group']} | {r['revenue']} | {r['cost']} | {r['profit']} | {r['margin']:.2%} |")
    lines+=['','图表与结论必须引用相同的聚合表。不能从两个观察月份推断因果或长期增长。','']
    out.write_text('\n'.join(lines),encoding='utf-8')
    return {'quality':quality,'region':region,'month':month}
