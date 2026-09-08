import time
import statistics
import gc
import numpy as np
from matplotlib import pyplot as plt
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

lista_n = [1000, 10000, 100000]

REPETICOES = 500  # mais amostras => histograma mais próximo do normal
WARMUP = 20       # iterações de aquecimento descartadas (cache, branch predictor)

for n in lista_n:
    # --- aquecimento ---
    for _ in range(WARMUP):
        for i in range(n):
            x = 1

    tt = []
    gc_old = gc.isenabled()
    gc.disable()
    try:
        for j in range(REPETICOES):
            tic = time.perf_counter()  # alta resolução, monotônico (corrige time.time)
            for i in range(n):
                x = 1
            toc = time.perf_counter()
            tt.append(toc - tic)
    finally:
        if gc_old:
            gc.enable()

    # --- filtragem de outliers via IQR (remove only distant outliers) ---
    OUTLIER_FACTOR = 3.0  # multiplier to keep only far outliers
    q1, q3 = np.percentile(tt, [25, 75])
    iqr = q3 - q1
    if iqr == 0:
        # fallback using extreme percentiles when data is nearly constant
        limite_inf = np.percentile(tt, 2.5)
        limite_sup = np.percentile(tt, 97.5)
    else:
        limite_inf = q1 - OUTLIER_FACTOR * iqr
        limite_sup = q3 + OUTLIER_FACTOR * iqr

    tt_filtrado = [x for x in tt if limite_inf <= x <= limite_sup]

    # estatísticas no vetor filtrado
    if len(tt_filtrado) == 0:
        media = desvio = cv = float('nan')
    elif len(tt_filtrado) == 1:
        media = statistics.mean(tt_filtrado)
        desvio = 0.0
        cv = 0.0 if media != 0 else float('nan')
    else:
        media = statistics.mean(tt_filtrado)
        desvio = statistics.stdev(tt_filtrado)
        cv = desvio / media if media != 0 else float('nan')

    # Improved, multi‑line log output for better readability
    print(f"""
=== Result for n={n} ===
IQR filter : [{limite_inf:.8f}, {limite_sup:.8f}]
Samples    : total={len(tt)}  filtered={len(tt_filtrado)}
Mean       : {media:.8f}
Std dev    : {desvio:.8f}
CV         : {cv:.4%}
Q1         : {q1:.8f}
Q3         : {q3:.8f}
IQR        : {iqr:.8f}
""")
    # --- Gráfico 1: série temporal ---
    plt.figure(figsize=(10, 4))
    # linha base com todos os pontos
    plt.plot(tt, linestyle='-', color='tab:blue', linewidth=1, alpha=0.6, label='tempo bruto')
    # destaca outliers em vermelho

    outliers_val = [tt[i] for i in outliers_idx]
    if outliers_idx:
        plt.scatter(outliers_idx, outliers_val, color='red', s=18, zorder=5, label=f'outliers ({len(outliers_idx)})')
    # linha de média e banda +- desvio
    if not np.isnan(media):
        plt.axhline(media, color='green', linestyle='--', linewidth=1.2, label=f'média filtrada {media:.6f}s')
        plt.axhline(media + desvio, color='green', linestyle=':', linewidth=1, alpha=0.7)
        plt.axhline(media - desvio, color='green', linestyle=':', linewidth=1, alpha=0.7)
        plt.fill_between(range(len(tt)), media - desvio, media + desvio, color='green', alpha=0.08)
    plt.ylabel('Tempo (s)')
    plt.xlabel('Iteração')
    plt.title(f'n = {n} — Tempo por iteração (perf_counter, {REPETICOES} reps, GC off + warmup)')
    plt.legend(fontsize=8)
    plt.tight_layout()
    plt.savefig(f'tempo_n_{n}.png', dpi=150)
    print(f'Gráfico salvo como tempo_n_{n}.png')
    plt.close()

    # --- Gráfico 2: histograma correto (corrige "1 barra por tempo") ---
    # Antes: Counter + round + bar categórico criava centenas de barras esparsas
    # (cada valor único virava uma coluna), sem forma de sino.
    # Agora: histograma contínuo com bins automáticos (Freedman-Diaconis).
    plt.figure(figsize=(8, 4.5))
    # usa dados filtrados para distribuição normal visível
    # Use filtered data if enough points; otherwise fall back to raw data
    dados_hist = tt_filtrado if len(tt_filtrado) >= 5 else tt
    # Utilize Freedman-Diaconis rule for optimal bin width
    n_bins = 'fd'  # automatically determines bin width
    counts, bins, patches = plt.hist(dados_hist, bins=n_bins, edgecolor='black', color='skyblue', linewidth=0.6, alpha=0.85, density=False)
    # marca média
    if not np.isnan(media):
        plt.axvline(media, color='red', linestyle='--', linewidth=1.2, label=f'média {media:.6f}s')
        plt.axvline(media + desvio, color='orange', linestyle=':', linewidth=1.1, label=f'±1σ')
        plt.axvline(media - desvio, color='orange', linestyle=':', linewidth=1.1)
    plt.ylabel('Frequência')
    plt.xlabel('Tempo (s)')
    plt.title(f'Histograma — n = {n} (bins=auto, {len(dados_hist)} amostras filtradas)')
    plt.legend(fontsize=8)
    # formatação científica se tempos muito pequenos
    plt.ticklabel_format(style='sci', axis='x', scilimits=(0,0))
    plt.tight_layout()
    plt.savefig(f'hist_n_{n}.png', dpi=150)
    print(f'Gráfico salvo como hist_n_{n}.png')
    plt.close()
