"""Five reproducible teaching projects. Uses public data or explicitly synthetic data."""
from pathlib import Path
import sys, json, csv, io, zipfile, urllib.request, hashlib, copy, time, argparse, platform
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "_ml_deps"))
import numpy as np
import torch
from torch import nn
from sklearn.datasets import load_digits
from sklearn.model_selection import train_test_split
from sklearn.linear_model import Ridge, LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, f1_score, confusion_matrix
from sklearn.feature_extraction.text import TfidfVectorizer

OUT=ROOT/"projects"/"results"; OUT.mkdir(parents=True,exist_ok=True)
DATA=ROOT/"projects"/"data"; DATA.mkdir(exist_ok=True)
torch.set_num_threads(2)
torch.use_deterministic_algorithms(True)

def seed(value):
    np.random.seed(value); torch.manual_seed(value)

def train(model,x,y,vx,vy,loss_fn,epochs=80,lr=.003,batch=64):
    tensors=[torch.as_tensor(v,dtype=torch.long if np.asarray(v).dtype.kind in 'iu' else torch.float32)
             for v in (x,y,vx,vy)]
    x,y,vx,vy=tensors
    opt=torch.optim.AdamW(model.parameters(),lr=lr,weight_decay=1e-4)
    best=float("inf"); state=None; hist=[]; best_epoch=0
    for epoch in range(epochs):
        model.train(); order=torch.randperm(len(x)); total=0.
        for ids in order.split(batch):
            opt.zero_grad(set_to_none=True); loss=loss_fn(model(x[ids]),y[ids])
            loss.backward(); opt.step(); total+=loss.item()*len(ids)
        model.eval()
        with torch.no_grad(): val=loss_fn(model(vx),vy).item()
        hist.append([epoch+1,total/len(x),val])
        if val<best: best=val; state=copy.deepcopy(model.state_dict()); best_epoch=epoch+1
    model.load_state_dict(state); model.eval()
    return np.array(hist),best_epoch

def predict(model,x):
    model.eval()
    with torch.no_grad(): return model(torch.as_tensor(x,dtype=torch.float32)).numpy()

def regression(y,p):
    return {"mae":float(np.mean(np.abs(y-p))),"rmse":float(np.sqrt(np.mean((y-p)**2)))}

def bikes():
    zpath=DATA/"bike_sharing.zip"
    url="https://archive.ics.uci.edu/static/public/275/bike+sharing+dataset.zip"
    if not zpath.exists(): zpath.write_bytes(urllib.request.urlopen(url,timeout=60).read())
    z=zipfile.ZipFile(zpath); rows=list(csv.DictReader(io.StringIO(z.read("day.csv").decode())))
    def col(k): return np.array([float(r[k]) for r in rows])
    target=col("cnt"); temp=col("temp"); hum=col("hum")
    inputs=[]
    for t in range(7,len(rows)):
        r=rows[t]; wd=float(r["weekday"]); mo=float(r["mnth"])
        inputs.append([target[t-1],target[t-7],target[t-7:t].mean(),
                       temp[t-1],hum[t-1],float(r["workingday"]),float(r["holiday"]),
                       np.sin(2*np.pi*wd/7),np.cos(2*np.pi*wd/7),
                       np.sin(2*np.pi*mo/12),np.cos(2*np.pi*mo/12),float(r["yr"])])
    x=np.array(inputs); y=target[7:]; cut1=500;cut2=600
    scale=StandardScaler().fit(x[:cut1]); xx=scale.transform(x).astype("float32")
    ym=y[:cut1].mean(); ys=y[:cut1].std(); yy=((y-ym)/ys).astype("float32")[:,None]
    out={"raw_days":len(rows),"usable_days":len(y),"split":[cut1,cut2-cut1,len(y)-cut2],
         "test_start":rows[cut2+7]["dteday"],"test_end":rows[-1]["dteday"],
         "source":url,"sha256":hashlib.sha256(zpath.read_bytes()).hexdigest(),
         "last_day":regression(y[cut2:],x[cut2:,0]),
         "last_week":regression(y[cut2:],x[cut2:,1])}
    best=None
    for alpha in [.1,1,10,100]:
        m=Ridge(alpha=alpha).fit(xx[:cut1],y[:cut1]); v=np.mean((m.predict(xx[cut1:cut2])-y[cut1:cut2])**2)
        if best is None or v<best[0]:best=(v,alpha,m)
    out["ridge"]={**regression(y[cut2:],best[2].predict(xx[cut2:])),"alpha":best[1]}
    runs=[]
    for s in [42,43,44]:
        seed(s); m=nn.Sequential(nn.Linear(12,32),nn.ReLU(),nn.Linear(32,16),nn.ReLU(),nn.Linear(16,1))
        hist,epoch=train(m,xx[:500],yy[:500],xx[500:600],yy[500:600],nn.MSELoss(),epochs=180,lr=.003)
        pred=predict(m,xx[600:]).ravel()*ys+ym
        runs.append({"seed":s,"best_epoch":epoch,**regression(y[600:],pred)})
        if s==42:
            np.savez(OUT/"bike.npz",dates=np.array([r["dteday"] for r in rows[607:]]),
                     truth=y[600:],pred=pred,last_day=x[600:,0],ridge=best[2].predict(xx[600:]),history=hist,
                     all_y=target,train_end=507,valid_end=607)
            torch.save({"weights":m.state_dict(),"mean":scale.mean_,"scale":scale.scale_,"y_mean":ym,"y_std":ys},OUT/"bike.pt")
    out["mlp"]=runs
    return out

