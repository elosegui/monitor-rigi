# -*- coding: utf-8 -*-
import json, datetime
prov=json.load(open('iiep_prov.json'))
# ordenar por total desc
rows=sorted(prov.items(), key=lambda kv:-kv[1]['tot'])
data=[{"prov":k,"tot":round(v['tot']),"formal":round(v['formal']),"informal":round(v['informal']),
       "pfor":round(v['pfor']),"dir":round(v['dir']),"ind":round(v['ind']),"indu":round(v['indu']),
       "pstock":round(v['pstock'],2)} for k,v in rows]
AGG=dict(shock=5511, inv_anun=46708, n_aprob=22, producto=9022, va=4589,
         empleo=11382, e_dir=6055, e_ind=2391, e_indu=2937, formal=8021, informal=3361, pform=70,
         banda_lo=10609, banda_hi=12241)
UPD=datetime.date(2026,9,6).strftime("%d/%m/%Y")
DATAJS="const PROV=%s;\nconst AGG=%s;\nconst UPDATED=%s;"%(json.dumps(data,ensure_ascii=False),json.dumps(AGG),json.dumps(UPD))
open('/sessions/eloquent-awesome-mayer/mnt/RIGI/sitio_rigi/data.js','w',encoding='utf-8').write(DATAJS)
print("data.js OK -",len(data),"provincias")
