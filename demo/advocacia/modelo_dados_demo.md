# Modelo de dados do painel demonstrativo para advocacia

Documentação técnica da demonstração publicada em `demo-advocacia.html`. O escritório RRodrigues e Associados é fictício e todos os registros foram gerados por `gerar_dados_demo.py`, com semente fixa. Este material descreve o modelo dimensional, a definição de cada indicador e um esboço dos modelos dbt para PostgreSQL que sustentam um painel desse tipo em um projeto real.

## Decisões de identidade visual

Registradas aqui porque o pedido determina seguir o site em caso de ambiguidade.

1. Paleta extraída de index.html, advocacia.html e sobre.html: azul-marinho `#0C1B2E` (cor de tema), `#12263F`, `#1B3556` e `#2A4A70` para superfícies e séries principais, dourado envelhecido `#C2A064` para chamadas para ação e `#7A5C2C` para destaques em texto, fundo `#F4F6F9`, linhas `#D3DAE3`, texto `#1B2430`.
2. Tipografia: o site carrega Spectral (títulos) e IBM Plex Sans (corpo) de um serviço remoto de fontes. O demo não pode ter dependências externas, então declara as mesmas famílias com alternativas locais (Georgia e a fonte de sistema). Em quem já tem as fontes instaladas a aparência é idêntica; nos demais, a hierarquia serifada nos títulos e sem serifa no corpo se mantém.
3. Cores de séries: a paleta do site tem dois matizes, insuficientes para cinco áreas do direito. As áreas usam uma paleta segura para daltonismo (azul `#0072B2`, vermelhão `#D55E00`, verde-azulado `#009E73`, rosa-púrpura `#CC79A7`, laranja `#E69F00`), sempre acompanhada de rótulo em texto e de marcador com forma diferente por área. Nenhuma informação depende só da cor: linhas de competência e caixa diferem também por traço e marcador, e resultados negativos usam hachura, sinal e texto em vermelho.
4. Tom: mesmo registro do site, direto e sem promessa de resultado. Cada tela abre com a decisão de gestão que ela apoia.

## Escopo dos dados sintéticos

| Item | Valor |
|---|---|
| Data de referência | 30/09/2026 (último dia do mês anterior à publicação) |
| Histórico | 24 meses, de out/2024 a set/2026 |
| Advogados | 14, sendo 4 sócios, 4 sêniores e 6 juniores |
| Clientes | 180, pessoas físicas e jurídicas, nomeados por setor e código |
| Processos | cerca de 860, abertos desde 2021, com classe e assunto no formato das tabelas processuais unificadas do CNJ |
| Áreas | Trabalhista, Cível, Empresarial, Tributário, Família |
| Inventário LGPD | 19 registros de tratamento |

Os identificadores de processo usam o formato interno `MCA-0000` para não se confundirem com numeração única de processos reais. Os padrões de gestão que o painel revela foram plantados de forma explícita no gerador, e a lista está ao final deste documento.

## Diagrama entidade-relacionamento

```
dim_area (area_id PK, nome)
dim_advogado (advogado_id PK, nome, nivel, custo_hora)
dim_cliente (cliente_id PK, nome, tipo_pessoa, setor)
dim_mes (mes_id PK, ano, mes, inicio, fim)

dim_engajamento (engajamento_id PK,
                 cliente_id FK -> dim_cliente,
                 area_id FK -> dim_area,
                 responsavel_id FK -> dim_advogado,
                 modelo_cobranca)                 -- partido mensal ou por processo

dim_processo (processo_id PK, codigo,
              engajamento_id FK -> dim_engajamento,
              classe, assunto, data_abertura, data_encerramento,
              resultado, valor_causa)

fct_horas (mes_id FK, advogado_id FK, engajamento_id FK,
           horas_lancadas, horas_faturadas, custo_apropriado)
           grão: mês x advogado x engajamento

fct_honorarios (engajamento_id FK, mes_competencia_id FK, mes_caixa_id FK NULL,
                tipo_honorario, valor)
           grão: lançamento de honorário; mes_caixa_id nulo = a receber

fct_carteira_snapshot (data_referencia, processo_id FK,
                       fase, data_proximo_prazo, dias_ate_prazo, faixa_prazo)
           grão: processo ativo x data de referência

fct_inventario_lgpd (registro_id PK, sistema_origem, categoria_titular, dados,
                     sensivel, base_legal, finalidade, prazo_retencao, area_id FK NULL)

Relacionamentos
  dim_cliente 1..N dim_engajamento N..1 dim_area
  dim_advogado 1..N dim_engajamento (responsável)
  dim_engajamento 1..N dim_processo
  dim_engajamento 1..N fct_horas, 1..N fct_honorarios
  dim_processo 1..N fct_carteira_snapshot
```

