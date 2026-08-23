# Tratamento das bases — Priceless Bank

Documento gerado automaticamente por `tratamento.py`. Cada linha aqui corresponde a uma
decisão que o script realmente executou — o texto não pode ficar desatualizado em relação
ao código porque os dois saem da mesma fonte.

## A regra que orienta tudo

> **Nenhuma linha é excluída.** O que não pode ser corrigido é marcado com uma coluna `flag_*`,
> e quem for analisar decide se filtra. Apagar dado é irreversível e invisível; marcar é
> reversível e auditável.

O script confere isso no final: se qualquer base perder uma linha, ele aborta sem salvar.

## Resumo

- **30 decisões** registradas
- **10 flags** de inconsistência criadas
- **5 colunas novas** derivadas
- **9 tratamentos** aplicados
- **6 pontos** apenas documentados, sem alterar dado
- **0 linhas excluídas**

## Etapa 1. Padronizar tipos e datas

### `colunas de data` · Todas

**O problema.** Três formatos diferentes de data nas cinco bases. Linhas afetadas: **—**.

**O que eu faço.** Converter tudo para datetime.

**Por quê.** Porque texto não se compara como data: "04/04/1984" > "28/12/2006" dá True se comparado como letra.

**O que eu descartei.** Comparar como texto — funcionaria por acidente em uma base e quebraria em silêncio na outra.

### `Sim/Não e 0/1` · Todas

**O problema.** Booleanos guardados como texto e como número. Linhas afetadas: **—**.

**O que eu faço.** Converter para True/False.

**Por quê.** Porque a palavra "Não" é considerada verdadeira pelo Python — é uma armadilha silenciosa.

**O que eu descartei.** Comparar com == "Sim" em cada uso: quebra com um acento ou espaço a mais.

## Etapa 2. Preencher o que não é buraco (vazio que significa algo)

### `Qtd_Parcelas` · Transações

**O problema.** Vazio em 72% das linhas. Linhas afetadas: **113.252**.

**O que eu faço.** Preencher com 1 e criar a coluna `parcelado`.

**Por quê.** Porque vazio quer dizer compra à vista — e o número 1 não existe em lugar nenhum da coluna, o que confirma a leitura.

**O que eu descartei.** Preencher com a média (6,5): inventaria 113 mil parcelamentos que nunca aconteceram.

### `Wallet` · Transações

**O problema.** Vazio em 86% das linhas. Linhas afetadas: **134.716**.

**O que eu faço.** Preencher com "Sem wallet" e criar `usou_wallet`.

**Por quê.** Porque vazio significa que a compra não passou por carteira digital — é resposta, não ausência.

**O que eu descartei.** Descartar a coluna por excesso de vazio: perderia a métrica de adoção digital, que o desafio pede.

### `Data_Ativacao` · Cartões

**O problema.** Valor sentinela 1900-01-01 usado como "nunca ativado". Linhas afetadas: **450**.

**O que eu faço.** Trocar por vazio real e criar a flag `ativado`.

**Por quê.** Porque a data de 1900 é um código para "não aconteceu"; mantê-la faria a média de dias até a ativação passar de 45 mil dias.

**O que eu descartei.** Excluir os 450 cartões: são 11,2% do portfólio que nunca foi usado — é o achado, não o lixo.

### `Data_de_vencimento` · Investimentos

**O problema.** Valor sentinela 299901 (ano 2999). Linhas afetadas: **7.864**.

**O que eu faço.** Trocar por vazio e criar a flag `produto_perpetuo`.

**Por quê.** Porque é o código para "sem vencimento" — e 100% dessas linhas são Reservinha, o produto de liquidez diária.

**O que eu descartei.** Manter o ano 2999: qualquer gráfico de vencimento ficaria ilegível.

### `Valor_Aplicado / Saldo_Atual` · Investimentos

**O problema.** Ambos vazios na mesma linha. Linhas afetadas: **14**.

**O que eu faço.** Marcar como tipo_evento="Vencimento", zerar os valores e manter a linha.

**Por quê.** Porque nas 14 linhas a data da operação é igual à data de vencimento: é uma marcação de vencimento, não uma operação sem valor.

**O que eu descartei.** Apagar as 14 linhas: perderia o registro do momento em que o produto vence — que é quando o cliente decide sacar.

