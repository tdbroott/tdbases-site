#!/usr/bin/env python3
"""
Verificação automatizada das demonstrações da TDBASES.

Uso: python3 demo/verificar_demos.py
Requer: playwright para Python, com Chromium.

Para cada painel (advocacia, contabilidade, varejo):
  reconciliação de totais entre telas em todas as combinações de período e
  em amostras dos demais filtros, recálculo independente em Python, ausência
  de NaN, undefined, null e Infinity no texto renderizado, descrição textual
  nos gráficos, abas por teclado e tempo de resposta dos filtros.
Para o exemplo de relatório do Raio-X: coerência dos volumes com os dados do
painel de advocacia.
Para todas as páginas novas e alteradas: termos de marca, travessões,
emojis, recursos remotos, armazenamento no navegador, peso, chamadas de rede,
erros de JavaScript, links internos e rolagem horizontal em 375 e 1280 px.
"""
import json
import re
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

RAIZ = Path(__file__).resolve().parent.parent
MARCAS = ["Astrea", "EasyJur", "Projuris", "Legal One", "SAJ", "iFood", "Rappi", "Power BI", "Tableau",
          "Excel", "Google Sheets", "Looker", "Nubank", "Itaú", "Bradesco", "Santander", "Caixa Econômica"]
DEMOS = ["demo-advocacia.html", "demo-contabilidade.html", "demo-varejo.html", "demo-raio-x.html"]
SITE = ["demos.html", "index.html", "advocacia.html", "contabilidade.html", "varejo-food-service.html", "contato.html", "sobre.html"]
oks, falhas = [], []


def ok(cond, msg):
    (oks if cond else falhas).append(msg)


def dados(html):
    m = re.search(r'<script id="dados-demo" type="application/json">(.*?)</script>', html, re.S)
    return json.loads(m.group(1).replace("<\\/", "</")) if m and m.group(1).strip() else None, (m.group(1) if m else "")


# ------------------------------------------------------------------ textos e peso
textos = {n: (RAIZ / n).read_text(encoding="utf-8") for n in DEMOS + ["demos.html"]}
for p in sorted((RAIZ / "demo").rglob("*")):
    if p.name == "verificar_demos.py":
        continue
    if p.suffix in (".md", ".py", ".js", ".css", ".html"):
        textos[str(p.relative_to(RAIZ))] = p.read_text(encoding="utf-8")
# a página de demonstrações herda o aviso de marcas do rodapé do site; verifica-se só o conteúdo principal
textos["demos.html"] = re.sub(r'<footer class="site-foot">.*?</footer>', "", textos["demos.html"], flags=re.S)
for nome, t in textos.items():
    achou = [mk for mk in MARCAS if re.search(r"(?<![\w-])" + re.escape(mk) + r"(?![\w-])", t)]
    ok(not achou, f"{nome}: sem termo de marca" + (f" (encontrado: {achou})" if achou else ""))
    ok("—" not in t and "–" not in t, f"{nome}: sem travessão nem meia-risca")
    ok(not re.findall(r"[\U0001F300-\U0001FAFF☀-➿]", t), f"{nome}: sem emojis")
for n in DEMOS:
    h = textos[n]
    _, bruto = dados(h)
    sem = len(h.encode()) - len(bruto.encode())
    ok(sem < 300 * 1024, f"{n}: {sem / 1024:.1f} KB sem os dados (limite 300 KB), {len(h.encode()) / 1024:.1f} KB no total")
    remoto = re.search(r'<script[^>]+src="https?://|<link[^>]+rel="(stylesheet|preload|preconnect)"[^>]*href="https?://|@import|url\(https?://', h)
    ok(not remoto, f"{n}: nenhum script, estilo ou fonte remota")
    ok(not re.search(r"localStorage|sessionStorage|indexedDB|document\.cookie", h), f"{n}: sem armazenamento no navegador")

