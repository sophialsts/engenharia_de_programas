import matplotlib.pyplot as plt
import numpy as np

# Dados
N = [1000, 10000, 100000]

# Três séries de tempos médios
tempos_1 = [1.7145e-06, 2.1429e-06, 2.2453e-06]
tempos_2 = [2.1084e-06, 3.2937e-06, 3.2500e-06]
tempos_3 = [2.5488e-06, 3.2093e-06, 3.1840e-06]

plt.figure(figsize=(10, 6))
plt.plot(N, tempos_1, 'o-', label='Tempo 1', linewidth=2, markersize=8)
plt.plot(N, tempos_2, 's-', label='Tempo 2', linewidth=2, markersize=8)
plt.plot(N, tempos_3, '^-', label='Tempo 3', linewidth=2, markersize=8)

plt.xscale('log')
plt.xlabel('Tamanho da Entrada (N)', fontsize=12)
plt.ylabel('Tempo Médio (s)', fontsize=12)
plt.title('Tempo Médio vs Tamanho da Entrada', fontsize=14)
plt.legend(fontsize=11)
plt.grid(True, which='both', linestyle='--', alpha=0.7)
plt.tight_layout()

plt.savefig('tempos_plot.png', dpi=300)
plt.show()