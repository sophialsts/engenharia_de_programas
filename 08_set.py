"""
08_set.py — Determinação do tempo médio de primitivas (OCA)
============================================================
Engenharia de Programas — Aula 08/09

Mede o tempo de execução de primitivas individuais:
  O = Operação (aritmética, lógica)
  C = Comparação
  A = Atribuição / acesso a variável

Dois cenários:
  1) Comparação variável vs variável:   if (a < b): b = -1
  2) Comparação variável vs constante:  if (a < 0): b = -1

Parâmetros:
  n = 1_000_000 (1 milhão de iterações)
  REPETICOES = 500

Ao final, calcula FLOPS e exibe a capacidade da máquina.
"""

import time
import gc
import os
import numpy as np
from matplotlib import pyplot as plt

# Pastas de saída organizadas por categoria
BASE_DIR = os.path.dirname(__file__)
DIRS = {
    'O': os.path.join(BASE_DIR, 'resultados', 'operacao'),
    'C': os.path.join(BASE_DIR, 'resultados', 'comparacao'),
    'A': os.path.join(BASE_DIR, 'resultados', 'atribuicao'),
    'Baseline': os.path.join(BASE_DIR, 'resultados', 'loops'),
    'oca': os.path.join(BASE_DIR, 'resultados', 'oca'),
}
for d in DIRS.values():
    os.makedirs(d, exist_ok=True)

# ---------------------------------------------------------------------------
# Configurações
# ---------------------------------------------------------------------------
N = 1_000_000          # iterações por medição
REPETICOES = 500       # repetições para estatística
WARMUP = 20            # aquecimento

# ---------------------------------------------------------------------------
# Funções auxiliares de medição
# ---------------------------------------------------------------------------

def medir_tempo(func, n, repeticoes, warmup):
    """
    Executa `func(n)` várias vezes e retorna um array com os tempos.
    """
    # Aquecimento
    for _ in range(warmup):
        func(n)

    tempos = []
    gc_old = gc.isenabled()
    gc.disable()
    try:
        for _ in range(repeticoes):
            tic = time.perf_counter()
            func(n)
            toc = time.perf_counter()
            tempos.append(toc - tic)
    finally:
        if gc_old:
            gc.enable()

    return np.array(tempos)


def gerar_histograma(tt, titulo, nome_arquivo, cor='skyblue'):
    """
    Gera histograma focado na região mais frequente (percentis 2–98).
    """
    media = tt.mean()
    sigma = tt.std()
    p2, p98 = np.percentile(tt, [2, 98])
    margem = 0.15 * (p98 - p2) if p98 != p2 else media * 0.05

    fig, ax = plt.subplots(figsize=(9, 5))
    ax.hist(tt, bins='fd', edgecolor='black', color=cor,
            linewidth=0.6, alpha=0.85)
    ax.axvline(media, color='red', linestyle='--', linewidth=1.3,
               label=f'µ = {media:.8f} s')
    ax.axvline(media + sigma, color='orange', linestyle=':', linewidth=1.1,
               label='µ ± 1σ')
    ax.axvline(media - sigma, color='orange', linestyle=':', linewidth=1.1)
    ax.axvline(media + 2 * sigma, color='teal', linestyle=':', linewidth=1,
               label='µ ± 2σ')
    ax.axvline(media - 2 * sigma, color='teal', linestyle=':', linewidth=1)

    ax.set_xlim(p2 - margem, p98 + margem)
    ax.set_ylabel('Frequência')
    ax.set_xlabel('Tempo (s)')
    ax.set_title(titulo)
    ax.ticklabel_format(style='sci', axis='x', scilimits=(0, 0))
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(nome_arquivo, dpi=150)
    print(f'  → Gráfico salvo: {nome_arquivo}')
    plt.close(fig)

    return media, sigma


# ===================================================================
# Definição das primitivas a medir
# ===================================================================

# --- Operações (O) ---
def op_soma(n):
    """O: operação de soma (a + b)"""
    a = 3.14
    b = 2.71
    for _ in range(n):
        c = a + b

def op_multiplicacao(n):
    """O: operação de multiplicação (a * b)"""
    a = 3.14
    b = 2.71
    for _ in range(n):
        c = a * b

def op_divisao(n):
    """O: operação de divisão (a / b)"""
    a = 3.14
    b = 2.71
    for _ in range(n):
        c = a / b

def op_modulo(n):
    """O: operação de módulo (a % b)"""
    a = 314
    b = 27
    for _ in range(n):
        c = a % b

# --- Comparações (C) ---
def cmp_var_var(n):
    """C: comparação variável < variável  →  if (a < b): b = -1"""
    a = 5.0
    b = 10.0
    for _ in range(n):
        if a < b:
            b = -1

def cmp_var_const(n):
    """C: comparação variável < constante  →  if (a < 0): b = -1"""
    a = 5.0
    b = 10.0
    for _ in range(n):
        if a < 0:
            b = -1

def cmp_igualdade(n):
    """C: comparação de igualdade (a == b)"""
    a = 5.0
    b = 10.0
    for _ in range(n):
        if a == b:
            b = -1

