import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np
import warnings
warnings.filterwarnings('ignore')

# =====================================================
# DASHBOARD ML - ANALISIS DE ATRASOS LOGISTICOS
# =====================================================

plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.size'] = 9

COLORS = {
    'CUMPLE_SLA': '#2E8B57',
    'FES': '#F0A500',
    'SALDO': '#7B1FA2',
    'CREDITO': '#D3392C',
    'OPERACIONES': '#1F5A7A',
    'DESPACHO': '#04A2C3',
    'PICKING': '#A64383',
    'ALTO': '#D3392C',
    'MEDIO': '#F0A500',
    'BAJO': '#2E8B57'
}
BG = '#FCFBF7'

fig = plt.figure(figsize=(16, 10), facecolor=BG)
gs = gridspec.GridSpec(2, 2, hspace=0.35, wspace=0.3)

# =====================================================
# PANEL 1: Distribucion de probabilidad ML
# =====================================================
ax1 = fig.add_subplot(gs[0, 0])
if 'PROB_ML_ATRASO' in dataset.columns:
    probs = dataset['PROB_ML_ATRASO'].dropna()
    ax1.hist(probs, bins=20, color='#1F5A7A', edgecolor='white', linewidth=0.5, alpha=0.8)
    ax1.axvline(x=0.5, color='#D3392C', linestyle='--', linewidth=2, label='Umbral 50%')
    ax1.axvline(x=0.7, color='#F0A500', linestyle='--', linewidth=2, label='Umbral 70%')
    ax1.set_xlabel('Probabilidad de Atraso', fontsize=9)
    ax1.set_ylabel('Cantidad de Pedidos', fontsize=9)
    ax1.set_title('Distribucion de Probabilidad ML', fontsize=12, fontweight='bold', color='#1B365D', pad=10)
    ax1.legend(fontsize=8)
    ax1.spines['top'].set_visible(False)
    ax1.spines['right'].set_visible(False)
    ax1.set_facecolor(BG)

# =====================================================
# PANEL 2: Riesgo por nivel
# =====================================================
ax2 = fig.add_subplot(gs[0, 1])
if 'RIESGO_ATRASO' in dataset.columns:
    riesgo = dataset['RIESGO_ATRASO'].value_counts()
    orden = ['BAJO', 'MEDIO', 'ALTO']
    riesgo = riesgo.reindex(orden).dropna()
    colors_r = [COLORS.get(r, '#84807D') for r in riesgo.index]
    bars = ax2.bar(riesgo.index, riesgo.values, color=colors_r, edgecolor='white', linewidth=0.5, width=0.5)
    for bar, val in zip(bars, riesgo.values):
        pct = val / len(dataset) * 100
        ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
                 f'{val}\n({pct:.0f}%)', ha='center', va='bottom', fontsize=8, fontweight='bold')
    ax2.set_ylabel('Pedidos', fontsize=9)
    ax2.set_title('Distribucion por Nivel de Riesgo', fontsize=12, fontweight='bold', color='#1B365D', pad=10)
    ax2.spines['top'].set_visible(False)
    ax2.spines['right'].set_visible(False)
    ax2.set_facecolor(BG)

# =====================================================
# PANEL 3: Factor principal (solo atrasados)
# =====================================================
ax3 = fig.add_subplot(gs[1, 0])
if 'FACTOR_PRINCIPAL' in dataset.columns and 'ESTADO_SLA' in dataset.columns:
    atrasados = dataset[dataset['ESTADO_SLA'] == 'FUERA_SLA']
    if len(atrasados) > 0:
        factores = atrasados['FACTOR_PRINCIPAL'].value_counts()
        colors_f = [COLORS.get(f, '#84807D') for f in factores.index]
        bars3 = ax3.barh(factores.index, factores.values, color=colors_f, edgecolor='white', linewidth=0.5, height=0.6)
        for bar, val in zip(bars3, factores.values):
            ax3.text(bar.get_width() + 0.3, bar.get_y() + bar.get_height()/2,
                     str(val), va='center', fontsize=8, fontweight='bold')
        ax3.set_xlabel('Pedidos Fuera de SLA', fontsize=9)
        ax3.set_title('Factor Principal de Atraso', fontsize=12, fontweight='bold', color='#1B365D', pad=10)
        ax3.spines['top'].set_visible(False)
        ax3.spines['right'].set_visible(False)
        ax3.set_facecolor(BG)

# =====================================================
# PANEL 4: DH Real vs DH Predicho (top 20)
# =====================================================
ax4 = fig.add_subplot(gs[1, 1])
if 'DH_TOTAL' in dataset.columns and 'DH_PREDICHO_ML' in dataset.columns:
    cerrados = dataset[dataset['DH_TOTAL'].notna() & (dataset['DH_TOTAL'] > 0)].head(20)
    if len(cerrados) > 0:
        x = range(len(cerrados))
        width = 0.35
        ax4.bar([i - width/2 for i in x], cerrados['DH_TOTAL'], width, label='DH Real', color='#1F5A7A', alpha=0.8)
        ax4.bar([i + width/2 for i in x], cerrados['DH_PREDICHO_ML'], width, label='DH Predicho ML', color='#F0A500', alpha=0.8)
        ax4.set_xlabel('Pedido (indice)', fontsize=9)
        ax4.set_ylabel('Dias Habiles', fontsize=9)
        ax4.set_title('DH Real vs Predicho (Top 20)', fontsize=12, fontweight='bold', color='#1B365D', pad=10)
        ax4.legend(fontsize=8)
        ax4.spines['top'].set_visible(False)
        ax4.spines['right'].set_visible(False)
        ax4.set_facecolor(BG)

fig.suptitle('Dashboard ML - Analisis de Atrasos Logisticos', fontsize=16, fontweight='bold', color='#0B3558', y=0.98)
plt.show()
