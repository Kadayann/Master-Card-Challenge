# 4 · Conclusões e Recomendações
## Priceless Bank — Mastercard Challenge 2026 · Inteli

---

## 1. Diagnóstico em uma frase

- O Priceless Bank não está perdendo clientes. Ele nunca foi o banco principal deles, e agora paroude conquistar novos.

O share cai de 33% para 19% entre o 1T25 e o 4T25. A decomposição desse número mostra que a causa
não é a que pensávamos inicialmente.

| O que se supôs | O que os dados mostram |
|---|---|
| Os clientes estão indo embora | A carteira ativa cai só 3,0% (1.403 → 1.361) |
| O produto cartão decepcionou | A frequência de uso cai 48,1% (13,6 → 7,1 cliente/trimestre) |
| O dinheiro está fugindo | A captação líquida segue positiva em todos os 12 trimestres |

Então, a queda de share é quase toda share-of-wallet, não churn. E a origem disso
é estrutural: sem o salário do cliente, o banco nunca teve mais do que uma fatia do bolso dele.

---

## 2. A cadeia causal

Três achados, validados e com explicações rivais testadas, encadeados:

```
  A conta nunca foi a principal                    →   O vínculo é fraco por construção
  (4,3% recebem PJ recorrente · sai 7,4x mais
   do que entra · 1.430 de 1.430 clientes com
   fluxo líquido negativo)
                    ↓
  Sem vínculo, o uso esvazia sozinho               →   Frequência -48%, carteira intacta
  (só 27 clientes sumiram entre os semestres)
                    ↓
  E a entrada de novos parou                       →   Aquisição -85%, emissão de cartão = ZERO
  (26 e 27 contas nos dois últimos trimestres          desde junho de 2025
   · 0 cartões emitidos em 7 meses)
```

Enquanto isso, os concorrentes atacam exatamente essas frentes:

| Concorrente | Diferencial | Share 1T25 → 4T25 |
|---|---|---|
| LuminaPay | Cashback, sem taxa de cartão, PIX no crédito, abertura 100% digital | 17% → 30% |
| Aurora Bank | Home Broker, investimento convertido em limite | 6% → 14% |
| Priceless Bank | — nenhum diferencial identificável na base | 33% → 19% |

---

## 3. Conclusão central

Deixar de disputar transações e passar a disputar principalidade.

Todo real investido em reativar transação de cartão sem antes resolver o vínculo é dinheiro gasto no
sintoma. A ordem correta é: trazer a renda → reabrir a entrada → destravar o cross-sell.

---

## 4. As frentes de ação do plano

### Frente 1 · Conquistar a principalidade

Insight que sustenta (Hipótese 1 · confirmada). Procuramos o salário na base e ele não está lá. Apenas
4,3% dos clientes (62 de 1.427) recebem PIX de PJ com regularidade mensal, e o recebimento mediano
de PJ é de R$ 160, não é salário. Para cada R$ 1,00 que entra por PIX, saem R$ 7,36.
E os 1.430 clientes que usam PIX têm fluxo líquido negativo, sem exceção.

A conta funciona como conta de passagem: o dinheiro chega de outro lugar e é imediatamente empurrado
para fora.

| # | O que fazer | Detalhe |
|---|---|---|
| 1.1 | Programa de domicílio de renda | Portabilidade de salário assistida, com incentivo condicionado à permanência do crédito por 3 ciclos |
| 1.2 | Ativar Open Finance | O benchmarking mostra 44% a 82% dos clientes dos concorrentes já exportando dados. O Priceless não aparece nesse eixo |
| 1.3 | **Rendimento no saldo em conta | Remover o incentivo estrutural de tirar o dinheiro no mesmo dia |
| 1.4 | Gatilho de retenção de saldo | Detectar o padrão "entrou e saiu em <24h" e acionar oferta no momento |

A Meta é: Clientes com crédito recorrente mensal: 4,3% → 25% em 12 meses.
Razão saída/entrada por PIX: 7,36× → 4,0×.

Se pegarmos o Papaya bank (42,7% de principalidade) e LuminaPay (37,4%) lideram exatamente essa métrica
no benchmarking. Principalidade é o que sustenta share.

---

### Frente 2 · Reabrir o funil de entrada

Insight que sustenta (Hipótese 3 · refutada, e a refutação vale mais). A hipótese era que o cliente parou de
pedir cartão por insatisfação. Os dados dizem o contrário:

