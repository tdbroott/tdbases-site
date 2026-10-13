# Modelo de dados do painel demonstrativo para varejo, bares e restaurantes

Documentação técnica da demonstração publicada em `demo-varejo.html`. O Bistrô Jatobá é fictício; cardápio, fichas técnicas, preços, vendas e estoque foram gerados por `gerar_dados.py`, com semente fixa. Os aplicativos de delivery aparecem sem marca de propósito, como "Aplicativo de delivery 1" e "Aplicativo de delivery 2"; comissões e taxas são valores de exemplo.

## Decisões de identidade visual

1. Mesma paleta, tipografia e estrutura de telas das demais demonstrações; o código comum fica em `demo/core`.
2. As cores por canal evitam o vermelho, reservado para alerta. No mapa de calor do ticket médio, o número é a leitura principal e o fundo indica apenas o volume de pedidos.
3. Divergências de estoque acima de 3% usam hachura além da cor.

## Escopo dos dados sintéticos

| Item | Valor |
|---|---|
| Data de referência | 30/09/2026 |
| Histórico | 24 meses, de out/2024 a set/2026 |
| Cardápio | 35 itens em 6 categorias, com ficha técnica |
| Insumos | 32, com preço de compra mensal |
| Canais | salão, balcão e retirada, dois aplicativos de delivery |
| Vendas | quantidade por item, canal e mês; preço por canal em centavos |
| Pedidos | por mês, canal, dia da semana e faixa horária, com receita em centavos |
| Estoque | estoque inicial, compras mensais e contagem final por insumo |

Valores de venda são gravados em centavos inteiros, para que faturamento por item, por canal, por categoria e por faixa horária reconciliem exatamente.

## Diagrama entidade-relacionamento

```
dim_item (item_id PK, nome, categoria)
dim_insumo (insumo_id PK, nome, unidade)
dim_canal (canal_id PK, nome, comissao, taxa_pagamento, fator_preco)
dim_mes (mes_id PK, ano, mes)
bridge_ficha_tecnica (item_id FK, insumo_id FK, quantidade, vigencia_inicio, vigencia_fim)

fct_venda_item (pedido_id, item_id FK, canal_id FK, data, hora, quantidade,
                preco_unitario, desconto_promocional, embalagem)
          grão: item vendido em um pedido
fct_pedido (pedido_id PK, canal_id FK, data, hora, valor_pago)
fct_preco_insumo (insumo_id FK, mes_id FK, preco_medio_compra)
fct_estoque_mensal (insumo_id FK, mes_id FK, estoque_inicial, compras, contagem_final)
```

A receita do pedido é igual à soma dos itens do pedido; é isso que permite comparar ticket médio, faturamento por item e margem por canal sobre a mesma base.

## Definição dos indicadores

| Indicador | Regra |
|---|---|
| Faturamento bruto | quantidade vezes o preço de cardápio do canal |
| Faturamento | bruto menos promoções pagas pelo restaurante |
| CMV | quantidade vezes o custo da ficha técnica no preço de compra do mês |
| Comissão | faturamento vezes a comissão do canal |
| Taxa de pagamento | faturamento vezes a taxa do meio de pagamento predominante no canal |
| Embalagem | quantidade vezes o custo de embalagem da categoria, integral nos aplicativos e pela metade no balcão e retirada |
| Margem de contribuição | faturamento menos CMV, comissão, taxa e embalagem; não inclui custos fixos |
| Ticket médio | receita dos pedidos dividida pelo número de pedidos; não depende da categoria |
| Curva ABC | classe A até 80% do faturamento acumulado, B até 95%, C o restante |
| Consumo teórico | vendas de todos os canais vezes a ficha técnica |
| Consumo real | estoque inicial mais compras menos contagem final |
| Divergência | consumo real menos teórico, em quantidade, percentual e valor ao preço médio do período |

## Esboço dos modelos dbt (PostgreSQL)

```
models/
  staging/
    pdv/        stg_pdv__pedidos.sql, stg_pdv__itens.sql
    delivery/   stg_delivery__pedidos.sql, stg_delivery__repasses.sql
    compras/    stg_compras__nfe_itens.sql
    cozinha/    stg_cozinha__fichas.sql, stg_cozinha__contagens.sql
  intermediate/
    int_item_unificado.sql          -- de-para do nome do item entre PDV e aplicativos
    int_venda_item_canal.sql
    int_custo_ficha_mes.sql
  marts/
    fct_venda_item.sql, fct_pedido.sql, fct_estoque_mensal.sql
    mart_margem_item_canal_mes.sql
```

### Cadastro único de itens

