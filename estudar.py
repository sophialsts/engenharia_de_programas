import matplotlib.pyplot as plt   # exibição de imagens e gráficos
import cv2                        # OpenCV: leitura e conversão de imagens
import numpy as np                # operações numéricas com arrays
import time                       # medição do tempo de execução

# ---------------------------------------------------------------
# C_init — fase de inicialização do K-means
# ---------------------------------------------------------------

init = time.time()                # marca o instante inicial (em segundos desde 1970)

img = cv2.imread("foto.jpeg")     # lê a imagem do disco -> array (altura, largura, 3)
                                   # ATENÇÃO: o OpenCV lê em BGR, não em RGB
img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)  # converte BGR -> RGB para o matplotlib
                                             # mostrar as cores corretamente

plt.imshow(img)                   # desenha a imagem na figura atual
plt.show()                        # exibe a figura e ESVAZIA a figura atual

n, m, c = img.shape               # desempacota as dimensões:
                                   #   n = linhas (altura em pixels)
                                   #   m = colunas (largura em pixels)
                                   #   c = canais de cor (3 = R, G, B)
print(f"linhas: {n}, colunas: {m}, cores: {c}")

plano = []                        # guardará cada canal de cor como matriz 2D (n x m)
faixa = []                        # guardará cada canal "achatado" em vetor 1D (n*m)

for cor in range(c):              # percorre os canais: 0 = R, 1 = G, 2 = B
    plano.append(img[:, :, cor])  # fatia todas as linhas e colunas de UM canal
                                   # resultado: matriz 2D de intensidades 0–255

    plt.imshow(plano[-1], cmap="gray")  # [-1] = último item adicionado à lista
    plt.show()                          # mostra o canal isolado em tons de cinza:
                                         # branco = intensidade alta naquele canal

    faixa.append(plano[-1].flatten())   # flatten(): transforma a matriz n x m em
                                         # um vetor de n*m elementos, lendo linha a linha
                                         # (é assim que o K-means enxerga: 1 pixel = 1 amostra)

    plt.scatter(np.arange(len(faixa[-1])), faixa[-1])
                                         # espalha os pontos: eixo X = índice do pixel,
                                         # eixo Y = intensidade daquele pixel
                                         # np.arange(N) gera [0, 1, 2, ..., N-1]
    plt.show()

# definir o número de clusters
K = 2                              # quantos agrupamentos de cor queremos encontrar

centroid = []                      # lista dos centroides iniciais
n_pixels = len(faixa[0])           # total de pixels da imagem (n * m)

for k in range(K):                 # cria um centroide por cluster
    px = np.random.randint(0, n_pixels)  # sorteia o índice de um pixel qualquer

    v0 = faixa[0][px]              # valor R desse pixel
    v1 = faixa[1][px]              # valor G desse pixel
    v2 = faixa[2][px]              # valor B desse pixel

    centroid.append([v0, v1, v2])  # o centroide é um ponto no espaço RGB 3D
    print(f"Centroid {centroid[-1]}")

end = time.time()                  # marca o instante final
tempo_init = end - init            # duração total da inicialização, em segundos
print(f"Tempo de inicialização {tempo_init}")

# ---------------------------------------------------------------
# Agrupamento: atribui cada pixel ao centroide mais próximo
# ---------------------------------------------------------------

tic = time.time()                  # marca o início da fase de agrupamento
CLUSTER = [[] for _ in range(K)]   # cria K listas vazias, uma para cada grupo
                                    # cada lista vai guardar os ÍNDICES dos pixels
                                    # que pertencem àquele grupo

for px in range(n_pixels):         # percorre todos os pixels da imagem
    v = [faixa[0][px], faixa[1][px], faixa[2][px]]  # cor [R, G, B] do pixel atual

    d = []                         # vai guardar a distância desse pixel até cada centroide
    for k in range(K):
        d.append(np.linalg.norm(np.array(v) - np.array(centroid[k])))
        # distância euclidiana entre a cor do pixel e a cor do centroide k
        # quanto menor a distância, mais parecida é a cor

    cluster = np.argmin(d)         # índice do centroide mais próximo (menor distância)
    CLUSTER[cluster].append(px)    # associa o pixel a esse grupo

print(f"Tempo do agrupamento para formar os cluters: {time.time() - tic}")
print(f"Tamanho cluster 1: {len(CLUSTER[0])}\nTamanho cluster 2: {len(CLUSTER[1])}")

# ---------------------------------------------------------------
# Atualização: recalcula os centroides como a média de cada grupo
# ---------------------------------------------------------------

tic = time.time()                  # marca o início da fase de atualização
novo_centroid = []                 # vai guardar os centroides recalculados

for k in range(K):                 # repete para cada grupo
    L = len(CLUSTER[k])            # quantos pixels caíram nesse grupo
    S = np.zeros(3)                # acumulador [0, 0, 0] para somar R, G, B

    for px in CLUSTER[k]:          # percorre cada pixel (pelo índice) do grupo k
        S += [faixa[0][px], faixa[1][px], faixa[2][px]]
        # soma a cor do pixel ao acumulador, posição a posição
        # (R+=R, G+=G, B+=B), pois S é um array numpy

    novo_centroid.append([int(S[0]/L), int(S[1]/L), int(S[2]/L)])
    # divide a soma pela quantidade de pixels do grupo -> média de cor
    # converte para inteiro, já que intensidade de cor vai de 0 a 255
    # ATENÇÃO: se L for 0 (grupo vazio), essa divisão gera um erro

print(f'Novos centroides: {novo_centroid}')
print(f'Tempo: {time.time() - tic}s')

# Fim do C_init