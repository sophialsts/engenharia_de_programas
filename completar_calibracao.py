#!/usr/bin/env python3
"""Completa as operações restantes"""

import time, statistics, gc, numpy as np, csv, os
from matplotlib import pyplot as plt
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

REPETICOES = 300
WARMUP = 10
OUTLIER_FACTOR = 3.0
N_ITER = 10000

OUTPUT_DIR = "resultados/calibracao"
CSV_PATH = os.path.join(OUTPUT_DIR, "calibracao_foca.csv")

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
        lim_inf = np.percentile(arr, 2.5)
        lim_sup = np.percentile(arr, 97.5)
    else:
        lim_inf = q1 - OUTLIER_FACTOR * iqr
        lim_sup = q3 + OUTLIER_FACTOR * iqr
    fil = arr[(arr >= lim_inf) & (arr <= lim_sup)]
    return fil, lim_inf, lim_sup, q1, q3, iqr

def stats(fil):
    if len(fil) == 0: return float('nan'), float('nan'), float('nan')
    if len(fil) == 1: return float(fil[0]), 0.0, 0.0
    m = statistics.mean(fil)
    s = statistics.stdev(fil)
    return m, s, s/m if m != 0 else float('nan')

def hist(nome, brutos, fil, lim_i, lim_s, media, desv, q1, q3, iqr):
    plt.figure(figsize=(8,4.5))
    d = fil if len(fil)>=5 else brutos
    plt.hist(d, bins='fd', edgecolor='black', color='skyblue', linewidth=0.6, alpha=0.85)
    plt.axvline(lim_i, color='red', ls='--', lw=1.2, label=f'Q1-{OUTLIER_FACTOR}×IQR')
    plt.axvline(lim_s, color='red', ls='--', lw=1.2, label=f'Q3+{OUTLIER_FACTOR}×IQR')
    if not np.isnan(media):
        plt.axvline(media, color='green', lw=1.5, label=f'μ={media:.2e}')
        plt.axvline(media+desv, color='orange', ls=':', lw=1.1)
        plt.axvline(media-desv, color='orange', ls=':', lw=1.1)
    plt.ylabel('Freq'); plt.xlabel('Tempo (s)'); plt.title(f'Hist Pós-Filtro — {nome} (n={len(d)})')
    plt.legend(fontsize=8); plt.ticklabel_format(style='sci', axis='x', scilimits=(0,0))
    plt.tight_layout()
    safe = nome.replace(' ','_').replace('<','_').replace('>','_').replace('=','_').replace('/','_').replace('*','_').replace('%','_').replace('+','_').replace('-','_')
    p = os.path.join(OUTPUT_DIR, f"hist_{safe}.png")
    plt.savefig(p, dpi=150); plt.close()
    return p

RESTANTES = [
    ("τo", "var_float_mul_var_float", "a = 5.0; b = 10.0", "a * b"),
    ("τo", "var_float_div_var_float", "a = 10.0; b = 5.0", "a / b"),
    ("τo", "var_int_floordiv_var_int", "a = 10; b = 3", "a // b"),
    ("τo", "var_int_mod_var_int", "a = 10; b = 3", "a % b"),
    ("τf", "math_sqrt_float", "import math; a = 25.0", "math.sqrt(a)"),
    ("τf", "abs_int", "a = -5", "abs(a)"),
    ("τf", "list_append", "lst = []; a = 5", "lst.append(a)"),
    ("τf", "len_list", "lst = [0]*100", "len(lst)"),
]

with open(CSV_PATH, 'a', newline='') as f:
    w = csv.writer(f)
    for cat, nome, setup, op in RESTANTES:
        logging.info(f"Medindo: {nome}")
        t = medir(setup, op)
        fil, li, ls, q1, q3, iqr = filtrar(t)
        m, s, cv = stats(fil)
        hp = hist(nome, t, fil, li, ls, m, s, q1, q3, iqr)
        w.writerow([cat, nome, f"{m:.10e}", f"{s:.10e}", f"{cv:.6f}", len(t), len(fil), f"{li:.10e}", f"{ls:.10e}", f"{q1:.10e}", f"{q3:.10e}", f"{iqr:.10e}", hp])
        f.flush()
        st = "✅" if cv < 0.15 else "❌"
        logging.info(f"  {nome}: μ={m:.2e} σ={s:.2e} CV={cv:.4%} {st} ({len(fil)}/{len(t)})")

print("\n✅ Concluído! CSV atualizado.")