class DigitCNN(nn.Module):
    def __init__(self):
        super().__init__()
        self.net=nn.Sequential(nn.Conv2d(1,8,3,padding=1),nn.ReLU(),nn.MaxPool2d(2),
                               nn.Conv2d(8,16,3,padding=1),nn.ReLU(),nn.Flatten(),
                               nn.Linear(16*4*4,10))
    def forward(self,x):return self.net(x)

def digits():
    data=load_digits(); x=data.images.astype("float32")[:,None]/16.; y=data.target
    ids=np.arange(len(y)); tr,rest=train_test_split(ids,test_size=.4,random_state=42,stratify=y)
    va,te=train_test_split(rest,test_size=.5,random_state=42,stratify=y[rest])
    linear=LogisticRegression(max_iter=2000,C=1).fit(x[tr].reshape(len(tr),-1),y[tr])
    lp=linear.predict(x[te].reshape(len(te),-1))
    out={"n":len(y),"split":[len(tr),len(va),len(te)],"split_protocol":"fixed stratified sample split; NOT writer-independent",
         "logistic":{"accuracy":float(accuracy_score(y[te],lp)),"macro_f1":float(f1_score(y[te],lp,average="macro"))},"cnn":[]}
    for s in [42,43,44]:
        seed(s);m=DigitCNN();hist,epoch=train(m,x[tr],y[tr],x[va],y[va],nn.CrossEntropyLoss(),epochs=45,lr=.003)
        logits=predict(m,x[te]);p=logits.argmax(1)
        out["cnn"].append({"seed":s,"best_epoch":epoch,"accuracy":float(accuracy_score(y[te],p)),
                           "macro_f1":float(f1_score(y[te],p,average="macro")),
                           "parameters":sum(p.numel() for p in m.parameters())})
        if s==42:
            np.savez(OUT/"digits.npz",images=x[te,0],truth=y[te],pred=p,logits=logits,
                     confusion=confusion_matrix(y[te],p),history=hist,train_ids=tr,valid_ids=va,test_ids=te)
            torch.save(m.state_dict(),OUT/"digits.pt")
    return out

class SensorCNN(nn.Module):
    def __init__(self):
        super().__init__(); self.net=nn.Sequential(nn.Conv1d(2,16,3),nn.ReLU(),nn.Conv1d(16,16,3),nn.ReLU(),
                                                  nn.Flatten(),nn.Linear(16*12,1))
    def forward(self,x):return self.net(x)

