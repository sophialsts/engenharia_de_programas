import time
import gc
import os

import numpy as np
from matplotlib import pyplot as plt

# Pasta de saída
OUT_DIR = os.path.join(os.path.dirname(__file__), 'resultados', 'loops')
os.makedirs(OUT_DIR, exist_ok=True)

# ---------------------------------------------------------------------------
# FOCA = F(chamada a Função), O(Operação), C(Comparação), A(Atribuição/acesso)
#
# O laço  `for i in range(n): x = 1`  tem as seguintes primitivas por iteração:
#   F = 0  (nenhuma chamada de função dentro do corpo)
#   O = 0  (nenhuma operação aritmética)
#   C = 1  (comparação implícita do for: i < n)
#   A = 2  (atribuição de x = 1  +  incremento i)
#
# Por repetição completa (n iterações + overhead do range):
#   FOCA laço  = (0, 0, n+1, n+2)      ← custo interno do laço
#   FOCA total = (0, 0, n+1, n+2+n)    ← inclui atribuições extras
#
# O script mede o tempo médio desse laço e gera gráficos.
# ---------------------------------------------------------------------------

lista_n = [1000, 10000, 100000]

REPETICOES = 100
WARMUP = 20

# Vetor para guardar médias FOCA de cada n
# Cada entrada: {'n': ..., 'media_original': ..., 'foca_1': ..., 'foca_2': ...}
resultados_foca = []

for n in lista_n:
    print(f"\n{'='*60}")
    print(f"  n = {n}")
    print(f"{'='*60}")

    # --- Aquecimento: estabilizar caches, branch predictor, etc. ---
    for _ in range(WARMUP):
        for i in range(n):
            x = 1

    # -------------------------------------------------------------------
    # 1) Medição do loop original: for i in range(n): x = 1
    # -------------------------------------------------------------------
    tt = []
    gc_old = gc.isenabled()
    gc.disable()
    try:
        for _ in range(REPETICOES):
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

    # -------------------------------------------------------------------
    # 2) Medições FOCA adicionais
    #    FOCA-1: range(n + 5)        → laço um pouco maior
    #    FOCA-2: range(2*n + 5)      → laço ~dobro do tamanho
    # -------------------------------------------------------------------
    foca_labels = [f'range({n}+5)', f'range(2*{n}+5)']
    foca_ranges = [n + 5, 2 * n + 5]
    foca_medias = []

    for foca_n in foca_ranges:
        foca_tt = []
        gc_old_f = gc.isenabled()
        gc.disable()
        try:
            for _ in range(REPETICOES):
                tic = time.perf_counter()
                for i in range(foca_n):
                    x = 1
                toc = time.perf_counter()
                foca_tt.append(toc - tic)
        finally:
            if gc_old_f:
                gc.enable()
        foca_medias.append(np.mean(foca_tt))

    resultados_foca.append({
        'n': n,
        'media_original': media,
        'foca_1': foca_medias[0],
        'foca_2': foca_medias[1],
    })

    # --- Estatísticas ---
    p2 = np.percentile(tt, 2)
    p5 = np.percentile(tt, 5)
    p95 = np.percentile(tt, 95)
    p98 = np.percentile(tt, 98)

    outliers_2 = (tt < media - 2 * sigma) | (tt > media + 2 * sigma)
    outliers_3 = (tt < media - 3 * sigma) | (tt > media + 3 * sigma)

    print(f"  média  = {media:.8f} s")
    print(f"  σ      = {sigma:.8f} s")
    print(f"  CV     = {cv:.4%}")
    print(f"  FOCA-1 (n+5)   média = {foca_medias[0]:.8f} s")
    print(f"  FOCA-2 (2n+5)  média = {foca_medias[1]:.8f} s")
    print(f"  outliers 2σ ({outliers_2.sum()}): {tt[outliers_2]}")
    print(f"  outliers 3σ ({outliers_3.sum()}): {tt[outliers_3]}")
    print(f"  percentis: p2={p2:.8f}  p5={p5:.8f}  p95={p95:.8f}  p98={p98:.8f}")

    # ===================================================================
    # GRÁFICO 1: Série temporal (tempo por iteração)
    # ===================================================================
    # Y_LIM calculado automaticamente a partir dos dados (resolve gráfico vazio)
    margem = 0.15 * (tt.max() - tt.min()) if tt.max() != tt.min() else tt.mean() * 0.1
    ylim_auto = (tt.min() - margem, tt.max() + margem)

    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(range(len(tt)), tt, linestyle='-', color='tab:blue', linewidth=1.2,
            marker='o', markersize=3, alpha=0.8, label='Tempo por repetição')

    ax.axhline(media, color='green', linestyle='-', linewidth=1.4, alpha=0.9,
               label=f'µ = {media:.6f}')
    ax.axhline(media + 2 * sigma, color='teal', linestyle=':', linewidth=1,
               label=f'µ±2σ')
    ax.axhline(media - 2 * sigma, color='teal', linestyle=':', linewidth=1, alpha=0.7)
    ax.axhline(media + 3 * sigma, color='darkmagenta', linestyle='-.', linewidth=1,
               label=f'µ±3σ')
    ax.axhline(media - 3 * sigma, color='darkmagenta', linestyle='-.', linewidth=1,
               alpha=0.7)

    # Faixa ±1σ sombreada
    ax.fill_between(range(len(tt)), media - sigma, media + sigma,
                    color='green', alpha=0.08, label='±1σ')

    if outliers_3.any():
        idx = np.where(outliers_3)[0]
        ax.scatter(idx, tt[idx], color='darkmagenta', s=40, zorder=5,
                   marker='x', label=f'outliers 3σ ({len(idx)})')
    if outliers_2.any():
        idx = np.where(outliers_2 & ~outliers_3)[0]
        if len(idx) > 0:
            ax.scatter(idx, tt[idx], color='teal', s=30, zorder=5,
                       marker='x', label=f'outliers 2σ ({len(idx)})')

    ax.set_ylim(ylim_auto)
    ax.set_ylabel('Tempo (s)')
    ax.set_xlabel('Repetição')
    ax.set_title(f'n = {n} — µ={media:.6f}s  σ={sigma:.6f}s  CV={cv:.2%} ({REPETICOES} reps)')
    ax.ticklabel_format(style='sci', axis='y', scilimits=(0, 0), useMathText=True)
    ax.yaxis.get_offset_text().set_fontsize(8)
    ax.legend(fontsize=6, loc='upper right', ncol=2)
    fig.tight_layout()
    caminho = os.path.join(OUT_DIR, f'tempo_n_{n}.png')
    fig.savefig(caminho, dpi=150)
    print(f'  → Gráfico salvo: {caminho}')
    plt.close(fig)

    # ===================================================================
    # GRÁFICO 2: Histograma (foco na região mais frequente)
    # ===================================================================
    # Limita o eixo X aos percentis 2–98 para focar nos tempos mais frequentes
    margem = 0.15 * (p98 - p2) if p98 != p2 else media * 0.05
    xlim_lo = p2 - margem
    xlim_hi = p98 + margem

    fig, ax = plt.subplots(figsize=(9, 5))
    ax.hist(tt, bins='fd', edgecolor='black', color='skyblue',
            linewidth=0.6, alpha=0.85)
    ax.axvline(media, color='red', linestyle='--', linewidth=1.3,
               label=f'µ = {media:.8f} s')
    ax.axvline(media + sigma, color='orange', linestyle=':', linewidth=1.1,
               label='µ ± 1σ')
    ax.axvline(media - sigma, color='orange', linestyle=':', linewidth=1.1)
    ax.axvline(media + 2 * sigma, color='teal', linestyle=':', linewidth=1,
               label='µ ± 2σ')
    ax.axvline(media - 2 * sigma, color='teal', linestyle=':', linewidth=1)

    ax.set_xlim(xlim_lo, xlim_hi)
    ax.set_ylabel('Frequência')
    ax.set_xlabel('Tempo (s)')
    ax.set_title(f'Histograma — n = {n} ({len(tt)} amostras)')
    ax.ticklabel_format(style='sci', axis='x', scilimits=(0, 0))
    ax.legend(fontsize=8)
    fig.tight_layout()
    caminho = os.path.join(OUT_DIR, f'hist_n_{n}.png')
    fig.savefig(caminho, dpi=150)
    print(f'  → Gráfico salvo: {caminho}')
    plt.close(fig)

