"""
27ago.py — Validação de Setup Computacional
============================================================
Engenharia de Programas — Prof. Dr. Diego Frias

Fluxo (conforme fluxograma do PDF):
  1. Definir vetor N = [1000, 10000, 100000] e R repetições
  2. LAÇO EXTERNO — para cada n em N:
       a. Gerar lista aleatória de tamanho n
       b. LAÇO INTERNO — R vezes:
            - medir tempo (t) e memória (m) do loop banal
       c. Calcular µ, σ e CV_n = σ / µ
  3. Gerar os 4 plots de validação
  4. Para cada n: se CV_n ≤ 0.15 → SETUP APROVADO

Critério de aprovação (CV):
  CV ≤ 0.10          → Excelente — sinal muito limpo
  0.10 < CV ≤ 0.15  → Aprovado — aceitável para análise
  CV > 0.15          → Reprovado — ruído excessivo
"""

import time
import gc
import os
import tracemalloc
import numpy as np
from matplotlib import pyplot as plt

# ─── Pasta de saída ────────────────────────────────────────────────────────
OUT_DIR = os.path.join(os.path.dirname(__file__), 'resultados', 'validacao')
os.makedirs(OUT_DIR, exist_ok=True)

# ═══════════════════════════════════════════════════════════════════════════
# PARÂMETROS
# ═══════════════════════════════════════════════════════════════════════════
N_LIST     = [1_000, 10_000, 100_000]   # vetor de tamanhos de entrada
R          = 100                         # repetições por n (laço interno)
CV_LIMITE  = 0.15                        # critério de aprovação do setup
SIGMA_CLIP = 2.0                         # sigma-clipping: remove amostras fora de µ2σ


def sigma_clip(t, n_sigma=SIGMA_CLIP, max_iter=5):
    """
    Sigma-clipping iterativo: remove amostras fora de µ ± n_sigma*σ.
    Repete até estabilizar ou atingir max_iter.
    É o método padrão em benchmarking astronômico/computacional.
    """
    t_clean = t.copy()
    for _ in range(max_iter):
        mu  = t_clean.mean()
        sig = t_clean.std()
        if sig == 0:
            break
        mask = np.abs(t_clean - mu) <= n_sigma * sig
        if mask.all():          # sem mais outliers
            break
        t_clean = t_clean[mask]
    return t_clean

# ═══════════════════════════════════════════════════════════════════════════
# ESTRUTURA PARA GUARDAR RESULTADOS
#   resultados[n] = {
#       'tempos':   array com os R tempos medidos (t)
#       'memorias': array com os R picos de memória medidos (m)
#       'media':    µ = média dos tempos
#       'sigma':    σ = desvio padrão dos tempos
#       'cv':       CV_n = σ / µ
#   }
# ═══════════════════════════════════════════════════════════════════════════
resultados = {}

print("=" * 60)
print("  VALIDAÇÃO DE SETUP COMPUTACIONAL")
print(f"  N = {N_LIST}  |  R = {R} repetições  |  CV limite = {CV_LIMITE}")
print("=" * 60)