O engajamento (cliente, área e advogado responsável) é a chave que permite reconciliar todas as telas: receita, custo, carteira e êxito são somados pelo mesmo conjunto de engajamentos para qualquer combinação de filtros.

## Definição dos indicadores

| Indicador | Regra | Período | Filtros de área e advogado |
|---|---|---|---|
| Honorários recebidos | soma de `fct_honorarios.valor` com `mes_caixa` no período | mês de caixa | engajamentos da área e do responsável |
| Honorários por competência | soma de `valor` com `mes_competencia` no período | mês de competência | idem |
| A receber | parte da competência do período com `mes_caixa` nulo | mês de competência | idem |
| Horas faturáveis | soma de `horas_lancadas` em clientes | mês do lançamento | idem; inclui horas de toda a equipe na carteira filtrada |
| Horas faturadas | soma de `horas_faturadas` | mês do lançamento | idem |
| Taxa de realização | horas faturadas dividido por horas faturáveis | mês do lançamento | idem |
| Custo apropriado | horas lançadas vezes custo-hora do nível do advogado | mês do lançamento | idem |
| Resultado | honorários recebidos menos custo apropriado | caixa e lançamento | idem |
| Margem | resultado dividido por honorários recebidos; sem recebimento, exibe "Sem recebimento" | caixa e lançamento | idem |
| Taxa de êxito | encerrados como procedente, parcialmente procedente ou acordo, divididos pelo total de encerrados | mês de encerramento | idem |
| Intervalo de confiança | método de Wilson, 95% | mês de encerramento | idem |
| Aging de prazos | faixas por dias até o próximo prazo na data de referência: vencidos, até 5, 6 a 15, acima de 15 | não se aplica (fotografia) | idem |
| Prazos em risco | vencidos mais até 5 dias | não se aplica | idem |
| Carteira por fase | processos ativos por fase na data de referência | não se aplica | idem |
| Concentração | menor número de clientes, ordenados por recebimento, cuja soma alcança 50% do recebido | mês de caixa | idem |
| Inventário LGPD | contagem de registros; alerta quando a base legal é "Não definida" ou o prazo de retenção é "Não definido" | não se aplica | só área; registros transversais sempre aparecem |

Regra de reconciliação, verificada por script: para qualquer combinação de período, área e advogado, o total do indicador de topo é igual à soma por área, à soma por cliente e à soma por advogado (custo e horas), e a curva de Pareto termina em 100%.

## Esboço dos modelos dbt (PostgreSQL)

Estrutura sugerida:

```
models/
  staging/
    juridico/  stg_juridico__processos.sql, stg_juridico__prazos.sql, stg_juridico__lancamentos_horas.sql
    financeiro/ stg_financeiro__honorarios.sql
    planilhas/ stg_planilhas__custo_hora.sql
    publico/   stg_datajud__movimentos.sql
  intermediate/
    int_engajamentos.sql
    int_horas_custeadas.sql
    int_honorarios_competencia_caixa.sql
  marts/
    dim_advogado.sql, dim_cliente.sql, dim_engajamento.sql, dim_processo.sql
    fct_horas.sql, fct_honorarios.sql, fct_carteira_snapshot.sql
    mart_rentabilidade_cliente_mes.sql
tests/
  assert_reconciliacao_rentabilidade.sql
```

### sources.yml

```yaml
version: 2
sources:
  - name: juridico
    schema: raw_juridico
    loaded_at_field: _extraido_em
    freshness:
      warn_after: {count: 24, period: hour}
    tables:
      - name: processos
      - name: prazos
      - name: lancamentos_horas
  - name: financeiro
    schema: raw_financeiro
    tables:
      - name: honorarios
  - name: planilhas
    schema: raw_planilhas
    tables:
      - name: custo_hora
  - name: datajud
    schema: raw_publico
    tables:
      - name: movimentos
```

### Staging

```sql
-- models/staging/juridico/stg_juridico__processos.sql
with origem as (
    select * from {{ source('juridico', 'processos') }}
)
select
    cast(id as bigint)                                   as processo_id,
    upper(trim(codigo))                                  as codigo,
    nullif(trim(numero_cnj), '')                         as numero_cnj,
    cast(cliente_id as bigint)                           as cliente_id,
    lower(trim(area))                                    as area_codigo,
    cast(responsavel_id as bigint)                       as responsavel_id,
    trim(classe)                                         as classe,
    trim(assunto)                                        as assunto,
    cast(data_distribuicao as date)                      as data_abertura,
    cast(nullif(data_encerramento, '') as date)          as data_encerramento,
    case lower(trim(resultado))
        when 'procedente' then 'procedente'
        when 'parcialmente procedente' then 'parcial'
        when 'acordo' then 'acordo'
        when 'improcedente' then 'improcedente'
        when 'extinto' then 'extinto'
    end                                                  as resultado,
    cast(valor_causa as numeric(14, 2))                  as valor_causa,
    _extraido_em
from origem
where coalesce(excluido, false) = false
```

