"""Verify every gradient in Chapter 27 using central finite differences."""
from pathlib import Path
import json
import numpy as np
ROOT=Path(__file__).resolve().parent
X=np.eye(2,dtype=np.float64);Y=np.array([[1.],[0.]])
PARAMS={"W1":np.array([[1.,-1.],[.5,1.]]),"b1":np.zeros(2),
        "W2":np.array([[1.],[-1.]]),"b2":np.zeros(1)}
def forward(p):
    z1=X@p["W1"]+p["b1"];h=np.maximum(z1,0)
    z=h@p["W2"]+p["b2"];prob=1/(1+np.exp(-z))
    loss=np.mean(np.logaddexp(0,z)-Y*z)
    return loss,z1,h,z,prob
def gradients(p):
    loss,z1,h,z,prob=forward(p)
    d2=(prob-Y)/len(X);d1=(d2@p["W2"].T)*(z1>0)
    return {"W1":X.T@d1,"b1":d1.sum(0),"W2":h.T@d2,"b2":d2.sum(0)}
def finite_difference(p,eps):
    out={}
    for key,value in p.items():
        g=np.empty_like(value)
        for index in np.ndindex(value.shape):
            plus={k:v.copy() for k,v in p.items()};minus={k:v.copy() for k,v in p.items()}
            plus[key][index]+=eps;minus[key][index]-=eps
            g[index]=(forward(plus)[0]-forward(minus)[0])/(2*eps)
        out[key]=g
    return out
def main():
    g=gradients(PARAMS);epsilons=np.logspace(-1,-12,12);errors=[]
    for eps in epsilons:
        num=finite_difference(PARAMS,eps)
        errors.append(max(np.max(np.abs(g[k]-num[k])) for k in g))
    after={k:PARAMS[k]-.1*g[k] for k in g}
    result={"loss_before":float(forward(PARAMS)[0]),"loss_after_sgd_0.1":float(forward(after)[0]),
            "gradients":{k:v.tolist() for k,v in g.items()},
            "finite_difference":[[float(e),float(r)] for e,r in zip(epsilons,errors)]}
    assert errors[4]<1e-8,"Analytic and numerical gradients disagree"
    assert result["loss_after_sgd_0.1"]<result["loss_before"]
    out=ROOT/"projects/results";out.mkdir(parents=True,exist_ok=True)
    (out/"derivation_lab.json").write_text(json.dumps(result,indent=2),encoding="utf-8")
    print(json.dumps(result,indent=2))
if __name__=="__main__":main()