# --- Atribuição / Acesso (A) ---
def atrib_simples(n):
    """A: atribuição simples (x = 1)"""
    for _ in range(n):
        x = 1

def atrib_variavel(n):
    """A: atribuição de variável (x = a) — acesso a memória"""
    a = 42
    for _ in range(n):
        x = a

# --- Loop vazio (baseline para subtrair overhead do for) ---
def loop_vazio(n):
    """Baseline: loop vazio (overhead do for/range)"""
    for _ in range(n):
        pass


# ===================================================================
# Execução das medições
# ===================================================================

primitivas = {
    # Operações (O)
    'O: soma (a+b)':         (op_soma,          'tab:blue'),
    'O: multiplicação (a*b)':(op_multiplicacao,  'tab:cyan'),
    'O: divisão (a/b)':      (op_divisao,        'cornflowerblue'),
    'O: módulo (a%b)':       (op_modulo,         'steelblue'),
    # Comparações (C)
    'C: var < var':           (cmp_var_var,       'tab:orange'),
    'C: var < const':         (cmp_var_const,     'sandybrown'),
    'C: var == var':          (cmp_igualdade,     'lightsalmon'),
    # Atribuição/Acesso (A)
    'A: x = 1 (const)':      (atrib_simples,     'tab:green'),
    'A: x = a (var)':        (atrib_variavel,    'mediumseagreen'),
    # Baseline
    'Baseline (loop vazio)':  (loop_vazio,        'lightgray'),
}

print("=" * 70)
print(f"  MEDIÇÃO DE PRIMITIVAS  —  n = {N:,}  |  repetições = {REPETICOES}")
print("=" * 70)

resultados = {}

for nome, (func, cor) in primitivas.items():
    print(f"\n--- {nome} ---")
    tt = medir_tempo(func, N, REPETICOES, WARMUP)
    # Determinar pasta de saída baseado no tipo (O, C, A, Baseline)
    tipo_key = nome.split(':')[0].strip()
    out_dir = DIRS.get(tipo_key, DIRS['oca'])
    nome_arquivo = os.path.join(out_dir, f'hist_{func.__name__}.png')
    media, sigma = gerar_histograma(
        tt,
        titulo=f'{nome}  (n={N:,}, {REPETICOES} reps)',
        nome_arquivo=nome_arquivo,
        cor=cor,
    )
    cv = sigma / media if media > 0 else float('nan')
    resultados[nome] = {
        'media': media,
        'sigma': sigma,
        'cv': cv,
        'tempos': tt,
    }
    print(f'  média = {media:.10f} s  |  σ = {sigma:.10f} s  |  CV = {cv:.4%}')


# ===================================================================
# Separar OCA — tempo bruto de cada primitiva
# ===================================================================
# Nota: em Python o overhead do loop (for/range) domina, então subtrair
# um baseline "loop vazio" pode dar resultado negativo ou zero.
# Usamos o tempo bruto por iteração (T_total / N) — a comparação
# relativa entre primitivas continua válida.
# ===================================================================
print("\n" + "=" * 70)
print("  SEPARAÇÃO OCA — Tempo por primitiva")
print("=" * 70)

t_baseline = resultados['Baseline (loop vazio)']['media']
t_baseline_iter = t_baseline / N
print(f"\n  Baseline (loop vazio): {t_baseline:.10f} s  ({t_baseline_iter:.2e} s/iter)")
print(f"  O baseline serve como referência; NÃO é subtraído.\n")

def formatar_flops(flops):
    """Retorna string legível para FLOPS."""
    if flops >= 1e12:
        return f"{flops/1e12:.2f} TFLOPS"
    elif flops >= 1e9:
        return f"{flops/1e9:.2f} GFLOPS"
    elif flops >= 1e6:
        return f"{flops/1e6:.2f} MFLOPS"
    elif flops >= 1e3:
        return f"{flops/1e3:.2f} kFLOPS"
    else:
        return f"{flops:.2f} FLOPS"

print(f"  {'Primitiva':<28}  {'T total (s)':>14}  {'T/iter (s)':>14}  {'1/T (FLOPS)':>16}")
print(f"  {'-'*28}  {'-'*14}  {'-'*14}  {'-'*16}")

dados_barras = []

for nome, res in resultados.items():
    if nome == 'Baseline (loop vazio)':
        continue
    t_total = res['media']
    t_por_iter = t_total / N
    flops = 1.0 / t_por_iter if t_por_iter > 0 else 0

    print(f"  {nome:<28}  {t_total:>14.10f}  {t_por_iter:>14.2e}  {formatar_flops(flops):>16}")

    dados_barras.append({
        'nome': nome,
        'tempo_por_iter': t_por_iter,
        'flops': flops,
        'tipo': nome.split(':')[0].strip(),
    })


# ===================================================================
# GRÁFICO COMPARATIVO — todas as primitivas (barras agrupadas por OCA)
# ===================================================================
from matplotlib.patches import Patch

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

