# Relatório

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
K = 2                             # quantos agrupamentos de cor queremos encontrar

centroid = []                     # lista dos centroides iniciais
n_pixels = len(faixa[0])          # total de pixels da imagem (n * m)

for k in range(K):                # cria um centroide por cluster
    px = np.random.randint(0, n_pixels)  # sorteia o índice de um pixel qualquer

    v0 = faixa[0][px]             # valor R desse pixel
    v1 = faixa[1][px]             # valor G desse pixel
    v2 = faixa[2][px]             # valor B desse pixel

    centroid.append([v0, v1, v2]) # o centroide é um ponto no espaço RGB 3D
    print(f"Centroid {centroid[-1]}")

end = time.time()                 # marca o instante final
tempo_init = end - init           # duração total da inicialização, em segundos
print(f"Tempo de inicialização {tempo_init}")

init_agrupamento = time.time()
CLUSTER = [[] for _ in range (K)]
for px in range (n_pixels):
    v = [faixa[0][px], faixa[1][px], faixa[2][px]]
    d = []
    for k in range(K):
        d.append(np.linalg.norm(np.array(v) - np.array(centroid[k]))) # calcula a distância entre o vértice e o centroide

    cluster = np.argmin(d) # retorna o índice que possui o valor mínimo
    CLUSTER[cluster].append(px)

end_agrupamento = time.time()
tempo_agrupamento = end_agrupamento - init_agrupamento
print(f"Tempo do agrupamento para formar os cluters: {tempo_agrupamento}")
print(f"Tamanho cluster 1: {len(CLUSTER[0])}\nTamanho cluster 2: {len(CLUSTER[1])}")

tic = time.time()
novo_centroid = []

for k in range(K):
    S = np.array(3)
    for px in CLUSTER[k]:
        S += px
    novo_centroid[k] = int(S / len(CLUSTER[k]))

print(f'Novos centroides: {novo_centroid}')
print(f'Tempo: {time.time() - tic}s')


# Fim do C_init