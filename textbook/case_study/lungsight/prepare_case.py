"""Freeze public source excerpts, synthetic task fixtures and a teaching task set."""
from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parent
REV='80932e2d34eefbfd3031e0a04370986562cf40ac'

def excerpt(id,title,path,first,last):
    p=ROOT/'sources'/path
    text='\n'.join(p.read_text(encoding='utf-8').splitlines()[first-1:last])
    return {'id':id,'version':REV,'title':title,'text':text,'path':path,'lines':[first,last],
            'url':f'https://github.com/wxy11117/LungSight/blob/{REV}/{path}#L{first}-L{last}',
            'excerpt_sha256':hashlib.sha256(text.encode()).hexdigest()}

docs=[
excerpt('LS01','本地模型架构 五折 ResNet18 权重版本','README.md',9,9),
excerpt('LS02','项目定义 四分类 科研教学用途','README.md',5,5),
excerpt('LS03','DICOM 单帧导入 抽取层数','README.md',66,66),
excerpt('LS04','未关联与关联任务的问答模式','documentation/medical-answer-modes.md',5,10),
excerpt('LS05','自动 RAG 评测使用模拟模型','backend/rag_evaluation.py',52,54),
excerpt('LS06','给大模型发送的内容 原始CT 数据隐私','documentation/medical-answer-modes.md',17,17),
excerpt('LS07','本地引文如何验证','documentation/medical-answer-modes.md',22,29),
excerpt('LS08','旧问答历史与报告保留规则','documentation/medical-answer-modes.md',37,41),
]
matrix=[[.10,.60,.20,.10],[.10,.55,.25,.10],[.15,.45,.30,.10],[.10,.30,.50,.10],[.10,.65,.15,.10]]
tasks={
 'DEMO-001':{'task_id':'DEMO-001','data_kind':'AUTHOR_CONSTRUCTED_PROBABILITIES','class_labels':['A','B','C','D'],
             'fold_probabilities':matrix,'model_version':'research-fivefold-20260902-165455','review_status':'pending'},
 'DEMO-002':{'task_id':'DEMO-002','data_kind':'AUTHOR_CONSTRUCTED_PROBABILITIES','class_labels':['A','B','C','D'],
             'fold_probabilities':matrix,'model_version':'future-model-not-in-snapshot','review_status':'pending'}
}

def question(id,category,text,value=None,sources=None,task=None,status='answered'):
    return {'id':id,'category':category,'question':text,'expected':{'status':status,'value':value,'source_ids':sources or [],'task_id':task}}

cases=[
 question('L01','source','LungSight 当前本地五折图像模型使用什么网络架构？value 只写架构名称。','ResNet18',['LS01']),
 question('L02','source','项目说明中的图像集成包含几折？value 填整数。',5,['LS01']),
 question('L03','source','项目定义中的 CT 分类任务有几类？value 填整数。',4,['LS02']),
 question('L04','source','项目当前研究权重的版本标识是什么？value 填完整标识。','research-fivefold-20260902-165455',['LS01']),
 question('L05','source','基础 DICOM 导入最多等距抽取多少层进入模型？value 填整数。',32,['LS03']),
 question('L06','source','已经关联 CT 任务的问答采用哪个服务端模式？value 填模式代码。','ct_hybrid',['LS04']),
 question('L07','source','未关联病例的主页问答采用哪个服务端模式？value 填模式代码。','medical_general',['LS04']),
 question('L08','source','仓库 run_rag_evaluation 创建了哪个模型提供者类？value 填类名。','MockLLMProvider',['LS05']),
 question('L09','source','当前问答流程会把原始 CT 文件发送给大模型吗？value 填 JSON 布尔值。',False,['LS06']),
 question('L10','source','基础 DICOM 导入支持单帧还是多帧 CT 对象？value 只填“单帧”或“多帧”。','单帧',['LS03']),
 question('L11','source','本地引文检查是否要求 quote 逐字包含于传入证据？value 填 JSON 布尔值。',True,['LS07']),
 question('L12','source','切换问答新模式时是否重新生成旧问答？value 填 JSON 布尔值。',False,['LS08']),
 question('L13','task','读取教学任务 DEMO-001；五折平均概率最大的类别是什么？value 只填类别字母。','B',task='DEMO-001'),
 question('L14','task','教学任务 DEMO-001 中，B 类五折平均概率是多少？value 填 0 到 1 的数值。',.51,task='DEMO-001'),
 question('L15','task','教学任务 DEMO-001 中，有多少比例的折把 B 排第一？value 填 0 到 1 的数值。',.8,task='DEMO-001'),
 question('L16','task','DEMO-001 的 B 类最高与最低单折概率之差是多少？value 填数值。',.35,task='DEMO-001'),
 question('L17','task','DEMO-001 第四折（从 1 起编号）的最高概率类别是什么？value 只填类别字母。','C',task='DEMO-001'),
 question('L18','missing','请读取任务 DEMO-999，报告它的最高概率类别。找不到该任务时请标记资料不足，value 为 null。',status='insufficient'),
 question('L19','missing','请查当前资料库：该项目在 2027 年独立多中心试验中的总体准确率是多少？未记录时 value 为 null，并标记资料不足。',status='insufficient'),
 question('L20','version','读取 DEMO-002 并查当前模型说明；这份任务的模型版本是否与资料版本匹配，足以据此解释模型架构？版本不匹配时标记资料不足，value 为 null。',sources=['LS01'],task='DEMO-002',status='insufficient'),
]
development=[
question('DEV01','development','查找项目说明：请给出本地图像模型的网络名称，value 只写名称。','ResNet18',['LS01']),
question('DEV02','development','读取教学任务 DEMO-001，平均分布中前两类的概率差是多少？value 填数值。',.23,task='DEMO-001')]

def save(name,value):
    p=ROOT/name
    if p.exists():raise RuntimeError('Frozen file already exists: '+name)
    p.write_text(json.dumps(value,ensure_ascii=False,indent=2),encoding='utf-8')

if __name__=='__main__':
    save('documents.json',docs);save('teaching_tasks.json',tasks)
    save('evaluation_cases.json',{'purpose':'teaching demonstration; author-written tasks','version':'lungsight-teaching-1','cases':cases,'development_cases':development,
         'sampling':'20 purposefully selected tasks; 12 source lookups, 5 numeric tasks, 2 missing-information cases, 1 version-conflict case',
         'reuse_notice':'Development and evaluation share the small source pack. Evaluation prompts are frozen before model calls; this is not an independent clinical or general Agent benchmark.'})
    sources={p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in (ROOT/'sources').rglob('*') if p.is_file()}
    manifest={'repository':'wxy11117/LungSight','commit':REV,'captured_at':'2026-11-10','source_files_sha256':sources,
              'fixtures':'Constructed class A/B/C/D probabilities, not patient data or measured model predictions.',
              'documents_sha256':hashlib.sha256((ROOT/'documents.json').read_bytes()).hexdigest(),
              'evaluation_sha256':hashlib.sha256((ROOT/'evaluation_cases.json').read_bytes()).hexdigest(),
              'task_sha256':hashlib.sha256((ROOT/'teaching_tasks.json').read_bytes()).hexdigest()}
    save('source_manifest.json',manifest)
    print(json.dumps({'documents':len(docs),'evaluation_tasks':len(cases),'development_tasks':len(development),'revision':REV}))
