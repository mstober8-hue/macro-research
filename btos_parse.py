import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from datapaths import dp
import pandas as pd, numpy as np, re

def pct(v):
    s=str(v).strip()
    if not s.endswith('%'): return np.nan
    try: return float(s[:-1])
    except: return np.nan

def parse(path, unit):
    d=pd.ExcelFile(path).parse("Response Estimates")
    d.columns=[str(c).strip() for c in d.columns]
    per=[c for c in d.columns if c.isdigit()]
    d["qid"]=d["Question ID"].astype(str).str.replace(r"\.0$","",regex=True)
    d["ans"]=d["Answer"].astype(str).str.strip()
    long=d.melt(id_vars=[unit,"qid","ans"],value_vars=per,var_name="period",value_name="v")
    long["v"]=long.v.map(pct)
    long=long.dropna(subset=["v"])
    return long

def build(path, unit):
    L=parse(path,unit)
    def g(qid,ans):
        s=L[(L.qid==qid)&(L.ans==ans)][[unit,"period","v"]]
        return s.rename(columns={"v":f"q{qid}_{ans.lower().replace(' ','_')}"})
    out=None
    for qid,ans in [("7","Yes"),("24","Yes"),("5","Increased"),("5","Decreased"),
                    ("17","Increase"),("17","Decrease"),("10","Increased"),("10","Decreased"),
                    ("4","Increased"),("4","Decreased"),("11","Increased"),("11","Decreased")]:
        s=g(qid,ans)
        out=s if out is None else out.merge(s,on=[unit,"period"],how="outer")
    out["ai"]=out["q7_yes"]
    out["ai_exp"]=out["q24_yes"]
    out["emp_net"]=out["q5_increased"]-out["q5_decreased"]
    out["emp_exp_net"]=out.get("q17_increase",np.nan)-out.get("q17_decrease",np.nan)
    out["dem_net"]=out["q10_increased"]-out["q10_decreased"]
    out["rev_net"]=out["q4_increased"]-out["q4_decreased"]
    out["price_net"]=out["q11_increased"]-out["q11_decreased"]
    out["t"]=out.period.astype(int)
    return out.sort_values([unit,"t"]).reset_index(drop=True)

if __name__=="__main__":
    for path,unit,tag in [(dp("old_Sector.xlsx"),"Sector","OLD sector"),
                          (dp("btos_Sector.xlsx"),"Sector","NEW sector"),
                          (dp("old_State.xlsx"),"State","OLD state"),
                          (dp("btos_State.xlsx"),"State","NEW state")]:
        B=build(path,unit)
        B=B[B.ai.notna()&B.emp_net.notna()]
        sd=B.groupby("t").ai.std()
        print(f"{tag:<12} units {B[unit].nunique():>3}  periods {B.t.nunique():>3}  cells {len(B):>5}  "
              f"AI mean {B.ai.mean():5.1f}%  cross-unit SD of AI: {sd.mean():.2f}pp "
              f"(first {sd.iloc[0]:.2f} -> last {sd.iloc[-1]:.2f})")
