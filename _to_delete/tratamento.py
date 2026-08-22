#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
 TRATAMENTO DAS BASES DO PRICELESS BANK
 Mastercard Challenge 2026 · Inteli
================================================================================

O QUE ESTE SCRIPT FAZ, EM UMA FRASE
-----------------------------------
Pega os 5 CSVs originais, arruma o que dá para arrumar, MARCA o que não dá, e
salva versões tratadas — sem nunca apagar uma linha sequer.

A REGRA DE OURO
---------------
    NENHUMA LINHA É EXCLUÍDA. NUNCA.

Por quê? Porque apagar dado é uma decisão irreversível tomada com informação
incompleta. Se eu apago 69 mil PIX porque "parecem estranhos" e depois descubro
que o estranho era a minha suposição, não tem volta — e ninguém revisando o
trabalho consegue ver o que sumiu.

Em vez de apagar, este script cria colunas que começam com `flag_`. Uma flag é
só um Sim/Não dizendo "olha, essa linha aqui tem tal problema". Quem for
analisar decide se filtra ou não — e a decisão fica visível.

    Errado:  df = df[df.valor > 0]                  # 917 linhas somem, ninguém sabe
    Certo:   df['flag_valor_impossivel'] = df.valor < 0   # 917 linhas marcadas

COMO RODAR
----------
    python tratamento.py

Precisa dos 5 CSVs na mesma pasta. Não precisa de nada além de pandas e numpy.

