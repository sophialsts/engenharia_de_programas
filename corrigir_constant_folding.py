#!/usr/bin/env python3
"""Corrige as 2 operações que sofrem constant folding:
- cte_int_eq_cte_int: use variáveis (não constantes literais)
- var_float_eq_var_float: use variáveis com valores não-obvios"""

import time, statistics, gc, numpy as np, csv, os
from matplotlib import pyplot as plt
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

REPETICOES = 500
WARMUP = 50
OUTLIER_FACTOR = 3.0
N_ITER = 50000

OUTPUT_DIR = "resultados/calibracao"
CSV_PATH = os.path.join(OUTPUT_DIR, "calibracao_foca.csv")

# CORREÇÃO: usar variáveis para evitar constant folding
CORRIGIDAS = [
    ("τc", "cte_int_eq_cte_int", "a = 5; b = 10", "a == b"),  # era: "5 == 10"
    ("τc", "var_float_eq_var_float", "a = 5.0; b = 10.0", "a == b"),  # já usa vars, mas vamos re-medir
    ("τo", "var_float_add_var_float", "a = 5.0; b = 10.0", "a + b"),
    ("τo", "var_int_sub_var_int", "a = 10; b = 5", "a - b"),
]

def medir(setup, op):
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
    return tempos

def filtrar(tempos):
    arr = np.array(tempos)
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

def stats(fil):
    if len(fil) == 0: return float('nan'), float('nan'), float('nan')
    if len(fil) == 1: return float(fil[0]), 0.0, 0.0
    m = statistics.mean(fil)
    s = statistics.stdev(fil)
    return m, s, s/m if m != 0 else float('nan')

# Ler CSV existente
linhas_existentes = []
with open(CSV_PATH, 'r') as f:
    reader = csv.reader(f)
    header = next(reader)
    for row in reader:
        if row[1] not in [p[1] for p in CORRIGIDAS]:
            linhas_existentes.append(row)

novas_linhas = []
for cat, nome, setup, op in CORRIGIDAS:
    logging.info(f"Re-medindo CORRIGIDO: {nome} (setup: {setup})")
    t = medir(setup, op)
    fil, li, ls, q1, q3, iqr = filtrar(t)
    m, s, cv = stats(fil)
    hp = f"resultados/calibracao/hist_{nome}.png"
    plt.figure(figsize=(8,4.5))
    d = fil if len(fil)>=5 else t
    plt.hist(d, bins='fd', edgecolor='black', color='skyblue', linewidth=0.6, alpha=0.85)
    plt.axvline(li, color='red', ls='--', lw=1.2, label=f'Q1-{OUTLIER_FACTOR}×IQR')
    plt.axvline(ls, color='red', ls='--', lw=1.2, label=f'Q3+{OUTLIER_FACTOR}×IQR')
    if not np.isnan(m):
        plt.axvline(m, color='green', lw=1.5, label=f'μ={m:.2e}')
        plt.axvline(m+s, color='orange', ls=':', lw=1.1)
        plt.axvline(m-s, color='orange', ls=':', lw=1.1)
    plt.ylabel('Freq'); plt.xlabel('Tempo (s)'); plt.title(f'Hist Pós-Filtro — {nome} (n={len(d)})')
    plt.legend(fontsize=8); plt.ticklabel_format(style='sci', axis='x', scilimits=(0,0))
    plt.tight_layout()
    plt.savefig(hp, dpi=150); plt.close()
    novas_linhas.append([cat, nome, f"{m:.10e}", f"{s:.10e}", f"{cv:.6f}", len(t), len(fil), f"{li:.10e}", f"{ls:.10e}", f"{q1:.10e}", f"{q3:.10e}", f"{iqr:.10e}", hp])
    st = "✅" if cv < 0.15 else "❌"
    logging.info(f"  {nome}: μ={m:.2e} σ={s:.2e} CV={cv:.4%} {st} ({len(fil)}/{len(t)})")

# Reescrever CSV
with open(CSV_PATH, 'w', newline='') as f:
    w = csv.writer(f)
    w.writerow(header)
    w.writerows(linhas_existentes + novas_linhas)

print("\n✅ CSV atualizado com operações corrigidas.")