### `Renda_Anual` · Clientes

**O problema.** Vazio em 13% dos clientes. Linhas afetadas: **255**.

**O que eu faço.** NÃO preencher. Criar a flag `cadastro_incompleto` e manter o vazio.

**Por quê.** Porque o vazio é o achado: esses clientes transacionam normalmente mas só 5,5% investem, contra 58% dos demais — o campo em branco parece bloquear a oferta.

**O que eu descartei.** Imputar pela mediana ou por modelo: deixaria a base bonita e apagaria o insight de maior retorno do trabalho.

## Etapa 3. Marcar o que não tem salvação

### `Crossborder` · Transações

**O problema.** Vazio em 95,6%; nos preenchidos, divisão 50/50. Linhas afetadas: **149.912**.

**O que eu faço.** Declarar inutilizável e não usar em nenhuma análise.

**Por quê.** Porque metade e metade é o resultado de jogar uma moeda — não há informação para extrair.

**O que eu descartei.** Preencher com 0: criaria uma taxa de transação internacional falsa e não auditável.

### `Contactless` · Transações

**O problema.** Vazio em 82,5%; nos preenchidos, divisão 50/50. Linhas afetadas: **129.332**.

**O que eu faço.** Declarar inutilizável e não usar em nenhuma análise.

**Por quê.** Porque mesmo caso do Crossborder — e é justamente a coluna que mediria maturidade digital.

**O que eu descartei.** Preencher com 0: inventaria uma taxa de contactless de 8,8% que iria parar no slide.

### `Valor` · PIX

**O problema.** Valores negativos de até −R$ 585.848. Linhas afetadas: **917**.

**O que eu faço.** Marcar com `flag_valor_impossivel`; a linha fica, o valor sai das somas.

**Por quê.** Porque não são estornos: 695 dos 917 são maiores que o maior PIX positivo da base inteira (R$ 6.780) — é corrupção, e somam −R$ 41 milhões.

**O que eu descartei.** Usar o valor absoluto (inventaria R$ 41 mi de movimentação) ou winsorizar (esconderia o problema).

### `Data` · PIX

**O problema.** Linhas sem data da transação. Linhas afetadas: **418**.

**O que eu faço.** Marcar com `flag_sem_data`.

**Por quê.** Porque sem data a linha não entra em análise temporal, mas ainda conta para o total de PIX do cliente.

**O que eu descartei.** Juntar com as linhas sem tipo numa flag só: a interseção entre os dois grupos é ZERO, então seriam dois problemas diferentes tratados como um.

### `Tipo_transacao` · PIX

**O problema.** Linhas sem indicação de envio ou recebimento. Linhas afetadas: **418**.

**O que eu faço.** Marcar com `flag_sem_tipo`.

**Por quê.** Porque sem saber se é envio ou recebimento a linha não entra no cálculo de fluxo, mas a data está lá e ela ainda conta no volume do mês.

**O que eu descartei.** Assumir que são envios (88% da base é envio): inventaria direção de dinheiro em 418 transações.

### `Valor_Compra` · Transações

**O problema.** Valores negativos misturados com as compras. Linhas afetadas: **165**.

**O que eu faço.** Criar `tipo_evento` (Compra/Estorno) e preservar o sinal negativo.

**Por quê.** Porque aqui o negativo é legítimo — são estornos autorizados, um evento real; o erro era não conseguir separá-los.

**O que eu descartei.** Excluir os estornos: a receita ficaria superestimada em R$ 132 mil de compras devolvidas.

## Etapa 4. Criar as colunas que faltam

### `Cliente_ID` · Cartões

**O problema.** A base não tem a coluna: impossível saber de quem é o cartão. Linhas afetadas: **469**.

**O que eu faço.** Reconstruir via base de transações e marcar os 469 que sobram com `flag_sem_dono`.

**Por quê.** Porque é a única ponte disponível, e é segura: nenhum cartão aparece com dois clientes diferentes.

**O que eu descartei.** Deduzir o dono por proximidade de datas: seria chute com aparência de método, numa coluna de chave.

### `chave primária` · PIX

**O problema.** A base não tem nenhuma coluna identificadora. Linhas afetadas: **278.940**.

**O que eu faço.** Criar `id_pix` sequencial.

