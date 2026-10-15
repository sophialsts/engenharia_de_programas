import os
import time
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from PIL import Image
from scipy.optimize import curve_fit

"""

Experimento:
1- Bateria/plano de teste
2- Sistema instrumentalizado
3- Metodologia de execução
4- Metodologia de análise
5- Exemplo de resultado

Instrumentos
Armazenamento
Análise
Notificação/Aviso

"""

# ==========================================
# 1. Função do Aluno
# ==========================================
def segmenta_imagem(imagem_array, K, MAX_ITER=1000):
    """
    Segmenta uma imagem utilizando K-means.

    Recebe o array da imagem já em memória e o número de clusters K.
    Utiliza a lógica do algoritmo implementado em 15set.py, adaptada
    para receber diretamente o array da imagem.

    Parâmetros
    ----------
    imagem_array : np.ndarray
        Array da imagem no formato RGB (altura, largura, 3).
    K : int
        Número de clusters desejado.
    MAX_ITER : int
        Número máximo de iterações do K-means.

    Retorno
    -------
    img_segmentada : np.ndarray
        Imagem segmentada com cada pixel substituído pela cor do centróide
        do cluster ao qual foi atribuído.
    """
    img = np.asarray(imagem_array)
    # Se a imagem tiver canal alpha (RGBA), descarta o alpha e usa só RGB
    if img.ndim == 3 and img.shape[2] == 4:
        img = img[:, :, :3]
    if img.ndim == 2:
        # Caso seja imagem em escala de cinza, converte para 3 canais
        n, m = img.shape
        c = 1
        img_rgb = np.stack([img, img, img], axis=-1)
    else:
        n, m, c = img.shape
        img_rgb = img

    # Constrói lista com canais achatados: faixa[0]=R, faixa[1]=G, faixa[2]=B
    faixa = []
    for cor in range(3):
        if c == 3:
            faixa.append(img_rgb[:, :, cor].flatten())
        else:
            # Imagem em escala de cinza
            faixa.append(img_rgb[:, :, 0].flatten())

    n_pixels = len(faixa[0]) if faixa else n * m

    # Inicialização: sorteia K pixels aleatórios como centroides
    centroid = []
    for k in range(K):
        px = np.random.randint(0, n_pixels)
        v0 = int(faixa[0][px])
        v1 = int(faixa[1][px])
        v2 = int(faixa[2][px])
        centroid.append([v0, v1, v2])

    # Loop K-means até convergir
    iteracao = 0
    CLUSTER = [[] for _ in range(K)]

    while iteracao < MAX_ITER:
        iteracao += 1

        # Atribuir cada pixel ao cluster mais próximo
        CLUSTER = [[] for _ in range(K)]
        for px in range(n_pixels):
            v = np.array([faixa[0][px], faixa[1][px], faixa[2][px]])
            distancias = [np.linalg.norm(v - np.array(centroid[k])) for k in range(K)]
            cluster_idx = np.argmin(distancias)
            CLUSTER[cluster_idx].append(px)

        # Calcular novos centroides
        novo_centroid = []
        for k in range(K):
            if len(CLUSTER[k]) > 0:
                soma = np.zeros(3)
                for px in CLUSTER[k]:
                    soma += np.array([faixa[0][px], faixa[1][px], faixa[2][px]])
                novo_c = (soma / len(CLUSTER[k])).astype(int).tolist()
                novo_centroid.append(novo_c)
            else:
                novo_centroid.append(centroid[k])

        # Verificar convergência: centroides antigos == novos centroides
        if np.array_equal(np.array(centroid), np.array(novo_centroid)):
            centroid = novo_centroid
            break

        centroid = novo_centroid

    # Reconstrói imagem segmentada: cada pixel recebe a cor do seu centróide
    img_segmentada = np.zeros_like(img_rgb, dtype=np.uint8)
    for k in range(K):
        if not CLUSTER[k]:
            continue
        cor_centroide = np.array(centroid[k], dtype=np.uint8)
        idx_pixels = np.array(CLUSTER[k])
        rows = idx_pixels // m
        cols = idx_pixels % m
        img_segmentada[rows, cols] = cor_centroide

    # Retorna no formato original da imagem
    if img.ndim == 2:
        return img_segmentada[:, :, 0]
    return img_segmentada


# ==========================================
# 2. Descoberta e Ordenação Ligeira (Sem estourar RAM)
# ==========================================
img_dir = "images"
k_list = [2, 3, 4]
R = 3  # Número de repetições por combinação

print("Mapeando imagens e calculando 'n' (apenas cabeçalhos)...")
arquivos_n = []