# ------------------------------------------------------------------ dados em Python
DA = dados(textos["demo-advocacia.html"])[0]
DC = dados(textos["demo-contabilidade.html"])[0]
DV = dados(textos["demo-varejo.html"])[0]


def per_meses(pid, nm):
    L = nm - 1
    if pid.endswith("m"):
        return set(range(L - int(pid[:-1]) + 1, L + 1))
    if pid == "mes":
        return {L}
    return None


def py_contab(pid, seg, emp, meses_lista):
    ms = per_meses(pid, len(meses_lista)) or {i for i, m in enumerate(meses_lista) if m.startswith(pid)}
    E = [i for i, e in enumerate(DC["emp"]) if (i == emp if emp >= 0 else (seg < 0 or e[1] == seg))]
    rb = sum(DC["dre"][i][0][m] for i in E for m in ms)
    ll = sum(DC["dre"][i][0][m] - sum(DC["dre"][i][j][m] for j in (1, 2, 3, 4, 5, 6, 7)) + DC["dre"][i][8][m] - DC["dre"][i][9][m] for i in E for m in ms)
    op = sum(DC["cx"][i][j][m] for i in E for j in range(6) for m in ms)
    pend = sum(1 for p in DC["pend"] if p[0] in E)
    return dict(RB=rb, LL=ll, op=op, pend=pend)


def py_varejo(pid, canal, cat):
    nm = len(DV["meta"]["meses"])
    ms = per_meses(pid, nm) or {i for i, m in enumerate(DV["meta"]["meses"]) if m.startswith(pid)}
    promo = {(p[0], p[1], p[2]): p[3] for p in DV["promo"]}
    net = cmv = 0
    for it, (nome, c_) in enumerate(DV["itens"]):
        if cat >= 0 and c_ != cat:
            continue
        for c in range(4):
            if canal >= 0 and c != canal:
                continue
            for m in ms:
                q = DV["Q"][it][c][m]
                net += q * DV["P"][it][c][m] - promo.get((it, c, m), 0)
                cmv += q * round(DV["custo"][it][m] * 100)
    ped = sum(DV["cel"][m][c][1][k] for m in ms for c in range(4) if canal < 0 or c == canal for k in range(21))
    return dict(net=net, cmv=cmv, ped=ped)


def py_advoc(pid, area, adv):
    nm = len(DA["meta"]["meses"])
    ms = per_meses(pid, nm) or {i for i, m in enumerate(DA["meta"]["meses"]) if m.startswith(pid)}
    inE = [(area < 0 or e[1] == area) and (adv < 0 or e[2] == adv) for e in DA["eng"]]
    rec = sum(r[4] for r in DA["rec"] if inE[r[0]] and r[2] >= 0 and r[2] in ms)
    cost = sum(t[3] * DA["adv"][t[1]][2] for t in DA["ts"] if inE[t[2]] and t[0] in ms)
    return dict(rec=rec, cost=cost)


