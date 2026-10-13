#!/usr/bin/env python3
"""
Gerador determinístico dos dados sintéticos do painel demonstrativo para
contabilidade da TDBASES: o escritório fictício Pereira Lins Contabilidade e
sua carteira de 40 empresas clientes, também fictícias.

Gera, por empresa e mês:
  DRE gerencial por competência, fluxo de caixa realizado com defasagens
  (prazo de recebimento, de pagamento, folha, 13º salário, impostos),
  estatísticas de conciliação bancária e a fila de pendências na data de
  referência.

Uso: python3 gerar_dados.py  (grava dados.json ao lado)
Nenhum registro representa empresa, pessoa ou banco real.
"""
import json
import math
import random
from datetime import date, timedelta
from pathlib import Path

SEMENTE = 20261013
DATA_REFERENCIA = date(2026, 9, 30)
MESES = 24
AQUECIMENTO = 4                       # meses anteriores usados só para as defasagens de caixa
ESCRITORIO = "Pereira Lins Contabilidade"
MINUTOS_POR_LINHA = 1.5               # premissa de conferência manual, exibida no painel

SEGMENTOS = ["Comércio", "Serviços", "Indústria", "Alimentação"]
REGIMES = ["Simples Nacional", "Lucro Presumido", "Lucro Real"]
FAIXAS_SIMPLES = [180000, 360000, 720000, 1800000, 3600000, 4800000]
MOTIVOS = ["Entrada sem nota fiscal correspondente", "Pagamento sem documento fiscal",
           "Divergência de valor", "Data fora da janela de conciliação", "Possível duplicidade"]
REGRAS = ["Valor e data", "Chave da nota fiscal", "Recorrência"]
LINHAS_DRE = ["RB", "DED", "CUS", "PES", "OCU", "COM", "ADM", "DEP", "RF", "IR"]
LINHAS_CX = ["REC", "FOR", "IMP", "PES", "DES", "FIN", "INV", "EMP"]

# custo direto sobre a receita bruta, por segmento
CUSTO = {0: (0.56, 0.64), 1: (0.26, 0.38), 2: (0.46, 0.54), 3: (0.34, 0.40)}
LINHAS_POR_REAL = {0: 1 / 1100, 1: 1 / 2600, 2: 1 / 3800, 3: 1 / 520}
DESC_ENTRADA = ["PIX recebido", "TED recebida", "Boleto liquidado", "Liquidação de cartão", "Depósito"]
DESC_SAIDA = ["PIX enviado", "Boleto pago", "Débito automático", "TED enviada", "Tarifa bancária", "Transferência entre contas"]


def lista_meses():
    out, y, m = [], DATA_REFERENCIA.year, DATA_REFERENCIA.month
    for _ in range(MESES + AQUECIMENTO):
        out.append((y, m))
        m -= 1
        if m == 0:
            y, m = y - 1, 12
    return list(reversed(out))


def distrib(mu, nmax=4):
    """Distribuição discreta de defasagem em meses com média aproximada mu."""
    w = [math.exp(-((k - mu) ** 2) / 0.55) for k in range(nmax + 1)]
    s = sum(w)
    return [x / s for x in w]