```sql
-- models/intermediate/int_item_unificado.sql
-- o mesmo prato tem nomes diferentes no PDV e em cada aplicativo; o de-para é mantido pela operação
select
    coalesce(d.item_id, p.item_id)            as item_id,
    s.origem,
    s.codigo_origem,
    s.nome_origem
from (
    select 'pdv' as origem, codigo as codigo_origem, nome as nome_origem from {{ ref('stg_pdv__itens') }}
    union all
    select canal, codigo_item, nome_item from {{ ref('stg_delivery__pedidos') }} group by 1, 2, 3
) s
left join {{ ref('de_para_itens') }} d on d.origem = s.origem and d.codigo_origem = s.codigo_origem
left join {{ ref('stg_pdv__itens') }} p on s.origem = 'pdv' and p.codigo = s.codigo_origem
```

### Custo pela ficha técnica

```sql
-- models/intermediate/int_custo_ficha_mes.sql
with preco as (
    select insumo_id, date_trunc('month', data_emissao)::date as mes,
           sum(valor_total) / nullif(sum(quantidade_convertida), 0) as preco_medio
    from {{ ref('stg_compras__nfe_itens') }}
    group by 1, 2
)
select f.item_id, p.mes, sum(f.quantidade * p.preco_medio) as custo_unitario
from {{ ref('stg_cozinha__fichas') }} f
join preco p on p.insumo_id = f.insumo_id
            and p.mes >= f.vigencia_inicio and p.mes < coalesce(f.vigencia_fim, date '9999-12-31')
group by 1, 2
```

### Margem por item, canal e mês

```sql
-- models/marts/mart_margem_item_canal_mes.sql
select
    v.item_id,
    v.canal_id,
    date_trunc('month', v.data)::date                         as mes,
    sum(v.quantidade)                                         as quantidade,
    sum(v.quantidade * v.preco_unitario)                      as faturamento_bruto,
    sum(v.desconto_promocional)                               as promocoes,
    sum(v.quantidade * v.preco_unitario - v.desconto_promocional) as faturamento,
    sum(v.quantidade * c.custo_unitario)                      as cmv,
    sum((v.quantidade * v.preco_unitario - v.desconto_promocional) * k.comissao)       as comissao,
    sum((v.quantidade * v.preco_unitario - v.desconto_promocional) * k.taxa_pagamento) as taxa,
    sum(v.embalagem)                                          as embalagem
from {{ ref('fct_venda_item') }} v
join {{ ref('int_custo_ficha_mes') }} c on c.item_id = v.item_id and c.mes = date_trunc('month', v.data)
join {{ ref('dim_canal') }} k using (canal_id)
group by 1, 2, 3
```

### Testes

```yaml
# models/marts/schema.yml (trecho)
version: 2
models:
  - name: fct_pedido
    tests:
      - dbt_utils.expression_is_true:
          expression: "valor_pago >= 0"
  - name: mart_margem_item_canal_mes
    tests:
      - dbt_utils.unique_combination_of_columns:
          combination_of_columns: [item_id, canal_id, mes]
```

```sql
-- tests/assert_pedidos_igual_itens.sql
-- a receita dos pedidos deve ser igual à soma dos itens, por canal e mês
with p as (select canal_id, date_trunc('month', data)::date as mes, sum(valor_pago) as v from {{ ref('fct_pedido') }} group by 1, 2),
     i as (select canal_id, mes, sum(faturamento) as v from {{ ref('mart_margem_item_canal_mes') }} group by 1, 2)
select p.canal_id, p.mes from p join i using (canal_id, mes) where abs(p.v - i.v) > 0.01
```

## Padrões plantados no gerador

| Padrão | Como foi gerado | Onde aparece |
|---|---|---|
| Prato sem margem em um canal | camarão subindo 46% em 15 meses e promoção de 25% no aplicativo 2 para risoto e moqueca | Visão geral, Margem por canal |
| CMV subindo sem reajuste | um único reajuste de cardápio, em jul/2025, enquanto filé mignon, camarão, azeite, chocolate e café sobem | Visão geral, CMV por prato |
| Canal com margem menor | comissão de 23% e 27% nos aplicativos, mais embalagem e promoções | Margem por canal |
| Ticket por horário | almoço com executivo no balcão, jantar com ticket maior no salão, aplicativos à noite | Ticket médio |
| Concentração do cardápio | popularidade desigual entre itens | Curva ABC |
| Divergência de estoque | filé mignon 9,5%, camarão 6,5%, cerveja 4% e parmesão 3,5%; demais entre 0,4% e 1,8% | Estoque |

## Como regenerar e verificar

```
python3 demo/build_demos.py varejo
python3 demo/verificar_demos.py
```