cores_tipo = {'O': 'tab:blue', 'C': 'tab:orange', 'A': 'tab:green'}
nomes = [d['nome'] for d in dados_barras]
tempos = [d['tempo_por_iter'] for d in dados_barras]
cores = [cores_tipo.get(d['tipo'], 'gray') for d in dados_barras]

y_pos = np.arange(len(nomes))

# --- Barras de tempo por iteração ---
ax1.barh(y_pos, tempos, color=cores, edgecolor='black', linewidth=0.5)
ax1.axvline(t_baseline_iter, color='gray', linestyle='--', linewidth=1.2,
            label=f'Baseline: {t_baseline_iter:.2e} s')
ax1.set_yticks(y_pos)
ax1.set_yticklabels(nomes, fontsize=8)
ax1.set_xlabel('Tempo por iteração (s)')
ax1.set_title('Tempo bruto por primitiva (1 iteração)')
ax1.ticklabel_format(style='sci', axis='x', scilimits=(0, 0))
ax1.invert_yaxis()
ax1.legend(fontsize=7, loc='lower right')

# --- Barras de FLOPS ---
flops_vals = [d['flops'] for d in dados_barras]
ax2.barh(y_pos, flops_vals, color=cores, edgecolor='black', linewidth=0.5)
ax2.set_yticks(y_pos)
ax2.set_yticklabels(nomes, fontsize=8)
ax2.set_xlabel('Primitivas / segundo')
ax2.set_title('Capacidade de processamento (FLOPS)')
ax2.ticklabel_format(style='sci', axis='x', scilimits=(0, 0))
ax2.invert_yaxis()

# Legenda OCA
legendas = [Patch(facecolor=c, edgecolor='black', label=t)
            for t, c in cores_tipo.items()]
ax2.legend(handles=legendas, loc='lower right', fontsize=8)

fig.suptitle(f'Benchmark de Primitivas — n = {N:,}  |  {REPETICOES} repetições',
             fontsize=13, fontweight='bold')
fig.tight_layout()
fig.savefig('oca_comparacao.png', dpi=150)
print(f'\n→ Gráfico comparativo salvo: oca_comparacao.png')
plt.close(fig)


# ===================================================================
# GRÁFICO SEPARADO — Cenário 1 vs Cenário 2 (var<var vs var<const)
# ===================================================================
fig, ax = plt.subplots(figsize=(10, 5))

t1 = resultados['C: var < var']['tempos']
t2 = resultados['C: var < const']['tempos']

# Limitar eixo X à região mais relevante
todos = np.concatenate([t1, t2])
p2_all, p98_all = np.percentile(todos, [2, 98])
margem = 0.15 * (p98_all - p2_all)

ax.hist(t1, bins='fd', alpha=0.65, color='tab:orange', edgecolor='black',
        linewidth=0.4, label=f'if (a < b): µ={t1.mean():.8f}s')
ax.hist(t2, bins='fd', alpha=0.65, color='sandybrown', edgecolor='black',
        linewidth=0.4, label=f'if (a < 0): µ={t2.mean():.8f}s')

ax.axvline(t1.mean(), color='darkorange', linestyle='--', linewidth=1.3)
ax.axvline(t2.mean(), color='saddlebrown', linestyle='--', linewidth=1.3)

ax.set_xlim(p2_all - margem, p98_all + margem)
ax.set_ylabel('Frequência')
ax.set_xlabel('Tempo (s)')
ax.set_title(f'Comparação: var<var  vs  var<const  (n={N:,}, {REPETICOES} reps)')
ax.ticklabel_format(style='sci', axis='x', scilimits=(0, 0))
ax.legend(fontsize=9)
fig.tight_layout()
fig.savefig('cmp_var_var_vs_var_const.png', dpi=150)
print(f'→ Gráfico comparativo de cenários salvo: cmp_var_var_vs_var_const.png')
plt.close(fig)


# ===================================================================
# Resumo da capacidade da máquina
# ===================================================================
print("\n" + "=" * 70)
print("  AVALIAÇÃO DE HARDWARE (Benchmark)")
print("=" * 70)

# Usar a operação de soma como referência (é uma primitiva real, não o baseline)
t_ref = resultados['O: soma (a+b)']['media']
t_por_prim = t_ref / N
flops_total = 1.0 / t_por_prim if t_por_prim > 0 else 0

print(f"\n  Referência: O: soma (a+b)")
print(f"  T (1 primitiva) = {t_por_prim:.2e} s")
print(f"  1/T = {flops_total:.2e} primitivas/s")
print(f"  → {formatar_flops(flops_total)}")

# Mostrar FLOPS para cada tipo de primitiva
print(f"\n  {'Tipo':<12}  {'Primitiva mais rápida':<28}  {'FLOPS':>16}")
print(f"  {'-'*12}  {'-'*28}  {'-'*16}")

for tipo in ['O', 'C', 'A']:
    tipo_dados = [d for d in dados_barras if d['tipo'] == tipo]
    if tipo_dados:
        mais_rapido = min(tipo_dados, key=lambda d: d['tempo_por_iter'])
        print(f"  {tipo:<12}  {mais_rapido['nome']:<28}  {formatar_flops(mais_rapido['flops']):>16}")

print()
