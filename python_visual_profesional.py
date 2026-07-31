import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np
import pandas as pd

# Modelo auditado: regresión logística (P incumplir SLA) + regresión lineal (DH esperados).
df = dataset.copy()
for c in ['PROB_ML_ATRASO','DH_PREDICHO_ML','DIAS_ACTUALES_DH','PRIORIDAD_SCORE','VALOR_MM','DH_TOTAL']:
    if c in df.columns:
        df[c] = pd.to_numeric(df[c], errors='coerce')
if 'ES_PENDIENTE' in df.columns:
    pending = df[df['ES_PENDIENTE'].astype(str).str.lower().isin(['true','1'])].copy()
else:
    pending = df[df['ESTADO_SLA'].eq('PENDIENTE')].copy()
if pending.empty:
    pending = df.copy()

NAVY='#1B365D'; BLUE='#1976D2'; GREEN='#2E8B57'; ORANGE='#D97706'; RED='#D3392C'; GRAY='#6B7280'; BG='#F7F9FC'; YELLOW='#F0A500'
plt.rcParams['font.family']='sans-serif'
fig=plt.figure(figsize=(16,9),facecolor=BG)
gs=gridspec.GridSpec(3,2,height_ratios=[0.55,2.2,2.5],hspace=0.48,wspace=0.28)

# KPI model audit
ax0=fig.add_subplot(gs[0,:]); ax0.axis('off')
first=df.iloc[0] if len(df) else {}
metrics=[
 ('Entrenamiento', int(first.get('N_ENTRENAMIENTO_FINAL',0) or 0), '#1B365D'),
 ('AUC logística', float(first.get('AUC_TEST',np.nan)), BLUE),
 ('MAE lineal', float(first.get('MAE_DIAS_TEST',np.nan)), ORANGE),
 ('RMSE lineal', float(first.get('RMSE_DIAS_TEST',np.nan)), RED),
 ('Pendientes', len(pending), NAVY),
 ('Alto/atrasado', int(pending['RIESGO_ATRASO'].isin(['ALTO','ATRASADO']).sum()) if 'RIESGO_ATRASO' in pending else 0, RED)
]
for i,(label,val,color) in enumerate(metrics):
    x=i/6
    ax0.add_patch(plt.Rectangle((x+0.005,0.08),0.155,0.82,facecolor='white',edgecolor='#D7E0EA',linewidth=1,transform=ax0.transAxes))
    ax0.text(x+0.082,0.68,label,ha='center',va='center',fontsize=9,color=GRAY,fontweight='bold',transform=ax0.transAxes)
    txt=f'{val:.1%}' if label=='AUC logística' else f'{val:.2f} DH' if 'lineal' in label else f'{int(val):,}'.replace(',','.')
    ax0.text(x+0.082,0.35,txt,ha='center',va='center',fontsize=17,color=color,fontweight='bold',transform=ax0.transAxes)

# Risk distribution pending
ax1=fig.add_subplot(gs[1,0])
order=['BAJO','MEDIO','ALTO','ATRASADO']
counts=pending['RIESGO_ATRASO'].value_counts().reindex(order,fill_value=0)
colors=[GREEN,ORANGE,RED,'#8B0000']
bars=ax1.bar(counts.index,counts.values,color=colors,width=.58)
for b,v in zip(bars,counts.values):
    ax1.text(b.get_x()+b.get_width()/2,b.get_height()+max(counts.max()*.03,.3),str(int(v)),ha='center',fontsize=9,fontweight='bold')
ax1.set_title('Pedidos pendientes por nivel de riesgo',color=NAVY,fontweight='bold')
ax1.set_ylabel('Pedidos'); ax1.grid(axis='y',alpha=.2); ax1.spines[['top','right']].set_visible(False)

# Predicted days vs SLA
ax2=fig.add_subplot(gs[1,1])
vals=pending['DH_PREDICHO_ML'].dropna()
if len(vals):
    bins=np.arange(0,max(12,int(np.ceil(vals.max())))+1,1)
    ax2.hist(vals,bins=bins,color=BLUE,alpha=.8,edgecolor='white')
ax2.axvline(4,color=ORANGE,linestyle='--',linewidth=1.8,label='SLA interno Santiago 4 DH')
ax2.axvline(5,color=RED,linestyle='--',linewidth=1.8,label='SLA interno Regiones 5 DH')
ax2.set_title('Días hábiles totales predichos',color=NAVY,fontweight='bold')
ax2.set_xlabel('DH predichos'); ax2.set_ylabel('Pedidos'); ax2.legend(frameon=False); ax2.spines[['top','right']].set_visible(False)

# Factors in current filter
ax3=fig.add_subplot(gs[2,0])
factors=pending['FEATURE_TOP1'].fillna('Sin factor').value_counts().head(8).sort_values()
ax3.barh(factors.index,factors.values,color=YELLOW,edgecolor='white')
for y,v in enumerate(factors.values): ax3.text(v+.15,y,str(int(v)),va='center',fontsize=8,fontweight='bold')
ax3.set_title('Factor predictivo predominante en el contexto',color=NAVY,fontweight='bold')
ax3.set_xlabel('Pedidos pendientes'); ax3.spines[['top','right']].set_visible(False)

# Prioritized pending table
ax4=fig.add_subplot(gs[2,1]); ax4.axis('off')
top=pending.sort_values(['PRIORIDAD_SCORE','PROB_ML_ATRASO'],ascending=False).head(9)
cols=['PED_NUMERO_PEDIDO','CLIENTE','PROB_ML_ATRASO','DH_PREDICHO_ML','HITO_ACTUAL']
show=top[cols].copy() if all(c in top.columns for c in cols) else top.head(9)
if not show.empty:
    show['PROB_ML_ATRASO']=show['PROB_ML_ATRASO'].map(lambda x:f'{x:.1%}' if pd.notna(x) else '--')
    show['DH_PREDICHO_ML']=show['DH_PREDICHO_ML'].map(lambda x:f'{x:.1f}' if pd.notna(x) else '--')
    show['CLIENTE']=show['CLIENTE'].astype(str).str.slice(0,22)
    show['HITO_ACTUAL']=show['HITO_ACTUAL'].astype(str).str.slice(0,22)
    show.columns=['Pedido','Cliente','Riesgo','DH pred.','Hito actual']
    table=ax4.table(cellText=show.values,colLabels=show.columns,cellLoc='left',colLoc='left',loc='center',colWidths=[.16,.28,.13,.12,.27])
    table.auto_set_font_size(False); table.set_fontsize(7.6); table.scale(1,1.42)
    for (r,c),cell in table.get_celld().items():
        cell.set_edgecolor('#E1E6ED')
        if r==0: cell.set_facecolor(NAVY); cell.get_text().set_color('white'); cell.get_text().set_fontweight('bold')
        elif r%2==0: cell.set_facecolor('#F3F6FA')
ax4.set_title('Ranking operativo de pedidos pendientes',color=NAVY,fontweight='bold',pad=8)

version=str(first.get('MODELO_VERSION','Modelo ML'))
fig.suptitle('Python · Predicción de incumplimiento SLA y días de ciclo',fontsize=16,fontweight='bold',color=NAVY,y=.985)
fig.text(.5,.955,f'{version} · Logística: probabilidad de atraso · Lineal: días estimados',ha='center',fontsize=9,color=GRAY)
plt.show()