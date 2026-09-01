import time
import gc

import numpy as np
from matplotlib import pyplot as plt

# adicionar ao vetor a média de tempo de um laço dentro das iterações

lista_n = [1000, 10000, 100000]
Y_LIM = {
    1000:   (6e-5,  6.75e-5),
    10000:  (0.6e-3, 1.2e-3),
    100000: (0.6e-2, 1.0e-2),
}

REPETICOES = 100
WARMUP = 20

for n in lista_n:
    for _ in range(WARMUP):
        for i in range(n):
            x = 1

    tt = []
    gc_old = gc.isenabled()
    gc.disable()
    try:
        for j in range(REPETICOES):
            tic = time.perf_counter()
            for i in range(n):
                x = 1
            toc = time.perf_counter()
            tt.append(toc - tic)
    finally:
        if gc_old:
            gc.enable()

    tt = np.array(tt)
    media = tt.mean()
    sigma = tt.std()
    cv = sigma / media

    p2 = np.percentile(tt, 2)
    p5 = np.percentile(tt, 5)
    p95 = np.percentile(tt, 95)
    p98 = np.percentile(tt, 98)

    outliers_2 = (tt < media - 2 * sigma) | (tt > media + 2 * sigma)
    outliers_3 = (tt < media - 3 * sigma) | (tt > media + 3 * sigma)

    print(f"n={n}  media={media:.8f}  sigma={sigma:.8f}  CV={cv:.4f}")
    print(f"  2σ outliers ({outliers_2.sum()}): {tt[outliers_2]}")
    print(f"  3σ outliers ({outliers_3.sum()}): {tt[outliers_3]}")
    print(f"  percentis: p2={p2:.8f}  p5={p5:.8f}  p95={p95:.8f}  p98={p98:.8f}")

    plt.figure(figsize=(10, 4))
    plt.plot(range(len(tt)), tt, linestyle='-', color='tab:blue', linewidth=1.2,
             marker='o', markersize=4, label='Tempo por iteração')

    plt.axhline(media + 2 * sigma, color='teal', linestyle=':', linewidth=1, label=f'µ+2σ ({media+2*sigma:.6f})')
    plt.axhline(media - 2 * sigma, color='teal', linestyle=':', linewidth=1, alpha=0.7)
    plt.axhline(media + 3 * sigma, color='darkmagenta', linestyle='-.', linewidth=1, label=f'µ+3σ ({media+3*sigma:.6f})')
    plt.axhline(media - 3 * sigma, color='darkmagenta', linestyle='-.', linewidth=1, alpha=0.7)

    plt.axhline(p2, color='red', linestyle='--', linewidth=1, alpha=0.8, label=f'p2 ({p2:.6f})')
    plt.axhline(p98, color='red', linestyle='--', linewidth=1, alpha=0.8, label=f'p98 ({p98:.6f})')
    plt.axhline(p5, color='orange', linestyle='--', linewidth=1, alpha=0.8, label=f'p5 ({p5:.6f})')
    plt.axhline(p95, color='orange', linestyle='--', linewidth=1, alpha=0.8, label=f'p95 ({p95:.6f})')

    if outliers_3.any():
        idx = np.where(outliers_3)[0]
        plt.scatter(idx, tt[idx], color='darkmagenta', s=40, zorder=5, marker='x', label=f'outliers 3σ ({len(idx)})')
    if outliers_2.any():
        idx = np.where(outliers_2 & ~outliers_3)[0]
        plt.scatter(idx, tt[idx], color='teal', s=30, zorder=5, marker='x', label=f'outliers 2σ ({len(idx)})')

    ylim = Y_LIM[n]
    plt.ylim(ylim)
    plt.ylabel('Tempo (s)')
    plt.xlabel('Iteração')
    plt.title(f'n = {n} — µ={media:.6f}s  σ={sigma:.6f}s  CV={cv:.2%} ({REPETICOES} reps)')
    plt.ticklabel_format(style='sci', axis='y', scilimits=(0, 0), useMathText=True)
    plt.gca().yaxis.get_offset_text().set_fontsize(8)
    plt.legend(fontsize=6, loc='upper right', ncol=2)
    plt.tight_layout()
    plt.savefig(f'tempo_n_{n}.png', dpi=150)
    print(f'Gráfico salvo como tempo_n_{n}.png\n')
    plt.close()

    plt.figure(figsize=(8, 4.5))
    plt.hist(tt, bins='fd', edgecolor='black', color='skyblue', linewidth=0.6, alpha=0.85)
    plt.axvline(media, color='red', linestyle='--', linewidth=1.2, label=f'µ={media:.6f}')
    plt.axvline(media + 2 * sigma, color='teal', linestyle=':', linewidth=1, label='µ±2σ')
    plt.axvline(media - 2 * sigma, color='teal', linestyle=':', linewidth=1)
    plt.axvline(media + 3 * sigma, color='darkmagenta', linestyle='-.', linewidth=1, label='µ±3σ')
    plt.axvline(media - 3 * sigma, color='darkmagenta', linestyle='-.', linewidth=1)
    plt.ylabel('Frequência')
    plt.xlabel('Tempo (s)')
    plt.title(f'Histograma — n = {n} ({len(tt)} amostras)')
    plt.ticklabel_format(style='sci', axis='x', scilimits=(0, 0))
    plt.legend(fontsize=8)
    plt.tight_layout()
    plt.savefig(f'hist_n_{n}.png', dpi=150)
    print(f'Gráfico salvo como hist_n_{n}.png')
    plt.close()