# ═══════════════════════════════════════════════════════════════════════════
# LAÇO EXTERNO — para cada n no vetor N
# ═══════════════════════════════════════════════════════════════════════════
for n in N_LIST:
    print(f"\n{'─'*60}")
    print(f"  n = {n:,}")
    print(f"{'─'*60}")

    # ── Aquecimento adaptativo (menos iterações para n grandes) ────────────────
    # Para n grandes o aquecimento demora muito e pode aquecer a CPU
    warmup_iters = max(5, 20 - n // 10_000)   # 20 para n=1k, 19 para 10k, 10 para 100k
    for _ in range(warmup_iters):
        _lista = list(np.random.randint(0, 10_000, size=n))
        for _i in range(n):
            _x = 1

    # ── Vetores de medição ──────────────────────────────────────────────────
    t = []   # t[r] = tempo da r-ésima repetição (segundos)
    m = []   # m[r] = pico de memória da r-ésima repetição (bytes)

    gc_old = gc.isenabled()
    gc.disable()   # desativa GC para não interferir na medição
    try:
        # ── LAÇO INTERNO — R repetições ──────────────────────────────────────
        for _ in range(R):

            # a) Gerar lista aleatória de tamanho n
            lista = list(np.random.randint(0, 10_000, size=n))

            # b) Medir tempo (t) e memória (m) do loop banal
            tracemalloc.start()
            tic = time.perf_counter()

            for i in range(n):   # loop banal — primitiva sendo medida
                x = 1

            toc = time.perf_counter()
            _, mem_pico = tracemalloc.get_traced_memory()
            tracemalloc.stop()

            t.append(toc - tic)
            m.append(mem_pico)

            # (Removido sleep que causava queda de C-state do processador)

    finally:
        if gc_old:
            gc.enable()

    t = np.array(t)
    m = np.array(m)

    # ── c) Calcular µ, σ e CV_n — sigma-clipping iterativo (±2σ) ─────────────
    # Remove amostras fora de µ ± 2σ de forma iterativa.
    # Mais robusto que percentil fixo: converge para o cluster de medidas estáveis.
    t_filtrado = sigma_clip(t)

    media = t_filtrado.mean()
    sigma = t_filtrado.std()
    cv_n  = sigma / media if media > 0 else float('nan')

    if cv_n <= 0.10:
        status = "✅ EXCELENTE"
    elif cv_n <= CV_LIMITE:
        status = "✅ APROVADO"
    else:
        status = "❌ REPROVADO"

    resultados[n] = {
        'tempos':    t,            # todos os tempos brutos (para o scatter)
        't_filtrado': t_filtrado,  # tempos sem outliers (para histograma/stats)
        'memorias':  m,
        'media':     media,
        'sigma':     sigma,
        'cv':        cv_n,
        'media_por_elemento': media / n if n else float('nan'),  # tempo médio = µ / n
        'n_outliers': len(t) - len(t_filtrado),
    }

    print(f"  Amostras brutas:   {len(t)}")
    print(f"  Outliers removidos: {len(t) - len(t_filtrado)} (sigma-clipping ±{SIGMA_CLIP}σ)")
    print(f"  µ  = {media:.8f} s")
    print(f"  σ  = {sigma:.8f} s")
    print(f"  CV = {cv_n:.4%}  →  {status}")
    print(f"  tempo médio (por elemento) = {media / n:.4e} s  ({media / n * 1e9:.2f} ns)  [µ / n]")
    print(f"  Memória pico média = {m.mean() / 1024:.2f} KB")


# ═══════════════════════════════════════════════════════════════════════════
# PLOTS DE VALIDAÇÃO
# ═══════════════════════════════════════════════════════════════════════════
print(f"\n{'='*60}")
print("  GERANDO PLOTS DE VALIDAÇÃO")
print(f"{'='*60}")

CORES  = {1_000: 'tab:blue', 10_000: 'tab:orange', 100_000: 'tab:green'}
LABELS = {n: f'n = {n:,}' for n in N_LIST}
x_pos  = np.arange(len(N_LIST))

# ───────────────────────────────────────────────────────────────────────────
# PLOT 1 — Scatter Plot: Dispersão Total dos Tempos
#   Mostra todos os R tempos para cada n.
#   Identifica outliers e tendências de throttling térmico.
# ───────────────────────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(12, 5))

for n in N_LIST:
    tt       = resultados[n]['tempos']       # todos os pontos brutos
    t_filt   = resultados[n]['t_filtrado']   # amostras após sigma-clipping
    mu       = resultados[n]['media']
    # Identificar quais pontos brutos foram mantidos pelo sigma-clipping
    mask_ok  = np.isin(tt, t_filt)
    ax.scatter(np.where(mask_ok)[0],  tt[mask_ok],  s=14, alpha=0.65,
               color=CORES[n], label=LABELS[n])
    # Outliers marcados com X vermelho
    ax.scatter(np.where(~mask_ok)[0], tt[~mask_ok], s=40, alpha=0.9,
               color='red', marker='x', zorder=5,
               label=f'outliers n={n:,} ({(~mask_ok).sum()})')
    ax.axhline(mu, color=CORES[n], linestyle='--', linewidth=1.2,
               label=f'µ n={n:,} = {mu:.2e}s')

ax.set_xlabel('Repetição (r)')
ax.set_ylabel('Tempo (s)')
ax.set_title(f'Plot 1 — Scatter: Dispersão Total dos Tempos  (R = {R} repetições)')
ax.ticklabel_format(style='sci', axis='y', scilimits=(0, 0))
ax.legend(fontsize=8, ncol=2)
fig.tight_layout()
caminho = os.path.join(OUT_DIR, 'plot1_scatter.png')
fig.savefig(caminho, dpi=150)
plt.close(fig)
print(f"  → Plot 1 salvo: {caminho}")

# ───────────────────────────────────────────────────────────────────────────
# PLOT 2 — Gráfico de Linha: Tempo Médio x Tamanho da Entrada
#   Mostra a relação entre o tempo médio (µ) e o tamanho da entrada n.
#   Permite visualizar a escalabilidade do setup.
# ───────────────────────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(10, 5))

ns = np.array(N_LIST)
medias = np.array([resultados[n]['media'] for n in N_LIST])

ax.plot(ns, medias, 'o-', color='tab:blue', linewidth=2, markersize=8, label='Tempo Médio (µ)')
for n, mu in zip(N_LIST, medias):
    ax.annotate(f'{mu:.2e}s', (n, mu), textcoords="offset points", xytext=(0,10), ha='center', fontsize=9)

ax.set_xlabel('Tamanho da Entrada (n)')
ax.set_ylabel('Tempo Médio (s)')
ax.set_title('Plot 2 — Gráfico de Linha: Tempo Médio x Tamanho da Entrada')
ax.set_xscale('log')
ax.set_xticks(N_LIST)
ax.set_xticklabels([f'{n:,}' for n in N_LIST])
ax.ticklabel_format(style='sci', axis='y', scilimits=(0, 0))
ax.grid(True, which='both', linestyle='--', alpha=0.5)
ax.legend(fontsize=9)
fig.tight_layout()
caminho = os.path.join(OUT_DIR, 'plot2_histogramas.png')
fig.savefig(caminho, dpi=150)
plt.close(fig)
print(f"  → Plot 2 salvo: {caminho}")

# ───────────────────────────────────────────────────────────────────────────
# PLOT 3 — Barras: µ (média) vs σ (desvio padrão) por n
#   A barra de σ deve ser VISIVELMENTE menor que a de µ.
#   Picos acentuados de σ indicam gargalos ou trocas de contexto elevadas.
# ───────────────────────────────────────────────────────────────────────────
medias = [resultados[n]['media'] for n in N_LIST]
sigmas = [resultados[n]['sigma'] for n in N_LIST]
largura = 0.35

fig, ax = plt.subplots(figsize=(9, 5))
ax.bar(x_pos - largura / 2, medias, largura,
       label='µ — Tempo Médio', color='tab:blue', edgecolor='black', linewidth=0.6)
ax.bar(x_pos + largura / 2, sigmas, largura,
       label='σ — Desvio Padrão', color='tab:orange', edgecolor='black', linewidth=0.6)

ax.set_xticks(x_pos)
ax.set_xticklabels([f'n = {n:,}' for n in N_LIST])
ax.set_ylabel('Tempo (s)')
ax.set_title('Plot 3 — µ vs σ por n  (σ deve ser muito menor que µ)')
ax.ticklabel_format(style='sci', axis='y', scilimits=(0, 0))
ax.legend(fontsize=9)
fig.tight_layout()
caminho = os.path.join(OUT_DIR, 'plot3_media_sigma.png')
fig.savefig(caminho, dpi=150)
plt.close(fig)
print(f"  → Plot 3 salvo: {caminho}")

# ───────────────────────────────────────────────────────────────────────────
# PLOT 4 — Barras: Coeficiente de Variação (CV) por n
#   CV = σ / µ  para cada n.
#   Linha vermelha em 0.15 = limite de aprovação.
#   Barras verdes = APROVADO | Barras vermelhas = REPROVADO
# ───────────────────────────────────────────────────────────────────────────
cvs       = [resultados[n]['cv'] for n in N_LIST]
cores_cv  = ['tab:green' if cv <= CV_LIMITE else 'tab:red' for cv in cvs]

fig, ax = plt.subplots(figsize=(9, 5))
bars = ax.bar(x_pos, cvs, 0.5, color=cores_cv, edgecolor='black', linewidth=0.7)

ax.axhline(CV_LIMITE, color='red', linestyle='--', linewidth=2.0,
           label=f'Limite CV = {CV_LIMITE}  (15%)')
ax.bar_label(bars, fmt='%.4f', fontsize=10, padding=4)

ax.set_xticks(x_pos)
ax.set_xticklabels([f'n = {n:,}' for n in N_LIST])
ax.set_ylabel('CV = σ / µ')
ax.set_title('Plot 4 — Coeficiente de Variação por n  (verde = aprovado)')
ax.set_ylim(0, max(max(cvs) * 1.4, CV_LIMITE * 1.8))
ax.legend(fontsize=9)
fig.tight_layout()
caminho = os.path.join(OUT_DIR, 'plot4_cv.png')
fig.savefig(caminho, dpi=150)
plt.close(fig)
print(f"  → Plot 4 salvo: {caminho}")


# ═══════════════════════════════════════════════════════════════════════════
# PARECER TÉCNICO CONCLUSIVO
# ═══════════════════════════════════════════════════════════════════════════
print(f"\n{'='*60}")
print("  PARECER TÉCNICO CONCLUSIVO")
print(f"{'='*60}")
print(f"\n  {'n':>10}  {'µ (s)':>14}  {'σ (s)':>14}  {'tempo médio (s)':>17}  {'CV':>9}  Status")
print(f"  {'─'*10}  {'─'*14}  {'─'*14}  {'─'*17}  {'─'*9}  {'─'*12}")

for n in N_LIST:
    r = resultados[n]
    cv = r['cv']
    if cv <= 0.10:
        status = "✅ EXCELENTE"
    elif cv <= CV_LIMITE:
        status = "✅ APROVADO"
    else:
        status = "❌ REPROVADO"
    print(f"  {n:>10,}  {r['media']:>14.8f}  {r['sigma']:>14.8f}  {r['media_por_elemento']:>17.4e}  {cv:>9.4%}  {status}")
print(f"  (tempo médio = µ / n, ou seja, tempo por elemento da iteração)")

aprovados = sum(1 for n in N_LIST if resultados[n]['cv'] <= CV_LIMITE)
print()
if aprovados == len(N_LIST):
    print("  ✅ SETUP APROVADO — CV ≤ 0.15 para todos os valores de n.")
    print("  O ambiente é estável e reprodutível para análise de algoritmos.")
else:
    print(f"  ❌ SETUP REPROVADO — {len(N_LIST) - aprovados} n(s) com CV > 0.15.")
    print("  Feche processos em background e repita a calibração.")
print()
