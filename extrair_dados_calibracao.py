#!/usr/bin/env python3
"""
Script para extrair dados de calibração FOCA (τa, τc, τo)
Mede cada operação primitiva isoladamente, aplica filtro IQR e exporta CSV.
"""

import time
import statistics
import gc
import numpy as np
import csv
from matplotlib import pyplot as plt
import logging
import os

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# ─── Configurações ──────────────────────────────────────────────
REPETICOES = 300
WARMUP = 10
OUTLIER_FACTOR = 3.0
N_ITER = 10000

OUTPUT_DIR = "resultados/calibracao"
os.makedirs(OUTPUT_DIR, exist_ok=True)
CSV_PATH = os.path.join(OUTPUT_DIR, "calibracao_foca.csv")

# ─── Utilitários ────────────────────────────────────────────────

def medir_operacao(nome, setup_code, operacao_code, n_iter=N_ITER):
    for _ in range(WARMUP):
        exec(setup_code)
        for _ in range(n_iter):
            exec(operacao_code)

    gc_old = gc.isenabled()
    gc.disable()
    tempos = []
    try:
        for _ in range(REPETICOES):
            exec(setup_code)
            tic = time.perf_counter()
            for _ in range(n_iter):
                exec(operacao_code)
            toc = time.perf_counter()
            tempos.append((toc - tic) / n_iter)
    finally:
        if gc_old:
            gc.enable()
    return tempos


def filtrar_iqr(tempos, factor=OUTLIER_FACTOR):
    arr = np.array(tempos)
    q1, q3 = np.percentile(arr, [25, 75])
    iqr = q3 - q1
    if iqr == 0:
        lim_inf = np.percentile(arr, 2.5)
        lim_sup = np.percentile(arr, 97.5)
    else:
        lim_inf = q1 - factor * iqr
        lim_sup = q3 + factor * iqr
    filtrados = arr[(arr >= lim_inf) & (arr <= lim_sup)]
    return filtrados, lim_inf, lim_sup, q1, q3, iqr


def estatisticas(filtrados):
    if len(filtrados) == 0:
        return float('nan'), float('nan'), float('nan')
    if len(filtrados) == 1:
        m = float(filtrados[0])
        return m, 0.0, 0.0
    m = statistics.mean(filtrados)
    s = statistics.stdev(filtrados)
    cv = s / m if m != 0 else float('nan')
    return m, s, cv


def salvar_histograma(nome, tempos_brutos, tempos_filtrados, lim_inf, lim_sup, media, desvio, q1, q3, iqr):
    plt.figure(figsize=(8, 4.5))
    dados = tempos_filtrados if len(tempos_filtrados) >= 5 else tempos_brutos
    counts, bins, patches = plt.hist(dados, bins='fd', edgecolor='black',
                                      color='skyblue', linewidth=0.6, alpha=0.85, density=False)
    plt.axvline(lim_inf, color='red', linestyle='--', linewidth=1.2, label=f'Limite inf (Q1-{OUTLIER_FACTOR}×IQR)')
    plt.axvline(lim_sup, color='red', linestyle='--', linewidth=1.2, label=f'Limite sup (Q3+{OUTLIER_FACTOR}×IQR)')
    if not np.isnan(media):
        plt.axvline(media, color='green', linestyle='-', linewidth=1.5, label=f'Média {media:.2e}s')
        plt.axvline(media + desvio, color='orange', linestyle=':', linewidth=1.1, label='±1σ')
        plt.axvline(media - desvio, color='orange', linestyle=':', linewidth=1.1)
    plt.ylabel('Frequência')
    plt.xlabel('Tempo por operação (s)')
    plt.title(f'Histograma Pós-Filtragem — {nome} (n={len(dados)} amostras)')
    plt.legend(fontsize=8)
    plt.ticklabel_format(style='sci', axis='x', scilimits=(0, 0))
    plt.tight_layout()
    safe_name = nome.replace(' ', '_').replace('<','_').replace('>','_').replace('=','_').replace('/','_').replace('*','_').replace('%','_').replace('+','_').replace('-','_')
    path = os.path.join(OUTPUT_DIR, f"hist_{safe_name}.png")
    plt.savefig(path, dpi=150)
    plt.close()
    return path


