# 📋 Calibração F.O.C.A. — Relatório Técnico de Calibração Empírica

**Equipe**: Sophia Lima & Isabel Costa  
**Disciplina**: Engenharia de Programas 2026.2  
**Professor**: Prof. Dr. Diego Frias  
**Setup**: 13th Gen Intel Core i7-1355U, 16GB RAM, Ubuntu 24.04.3, Python 3.12.3 (CPython)  
**Data**: 08/09/2026

---

## 📌 Visão Geral das Fases

| Fase | Descrição | Status |
|------|-----------|--------|
| **Fase 1** | Correção e homologação das 4 operações com CV ≥ 0.15 | ✅ CONCLUÍDA |
| **Fase 2** | Preparação de materiais (dados, gráficos, painéis) | ✅ CONCLUÍDA |
| **Fase 3** | Preenchimento das seções 1–2–4 do relatório | 📝 PENDENTE |
| **Fase 4** | Respostas das 5 questões de Análise Crítica (Seção 5) | 📝 PENDENTE |

---

## 📁 Estrutura de Arquivos

```
engenhariaDeProgramas/
│
├── 📄 DOCUMENTOS DE REFERÊNCIA (PDFs)
│   ├── RelatorioTecnico/
│   │   ├── RelatorioTecnico_Calibracao.pdf   ← TEMPLATE do relatório final
│   │   └── Filtragem-de-Outliers-em-Engenharia-de-Programas.pdf  ← Metodologia de filtragem
│   ├── contagem_primitivas_em_loops-1.pdf    ← Explicação do método FOCA para loops
│   ├── RTA - Validação de Setup Computacional V3.pdf  ← RTA (primeira entrega)
│   └── descricao_sistema_avaliacao_EP_2026_2.pdf  ← Rubrica de avaliação
│
├── 🐍 SCRIPTS DE CALIBRAÇÃO
│   ├── extrair_dados_calibracao.py           ← Script PRINCIPAL: mede 25 operações, gera CSV + histogramas
│   ├── corrigir_constant_folding.py          ← Corrige constant folding (cte_int_eq_cte_int) + re-mede 4 ops problemáticas
│   ├── remedir_problematicas.py              ← Re-mede 4 ops com parâmetros mais robustos (N_ITER=50000, WARMUP=50, REPS=500)
│   ├── completar_calibracao.py              ← Mede 8 operações restantes (τf) e adiciona ao CSV
│   ├── gerar_paineis.py                    ← Gera 3 painéis gráficos (Scatter + Hist Bruto + Hist Filtrado) para τa, τc, τo
│   └── 27ago.py                            ← Validação de setup com sigma-clipping iterativo (gera plots de validação)
│
├── 📊 CSV DE RESULTADOS
│   └── resultados/calibracao/calibracao_foca.csv  ← DADOS CENTRAIS: todas as 25 operações com μ, σ, CV filtrados
│
├── 📈 GRÁFICOS — RESULTADOS DA CALIBRAÇÃO
│   ├── resultados/calibracao/              ← Histogramas individuais (25 PNGs)
│   │   ├── hist_var_int_cte_int.png
│   │   ├── hist_var_float_cte_float.png
│   │   ├── hist_var_bool_cte_bool.png
│   │   ├── hist_var_int_var_int.png
│   │   ├── hist_var_float_var_float.png
│   │   ├── hist_cte_int_eq_cte_int.png
│   │   ├── hist_var_int_eq_cte_int.png
│   │   ├── hist_var_int_eq_var_int.png
│   │   ├── hist_var_float_eq_var_float.png
│   │   ├── hist_var_int_ne_var_int.png
│   │   ├── hist_var_int_gt_var_int.png
│   │   ├── hist_var_float_lt_cte_float.png
│   │   ├── hist_var_int_add_cte_int.png
│   │   ├── hist_var_int_add_var_int.png
│   │   ├── hist_var_float_add_var_float.png
│   │   ├── hist_var_int_sub_var_int.png
│   │   ├── hist_var_int_mul_var_int.png
│   │   ├── hist_var_float_mul_var_float.png
│   │   ├── hist_var_float_div_var_float.png
│   │   ├── hist_var_int_floordiv_var_int.png
│   │   ├── hist_var_int_mod_var_int.png
│   │   ├── hist_math_sqrt_float.png
│   │   ├── hist_abs_int.png
│   │   ├── hist_list_append.png
│   │   ├── hist_len_list.png
│   │   └── paineis/                        ← PAINÉIS 3-EM-1 (Seção 3 do relatório)
│   │       ├── painel_τa.png              ← Scatter + Hist Bruto + Hist Filtrado (τa)
│   │       ├── painel_τc.png              ← Scatter + Hist Bruto + Hist Filtrado (τc)
│   │       └── painel_τo.png              ← Scatter + Hist Bruto + Hist Filtrado (τo)
│   │
│   └── resultados/validacao/               ← Gráficos de validação do setup (Seção do RTA)
│       ├── plot1_scatter.png              ← Dispersão: Tempo × Repetição
│       ├── plot2_histogramas.png          ← Tempo Médio × Tamanho da Entrada
│       ├── plot3_media_sigma.png          ← µ vs σ por tamanho de entrada
│       └── plot4_cv.png                   ← CV × Tamanho da entrada (critério < 0.15)
│
├── 📊 GRÁFICOS — OUTRAS MEDIÇÕES (REFERÊNCIA)
│   ├── resultados/loops/                   ← Benchmark de loop (resultados/loops/*.png)
│   │   ├── tempo_n_1000.png, tempo_n_10000.png, tempo_n_100000.png
│   │   ├── hist_n_1000.png, hist_n_10000.png, hist_n_100000.png
│   │   ├── hist_baseline (loop vazio)_loop_vazio.png
│   │   └── foca_comparacao.png
│   ├── resultados/operacao/                ← Operações OCA (soma, mult, div, mod)
│   │   ├── hist_o_op_multiplicacao.png
│   │   ├── hist_o_op_divisao.png
│   │   ├── hist_o_op_soma.png
│   │   └── hist_o_op_modulo.png
│   ├── resultados/comparacao/              ← Comparações (var<var vs var<const, igualdade)
│   │   ├── cmp_var_var_vs_var_const.png
│   │   ├── hist_c_cmp_var_const.png
│   │   ├── hist_c_cmp_var_var.png
│   │   └── hist_c_cmp_igualdade.png
│   ├── resultados/atribuicao/              ← Atribuições (simples, variável)
│   │   ├── hist_a_atrib_simples.png
│   │   └── hist_a_atrib_variavel.png
│   ├── resultados/oca/                     ← Gráfico comparativo OCA completo
│   │   ├── oca_comparacao.png
│   │   └── foca_comparacao.png
│   └── resultados/calibracao/paineis/      ← Painéis (já listados acima)
│
└── 📝 OUTROS SCRIPTS
    ├── 08_set.py                           ← Medição OCA de primitivas (resultados/operacao, comparacao, atribuicao)
    ├── loop.py                             ← Loop de benchmark (similar ao 27ago.py)
    ├── plot_tempos.py                      ← Gráfico de tempo vs tamanho de entrada
    ├── estudar.py                          ← Código de exemplo para estudo (K-means, OpenCV)
    ├── teste.py                            ← Script de teste
    └── lista_exercicios_EP_c1.pdf          ← Lista de exercícios (referência teórica)
```

