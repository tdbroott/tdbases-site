#!/usr/bin/env python3
"""
Gerador determinístico dos dados sintéticos do painel demonstrativo
"RRodrigues e Associados" (escritório fictício) da TDBASES.

Uso:
    python3 gerar_dados_demo.py                      # gera dados_demo.json
    python3 gerar_dados_demo.py --html ../../demo-advocacia.html
        # gera o JSON e injeta no HTML, entre os marcadores
        # <script id="dados-demo" type="application/json"> ... </script>,
        # atualizando também a URL canônica e as meta tags Open Graph.

Nenhum dado aqui representa pessoa, empresa ou processo real. Classes e
assuntos são inspirados na estrutura das tabelas processuais unificadas do
CNJ, mas os registros são inventados.
"""
import argparse
import json
import math
import random
import re
from datetime import date, timedelta
from pathlib import Path

# ---------------------------------------------------------------- constantes
SEMENTE = 20261001
DATA_REFERENCIA = date(2026, 9, 30)   # último dia do mês anterior à publicação
MESES_HISTORICO = 24
CANONICAL_URL = "https://www.tdbases.com.br/demo-advocacia.html"
ESCRITORIO = "RRodrigues e Associados"

AREAS = ["Trabalhista", "Cível", "Empresarial", "Tributário", "Família"]
TRAB, CIV, EMP, TRIB, FAM = range(5)
NIVEIS = ["Sócio", "Sênior", "Júnior"]
CUSTO_HORA = {0: 390, 1: 240, 2: 125}   # custo-hora apropriado (salário, encargos, rateio)

# nome, nível, áreas, horas lançadas/mês, taxa de realização
ADVOGADOS = [
    ("Ricardo Meireles", 0, [EMP, CIV], 132, 0.58),   # padrão c: sócio com muitas horas não faturadas
    ("Beatriz Campos", 0, [TRAB], 128, 0.90),
    ("Fernando Aguiar", 0, [TRIB], 130, 0.89),
    ("Lúcia Nogueira", 0, [FAM, CIV], 126, 0.91),
    ("Paulo Teixeira", 1, [TRAB], 150, 0.88),
    ("Mariana Duarte", 1, [CIV], 148, 0.90),
    ("Gustavo Rezende", 1, [TRIB], 152, 0.87),
    ("Camila Freitas", 1, [EMP, FAM], 146, 0.89),
    ("Rafael Lima", 2, [TRAB], 182, 0.96),            # padrão c: júnior acima da média
    ("Juliana Ramos", 2, [TRAB], 150, 0.86),
    ("Thiago Barros", 2, [CIV], 148, 0.85),
    ("Larissa Pacheco", 2, [TRIB], 152, 0.87),
    ("André Vasconcelos", 2, [EMP], 147, 0.86),
    ("Natália Brito", 2, [FAM], 145, 0.88),
]

FASES = ["Postulatória", "Instrução", "Recursal", "Execução", "Suspenso"]
RESULTADOS = ["Procedente", "Parcialmente procedente", "Acordo", "Improcedente", "Extinto sem mérito"]
EXITO = {0, 1, 2}   # procedente, parcialmente procedente ou acordo