def medir_e_salvar(nome, setup, operacao, categoria, csv_writer, csv_file):
    logging.info(f"Medindo: {nome}")
    tempos = medir_operacao(nome, setup, operacao)
    filtrados, lim_inf, lim_sup, q1, q3, iqr = filtrar_iqr(tempos)
    media, desvio, cv = estatisticas(filtrados)

    hist_path = salvar_histograma(nome, tempos, filtrados, lim_inf, lim_sup, media, desvio, q1, q3, iqr)

    csv_writer.writerow([
        categoria, nome,
        f"{media:.10e}", f"{desvio:.10e}", f"{cv:.6f}",
        len(tempos), len(filtrados),
        f"{lim_inf:.10e}", f"{lim_sup:.10e}",
        f"{q1:.10e}", f"{q3:.10e}", f"{iqr:.10e}",
        hist_path
    ])
    csv_file.flush()

    status = "✅ CV < 0.15" if cv < 0.15 else "❌ CV ≥ 0.15"
    logging.info(f"  {nome}: μ={media:.2e}  σ={desvio:.2e}  CV={cv:.4%}  {status}  (amostras: {len(filtrados)}/{len(tempos)})")
    return cv < 0.15


# ─── Definição das Operações ────────────────────────────────────

OPERACOES = [
    ("τa", "var_int_cte_int", "a = 0", "a = 5"),
    ("τa", "var_float_cte_float", "a = 0.0", "a = 5.0"),
    ("τa", "var_bool_cte_bool", "a = False", "a = True"),
    ("τa", "var_int_var_int", "a = 0; b = 5", "a = b"),
    ("τa", "var_float_var_float", "a = 0.0; b = 5.0", "a = b"),

    ("τc", "cte_int_eq_cte_int", "", "5 == 10"),
    ("τc", "var_int_eq_cte_int", "a = 5", "a == 10"),
    ("τc", "var_int_eq_var_int", "a = 5; b = 10", "a == b"),
    ("τc", "var_float_eq_var_float", "a = 5.0; b = 10.0", "a == b"),
    ("τc", "var_int_ne_var_int", "a = 5; b = 10", "a != b"),
    ("τc", "var_int_gt_var_int", "a = 5; b = 10", "a > b"),
    ("τc", "var_float_lt_cte_float", "a = 5.0", "a < 10.0"),

    ("τo", "var_int_add_cte_int", "a = 5", "a + 10"),
    ("τo", "var_int_add_var_int", "a = 5; b = 10", "a + b"),
    ("τo", "var_float_add_var_float", "a = 5.0; b = 10.0", "a + b"),
    ("τo", "var_int_sub_var_int", "a = 5; b = 10", "a - b"),
    ("τo", "var_int_mul_var_int", "a = 5; b = 10", "a * b"),
    ("τo", "var_float_mul_var_float", "a = 5.0; b = 10.0", "a * b"),
    ("τo", "var_float_div_var_float", "a = 10.0; b = 5.0", "a / b"),
    ("τo", "var_int_floordiv_var_int", "a = 10; b = 3", "a // b"),
    ("τo", "var_int_mod_var_int", "a = 10; b = 3", "a % b"),
]

FUNCOES_OPACAS = [
    ("τf", "math_sqrt_float", "import math; a = 25.0", "math.sqrt(a)"),
    ("τf", "abs_int", "a = -5", "abs(a)"),
    ("τf", "list_append", "lst = []; a = 5", "lst.append(a)"),
    ("τf", "len_list", "lst = [0]*100", "len(lst)"),
]

# ─── Main ───────────────────────────────────────────────────────

def main():
    with open(CSV_PATH, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([
            "categoria", "operacao",
            "media_filtrada", "desvio_filtrado", "cv_filtrado",
            "amostras_brutas", "amostras_filtradas",
            "limite_inferior", "limite_superior",
            "q1", "q3", "iqr",
            "histograma_path"
        ])
        f.flush()

        print("\n" + "="*60)
        print("CALIBRAÇÃO FOCA - EXTRAÇÃO DE τa, τc, τo")
        print("="*60 + "\n")

        for cat, nome, setup, op in OPERACOES:
            medir_e_salvar(nome, setup, op, cat, writer, f)

        print("\n--- Funções Opacas (Opcional) ---\n")
        for cat, nome, setup, op in FUNCOES_OPACAS:
            medir_e_salvar(nome, setup, op, cat, writer, f)

    print(f"\n✅ CSV salvo em: {CSV_PATH}")
    print(f"✅ Histogramas salvos em: {OUTPUT_DIR}/")
    print("\nPróximo: abra o CSV e preencha as matrizes do relatório (Seção 4).")


if __name__ == "__main__":
    main()