---

## 📖 Mapeamento: Arquivos → Seções do Relatório Técnico

O **RelatorioTecnico_Calibracao.pdf** é o template a ser preenchido. As seções são numeradas de 1 a 5.

### Seção 1 — Especificação Rigorosa do Setup Computacional
**O que preencher**: Dados do hardware, SO, linguagem, plano de energia.

| Informação | Valor | Fonte |
|-----------|-------|-------|
| Processador | Intel Core i7-1355U (13th Gen) | `lscpu` / `/proc/cpuinfo` |
| Núcleos/Threads | 10 núcleos / 12 threads | `lscpu` |
| Cache L3 | 12288 KB (12 MB) | `/proc/cpuinfo` |
| Frequência | 400 MHz – 5000 MHz | `/sys/devices/system/cpu/` |
| RAM | 16 GB | `lscpu` |
| Sistema Operacional | Ubuntu 24.04.3 LTS | `/etc/os-release` |
| Kernel | 7.0.0-31 | `/proc/version` |
| Plano de Energia | `powersave` | `/sys/devices/system/cpu/cpu*/cpufreq/scaling_governor` |
| Linguagem/Versão | Python 3.12.3 (CPython), GCC 13.3.0 | `python3 --version` |

---

### Seção 2 — Parâmetros Metodológicos do Experimento
**O que preencher**: Hipérparâmetros de captura e justificativa.

