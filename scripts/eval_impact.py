import numpy as np, json, csv, openpyxl
REP='/sessions/eloquent-awesome-mayer/mnt/RIGI/replicacion'
o=json.load(open(REP+'/rep_orden.json')); provs=o['provs']; SEC=o['SEC']; N=480; RATE=296.0
meta=list(csv.DictReader(open(REP+'/rep_meta.csv')))
vbp=np.array([float(r['vbp']) for r in meta]); vbps=np.where(vbp==0,1e-9,vbp)
vab=np.array([float(r['vab']) for r in meta]); v=vab/vbps; cons=np.array([float(r['consumo']) for r in meta]); emp=np.array([float(r['empleo']) for r in meta]); ecoef=emp/vbps
Z=np.loadtxt(REP+'/rep_Z.csv',delimiter=','); L=np.linalg.inv(np.eye(N)-Z/vbps[None,:])
comp={r['categoria']:r for r in csv.DictReader(open(REP+'/rep_composicion.csv'))}
OWN={'PG_UP':'05T06','PG_TRANS':'35T39','GNL':'35T39','MIN_METAL':'07T08','MIN_METAL_LEACH':'07T08','MIN_LITIO':'07T08','ENERGIA':'35T39','SIDER':'24T25','INFRA':'41T43'}
MULT=1.3949; IND_RATE=0.3477; KIND=0.353
def ixf(pv,s): return provs.index(pv)*20+SEC.index(s)
# formalidad prov x sector
we=openpyxl.load_workbook('/sessions/eloquent-awesome-mayer/mnt/uploads/empleo_prov_sec_ipf.xlsx',read_only=True,data_only=True)['empleo_ipf']
reg=np.zeros(N); tt=np.zeros(N)
for pv,sec,cat,val in we.iter_rows(min_row=2,values_only=True):
    if pv in provs and sec in SEC and val:
        k=ixf(pv,sec); tt[k]+=float(val)
        if cat=='registrado': reg[k]+=float(val)
fps=np.where(tt>0,reg/np.where(tt==0,1,tt),0.5)
# comercio interprovincial (dest x origen), fila-normalizada
wc=openpyxl.load_workbook('/sessions/eloquent-awesome-mayer/mnt/RIGI/MATRIZ DE COMERCIO INTRAPROVINCIAL.xlsx',read_only=True,data_only=True)['TOTAL TOTAL']
rws=list(wc.iter_rows(values_only=True))
COM=['CAPITAL','BUENOS AIRES','CÓRDOBA','SANTA FE','ENTRE RÍOS','LA PAMPA','MENDOZA','SAN JUAN','SAN LUIS','CATAMARCA','CHACO','CORRIENTES','FORMOSA','JUJUY','LA RIOJA','MISIONES','SALTA','SANTIAGO DEL ESTERO','TUCUMÁN','CHUBUT','NEUQUÉN','RÍO NEGRO','SANTA CRUZ','TIERRA DEL FUEGO']
c2p={'CAPITAL':'Ciudad_de_Buenos_Aires','BUENOS AIRES':'Buenos_Aires','CÓRDOBA':'Cordoba','SANTA FE':'Santa_Fe','ENTRE RÍOS':'Entre_Rios','LA PAMPA':'La_Pampa','MENDOZA':'Mendoza','SAN JUAN':'San_Juan','SAN LUIS':'San_Luis','CATAMARCA':'Catamarca','CHACO':'Chaco','CORRIENTES':'Corrientes','FORMOSA':'Formosa','JUJUY':'Jujuy','LA RIOJA':'La_Rioja','MISIONES':'Misiones','SALTA':'Salta','SANTIAGO DEL ESTERO':'Santiago_del_Estero','TUCUMÁN':'Tucuman','CHUBUT':'Chubut','NEUQUÉN':'Neuquen','RÍO NEGRO':'Rio_Negro','SANTA CRUZ':'Santa_Cruz','TIERRA DEL FUEGO':'Tierra_del_Fuego'}
Mc=np.array([[float(x) if isinstance(x,(int,float)) else 0 for x in rws[2+i][3:27]] for i in range(24)])
Trow=Mc/Mc.sum(1,keepdims=True); idxmap=[provs.index(c2p[c]) for c in COM]
secsh=np.array([sum(cons[p*20+s] for p in range(24)) for s in range(20)]); secsh/=secsh.sum()
def realiz(a,m,mo):
    if mo=="complete": return 0.9*a
    if mo=="ramp": return 0.3*a
    if a>=2000: return 200.0
    return min(0.2*m,a)
