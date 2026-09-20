#!/usr/bin/env python3
"""Gera os 3 painéis gráficos obrigatórios (Scatter + Hist Bruto + Hist Filtrado)
para cada macro-primitiva: τa, τc, τo"""

import time, statistics, gc, numpy as np, os, csv
from matplotlib import pyplot as plt
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

REPETICOES = 300
WARMUP = 10
OUTLIER_FACTOR = 3.0
N_ITER = 10000

OUTPUT_DIR = "resultados/calibracao/paineis"
os.makedirs(OUTPUT_DIR, exist_ok=True)
CSV_PATH = "resultados/calibracao/calibracao_foca.csv"

# Agrupar operações por categoria
CAT_OPERACOES = {
    "τa": [
        ("var_int_cte_int", "a = 0", "a = 5"),
        ("var_float_cte_float", "a = 0.0", "a = 5.0"),
        ("var_bool_cte_bool", "a = False", "a = True"),
        ("var_int_var_int", "a = 0; b = 5", "a = b"),
        ("var_float_var_float", "a = 0.0; b = 5.0", "a = b"),
    ],
    "τc": [
        ("cte_int_eq_cte_int", "a = 5; b = 10", "a == b"),
        ("var_int_eq_cte_int", "a = 5", "a == 10"),
        ("var_int_eq_var_int", "a = 5; b = 10", "a == b"),
        ("var_float_eq_var_float", "a = 5.0; b = 10.0", "a == b"),
        ("var_int_ne_var_int", "a = 5; b = 10", "a != b"),
        ("var_int_gt_var_int", "a = 5; b = 10", "a > b"),
        ("var_float_lt_cte_float", "a = 5.0", "a < 10.0"),
    ],
    "τo": [
        ("var_int_add_cte_int", "a = 5", "a + 10"),
        ("var_int_add_var_int", "a = 5; b = 10", "a + b"),
        ("var_float_add_var_float", "a = 5.0; b = 10.0", "a + b"),
        ("var_int_sub_var_int", "a = 10; b = 5", "a - b"),
        ("var_int_mul_var_int", "a = 5; b = 10", "a * b"),
        ("var_float_mul_var_float", "a = 5.0; b = 10.0", "a * b"),
        ("var_float_div_var_float", "a = 10.0; b = 5.0", "a / b"),
        ("var_int_floordiv_var_int", "a = 10; b = 3", "a // b"),
        ("var_int_mod_var_int", "a = 10; b = 3", "a % b"),
    ],
}

def medir_brutos(setup, op):
    """Coleta tempos BRUTOS (sem filtro) para scatter e hist bruto"""
    for _ in range(WARMUP):
        exec(setup)
        for _ in range(N_ITER): exec(op)
    gc_old = gc.isenabled()
    gc.disable()
    tempos = []
    try:
        for _ in range(REPETICOES):
            exec(setup)
            tic = time.perf_counter()
            for _ in range(N_ITER): exec(op)
            toc = time.perf_counter()
            tempos.append((toc - tic) / N_ITER)
    finally:
        if gc_old: gc.enable()
    return np.array(tempos)

def filtrar_iqr(arr):
    q1, q3 = np.percentile(arr, [25, 75])
    iqr = q3 - q1
    if iqr == 0:
        li = np.percentile(arr, 2.5)
        ls = np.percentile(arr, 97.5)
    else:
        li = q1 - OUTLIER_FACTOR * iqr
        ls = q3 + OUTLIER_FACTOR * iqr
    fil = arr[(arr >= li) & (arr <= ls)]
    return fil, li, ls, q1, q3, iqr