| Parâmetro | Valor | Justificativa |
|-----------|-------|---------------|
| Tamanho da Amostra Interna (n) | 10.000 iterações por repetição | Estabilidade estatística |
| Número de Repetições Globais (r) | 300 repetições | Confiabilidade da média |
| Estratégia de Filtro | IQR (Percentis 25-75) com fator 3.0 | Robusto, imune a outliers extremos |
| Warmup | 10 iterações (calibração) / 50 (correção) | Estabiliza cache e branch predictor |
| GC | Desativado durante medição | Elimina interferência do Garbage Collector |

**Justificativa do filtro IQR**: Baseada no PDF *"Filtragem de Outliers em Engenharia de Programas"*. O método de Percentis/IQR é estruturalmente superior ao desvio padrão porque é imune à magnitude dos outliers — a média e o σ são corrompidos por outliers, expandindo o intervalo de corte e deixando o ruído passar. O IQR usa a posição ordinal dos dados, não a magnitude, tornando-o robusto.

---

### Seção 3 — Painel Gráfico de Estabilidade (EXIGÊNCIA VISUAL) ✅ PRONTA
**O que inserir**: Para cada macro-primitiva (τa, τc, τo), um painel com 3 gráficos.

**Arquivos** (já gerados com dados corrigidos):
- `resultados/calibracao/paineis/painel_τa.png` → Seção 3, macro-primitiva **τa**
- `resultados/calibracao/paineis/painel_τc.png` → Seção 3, macro-primitiva **τc**
- `resultados/calibracao/paineis/painel_τo.png` → Seção 3, macro-primitiva **τo**

**Cada painel contém**:
1. **Gráfico de Dispersão Temporizada**: Eixo X (Iteração r) vs Eixo Y (Tempo). Evidencia picos do SO/GC.
2. **Histograma de Dados Brutos**: Frequência mostrando assimetria e caudas longas (Thermal Throttling/Cache Misses).
3. **Histograma Pós-Filtragem**: Distribuição após filtro IQR, com linhas de corte visíveis. Deve tender à normalidade.

**Nota**: Os painéis foram regenerados com o setup corrigido para `cte_int_eq_cte_int` (`a = 5; b = 10; a == b`). Os histogramas individuais também foram atualizados.

---

### Seção 4 — Matrizes Exaustivas de Calibração (τa, τc, τo, F) ✅ DADOS PRONTOS
**O que preencher**: Tabelas com μ_filtrado, σ_filtrado, CV_filtrado para cada operação. Todas as 25 operações têm CV < 0.15 (homologadas).

**Fonte dos dados**: `resultados/calibracao/calibracao_foca.csv` (25 linhas, todas homologadas)

**Dados atualizados após correções** (2026-09-20):