JS = {
 "demo-advocacia.html": r"""(f)=>{var M=DEMO.calcular(f),s=a=>a.reduce((x,y)=>x+y,0),E=1e-6,err=[];
  var cR=s(M.cliOrd.map(c=>M.cli.rec[c])),cC=s(M.cliOrd.map(c=>M.cli.cost[c]));
  if(Math.abs(s(M.area.rec)-M.rec)>E||Math.abs(cR-M.rec)>E||Math.abs(s(M.mes.cx)-M.rec)>E)err.push('recebido');
  if(Math.abs(s(M.area.cost)-M.cost)>E||Math.abs(cC-M.cost)>E||Math.abs(s(M.adv.cost)-M.cost)>E)err.push('custo');
  if(Math.abs(s(M.adv.h)-M.h)>E||Math.abs(s(M.area.h)-M.h)>E)err.push('horas');
  if(Math.abs(s(M.area.comp)-M.comp)>E||Math.abs(s(M.mes.comp)-M.comp)>E)err.push('competência');
  if(M.rec>0&&Math.abs(M.pareto[M.pareto.length-1]-1)>1e-9)err.push('pareto');
  var ag=0;M.ag.forEach(r=>ag+=s(r));var fa=0;M.fase.forEach(r=>fa+=s(r));if(ag!==fa||ag!==s(M.adv.ativos))err.push('carteira');
  if(s(M.ex.n)!==M.exN||s(M.adv.enc)!==M.exN)err.push('encerrados');
  return {err:err,v:{rec:M.rec,cost:M.cost}};}""",
 "demo-contabilidade.html": r"""(f)=>{var M=DEMO.calcular(f),s=a=>a.reduce((x,y)=>x+y,0),err=[],t=M.tot,c=M.cx;
  ['RB','DED','CUS','PES','LL','RL','LB'].forEach(k=>{if(s(M.emp.map(i=>M.porEmp[i].d[k]))!==t[k])err.push('soma por empresa '+k);});
  if(s(M.emp.map(i=>M.porEmp[i].op))!==M.op)err.push('caixa por empresa');
  var ponte=t.LL+t.DEP+(c[0]-t.RB)+(t.CUS+c[1])+(t.DED+t.IR+c[2])+(t.PES+c[3])+(t.OCU+t.COM+t.ADM+c[4]);
  if(ponte!==M.op)err.push('ponte '+ponte+' '+M.op);
  if(M.op+c[6]+c[7]!==M.var)err.push('variação');
  if(s(M.mes.LL)!==t.LL||s(M.mes.OP)!==M.op||s(M.mes.RB)!==t.RB)err.push('séries mensais');
  if(s(M.mes.ent)+s(M.mes.sai)!==M.var)err.push('entradas e saídas');
  if(M.mes.saldo[M.mes.saldo.length-1]!==M.saldo0+M.var)err.push('saldo');
  var cc=M.conc;if(cc[0]!==cc[1]+cc[2]+cc[3]+cc[4]+cc[5]+cc[6]+cc[7]+cc[8]+cc[9])err.push('linhas de conciliação');
  if(s(M.pendMot)!==M.pend.length||s(M.emp.map(i=>M.porEmp[i].pend))!==M.pend.length)err.push('pendências');
  return {err:err,v:{RB:t.RB,LL:t.LL,op:M.op,pend:M.pend.length}};}""",
 "demo-varejo.html": r"""(f)=>{var M=DEMO.calcular(f),err=[],t=M.tot,E=1e-6;
  var sm=(arr,k)=>arr.reduce((x,o)=>x+o[k],0);
  ['net','cmv','mc','bruto','desc','q'].forEach(k=>{
   if(Math.abs(sm(M.canais.map(c=>M.porCanal[c]),k)-t[k])>E)err.push('canal '+k);
   if(Math.abs(sm(M.itens.map(i=>M.porItem[i]),k)-t[k])>E)err.push('item '+k);
   if(Math.abs(sm(M.porCat,k)-t[k])>E)err.push('categoria '+k);
   if(Math.abs(sm(M.mes,k)-t[k])>E)err.push('mês '+k);});
  if(M.recCel!==M.netTodos)err.push('pedidos x itens '+M.recCel+' '+M.netTodos);
  var p=0;M.cel.forEach(l=>l.forEach(c=>p+=c.p));if(p!==M.ped||M.pedCanal.reduce((a,b)=>a+b,0)!==M.ped)err.push('pedidos');
  if(t.net>0&&Math.abs(M.cum[M.cum.length-1]-1)>1e-9)err.push('ABC');
  return {err:err,v:{net:t.net,cmv:t.cmv,ped:M.ped}};}""",
}
PY = {"demo-advocacia.html": py_advoc, "demo-contabilidade.html": None, "demo-varejo.html": py_varejo}

JS_DOM = r"""()=>{DEMO.renderTodas();var t=document.querySelector('main').innerText,bad=(t.match(/NaN|undefined|null|Infinity|\[object/g)||[]);
 var sem=[...document.querySelectorAll('svg[role="img"]')].filter(s=>!s.getAttribute('aria-label')).length;
 return {bad:bad,sem:sem,ms:DEMO.ultimoMs};}"""