# Varre os arquivos no diretório especificado
if os.path.exists(img_dir):
    for filename in os.listdir(img_dir):
        if filename.lower().endswith((".png", ".jpg", ".jpeg", ".bmp", ".tif")):
            filepath = os.path.join(img_dir, filename)

            # Image.open lê apenas os metadados. Não aloca a matriz de pixels.
            with Image.open(filepath) as img:
                w, h = img.size
                n = w * h
                arquivos_n.append({"arquivo": filename, "caminho": filepath, "n": n})

# Ordena a lista de dicionários pelo valor de 'n' crescente
arquivos_n = sorted(arquivos_n, key=lambda x: x["n"])

print(f"{len(arquivos_n)} imagens ordenadas prontas para processamento.")

"""
for k in k_list:
    for r in range(R):
        to = time.perf_counter
        seg_img = sua_kmeans(img_array, k)
        ti = ti.perf_counter()
        if r==0:
            plt.imShow()
            # plt.show()  # headless
"""


# ==========================================
# 3. Execução (Carregando sob demanda)
# ==========================================
resultados = []

for item in arquivos_n:
    n = item["n"]
    filepath = item["caminho"]
    nome_arquivo = item["arquivo"]

    print(f"Carregando {nome_arquivo} para a RAM (n={n})...")

    # Carrega a imagem real para a RAM apenas no momento de usar
    with Image.open(filepath) as img:
        img_array = np.array(img)

    # Executa todas as repetições e Ks para esta imagem
    for k in k_list:
        for r in range(R):
            t0 = time.perf_counter()
            segmenta_imagem(img_array, k)  # A matriz é passada aqui
            t1 = time.perf_counter()

            resultados.append(
                {
                    "arquivo": nome_arquivo,
                    "n": n,
                    "k": k,
                    "repeticao": r,
                    "tempo": (t1 - t0),
                }
            )

    # Libera a RAM explicitamente antes de carregar a próxima imagem
    del img_array
    print(f"Análise de {nome_arquivo} concluída. Memória liberada.")

# Transforma os resultados em DataFrame
df_raw = pd.DataFrame(resultados)