#### 4.1 — Custo de Atribuições (τa) — Responsável: Aluno 1
**Operações**: 5 primitivas
| Operação | μ_fil (τa) | σ_fil | CV_fil |
|----------|-----------|-------|--------|
| var int ← cte int | 9.28e-06 | 2.57e-07 | 0.0277 |
| var float ← cte float | 9.70e-06 | 1.74e-07 | 0.0179 |
| var bool ← cte bool | 9.34e-06 | 1.45e-07 | 0.0156 |
| var int ← var int | 9.64e-06 | 3.51e-07 | 0.0364 |
| var float ← var float | 9.81e-06 | 1.81e-07 | 0.0184 |

#### 4.2 — Custo de Comparações (τc) — Responsável: Aluno 2
**Operações**: 7 primitivas
| Operação | μ_fil (τc) | σ_fil | CV_fil |
|----------|-----------|-------|--------|
| cte int == cte int | 5.53e-06 | 7.24e-07 | 0.1309 |
| var int == cte int | 1.10e-05 | 1.04e-06 | 0.0944 |
| var int == var int | 1.09e-05 | 6.04e-07 | 0.0554 |
| var float == var float | 6.87e-06 | 4.16e-07 | 0.0607 |
| var int != var int | 1.08e-05 | 1.98e-07 | 0.0183 |
| var int > var int | 1.14e-05 | 1.57e-06 | 0.1377 |
| var float < cte float | 1.07e-05 | 2.54e-07 | 0.0237 |

#### 4.3 — Custo de Operações Matemáticas (τo) — Responsável: Aluno 3
**Operações**: 9 primitivas
| Operação | μ_fil (τo) | σ_fil | CV_fil |
|----------|-----------|-------|--------|
| int + cte int | 1.00e-05 | 3.00e-07 | 0.0301 |
| int + int | 1.04e-05 | 2.78e-07 | 0.0268 |
| float + float | 6.66e-06 | 7.96e-07 | 0.1195 |
| int - int | 6.53e-06 | 5.51e-07 | 0.0843 |
| int * int | 1.01e-05 | 2.09e-07 | 0.0207 |
| float * float | 1.02e-05 | 7.71e-07 | 0.0757 |
| float / float | 1.00e-05 | 2.50e-07 | 0.0250 |
| int // int | 1.01e-05 | 2.25e-07 | 0.0223 |
| int % int | 9.93e-06 | 2.13e-07 | 0.0214 |

#### 4.4 — Custo de Funções Opacas (τf) — Responsável: Equipe (Opcional, +1 ponto extra)
**Operações**: 4 primitivas
| Função | μ_fil (τf) | σ_fil | CV_fil |
|--------|-----------|-------|--------|
| math.sqrt(var float) | 1.27e-05 | 2.39e-07 | 0.0187 |
| abs(var int) | 1.20e-05 | 2.89e-07 | 0.0241 |
| lst.append(a) | 1.26e-05 | 3.16e-07 | 0.0251 |
| len(lst) | 1.25e-05 | 2.14e-07 | 0.0171 |

---

### Seção 5 — Análise Crítica da Engenharia F.O.C.A. (DEFESA DOS RESULTADOS)
**O que fazer**: Responder às 5 questões com base nos dados das matrizes e nos PDFs de referência.

#### Questão 1 — Acesso à Memória (τa)
**Base**: Comparar `var ← cte` vs `var ← var` na tabela τa.
**Referência**: Dados do CSV (τa: var_int_cte_int vs var_int_var_int).
**O que explicar**: O gargalo arquitetural de `var ← var` é o acesso à memória (RAM → registrador). `var ← cte` tem o valor embutido na instrução (código). Diferença de tempo reflete o custo de load da memória.

#### Questão 2 — ALU vs FPU (τo)
**Base**: Comparar operações int vs float na tabela τo.
**Referência**: Dados do CSV.
**O que explicar**: Impacto percentual do tempo de processamento int vs float. Discutir se o i7-1355U favorece algum dos dois. Considerar que divisão float é muito mais lenta que soma int.

