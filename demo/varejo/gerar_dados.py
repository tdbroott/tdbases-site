#!/usr/bin/env python3
"""
Gerador determinístico dos dados sintéticos do painel demonstrativo para
varejo, bares e restaurantes da TDBASES: o restaurante fictício Bistrô Jatobá,
com salão, balcão e retirada e dois aplicativos de delivery (sem marca).

Gera: cardápio com fichas técnicas, preço de insumos por mês, vendas por
item, canal e mês, promoções pagas pelo restaurante, pedidos e receita por
dia da semana e faixa horária, compras e contagens de estoque.

Valores monetários de venda são gravados em centavos inteiros, para que os
totais reconciliem exatamente entre as telas.

Uso: python3 gerar_dados.py  (grava dados.json ao lado)
"""
import json
import math
import random
from datetime import date
from pathlib import Path

SEMENTE = 20261014
DATA_REFERENCIA = date(2026, 9, 30)
MESES = 24
RESTAURANTE = "Bistrô Jatobá"

CANAIS = ["Salão", "Balcão e retirada", "Aplicativo de delivery 1", "Aplicativo de delivery 2"]
FATOR_PRECO = [1.0, 1.0, 1.15, 1.15]
COMISSAO = [0.0, 0.0, 0.23, 0.27]
TAXA_PAG = [0.026, 0.022, 0.032, 0.032]
FAIXAS = ["Almoço (11h às 15h)", "Tarde (15h às 18h)", "Noite (18h às 23h)"]
DIAS = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"]
CATEGORIAS = ["Entradas", "Pratos principais", "Massas e risotos", "Executivos", "Sobremesas", "Bebidas"]
EMBALAGEM = {0: 1.80, 1: 2.90, 2: 2.90, 3: 2.40, 4: 1.50, 5: 0.40}

# nome, unidade, preço inicial, variação total no período (fração), meses finais em que a alta se concentra
INSUMOS = [
    ("Filé mignon", "kg", 72.0, 0.30, 10), ("Contrafilé", "kg", 46.0, 0.12, 24), ("Frango (peito)", "kg", 19.5, 0.06, 24),
    ("Camarão limpo", "kg", 89.0, 0.46, 15), ("Salmão", "kg", 98.0, 0.10, 24), ("Tilápia (filé)", "kg", 42.0, 0.08, 24),
    ("Arroz arbóreo", "kg", 28.0, 0.09, 24), ("Arroz branco", "kg", 6.2, 0.10, 24), ("Feijão", "kg", 8.4, 0.05, 24),
    ("Massa fresca", "kg", 24.0, 0.07, 24), ("Batata", "kg", 5.8, 0.18, 24), ("Cebola", "kg", 5.2, 0.15, 24),
    ("Tomate", "kg", 7.9, 0.22, 24), ("Alho", "kg", 26.0, 0.10, 24), ("Folhas e legumes", "kg", 14.0, 0.12, 24),
    ("Queijo muçarela", "kg", 39.0, 0.10, 24), ("Queijo parmesão", "kg", 92.0, 0.14, 24), ("Creme de leite", "L", 21.0, 0.09, 24),
    ("Manteiga", "kg", 52.0, 0.16, 24), ("Azeite extravirgem", "L", 48.0, 0.36, 14), ("Óleo de soja", "L", 8.2, 0.06, 24),
    ("Farinha de trigo", "kg", 5.4, 0.05, 24), ("Ovos", "un", 0.85, 0.12, 24), ("Leite", "L", 5.6, 0.08, 24),
    ("Chocolate", "kg", 64.0, 0.25, 12), ("Açúcar", "kg", 4.6, 0.04, 24), ("Café", "kg", 58.0, 0.28, 12),
    ("Frutas", "kg", 11.0, 0.10, 24), ("Refrigerante lata", "un", 2.6, 0.08, 24), ("Água mineral", "un", 1.1, 0.06, 24),
    ("Polpa de fruta", "kg", 16.0, 0.09, 24), ("Cerveja long neck", "un", 4.4, 0.10, 24),
]
I = {n[0]: k for k, n in enumerate(INSUMOS)}