def gerar():
    rnd = random.Random(SEMENTE)
    MS = lista_meses()
    T = len(MS)
    H0 = AQUECIMENTO                       # índice do primeiro mês publicado

    # ------------------------------------------------------------ empresas
    especiais = {
        "Alimentação 03": dict(seg=3, reg=0, rb=148000, margem_cai=True),
        "Comércio 11": dict(seg=0, reg=1, rb=520000, margem_cai=True),
        "Indústria 04": dict(seg=2, reg=2, rb=1350000, prazo_alonga=True),
        "Comércio 07": dict(seg=0, reg=0, rb=338000, perto_faixa=4800000 * 0.962),
        "Serviços 05": dict(seg=1, reg=0, rb=55500, perto_faixa=720000 * 0.951),
        "Alimentação 08": dict(seg=3, reg=0, rb=142000, perto_faixa=1800000 * 0.934),
        "Comércio 02": dict(seg=0, reg=0, rb=96000, excecao=0, atraso=True),
        "Alimentação 06": dict(seg=3, reg=0, rb=118000, excecao=0, atraso=True),
        "Serviços 09": dict(seg=1, reg=1, rb=210000, excecao=1, atraso=True),
    }
    cont = {s: 0 for s in range(4)}
    usados = set(especiais)
    empresas = []
    alvo_seg = [13, 12, 6, 9]
    for s in range(4):
        while sum(1 for e in empresas if e["seg"] == s) + sum(1 for k, v in especiais.items() if v["seg"] == s) < alvo_seg[s]:
            cont[s] += 1
            nome = f"{SEGMENTOS[s]} {cont[s]:02d}"
            if nome in usados:
                continue
            usados.add(nome)
            porte = rnd.random()
            rb = math.exp(rnd.uniform(math.log(38000), math.log(900000)))
            if s == 2:
                rb *= 1.6
            reg = 0 if rb < 260000 else (1 if rb < 1100000 or rnd.random() < 0.4 else 2)
            if reg == 0 and rb * 12 * 1.05 > 4800000:
                rb = 4800000 / 12 / 1.3
            empresas.append(dict(nome=nome, seg=s, reg=reg, rb=rb))
    for nome, e in especiais.items():
        empresas.append(dict(nome=nome, **e))
    empresas.sort(key=lambda e: (e["seg"], e["nome"]))

    # ------------------------------------------------------------ séries mensais
    sazon = {0: [0.92, 0.86, 0.95, 0.96, 1.0, 0.97, 0.98, 1.0, 0.99, 1.02, 1.12, 1.33],
             1: [0.90, 0.95, 1.02, 1.0, 1.02, 1.0, 1.0, 1.03, 1.02, 1.03, 1.02, 0.98],
             2: [0.88, 0.94, 1.03, 1.0, 1.04, 1.02, 1.03, 1.05, 1.04, 1.03, 1.0, 0.92],
             3: [1.02, 0.94, 0.98, 0.97, 1.0, 0.97, 1.04, 1.0, 0.98, 1.0, 1.03, 1.16]}
    out_emp, dre, cx, saldo_ini, conc, atraso, pend = [], [], [], [], [], [], []
    for ei, e in enumerate(empresas):
        s, reg = e["seg"], e["reg"]
        base = e["rb"]
        cresc = rnd.uniform(-0.002, 0.012)
        if e.get("perto_faixa"):
            cresc = 0.006
        c_lo, c_hi = CUSTO[s]
        custo_base = rnd.uniform(c_lo, c_hi)
        aliq = {0: rnd.uniform(0.062, 0.10), 1: rnd.uniform(0.095, 0.135), 2: rnd.uniform(0.15, 0.19)}[reg]
        if s == 1 and reg == 0:
            aliq = rnd.uniform(0.06, 0.09)
        salario = base * {0: 0.09, 1: 0.36, 2: 0.13, 3: 0.27}[s] * rnd.uniform(0.85, 1.15) / 1.394
        aluguel = base * rnd.uniform(0.025, 0.06)
        com_pct = {0: 0.04, 1: 0.03, 2: 0.025, 3: 0.05}[s] * rnd.uniform(0.7, 1.3)
        adm_fixo = base * rnd.uniform(0.02, 0.045)
        dep = base * rnd.uniform(0.004, 0.015) * (2.2 if s == 2 else 1)
        divida = base * rnd.uniform(0, 1.6) if rnd.random() < 0.55 else 0
        pmr = {0: 24, 1: 32, 2: 42, 3: 9}[s] * rnd.uniform(0.7, 1.3)
        pmp = {0: 36, 1: 20, 2: 40, 3: 24}[s] * rnd.uniform(0.75, 1.25)
        cobertura = {0: 1.3, 1: 0.0, 2: 1.1, 3: 0.25}[s] * rnd.uniform(0.8, 1.2)

        L = {k: [0.0] * T for k in LINHAS_DRE}
        S = [0.0] * T
        estoque = [0.0] * T
        pmr_t, cob_t = [pmr] * T, [cobertura] * T
        for t, (y, mo) in enumerate(MS):
            idade = t - (T - 1)               # 0 no mês de referência
            rb = base * sazon[s][mo - 1] * (1 + cresc) ** t * rnd.uniform(0.95, 1.05)
            cus = custo_base
            if e.get("margem_cai") and idade > -7:
                cus = custo_base + (idade + 7) * 0.013          # até +8 p.p. nos últimos 6 meses
            if e.get("prazo_alonga") and idade > -10:
                pmr_t[t] = pmr + (idade + 10) * 5.5
                cob_t[t] = cobertura + (idade + 10) * 0.09
            sal = salario * (1.055 if t >= T - 12 + 4 else 1.0)  # dissídio em maio do último ano
            S[t] = sal
            L["RB"][t] = rb
            L["DED"][t] = rb * aliq + (rb * rnd.uniform(0.004, 0.018) if s in (0, 3) else 0)
            L["CUS"][t] = rb * cus * rnd.uniform(0.98, 1.02)
            L["PES"][t] = sal * 1.394
            L["OCU"][t] = aluguel * (1.04 if t >= T - 8 else 1.0)
            L["COM"][t] = rb * com_pct
            L["ADM"][t] = adm_fixo * rnd.uniform(0.9, 1.1) + rb * 0.006
            L["DEP"][t] = dep
            juros = -divida * 0.0145 if divida else 0
            L["RF"][t] = juros + base * rnd.uniform(0.0, 0.002)
            lair = rb - L["DED"][t] - L["CUS"][t] - L["PES"][t] - L["OCU"][t] - L["COM"][t] - L["ADM"][t] - dep + L["RF"][t]
            if reg == 1:
                L["IR"][t] = rb * (0.0593 if s == 1 else 0.0228)
            elif reg == 2:
                L["IR"][t] = max(0.0, lair) * 0.34
            estoque[t] = L["CUS"][t] * cob_t[t]

        # caixa com defasagens
        C = {k: [0.0] * T for k in LINHAS_CX}
        for t in range(T):
            d_rec = distrib(pmr_t[t] / 30)
            for k, w in enumerate(d_rec):
                if t + k < T:
                    C["REC"][t + k] += L["RB"][t] * w
            compra = L["CUS"][t] + (estoque[t] - (estoque[t - 1] if t else estoque[t]))
            for k, w in enumerate(distrib(pmp / 30)):
                if t + k < T:
                    C["FOR"][t + k] -= compra * w
            if t + 1 < T:
                C["IMP"][t + 1] -= L["DED"][t] + L["IR"][t]
                C["PES"][t + 1] -= S[t] * 1.20
            C["PES"][t] -= S[t] * 0.111                       # férias pagas ao longo do ano
            mo = MS[t][1]
            if mo == 11:
                C["PES"][t] -= S[t] * 0.5                      # 1ª parcela do 13º
            if mo == 12:
                C["PES"][t] -= S[t] * 0.5
            demais = L["OCU"][t] + L["COM"][t] + L["ADM"][t]
            C["DES"][t] -= demais * 0.9
            if t + 1 < T:
                C["DES"][t + 1] -= demais * 0.1
            C["FIN"][t] = L["RF"][t]
            if divida:
                C["EMP"][t] -= divida / 36
        for _ in range(rnd.randint(0, 2)):
            C["INV"][rnd.randrange(H0, T)] -= base * rnd.uniform(0.15, 0.6)
        if e.get("prazo_alonga"):
            C["INV"][T - 7] -= base * 0.55
            C["EMP"][T - 4] += base * 0.9

        # empresas do Simples posicionadas perto de uma faixa de receita bruta acumulada (RBT12)
        if e.get("perto_faixa"):
            f = e["perto_faixa"] / sum(L["RB"][T - 12:])
            for k in LINHAS_DRE:
                L[k] = [v * f for v in L[k]]
            for k in LINHAS_CX:
                C[k] = [v * f for v in C[k]]
            base *= f

        # inteiros e recorte do histórico publicado
        Li = {k: [int(round(v)) for v in L[k][H0:]] for k in LINHAS_DRE}
        Ci = {k: [int(round(v)) for v in C[k][H0:]] for k in LINHAS_CX}
        dre.append([Li[k] for k in LINHAS_DRE])
        cx.append([Ci[k] for k in LINHAS_CX])
        saldo_ini.append(int(round(base * rnd.uniform(0.25, 0.8), -2)))

        # ------------------------------------------------------- conciliação
        prob = e.get("excecao")
        cm, at = [], []
        for t in range(H0, T):
            m = t - H0
            n = int(max(60, min(1150, L["RB"][t] * LINHAS_POR_REAL[s] * rnd.uniform(0.9, 1.1))))
            taxa_exc = rnd.uniform(0.015, 0.035) if prob is None else rnd.uniform(0.15, 0.19)
            exc_tot = max(1, int(round(n * taxa_exc)))
            pesos = [0.22, 0.2, 0.26, 0.2, 0.12]
            if prob is not None:
                pesos = [0.08] * 5
                pesos[prob] = 0.68
            exc = [0] * 5
            for _ in range(exc_tot):
                exc[rnd.choices(range(5), pesos)[0]] += 1
            taxa_auto = min(0.95, 0.83 + 0.0035 * m + rnd.uniform(-0.015, 0.015)) - (0.06 if prob is not None else 0)
            auto = int(n * taxa_auto)
            auto = min(auto, n - exc_tot)
            a1 = int(auto * 0.55)
            a2 = int(auto * 0.30)
            a3 = auto - a1 - a2
            manual = n - auto - exc_tot
            cm.append([n, a1, a2, a3, manual] + exc)
            at.append(rnd.randint(9, 19) if e.get("atraso") and m >= MESES - 4 else rnd.choice([0, 0, 0, 0, 0, 1, 2, 3, 4]))
        conc.append(cm)
        atraso.append(at)

        # pendências abertas na data de referência
        frac = {0: 0.40, 1: 0.10, 2: 0.02}
        for back in range(0, 4):
            m = MESES - 1 - back
            f = frac.get(back, 0.0)
            if prob is not None:
                f = {0: 0.9, 1: 0.65, 2: 0.45, 3: 0.3}[back]
            y, mo = MS[H0 + m]
            ult = (date(y + (mo == 12), mo % 12 + 1, 1) - timedelta(days=1)).day
            for mot in range(5):
                k = int(round(cm[m][5 + mot] * f))
                for _ in range(k):
                    dia = rnd.randint(1, ult)
                    dt = date(y, mo, dia)
                    entrada = mot in (0,) or (mot in (2, 3, 4) and rnd.random() < 0.5)
                    desc = rnd.choice(DESC_ENTRADA if entrada else DESC_SAIDA)
                    if mot == 4:
                        desc = desc + " (repetido)"
                    v = round(math.exp(rnd.gauss(math.log(L["RB"][H0 + m] / max(60, n) * 1.4), 0.9)), 2)
                    v = max(12.0, min(v, 180000.0))
                    pend.append([ei, dt.isoformat(), desc, round(v if entrada else -v, 2), mot])
        out_emp.append([e["nome"], s, reg])
    pend.sort(key=lambda r: (r[1], r[0]))

    return {
        "meta": {"escritorio": ESCRITORIO, "ficticio": True, "referencia": DATA_REFERENCIA.isoformat(),
                 "meses": [f"{y:04d}-{m:02d}" for y, m in MS[H0:]], "semente": SEMENTE,
                 "minutos_por_linha": MINUTOS_POR_LINHA, "faixas_simples": FAIXAS_SIMPLES},
        "segmentos": SEGMENTOS, "regimes": REGIMES, "motivos": MOTIVOS, "regras": REGRAS,
        "linhas_dre": LINHAS_DRE, "linhas_cx": LINHAS_CX,
        "emp": out_emp, "saldo_ini": saldo_ini, "dre": dre, "cx": cx, "conc": conc, "atraso": atraso, "pend": pend,
    }


if __name__ == "__main__":
    d = gerar()
    Path(__file__).with_name("dados.json").write_text(json.dumps(d, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(f"empresas={len(d['emp'])} pendencias={len(d['pend'])}")