def sensor():
    rng=np.random.default_rng(17);episodes=[]
    for j in range(120):
        t=np.arange(96); clean=rng.uniform(30,120)+rng.uniform(4,15)*np.sin(t/rng.uniform(8,20)+rng.uniform(0,6))
        clean+=rng.uniform(-.2,.2)*t
        noisy=clean+rng.normal(0,2,96)
        spikes=rng.random(96)<.045; noisy[spikes]+=rng.normal(0,22,spikes.sum())
        missing=rng.random(96)<.035
        filled=noisy.copy()
        for k in range(96):
            if missing[k]:filled[k]=filled[k-1] if k else 75
        windows=np.array([np.stack((filled[k-15:k+1],missing[k-15:k+1].astype(float))) for k in range(15,96)])
        episodes.append((windows,clean[15:],filled[15:],np.array([np.median(filled[k-4:k+1]) for k in range(15,96)])))
    def stack(a,b):
        return [np.concatenate([ep[i] for ep in episodes[a:b]]) for i in range(4)]
    tx,ty,_,_=stack(0,80);vx,vy,_,_=stack(80,100);ex,ey,raw,med=stack(100,120)
    mean=tx[:,0].mean();std=tx[:,0].std()
    for xx in (tx,vx,ex):xx[:,0]=(xx[:,0]-mean)/std
    seed(42);m=SensorCNN()
    hist,ep=train(m,tx.astype("float32"),((ty-mean)/std).astype("float32")[:,None],
                  vx.astype("float32"),((vy-mean)/std).astype("float32")[:,None],nn.MSELoss(),epochs=35,lr=.001,batch=128)
    pred=predict(m,ex).ravel()*std+mean
    np.savez(OUT/"sensor.npz",truth=ey,pred=pred,raw=raw,median=med,history=hist,inputs=ex.astype("float32"))
    torch.save({"weights":m.state_dict(),"mean":float(mean),"std":float(std),
                "window":16,"channels":["distance","missing_mask"]},OUT/"sensor.pt")
    return {"data":"SIMULATED, not hardware measurements","unit":"cm","episodes":[80,20,20],"windows":[len(ty),len(vy),len(ey)],
            "best_epoch":ep,"raw":regression(ey,raw),"causal_median5":regression(ey,med),"cnn":regression(ey,pred)}

class TinyUNet(nn.Module):
    def __init__(self):
        super().__init__()
        self.enc=nn.Sequential(nn.Conv2d(1,8,3,padding=1),nn.ReLU(),nn.Conv2d(8,8,3,padding=1),nn.ReLU())
        self.down=nn.Sequential(nn.MaxPool2d(2),nn.Conv2d(8,16,3,padding=1),nn.ReLU())
        self.out=nn.Sequential(nn.Conv2d(24,8,3,padding=1),nn.ReLU(),nn.Conv2d(8,1,1))
    def forward(self,x):
        a=self.enc(x);b=self.down(a);b=nn.functional.interpolate(b,size=a.shape[-2:],mode="bilinear",align_corners=False)
        return self.out(torch.cat([a,b],dim=1))

def segmentation():
    rng=np.random.default_rng(28)
    def gen(n):
        imgs=[];masks=[]; yy,xx=np.mgrid[:32,:32]
        for _ in range(n):
            slope=rng.uniform(-1,1);offset=rng.uniform(6,26); width=rng.uniform(.7,1.4)
            mask=(np.abs(yy-(slope*(xx-16)+offset))<width)
            if rng.random()<.2:mask[:]=False
            bg=rng.uniform(.15,.45)+.05*np.sin(xx/rng.uniform(2,6))
            image=np.clip(bg+rng.normal(0,.06,(32,32))+mask*rng.uniform(.28,.5),0,1)
            imgs.append(image);masks.append(mask)
        return np.array(imgs,dtype="float32")[:,None],np.array(masks,dtype="float32")[:,None]
    tx,ty=gen(240);vx,vy=gen(60);ex,ey=gen(100)
    seed(42);m=TinyUNet()
    hist,ep=train(m,tx,ty,vx,vy,nn.BCEWithLogitsLoss(pos_weight=torch.tensor(8.)),epochs=30,lr=.003,batch=24)
    vprob=1/(1+np.exp(-predict(m,vx)));prob=1/(1+np.exp(-predict(m,ex)))
    def metrics(target,pred):
        y=target.astype(bool);tp=np.logical_and(y,pred).sum();fp=np.logical_and(~y,pred).sum();fn=np.logical_and(y,~pred).sum()
        return {"iou":float(tp/(tp+fp+fn)),"dice":float(2*tp/(2*tp+fp+fn))}
    th=max([.3,.4,.5,.6,.7],key=lambda t:metrics(vy,vprob>t)["iou"])
    base_th=max([.4,.5,.6,.7,.8],key=lambda t:metrics(vy,vx>t)["iou"])
    np.savez(OUT/"segmentation.npz",images=ex[:,0],truth=ey[:,0],prob=prob[:,0],pred=(prob[:,0]>th),
             threshold_baseline=(ex[:,0]>base_th),history=hist)
    torch.save({"weights":m.state_dict(),"threshold":th,"input_scale":"0 to 1 grayscale"},
               OUT/"segmentation.pt")
    return {"data":"SIMULATED grayscale scratches; not production defects","split":[240,60,100],"best_epoch":ep,
            "aggregation":"global pixel sums","unet_threshold":th,"baseline_threshold":base_th,
            "intensity_baseline":metrics(ey,ex>base_th),"tiny_unet":metrics(ey,prob>th)}

