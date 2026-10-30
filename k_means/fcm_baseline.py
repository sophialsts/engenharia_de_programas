import random
import numpy as np

# ==========================================================
# BASELINE - fcm_puro.py (codigo oficial do professor)
# NAO ALTERAR: qualquer mudanca aqui contamina a comparacao.
# ==========================================================
def fcm_puro(X, K, m=2.0, max_iter=100, epsilon=0.01):
    """
    Implementacao FCM "Puro" (Baseline) sem bibliotecas avancadas
    ou funcoes escuras (utilizado por todas as equipes como base).
    X: Imagem (Lista de pixels, onde cada pixel e [R, G, B])
    K: Numero de clusters
    m: Fator de fuzzificacao (padrao 2.0)
    """
    N = len(X)
    canais = len(X[0])  # Tipicamente 3 (RGB)

    # FASE 1: INICIALIZACAO DA MATRIZ DE PERTINENCIA (U)
    U = []
    for i in range(N):
        linha = []
        soma_linha = 0.0

        for j in range(K):
            val = random.random()
            linha.append(val)
            soma_linha += val

        for j in range(K):
            linha[j] = linha[j] / soma_linha

        U.append(linha)

    # LACO PRINCIPAL DO FCM
    for iteracao in range(max_iter):

        # FASE 2: ATUALIZACAO DOS CENTROIDES
        C = []
        for j in range(K):
            numerador = [0.0] * canais
            denominador = 0.0

            for i in range(N):
                u_m = U[i][j] ** m
                denominador += u_m

                for c in range(canais):
                    numerador[c] += u_m * X[i][c]

            centroide_j = []
            for c in range(canais):
                centroide_j.append(numerador[c] / denominador)
            C.append(centroide_j)

        # FASE 3 E 4: ASSOCIACAO (DISTANCIA) E CONVERGENCIA
        U_nova = []
        max_diff = 0.0

        for i in range(N):
            linha_nova = [0.0] * K
            distancias = [0.0] * K

            for j in range(K):
                soma_quadrados = 0.0
                for c in range(canais):
                    diff = X[i][c] - C[j][c]
                    soma_quadrados += diff * diff

                distancias[j] = soma_quadrados ** 0.5

            for j in range(K):
                if distancias[j] == 0.0:
                    linha_nova[j] = 1.0
                    for k in range(K):
                        if k != j:
                            linha_nova[k] = 0.0
                    break

                soma_dist = 0.0
                for k in range(K):
                    razao = distancias[j] / distancias[k]
                    soma_dist += razao ** (2.0 / (m - 1.0))

                pertinencia = 1.0 / soma_dist
                linha_nova[j] = pertinencia

                diff_u = pertinencia - U[i][j]
                if diff_u < 0:
                    diff_u = -diff_u

                if diff_u > max_diff:
                    max_diff = diff_u

            U_nova.append(linha_nova)

        U = U_nova

        if max_diff < epsilon:
            break

    return C, U


# ==========================================================
# WRAPPER para o experimentador.py (versao BASELINE / AoS)
# Recebe o array NumPy (H, W, 3), converte para lista de
# pixels [R, G, B] (formato AoS) DENTRO da funcao cronometrada
# e chama o FCM puro.
# ==========================================================
SEMENTE = 42  # mesma semente nas duas versoes -> mesmo trabalho por repeticao


def segmenta_imagem(imagem_array, K, MAX_ITER=100):
    img = np.asarray(imagem_array)
    if img.ndim == 3 and img.shape[2] == 4:  # descarta alpha
        img = img[:, :, :3]
    if img.ndim == 2:  # escala de cinza -> 3 canais
        img = np.stack([img, img, img], axis=-1)

    random.seed(SEMENTE)

    # Conversao AoS: lista de pixels [R, G, B] com ints nativos do Python
    X = img.reshape(-1, 3).tolist()

    C, U = fcm_puro(X, K, max_iter=MAX_ITER)
    return C, U