def combos(nome, pg):
    pers = [p["id"] for p in pg.evaluate("DEMO.periodos")]
    if nome == "demo-advocacia.html":
        full = [{"per": p, "area": a, "adv": -1} for p in pers for a in range(-1, 5)] + [{"per": p, "area": -1, "adv": v} for p in pers for v in range(14)]
        amostra = [{"per": "12m", "area": a, "adv": -1} for a in range(-1, 5)] + [{"per": "24m", "area": -1, "adv": v} for v in (0, 4, 8)] + [{"per": "6m", "area": 0, "adv": 1}]
    elif nome == "demo-contabilidade.html":
        full = [{"per": p, "seg": s, "emp": -1} for p in pers for s in range(-1, 4)] + [{"per": p, "seg": -1, "emp": e} for p in pers for e in range(len(DC["emp"]))]
        amostra = [{"per": p, "seg": -1, "emp": -1} for p in pers] + [{"per": "12m", "seg": s, "emp": -1} for s in range(4)] + [{"per": "6m", "seg": -1, "emp": e} for e in (0, 10, 22, 35)]
    else:
        full = [{"per": p, "canal": c, "cat": k} for p in pers for c in range(-1, 4) for k in range(-1, 6)]
        amostra = [{"per": p, "canal": -1, "cat": -1} for p in pers] + [{"per": "12m", "canal": c, "cat": -1} for c in range(4)] + [{"per": "3m", "canal": 3, "cat": 1}]
    return full, amostra