**Por quê.** Porque sem identificador não há como auditar uma linha, rastrear uma reclamação ou juntar com outra tabela.

**O que eu descartei.** Concatenar cliente+data+valor: funcionaria hoje e quebraria no primeiro empate.

### `Saldo_Atual` · Investimentos

**O problema.** É o saldo ANTES da operação, não depois — o dicionário não diz isso. Linhas afetadas: **21.200**.

**O que eu faço.** Criar `saldo_fechamento` = Saldo_Atual + Valor_Aplicado.

**Por quê.** Porque 73,3% das primeiras operações têm saldo zero e 432 resgates sacam exatamente o saldo exibido, sem nenhum sacar mais — só faz sentido se o saldo for o de abertura.

**O que eu descartei.** Confiar no dicionário de dados: a descrição é ambígua e os dados discordam dela.

### `idade / meses_de_casa` · Clientes

**O problema.** A base traz data de nascimento e de abertura, mas não a idade nem o tempo de relacionamento. Linhas afetadas: **1.960**.

**O que eu faço.** Calcular ambas com data de corte fixa em 31/12/2025.

**Por quê.** Porque data de corte fixa garante que rodar o script amanhã dá o mesmo resultado de hoje — análise tem que ser reprodutível.

**O que eu descartei.** Usar a data de hoje: o número mudaria a cada execução e ninguém conseguiria reproduzir o relatório.

## Etapa 5. Flags de consistência (o que é logicamente impossível)

### `Data vs abertura da conta` · PIX

**O problema.** PIX registrado antes de o cliente existir no banco. Linhas afetadas: **69.427**.

**O que eu faço.** Marcar com `flag_antes_da_conta` — sem corrigir nada.

**Por quê.** Porque atinge 1.121 dos 1.430 clientes, com 292 dias de antecedência mediana; não dá para saber qual das duas datas está errada.

**O que eu descartei.** Corrigir empurrando a data do PIX para a frente: seria escolher no chute qual sistema mentiu.

### `Data vs Data_Validade` · Transações

**O problema.** Compra feita com cartão já vencido. Linhas afetadas: **2.700**.

**O que eu faço.** Marcar com `flag_cartao_vencido`.

**Por quê.** Porque no mundo real o terminal recusa; se está na base como autorizada, uma das duas datas está errada.

**O que eu descartei.** Excluir as transações: 1,7% da base sairia sem que se saiba qual data é a culpada.

### `Data vs Data_Ativacao` · Transações

**O problema.** Compra registrada antes de o cartão ser ativado. Linhas afetadas: **2.131**.

**O que eu faço.** Marcar com `flag_antes_ativacao`.

**Por quê.** Porque a data de emissão nunca é violada (zero casos), o que isola a Data_Ativacao como campo suspeito.

**O que eu descartei.** Ajustar a data de ativação para a primeira compra: apagaria a evidência de que o campo é pouco confiável.

### `Qtd_Parcelas vs Tipo_Cartao` · Transações

**O problema.** Compra parcelada em cartão de débito. Linhas afetadas: **6.852**.

**O que eu faço.** Marcar com `flag_debito_parcelado`.

**Por quê.** Porque débito debita na hora, parcelamento não existe nesse produto — são 26% de todas as compras em débito.

**O que eu descartei.** Zerar as parcelas nesses casos: mascararia uma inconsistência que atinge um quarto do débito.

### `Valor_Compra vs Limite_Cartao` · Transações

**O problema.** Compra acima do limite do cartão (só crédito). Linhas afetadas: **35**.

**O que eu faço.** Marcar com `flag_acima_do_limite`, excluindo débito da checagem.

**Por quê.** Porque a checagem ingênua acusava 26.166 casos, mas quase todos eram débito com limite zero — que está correto, porque débito usa saldo e não limite.

**O que eu descartei.** Manter a checagem ingênua: viraria um slide dizendo "17% das compras estouram o limite", o que é falso.

### `Data_de_vencimento vs Data` · Investimentos

**O problema.** Operação com data de vencimento anterior à própria operação. Linhas afetadas: **188**.

**O que eu faço.** Marcar com `flag_vencimento_passado`.

**Por quê.** Porque não dá para aplicar dinheiro em um produto que já venceu — mas são 0,9% das linhas e nenhuma métrica do estudo depende delas.