```sql
-- models/staging/juridico/stg_juridico__lancamentos_horas.sql
select
    cast(id as bigint)                    as lancamento_id,
    cast(advogado_id as bigint)           as advogado_id,
    cast(processo_id as bigint)           as processo_id,
    cast(cliente_id as bigint)            as cliente_id,
    cast(data_lancamento as date)         as data_lancamento,
    cast(minutos as numeric) / 60.0       as horas_lancadas,
    case when faturavel and status_cobranca = 'faturado'
         then cast(minutos as numeric) / 60.0 else 0 end as horas_faturadas
from {{ source('juridico', 'lancamentos_horas') }}
where minutos > 0
```

```sql
-- models/staging/financeiro/stg_financeiro__honorarios.sql
select
    cast(id as bigint)                                    as honorario_id,
    cast(cliente_id as bigint)                            as cliente_id,
    lower(trim(area))                                     as area_codigo,
    case tipo when 'mensal' then 'partido_mensal'
              when 'exito' then 'exito'
              else 'contratual' end                       as tipo_honorario,
    date_trunc('month', cast(data_competencia as date))::date as mes_competencia,
    date_trunc('month', cast(data_recebimento as date))::date as mes_caixa,   -- nulo enquanto não recebido
    cast(valor as numeric(14, 2))                         as valor
from {{ source('financeiro', 'honorarios') }}
where status <> 'cancelado'
```

### Intermediate

```sql
-- models/intermediate/int_engajamentos.sql
-- um engajamento por cliente, área e advogado responsável
select
    {{ dbt_utils.generate_surrogate_key(['cliente_id', 'area_codigo', 'responsavel_id']) }} as engajamento_id,
    cliente_id,
    area_codigo,
    responsavel_id,
    min(data_abertura) as inicio_relacao
from {{ ref('stg_juridico__processos') }}
group by 1, 2, 3, 4
```

```sql
-- models/intermediate/int_horas_custeadas.sql
with horas as (
    select h.*, p.area_codigo, p.responsavel_id
    from {{ ref('stg_juridico__lancamentos_horas') }} h
    join {{ ref('stg_juridico__processos') }} p using (processo_id)
),
custo as (
    -- custo-hora apropriado mantido pelo escritório em planilha, com vigência
    select nivel, custo_hora, vigencia_inicio,
           coalesce(lead(vigencia_inicio) over (partition by nivel order by vigencia_inicio),
                    date '9999-12-31') as vigencia_fim
    from {{ ref('stg_planilhas__custo_hora') }}
)
select
    date_trunc('month', h.data_lancamento)::date as mes,
    h.advogado_id,
    e.engajamento_id,
    sum(h.horas_lancadas)                        as horas_lancadas,
    sum(h.horas_faturadas)                       as horas_faturadas,
    sum(h.horas_lancadas * c.custo_hora)         as custo_apropriado
from horas h
join {{ ref('dim_advogado') }} a on a.advogado_id = h.advogado_id
join custo c on c.nivel = a.nivel
            and h.data_lancamento >= c.vigencia_inicio and h.data_lancamento < c.vigencia_fim
join {{ ref('int_engajamentos') }} e
  on e.cliente_id = h.cliente_id and e.area_codigo = h.area_codigo and e.responsavel_id = h.responsavel_id
group by 1, 2, 3
```

### Marts

```sql
-- models/marts/fct_carteira_snapshot.sql
{{ config(materialized='incremental', unique_key=['data_referencia', 'processo_id']) }}
with ref_data as (select {{ var('data_referencia', 'current_date - 1') }}::date as data_referencia),
proximo as (
    select processo_id, min(data_prazo) filter (where cumprido = false) as data_proximo_prazo
    from {{ ref('stg_juridico__prazos') }}
    group by 1
)
select
    r.data_referencia,
    p.processo_id,
    p.fase,
    x.data_proximo_prazo,
    x.data_proximo_prazo - r.data_referencia as dias_ate_prazo,
    case
        when x.data_proximo_prazo is null then 'sem prazo pendente'
        when x.data_proximo_prazo < r.data_referencia then 'vencido'
        when x.data_proximo_prazo - r.data_referencia <= 5 then 'até 5 dias'
        when x.data_proximo_prazo - r.data_referencia <= 15 then '6 a 15 dias'
        else 'acima de 15 dias'
    end as faixa_prazo
from {{ ref('dim_processo') }} p
cross join ref_data r
left join proximo x using (processo_id)
where p.data_encerramento is null
```