with sync_playwright() as pw:
    b = pw.chromium.launch()
    for nome in ["demo-advocacia.html", "demo-contabilidade.html", "demo-varejo.html"]:
        pg = b.new_page(viewport={"width": 1280, "height": 900})
        erros, rede = [], []
        pg.on("pageerror", lambda e: erros.append(str(e)))
        pg.on("console", lambda c: erros.append(c.text) if c.type == "error" else None)
        pg.on("request", lambda r: rede.append(r.url) if not r.url.startswith(("file:", "data:", "blob:")) else None)
        pg.goto((RAIZ / nome).as_uri())
        pg.wait_for_timeout(400)
        full, amostra = combos(nome, pg)
        er = [(f, r["err"]) for f in full for r in [pg.evaluate(JS[nome], f)] if r["err"]]
        ok(not er, f"{nome}: reconciliação entre telas em {len(full)} combinações de filtro" + (f": {er[:2]}" if er else ""))
        pyerr = []
        for f in amostra:
            v = pg.evaluate(JS[nome], f)["v"]
            if nome == "demo-contabilidade.html":
                q = py_contab(f["per"], f["seg"], f["emp"], DC["meta"]["meses"])
            elif nome == "demo-varejo.html":
                q = py_varejo(f["per"], f["canal"], f["cat"])
            else:
                q = py_advoc(f["per"], f["area"], f["adv"])
            for k in q:
                if abs(v[k] - q[k]) > 1e-6:
                    pyerr.append((f, k, v[k], q[k]))
        ok(not pyerr, f"{nome}: recálculo independente em Python confere em {len(amostra)} recortes" + (f": {pyerr[:2]}" if pyerr else ""))
        bad, tempos, sem = [], [], 0
        for f in amostra:
            pg.evaluate("f=>DEMO.aplicar(f)", f)
            tempos.append(pg.evaluate("DEMO.ultimoMs"))
            r = pg.evaluate(JS_DOM)
            sem += r["sem"]
            if r["bad"]:
                bad.append((f, r["bad"][:3]))
        ok(not bad, f"{nome}: nenhum NaN, undefined, null ou Infinity renderizado em {len(amostra)} recortes, todas as telas" + (f": {bad[:2]}" if bad else ""))
        ok(sem == 0, f"{nome}: todos os gráficos têm descrição textual")
        ok(max(tempos) < 100, f"{nome}: filtros respondem em até {max(tempos):.1f} ms (limite 100 ms)")
        primeira = pg.evaluate("document.querySelector('[role=tab]').id")
        pg.evaluate(f"DEMO.abrir('{primeira[2:]}')")
        pg.focus("#" + primeira)
        pg.keyboard.press("ArrowRight")
        ok(pg.evaluate("document.activeElement.getAttribute('role')") == "tab" and pg.evaluate("document.activeElement.id") != primeira,
           f"{nome}: abas navegáveis por teclado")
        ok(not erros, f"{nome}: nenhum erro de JavaScript" + (f": {erros[:2]}" if erros else ""))
        ok(not rede, f"{nome}: nenhuma chamada de rede" + (f": {rede[:2]}" if rede else ""))
        pg.close()

    # Raio-X coerente com o painel de advocacia
    rx = textos["demo-raio-x.html"]
    ativos = [p for p in DA["proc"] if not p[5]]
    esperados = {"processos": f"{len(DA['proc'])} processos", "clientes": f"{len(DA['cli'])} clientes",
                 "advogados": f"{len(DA['adv'])} advogados", "encerrados": f"de {len(DA['proc']) - len(ativos)}",
                 "prazos abertos": f"{sum(1 for p in ativos if p[8])} prazos abertos"}
    faltam = [k for k, v in esperados.items() if v not in rx]
    ok(not faltam, "demo-raio-x.html: volumes iguais aos do painel de advocacia (processos, clientes, advogados, encerrados, prazos)" + (f"; divergem: {faltam}" if faltam else ""))
    horas = sum(t[3] for t in DA["ts"])
    ok("2.250 h" in rx and abs(horas * 0.046 - 2250) < 50, f"demo-raio-x.html: horas sem destino coerentes com {horas:.0f} h lançadas no painel")

    # páginas: links internos, rolagem horizontal, erros
    quebras, links, erros_pag = [], [], []
    for n in DEMOS + SITE:
        h = (RAIZ / n).read_text(encoding="utf-8")
        for href in re.findall(r'(?:href|src)="([^"#?]+)', h):
            if href.startswith(("http", "mailto:", "data:", "tel:")):
                if href.startswith("https://www.tdbases.com.br/"):
                    alvo = href[len("https://www.tdbases.com.br/"):] or "index.html"
                    if not (RAIZ / alvo).exists():
                        links.append((n, href))
                continue
            if not (RAIZ / href).exists():
                links.append((n, href))
    ok(not links, "links internos e imagens apontam para arquivos existentes" + (f": {links[:4]}" if links else ""))
    for w in (375, 1280):
        pg = b.new_page(viewport={"width": w, "height": 900})
        pg.on("pageerror", lambda e: erros_pag.append(str(e)))
        for n in DEMOS + SITE:
            pg.goto((RAIZ / n).as_uri())
            pg.wait_for_timeout(250)
            tabs = pg.evaluate("[...document.querySelectorAll('[role=tab]')].map(t=>t.id.slice(2))")
            for t in tabs or [None]:
                if t:
                    pg.evaluate(f"DEMO.abrir('{t}')")
                    pg.wait_for_timeout(80)
                sw = pg.evaluate("document.documentElement.scrollWidth")
                if sw > w:
                    quebras.append((n, t, w, sw))
        pg.close()
    ok(not quebras, f"sem rolagem horizontal da página em 375 e 1280 px, em {len(DEMOS + SITE)} páginas e todas as abas" + (f": {quebras[:4]}" if quebras else ""))
    ok(not erros_pag, "nenhum erro de JavaScript nas páginas do site" + (f": {erros_pag[:2]}" if erros_pag else ""))
    b.close()

print("VERIFICADO")
for o in oks:
    print("  ok   ", o)
if falhas:
    print("FALHAS")
    for f in falhas:
        print("  falha", f)
    sys.exit(1)