# nome, categoria, preço de cardápio inicial, popularidade, ficha técnica [(insumo, quantidade)]
ITENS = [
    ("Bruschetta de tomate", 0, 32.0, 0.9, [("Tomate", 0.12), ("Farinha de trigo", 0.08), ("Azeite extravirgem", 0.02), ("Alho", 0.005)]),
    ("Batata rústica", 0, 34.0, 1.4, [("Batata", 0.45), ("Óleo de soja", 0.08), ("Alho", 0.01)]),
    ("Pastéis de queijo", 0, 36.0, 1.0, [("Farinha de trigo", 0.12), ("Queijo muçarela", 0.10), ("Óleo de soja", 0.06)]),
    ("Carpaccio", 0, 52.0, 0.5, [("Filé mignon", 0.10), ("Queijo parmesão", 0.02), ("Azeite extravirgem", 0.02), ("Folhas e legumes", 0.04)]),
    ("Tábua de frios", 0, 89.0, 0.25, [("Queijo parmesão", 0.12), ("Queijo muçarela", 0.12), ("Azeite extravirgem", 0.02), ("Frutas", 0.1)]),
    ("Salada da casa", 0, 38.0, 0.7, [("Folhas e legumes", 0.25), ("Tomate", 0.08), ("Azeite extravirgem", 0.02), ("Queijo parmesão", 0.015)]),
    ("Filé ao molho madeira", 1, 79.9, 2.6, [("Filé mignon", 0.22), ("Batata", 0.25), ("Arroz branco", 0.12), ("Manteiga", 0.02), ("Cebola", 0.04)]),
    ("Contrafilé com fritas", 1, 64.9, 2.2, [("Contrafilé", 0.28), ("Batata", 0.30), ("Óleo de soja", 0.06), ("Arroz branco", 0.12)]),
    ("Frango grelhado", 1, 46.9, 2.0, [("Frango (peito)", 0.25), ("Arroz branco", 0.14), ("Feijão", 0.1), ("Folhas e legumes", 0.08)]),
    ("Salmão com legumes", 1, 89.9, 1.0, [("Salmão", 0.22), ("Folhas e legumes", 0.18), ("Azeite extravirgem", 0.02), ("Manteiga", 0.015)]),
    ("Tilápia ao limão", 1, 59.9, 1.0, [("Tilápia (filé)", 0.25), ("Arroz branco", 0.12), ("Folhas e legumes", 0.1), ("Manteiga", 0.015)]),
    ("Moqueca de camarão", 1, 98.0, 0.9, [("Camarão limpo", 0.32), ("Tomate", 0.12), ("Cebola", 0.08), ("Azeite extravirgem", 0.03), ("Arroz branco", 0.12)]),
    ("Picadinho da casa", 1, 54.9, 1.3, [("Contrafilé", 0.20), ("Arroz branco", 0.12), ("Feijão", 0.1), ("Ovos", 1), ("Batata", 0.1)]),
    ("Parmegiana de frango", 1, 58.9, 1.8, [("Frango (peito)", 0.25), ("Queijo muçarela", 0.10), ("Tomate", 0.1), ("Farinha de trigo", 0.05), ("Arroz branco", 0.12), ("Batata", 0.2)]),
    ("Risoto de camarão", 2, 86.0, 1.2, [("Camarão limpo", 0.24), ("Arroz arbóreo", 0.12), ("Manteiga", 0.03), ("Queijo parmesão", 0.03), ("Creme de leite", 0.05)]),
    ("Risoto de cogumelos", 2, 68.0, 0.8, [("Arroz arbóreo", 0.12), ("Folhas e legumes", 0.12), ("Manteiga", 0.03), ("Queijo parmesão", 0.04)]),
    ("Talharim ao sugo", 2, 44.0, 1.1, [("Massa fresca", 0.20), ("Tomate", 0.18), ("Azeite extravirgem", 0.015), ("Queijo parmesão", 0.015)]),
    ("Talharim com filé", 2, 69.0, 1.3, [("Massa fresca", 0.20), ("Filé mignon", 0.14), ("Creme de leite", 0.08), ("Queijo parmesão", 0.02)]),
    ("Nhoque ao molho branco", 2, 49.0, 0.7, [("Batata", 0.3), ("Farinha de trigo", 0.08), ("Creme de leite", 0.1), ("Queijo parmesão", 0.02)]),
    ("Lasanha bolonhesa", 2, 56.0, 1.1, [("Massa fresca", 0.15), ("Contrafilé", 0.12), ("Queijo muçarela", 0.10), ("Tomate", 0.12)]),
    ("Executivo de frango", 3, 32.9, 2.4, [("Frango (peito)", 0.18), ("Arroz branco", 0.14), ("Feijão", 0.12), ("Folhas e legumes", 0.06)]),
    ("Executivo de carne", 3, 37.9, 2.2, [("Contrafilé", 0.18), ("Arroz branco", 0.14), ("Feijão", 0.12), ("Batata", 0.12)]),
    ("Executivo de peixe", 3, 36.9, 1.1, [("Tilápia (filé)", 0.18), ("Arroz branco", 0.14), ("Feijão", 0.12), ("Folhas e legumes", 0.06)]),
    ("Executivo vegetariano", 3, 30.9, 0.7, [("Folhas e legumes", 0.22), ("Arroz branco", 0.14), ("Feijão", 0.12), ("Ovos", 1)]),
    ("Petit gâteau", 4, 34.0, 1.3, [("Chocolate", 0.06), ("Manteiga", 0.03), ("Ovos", 2), ("Açúcar", 0.03), ("Farinha de trigo", 0.02)]),
    ("Pudim", 4, 22.0, 1.1, [("Leite", 0.2), ("Ovos", 2), ("Açúcar", 0.06)]),
    ("Mousse de chocolate", 4, 24.0, 0.8, [("Chocolate", 0.05), ("Creme de leite", 0.06), ("Açúcar", 0.02)]),
    ("Salada de frutas", 4, 19.0, 0.5, [("Frutas", 0.3), ("Açúcar", 0.01)]),
    ("Torta de limão", 4, 23.0, 0.6, [("Farinha de trigo", 0.04), ("Manteiga", 0.03), ("Leite", 0.08), ("Ovos", 1), ("Frutas", 0.05)]),
    ("Refrigerante", 5, 7.5, 3.0, [("Refrigerante lata", 1)]),
    ("Água mineral", 5, 5.5, 2.0, [("Água mineral", 1)]),
    ("Suco natural", 5, 12.0, 2.0, [("Polpa de fruta", 0.12), ("Açúcar", 0.02)]),
    ("Café expresso", 5, 7.0, 2.2, [("Café", 0.009)]),
    ("Cerveja long neck", 5, 14.0, 1.6, [("Cerveja long neck", 1)]),
    ("Limonada", 5, 11.0, 1.0, [("Frutas", 0.15), ("Açúcar", 0.03)]),
]
SO_SALAO = {"Tábua de frios", "Café expresso"}
NIVEL_PRECO = 1.35         # nível geral de preço dos insumos em relação à tabela acima
REVISAO_PRECO = 9          # índice do mês da única revisão de cardápio no histórico
AJUSTE_REVISAO = 1.06
# promoções pagas pelo restaurante no aplicativo 2: item, mês inicial, taxa de desconto
PROMOS = [("Risoto de camarão", 10, 0.25), ("Moqueca de camarão", 11, 0.25), ("Filé ao molho madeira", 16, 0.15),
          ("Parmegiana de frango", 6, 0.15), ("Lasanha bolonhesa", 18, 0.12)]
