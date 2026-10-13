# Modelo de dados do painel demonstrativo para contabilidade

Documentação técnica da demonstração publicada em `demo-contabilidade.html`. O escritório Pereira Lins Contabilidade e as 40 empresas clientes são fictícios; todos os registros foram gerados por `gerar_dados.py`, com semente fixa. Este material descreve o modelo dimensional, a definição de cada indicador e um esboço dos modelos dbt para PostgreSQL que sustentam um painel desse tipo em um projeto real.

## Decisões de identidade visual

1. Mesma paleta, tipografia e estrutura de telas do painel de advocacia, para que as demonstrações formem um conjunto. O código comum fica em `demo/core` e é embutido em cada página por `demo/build_demos.py`.
2. Séries negativas, como saídas de caixa e itens que reduzem o caixa na ponte, usam hachura além da cor, para não depender só do vermelho.
3. A identificação das empresas é genérica (segmento e número) de propósito, para não sugerir cliente real.

## Escopo dos dados sintéticos

| Item | Valor |
|---|---|
| Data de referência | 30/09/2026 |
| Histórico | 24 meses, de out/2024 a set/2026, mais 4 meses de aquecimento usados só para as defasagens de caixa |
| Empresas | 40: 13 de comércio, 12 de serviços, 6 indústrias, 9 de alimentação |
| Regimes | Simples Nacional, Lucro Presumido e Lucro Real |
| DRE | 10 linhas por empresa e mês, por competência |
| Caixa | 8 linhas por empresa e mês, realizadas, com defasagens de recebimento, pagamento, folha, 13º salário e impostos |
| Conciliação | linhas de extrato por regra, conciliações manuais e exceções por motivo, por empresa e mês |
| Pendências | fila individual de exceções abertas na data de referência |

## Diagrama entidade-relacionamento

```
dim_empresa (empresa_id PK, nome, segmento, regime_tributario)
dim_mes (mes_id PK, ano, mes, inicio, fim)
dim_conta_gerencial (conta_gerencial_id PK, linha_dre, ordem, sinal)
map_conta (empresa_id FK, conta_contabil, conta_gerencial_id FK)     -- de-para por cliente
dim_regra_conciliacao (regra_id PK, nome)                             -- valor e data, chave da nota, recorrência
dim_motivo_excecao (motivo_id PK, nome)

fct_resultado_mensal (empresa_id FK, mes_id FK, conta_gerencial_id FK, valor)
          grão: empresa x mês x linha da DRE gerencial, por competência
fct_caixa_mensal (empresa_id FK, mes_id FK, categoria_caixa, valor)
          grão: empresa x mês x categoria de caixa realizado
fct_extrato (lancamento_extrato_id PK, empresa_id FK, data, descricao, valor,
             status, regra_id FK NULL, motivo_id FK NULL, conciliado_em NULL)
          grão: linha de extrato bancário
fct_entrega_documentos (empresa_id FK, mes_id FK, data_prevista, data_entrega, dias_atraso)
```

A chave que reconcilia as telas é a empresa: DRE, caixa, conciliação e pendências são somadas pelo mesmo conjunto de empresas para qualquer combinação de filtros.

## Definição dos indicadores

| Indicador | Regra |
|---|---|
| Faturamento bruto | soma da receita bruta por competência no período |
| Margem bruta | (receita líquida menos custo) dividido pela receita líquida |
| Margem líquida | resultado líquido dividido pela receita líquida |
| Variação da margem | margem do período menos a margem do período anterior de mesma duração, em pontos percentuais |
| Tendência da margem bruta | margem dos 3 últimos meses do período menos a dos 3 meses anteriores; alerta abaixo de -3 p.p. |
| Caixa das operações | recebimentos menos pagamentos a fornecedores, impostos, folha, demais despesas, mais resultado financeiro |
| Variação do caixa | caixa das operações mais investimentos e empréstimos |
| Ponte do resultado ao caixa | resultado líquido, mais depreciação, mais a diferença entre caixa e competência de cada grupo: clientes, fornecedores e estoque, impostos, folha e provisões, demais despesas; fecha exatamente no caixa das operações |
| Conciliação automática | linhas conciliadas por regra divididas pelo total de linhas de extrato do período |
| Horas de conferência evitadas | linhas conciliadas por regra vezes a premissa de 1,5 minuto por linha; a premissa é medida no Raio-X |
| Pendências abertas | exceções sem conciliação na data de referência; não dependem do filtro de período |
| RBT12 | receita bruta acumulada nos 12 meses até a data de referência |
| Perto da faixa | RBT12 a menos de 10% do limite da faixa seguinte do Simples Nacional |
| Atraso | dias além do prazo combinado para entrega dos documentos do último mês |

