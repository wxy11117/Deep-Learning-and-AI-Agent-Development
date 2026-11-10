"""A tiny decoder: shape, causality and backward checks; not a language benchmark."""
from pathlib import Path
import sys,json,math
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"_ml_deps"))
import numpy as np
import torch
from torch import nn
torch.set_num_threads(2)
torch.manual_seed(71)
torch.use_deterministic_algorithms(True)

class CausalAttention(nn.Module):
    def __init__(self,d=16,heads=4):
        super().__init__()
        assert d%heads==0
        self.heads=heads;self.head_dim=d//heads
        self.qkv=nn.Linear(d,3*d)
        self.proj=nn.Linear(d,d)
    def forward(self,x):
        b,t,d=x.shape
        q,k,v=self.qkv(x).chunk(3,dim=-1)
        def split(a):
            return a.reshape(b,t,self.heads,self.head_dim).transpose(1,2)
        q,k,v=map(split,(q,k,v))
        scores=q@k.transpose(-2,-1)/math.sqrt(self.head_dim)
        mask=torch.ones(t,t,dtype=torch.bool,device=x.device).triu(1)
        scores=scores.masked_fill(mask,float("-inf"))
        weights=scores.softmax(dim=-1)
        context=(weights@v).transpose(1,2).contiguous().reshape(b,t,d)
        return self.proj(context),weights

class TinyDecoder(nn.Module):
    def __init__(self,vocab=8,d=16,max_length=16):
        super().__init__()
        self.tokens=nn.Embedding(vocab,d)
        self.positions=nn.Embedding(max_length,d)
        self.norm1=nn.LayerNorm(d);self.attention=CausalAttention(d,4)
        self.norm2=nn.LayerNorm(d)
        self.ffn=nn.Sequential(nn.Linear(d,4*d),nn.GELU(),nn.Linear(4*d,d))
        self.final_norm=nn.LayerNorm(d);self.head=nn.Linear(d,vocab)
    def forward(self,tokens):
        b,t=tokens.shape
        positions=torch.arange(t,device=tokens.device)
        x=self.tokens(tokens)+self.positions(positions)
        delta,weights=self.attention(self.norm1(x));x=x+delta
        x=x+self.ffn(self.norm2(x))
        return self.head(self.final_norm(x)),weights

def main():
    model=TinyDecoder()
    sequences=torch.tensor([[0,1,2,3,4],[1,2,3,4,5]])
    inputs=sequences[:,:-1];targets=sequences[:,1:]
    criterion=nn.CrossEntropyLoss();optimizer=torch.optim.AdamW(model.parameters(),lr=.01)
    initial_logits,initial_weights=model(inputs)
    initial_loss=criterion(initial_logits.reshape(-1,8),targets.reshape(-1)).item()
    losses=[]
    for _ in range(30):
        optimizer.zero_grad(set_to_none=True)
        logits,weights=model(inputs)
        loss=criterion(logits.reshape(-1,8),targets.reshape(-1))
        losses.append(loss.item());loss.backward()
        assert all(torch.isfinite(p.grad).all() for p in model.parameters() if p.grad is not None)
        optimizer.step()
    model.eval()
    with torch.no_grad():
        logits,weights=model(inputs)
        final_loss=criterion(logits.reshape(-1,8),targets.reshape(-1)).item()
        changed=inputs.clone();changed[:,-1]=7
        altered,_=model(changed)
        per_position=(logits-altered).abs().amax(dim=(0,2))
    assert per_position[:-1].max().item()<1e-6
    assert torch.triu(weights,diagonal=1).abs().max().item()==0
    assert final_loss<initial_loss
    output=ROOT/"projects/results";output.mkdir(parents=True,exist_ok=True)
    report={"scope":"two fixed sequences, training-fit and implementation checks only",
            "parameters":sum(p.numel() for p in model.parameters()),"input_shape":list(inputs.shape),
            "logit_shape":list(logits.shape),"attention_shape":list(weights.shape),
            "initial_loss":initial_loss,"final_loss":final_loss,
            "causality_max_earlier_logit_difference":per_position[:-1].max().item(),
            "changed_last_position_difference":per_position[-1].item(),
            "future_attention_max":torch.triu(weights,diagonal=1).max().item()}
    (output/"mini_transformer.json").write_text(json.dumps(report,indent=2),encoding="utf-8")
    np.savez(output/"mini_transformer.npz",losses=np.array(losses),initial_attention=initial_weights.detach().numpy(),
             final_attention=weights.numpy(),causal_difference=per_position.numpy())
    print(json.dumps(report,indent=2))
if __name__=="__main__":main()