DIVERGENCIA = {"Filé mignon": 0.095, "Camarão limpo": 0.065, "Cerveja long neck": 0.04, "Queijo parmesão": 0.035}


def meses():
    out, y, m = [], DATA_REFERENCIA.year, DATA_REFERENCIA.month
    for _ in range(MESES):
        out.append((y, m))
        m -= 1
        if m == 0:
            y, m = y - 1, 12
    return list(reversed(out))


def centavos(v):
    return int(math.floor(v * 100 + 0.5))


def gerar():
    rnd = random.Random(SEMENTE)
    MS = meses()

    # preço dos insumos por mês
    preco_ins = []
    for nome, un, p0, var, janela in INSUMOS:
        serie = []
        for m in range(MESES):
            ini = MESES - janela
            prog = 0 if m < ini else (m - ini + 1) / janela
            p = p0 * NIVEL_PRECO * (1 + var * prog) * (1 + rnd.uniform(-0.015, 0.015))
            serie.append(round(p, 2))
        preco_ins.append(serie)

    # preço de cardápio no salão, em centavos, por mês
    preco = []
    for nome, cat, p0, pop, ficha in ITENS:
        novo = math.floor(p0 * AJUSTE_REVISAO) + 0.9
        preco.append([centavos(novo if m >= REVISAO_PRECO else p0) for m in range(MESES)])
    # preço por canal: arredondado para terminar em ,90 nos aplicativos
    def preco_canal(it, c, m):
        p = preco[it][m]
        if FATOR_PRECO[c] == 1.0:
            return p
        v = p * FATOR_PRECO[c] / 100
        return centavos(math.floor(v) + 0.9)

    # custo unitário pela ficha técnica, por mês
    custo = []
    for nome, cat, p0, pop, ficha in ITENS:
        custo.append([round(sum(q * preco_ins[I[ins]][m] for ins, q in ficha), 2) for m in range(MESES)])

    # vendas por item, canal e mês
    saz = [0.93, 0.88, 0.96, 0.97, 1.0, 0.98, 1.02, 1.0, 0.98, 1.02, 1.04, 1.18]
    base_canal = [1.0, 0.42, 0.34, 0.20]
    Q = []
    for it, (nome, cat, p0, pop, ficha) in enumerate(ITENS):
        porC = []
        for c in range(4):
            linha = []
            for m, (y, mo) in enumerate(MS):
                if c > 0 and nome in SO_SALAO:
                    linha.append(0)
                    continue
                share = base_canal[c]
                if c == 3:
                    share *= 1 + 0.045 * m          # aplicativo 2 crescendo
                if c == 2:
                    share *= 1 + 0.012 * m
                if cat == 3:
                    share *= [1.0, 1.25, 0.0, 0.0][c]  # executivo só no almoço, salão e balcão
                if cat == 0 and c >= 2:
                    share *= 0.6
                if cat == 5 and c >= 2:
                    share *= 0.75
                promo = next((p for p in PROMOS if p[0] == nome and c == 3 and m >= p[1]), None)
                if promo:
                    share *= 1.7
                q = 34 * pop * share * saz[mo - 1] * (1 + 0.004 * m) * rnd.uniform(0.9, 1.1) * 2.8
                linha.append(int(round(q)))
            porC.append(linha)
        Q.append(porC)
    P = [[[preco_canal(it, c, m) for m in range(MESES)] for c in range(4)] for it in range(len(ITENS))]
    promo = []
    for nome, m0, taxa in PROMOS:
        it = next(k for k, x in enumerate(ITENS) if x[0] == nome)
        for m in range(m0, MESES):
            bruto = Q[it][3][m] * P[it][3][m]
            promo.append([it, 3, m, int(round(bruto * taxa))])

    # pedidos e receita por dia da semana e faixa horária (receita em centavos)
    peso_dia = {0: [0.9, 0.95, 1.0, 1.05, 1.25, 1.45, 1.2], 1: [1.1, 1.1, 1.1, 1.1, 1.15, 0.8, 0.6],
                2: [0.8, 0.85, 0.9, 1.0, 1.3, 1.45, 1.4], 3: [0.8, 0.85, 0.9, 1.0, 1.3, 1.45, 1.4]}
    peso_faixa = {0: [0.48, 0.07, 0.45], 1: [0.62, 0.12, 0.26], 2: [0.28, 0.12, 0.60], 3: [0.25, 0.12, 0.63]}
    ticket_base = {0: [78, 46, 122], 1: [41, 30, 52], 2: [64, 48, 76], 3: [61, 45, 72]}
    desc = {}
    for it, c, m, v in promo:
        desc[(c, m)] = desc.get((c, m), 0) + v
    cel = []
    for m in range(MESES):
        porC = []
        for c in range(4):
            receita = sum(Q[it][c][m] * P[it][c][m] for it in range(len(ITENS))) - desc.get((c, m), 0)
            pesos = [peso_dia[c][d] * peso_faixa[c][f] * rnd.uniform(0.92, 1.08) for d in range(7) for f in range(3)]
            s = sum(pesos)
            partes = [int(receita * w / s) for w in pesos]
            partes[-1] += receita - sum(partes)
            ped = []
            for k, rv in enumerate(partes):
                f = k % 3
                t = ticket_base[c][f] * (1.03 if k // 3 >= 4 else 1.0) * rnd.uniform(0.94, 1.06) * (1 + 0.003 * m)
                ped.append(max(1, int(round(rv / 100 / t))))
            porC.append([partes, ped])
        cel.append(porC)

    # estoque: consumo teórico pela ficha, divergência plantada, compras e contagem final
    teor = [[0.0] * MESES for _ in INSUMOS]
    for it, (nome, cat, p0, pop, ficha) in enumerate(ITENS):
        for m in range(MESES):
            q = sum(Q[it][c][m] for c in range(4))
            for ins, qt in ficha:
                teor[I[ins]][m] += q * qt
    comp, ef, ei0 = [], [], []
    for k, (nome, un, *_r) in enumerate(INSUMOS):
        div = DIVERGENCIA.get(nome, rnd.uniform(0.004, 0.018))
        estoque = teor[k][0] * 0.35
        ei0.append(round(estoque, 3))
        cl, el = [], []
        for m in range(MESES):
            real = teor[k][m] * (1 + div * rnd.uniform(0.8, 1.2))
            alvo = teor[k][m] * rnd.uniform(0.28, 0.42)
            compra = max(0.0, real + alvo - estoque)
            final = estoque + compra - real
            cl.append(round(compra, 3))
            el.append(round(final, 3))
            estoque = final
        comp.append(cl)
        ef.append(el)

    return {
        "meta": {"restaurante": RESTAURANTE, "ficticio": True, "referencia": DATA_REFERENCIA.isoformat(),
                 "meses": [f"{y:04d}-{m:02d}" for y, m in MS], "semente": SEMENTE, "revisao_preco": REVISAO_PRECO},
        "canais": CANAIS, "comissao": COMISSAO, "taxa_pag": TAXA_PAG, "faixas": FAIXAS, "dias": DIAS,
        "categorias": CATEGORIAS, "embalagem": [EMBALAGEM[k] for k in range(6)],
        "itens": [[n, c] for n, c, *_r in ITENS],
        "ficha": [[[I[ins], q] for ins, q in f] for *_r, f in ITENS],
        "insumos": [[n, u] for n, u, *_r in INSUMOS], "preco_ins": preco_ins,
        "custo": custo, "Q": Q, "P": P, "promo": promo, "cel": cel,
        "ei0": ei0, "compras": comp, "ef": ef,
    }


if __name__ == "__main__":
    d = gerar()
    Path(__file__).with_name("dados.json").write_text(json.dumps(d, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print("itens", len(d["itens"]), "insumos", len(d["insumos"]))