- 2023 é o ano de maior frequência da série (13,7 tx/trimestre), não o menor
- a safra de 2023 fez 47,7 transações no primeiro ano, quase igual à de 2024 (50,4)  e 77% dela
  continua ativa três anos depois
- cada safra só recebe cartão no ano em que entra. O cartão sai junto com a conta, não a pedido.

Em 2025 o banco abriu 189 contas e emitiu 27 cartões. E desde junho de 2025 não emitiu
nenhum. A emissão não secou por falta de demanda, secou porque a aquisição despencku.

| # | O que fazer | Detalhe |
|---|---|---|
| 2.1 | Destravar a emissão de cartão  | Zero cartões em 7 meses é algo que não pode acontecer de jeito nenhum |
| 2.2 | Abertura de conta 100% digital | Os dois concorrentes que mais cresceram (LuminaPay, Aurora) são digitais. O benchmarking associa canal físico a baixa maturidade digital |
| 2.3 | Ativação assistida em 30 dias | Um em cada quatro cartões passa 7 meses parado |
| 2.4 | Resgatar o produto Standard | 25,8% dos Standard nunca são ativados, o dobro do Platinum (9,0%). É o produto de entrada, e é o que mais falha |

Meta: Novas contas por trimestre: 27 → 150 em 6 meses.
Cartões emitidos por cliente novo: 0,14 → 1,50.
Ativação em até 30 dias: 48,7% → 80%.

Tamanho do vazamento atual. 450 cartões emitidos que nunca geraram uma transação (11,2% do
portfólio) e 85 clientes cadastrados sem nenhuma movimentação em 3 anos.

---

### Frente 3 · Destravar o investimento 

Insight que sustenta (Hipótese 8 · confirmada, com as duas explicações rivais descartadas). Os 255
clientes sem renda cadastrada usam cartão (73,3%) e PIX (74,1%) exatamente como os demais, não são
clientes inativos. Mas apenas 5,5% deles investem, contra 58,0% de quem tem renda preenchida. Onze vezes menos.

As duas objeções foram testadas e caem:

- "São clientes novos" → não: a proporção de cadastro incompleto é ~13% em todas as safras, e o
  tempo de casa mediano é idêntico (34 meses)
- "O banco só pede renda quando o cliente vai investir" → não: 74,8% de quem nunca investiu tem a
  renda preenchida, e existem 14 investidores com cadastro incompleto. Não é bloqueio técnico absoluto.

Um campo de cadastro em branco está bloqueando a venda do produto mais estratégico do banco, justamente
o terreno onde o Aurora Bank saiu de 6% para 14% de share.

| # | O que fazer | Detalhe |
|---|---|---|
| 3.1 | Campanha de recadastramento nominal | Lista de 255 clientes, todos já ativos e transacionando. Custo próximo de zero |
| 3.2 | Revisar o fluxo de suitability | Medir onde o cliente abandona o preenchimento. Se 13% param, o formulário é o problema |
| 3.3 | Investimento que vira limite de cartão | Replica o mecanismo com precedente comprovado (Aurora) e amarra os dois produtos |
| 3.4 | Cross-sell sobre os 695 sem investimento | Clientes que usam cartão mas não investem. Penetração total hoje: 51,2% |

Nossa Meta é: Cadastro completo: 87,0% → 97% em 90 dias.
Penetração de investimento: 51,2% → 60% em 12 meses.

Potencial estimado. Se os 255 clientes convertessem à taxa da base (58%), seriam 147 novos
investidores. Ao patrimônio mediano por investidor (R$ 52.122), isso representa ~R$ 7,7 milhões
de captação, ordem de grandeza, não previsão. É a maior relação retorno/esforço de toda a lista.

---

### Frente 4 · Higiene competitiva 

Insight que sustenta (Hipótese 6 · parcialmente confirmada). O PIX é reprovado em 10,07% das tentativas, 
19 vezes a taxa de negativa do cartão do próprio banco (0,53%). E o padrão é rigorosamente
uniforme entre PF/PJ, agendado/não agendado e envio/recebimento, o que descarta saldo insuficiente e
aponta para falha de plataforma. São 28.085 falhas na cara do cliente.

Portanto, consertar o PIX não trará os clientes de volta sozinho. É higiene competitiva contra
um concorrente cuja maturidade digital é "Alta" na tabela do benchmarking, não é a alavanca de
recuperação. Executar em paralelo, sem consumir a prioridade das Frentes 1 a 3.

A Meta segue pra Reprovação de PIX: **10,07% → <2%**.

---