# ===================================================================
# GRÁFICO 3: Comparação das médias FOCA por n (gráfico de barras)
# ===================================================================
fig, ax = plt.subplots(figsize=(10, 5))
x_pos = np.arange(len(lista_n))
largura = 0.25

barras_orig = [r['media_original'] for r in resultados_foca]
barras_f1   = [r['foca_1'] for r in resultados_foca]
barras_f2   = [r['foca_2'] for r in resultados_foca]

ax.bar(x_pos - largura, barras_orig, largura, label='Original (n)', color='tab:blue')
ax.bar(x_pos,           barras_f1,   largura, label='FOCA-1 (n+5)', color='tab:orange')
ax.bar(x_pos + largura, barras_f2,   largura, label='FOCA-2 (2n+5)', color='tab:green')

ax.set_xticks(x_pos)
ax.set_xticklabels([str(n) for n in lista_n])
ax.set_xlabel('n')
ax.set_ylabel('Tempo médio (s)')
ax.set_title('Comparação FOCA — Tempo médio por variante de loop')
ax.legend()
ax.ticklabel_format(style='sci', axis='y', scilimits=(0, 0), useMathText=True)
fig.tight_layout()
caminho = os.path.join(OUT_DIR, 'foca_comparacao.png')
fig.savefig(caminho, dpi=150)
print(f'\n→ Gráfico FOCA salvo: {caminho}')
plt.close(fig)

# --- Resumo final ---
print("\n" + "="*60)
print("  RESUMO FOCA (médias em segundos)")
print("="*60)
print(f"  {'n':>8}  {'Original':>12}  {'FOCA-1(n+5)':>14}  {'FOCA-2(2n+5)':>14}")
for r in resultados_foca:
    print(f"  {r['n']:>8}  {r['media_original']:>12.8f}  {r['foca_1']:>14.8f}  {r['foca_2']:>14.8f}")
print()