def run(P):
    f=np.zeros(N); Edir=np.zeros(N); Edirf=np.zeros(N); rzt=0
    for name,cat,ps,anun,minr,mo in P:
        c=comp[cat]; base='MIN_METAL' if cat=='MIN_METAL_LEACH' else cat
        rz=realiz(anun,minr,mo); rzt+=rz; pl=ps.split('|'); sh=rz/len(pl)
        ob,eq,se=float(c['obra']),float(c['equipo_nac']),float(c['servicios']); io,ip_,ofm=float(c['int_obra']),float(c['int_oper']),float(c['oper_formal'])
        for pv in pl:
            amt=sh*RATE
            f[ixf(pv,'41T43')]+=amt*ob; f[ixf(pv,'26T28')]+=amt*eq; f[ixf(pv,'64T82')]+=amt*se
            eo=sh*io; ep=sh*ip_
            Edir[ixf(pv,'41T43')]+=eo; Edirf[ixf(pv,'41T43')]+=eo
            Edir[ixf(pv,OWN[cat])]+=ep; Edirf[ixf(pv,OWN[cat])]+=ep*ofm
    X=L@f; prodD=f.copy(); prodI=np.maximum(X-f,0); VAd=v*f; VAi=v*prodI
    tiVA=VAd.sum()+VAi.sum(); indVA=KIND*tiVA
    # inducido local por comercio
    tiVA_p=np.array([sum((VAd+VAi)[p*20+s] for s in range(20)) for p in range(24)]); Wsh=tiVA_p/max(tiVA_p.sum(),1)
    Wc_=np.array([Wsh[idxmap[i]] for i in range(24)]); pwc=Wc_@Trow; pw=np.zeros(24)
    for i,cc in enumerate(COM): pw[provs.index(c2p[cc])]=pwc[i]
    cnew=np.zeros(N)
    for p in range(24):
        for s in range(20): cnew[p*20+s]=pw[p]*secsh[s]
    if cnew.sum()>0: cnew/=cnew.sum()
    ind_prod=L@(cnew*(indVA/max((v*(L@cnew)).sum(),1e-9))); ind_VA=v*ind_prod
    Edt=Edir.sum(); Ei=Edt*(MULT-1); Eu=(Edt+Ei)*IND_RATE
    wi=ecoef*prodI; Eind=wi/max(wi.sum(),1e-9)*Ei; wu=np.maximum(ecoef*ind_prod,0); Eindu=wu/max(wu.sum(),1e-9)*Eu
    obra=np.zeros(N)
    for p in range(24): obra[p*20+SEC.index('41T43')]=Edir[p*20+SEC.index('41T43')]
    Ef=obra+(Edir-obra)*fps+Eind*fps+Eindu*fps
    return dict(rz=rzt,prodD=prodD,prodI=prodI,ind_prod=ind_prod,VAd=VAd,VAi=VAi,ind_VA=ind_VA,Edir=Edir,Eind=Eind,Eindu=Eindu,Ef=Ef)
# ---- EN EVALUACIÓN (16) ----  data center->ENERGIA (alta import), Pampa Fértil->SIDER
EV=[("Argentina LNG","GNL","Rio_Negro",51000,600,"floor"),
("Data center IA","ENERGIA","Neuquen|Rio_Negro|Chubut",25000,200,"floor"),
("Bajo del Choique","PG_UP","Neuquen",12240,600,"floor"),
("El Pachón","MIN_METAL","San_Juan",11600,200,"floor"),
("Agua Rica (MARA)","MIN_METAL","Catamarca",6699,200,"floor"),
("Los Toldos","PG_UP","Neuquen",6391,600,"floor"),
("Pozuelos Pastos Grandes","MIN_LITIO","Salta",4245,200,"floor"),
("Industrializ. líq. de gas","PG_TRANS","Neuquen",3000,300,"floor"),
("Pampa Fértil (fertilizantes)","SIDER","Buenos_Aires",2400,200,"floor"),
("Sal de Vida","MIN_LITIO","Catamarca",1380,200,"floor"),
("Jama Solaroz","MIN_LITIO","Jujuy",1151,200,"floor"),
("Duplicar Norte","PG_TRANS","Neuquen|Rio_Negro",1000,300,"floor"),
("Litio Ángeles","MIN_LITIO","Salta",726,200,"floor"),
("Midstream RDA","PG_TRANS","Neuquen",295,300,"floor"),
("Arenas de Cercanías","MIN_METAL","Rio_Negro",233,200,"floor"),
("Eólico La Rinconada","ENERGIA","Buenos_Aires",219,200,"floor")]
r=run(EV)
print("EN EVALUACIÓN (16) — realizable 1er año %d M (todos piso, greenfield presentados)"%round(r['rz']))
print("Producto %d | VA %d | Empleo %d | formal %d (%.0f%%)"%(round((r['prodD'].sum()+r['prodI'].sum()+r['ind_prod'].sum())/RATE),round((r['VAd'].sum()+r['VAi'].sum()+r['ind_VA'].sum())/RATE),round(r['Edir'].sum()+r['Eind'].sum()+r['Eindu'].sum()),round(r['Ef'].sum()),100*r['Ef'].sum()/(r['Edir'].sum()+r['Eind'].sum()+r['Eindu'].sum())))
np.savez('eval_res.npz',**r)
