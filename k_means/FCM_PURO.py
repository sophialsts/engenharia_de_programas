import random

def fcm_Puro(X, K, m=2.0, max_iter=100, epsilon=0.01):
    """
    Implementação FCM "From Scratch" e sem funções escuras.
    X: Imagem (Lista de pixels, onde cada pixel é [R, G, B])
    K: Número de clusters
    m: Fator de fuzzificação (padrão 2.0)
    """
    N = len(X)
    canais = len(X[0]) # Tipicamente 3 (RGB)
    
    # ---------------------------------------------------------
    # FASE 1: INICIALIZAÇÃO DA MATRIZ DE PERTINÊNCIA (U)
    # ---------------------------------------------------------
    U = []
    for i in range(N):
        linha = []
        soma_linha = 0.0
        
        # Preenche com valores aleatórios
        for j in range(K):
            val = random.random()
            linha.append(val)
            soma_linha += val
            
        # Garante que a soma das pertinências do pixel seja 1.0 (sem função sum!)
        for j in range(K):
            linha[j] = linha[j] / soma_linha
            
        U.append(linha)
        
    # ---------------------------------------------------------
    # LACO PRINCIPAL DO FCM
    # ---------------------------------------------------------
    for iteracao in range(max_iter):
        
        # ---------------------------------------------------------
        # FASE 2: ATUALIZAÇÃO DOS CENTROIDES
        # ---------------------------------------------------------
        C = []
        for j in range(K):
            numerador = [0.0] * canais
            denominador = 0.0
            
            for i in range(N):
                # Otimização: calcula u_ij elevado a 'm' uma vez
                u_m = U[i][j] ** m
                denominador += u_m
                
                for c in range(canais):
                    numerador[c] += u_m * X[i][c]
            
            # Centroide final J
            centroide_j = []
            for c in range(canais):
                centroide_j.append(numerador[c] / denominador)
            C.append(centroide_j)
            
        # ---------------------------------------------------------
        # FASE 3 E 4: ASSOCIAÇÃO (DISTÂNCIA) E CONVERGÊNCIA
        # ---------------------------------------------------------
        U_nova = []
        max_diff = 0.0 # Controla o critério de parada (sem usar abs() ou max())
        
        for i in range(N):
            linha_nova = [0.0] * K
            distancias = [0.0] * K
            
            # Passo A: Calcula todas as distâncias do Pixel I para os K Centroides
            for j in range(K):
                soma_quadrados = 0.0
                for c in range(canais):
                    diff = X[i][c] - C[j][c]
                    soma_quadrados += diff * diff # Sem math.pow()
                
                # Raiz quadrada sem usar math.sqrt() (Função Escura banida)
                distancias[j] = soma_quadrados ** 0.5 
                
            # Passo B: Atualiza a pertinência do Pixel I
            for j in range(K):
                # Tratamento de singularidade (se o pixel cair exatamente no centroide)
                if distancias[j] == 0.0:
                    linha_nova[j] = 1.0
                    for k in range(K):
                        if k != j:
                            linha_nova[k] = 0.0
                    break
                    
                soma_dist = 0.0
                for k in range(K):
                    # Sem early exit (Missão 5 banida) e iterando normalmente
                    razao = distancias[j] / distancias[k]
                    soma_dist += razao ** (2.0 / (m - 1.0))
                    
                pertinencia = 1.0 / soma_dist
                linha_nova[j] = pertinencia
                
                # Passo C: Cálculo do Erro de Convergência (Fase 4 embutida)
                diff_u = pertinencia - U[i][j]
                
                # Simulando a função abs() que está banida
                if diff_u < 0:
                    diff_u = -diff_u
                    
                # Simulando a função max() que está banida
                if diff_u > max_diff:
                    max_diff = diff_u
                    
            U_nova.append(linha_nova)
            
        # Atualiza a matriz global
        U = U_nova
        
        # Avalia se a maior variação na matriz U foi menor que a tolerância
        print(f"Iteração {iteracao:02d} | Erro (Delta U): {max_diff:.6f}")
        if max_diff < epsilon:
            print(f"-> Convergiu com sucesso na iteração {iteracao}!")
            break
            
    return C, U

# ==========================================
# TESTE DE BANCADA (MOCK DATA)
# ==========================================
if __name__ == "__main__":
    # Gerando 100 pixels aleatórios RGB simulando uma imagem minúscula (AoS puro)
    N_pixels = 100
    imagem_mock = [[random.uniform(0, 255) for _ in range(3)] for _ in range(N_pixels)]
    
    # Rodando o FCM Puro
    print("Iniciando FCM Puro...")
    centroides, matriz_u = fcm_Puro(X=imagem_mock, K=3, m=2.0, max_iter=50, epsilon=0.001)
    
    print("\nCentroides Finais Encontrados:")
    for idx, c in enumerate(centroides):
        print(f"C{idx}: R={c[0]:.2f}, G={c[1]:.2f}, B={c[2]:.2f}")