import pandas as pd
import numpy as np

class SupplyChainResilienceTrainer:
    def generate_dataset(self,n=800):
        lt=np.random.randint(5,40,n)
        rel=np.random.randint(50,100,n)
        score=(rel*0.7)+((1/lt)*30)
        df=pd.DataFrame({"lead_time":lt,"reliability":rel,"score":score})
        return df
    def train(self,df):
        c1=abs(df["lead_time"].corr(df["score"]))
        c2=abs(df["reliability"].corr(df["score"]))
        w1=c1/(c1+c2)
        w2=c2/(c1+c2)
        return w1,w2

class SupplyChainResilienceAgent:
    def __init__(self,delay_weight,reliability_weight,threshold=40):
        self.dw=delay_weight
        self.rw=reliability_weight
        self.threshold=threshold
    def compute_reliability(self,lead_times):
        df=pd.DataFrame(lead_times,columns=["lt"])
        variance=np.var(df["lt"])
        consistency=(1/(1+variance))*100
        on_time=len(df[df["lt"]<=df["lt"].mean()])/len(df)*100
        score=(consistency*0.4)+(on_time*0.6)
        return np.clip(score,0,100)
    def compute_delay(self,lead_times):
        avg=np.mean(lead_times)
        return (1/avg)*100
    def run(self,vendors):
        rows=[]
        for v in vendors:
            rel=self.compute_reliability(v["lead_times"])
            d=self.compute_delay(v["lead_times"])
            final=(d*self.dw)+(rel*self.rw)
            rec="SWITCH_VENDOR" if final<self.threshold else "KEEP_VENDOR"
            rows.append({"vendor_name":v["name"],"score":round(final,2),"recommendation":rec})
        return pd.DataFrame(rows)

trainer=SupplyChainResilienceTrainer()
data=trainer.generate_dataset()
dw,rw=trainer.train(data)
agent=SupplyChainResilienceAgent(dw,rw)

vendors=[
    {"name":"MedSupply Labs","lead_times":[11,12,12,13,14,15]},
    {"name":"HealthPro Distributors","lead_times":[22,3,25,26,27,28]},
    {"name":"RapidMed Logistics","lead_times":[78,58,98,79,98,100]},
    {"name":"CareChain Global","lead_times":[28,30,31,33,34]},
    {"name":"VitaSource Pharma","lead_times":[95,15,16,87,18]}
]

result=agent.run(vendors)
print(result)