O QUE SAI DAQUI
---------------
    bases_tratadas/*.csv       as 5 bases arrumadas
    relatorio_qualidade.csv    uma linha por decisão tomada, com o porquê
    TRATAMENTO.md             o mesmo relatório em texto, para ler no GitHub

COMO ESTE ARQUIVO ESTÁ ORGANIZADO
---------------------------------
    ETAPA 1  Padronizar tipos e datas       (arrumar a forma)
    ETAPA 2  Preencher o que não é buraco   (nulo que significa algo)
    ETAPA 3  Marcar o que não tem salvação  (dado corrompido ou inútil)
    ETAPA 4  Criar as colunas que faltam    (o que a base deveria ter e não tem)
    ETAPA 5  Flags de consistência          (o que é logicamente impossível)
    ETAPA 6  Normalizar a escala do PIX     (a régua trocada)
    ETAPA 7  Salvar tudo e explicar

Cada tratamento tem um bloco de comentário assim:

    # ─── O PROBLEMA ───  o que está errado, em português
    # ─── A DECISÃO  ───  o que eu faço
    # ─── POR QUÊ    ───  a razão, sem jargão
    # ─── DESCARTEI  ───  a alternativa que eu NÃO escolhi, e por quê

Esse último campo é o mais importante. Mostrar o que você considerou e
rejeitou é o que separa "tratei os dados" de "tomei decisões defensáveis".
"""

import unicodedata
from pathlib import Path

import numpy as np
import pandas as pd

PASTA   = Path(__file__).resolve().parent
SAIDA   = PASTA / 'bases_tratadas'
SAIDA.mkdir(exist_ok=True)

# Guarda cada decisão tomada, para virar relatório no final.
DECISOES = []
_etapa_atual = {'n': 0, 'nome': ''}


def etapa(n, nome):
    """Marca o início de uma etapa e imprime o cabeçalho."""
    _etapa_atual.update(n=n, nome=nome)
    print(f'\n{"─"*78}\n  ETAPA {n} · {nome}\n{"─"*78}')


def decisao(base, campo, problema, linhas, o_que_faco, por_que, descartei, tipo='Tratamento'):
    """
    Registra UMA decisão de tratamento e imprime na tela em linguagem simples.

    base       qual das 5 bases
    campo      qual coluna
    problema   o que está errado
    linhas     quantas linhas são afetadas
    o_que_faco a ação tomada
    por_que    a justificativa, sem jargão
    descartei  a alternativa rejeitada e o motivo
    tipo       Tratamento | Flag | Coluna nova | Documentação
    """
    DECISOES.append(dict(Etapa=f'{_etapa_atual["n"]}. {_etapa_atual["nome"]}', Base=base, Campo=campo,
                         Tipo=tipo, Problema=problema, Linhas_afetadas=linhas,
                         Decisao=o_que_faco, Por_que=por_que, Alternativa_descartada=descartei))
    marca = {'Tratamento': '·', 'Flag': '!', 'Coluna nova': '+', 'Documentação': 'i'}[tipo]
    pct = f' ({100*linhas/TOTAIS.get(base, linhas or 1):.1f}%)' if linhas else ''
    print(f'  [{marca}] {campo:<26} {linhas:>7,} linhas{pct}'.replace(',', '.'))
    print(f'      → {o_que_faco}')
    print(f'        porque {por_que}')


def sim_nao(serie):
    """Converte a coluna de texto 'Sim'/'Não' em booleano de verdade."""
    return serie.astype(str).str.strip().str.lower().map({'sim': True, 'não': False, 'nao': False})


print(__doc__)

# ══════════════════════════════════════════════════════════════════════════════
#  ETAPA 0 — Carga dos arquivos originais
# ══════════════════════════════════════════════════════════════════════════════
etapa(0, 'Carga dos CSVs originais')

clientes = pd.read_csv(PASTA / 'Base_clientes_v4.csv')
cartoes  = pd.read_csv(PASTA / 'Base_cartoes_v4.csv')
transac  = pd.read_csv(PASTA / 'Base_transacoes_v4.csv')
pix      = pd.read_csv(PASTA / 'Base_pix_v4.csv')
invest   = pd.read_csv(PASTA / 'Base_investimentos_v4.csv')

TOTAIS = {'Clientes': len(clientes), 'Cartões': len(cartoes), 'Transações': len(transac),
          'PIX': len(pix), 'Investimentos': len(invest)}
LINHAS_ANTES = dict(TOTAIS)
for nome, n in TOTAIS.items():
    print(f'  {nome:<15} {n:>8,} linhas'.replace(',', '.'))


# ══════════════════════════════════════════════════════════════════════════════
#  ETAPA 1 — Padronizar tipos e datas
#
#  Nada de decisão difícil aqui. É só arrumar a forma dos dados para que o resto
#  do script consiga trabalhar. Como organizar a bancada antes de cozinhar.
# ══════════════════════════════════════════════════════════════════════════════
etapa(1, 'Padronizar tipos e datas')

# ─── O PROBLEMA ───
#   As cinco bases usam TRÊS formatos de data diferentes:
#       Base_clientes:      04/04/1984   (dia/mês/ano, jeito brasileiro)
#       Base_cartoes:       2023-01-01   (ano-mês-dia, jeito internacional)
#       Base_investimentos: 202407       (ano e mês grudados, é um NÚMERO)
#   Enquanto forem texto ou número, o computador não sabe que 202407 vem depois
#   de 202312. Ele compara como se fossem etiquetas, não como datas.
# ─── A DECISÃO ───
#   Converter tudo para o tipo datetime do pandas.
# ─── POR QUÊ ───
#   Só depois de converter é que "esta data é maior que aquela" passa a fazer
#   sentido. Todas as checagens da ETAPA 5 dependem disso.
# ─── DESCARTEI ───
#   Comparar como texto. Funcionaria por acidente no formato ano-mês-dia e
#   quebraria silenciosamente no formato brasileiro — o pior tipo de bug,
#   porque não dá erro, só dá resposta errada.

clientes['Data_Nascimento']    = pd.to_datetime(clientes.Data_Nascimento, format='%d/%m/%Y', errors='coerce')
clientes['Data_Criacao_Conta'] = pd.to_datetime(clientes.Data_Criacao_Conta, errors='coerce')
cartoes['Data_Emissao']        = pd.to_datetime(cartoes.Data_Emissao,  errors='coerce')
cartoes['Data_Ativacao']       = pd.to_datetime(cartoes.Data_Ativacao, errors='coerce')
cartoes['Data_Validade']       = pd.to_datetime(cartoes.Data_Validade, errors='coerce')
transac['Data']                = pd.to_datetime(transac.Data, errors='coerce')
pix['Data']                    = pd.to_datetime(pix.Data,     errors='coerce')
invest['Data']                 = pd.to_datetime(invest.Data.astype(str),                    format='%Y%m', errors='coerce')
invest['Data_Abertura_Conta_Inv'] = pd.to_datetime(invest.Data_Abertura_Conta_Inv.astype(str), format='%Y%m', errors='coerce')

decisao('Todas', 'colunas de data', 'Três formatos diferentes de data nas cinco bases',
        0, 'Converter tudo para datetime',
        'texto não se compara como data: "04/04/1984" > "28/12/2006" dá True se comparado como letra',
        'Comparar como texto — funcionaria por acidente em uma base e quebraria em silêncio na outra',
        tipo='Tratamento')

# ─── O PROBLEMA ───
#   Colunas de Sim/Não guardadas como texto, e de 0/1 guardadas como número.
#   Texto "Não" é um valor verdadeiro em Python. `if cliente.Possui_Conta:` dá
#   True mesmo quando o valor é a palavra "Não".
# ─── A DECISÃO ───
#   Virar True/False de verdade.
# ─── POR QUÊ ───
#   Além de evitar a armadilha acima, booleano permite fazer `.mean()` e obter
#   direto o percentual. `clientes.Possui_Conta_Adicional.mean()` vira "21,2%".
# ─── DESCARTEI ───
#   Deixar como está e comparar com == 'Sim' toda vez. Funciona, mas basta um
#   acento diferente ou um espaço sobrando em uma linha para quebrar tudo.

clientes['Possui_Conta_Adicional'] = sim_nao(clientes.Possui_Conta_Adicional)
transac['Autorizado']              = sim_nao(transac.Autorizado)
pix['Agendado']                    = sim_nao(pix.Agendado)
pix['Aprovado']                    = pix.Aprovado.astype('boolean')
pix['Pix_para_si_mesmo']           = pix.Pix_para_si_mesmo.astype('boolean')

decisao('Todas', 'Sim/Não e 0/1', 'Booleanos guardados como texto e como número',
        0, 'Converter para True/False',
        'a palavra "Não" é considerada verdadeira pelo Python — é uma armadilha silenciosa',
        'Comparar com == "Sim" em cada uso: quebra com um acento ou espaço a mais')


# ══════════════════════════════════════════════════════════════════════════════
#  ETAPA 2 — Preencher o que não é buraco
#
#  Aqui está a confusão mais comum em tratamento de dados. Célula vazia NÃO é
#  sempre "dado perdido". Às vezes vazio É a informação.
#
#  Analogia: numa ficha de matrícula, o campo "nome do cônjuge" em branco não
#  significa que a pessoa esqueceu de responder. Significa que ela é solteira.
#  Preencher com a média dos cônjuges dos outros seria absurdo.
#
#  Regra que aplico aqui: se o vazio tem significado, eu escrevo o significado.
#  Se o vazio é ausência de verdade, eu deixo vazio.
# ══════════════════════════════════════════════════════════════════════════════
etapa(2, 'Preencher o que não é buraco (vazio que significa algo)')

# ─── O PROBLEMA ───
#   113.252 transações (72% da base) têm Qtd_Parcelas em branco.
# ─── A DECISÃO ───
#   Preencher com 1 e criar a coluna booleana `parcelado`.
# ─── POR QUÊ ───
#   Compra à vista não tem "quantidade de parcelas" para registrar — o sistema
#   deixa em branco. À vista é 1 parcela. Não estou inventando dado: estou
#   escrevendo o que o branco já queria dizer.
#   Prova de que a leitura está certa: entre as compras que TÊM o campo
#   preenchido, os valores vão de 2 a 12, distribuídos por igual. Não existe
#   nenhum "1" na base. Se o branco não fosse "à vista", faltaria o 1.
# ─── DESCARTEI ───
#   Preencher com a média (6,5 parcelas). Criaria 113 mil compras parceladas em
#   seis vezes e meia que nunca existiram, e infetaria toda análise de crédito.

transac['parcelado']    = transac.Qtd_Parcelas.fillna(1) > 1
transac['Qtd_Parcelas'] = transac.Qtd_Parcelas.fillna(1).astype(int)

decisao('Transações', 'Qtd_Parcelas', 'Vazio em 72% das linhas', 113_252,
        'Preencher com 1 e criar a coluna `parcelado`',
        'vazio quer dizer compra à vista — e o número 1 não existe em lugar nenhum da coluna, o que confirma a leitura',
        'Preencher com a média (6,5): inventaria 113 mil parcelamentos que nunca aconteceram')

# ─── O PROBLEMA ───
#   134.716 transações (86%) sem Wallet.
# ─── A DECISÃO ───
#   Preencher com o texto "Sem wallet" e criar a booleana `usou_wallet`.
# ─── POR QUÊ ───
#   Wallet é Apple Pay, Google Pay, Samsung Pay. Quem paga com o cartão físico
#   não usa nenhuma delas — o campo fica vazio porque não houve carteira. O
#   vazio é a resposta "nenhuma", e ela é analiticamente útil: significa que
#   só 14,1% das compras do banco passam por carteira digital.
# ─── DESCARTEI ───
#   Jogar a coluna fora por ter 86% de vazio. Perderia o dado de adoção digital,
#   que é justamente um dos eixos do benchmarking do desafio.

transac['usou_wallet'] = transac.Wallet.notna()
transac['Wallet']      = transac.Wallet.fillna('Sem wallet')

decisao('Transações', 'Wallet', 'Vazio em 86% das linhas', 134_716,
        'Preencher com "Sem wallet" e criar `usou_wallet`',
        'vazio significa que a compra não passou por carteira digital — é resposta, não ausência',
        'Descartar a coluna por excesso de vazio: perderia a métrica de adoção digital, que o desafio pede')

# ─── O PROBLEMA ───
#   450 cartões têm Data_Ativacao = 1900-01-01. Ninguém ativou cartão em 1900.
# ─── A DECISÃO ───
#   Trocar por vazio de verdade (NaT) e criar a flag `ativado`.
# ─── POR QUÊ ───
#   Isso se chama VALOR SENTINELA: o sistema antigo não sabia guardar "vazio",
#   então guardou uma data absurda para significar "não aconteceu". É comum em
#   bases legadas.
#   Se eu deixar 1900 lá, qualquer conta de "tempo até ativar" vai dar mais de
#   45 mil dias e destruir a média.
#   Confirmação de que a leitura está certa: esses 450 cartões são EXATAMENTE
#   os mesmos 450 que estão sem Data_Validade. Cartão não ativado não ganha
#   validade. Duas colunas contando a mesma história.
# ─── DESCARTEI ───
#   Excluir esses 450 cartões. Seriam justamente os mais interessantes: 11,2%
#   do portfólio emitido que nunca gerou um centavo. É achado, não sujeira.

cartoes['ativado']       = cartoes.Data_Ativacao.dt.year > 1900
cartoes['Data_Ativacao'] = cartoes.Data_Ativacao.where(cartoes.ativado)

decisao('Cartões', 'Data_Ativacao', 'Valor sentinela 1900-01-01 usado como "nunca ativado"', 450,
        'Trocar por vazio real e criar a flag `ativado`',
        'a data de 1900 é um código para "não aconteceu"; mantê-la faria a média de dias até a ativação passar de 45 mil dias',
        'Excluir os 450 cartões: são 11,2% do portfólio que nunca foi usado — é o achado, não o lixo')

# ─── O PROBLEMA ───
#   7.864 investimentos têm Data_de_vencimento = 299901, ou seja, ano 2999.
# ─── A DECISÃO ───
#   Trocar por vazio e criar a flag `produto_perpetuo`.
# ─── POR QUÊ ───
#   Mesma ideia do 1900: sentinela para "não vence nunca". E dá para provar:
#   100% dessas linhas são do produto Reservinha, e 0% dos outros três produtos
#   tem esse valor. Reservinha é o produto de liquidez, resgatável a qualquer
#   momento — não tem vencimento mesmo.
# ─── DESCARTEI ───
#   Manter o ano 2999. Um gráfico de "vencimentos por ano" ficaria com uma barra
#   solitária mil anos à direita, esmagando todo o resto do eixo.

invest['produto_perpetuo']    = invest.Data_de_vencimento == 299901
invest['Data_de_vencimento']  = pd.to_datetime(
    invest.Data_de_vencimento.where(~invest.produto_perpetuo).astype('Int64').astype(str),
    format='%Y%m', errors='coerce')

decisao('Investimentos', 'Data_de_vencimento', 'Valor sentinela 299901 (ano 2999)', 7_864,
        'Trocar por vazio e criar a flag `produto_perpetuo`',
        'é o código para "sem vencimento" — e 100% dessas linhas são Reservinha, o produto de liquidez diária',
        'Manter o ano 2999: qualquer gráfico de vencimento ficaria ilegível')

# ─── O PROBLEMA ───
#   14 linhas de investimento sem Valor_Aplicado e sem Saldo_Atual.
# ─── A DECISÃO ───
#   Criar `tipo_evento = 'Vencimento'`, valor 0, e manter a linha.
# ─── POR QUÊ ───
#   Olhei linha por linha: nas 14, a coluna Data é IGUAL à Data_de_vencimento.
#   Não são operações com valor perdido — são marcações de "o produto venceu
#   neste mês". Não tem valor porque nada foi movimentado.
# ─── DESCARTEI ───
#   Apagar as 14 linhas. Perderia a informação de que o produto venceu, que é
#   justamente o momento em que o banco corre risco de o cliente sacar tudo.

venc = invest.Valor_Aplicado.isna() & invest.Saldo_Atual.isna()
invest['tipo_evento']    = np.where(venc, 'Vencimento',
                           np.where(invest.Valor_Aplicado.fillna(0) < 0, 'Resgate', 'Aporte'))
invest['Valor_Aplicado'] = invest.Valor_Aplicado.fillna(0)
invest['Saldo_Atual']    = invest.Saldo_Atual.fillna(0)

decisao('Investimentos', 'Valor_Aplicado / Saldo_Atual', 'Ambos vazios na mesma linha', int(venc.sum()),
        'Marcar como tipo_evento="Vencimento", zerar os valores e manter a linha',
        'nas 14 linhas a data da operação é igual à data de vencimento: é uma marcação de vencimento, não uma operação sem valor',
        'Apagar as 14 linhas: perderia o registro do momento em que o produto vence — que é quando o cliente decide sacar')

# ─── O PROBLEMA ───
#   255 clientes (13%) sem Renda_Anual.
# ─── A DECISÃO ───
#   NÃO preencher. Criar a flag `cadastro_incompleto` e deixar o vazio como está.
# ─── POR QUÊ ───
#   Este é o caso em que o vazio é o próprio achado do trabalho. Esses 255
#   clientes usam cartão (73,3%) e PIX (74,1%) igual a todo mundo, mas só 5,5%
#   deles investem — contra 58% de quem tem renda preenchida. Dez vezes menos.
#   A explicação provável é regulatória: sem renda declarada não há análise de
#   perfil (suitability) e o cliente não fica elegível à oferta de investimento.
#   Se eu preencher com a média, o campo fica bonito e o insight desaparece.
# ─── DESCARTEI ───
#   Imputar pela mediana, ou por um modelo usando idade e cidade. Ambos apagam
#   exatamente a informação que interessa: o fato de estar em branco.

clientes['cadastro_incompleto'] = clientes.Renda_Anual.isna()

decisao('Clientes', 'Renda_Anual', 'Vazio em 13% dos clientes', 255,
        'NÃO preencher. Criar a flag `cadastro_incompleto` e manter o vazio',
        'o vazio é o achado: esses clientes transacionam normalmente mas só 5,5% investem, contra 58% dos demais — o campo em branco parece bloquear a oferta',
        'Imputar pela mediana ou por modelo: deixaria a base bonita e apagaria o insight de maior retorno do trabalho')


# ══════════════════════════════════════════════════════════════════════════════
#  ETAPA 3 — Marcar o que não tem salvação
#
#  Aqui estão os dados que realmente estão quebrados. A tentação é apagar.
#  Não apago: marco. A diferença é que uma linha marcada continua contando
#  para "quantas transações houve" — só não entra nas contas de dinheiro.
# ══════════════════════════════════════════════════════════════════════════════
etapa(3, 'Marcar o que não tem salvação')

# ─── O PROBLEMA ───
#   Crossborder está vazia em 95,6% das linhas. Contactless, em 82,5%.
# ─── A DECISÃO ───
#   Marcar as duas como INUTILIZÁVEIS na documentação e não usar em nenhuma
#   análise. As colunas continuam no arquivo.
# ─── POR QUÊ ───
#   Não é só o volume de vazio — é o que sobra. Nas poucas linhas preenchidas,
#   a divisão é 50/50 em ambas: 3.462 nacionais contra 3.452 internacionais;
#   13.666 sem aproximação contra 13.828 com. Cinquenta por cento é o resultado
#   de jogar uma moeda. Não há sinal nenhum ali dentro.
#   E dói: essas são exatamente as duas colunas que mediriam "maturidade
#   digital" e "internacionalização", que são eixos do benchmarking do desafio.
# ─── DESCARTEI ───
#   Preencher com 0 ("assumir que não foi contactless"). Isso inventaria uma
#   taxa de contactless de 8,8% na base inteira — um número que iria para o
#   slide e que ninguém conseguiria auditar.

decisao('Transações', 'Crossborder', 'Vazio em 95,6%; nos preenchidos, divisão 50/50', 149_912,
        'Declarar inutilizável e não usar em nenhuma análise',
        'metade e metade é o resultado de jogar uma moeda — não há informação para extrair',
        'Preencher com 0: criaria uma taxa de transação internacional falsa e não auditável',
        tipo='Documentação')

decisao('Transações', 'Contactless', 'Vazio em 82,5%; nos preenchidos, divisão 50/50', 129_332,
        'Declarar inutilizável e não usar em nenhuma análise',
        'mesmo caso do Crossborder — e é justamente a coluna que mediria maturidade digital',
        'Preencher com 0: inventaria uma taxa de contactless de 8,8% que iria parar no slide',
        tipo='Documentação')

# ─── O PROBLEMA ───
#   917 PIX com valor negativo, chegando a −R$ 585.848.
# ─── A DECISÃO ───
#   Flag `flag_valor_impossivel`. A linha fica; o valor não entra em soma nenhuma.
# ─── POR QUÊ ───
#   Investiguei se seriam estornos (o espelho negativo de um PIX que aconteceu).
#   Não são, e a prova é de tamanho:
#       maior PIX positivo legítimo da base ......... R$    6.780
#       valor mediano desses negativos (em módulo) .. R$   19.773
#       quantos superam o maior positivo ............ 695 de 917
#   Estorno espelha um valor que existiu. Esses números nunca existiram do lado
#   positivo. É corrupção de dado, não evento de negócio.
#   Somam −R$ 41 milhões. Uma soma de PIX que os inclua fica errada em 41 milhões.
# ─── DESCARTEI ───
#   (a) Apagar as 917 linhas — perderia a contagem de que aquele PIX ocorreu.
#   (b) Usar o valor absoluto — inventaria R$ 41 milhões de movimentação.
#   (c) Winsorizar (cortar no percentil 1) — mascararia o problema em vez de
#       registrá-lo, e um analista futuro não saberia que existiu.

pix['flag_valor_impossivel'] = pix.Valor < 0

decisao('PIX', 'Valor', 'Valores negativos de até −R$ 585.848', int(pix.flag_valor_impossivel.sum()),
        'Marcar com `flag_valor_impossivel`; a linha fica, o valor sai das somas',
        'não são estornos: 695 dos 917 são maiores que o maior PIX positivo da base inteira (R$ 6.780) — é corrupção, e somam −R$ 41 milhões',
        'Usar o valor absoluto (inventaria R$ 41 mi de movimentação) ou winsorizar (esconderia o problema)',
        tipo='Flag')

# ─── O PROBLEMA ───
#   418 linhas de PIX sem Data. E outras 418 sem Tipo_transacao.
# ─── A DECISÃO ───
#   DUAS flags separadas: `flag_sem_data` e `flag_sem_tipo`.
# ─── POR QUÊ SEPARADAS ───
#   Porque descobri uma coisa contraintuitiva ao conferir: a interseção entre os
#   dois grupos é ZERO. Nenhuma linha está sem os dois campos ao mesmo tempo.
#   São 836 linhas distintas, não 418.
#       sem Data ........................ 418
#       sem Tipo_transacao .............. 418
#       sem os dois ..................... 0
#       total de linhas atingidas ....... 836
#   Isso muda o tratamento. Uma linha sem data mas COM tipo ainda serve para
#   contar "quantos envios este cliente fez". Uma linha sem tipo mas COM data
#   ainda serve para contar "quantos PIX houve em março". Se eu juntasse tudo
#   numa flag só, perderia metade da informação em cada caso.
#   Lição geral: nunca assuma que dois campos com o mesmo número de vazios são
#   os mesmos vazios. Confira a interseção.
# ─── DESCARTEI ───
#   (a) Uma flag só para os dois casos — descartaria informação aproveitável.
#   (b) Excluir as 836. São 0,3% da base, o impacto seria mínimo — mas a regra
#       de ouro vale igual para 836 linhas e para 836 mil.

pix['flag_sem_data'] = pix.Data.isna()
pix['flag_sem_tipo'] = pix.Tipo_transacao.isna()

decisao('PIX', 'Data', 'Linhas sem data da transação', int(pix.flag_sem_data.sum()),
        'Marcar com `flag_sem_data`',
        'sem data a linha não entra em análise temporal, mas ainda conta para o total de PIX do cliente',
        'Juntar com as linhas sem tipo numa flag só: a interseção entre os dois grupos é ZERO, então seriam dois problemas diferentes tratados como um',
        tipo='Flag')

decisao('PIX', 'Tipo_transacao', 'Linhas sem indicação de envio ou recebimento', int(pix.flag_sem_tipo.sum()),
        'Marcar com `flag_sem_tipo`',
        'sem saber se é envio ou recebimento a linha não entra no cálculo de fluxo, mas a data está lá e ela ainda conta no volume do mês',
        'Assumir que são envios (88% da base é envio): inventaria direção de dinheiro em 418 transações',
        tipo='Flag')

# ─── O PROBLEMA ───
#   165 transações com Valor_Compra negativo.
# ─── A DECISÃO ───
#   Criar `tipo_evento` com os valores Compra / Estorno. Manter o sinal negativo.
# ─── POR QUÊ ───
#   Aqui, ao contrário do PIX, o negativo faz sentido: são estornos, e todos os
#   165 estão marcados como autorizados. Um estorno é um evento real do negócio
#   — o cliente comprou e o dinheiro voltou. Somam apenas −R$ 132 mil.
#   O que estava errado era estar tudo misturado numa coluna só. Com a nova
#   coluna dá para contar compras e estornos separadamente, e a soma continua
#   dando o valor líquido correto porque o sinal foi preservado.
# ─── DESCARTEI ───
#   Excluir os estornos. A receita ficaria superestimada em R$ 132 mil, porque
#   contaria compras que foram devolvidas.

transac['tipo_evento'] = np.where(transac.Valor_Compra < 0, 'Estorno', 'Compra')

decisao('Transações', 'Valor_Compra', 'Valores negativos misturados com as compras', 165,
        'Criar `tipo_evento` (Compra/Estorno) e preservar o sinal negativo',
        'aqui o negativo é legítimo — são estornos autorizados, um evento real; o erro era não conseguir separá-los',
        'Excluir os estornos: a receita ficaria superestimada em R$ 132 mil de compras devolvidas',
        tipo='Coluna nova')


# ══════════════════════════════════════════════════════════════════════════════
#  ETAPA 4 — Criar as colunas que faltam
#
#  Nada aqui está "errado" nas bases originais. O problema é o que elas não têm.
#  Toda coluna criada aqui é derivada do que já existe — nenhum dado inventado.
# ══════════════════════════════════════════════════════════════════════════════
etapa(4, 'Criar as colunas que faltam')

# ─── O PROBLEMA ───
#   A base de cartões não tem Cliente_ID. Não dá para saber de quem é o cartão.
# ─── A DECISÃO ───
#   Reconstruir o dono pelo caminho indireto: a base de transações liga cartão
#   a cliente. Quem não transacionou nunca fica sem dono, com flag.
# ─── POR QUÊ ───
#   É a única ponte disponível. E ela é segura: verifiquei que nenhum cartão da
#   base aparece com dois clientes diferentes nas transações — a relação é
#   sempre um cartão para um cliente.
#   Sobram 469 cartões órfãos (11,7%), e não é coincidência: 450 deles são os
#   nunca ativados. Cartão que nunca foi usado não deixa rastro em lugar nenhum.
# ─── DESCARTEI ───
#   Deduzir o dono por proximidade de data de emissão com a abertura da conta.
#   Seria chute com cara de método — e chute em coluna de chave primária
#   contamina toda análise que use aquele join.

dono = transac.groupby('ID_Cartao').Cliente_ID.first()
cartoes['Cliente_ID']      = cartoes.ID_Cartao.map(dono).astype('Int64')
cartoes['flag_sem_dono']   = cartoes.Cliente_ID.isna()
cartoes['usado']           = cartoes.ID_Cartao.isin(transac.ID_Cartao)

decisao('Cartões', 'Cliente_ID', 'A base não tem a coluna: impossível saber de quem é o cartão',
        int(cartoes.flag_sem_dono.sum()),
        'Reconstruir via base de transações e marcar os 469 que sobram com `flag_sem_dono`',
        'é a única ponte disponível, e é segura: nenhum cartão aparece com dois clientes diferentes',
        'Deduzir o dono por proximidade de datas: seria chute com aparência de método, numa coluna de chave',
        tipo='Coluna nova')

# ─── O PROBLEMA ───
#   A base PIX não tem chave primária. Nenhuma coluna identifica a transação.
# ─── A DECISÃO ───
#   Criar `id_pix`, um número sequencial.
# ─── POR QUÊ ───
#   Sem identificador não dá para dizer "esta linha aqui" para ninguém. Não dá
#   para auditar, para rastrear uma reclamação de cliente, nem para juntar com
#   outra tabela no futuro. É a coluna mais básica que uma tabela transacional
#   precisa ter, e a maior base do banco (279 mil linhas) não tem.
#   Já aproveito e testo duplicidade: procurei o mesmo cliente com o mesmo valor
#   no mesmo segundo, e não achei nenhum. A base não tem duplicata.
# ─── DESCARTEI ───
#   Montar a chave concatenando cliente + data + valor. Funcionaria hoje, mas
#   quebraria no dia em que dois PIX iguais acontecessem no mesmo instante.

pix.insert(0, 'id_pix', np.arange(1, len(pix) + 1))

decisao('PIX', 'chave primária', 'A base não tem nenhuma coluna identificadora', len(pix),
        'Criar `id_pix` sequencial',
        'sem identificador não há como auditar uma linha, rastrear uma reclamação ou juntar com outra tabela',
        'Concatenar cliente+data+valor: funcionaria hoje e quebraria no primeiro empate',
        tipo='Coluna nova')

# ─── O PROBLEMA ───
#   Saldo_Atual não é o saldo depois da operação. É o saldo ANTES dela.
# ─── A DECISÃO ───
#   Criar `saldo_fechamento = Saldo_Atual + Valor_Aplicado`.
# ─── POR QUÊ ───
#   Descobri isso investigando por que o valor aplicado às vezes é maior que o
#   saldo. Três evidências apontam para a mesma conclusão:
#       73,3% das primeiras operações de cada produto têm saldo zero;
#       o saldo é maior ou igual à soma dos aportes ANTERIORES em 100% das linhas;
#       432 resgates sacam exatamente o valor do saldo exibido, e nenhum saca mais.
#   Sem essa coluna, qualquer conta de patrimônio do cliente sai errada para
#   baixo, e a diferença é grande no começo do histórico.
#   Atenção: Saldo_Atual é por PRODUTO, não da conta toda. O patrimônio do
#   cliente é a soma disso sobre os produtos dele.
# ─── DESCARTEI ───
#   Confiar no dicionário de dados, que descreve o campo como "valor que o
#   produto apresenta na data analisada". A descrição é ambígua e os dados
#   discordam dela.

invest['saldo_fechamento'] = invest.Saldo_Atual + invest.Valor_Aplicado

decisao('Investimentos', 'Saldo_Atual', 'É o saldo ANTES da operação, não depois — o dicionário não diz isso',
        len(invest), 'Criar `saldo_fechamento` = Saldo_Atual + Valor_Aplicado',
        '73,3% das primeiras operações têm saldo zero e 432 resgates sacam exatamente o saldo exibido, sem nenhum sacar mais — só faz sentido se o saldo for o de abertura',
        'Confiar no dicionário de dados: a descrição é ambígua e os dados discordam dela',
        tipo='Coluna nova')

# Colunas de conveniência: idade e tempo de casa, calculadas na data de corte.
DATA_CORTE = pd.Timestamp('2025-12-31')
clientes['idade']         = ((DATA_CORTE - clientes.Data_Nascimento).dt.days / 365.25).round(0)
clientes['meses_de_casa'] = ((DATA_CORTE - clientes.Data_Criacao_Conta).dt.days / 30.44).round(0)

decisao('Clientes', 'idade / meses_de_casa', 'A base traz data de nascimento e de abertura, mas não a idade nem o tempo de relacionamento',
        len(clientes), 'Calcular ambas com data de corte fixa em 31/12/2025',
        'data de corte fixa garante que rodar o script amanhã dá o mesmo resultado de hoje — análise tem que ser reprodutível',
        'Usar a data de hoje: o número mudaria a cada execução e ninguém conseguiria reproduzir o relatório',
        tipo='Coluna nova')


# ══════════════════════════════════════════════════════════════════════════════
#  ETAPA 5 — Flags de consistência
#
#  Esta é a etapa mais valiosa do script, e a que menos "trata" alguma coisa.
#
#  A ideia: existem coisas que simplesmente NÃO PODEM acontecer. Não é opinião,
#  é lógica. Um cartão não pode ser usado antes de ser ativado. Um cliente não
#  pode fazer PIX antes de ter conta. Cada checagem dessas é uma pergunta com
#  resposta óbvia — e quando a base responde "aconteceu 69 mil vezes", isso não
#  é sujeira para varrer: é o diagnóstico.
#
#  Nada é corrigido aqui. Só marcado.
# ══════════════════════════════════════════════════════════════════════════════
etapa(5, 'Flags de consistência (o que é logicamente impossível)')

conta_cliente = clientes.set_index('Cliente_ID').Data_Criacao_Conta
mapa_ativacao = cartoes.set_index('ID_Cartao').Data_Ativacao
mapa_validade = cartoes.set_index('ID_Cartao').Data_Validade
mapa_tipo     = cartoes.set_index('ID_Cartao').Tipo_Cartao

# ─── CHECAGEM 1 · a mais grave ───
#   Pergunta: existe PIX feito antes de o cliente abrir a conta?
#   Resposta: 69.427 vezes, um quarto da base.
#   Isso atinge 1.121 dos 1.430 clientes que usam PIX, com uma antecedência
#   mediana de 292 dias. Em 220 clientes, mais da METADE dos PIX é anterior à
#   própria conta.
#   Não corrijo porque não sei qual das duas datas está errada — a do PIX ou a
#   de abertura. Corrigir seria escolher uma no chute.
#   Leitura honesta: ou o banco tem um problema real de integridade entre
#   sistemas, ou as datas foram geradas de forma independente na montagem da
#   base. As duas hipóteses valem ser ditas; nenhuma pode ser afirmada só com
#   este dado. A formulação segura é: "a base não passa em checagem elementar
#   de consistência temporal".

pix['flag_antes_da_conta'] = pix.Data < pix.Cliente_ID.map(conta_cliente)
n = int(pix.flag_antes_da_conta.sum())
decisao('PIX', 'Data vs abertura da conta', 'PIX registrado antes de o cliente existir no banco', n,
        'Marcar com `flag_antes_da_conta` — sem corrigir nada',
        'atinge 1.121 dos 1.430 clientes, com 292 dias de antecedência mediana; não dá para saber qual das duas datas está errada',
        'Corrigir empurrando a data do PIX para a frente: seria escolher no chute qual sistema mentiu',
        tipo='Flag')

# ─── CHECAGEM 2 ───
#   Pergunta: existe compra feita com cartão que já venceu?
#   Resposta: 2.700 vezes.
#   No mundo real o terminal recusa a transação. Se aparece na base como
#   autorizada, ou a data de validade está errada, ou a da transação está.

transac['flag_cartao_vencido'] = transac.Data > transac.ID_Cartao.map(mapa_validade)
n = int(transac.flag_cartao_vencido.sum())
decisao('Transações', 'Data vs Data_Validade', 'Compra feita com cartão já vencido', n,
        'Marcar com `flag_cartao_vencido`',
        'no mundo real o terminal recusa; se está na base como autorizada, uma das duas datas está errada',
        'Excluir as transações: 1,7% da base sairia sem que se saiba qual data é a culpada',
        tipo='Flag')

# ─── CHECAGEM 3 ───
#   Pergunta: existe compra feita antes de o cartão ser ativado?
#   Resposta: 2.131 vezes.
#   Nota de rodapé importante: emissão sempre vem antes da transação (0 casos de
#   violação). Ou seja, o problema é só entre ativação e uso, o que aponta para
#   o campo Data_Ativacao como o suspeito mais provável.

transac['flag_antes_ativacao'] = transac.Data < transac.ID_Cartao.map(mapa_ativacao)
n = int(transac.flag_antes_ativacao.sum())
decisao('Transações', 'Data vs Data_Ativacao', 'Compra registrada antes de o cartão ser ativado', n,
        'Marcar com `flag_antes_ativacao`',
        'a data de emissão nunca é violada (zero casos), o que isola a Data_Ativacao como campo suspeito',
        'Ajustar a data de ativação para a primeira compra: apagaria a evidência de que o campo é pouco confiável',
        tipo='Flag')

# ─── CHECAGEM 4 ───
#   Pergunta: existe compra parcelada em cartão de DÉBITO?
#   Resposta: 6.852 — 26% de todas as compras feitas em débito.
#   Débito debita na hora. Não existe parcelamento. Ou a compra não era débito,
#   ou o parcelamento não era daquela compra.

eh_debito = transac.ID_Cartao.map(mapa_tipo) == 'Débito'
transac['flag_debito_parcelado'] = eh_debito & transac.parcelado
n = int(transac.flag_debito_parcelado.sum())
decisao('Transações', 'Qtd_Parcelas vs Tipo_Cartao', 'Compra parcelada em cartão de débito', n,
        'Marcar com `flag_debito_parcelado`',
        'débito debita na hora, parcelamento não existe nesse produto — são 26% de todas as compras em débito',
        'Zerar as parcelas nesses casos: mascararia uma inconsistência que atinge um quarto do débito',
        tipo='Flag')

# ─── CHECAGEM 5 ───
#   Pergunta: alguém gastou mais do que o limite do cartão numa única compra?
#   Resposta: 35 vezes, só 0,03%.
#   Aqui foi preciso cuidado: a checagem ingênua acusava 26.166 casos. Quase
#   todos eram cartão de DÉBITO, que tem limite zero na base — e limite zero em
#   débito está correto, porque débito usa saldo, não limite. Depois de tirar o
#   débito da conta, sobram 35. O problema quase não existe.
#   Fica o registro: uma checagem mal formulada teria virado um slide dizendo
#   "17% das compras estouram o limite", o que é falso.

limite = transac.ID_Cartao.map(cartoes.set_index('ID_Cartao').Limite_Cartao)
transac['flag_acima_do_limite'] = (~eh_debito) & (transac.Valor_Compra > limite)
n = int(transac.flag_acima_do_limite.sum())
decisao('Transações', 'Valor_Compra vs Limite_Cartao', 'Compra acima do limite do cartão (só crédito)', n,
        'Marcar com `flag_acima_do_limite`, excluindo débito da checagem',
        'a checagem ingênua acusava 26.166 casos, mas quase todos eram débito com limite zero — que está correto, porque débito usa saldo e não limite',
        'Manter a checagem ingênua: viraria um slide dizendo "17% das compras estouram o limite", o que é falso',
        tipo='Flag')

# ─── CHECAGEM 6 ───
#   Pergunta: existe operação de investimento com vencimento no passado?
#   Resposta: 188.

invest['flag_vencimento_passado'] = (invest.Data_de_vencimento < invest.Data) & ~invest.produto_perpetuo
n = int(invest.flag_vencimento_passado.sum())
decisao('Investimentos', 'Data_de_vencimento vs Data', 'Operação com data de vencimento anterior à própria operação', n,
        'Marcar com `flag_vencimento_passado`',
        'não dá para aplicar dinheiro em um produto que já venceu — mas são 0,9% das linhas e nenhuma métrica do estudo depende delas',
        'Excluir: impacto próximo de zero e a regra de não apagar continua valendo',
        tipo='Flag')

# ─── CHECAGEM 7 ───
#   Cliente cadastrado que nunca fez absolutamente nada em 3 anos.
#   Não é erro. É segmento — e vale saber que existe.

sem_atividade = (~clientes.Cliente_ID.isin(transac.Cliente_ID)
                 & ~clientes.Cliente_ID.isin(pix.Cliente_ID)
                 & ~clientes.Cliente_ID.isin(invest.Cliente_ID))
clientes['flag_sem_atividade'] = sem_atividade
decisao('Clientes', 'atividade', 'Cliente sem nenhuma movimentação em 3 anos', int(sem_atividade.sum()),
        'Marcar com `flag_sem_atividade`',
        'não é erro de dado, é um segmento: 4,3% da base cadastrada nunca usou nada',
        'Tratar como cadastro inválido e remover: são clientes reais, só inativos',
        tipo='Flag')


# ══════════════════════════════════════════════════════════════════════════════
#  ETAPA 6 — Normalizar a escala do PIX
#
#  Este é o único tratamento do script que MUDA valores. Por isso é o mais
#  perigoso, e o que exige mais justificativa.
# ══════════════════════════════════════════════════════════════════════════════
etapa(6, 'Normalizar a escala do PIX')

# ─── O PROBLEMA ───
#   De agosto de 2025 em diante, todos os valores de PIX ficam ~4 vezes maiores.
#   Não é o cliente gastando mais: é a régua que mudou. O PIX típico salta de
#   R$ 155 para R$ 640 de um mês para o outro.
# ─── COMO TESTEI SE PODIA CORRIGIR ───
#   Se alguém multiplicou a coluna por um número, então a razão entre os dois
#   períodos tem que ser a MESMA em toda a distribuição — nas transferências
#   pequenas e nas grandes igualmente.
#       No PIX:        razão entre 4,02 e 4,20 do percentil 5 ao 95. É uma reta.
#       Nas transações: razão entre 1,25 e 3,72. É uma rampa. Não é escala.
#   Segundo teste: a FORMA da distribuição tem que ficar intacta. O coeficiente
#   de variação do PIX vai de 1,108 para 1,107 — igual até a terceira casa.
#   Nas transações vai de 0,835 para 1,068. Mudou.
#   Conclusão: PIX pode ser normalizado; transações não podem.
# ─── A DECISÃO ───
#   Criar `Valor_norm`, dividindo por 4,13 apenas de 2025-08 em diante.
#   A coluna `Valor` original fica intacta ao lado.
# ─── POR QUÊ MANTER AS DUAS ───
#   Porque normalização embute uma premissa, e premissa tem que ser auditável.
#   Quem discordar da minha premissa usa a coluna original.
# ─── A PREMISSA, DITA EM VOZ ALTA ───
#   Estou assumindo que a ESCALA mudou e o COMPORTAMENTO não. Estatisticamente,
#   "multiplicaram a coluna por 4,13" e "todos os clientes passaram a mandar PIX
#   4,13 vezes maiores" são indistinguíveis — as duas coisas preservam a forma.
#   O que decide a favor da primeira é o contexto: a mudança é instantânea,
#   atinge todo mundo igualmente, e acontece exatamente no mês em que a base
#   volta depois de sete meses sem nenhum registro.
# ─── DESCARTEI ───
#   (a) Normalizar as transações também — reprovaram no teste, seria trocar um
#       erro por outro.
#   (b) Substituir a coluna original — quem quiser conferir a premissa não teria
#       como voltar.
#   (c) Não normalizar nada — perderia a única forma de comparar PIX em reais
#       ao longo da série.

CORTE_PIX = pd.Timestamp('2025-08-01')
# Filtro do cálculo: PIX aprovado, com data e com valor ESTRITAMENTE positivo.
# O ">0" importa: 591 linhas têm valor exatamente zero. Incluí-las puxaria a
# mediana e mudaria o fator de 4,1286 para 4,1495 — pequeno, mas é o tipo de
# escolha silenciosa que faz dois relatórios do mesmo time não baterem.
ok = pix.Aprovado.fillna(False) & pix.Data.notna() & (pix.Valor > 0)
antes  = pix.loc[ok & (pix.Data <  CORTE_PIX), 'Valor']
depois = pix.loc[ok & (pix.Data >= CORTE_PIX), 'Valor']
K_PIX  = depois.median() / antes.median()

pix['Valor_norm']       = np.where(pix.Data >= CORTE_PIX, pix.Valor / K_PIX, pix.Valor)
pix['flag_normalizado'] = pix.Data >= CORTE_PIX

print(f'\n  Fator estimado: K = {K_PIX:.4f}')
print(f'  Mediana do envio ANTES da correção  → {antes.median():>8.2f}  vs  {depois.median():>8.2f}')
print(f'  Mediana do envio DEPOIS da correção → {antes.median():>8.2f}  vs  {depois.median()/K_PIX:>8.2f}   (deve bater)')

decisao('PIX', 'Valor', 'A partir de 2025-08 todos os valores ficam ~4,13x maiores (troca de escala)',
        int(pix.flag_normalizado.sum()),
        f'Criar `Valor_norm` dividindo por {K_PIX:.4f} de 2025-08 em diante; manter a coluna original',
        'passou no teste de escala pura: razão constante entre 4,02 e 4,20 em toda a distribuição e forma preservada (CV 1,108 → 1,107)',
        'Normalizar também as transações (reprovaram no teste: razão de 1,25 a 3,72) ou substituir a coluna original (impediria auditar a premissa)')

decisao('Transações', 'Valor_Compra', 'Em 2024 os valores seguem outra distribuição', 0,
        'NÃO normalizar. Valores de cartão seguem incomparáveis entre 2023/2025 e 2024',
        'a razão entre os regimes vai de 1,25 nas compras pequenas a 3,72 nas grandes — não houve multiplicação, mudou a distribuição inteira',
        'Dividir 2024 por um fator médio: as compras pequenas ficariam subestimadas e as grandes superestimadas',
        tipo='Documentação')

decisao('Transações', 'Valor_Compra', 'Em 2023 e 2025 os valores seguem uma distribuição uniforme entre R$ 0 e R$ 1.200',
        0, 'Documentar: o valor da compra NÃO deve ser usado como variável analítica',
        'os quantis caem em cima da diagonal teórica (p25 R$ 305 vs R$ 300; p50 R$ 603 vs R$ 600) e só 0,09% passa de R$ 1.200 — consumo real nunca tem esse formato, o campo parece sorteado',
        'Usar ticket médio e "cliente de alto valor" nas análises: seriam métricas sobre um número aleatório',
        tipo='Documentação')

# ─── Redundância: não é erro, mas vale registrar ───
decisao('Clientes', 'Cidade / Estado', 'As duas colunas são equivalentes: uma cidade por estado', len(clientes),
        'Manter as duas e documentar a redundância',
        'são 6 cidades em 6 estados, relação um para um — a segunda coluna não acrescenta informação nenhuma',
        'Remover uma delas: economizaria espaço e criaria atrito com quem espera a coluna no arquivo',
        tipo='Documentação')

decisao('Transações', 'Input_Mode / Input_Mode_Code', 'As duas colunas são equivalentes', len(transac),
        'Manter as duas e documentar a redundância',
        'cada código corresponde sempre ao mesmo modo de entrada — é a mesma informação em dois formatos',
        'Remover o código numérico: é o formato que os sistemas Mastercard usam de verdade',
        tipo='Documentação')


# ══════════════════════════════════════════════════════════════════════════════
#  ETAPA 7 — Conferir, salvar e explicar
# ══════════════════════════════════════════════════════════════════════════════
etapa(7, 'Conferir, salvar e explicar')

TRATADAS = {'Clientes': clientes, 'Cartões': cartoes, 'Transações': transac,
            'PIX': pix, 'Investimentos': invest}
ARQUIVOS = {'Clientes': 'clientes', 'Cartões': 'cartoes', 'Transações': 'transacoes',
            'PIX': 'pix', 'Investimentos': 'investimentos'}

# ─── A conferência mais importante do script ───
#   A regra de ouro dizia: nenhuma linha é excluída. Aqui eu PROVO isso, em vez
#   de pedir que acreditem. Se qualquer base tiver perdido uma linha sequer, o
#   script para com erro e não salva nada.
print('\n  Conferência — nenhuma linha pode ter sido perdida:')
falhou = False
for nome, df in TRATADAS.items():
    antes_, depois_ = LINHAS_ANTES[nome], len(df)
    ok_ = antes_ == depois_
    falhou |= not ok_
    print(f'    {"OK " if ok_ else "ERRO"}  {nome:<15} {antes_:>8,} → {depois_:>8,}'.replace(',', '.'))
assert not falhou, 'ABORTADO: alguma base perdeu linhas. Isso viola a regra de ouro do script.'

# ─── Quantas linhas ficaram marcadas com alguma flag ───
print('\n  Linhas marcadas por flag (continuam na base, só sinalizadas):')
resumo_flags = []
for nome, df in TRATADAS.items():
    flags = [c for c in df.columns if c.startswith('flag_')]
    for f in flags:
        q = int(df[f].fillna(False).sum())
        resumo_flags.append(dict(Base=nome, Flag=f, Linhas=q, Pct=round(100*q/len(df), 2)))
        print(f'    {nome:<15} {f:<26} {q:>7,}  ({100*q/len(df):>5.2f}%)'.replace(',', '.'))

# ─── Salvar as bases tratadas ───
print('\n  Gravando bases tratadas:')
for nome, df in TRATADAS.items():
    caminho = SAIDA / f'{ARQUIVOS[nome]}_tratado.csv'
    df.to_csv(caminho, index=False, encoding='utf-8-sig')
    print(f'    {caminho.name:<32} {len(df):>8,} linhas × {df.shape[1]:>2} colunas'.replace(',', '.'))

# ─── Relatório de qualidade, em CSV ───
relatorio = pd.DataFrame(DECISOES)
relatorio.to_csv(PASTA / 'relatorio_qualidade.csv', index=False, encoding='utf-8-sig')
pd.DataFrame(resumo_flags).to_csv(PASTA / 'relatorio_flags.csv', index=False, encoding='utf-8-sig')

# ─── Relatório em texto, para ler no GitHub ───
#   Gerado a partir da MESMA lista de decisões que o script executou. Assim o
#   documento nunca fica desatualizado em relação ao código.
linhas_md = [
    '# Tratamento das bases — Priceless Bank',
    '',
    'Documento gerado automaticamente por `tratamento.py`. Cada linha aqui corresponde a uma',
    'decisão que o script realmente executou — o texto não pode ficar desatualizado em relação',
    'ao código porque os dois saem da mesma fonte.',
    '',
    '## A regra que orienta tudo',
    '',
    '> **Nenhuma linha é excluída.** O que não pode ser corrigido é marcado com uma coluna `flag_*`,',
    '> e quem for analisar decide se filtra. Apagar dado é irreversível e invisível; marcar é',
    '> reversível e auditável.',
    '',
    'O script confere isso no final: se qualquer base perder uma linha, ele aborta sem salvar.',
    '',
    '## Resumo',
    '',
    f'- **{len(relatorio)} decisões** registradas',
    f'- **{int((relatorio.Tipo == "Flag").sum())} flags** de inconsistência criadas',
    f'- **{int((relatorio.Tipo == "Coluna nova").sum())} colunas novas** derivadas',
    f'- **{int((relatorio.Tipo == "Tratamento").sum())} tratamentos** aplicados',
    f'- **{int((relatorio.Tipo == "Documentação").sum())} pontos** apenas documentados, sem alterar dado',
    '- **0 linhas excluídas**',
    '',
]
for etapa_nome, bloco in relatorio.groupby('Etapa', sort=False):
    linhas_md += [f'## Etapa {etapa_nome}', '']
    for _, r in bloco.iterrows():
        qtd = f'{r.Linhas_afetadas:,}'.replace(',', '.') if r.Linhas_afetadas else '—'
        linhas_md += [
            f'### `{r.Campo}` · {r.Base}',
            '',
            f'**O problema.** {r.Problema}. Linhas afetadas: **{qtd}**.',
            '',
            f'**O que eu faço.** {r.Decisao}.',
            '',
            f'**Por quê.** Porque {r.Por_que}.',
            '',
            f'**O que eu descartei.** {r.Alternativa_descartada}.',
            '',
        ]
linhas_md += [
    '## Como usar as bases tratadas',
    '',
    '```python',
    'import pandas as pd',
    '',
    "clientes = pd.read_csv('bases_tratadas/clientes_tratado.csv')",
    "pix      = pd.read_csv('bases_tratadas/pix_tratado.csv')",
    '',
    '# Somar valores de PIX: use a coluna normalizada e tire os valores corrompidos',
    'validos = pix[~pix.flag_valor_impossivel & ~pix.flag_sem_data]',
    'total   = validos.Valor_norm.sum()',
    '',
    '# Quer conferir a premissa da normalização? A coluna original continua lá:',
    'total_sem_normalizar = validos.Valor.sum()',
    '```',
    '',
    '**Uma advertência que vale repetir:** não use `Valor_Compra` como variável analítica.',
    'Em 2023 e 2025 ela segue uma distribuição uniforme entre R$ 0 e R$ 1.200, o que indica',
    'que o campo foi sorteado e não observado. Use contagem de transações.',
    '',
]
(PASTA / 'TRATAMENTO.md').write_text('\n'.join(linhas_md), encoding='utf-8')

print(f'\n    relatorio_qualidade.csv          {len(relatorio)} decisões registradas')
print(f'    relatorio_flags.csv              {len(resumo_flags)} flags')
print(f'    TRATAMENTO.md                    documento explicativo')

print(f'\n{"═"*78}')
print('  PRONTO'.center(78))
print(f'{"═"*78}')
print(f'  {len(relatorio)} decisões · {int((relatorio.Tipo=="Flag").sum())} flags · '
      f'{int((relatorio.Tipo=="Coluna nova").sum())} colunas novas · 0 linhas excluídas')
print(f'{"═"*78}\n')