# classe -> assuntos, por área (estrutura inspirada nas TPU do CNJ)
CLASSES = {
    TRAB: [("Ação Trabalhista - Rito Ordinário", ["Horas extras", "Verbas rescisórias", "Adicional de insalubridade", "Reconhecimento de vínculo"]),
           ("Ação Trabalhista - Rito Sumaríssimo", ["Verbas rescisórias", "Multa do art. 477 da CLT"]),
           ("Recurso Ordinário Trabalhista", ["Horas extras", "Danos morais"])],
    CIV: [("Procedimento Comum Cível", ["Indenização por dano moral", "Rescisão contratual", "Responsabilidade civil"]),
          ("Execução de Título Extrajudicial", ["Cheque", "Contrato de prestação de serviços"]),
          ("Procedimento do Juizado Especial Cível", ["Defeito do produto", "Cobrança indevida"]),
          ("Monitória", ["Duplicata", "Nota promissória"])],
    EMP: [("Dissolução Parcial de Sociedade", ["Apuração de haveres", "Exclusão de sócio"]),
          ("Recuperação Judicial", ["Concurso de credores"]),
          ("Procedimento Comum Cível", ["Contratos empresariais", "Propriedade industrial"])],
    TRIB: [("Mandado de Segurança Cível", ["ICMS", "PIS/COFINS", "Contribuições previdenciárias"]),
           ("Execução Fiscal", ["Dívida ativa tributária"]),
           ("Embargos à Execução Fiscal", ["ICMS", "IPTU"]),
           ("Procedimento Comum Cível", ["Repetição de indébito", "Compensação tributária"])],
    FAM: [("Divórcio Litigioso", ["Partilha de bens", "Guarda"]),
          ("Alimentos - Lei Especial nº 5.478/68", ["Fixação", "Revisão"]),
          ("Inventário", ["Partilha", "Sobrepartilha"]),
          ("Regulamentação de Visitas", ["Direito de convivência"])],
}

# parâmetros por área
DUR_MED = {TRAB: 20, CIV: 26, EMP: 18, TRIB: 22, FAM: 13}            # duração mediana (meses)
P_EXITO = {TRAB: 0.54, CIV: 0.60, EMP: 0.63, TRIB: 0.86, FAM: 0.62}   # padrão a: tributário alto
ESFORCO = {TRAB: 1.5, CIV: 2.3, EMP: 4.2, TRIB: 7.0, FAM: 3.0}       # h/processo/mês antes de normalizar
CAUSA_MED = {TRAB: 55000, CIV: 70000, EMP: 260000, TRIB: 420000, FAM: 140000}
SETORES = ["Varejo", "Indústria", "Serviços", "Construção", "Saúde", "Agronegócio",
           "Logística", "Tecnologia", "Educação"]


def meses():
    m0 = date(DATA_REFERENCIA.year, DATA_REFERENCIA.month, 1)
    out = []
    y, mo = m0.year, m0.month
    for _ in range(MESES_HISTORICO):
        out.append((y, mo))
        mo -= 1
        if mo == 0:
            y, mo = y - 1, 12
    return list(reversed(out))


MESES = meses()
IDX_MES = {ym: i for i, ym in enumerate(MESES)}


def add_meses(d, n):
    y = d.year + (d.month - 1 + n) // 12
    m = (d.month - 1 + n) % 12 + 1
    return date(y, m, min(d.day, 28))


def fim_mes(y, m):
    return (date(y + (m == 12), m % 12 + 1, 1) - timedelta(days=1))