**O que eu descartei.** Excluir: impacto próximo de zero e a regra de não apagar continua valendo.

### `atividade` · Clientes

**O problema.** Cliente sem nenhuma movimentação em 3 anos. Linhas afetadas: **85**.

**O que eu faço.** Marcar com `flag_sem_atividade`.

**Por quê.** Porque não é erro de dado, é um segmento: 4,3% da base cadastrada nunca usou nada.

**O que eu descartei.** Tratar como cadastro inválido e remover: são clientes reais, só inativos.

## Etapa 6. Normalizar a escala do PIX

### `Valor` · PIX

**O problema.** A partir de 2025-08 todos os valores ficam ~4,13x maiores (troca de escala). Linhas afetadas: **63.707**.

**O que eu faço.** Criar `Valor_norm` dividindo por 4.1286 de 2025-08 em diante; manter a coluna original.

**Por quê.** Porque passou no teste de escala pura: razão constante entre 4,02 e 4,20 em toda a distribuição e forma preservada (CV 1,108 → 1,107).

**O que eu descartei.** Normalizar também as transações (reprovaram no teste: razão de 1,25 a 3,72) ou substituir a coluna original (impediria auditar a premissa).

### `Valor_Compra` · Transações

**O problema.** Em 2024 os valores seguem outra distribuição. Linhas afetadas: **—**.

**O que eu faço.** NÃO normalizar. Valores de cartão seguem incomparáveis entre 2023/2025 e 2024.

**Por quê.** Porque a razão entre os regimes vai de 1,25 nas compras pequenas a 3,72 nas grandes — não houve multiplicação, mudou a distribuição inteira.

**O que eu descartei.** Dividir 2024 por um fator médio: as compras pequenas ficariam subestimadas e as grandes superestimadas.

### `Valor_Compra` · Transações

**O problema.** Em 2023 e 2025 os valores seguem uma distribuição uniforme entre R$ 0 e R$ 1.200. Linhas afetadas: **—**.

**O que eu faço.** Documentar: o valor da compra NÃO deve ser usado como variável analítica.

**Por quê.** Porque os quantis caem em cima da diagonal teórica (p25 R$ 305 vs R$ 300; p50 R$ 603 vs R$ 600) e só 0,09% passa de R$ 1.200 — consumo real nunca tem esse formato, o campo parece sorteado.

**O que eu descartei.** Usar ticket médio e "cliente de alto valor" nas análises: seriam métricas sobre um número aleatório.

### `Cidade / Estado` · Clientes

**O problema.** As duas colunas são equivalentes: uma cidade por estado. Linhas afetadas: **1.960**.

**O que eu faço.** Manter as duas e documentar a redundância.

**Por quê.** Porque são 6 cidades em 6 estados, relação um para um — a segunda coluna não acrescenta informação nenhuma.

**O que eu descartei.** Remover uma delas: economizaria espaço e criaria atrito com quem espera a coluna no arquivo.

### `Input_Mode / Input_Mode_Code` · Transações

**O problema.** As duas colunas são equivalentes. Linhas afetadas: **156.826**.

**O que eu faço.** Manter as duas e documentar a redundância.

**Por quê.** Porque cada código corresponde sempre ao mesmo modo de entrada — é a mesma informação em dois formatos.

**O que eu descartei.** Remover o código numérico: é o formato que os sistemas Mastercard usam de verdade.

## Como usar as bases tratadas

```python
import pandas as pd

clientes = pd.read_csv('bases_tratadas/clientes_tratado.csv')
pix      = pd.read_csv('bases_tratadas/pix_tratado.csv')

# Somar valores de PIX: use a coluna normalizada e tire os valores corrompidos
validos = pix[~pix.flag_valor_impossivel & ~pix.flag_sem_data]
total   = validos.Valor_norm.sum()

# Quer conferir a premissa da normalização? A coluna original continua lá:
total_sem_normalizar = validos.Valor.sum()
```

**Uma advertência que vale repetir:** não use `Valor_Compra` como variável analítica.
Em 2023 e 2025 ela segue uma distribuição uniforme entre R$ 0 e R$ 1.200, o que indica
que o campo foi sorteado e não observado. Use contagem de transações.