# ==========================================
# 4. Pré-processamento e Validação F.O.C.A.
# ==========================================
if not df_raw.empty:
    df_filtered = pd.DataFrame()

    # Filtragem de Outliers (Percentis 5 e 95)
    for (n, k), group in df_raw.groupby(["n", "k"]):
        p05 = group["tempo"].quantile(0.05)
        p95 = group["tempo"].quantile(0.95)
        valid_mask = (group["tempo"] >= p05) & (group["tempo"] <= p95)
        df_filtered = pd.concat([df_filtered, group[valid_mask]])

    # Validação de Estabilidade (Média, Desvio e CV)
    resumo = (
        df_filtered.groupby(["n", "k"])
        .agg(
            tempo_medio=("tempo", "mean"),
            desvio=("tempo", "std"),
            contagem_valida=("tempo", "count"),
        )
        .reset_index()
    )

    resumo["CV"] = resumo["desvio"] / resumo["tempo_medio"]
    resumo["estavel_CV_menor_15"] = resumo["CV"] < 0.15

    print("\n--- Resumo de Estabilidade ---")
    print(resumo)

    # ==========================================
    # 5. Ajuste de Curvas
    # ==========================================
    def model_n_k_full(X, alpha, beta, gamma, delta):
        n, k = X
        return alpha * (n * k) + beta * n + gamma * k + delta

    def model_n_k_red(X, alpha, beta, gamma):
        n, k = X
        return alpha * (n * k) + beta * n + gamma * k

    def exibir_equacao_ajustada_full(popt, X_data, y_data):
        alpha, beta, gamma, delta = popt
        y_pred = model_n_k_full(X_data, *popt)
        ss_res = np.sum((y_data - y_pred) ** 2)
        ss_tot = np.sum((y_data - np.mean(y_data)) ** 2)
        r2 = 1.0 - (ss_res / ss_tot) if ss_tot != 0 else 0.0

        print("\n" + "="*60)
        print("   MODELO EMPÍRICO AJUSTADO: T(n, K)")
        print("="*60)
        print("Formulação Geral:")
        print("  T(n, K) = α·(n·K) + β·n + γ·K + δ\n")
        print("Parâmetros Identificados:")
        print(f"  α (alpha) = {alpha:14.6e} s/(pixel·cluster)")
        print(f"  β (beta)  = {beta:14.6e} s/pixel")
        print(f"  γ (gamma) = {gamma:14.6e} s/cluster")
        print(f"  δ (delta) = {delta:14.6e} s (overhead base)")
        print("-" * 60)
        print("Equação Parametrizada:")
        print(f"  T(n, K) = ({alpha:.4e})·(n·K) + ({beta:.4e})·n + ({gamma:.4e})·K + ({delta:.4e})")
        print(f"Aderência Estatística (R²): {r2:.4f}")
        print("="*60 + "\n")

    def exibir_equacao_ajustada_red(popt_red, X_data, y_data):
        alpha, beta, gamma = popt_red
        y_pred = model_n_k_red(X_data, *popt_red)
        ss_res = np.sum((y_data - y_pred) ** 2)
        ss_tot = np.sum((y_data - np.mean(y_data)) ** 2)
        r2 = 1.0 - (ss_res / ss_tot) if ss_tot != 0 else 0.0

        print("\n" + "="*60)
        print("   MODELO EMPÍRICO AJUSTADO: T(n, K)")
        print("="*60)
        print("Formulação Geral (reduzida por poucos pontos):")
        print("  T(n, K) = α·(n·K) + β·n + γ·K\n")
        print("Parâmetros Identificados:")
        print(f"  α (alpha) = {alpha:14.6e} s/(pixel·cluster)")
        print(f"  β (beta)  = {beta:14.6e} s/pixel")
        print(f"  γ (gamma) = {gamma:14.6e} s/cluster")
        print("-" * 60)
        print("Equação Parametrizada:")
        print(f"  T(n, K) = ({alpha:.4e})·(n·K) + ({beta:.4e})·n + ({gamma:.4e})·K")
        print(f"Aderência Estatística (R²): {r2:.4f}")
        print("Obs.: Termo δ (overhead) não foi ajustado por insuficiência de pontos (n fixo).")
        print("="*60 + "\n")

    X_data = np.vstack((resumo["n"], resumo["k"]))
    y_data = resumo["tempo_medio"]

    if len(resumo) >= 4:
        popt, _ = curve_fit(model_n_k_full, X_data, y_data, p0=[1e-6, 1e-6, 1e-6, 0.01], maxfev=10000)
        resumo["tempo_predito"] = model_n_k_full(X_data, *popt)
        exibir_equacao_ajustada_full(popt, X_data, y_data)
        model_n_k = model_n_k_full
    else:
        popt_r, _ = curve_fit(model_n_k_red, X_data, y_data, p0=[1e-6, 1e-6, 1e-6], maxfev=10000)
        resumo["tempo_predito"] = model_n_k_red(X_data, *popt_r)
        exibir_equacao_ajustada_red(popt_r, X_data, y_data)
        model_n_k = model_n_k_red

    # ==========================================
    # 6. Plotagens Bidimensionais
    # ==========================================
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

    # Plot A: Tempo vs n
    colors_k = ["red", "green", "blue", "orange", "purple"]
    for idx, k in enumerate(k_list):
        dados_k = resumo[resumo["k"] == k]
        if not dados_k.empty:
            c = colors_k[idx % len(colors_k)]
            ax1.plot(
                dados_k["n"],
                dados_k["tempo_medio"],
                marker="o",
                color=c,
                label=f"K={k} (Empírico)",
            )
            ax1.plot(
                dados_k["n"],
                dados_k["tempo_predito"],
                linestyle="--",
                color=c,
                alpha=0.6,
            )

    ax1.set_xlabel("Número de Pixels (n)")
    ax1.set_ylabel("Tempo Médio de Execução (s)")
    ax1.set_title("Tempo vs Tamanho da Imagem")
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    # Plot B: Tempo vs K
    n_processados = sorted(resumo["n"].unique())
    colors_n = plt.cm.viridis(np.linspace(0, 1, len(n_processados)))

    for idx, n_val in enumerate(n_processados):
        dados_n = resumo[resumo["n"] == n_val]
        if not dados_n.empty:
            ax2.plot(
                dados_n["k"],
                dados_n["tempo_medio"],
                marker="s",
                color=colors_n[idx],
                label=f"n={n_val}",
            )
            ax2.plot(
                dados_n["k"],
                dados_n["tempo_predito"],
                linestyle="--",
                color=colors_n[idx],
                alpha=0.6,
            )

    ax2.set_xlabel("Número de Clusters (K)")
    ax2.set_title("Tempo vs Número de Clusters")
    ax2.set_xticks(k_list)
    ax2.legend()
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig("relatorio_complexidade.png", dpi=300)
    # plt.show()  # headless

    print(
        "\nPipeline concluído. Gráficos gerados e salvos como 'relatorio_complexidade.png'."
    )

    # ==========================================
    # 7. Exportação dos Dados para Avaliação
    # ==========================================
    arquivo_csv = "resultados_foca_aluno.csv"

    # Exporta os dados usando ponto e vírgula como separador e vírgula para decimais,
    # garantindo que o arquivo seja aberto corretamente no Excel em PT-BR.
    resumo.to_csv(arquivo_csv, index=False, float_format="%.6f", sep=";", decimal=",")

    print(f"Tabela de avaliação exportada com sucesso para: {arquivo_csv}")

else:
    print("\nNenhum dado processado. Verifique se o diretório contém imagens válidas.")
