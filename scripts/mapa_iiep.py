# -*- coding: utf-8 -*-
import geopandas as gpd, json
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap, PowerNorm
from matplotlib.cm import ScalarMappable
d=json.load(open('iiep_prov.json'))
NAM={'Rio Negro':'Río Negro','Neuquen':'Neuquén','Cordoba':'Córdoba','Ciudad de Buenos Aires':'Ciudad Autónoma de Buenos Aires',
     'Tucuman':'Tucumán','Entre Rios':'Entre Ríos','Tierra del Fuego':'Tierra del Fuego, Antártida e Islas del Atlántico Sur'}
def nam(p): return NAM.get(p,p)
TOT={nam(p):v['tot'] for p,v in d.items()}
FOR={nam(p):v['formal'] for p,v in d.items()}; INF={nam(p):v['informal'] for p,v in d.items()}
g=gpd.read_file('/sessions/eloquent-awesome-mayer/mnt/RIGI/shapeProvincias/ign_provincia.shp')
g['total']=g['NAM'].map(TOT).fillna(0)
cent={}
for _,r in g[g['total']>0].iterrows():
    p=r.geometry.representative_point(); cent[r['NAM']]=(p.x,p.y)
def fmt(v): return f"{v:,.0f}".replace(",",".")
fig=plt.figure(figsize=(13.3,8.4)); axm=fig.add_axes([0.02,0.06,0.96,0.92])
cm=LinearSegmentedColormap.from_list('grn',['#e5f5e0','#a1d99b','#41ab5d','#238b45','#00441b'])
vmax=g['total'].max(); norm=PowerNorm(gamma=0.55,vmin=0,vmax=vmax)
g.plot(ax=axm,column='total',cmap=cm,norm=norm,edgecolor='#7f7f7f',linewidth=0.45)
g.boundary.plot(ax=axm,color='#7f7f7f',linewidth=0.2)
axm.set_xlim(-96,-32); axm.set_ylim(-58,-21); axm.set_aspect('equal'); axm.axis('off')
LX,RX=-94,-33
left =[("Catamarca",-25),("San Juan",-31),("Mendoza",-37.5),("Neuquén",-44),("Río Negro",-51)]
right=[("Jujuy",-24.5),("Salta",-29.5),("Córdoba",-34.5),("Buenos Aires",-40),("Santa Fe",-45.5),("Ciudad Autónoma de Buenos Aires",-50.5)]
anns=[]
def box(name,lx,ly,ha):
    if name not in cent: return
    cx,cy=cent[name]
    disp='CABA' if name.startswith('Ciudad') else name
    txt=f"Empleo total: {fmt(TOT.get(name,0))}\nFormal: {fmt(FOR.get(name,0))}\nInformal: {fmt(INF.get(name,0))}"
    ann=axm.annotate(txt,xy=(cx,cy),xytext=(lx,ly),ha=ha,va='center',fontsize=8,color='#1a1a1a',linespacing=1.5,
        bbox=dict(boxstyle='round,pad=0.42',fc='white',ec='#7f7f7f',lw=1.0,alpha=0.97),
        arrowprops=dict(arrowstyle='-',color='#7f7f7f',lw=0.9,connectionstyle='arc3,rad=0.05',shrinkA=4,shrinkB=3))
    anns.append((ann,disp))
for n,y in left: box(n,LX,y,'left')
for n,y in right: box(n,RX,y,'right')
fig.canvas.draw(); inv=axm.transData.inverted()
for ann,disp in anns:
    bb=ann.get_bbox_patch().get_window_extent()
    (x0,y0)=inv.transform((bb.x0,bb.y0)); (x1,y1)=inv.transform((bb.x1,bb.y1))
    axm.annotate(disp,xy=((x0+x1)/2,max(y0,y1)),xytext=(0,3),textcoords='offset points',
        ha='center',va='bottom',fontsize=10.5,fontweight='bold',color='#00441b',annotation_clip=False)
tt=sum(v['tot'] for v in d.values()); tf=sum(v['formal'] for v in d.values()); ti=sum(v['informal'] for v in d.values())
fig.text(0.5,0.045,f'Empleo del primer año — 22 proyectos RIGI aprobados: {fmt(tt)} puestos ({fmt(tf)} formales · {fmt(ti)} informales · {100*tf/tt:.0f}% formalidad)',ha='center',fontsize=10.5,fontweight='bold',color='#222')
fig.text(0.5,0.012,'Base: inversión comprometida Año 1 (IIEP, Monitor RIGI) = USD 5.511 M. Empleo directo+indirecto+inducido vía MIP provincial 2023; formalidad ajustada por provincia. Color = empleo total generado.',ha='center',fontsize=7,color='#666',wrap=True)
sm=ScalarMappable(cmap=cm,norm=norm); sm.set_array([])
cax=fig.add_axes([0.30,0.17,0.19,0.016]); cb=fig.colorbar(sm,cax=cax,orientation='horizontal')
cb.set_label('Empleo total (puestos)',fontsize=8); cb.ax.tick_params(labelsize=7)
cb.ax.xaxis.set_major_formatter(lambda x,_:f"{x:,.0f}".replace(",","."))
fig.savefig('/sessions/eloquent-awesome-mayer/mnt/RIGI/RIGI_mapa_empleo_iiep.png',dpi=200,bbox_inches='tight',facecolor='white')
fig.savefig('/sessions/eloquent-awesome-mayer/mnt/outputs/RIGI_mapa_empleo_iiep.png',dpi=200,bbox_inches='tight',facecolor='white')
print('mapa OK')