### Frente 5 · Governança de dados

Nada acima é gerenciável sem isto. Notamos que a base tem:

- 7 meses inteiros ausentes na maior base do banco (PIX, jan–jul/2025);
- o valor da compra de cartão distribuído uniformemente entre R$ 0 e R$ 1.200, sorteado, não
  observado. Ticket médio e segmentação por valor são inanalisáveis;
- nenhuma chave primária na base PIX e nenhum `Cliente_ID` na base de cartões;
- 24,9% dos PIX registrados antes de o cliente abrir a conta;
- duas quebras de escala não documentadas.

Portanto é necessário Instituir contrato de dados com checagens automáticas de consistência temporal, chave primária
em toda tabela transacional, e versionamento de extração. Um banco que não consegue medir o próprio
funil não consegue corrigi-lo.

---

## 5. Priorização

| Frente | Ação | Impacto | Esforço | Prazo | Prioridade |
|---|---|---|---|---|---|
| 2 | Destravar a emissão de cartão |  Alto |  Baixo | 30 dias | **1ª** |
| 3 | Recadastramento dos 255 |  Médio |  Baixo | 90 dias | **2ª** |
| 1 | Programa de domicílio de renda |  Alto |  Alto | 12 meses | **3ª** |
| 2 | Abertura de conta digital |  Alto |  Médio | 6 meses | **4ª** |
| 3 | Investimento vira limite |  Alto | Médio | 9 meses | **5ª** |
| 2 | Ativação assistida em 30 dias |  Médio |  Baixo | 90 dias | **6ª** |
| 4 | Investigação técnica do PIX |  Médio |  Médio | 6 meses | **7ª** |
| 5 | Contrato de dados |  Médio |  Médio | contínuo | **paralelo** |

As duas primeiras são alto retorno e baixo esforço. 
A Frente 1 é a que resolve a raiz, mas é a mais cara e a mais lenta.

---

## 6. Roadmap

30 dias, "stop the bleeding"
- Responder por que a emissão de cartão está em zero desde junho de 2025
- Disparar a campanha sobre os 255 clientes com cadastro incompleto
- Instrumentar os 8 KPIs da seção 7 com baseline congelado

90 dias,  quick win
- Cadastro completo em 97%
- Onboarding de ativação de cartão em 30 dias, com resgate do produto Standard
- Piloto de portabilidade de salário em 1 das 6 praças

180 dias, reabrir a entrada
- Abertura de conta 100% digital em produção
- Open Finance ativo
- Meta de 150 novas contas por trimestre

360 dias, principalidade
- Programa de domicílio de renda em escala
- Investimento convertido em limite de cartão
- Meta de 25% dos clientes com crédito recorrente

---

## 7. KPIs — baseline e meta

| # | Indicador | Hoje | Meta 90d | Meta 12m | Frente |
|---|---|---|---|---|---|
| 1 | Clientes com crédito recorrente mensal | **4,3%** | 8% | **25%** | 1 |
| 2 | Razão saída/entrada por PIX | **7,36×** | 6,5× | **4,0×** | 1 |
| 3 | Novas contas por trimestre | **27** | 80 | **150** | 2 |
| 4 | Cartões emitidos por cliente novo | **0,14** | 1,00 | **1,50** | 2 |
| 5 | Cartões ativados em até 30 dias | **48,7%** | 65% | **80%** | 2 |
| 6 | Cadastro completo | **87,0%** | **97%** | 99% | 3 |
| 7 | Penetração de investimento | **51,2%** | 54% | **60%** | 3 |
| 8 | Reprovação de PIX | **10,07%** | 6% | **<2%** | 4 |

Métricas que podem ser adotadas: transações por cliente ativo por trimestre, hoje 7,1, teto histórico 13,7
(2023). Recuperar o patamar de 2023 é o alvo de 24 meses.

---

## 10. Síntese para a banca

O problema. O Priceless Bank perdeu 14 pontos de share em um ano sem perder clientes. A carteira caiu
3%; o uso caiu 48%.

A causa. A conta nunca foi a principal, sem salário, com 7,4× mais saída do que entrada e nenhum
cliente com fluxo positivo. Vínculo fraco esvazia sozinho. E a entrada de novos clientes parou: 27
contas e zero cartões no último trimestre.

A recomendação. Disputar principalidade, não transação. Três frentes em paralelo: trazer a renda
(raiz), reabrir a entrada (urgência), destravar o investimento (quick win de R$ 7,7 mi com custo
próximo de zero).
