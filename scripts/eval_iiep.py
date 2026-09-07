# -*- coding: utf-8 -*-
"""Impacto 1er ano con inversion comprometida Ano 1 (IIEP). Reusa el motor de eval_impact."""
import numpy as np
import eval_impact as M   # importa datos: comp, L, v, N, RATE, ixf, OWN, KIND, MULT, IND_RATE, fps, idxmap, Trow, secsh, provs, SEC, ecoef, c2p, COM
provs,SEC,N,RATE=M.provs,M.SEC,M.N,M.RATE
comp,L,v,fps,ecoef=M.comp,M.L,M.v,M.fps,M.ecoef
OWN,KIND,MULT,IND_RATE=M.OWN,M.KIND,M.MULT,M.IND_RATE
idxmap,Trow,secsh=M.idxmap,M.Trow,M.secsh
ixf=M.ixf
c2p,COM=M.c2p,M.COM

def run_rz(P):
    """P: lista (name, cat, provincias '|', rz_ano1_USDmill)."""
    f=np.zeros(N); Edir=np.zeros(N); Edirf=np.zeros(N); rzt=0
    for name,cat,ps,rz in P:
        c=comp[cat]; rzt+=rz; pl=ps.split('|'); sh=rz/len(pl)
        ob,eq,se=float(c['obra']),float(c['equipo_nac']),float(c['servicios'])
        io,ip_,ofm=float(c['int_obra']),float(c['int_oper']),float(c['oper_formal'])
        for pv in pl:
            amt=sh*RATE
            f[ixf(pv,'41T43')]+=amt*ob; f[ixf(pv,'26T28')]+=amt*eq; f[ixf(pv,'64T82')]+=amt*se
            eo=sh*io; ep=sh*ip_
            Edir[ixf(pv,'41T43')]+=eo; Edirf[ixf(pv,'41T43')]+=eo
            Edir[ixf(pv,OWN[cat])]+=ep; Edirf[ixf(pv,OWN[cat])]+=ep*ofm
    X=L@f; prodD=f.copy(); prodI=np.maximum(X-f,0); VAd=v*f; VAi=v*prodI
    tiVA=VAd.sum()+VAi.sum(); indVA=KIND*tiVA
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
    return dict(rz=rzt,prodD=prodD,prodI=prodI,ind_prod=ind_prod,VAd=VAd,VAi=VAi,ind_VA=ind_VA,
                Edir=Edir,Eind=Eind,Eindu=Eindu,Ef=Ef)

# ---- 22 APROBADOS con inv Ano 1 (IIEP base_completa.xlsx) ----
def pv(s):
    m={'Buenos Aires':'Buenos_Aires','Río Negro':'Rio_Negro','Santa Fe':'Santa_Fe','La Pampa':'La_Pampa',
       'San Juan':'San_Juan','Santiago del Estero':'Santiago_del_Estero','Neuquén':'Neuquen','Córdoba':'Cordoba',
       'Tucumán':'Tucuman','Salta':'Salta','Catamarca':'Catamarca','Mendoza':'Mendoza','Jujuy':'Jujuy','Chaco':'Chaco'}
    return '|'.join(m.get(x.strip(),x.strip()) for x in s.replace(';','|').split('|'))
APROB=[
 ("Gasoducto Perito Moreno (TGS)","PG_TRANS",pv("Neuquén; Buenos Aires"),393.617),
 ("Diablillos (AbraSilver)","MIN_METAL",pv("Salta; Catamarca"),98.500),
 ("Nuevo Gualcamayo (Aisa)","MIN_METAL",pv("San Juan"),46.741),
 ("Eolico Olavarria (PCR/Acindar)","ENERGIA",pv("Buenos Aires"),80.372),
 ("Solar El Quemado (YPF Luz)","ENERGIA",pv("Mendoza"),102.272),
 ("GNL Southern Energy","GNL",pv("Río Negro"),105.000),
 ("Sidersa","SIDER",pv("Buenos Aires"),142.874),
 ("PSJ Cobre Mendocino (Zonda)","MIN_METAL",pv("Mendoza"),40.542),
 ("Rincon litio (Rio Tinto)","MIN_LITIO",pv("Salta"),516.964),
 ("Fenix Fase 1B (Rio Tinto)","MIN_LITIO",pv("Catamarca"),92.662),
 ("Timbues (Terminales y Serv.)","INFRA",pv("Santa Fe"),91.702),
 ("VMOS","PG_TRANS",pv("Río Negro"),1318.000),
 ("Veladero (Barrick/Shandong)","MIN_METAL_LEACH",pv("San Juan"),79.229),
 ("Cauchari-Olaroz (Ganfeng)","MIN_LITIO",pv("Jujuy"),37.968),
 ("Rincon de Aranda (Pampa)","PG_UP",pv("Neuquén"),521.000),
 ("Sal de Oro II (Posco)","MIN_LITIO",pv("Salta; Catamarca"),90.917),
 ("Tres Quebradas 3Q (Zijin)","MIN_LITIO",pv("Catamarca"),107.537),
 ("Vicuna (BHP/Lundin)","MIN_METAL",pv("San Juan"),1004.657),
 ("Los Azules (McEwen)","MIN_METAL_LEACH",pv("San Juan"),33.513),
 ("YPF-Petrobras-Dow (gas)","PG_UP",pv("Neuquén; La Pampa; Río Negro; Buenos Aires"),121.614),
 ("San Matias (PAE)","PG_TRANS",pv("Río Negro; Neuquén"),454.000),
 ("Hombre Muerto Oeste (Galan)","MIN_LITIO",pv("Catamarca"),31.113),
]
if __name__=='__main__':
    r=run_rz(APROB); NP,NS=24,20
    def g(x): return np.asarray(x).reshape(NP,NS)
    E=g(r['Edir']+r['Eind']+r['Eindu']).sum(1); Ef=g(r['Ef']).sum(1); Einf=E-Ef
    prod=(r['prodD']+r['prodI']+r['ind_prod']).sum()/RATE; va=(r['VAd']+r['VAi']+r['ind_VA']).sum()/RATE
    print("Realizable Ano1 (IIEP): USD %.0f M"%r['rz'])
    print("Producto %.0f | VA %.0f | Empleo %.0f | formal %.0f (%.0f%%) | informal %.0f"%(
        prod,va,E.sum(),Ef.sum(),100*Ef.sum()/E.sum(),Einf.sum()))
    print("Empleo: directo %.0f indirecto %.0f inducido %.0f"%(r['Edir'].sum(),r['Eind'].sum(),r['Eindu'].sum()))
    np.savez('iiep_res.npz',**r)
