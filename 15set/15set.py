import matplotlib.pyplot as plt
import cv2
import numpy as np
import time

init = time.time()
img = cv2.imread("foto.jpeg")
img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

plt.imshow(img)
plt.show()

# plt.savefig("resultado.png", bbox_inches="tight")
# print("Imagem salva com sucesso como 'resultado.png'!")

n, m, c = img.shape
print(f"linhas: {n}, colunas: {m}, cores: {c}")

plano = []
faixa = []

for cor in range(c):
    plano.append(img[:, :, cor])
    plt.imshow(plano[-1], cmap="gray")
    plt.show()
    faixa.append(plano[-1].flatten())
    # plt.plot(faixa[-1])
    plt.scatter(np.arange(len(faixa[-1])), faixa[-1])
    plt.show()

# definir o número de clusters
K = 2
centroid = []
n_pixels = len(faixa[0])

for k in range(K):
    px = np.random.randint(0, n_pixels)
    v0 = faixa[0][px]
    v1 = faixa[1][px]
    v2 = faixa[2][px]
    centroid.append([v0, v1, v2])
    print(centroid[-1])

end = time.time()
tempo_init = end - init
print(f"Tempo de inicialização {tempo_init}")

# Fim do C_init