def gerar():
    rnd = random.Random(SEMENTE)
    lognorm = lambda med, s: med * math.exp(rnd.gauss(0, s))

    area_adv = {a: [i for i, ad in enumerate(ADVOGADOS) if a in ad[2]] for a in range(5)}

    # ------------------------------------------------------------ clientes
    clientes = []        # nome, tipo, setor
    engs = []            # cliente, área, responsável, ajudante, retenção mensal, pct êxito
    planos = []          # (eng, n_processos)

    def novo_cliente(setor, tipo="PJ"):
        n = len(clientes) + 1
        nome = f"{setor} {n:03d}" if tipo == "PJ" else f"Pessoa física {n:03d}"
        clientes.append([nome, tipo, setor if tipo == "PJ" else "Pessoa física"])
        return len(clientes) - 1

    def novo_eng(c, area, retencao, nproc, resp=None, pct=None):
        equipe = area_adv[area]
        if resp is None:
            pesos = [3 if ADVOGADOS[i][1] == 0 else 2 for i in equipe]
            resp = rnd.choices(equipe, pesos)[0]
        aj = [i for i in equipe if i != resp and ADVOGADOS[i][1] > 0]
        ajud = rnd.choice(aj) if aj else resp
        if pct is None:
            pct = rnd.uniform(0.05, 0.09) if retencao else rnd.uniform(0.12, 0.20)
        engs.append([c, area, resp, ajud, retencao, round(pct, 3)])
        planos.append((len(engs) - 1, nproc))

    # padrão b: grandes volumes com retenção baixa
    c = novo_cliente("Varejo"); novo_eng(c, TRAB, 8800, 132, resp=1)
    c = novo_cliente("Logística"); novo_eng(c, TRAB, 6200, 82, resp=4)
    c = novo_cliente("Saúde"); novo_eng(c, CIV, 6900, 70, resp=5)
    # padrão d: poucos clientes consultivos concentram a receita
    c = novo_cliente("Indústria"); novo_eng(c, EMP, 41000, 7, resp=0); novo_eng(c, TRIB, 12000, 6, resp=2)
    c = novo_cliente("Construção"); novo_eng(c, EMP, 29000, 5, resp=0); novo_eng(c, CIV, 6000, 6, resp=3)
    c = novo_cliente("Agronegócio"); novo_eng(c, TRIB, 23000, 9, resp=2)
    c = novo_cliente("Tecnologia"); novo_eng(c, EMP, 21000, 4, resp=7)
    c = novo_cliente("Varejo"); novo_eng(c, CIV, 17500, 9, resp=3)
    c = novo_cliente("Serviços"); novo_eng(c, TRAB, 16000, 12, resp=1)
    c = novo_cliente("Indústria"); novo_eng(c, TRAB, 13500, 14, resp=4)

    while len(clientes) < 180:
        if rnd.random() < 0.58:
            setor = rnd.choice(SETORES)
            c = novo_cliente(setor)
            area = rnd.choices([TRAB, CIV, EMP, TRIB], [0.35, 0.27, 0.16, 0.22])[0]
            ret = round(lognorm(2600, 0.45), -2) if rnd.random() < 0.42 else 0
            n = min(14, 1 + int(rnd.expovariate(0.33)))
            novo_eng(c, area, ret, n)
            if rnd.random() < 0.16:
                a2 = rnd.choice([a for a in (TRAB, CIV, TRIB) if a != area])
                novo_eng(c, a2, 0, 1 + int(rnd.expovariate(0.9)))
        else:
            c = novo_cliente("", "PF")
            area = rnd.choices([FAM, CIV, TRAB], [0.50, 0.32, 0.18])[0]
            novo_eng(c, area, 0, 1 + int(rnd.expovariate(1.2)))

    # ------------------------------------------------------------ processos
    procs = []   # eng, cod, classe, assunto, abertura, encerramento, resultado, fase, prazo, valor
    classes_l, assuntos_l = [], []

    def idx(lista, v):
        if v not in lista:
            lista.append(v)
        return lista.index(v)

    inicio_abert = date(2021, 1, 1)
    janela_dias = (DATA_REFERENCIA - inicio_abert).days
    for e, n in planos:
        area = engs[e][1]
        for _ in range(n):
            # aberturas mais densas nos anos recentes
            u = rnd.random() ** 0.72
            abert = inicio_abert + timedelta(days=int(u * janela_dias))
            dur = lognorm(DUR_MED[area], 0.55)
            enc = abert + timedelta(days=int(dur * 30.4))
            classe, assuntos = rnd.choice(CLASSES[area])
            assunto = rnd.choice(assuntos)
            valor = round(lognorm(CAUSA_MED[area], 0.7), -2)
            if enc <= DATA_REFERENCIA:
                pe = P_EXITO[area]
                res = rnd.choices([0, 1, 2, 3, 4], [pe * .45, pe * .30, pe * .25, (1 - pe) * .75, (1 - pe) * .25])[0]
                fase, prazo = -1, ""
            else:
                enc, res = None, -1
                idade = (DATA_REFERENCIA - abert).days / 30.4
                if rnd.random() < 0.05:
                    fase = 4
                else:
                    lim = [6, 18, 34]
                    fase = 0 if idade < lim[0] else 1 if idade < lim[1] else 2 if idade < lim[2] else 3
                    if rnd.random() < 0.2:
                        fase = max(0, min(3, fase + rnd.choice([-1, 1])))
                    if classe.startswith("Recurso"):
                        fase = 2
                prazo = ""
                if fase != 4 and rnd.random() < 0.78:
                    # padrão e: bolsão de prazos próximos no trabalhista
                    p5 = 0.34 if area == TRAB else 0.09
                    r = rnd.random()
                    if r < 0.04:
                        d = -rnd.randint(1, 9)
                    elif r < 0.04 + p5:
                        d = rnd.randint(0, 5)
                    elif r < 0.04 + p5 + 0.22:
                        d = rnd.randint(6, 15)
                    else:
                        d = rnd.randint(16, 75)
                    prazo = (DATA_REFERENCIA + timedelta(days=d)).isoformat()
            procs.append([e, f"MCA-{len(procs) + 1:04d}", idx(classes_l, classe), idx(assuntos_l, assunto),
                          abert.isoformat(), enc.isoformat() if enc else "", res, fase, prazo, int(valor)])

    # ------------------------------------------------------------ horas
    # esforço bruto por engajamento e mês, depois normalizado à capacidade de cada advogado
    bruto = [[0.0] * len(engs) for _ in range(MESES_HISTORICO)]
    for p in procs:
        e, area = p[0], engs[p[0]][1]
        abert = date.fromisoformat(p[4])
        enc = date.fromisoformat(p[5]) if p[5] else None
        for m, (y, mo) in enumerate(MESES):
            ini, fim = date(y, mo, 1), fim_mes(y, mo)
            if abert <= fim and (enc is None or enc >= ini):
                f = 1.6 if abert >= ini else 1.0       # mês de abertura pesa mais
                bruto[m][e] += ESFORCO[area] * f
    for e, eng in enumerate(engs):
        if eng[4]:
            for m in range(MESES_HISTORICO):
                bruto[m][e] += eng[4] / 480.0          # horas consultivas do partido mensal

    ts = []   # mês, advogado, eng, horas lançadas, horas faturadas
    for m in range(MESES_HISTORICO):
        for a, (nome, nivel, areas, cap, real) in enumerate(ADVOGADOS):
            parts = {}
            for e, eng in enumerate(engs):
                if bruto[m][e] <= 0:
                    continue
                if eng[2] == a:
                    w = 0.45
                elif eng[3] == a:
                    w = 0.55
                else:
                    continue
                parts[e] = bruto[m][e] * w
            tot = sum(parts.values())
            if not tot:
                continue
            alvo = cap * rnd.uniform(0.93, 1.07)
            for e, v in parts.items():
                h = round(alvo * v / tot * 2) / 2
                if h <= 0:
                    continue
                hf = min(h, round(h * real * rnd.uniform(0.94, 1.04) * 2) / 2)
                ts.append([m, a, e, h, hf])

    # ------------------------------------------------------------ receitas
    # A receita de cada engajamento é calibrada a partir do custo-hora apropriado e
    # de uma margem-alvo sorteada, para que os padrões do painel sejam controlados.
    # tipo 0 = honorário mensal (partido), 1 = parcela contratual por processo,
    # 2 = honorário de êxito
    custo = [[0.0] * len(engs) for _ in range(MESES_HISTORICO)]
    for m, a, e, h, hf in ts:
        custo[m][e] += h * CUSTO_HORA[ADVOGADOS[a][1]]
    MARGEM_BASE = {TRAB: 0.30, CIV: 0.30, EMP: 0.42, TRIB: 0.03, FAM: 0.30}
    alvo_especial = {0: -0.48, 1: -0.38, 2: -0.33,               # padrão b
                     3: 0.62, 4: 0.60, 5: 0.60, 6: 0.60, 7: 0.57}  # consultivos (padrão d)
    exito_por_eng = {}
    for p in procs:
        if p[5] and p[6] in EXITO:
            enc = date.fromisoformat(p[5])
            me = IDX_MES.get((enc.year, enc.month))
            if me is not None:
                fator = {0: 1.0, 1: 0.55, 2: 0.45}[p[6]]
                exito_por_eng.setdefault(p[0], []).append((me, p[9] * engs[p[0]][5] * fator))
    rec = []   # eng, mês competência, mês caixa (-1 = a receber), tipo, valor

    def lanca(e, m, atraso, tipo, v):
        cx = m + atraso
        rec.append([e, m, cx if cx < MESES_HISTORICO else -1, tipo, int(round(v, -1))])

    for e, (c, area, resp, aj, ret, pct) in enumerate(engs):
        ce = sum(custo[m][e] for m in range(MESES_HISTORICO))
        if ce <= 0:
            continue
        if c in alvo_especial and area != TRIB:
            mg = alvo_especial[c]
        elif ce < 60000 and rnd.random() < 0.05:
            mg = rnd.uniform(-0.22, -0.06)
        else:
            mg = MARGEM_BASE[area] + rnd.uniform(-0.12, 0.12)
        receita = ce / (1 - mg)
        ex = exito_por_eng.get(e, [])
        tot_ex = sum(v for _, v in ex)
        teto = (0.60 if area == TRIB else 0.40) * receita
        esc = min(1.0, teto / tot_ex) if tot_ex else 0
        for me, v in ex:
            if area == TRIB:                      # padrão f: compensação e precatório
                atraso = rnd.randint(6, 12)
            else:
                atraso = rnd.choices([0, 1, 2, 3, 4, 6, 9], [0.10, 0.20, 0.22, 0.18, 0.14, 0.10, 0.06])[0]
            lanca(e, me, atraso, 2, v * esc)
        resto = receita - tot_ex * esc
        if ret:
            mensal = resto / MESES_HISTORICO
            for m in range(MESES_HISTORICO):
                lanca(e, m, rnd.choices([0, 1, 2], [0.82, 0.15, 0.03])[0], 0, mensal * rnd.uniform(0.98, 1.02))
        else:
            # parcelas mensais acompanhando o trabalho executado
            for m in range(MESES_HISTORICO):
                if custo[m][e] > 0:
                    lanca(e, m, rnd.choices([0, 1, 2], [0.7, 0.22, 0.08])[0], 1, resto * custo[m][e] / ce)
    rec = [r for r in rec if r[4] > 0]

    # ------------------------------------------------------------ LGPD
    S = {"j": "Sistema de gestão jurídica", "f": "Financeiro", "p": "Planilhas paralelas",
         "e": "E-mail corporativo", "c": "Pastas compartilhadas", "a": "Agenda e atendimento"}
    B6 = "Art. 7º, VI (exercício regular de direitos)"
    B5 = "Art. 7º, V (execução de contrato)"
    B2 = "Art. 7º, II (obrigação legal)"
    S11 = "Art. 11, II, d (exercício regular de direitos)"
    ND = "Não definida"
    lgpd = [
        [S["j"], "Clientes pessoa física", "Nome, CPF, endereço e contato", 0, B5, "Representação e comunicação com o cliente", "5 anos após o encerramento", -1],
        [S["j"], "Partes contrárias", "Nome, CPF ou CNPJ e endereço", 0, B6, "Condução do processo", "5 anos após o encerramento", -1],
        [S["j"], "Reclamantes", "Atestados e laudos médicos", 1, S11, "Defesa em ação trabalhista", "5 anos após o trânsito em julgado", TRAB],
        [S["j"], "Reclamantes", "Filiação sindical", 1, S11, "Defesa em ação trabalhista", "5 anos após o trânsito em julgado", TRAB],
        [S["c"], "Reclamantes", "Holerites e cartões de ponto", 0, B6, "Cálculo de verbas", "Não definido", TRAB],
        [S["p"], "Testemunhas", "Nome, telefone e endereço", 0, ND, "Controle de audiências", "Não definido", TRAB],
        [S["j"], "Menores envolvidos", "Nome, idade, escola e rotina", 1, S11, "Ações de guarda e alimentos", "5 anos após a maioridade", FAM],
        [S["c"], "Clientes pessoa física", "Declarações de imposto de renda", 0, B6, "Partilha e alimentos", "5 anos após o encerramento", FAM],
        [S["e"], "Clientes pessoa física", "Relatos de saúde e laudos psicológicos", 1, ND, "Instrução de ações de família", "Não definido", FAM],
        [S["j"], "Consumidores autores", "Prontuários e exames", 1, S11, "Defesa em ações de saúde suplementar", "5 anos após o trânsito em julgado", CIV],
        [S["p"], "Devedores", "Nome, CPF e histórico de pagamento", 0, B6, "Cobrança judicial e extrajudicial", "Não definido", CIV],
        [S["c"], "Sócios de clientes", "Documentos pessoais e participação societária", 0, B5, "Atos societários", "5 anos após o encerramento", EMP],
        [S["e"], "Administradores de clientes", "Contato e assinatura digitalizada", 0, B5, "Atos societários e contratos", "Enquanto durar o contrato", EMP],
        [S["j"], "Responsáveis legais de clientes", "Nome e CPF", 0, B2, "Defesa em execução fiscal", "5 anos após o trânsito em julgado", TRIB],
        [S["p"], "Responsáveis legais de clientes", "Dados bancários para compensação", 0, ND, "Acompanhamento de restituições", "Não definido", TRIB],
        [S["f"], "Clientes pessoa física", "CPF, dados bancários e notas emitidas", 0, B2, "Faturamento e obrigações fiscais", "5 anos (legislação tributária)", -1],
        [S["f"], "Colaboradores", "Dados de folha e conta salário", 0, B2, "Folha de pagamento", "Prazos da legislação trabalhista", -1],
        [S["a"], "Interessados e prospectos", "Nome, telefone e assunto da consulta", 0, ND, "Agendamento de atendimento", "Não definido", -1],
        [S["c"], "Colaboradores", "Atestados médicos", 1, S11, "Gestão de afastamentos", "Prazos da legislação trabalhista", -1],
    ]

    return {
        "meta": {"escritorio": ESCRITORIO, "ficticio": True, "referencia": DATA_REFERENCIA.isoformat(),
                 "meses": [f"{y:04d}-{m:02d}" for y, m in MESES], "semente": SEMENTE,
                 "definicoes": {"exito": "procedente, parcialmente procedente ou acordo"}},
        "areas": AREAS, "niveis": NIVEIS, "fases": FASES, "resultados": RESULTADOS,
        "classes": classes_l, "assuntos": assuntos_l,
        "adv": [[n, nv, CUSTO_HORA[nv]] for n, nv, *_ in ADVOGADOS],
        "cli": clientes,
        "eng": [[c, a, r] for c, a, r, *_ in engs],
        "proc": procs, "rec": rec, "ts": ts, "lgpd": lgpd,
    }


