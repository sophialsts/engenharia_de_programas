import random
import numpy as np

# ==========================================================
# MISSAO 3 - STRUCTURE OF ARRAYS (SoA)
# Mesmo codigo do baseline fcm_puro; as UNICAS diferencas estao
# marcadas com "# SoA:". A imagem deixa de ser uma lista de
# pixels [R, G, B] e passa a ser tres vetores independentes
# X_R, X_G, X_B.
# ==========================================================
def fcm_soa(X_R, X_G, X_B, K, m=2.0, max_iter=100, epsilon=0.01):  # SoA: assinatura
    """
    FCM com a imagem desmembrada em tres vetores isolados.
    X_R, X_G, X_B: listas com o canal R, G e B de cada pixel
    K: Numero de clusters
    m: Fator de fuzzificacao (padrao 2.0)
    """
    XC = (X_R, X_G, X_B)  # SoA: apenas 3 referencias; os dados seguem em 3 vetores
    N = len(X_R)  # SoA: N vem do vetor R
    canais = len(XC)  # SoA: 3 canais

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
                    numerador[c] += u_m * XC[c][i]  # SoA: era X[i][c]

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
                    diff = XC[c][i] - C[j][c]  # SoA: era X[i][c]
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
# WRAPPER para o experimentador.py (versao SoA)
# Recebe o array NumPy (H, W, 3), converte para TRES listas
# (X_R, X_G, X_B) DENTRO da funcao cronometrada e chama o FCM.
# ==========================================================
SEMENTE = 42  # mesma semente do baseline


def segmenta_imagem(imagem_array, K, MAX_ITER=100):
    img = np.asarray(imagem_array)
    if img.ndim == 3 and img.shape[2] == 4:  # descarta alpha
        img = img[:, :, :3]
    if img.ndim == 2:  # escala de cinza -> 3 canais
        img = np.stack([img, img, img], axis=-1)

    random.seed(SEMENTE)

    # Conversao SoA: um vetor por canal, com ints nativos do Python
    X_R = img[:, :, 0].flatten().tolist()
    X_G = img[:, :, 1].flatten().tolist()
    X_B = img[:, :, 2].flatten().tolist()

    C, U = fcm_soa(X_R, X_G, X_B, K, max_iter=MAX_ITER)
    return C, U