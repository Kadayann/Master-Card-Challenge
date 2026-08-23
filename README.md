# Priceless Bank, Mastercard Challenge 2026

Diagnóstico da perda de participação de mercado do Priceless Bank, que caiu de 33% para 19% de
share entre o 1T25 e o 4T25.

## A conclusão em uma frase

> O banco não está perdendo clientes. Ele nunca foi o banco principal deles, e agora parou de
> conquistar novos.

A carteira de clientes ativos caiu apenas 3%; o uso por cliente caiu 48%. Não é churn, é perda
de share-of-wallet. E a aquisição de novos clientes caiu 85%, com zero cartões emitidos desde
junho de 2025.

## Ordem de leitura

| # | Arquivo | O que faz |
|---|---|---|
| 1 | [`1_exploracao_inicial.ipynb`](1_exploracao_inicial.ipynb) | Primeiro olhar sobre as 5 bases: o que existe, quem é o cliente, onde está a queda, e três problemas que condicionam todo o resto |
| 2 | [`2_limpeza_de_dados.ipynb`](2_limpeza_de_dados.ipynb) | Decisões de tratamento, cada uma com o problema, o que foi feito e a alternativa descartada. |
| 3 | [`3_validacao_de_hipoteses.ipynb`](3_validacao_de_hipoteses.ipynb) | 9 hipóteses testadas com veredito explícito. Quatro não sobreviveram , e duas refutações mudaram o alvo da recomendação |
| 4 | [`4_conclusoes_e_recomendacoes.md`](4_conclusoes_e_recomendacoes.md) | Três frentes de ação priorizadas e roadmap |


## Como reproduzir

```bash
pip install pandas numpy matplotlib jupyter
jupyter notebook          # execute os notebooks 1, 2 e 3 nessa ordem
```

Os CSVs de origem estão na raiz do repositório. Não há outras dependências.