def retrieval():
    docs=[
      "A01 设备启动前应确认供电为十二伏直流，启动自检持续三秒。供电电压不符时不得启动。",
      "A02 温度报警阈值为七十五摄氏度，连续超过阈值五秒后触发报警。",
      "A03 传感器数据每一百毫秒采样一次，每十次采样形成一条汇总记录。",
      "A04 通信断开超过两秒进入保持状态，超过十秒停止自动运行。",
      "A05 清洁镜头应先断电，再使用无尘布，不得使用研磨材料。",
      "A06 固件升级前先保存配置，升级完成后重新启动并检查版本号。",
      "A07 故障码E12表示电机过流，停止运行并检查负载和接线。",
      "A08 故障码E21表示传感器超时，检查接头与采样任务是否运行。",
      "A09 操作日志保留三十天，导出格式为CSV，时间戳采用本地时间。",
      "A10 急停按钮按下后切断执行机构输出，复位需要人工确认。",
      "A11 手动模式下自动调度暂停，操作员负责逐次确认动作。",
      "A12 电池电量低于百分之二十时提示充电，低于百分之十时停止自动任务。"]
    queries=[
      ("启动自检需要多长时间",0),("设备需要什么电源电压",0),("高温报警要持续多久才触发",1),
      ("数据采样间隔是多少",2),("断线十秒会发生什么",3),("擦镜头前先做什么",4),
      ("升级后如何确认版本",5),("E12故障怎样处理",6),("E21意味着什么",7),
      ("日志最多保存多久",8),("急停后怎么恢复",9),("手动模式自动调度会怎样",10),
      ("电量不足什么时候停止任务",11),("多少摄氏度会报警",1),("怎么导出操作记录",8)]
    vec=TfidfVectorizer(analyzer="char",ngram_range=(2,3),norm="l2")
    matrix=vec.fit_transform(docs); scores=(vec.transform([q[0] for q in queries])@matrix.T).toarray()
    ranks=np.argsort(-scores,axis=1);truth=np.array([q[1] for q in queries])
    recalls={str(k):float(np.mean([t in r[:k] for t,r in zip(truth,ranks)])) for k in [1,3,5]}
    mrr=float(np.mean([1/(np.flatnonzero(r==t)[0]+1) for t,r in zip(truth,ranks)]))
    result={"corpus":"AUTHOR-WRITTEN FICTIONAL device manual; not a real device specification",
            "documents":len(docs),"queries":len(queries),"recall_at_k":recalls,"mrr":mrr,
            "generative_llm_executed":False,"queries_and_targets":queries}
    np.savez(OUT/"retrieval.npz",scores=scores,truth=truth,ranks=ranks)
    (DATA/"fictional_manual.txt").write_text(
        "教学虚构语料：以下参数不属于真实设备，不可作为设备操作依据。\n\n"+"\n".join(docs),encoding="utf-8")
    import joblib
    joblib.dump({"vectorizer":vec,"document_matrix":matrix,"documents":docs},
                OUT/"retrieval_index.joblib")
    return result

if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project',choices=['all','bike','digits','sensor','segmentation','retrieval'],default='all',help='Run one project; preserve metrics for other projects.')
    selected=parser.parse_args().project
    metrics_path=OUT/'metrics.json'
    results=json.loads(metrics_path.read_text(encoding='utf-8')) if selected!='all' and metrics_path.exists() else {}
    environments_path=OUT/'project_environments.json'
    environments=json.loads(environments_path.read_text(encoding='utf-8')) if environments_path.exists() else {}
    environment={'python':sys.version,'torch':torch.__version__,'numpy':np.__version__,'platform':platform.platform()}
    for name,fn in [("bike",bikes),("digits",digits),("sensor",sensor),("segmentation",segmentation),("retrieval",retrieval)]:
        if selected not in ('all',name):continue
        t=time.time();results[name]=fn();results[name]["elapsed_seconds"]=round(time.time()-t,2)
        metrics_path.write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding="utf-8")
        environments[name]={**environment,'completed_at':time.strftime('%Y-%m-%dT%H:%M:%S%z')}
        environments_path.write_text(json.dumps(environments,ensure_ascii=False,indent=2),encoding='utf-8')
        print(name,json.dumps(results[name],ensure_ascii=False),flush=True)
    if selected=='all':
        (OUT/"environment.json").write_text(json.dumps(environment,indent=2),encoding="utf-8")
