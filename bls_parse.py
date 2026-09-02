import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from datapaths import dp
import re, numpy as np, pandas as pd

ROW=re.compile(r'<tr[^>]*>\s*<th id="([^"]+)"[^>]*>(.*?)</th>(.*?)</tr>',re.S)
VAL=re.compile(r'<span class="datavalue">([^<]*)</span>')
TAG=re.compile(r'<[^>]+>')

def num(s):
    s=s.replace(',','').replace('–','').strip()
    try: return float(s)
    except: return np.nan

def load(path, year):
    h=open(path).read()
    rows=[]
    for rid,th,rest in ROW.findall(h):
        title=TAG.sub(' ',th)
        title=re.sub(r'\s+',' ',title).replace('\xa0',' ').strip()
        vals=[num(v) for v in VAL.findall(rest)]
        if title and vals: rows.append((rid,title,vals))
    ids=set(r[0] for r in rows)
    # a leaf is a row whose id is not a strict prefix of any other row's id
    leaf=[r for r in rows if not any(o!=r[0] and o.startswith(r[0]+'.') for o in ids)]
    out=pd.DataFrame({"rid":[r[0] for r in leaf],"title":[r[1] for r in leaf],
                      "tot":[r[2][0] if len(r[2])>0 else np.nan for r in leaf],
                      "a16_19":[r[2][1] if len(r[2])>1 else np.nan for r in leaf],
                      "a20_24":[r[2][2] if len(r[2])>2 else np.nan for r in leaf],
                      "a25_34":[r[2][3] if len(r[2])>3 else np.nan for r in leaf]})
    out["year"]=year
    tot_all=[r[2][0] for r in rows if r[1].lower().startswith("total employed")]
    out.attrs["total"]=tot_all[0] if tot_all else np.nan
    return out

if __name__=="__main__":
    for y in [2011,2015,2019,2022]:
        d=load(dp(f"aa{y}.htm"),y)
        d=d[~d.title.str.lower().str.startswith("total employed")]
        print(f"{y}: {len(d)} leaf rows, sum {d.tot.sum():,.0f}k vs published total {d.attrs['total']:,.0f}k "
              f"({100*d.tot.sum()/d.attrs['total']:.1f}%)")