Regras de reconciliação verificadas por script: total da DRE igual à soma por empresa; ponte fechando no caixa das operações e na variação do caixa; saldo final igual a saldo inicial mais a soma das variações; pendências por motivo somando o total da fila.

## Esboço dos modelos dbt (PostgreSQL)

```
models/
  staging/
    erp/        stg_erp__lancamentos.sql, stg_erp__plano_contas.sql
    bancos/     stg_bancos__extrato_ofx.sql
    fiscal/     stg_fiscal__nfe.sql, stg_fiscal__nfse.sql
    escritorio/ stg_escritorio__de_para_contas.sql, stg_escritorio__entregas.sql, stg_escritorio__recorrencias.sql
  intermediate/
    int_lancamentos_gerenciais.sql
    int_conciliacao_candidatos.sql
    int_conciliacao_resultado.sql
    int_ponte_caixa_competencia.sql
  marts/
    fct_resultado_mensal.sql, fct_caixa_mensal.sql, fct_extrato.sql
    mart_carteira_empresa_mes.sql
```

### Staging do extrato

```sql
-- models/staging/bancos/stg_bancos__extrato_ofx.sql
select
    {{ dbt_utils.generate_surrogate_key(['empresa_id', 'conta_id', 'fitid']) }} as lancamento_extrato_id,
    cast(empresa_id as bigint)                  as empresa_id,
    cast(conta_id as bigint)                    as conta_id,
    cast(dtposted as date)                      as data,
    upper(trim(memo))                           as descricao,
    cast(trnamt as numeric(14, 2))              as valor,
    nullif(trim(checknum), '')                  as documento
from {{ source('bancos', 'extrato_ofx') }}
```

### Conciliação por regras

```sql
-- models/intermediate/int_conciliacao_candidatos.sql
-- três regras em ordem de confiança; cada linha de extrato fica com a primeira regra que casar
with extrato as (select * from {{ ref('stg_bancos__extrato_ofx') }}),
notas as (
    select empresa_id, chave_acesso, data_emissao, valor_total, documento_cliente
    from {{ ref('stg_fiscal__nfe') }}
    union all
    select empresa_id, chave_acesso, data_emissao, valor_total, documento_cliente
    from {{ ref('stg_fiscal__nfse') }}
),
lanc as (select * from {{ ref('int_lancamentos_gerenciais') }}),
por_chave as (
    select e.lancamento_extrato_id, 2 as regra_id, 1 as prioridade
    from extrato e
    join notas n on n.empresa_id = e.empresa_id
                and e.descricao like '%' || right(n.chave_acesso, 9) || '%'
),
por_valor_data as (
    select e.lancamento_extrato_id, 1 as regra_id, 2 as prioridade
    from extrato e
    join lanc l on l.empresa_id = e.empresa_id
               and l.valor = e.valor
               and l.data between e.data - 3 and e.data + 3
),
por_recorrencia as (
    select e.lancamento_extrato_id, 3 as regra_id, 3 as prioridade
    from extrato e
    join {{ ref('stg_escritorio__recorrencias') }} r
      on r.empresa_id = e.empresa_id and e.descricao ilike r.padrao_descricao
     and abs(e.valor - r.valor_esperado) <= r.tolerancia
)
select distinct on (lancamento_extrato_id) lancamento_extrato_id, regra_id
from (select * from por_chave union all select * from por_valor_data union all select * from por_recorrencia) c
order by lancamento_extrato_id, prioridade
```

```sql
-- models/intermediate/int_conciliacao_resultado.sql
-- linhas sem regra viram exceção com motivo provável
select
    e.*,
    c.regra_id,
    case
        when c.regra_id is not null then null
        when e.valor > 0 and not exists (select 1 from {{ ref('stg_fiscal__nfe') }} n
                                         where n.empresa_id = e.empresa_id
                                           and n.data_emissao between e.data - 30 and e.data) then 1
        when e.valor < 0 and e.documento is null then 2
        when exists (select 1 from {{ ref('int_lancamentos_gerenciais') }} l
                     where l.empresa_id = e.empresa_id and l.data between e.data - 3 and e.data + 3
                       and abs(l.valor - e.valor) between 0.01 and abs(e.valor) * 0.05) then 3
        when exists (select 1 from {{ ref('stg_bancos__extrato_ofx') }} d
                     where d.empresa_id = e.empresa_id and d.valor = e.valor and d.descricao = e.descricao
                       and d.data = e.data and d.lancamento_extrato_id <> e.lancamento_extrato_id) then 5
        else 4
    end as motivo_id
from {{ ref('stg_bancos__extrato_ofx') }} e
left join {{ ref('int_conciliacao_candidatos') }} c using (lancamento_extrato_id)
```

