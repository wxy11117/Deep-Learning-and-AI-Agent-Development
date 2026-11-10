"""Recompute reported metrics and compare reloaded model outputs with saved arrays."""
from pathlib import Path
import sys,json,csv,zipfile,io,ast
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"_ml_deps"))
sys.path.insert(0,str(ROOT/"projects"))
sys.path.insert(0,str(ROOT))
import numpy as np
import torch,joblib
from sklearn.datasets import load_digits
from sklearn.metrics import accuracy_score,f1_score
from run_projects import DigitCNN,SensorCNN,TinyUNet,predict,regression
OUT=ROOT/"projects/results"
m=json.loads((OUT/"metrics.json").read_text(encoding="utf-8"))
checks=[]
def close(name,a,b,tol=1e-5):
    error=float(np.max(np.abs(np.asarray(a)-np.asarray(b))))
    assert error<=tol,(name,error)
    checks.append({"check":name,"maximum_absolute_error":error,"tolerance":tol})

d=np.load(OUT/"bike.npz")
for metric,value in regression(d["truth"],d["pred"]).items():close("bike "+metric,value,m["bike"]["mlp"][0][metric])
c=torch.load(OUT/"bike.pt",map_location="cpu",weights_only=False)
with zipfile.ZipFile(ROOT/"projects/data/bike_sharing.zip") as z:
    rows=list(csv.DictReader(io.StringIO(z.read("day.csv").decode())))
y=np.array([float(r["cnt"]) for r in rows]);xx=[]
for t in range(607,len(rows)):
    r=rows[t];wd=float(r["weekday"]);mo=float(r["mnth"])
    xx.append([y[t-1],y[t-7],y[t-7:t].mean(),float(rows[t-1]["temp"]),float(rows[t-1]["hum"]),
               float(r["workingday"]),float(r["holiday"]),np.sin(2*np.pi*wd/7),np.cos(2*np.pi*wd/7),
               np.sin(2*np.pi*mo/12),np.cos(2*np.pi*mo/12),float(r["yr"])])
model=torch.nn.Sequential(torch.nn.Linear(12,32),torch.nn.ReLU(),torch.nn.Linear(32,16),
                          torch.nn.ReLU(),torch.nn.Linear(16,1))
model.load_state_dict(c["weights"])
pred=predict(model,((np.array(xx)-c["mean"])/c["scale"]).astype("float32")).ravel()*c["y_std"]+c["y_mean"]
close("bike reload and preprocessing",pred,d["pred"],1e-3)

d=np.load(OUT/"digits.npz");data=load_digits()
assert not (set(d["train_ids"])&set(d["valid_ids"]) or set(d["train_ids"])&set(d["test_ids"]) or set(d["valid_ids"])&set(d["test_ids"]))
assert len(set(np.concatenate([d["train_ids"],d["valid_ids"],d["test_ids"]])))==1797
model=DigitCNN();model.load_state_dict(torch.load(OUT/"digits.pt",map_location="cpu",weights_only=True))
logits=predict(model,data.images[d["test_ids"]].astype("float32")[:,None]/16)
close("digits reload logits",logits,d["logits"])
close("digits accuracy",accuracy_score(d["truth"],d["pred"]),m["digits"]["cnn"][0]["accuracy"])
close("digits macro F1",f1_score(d["truth"],d["pred"],average="macro"),m["digits"]["cnn"][0]["macro_f1"])
assert d["confusion"].sum()==360

d=np.load(OUT/"sensor.npz");c=torch.load(OUT/"sensor.pt",map_location="cpu",weights_only=True)
model=SensorCNN();model.load_state_dict(c["weights"])
close("sensor reload",predict(model,d["inputs"]).ravel()*c["std"]+c["mean"],d["pred"],1e-4)
for key,label in [("raw","raw"),("median","causal_median5"),("pred","cnn")]:
    for metric,value in regression(d["truth"],d[key]).items():close("sensor "+key+" "+metric,value,m["sensor"][label][metric])

d=np.load(OUT/"segmentation.npz");c=torch.load(OUT/"segmentation.pt",map_location="cpu",weights_only=True)
model=TinyUNet();model.load_state_dict(c["weights"])
logits=predict(model,d["images"][:,None]);prob=1/(1+np.exp(-logits[:,0]))
close("segmentation reload probabilities",prob,d["prob"])
target=d["truth"].astype(bool)
for key,name in [("pred","tiny_unet"),("threshold_baseline","intensity_baseline")]:
    pred=d[key].astype(bool);tp=(target&pred).sum();fp=(~target&pred).sum();fn=(target&~pred).sum()
    close("segmentation "+name+" IoU",tp/(tp+fp+fn),m["segmentation"][name]["iou"])
    close("segmentation "+name+" Dice",2*tp/(2*tp+fp+fn),m["segmentation"][name]["dice"])

d=np.load(OUT/"retrieval.npz");index=joblib.load(OUT/"retrieval_index.joblib")
queries=[x[0] for x in m["retrieval"]["queries_and_targets"]]
scores=(index["vectorizer"].transform(queries)@index["document_matrix"].T).toarray()
close("retrieval index reload",scores,d["scores"])
for k in [1,3,5]:
    recall=np.mean([t in r[:k] for t,r in zip(d["truth"],d["ranks"])])
    close("retrieval recall@"+str(k),recall,m["retrieval"]["recall_at_k"][str(k)])
from numpy_mlp_demo import evaluate
d=np.load(ROOT/"experiment/numpy_mlp.npz")
params={k:d[k] for k in ["w1","b1","w2","b2"]}
loss,accuracy=evaluate(d["x_test"],d["y_test"],params)
reference=json.loads((ROOT/"experiment/result.json").read_text(encoding="utf-8"))
close("numpy demo reload loss",loss,reference["test_loss"])
close("numpy demo reload accuracy",accuracy,reference["test_accuracy"])

c=torch.load(ROOT/"pytorch_mlp.pt",map_location="cpu",weights_only=True)
model=torch.nn.Sequential(torch.nn.Linear(2,32),torch.nn.Tanh(),torch.nn.Linear(32,2))
model.load_state_dict(c["state_dict"]);model.eval()
generator=torch.Generator().manual_seed(42)
for n in [1000,400,800]:
    xx=torch.rand(n,2,generator=generator)*3-1.5
    yy=(xx.square().sum(1)>1).long()
with torch.no_grad():
    logits=model((xx-c["mean"])/c["std"])
    loss=torch.nn.functional.cross_entropy(logits,yy).item()
    accuracy=(logits.argmax(1)==yy).float().mean().item()
ref=ast.literal_eval((OUT/"pytorch_mlp_log.txt").read_text(encoding="utf-8").strip().splitlines()[-1])
close("pytorch demo reload loss",loss,ref["test_loss"])
close("pytorch demo reload accuracy",accuracy,ref["test_accuracy"])

report={"passed":len(checks),"checks":checks,"digit_split_disjoint":True,"digit_confusion_total":360}
(OUT/"verification.json").write_text(json.dumps(report,indent=2),encoding="utf-8")
print(json.dumps(report,indent=2))