#### Questão 3 — Complexidade de Hardware (τo)
**Base**: Ordenar Soma, Multiplicação, Divisão na tabela τo.
**Referência**: Dados do CSV + teoria de circuitos digitais.
**O que explicar**: Soma < Multiplicação < Divisão. Explicar circuitos: somadores (half/full adder), multiplicadores (array/Booth), divisores (restoration/non-restoration). A diferença empírica reflete a complexidade eletrônica dos circuitos.

#### Questão 4 — Interferência Sistêmica e Filtragem
**Base**: Comparar métricas antes/depois do filtro IQR.
**Referência**: PDF *"Filtragem de Outliers em Engenharia de Programas"*.
**O que explicar**: Quais métricas melhoraram. Eventos físicos/lógicos que geraram anomalias:
- Scheduler do SO (troca de contexto)
- Garbage Collector do CPython
- Thermal Throttling (redução de clock por temperatura)
- Cache misses, branch prediction misses
- Interrupts de hardware

#### Questão 5 — FLOPS/IPS e Benchmarking (Pior Caso)
**Base**: Identificar a primitiva homologada mais lenta e calcular 1/τ_pior.
**Referência**: Dados do CSV + specs do i7-1355U (4.7 GHz turbo).
**O que explicar**: Cálculo de FLOPS/IPS mínimo garantido. Comparação com a frequência teórica do fabricante. Discussão sobre overhead do Python e IPC (Instructions Per Clock).

---

## 🔄 Fluxo de Trabalho Resumido

```
1. Executar: python3 extrair_dados_calibracao.py
   → Gera calibracao_foca.csv + 25 histogramas PNG

2. Corrigir scripts (se necessário):
   - gerar_paineis.py: alterar setup de cte_int_eq_cte_int para "a = 5; b = 10" / "a == b"
   - remedir_problematicas.py: mesma correção

3. Executar: python3 remedir_problematicas.py
   → Re-mede cte_int_eq_cte_int, var_float_eq_var_float,
     var_float_add_var_float, var_int_sub_var_int com N_ITER=50000, WARMUP=50, REPS=500

4. Executar: python3 corrigir_constant_folding.py (ou medir individualmente)
   → Re-mede cte_int_eq_cte_int com setup corrigido (N_ITER=10000, REPS=300)

5. Executar: python3 gerar_paineis.py
   → Gera os 3 painéis 3-em-1 para τa, τc, τo

6. Executar: python3 27ago.py
   → Gera os 4 plots de validação do setup

7. Verificar: todos os CVs < 0.15 no CSV

8. Preencher o template do RelatorioTecnico_Calibracao.pdf
   com os dados das seções 1-5 acima
```

### ⚠️ Nota sobre scripts de correção
Os scripts `corrigir_constant_folding.py` e `remedir_problematicas.py` reescrevem o CSV **apenas ao final**. Se forem interrompidos durante a execução, o CSV pode ficar corrompido. Para evitar isso:
- Use `python3 ... &` ou rode em `tmux`/`screen` se necessário
- Ou edite o CSV diretamente via Python para atualizar linhas específicas
- Após qualquer correção, execute `gerar_paineis.py` para regenerar os painéis com os dados atualizados

---

## 📐 Notas Metodológicas

- **Filtro IQR**: Q1 - 3×IQR ≤ x ≤ Q3 + 3×IQR. Se IQR = 0, usa percentis 2.5-97.5 como fallback.
- **CV**: CV = σ / μ. Apenas operações com CV < 0.15 são homologadas.
- **GC desativado**: `gc.disable()` durante medição para eliminar interferência do Garbage Collector.
- **Warmup**: 10-50 iterações de aquecimento antes da medição para estabilizar cache e branch predictor.
- **Tempo medido**: `time.perf_counter()` — alta resolução, monotônico.
- **Unidade**: Segundos (s), com notação científica (ex: 9.28e-06 = 9.28 microssegundos).