for cat, ops in CAT_OPERACOES.items():
    logging.info(f"\n=== Gerando painel para {cat} ===")
    
    # Usar a PRIMEIRA operação como representante da categoria para o painel
    # (o relatório pede 1 painel por macro-primitiva)
    nome_rep, setup_rep, op_rep = ops[0]
    logging.info(f"  Medindo {nome_rep} para painel...")
    
    # Coletar dados brutos
    tempos_brutos = medir_brutos(setup_rep, op_rep)
    tempos_filtrados, li, ls, q1, q3, iqr = filtrar_iqr(tempos_brutos)
    media = np.mean(tempos_filtrados) if len(tempos_filtrados) > 0 else np.nan
    desv = np.std(tempos_filtrados, ddof=1) if len(tempos_filtrados) > 1 else 0.0
    
    # ============================================================
    # PAINEL: 3 subplots (Scatter | Hist Bruto | Hist Filtrado)
    # ============================================================
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))
    fig.suptitle(f'Painel de Estabilidade — {cat} ({nome_rep})', fontsize=14, fontweight='bold')
    
    # 1. SCATTER TEMPORAL (Iteração × Tempo)
    ax = axes[0]
    ax.plot(tempos_brutos, 'o-', color='tab:blue', markersize=2, linewidth=0.5, alpha=0.6, label='Tempo bruto')
    # Destacar outliers
    outliers_idx = np.where((tempos_brutos < li) | (tempos_brutos > ls))[0]
    if len(outliers_idx) > 0:
        ax.scatter(outliers_idx, tempos_brutos[outliers_idx], color='red', s=20, zorder=5, label=f'Outliers ({len(outliers_idx)})')
    # Média e ±σ filtrados
    if not np.isnan(media):
        ax.axhline(media, color='green', ls='--', lw=1.5, label=f'Média filtrada {media:.2e}s')
        ax.axhline(media + desv, color='green', ls=':', lw=1, alpha=0.7)
        ax.axhline(media - desv, color='green', ls=':', lw=1, alpha=0.7)
        ax.fill_between(range(len(tempos_brutos)), media - desv, media + desv, color='green', alpha=0.08)
    ax.set_ylabel('Tempo por operação (s)')
    ax.set_xlabel('Iteração (réplica)')
    ax.set_title('1. Scatter Temporal — Dispersão Total')
    ax.legend(fontsize=8)
    ax.ticklabel_format(style='sci', axis='y', scilimits=(0,0))
    
    # 2. HISTOGRAMA BRUTO
    ax = axes[1]
    ax.hist(tempos_brutos, bins='fd', edgecolor='black', color='lightcoral', linewidth=0.6, alpha=0.85, density=False)
    if not np.isnan(media):
        ax.axvline(media, color='red', ls='--', lw=1.2, label=f'Média filtrada')
    ax.set_ylabel('Frequência')
    ax.set_xlabel('Tempo (s)')
    ax.set_title(f'2. Histograma Bruto — Assimetria/Caudas (n={len(tempos_brutos)})')
    ax.legend(fontsize=8)
    ax.ticklabel_format(style='sci', axis='x', scilimits=(0,0))
    
    # 3. HISTOGRAMA PÓS-FILTRAGEM
    ax = axes[2]
    dados = tempos_filtrados if len(tempos_filtrados) >= 5 else tempos_brutos
    ax.hist(dados, bins='fd', edgecolor='black', color='skyblue', linewidth=0.6, alpha=0.85, density=False)
    ax.axvline(li, color='red', ls='--', lw=1.2, label=f'Lim inf (Q1-{OUTLIER_FACTOR}×IQR)')
    ax.axvline(ls, color='red', ls='--', lw=1.2, label=f'Lim sup (Q3+{OUTLIER_FACTOR}×IQR)')
    if not np.isnan(media):
        ax.axvline(media, color='green', lw=1.5, label=f'Média {media:.2e}s')
        ax.axvline(media + desv, color='orange', ls=':', lw=1.1, label='±1σ')
        ax.axvline(media - desv, color='orange', ls=':', lw=1.1)
    ax.set_ylabel('Frequência')
    ax.set_xlabel('Tempo (s)')
    ax.set_title(f'3. Histograma Pós-Filtragem — Normalidade (n={len(dados)})')
    ax.legend(fontsize=8)
    ax.ticklabel_format(style='sci', axis='x', scilimits=(0,0))
    
    plt.tight_layout()
    painel_path = os.path.join(OUTPUT_DIR, f"painel_{cat}.png")
    plt.savefig(painel_path, dpi=200)
    plt.close()
    logging.info(f"  ✅ Painel salvo: {painel_path}")

print(f"\n✅ 3 painéis gerados em: {OUTPUT_DIR}/")
print("   - painel_τa.png")
print("   - painel_τc.png")
print("   - painel_τo.png")