def injetar(html_path, dados):
    p = Path(html_path)
    html = p.read_text(encoding="utf-8")
    js = json.dumps(dados, ensure_ascii=False, separators=(",", ":"))
    js = js.replace("</", "<\\/")
    html, n = re.subn(r'(<script id="dados-demo" type="application/json">)(.*?)(</script>)',
                      lambda m: m.group(1) + js + m.group(3), html, flags=re.S)
    if n != 1:
        raise SystemExit("marcador <script id=\"dados-demo\"> não encontrado")
    html = re.sub(r'(<link rel="canonical" href=")[^"]*', lambda m: m.group(1) + CANONICAL_URL, html)
    html = re.sub(r'(<meta property="og:url" content=")[^"]*', lambda m: m.group(1) + CANONICAL_URL, html)
    p.write_text(html, encoding="utf-8")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--html", help="caminho do demo-advocacia.html para injetar os dados")
    ap.add_argument("--json", default=str(Path(__file__).with_name("dados_demo.json")))
    args = ap.parse_args()
    dados = gerar()
    Path(args.json).write_text(json.dumps(dados, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    if args.html:
        injetar(args.html, dados)
    print(f"processos={len(dados['proc'])} clientes={len(dados['cli'])} "
          f"lancamentos_horas={len(dados['ts'])} receitas={len(dados['rec'])}")