### Resultado e caixa

```sql
-- models/marts/fct_resultado_mensal.sql
select
    l.empresa_id,
    date_trunc('month', l.data_competencia)::date as mes,
    m.conta_gerencial_id,
    sum(l.valor * g.sinal)                         as valor
from {{ ref('stg_erp__lancamentos') }} l
join {{ ref('stg_escritorio__de_para_contas') }} m
  on m.empresa_id = l.empresa_id and m.conta_contabil = l.conta_contabil
join {{ ref('dim_conta_gerencial') }} g using (conta_gerencial_id)
group by 1, 2, 3
```

```sql
-- models/marts/mart_carteira_empresa_mes.sql
with dre as (
    select empresa_id, mes,
           sum(valor) filter (where linha_dre = 'RB')  as receita_bruta,
           sum(valor) filter (where linha_dre in ('RB', 'DED')) as receita_liquida,
           sum(valor) filter (where linha_dre in ('RB', 'DED', 'CUS')) as lucro_bruto,
           sum(valor)                                   as resultado
    from {{ ref('fct_resultado_mensal') }} r
    join {{ ref('dim_conta_gerencial') }} g using (conta_gerencial_id)
    group by 1, 2
),
caixa as (
    select empresa_id, mes, sum(valor) filter (where categoria_caixa not in ('INV', 'EMP')) as caixa_operacoes
    from {{ ref('fct_caixa_mensal') }} group by 1, 2
),
conc as (
    select empresa_id, date_trunc('month', data)::date as mes,
           count(*) as linhas, count(regra_id) as automaticas, count(motivo_id) as excecoes
    from {{ ref('fct_extrato') }} group by 1, 2
)
select d.*, c.caixa_operacoes, k.linhas, k.automaticas, k.excecoes,
       sum(d.receita_bruta) over (partition by d.empresa_id order by d.mes
                                  rows between 11 preceding and current row) as rbt12
from dre d
left join caixa c using (empresa_id, mes)
left join conc k using (empresa_id, mes)
```

### Testes

```sql
-- tests/assert_ponte_resultado_caixa.sql
-- a soma das diferenças entre caixa e competência por grupo deve fechar no caixa das operações
with r as (select empresa_id, mes, sum(valor) as resultado from {{ ref('fct_resultado_mensal') }} group by 1, 2),
     c as (select empresa_id, mes, sum(valor) filter (where categoria_caixa not in ('INV', 'EMP')) as caixa
           from {{ ref('fct_caixa_mensal') }} group by 1, 2),
     p as (select empresa_id, mes, sum(diferenca) as ponte from {{ ref('int_ponte_caixa_competencia') }} group by 1, 2)
select r.empresa_id, r.mes
from r join c using (empresa_id, mes) join p using (empresa_id, mes)
where abs(r.resultado + p.ponte - c.caixa) > 0.01
```

## Padrões plantados no gerador

| Padrão | Como foi gerado | Onde aparece |
|---|---|---|
| Margem bruta em queda | Alimentação 03 e Comércio 11 com custo subindo até 8 p.p. nos últimos 6 meses | Visão geral, Carteira |
| Lucro que não virou caixa | Indústria 04 com prazo médio de recebimento subindo cerca de 55 dias nos últimos 10 meses e estoque crescendo | Visão geral, DRE e caixa, Carteira |
| Perto da faixa do Simples | Comércio 07, Serviços 05 e Alimentação 08 posicionadas entre 93% e 96% do limite da faixa seguinte | Visão geral, Carteira |
| Pendências concentradas | Comércio 02, Alimentação 06 e Serviços 09 com taxa de exceção de 15% a 19% e atraso na entrega de documentos | Conciliação, Carteira |
| 13º salário | provisão mensal na competência e pagamento em novembro e dezembro no caixa | Visão geral, Fluxo de caixa |

## Como regenerar e verificar

```
python3 demo/build_demos.py contabilidade
python3 demo/verificar_demos.py
```