```sql
-- models/marts/mart_rentabilidade_cliente_mes.sql
with receita as (
    select engajamento_id, mes_caixa as mes, sum(valor) as recebido
    from {{ ref('fct_honorarios') }}
    where mes_caixa is not null
    group by 1, 2
),
custo as (
    select engajamento_id, mes, sum(custo_apropriado) as custo, sum(horas_lancadas) as horas
    from {{ ref('fct_horas') }}
    group by 1, 2
),
base as (
    select coalesce(r.engajamento_id, c.engajamento_id) as engajamento_id,
           coalesce(r.mes, c.mes)                       as mes,
           coalesce(r.recebido, 0)                      as recebido,
           coalesce(c.custo, 0)                         as custo,
           coalesce(c.horas, 0)                         as horas
    from receita r
    full outer join custo c on c.engajamento_id = r.engajamento_id and c.mes = r.mes
)
select
    b.mes, e.cliente_id, e.area_id, e.responsavel_id,
    sum(b.recebido)                     as recebido,
    sum(b.custo)                        as custo_apropriado,
    sum(b.recebido) - sum(b.custo)      as resultado,
    sum(b.horas)                        as horas
from base b
join {{ ref('dim_engajamento') }} e using (engajamento_id)
group by 1, 2, 3, 4
```

### Testes

```yaml
# models/marts/schema.yml (trecho)
version: 2
models:
  - name: fct_honorarios
    columns:
      - name: engajamento_id
        tests: [not_null, {relationships: {to: ref('dim_engajamento'), field: engajamento_id}}]
      - name: valor
        tests: [not_null, {dbt_utils.accepted_range: {min_value: 0, inclusive: false}}]
  - name: fct_horas
    tests:
      - dbt_utils.unique_combination_of_columns:
          combination_of_columns: [mes, advogado_id, engajamento_id]
      - dbt_utils.expression_is_true:
          expression: "horas_faturadas <= horas_lancadas"
```

```sql
-- tests/assert_reconciliacao_rentabilidade.sql
-- falha se o total do mart divergir das tabelas de fato em qualquer mês
with mart as (
    select mes, sum(recebido) as recebido, sum(custo_apropriado) as custo
    from {{ ref('mart_rentabilidade_cliente_mes') }} group by 1
),
fato as (
    select coalesce(h.mes, r.mes) as mes, coalesce(r.recebido, 0) as recebido, coalesce(h.custo, 0) as custo
    from (select mes_caixa as mes, sum(valor) as recebido from {{ ref('fct_honorarios') }}
          where mes_caixa is not null group by 1) r
    full outer join (select mes, sum(custo_apropriado) as custo from {{ ref('fct_horas') }} group by 1) h
      on h.mes = r.mes
)
select f.mes
from fato f
left join mart m using (mes)
where abs(f.recebido - coalesce(m.recebido, 0)) > 0.01
   or abs(f.custo - coalesce(m.custo, 0)) > 0.01
```

## Padrões plantados no gerador

Os dados foram calibrados para que o painel tenha o que mostrar. Em um projeto real, esses achados vêm dos dados do cliente; aqui eles são declarados para quem quiser auditar.

| Padrão | Como foi gerado | Onde aparece |
|---|---|---|
| a) área com êxito alto e rentabilidade baixa | Tributário com probabilidade de êxito de 86%, esforço por processo maior e margem-alvo de 3% | Visão geral, Taxa de êxito, Rentabilidade |
| b) clientes de grande volume com margem negativa | Varejo 001, Logística 002 e Saúde 003 com dezenas de processos e partido mensal baixo | Visão geral, Rentabilidade |
| c) júnior acima da média e sócio com horas não faturadas | Rafael Lima com 182 h/mês e realização de 96%; Ricardo Meireles com realização de 58% | Produtividade |
| d) concentração da receita | sete clientes consultivos com partido mensal alto | Visão geral, Pareto |
| e) bolsão de prazos próximos | 34% dos prazos trabalhistas ativos em até 5 dias, contra 9% nas demais áreas | Prazos e carteira |
| f) êxito reconhecido com atraso | honorários de êxito recebidos de 0 a 9 meses após o encerramento, e de 6 a 12 meses no tributário | Visão geral (competência e caixa), Rentabilidade (a receber) |

A receita de cada engajamento é calculada a partir do custo-hora apropriado e de uma margem-alvo sorteada. Por isso os números variam entre períodos de forma plausível, mas a direção dos padrões se mantém no período padrão de 12 meses.

## Como regenerar e verificar

```
cd demo/advocacia
python3 gerar_dados_demo.py --html ../../demo-advocacia.html
python3 ../verificar_demos.py
```

A URL canônica e a URL do Open Graph são definidas pela constante `CANONICAL_URL` em `gerar_dados_demo.py` e reescritas no HTML a cada geração. A data de referência é a constante `DATA_REFERENCIA`; para publicar um novo mês, avance essa data e regenere.
