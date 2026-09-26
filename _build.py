import os, json
OUT = "/home/claude/site/dist"
os.makedirs(OUT, exist_ok=True)
BASE = "https://tdbases.com.br"
WA = "5561991358553"
EMAIL = "tdbroott@gmail.com"

CSS = r"""
:root{--n9:#0C1B2E;--n8:#12263F;--n7:#1B3556;--n6:#2A4A70;--n1:#E4E9F0;--paper:#F4F6F9;--white:#FFFFFF;--ink:#1B2430;--muted:#556170;--line:#D3DAE3;--gold:#C2A064;--gold-d:#7A5C2C;--gold-l:#D9BF8C;--serif:"Spectral",Georgia,"Times New Roman",serif;--sans:"IBM Plex Sans",system-ui,-apple-system,"Segoe UI",Roboto,Arial,sans-serif;--wrap:1160px}
*,*::before,*::after{box-sizing:border-box}
html{scroll-padding-top:88px}
body{margin:0;font-family:var(--sans);font-size:1.0625rem;line-height:1.62;color:var(--ink);background:var(--white);-webkit-font-smoothing:antialiased}
img,svg{max-width:100%;height:auto}
a{color:var(--n7)}
a:hover{color:var(--gold-d)}
:focus-visible{outline:3px solid var(--gold);outline-offset:3px}
h1,h2,h3,h4{font-family:var(--serif);font-weight:600;line-height:1.15;margin:0 0 .6em;color:var(--n9);letter-spacing:-.01em}
h1{font-size:clamp(2.3rem,4.6vw,3.7rem);font-weight:500}
h2{font-size:clamp(1.8rem,3vw,2.55rem);font-weight:500}
h3{font-size:1.32rem}
p{margin:0 0 1em;max-width:68ch}
.wrap{max-width:var(--wrap);margin:0 auto;padding:0 24px}
.skip{position:absolute;left:-999px;top:0;background:var(--gold);color:var(--n9);padding:10px 14px;z-index:99}
.skip:focus{left:12px;top:12px}
/* header */
.site-head{position:sticky;top:0;z-index:50;background:var(--n9);border-bottom:1px solid rgba(255,255,255,.08)}
.site-head .wrap{display:flex;align-items:center;justify-content:space-between;height:72px;gap:24px}
.brand{display:flex;align-items:center;gap:12px;text-decoration:none;color:#fff}
.brand:hover{color:#fff}
.brand-name{font-family:var(--serif);font-size:1.45rem;font-weight:600;letter-spacing:.06em}
.nav{display:flex;align-items:center;gap:26px}
.nav a{color:#C9D3DF;text-decoration:none;font-size:.95rem}
.nav a:hover,.nav a[aria-current="page"]{color:#fff}
.nav a[aria-current="page"]{box-shadow:inset 0 -2px 0 var(--gold)}
.nav .btn{color:var(--n9);box-shadow:none}
.nav-toggle{display:none;background:none;border:1px solid rgba(255,255,255,.3);color:#fff;border-radius:4px;padding:8px 12px;font:inherit;font-size:.9rem;cursor:pointer}
@media (max-width:980px){
 .nav-toggle{display:block}
 .nav{position:absolute;top:72px;left:0;right:0;background:var(--n9);flex-direction:column;align-items:flex-start;padding:12px 24px 24px;gap:14px;display:none;border-bottom:1px solid rgba(255,255,255,.1)}
 .nav.open{display:flex}
}
/* buttons */
.btn{display:inline-block;font-family:var(--sans);font-weight:600;font-size:1rem;text-decoration:none;padding:14px 24px;border-radius:3px;border:2px solid transparent;cursor:pointer;line-height:1.2}
.btn-gold{background:var(--gold);color:var(--n9)}
.btn-gold:hover{background:var(--gold-l);color:var(--n9)}
.btn-line{border-color:rgba(255,255,255,.45);color:#fff;background:transparent}
.btn-line:hover{border-color:#fff;color:#fff}
.btn-navy{background:var(--n9);color:#fff}
.btn-navy:hover{background:var(--n7);color:#fff}
.btn-sm{padding:10px 16px;font-size:.92rem}
.actions{display:flex;flex-wrap:wrap;gap:14px;margin-top:28px}
/* sections */
section{padding:96px 0}
.bg-paper{background:var(--paper)}
.bg-navy{background:var(--n9);color:#D3DBE5}
.bg-navy h1,.bg-navy h2,.bg-navy h3{color:#fff}
.bg-navy a{color:var(--gold-l)}
.lede{font-size:1.2rem;color:var(--muted);max-width:62ch}
.bg-navy .lede{color:#B7C3D1}
.head-block{max-width:760px;margin-bottom:48px}
/* hero */
.hero{padding:88px 0 96px;background:var(--n9);color:#C9D3DF;position:relative;overflow:hidden}
.hero::after{content:"";position:absolute;inset:0;background-image:linear-gradient(rgba(255,255,255,.035) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,.035) 1px,transparent 1px);background-size:40px 40px;pointer-events:none}
.hero .wrap{position:relative;z-index:1;display:grid;grid-template-columns:1.05fr .95fr;gap:56px;align-items:center}
.hero h1{color:#fff}
.hero p.lede{color:#B7C3D1}
.hero-note{margin-top:22px;font-size:.93rem;color:#93A3B6}
@media (max-width:900px){.hero .wrap{grid-template-columns:1fr}.hero{padding:64px 0 72px}}
/* flow diagram */
.flow-svg text{font-family:var(--sans);fill:#D3DBE5;font-size:13px}
.flow-svg .src rect{fill:#12263F;stroke:#2F4E74}
.flow-svg .hub rect{fill:#1B3556;stroke:var(--gold)}
.flow-svg .hub text.t1{font-family:var(--serif);font-size:18px;fill:#fff}
.flow-svg .hub text.t2{font-size:11.5px;fill:#AEBBCB}
.flow-svg path.f{fill:none;stroke:var(--gold);stroke-width:1.4;stroke-dasharray:260;stroke-dashoffset:260;opacity:.85}
.flow-svg .panel rect.frame{fill:#F4F6F9;stroke:none}
.flow-svg .panel rect.bar{fill:var(--n7);transform-box:fill-box;transform-origin:bottom}
.flow-svg .panel rect.bar.g{fill:var(--gold)}
.flow-svg .panel text{fill:#12263F;font-size:11px}
.flow-svg .src{opacity:0}
@media (prefers-reduced-motion:no-preference){
 .flow-svg .src{animation:fade .5s ease forwards}
 .flow-svg path.f{animation:draw 1.1s ease forwards}
 .flow-svg .panel rect.bar{transform:scaleY(0);animation:grow .6s ease forwards;animation-delay:2.1s}
 .flow-svg .hub{opacity:0;animation:fade .6s ease forwards;animation-delay:1.3s}
}
@media (prefers-reduced-motion:reduce){.flow-svg .src{opacity:1}.flow-svg path.f{stroke-dashoffset:0}}
@keyframes fade{to{opacity:1}}
@keyframes draw{to{stroke-dashoffset:0}}
@keyframes grow{to{transform:scaleY(1)}}
/* risks */
.risks{display:grid;grid-template-columns:repeat(3,1fr);gap:40px;border-top:1px solid var(--line);padding-top:36px}
.risks h3{font-size:1.2rem}
.risks p{color:var(--muted);font-size:1rem}
@media (max-width:860px){.risks{grid-template-columns:1fr;gap:24px}}
/* authority dossier */
.dossier{display:grid;grid-template-columns:1fr 1fr;gap:0 56px}
.dossier div{border-left:2px solid var(--gold);padding:4px 0 4px 20px;margin-bottom:32px}
.dossier strong{display:block;font-family:var(--serif);font-weight:600;font-size:1.2rem;color:#fff;margin-bottom:4px}
.dossier span{color:#B7C3D1;font-size:.98rem}
@media (max-width:760px){.dossier{grid-template-columns:1fr}}
/* ladder */
.ladder{display:grid;grid-template-columns:repeat(3,1fr);gap:0;counter-reset:st;position:relative}
.ladder > div{padding:0 32px 0 0;position:relative}
.ladder > div + div{padding-left:32px;border-left:1px solid var(--line)}
.step-n{font-family:var(--serif);font-size:3.4rem;line-height:1;color:var(--gold-d);display:block;margin-bottom:14px}
.step-meta{display:block;font-size:.9rem;color:var(--gold-d);font-weight:600;margin-bottom:12px}
.ladder p{color:var(--muted);font-size:1rem}
.ladder .why{font-size:.95rem;color:var(--ink);border-top:1px solid var(--line);padding-top:12px;margin-top:6px}
@media (max-width:860px){.ladder{grid-template-columns:1fr;gap:36px}.ladder > div + div{border-left:none;padding-left:0;border-top:1px solid var(--line);padding-top:28px}}
/* segments on home */
.seg-grid{display:grid;grid-template-columns:1.35fr 1fr;gap:28px}
.seg-main{background:var(--n9);color:#C9D3DF;padding:44px 44px 40px;border-radius:4px;grid-row:span 2;display:flex;flex-direction:column}
.seg-main h3{color:#fff;font-size:1.9rem;font-weight:500}
.seg-main .tag{color:var(--gold-l);font-size:.95rem;font-weight:600;margin-bottom:14px;display:block}
.seg-main ul{margin:8px 0 28px;padding-left:1.1em}
.seg-main li{margin-bottom:6px}
.seg-main .btn{align-self:flex-start;margin-top:auto}
.seg-side{border:1px solid var(--line);padding:32px;border-radius:4px;background:var(--white);display:flex;flex-direction:column}
.seg-side p{color:var(--muted);font-size:1rem}
.seg-side a.more{margin-top:auto;font-weight:600;color:var(--n7)}
@media (max-width:860px){.seg-grid{grid-template-columns:1fr}.seg-main{grid-row:auto;padding:32px 26px}}
/* final cta */
.cta-band{background:var(--n8);color:#C9D3DF;padding:80px 0}
.cta-band .wrap{display:grid;grid-template-columns:1.4fr .6fr;gap:40px;align-items:center}
.cta-band h2{color:#fff}
.cta-band .actions{justify-content:flex-end;margin-top:0}
@media (max-width:860px){.cta-band .wrap{grid-template-columns:1fr}.cta-band .actions{justify-content:flex-start}}
/* page hero (inner) */
.page-hero{background:var(--n9);color:#C9D3DF;padding:80px 0 72px}
.page-hero h1{color:#fff;max-width:20ch}
.page-hero .lede{color:#B7C3D1}
.crumb{font-size:.9rem;color:#93A3B6;margin-bottom:18px;display:block}
.crumb a{color:#C9D3DF}
/* pains */
.pains{display:grid;grid-template-columns:repeat(2,1fr);gap:22px 48px;list-style:none;padding:0;margin:0}
.pains li{padding-left:28px;position:relative;max-width:52ch}
.pains li::before{content:"";position:absolute;left:0;top:.62em;width:14px;height:2px;background:var(--gold-d)}
@media (max-width:760px){.pains{grid-template-columns:1fr}}
/* stages detailed */
.stages{position:relative;margin-top:8px}
.stage{display:grid;grid-template-columns:120px 1fr;gap:32px;padding:40px 0;border-top:1px solid var(--line)}
.stage:last-child{border-bottom:1px solid var(--line)}
.stage .step-n{font-size:4rem}
.stage h3{font-size:1.6rem;font-weight:500}
.stage .cols{display:grid;grid-template-columns:1.2fr 1fr;gap:40px}
.stage ul{margin:0;padding-left:1.1em}
.stage li{margin-bottom:6px}
.stage .box{background:var(--white);border-left:3px solid var(--gold);align-self:start;padding:22px 24px;border-radius:3px;font-size:.98rem}
.stage .box h4{font-family:var(--sans);font-size:.95rem;font-weight:600;color:var(--n9);margin-bottom:8px}
.stage .box p{margin:0}
@media (max-width:860px){.stage{grid-template-columns:1fr;gap:8px}.stage .cols{grid-template-columns:1fr;gap:22px}}
/* indicator table */
.table-wrap{overflow-x:auto;margin-top:12px}
table.ind{border-collapse:collapse;width:100%;min-width:560px;font-size:.98rem;background:var(--white)}
table.ind th,table.ind td{text-align:left;padding:14px 16px;border-bottom:1px solid var(--line);vertical-align:top}
table.ind th{font-family:var(--sans);font-weight:600;color:var(--n9);background:var(--n1);font-size:.92rem}
table.ind td:first-child{font-weight:600;color:var(--n9);width:32%}
/* feature split */
.split{display:grid;grid-template-columns:1fr 1fr;gap:56px;align-items:start}
@media (max-width:860px){.split{grid-template-columns:1fr;gap:32px}}
.systems{display:flex;flex-wrap:wrap;gap:10px;margin:18px 0 12px;padding:0;list-style:none}
.systems li{border:1px solid var(--line);padding:8px 14px;border-radius:3px;font-size:.95rem;background:var(--white)}
.bg-navy .systems li{background:transparent;border-color:#35557C;color:#E4E9F0}
.fine{font-size:.88rem;color:var(--muted)}
.bg-navy .fine{color:#93A3B6}
.callout{border-left:3px solid var(--gold);padding:6px 0 6px 22px;margin:28px 0}
.callout p{margin:0;font-family:var(--serif);font-size:1.3rem;line-height:1.4;color:var(--n9)}
.bg-navy .callout p{color:#fff}
/* faq */
.faq details{border-top:1px solid var(--line);padding:18px 0}
.faq details:last-child{border-bottom:1px solid var(--line)}
.faq summary{cursor:pointer;font-weight:600;color:var(--n9);font-size:1.05rem;list-style:none;display:flex;justify-content:space-between;gap:16px}
.faq summary::-webkit-details-marker{display:none}
.faq summary::after{content:"+";font-family:var(--serif);font-size:1.5rem;line-height:1;color:var(--gold-d)}
.faq details[open] summary::after{content:"\2212"}
.faq details p{margin:12px 0 0;color:var(--muted)}
/* about timeline */
.timeline{list-style:none;padding:0;margin:0;position:relative}
.timeline li{display:grid;grid-template-columns:150px 1fr;gap:28px;padding:26px 0;border-top:1px solid var(--line)}
.timeline li:last-child{border-bottom:1px solid var(--line)}
.timeline .when{font-family:var(--serif);font-size:1.15rem;color:var(--gold-d)}
.timeline h3{font-size:1.2rem;margin-bottom:6px}
.timeline p{color:var(--muted);margin:0;font-size:1rem}
@media (max-width:700px){.timeline li{grid-template-columns:1fr;gap:4px}}
.creds{display:grid;grid-template-columns:repeat(3,1fr);gap:40px}
.creds h3{font-size:1.15rem}
.creds ul{margin:0;padding-left:1.1em;color:var(--muted);font-size:1rem}
.creds li{margin-bottom:6px}
@media (max-width:860px){.creds{grid-template-columns:1fr;gap:24px}}
.principles{display:grid;grid-template-columns:repeat(2,1fr);gap:28px 56px}
.principles h3{font-size:1.15rem}
.principles p{color:#B7C3D1;font-size:1rem}
@media (max-width:760px){.principles{grid-template-columns:1fr}}
/* contact */
.contact-grid{display:grid;grid-template-columns:1.25fr .75fr;gap:64px;align-items:start}
@media (max-width:900px){.contact-grid{grid-template-columns:1fr;gap:40px}}
form.lead{display:grid;gap:18px}
.field{display:grid;gap:6px}
.field label{font-weight:600;color:var(--n9);font-size:.95rem}
.field .hint{font-weight:400;color:var(--muted);font-size:.88rem}
.field input,.field select,.field textarea{font:inherit;font-size:1rem;padding:12px 14px;border:1px solid #B9C3CF;border-radius:3px;background:#fff;color:var(--ink);width:100%}
.field textarea{min-height:120px;resize:vertical}
.field input:focus,.field select:focus,.field textarea:focus{outline:3px solid var(--gold);outline-offset:0;border-color:var(--n7)}
.row2{display:grid;grid-template-columns:1fr 1fr;gap:18px}
@media (max-width:600px){.row2{grid-template-columns:1fr}}
.consent{display:flex;gap:12px;align-items:flex-start;font-size:.93rem;color:var(--muted)}
.consent input{margin-top:5px;width:18px;height:18px;flex:0 0 auto}
.form-actions{display:flex;flex-wrap:wrap;gap:12px;align-items:center}
.status{font-size:.95rem;min-height:1.4em;margin:0}
.status.err{color:#9B2C2C}
.status.ok{color:#1E5B3A}
.side-box{background:var(--paper);padding:32px;border-radius:4px}
.side-box h3{font-size:1.2rem}
.next{list-style:none;padding:0;margin:0 0 28px;counter-reset:nx}
.next li{counter-increment:nx;padding-left:40px;position:relative;margin-bottom:16px;font-size:1rem}
.next li::before{content:counter(nx);position:absolute;left:0;top:-2px;font-family:var(--serif);font-size:1.5rem;color:var(--gold-d)}
.direct a{display:block;font-weight:600;margin-bottom:6px}
/* footer */
.site-foot{background:var(--n9);color:#93A3B6;padding:64px 0 40px;font-size:.93rem}
.foot-grid{display:grid;grid-template-columns:1.4fr 1fr 1fr;gap:40px;margin-bottom:40px}
.site-foot h4{font-family:var(--sans);font-size:.95rem;color:#fff;margin-bottom:12px;font-weight:600}
.site-foot a{color:#C9D3DF;text-decoration:none}
.site-foot a:hover{color:#fff;text-decoration:underline}
.site-foot ul{list-style:none;padding:0;margin:0}
.site-foot li{margin-bottom:8px}
.legal{border-top:1px solid rgba(255,255,255,.1);padding-top:24px;font-size:.84rem;line-height:1.55}
.legal p{max-width:none;margin-bottom:.5em}
@media (max-width:760px){.foot-grid{grid-template-columns:1fr}}
"""

LOGO = '''<svg width="30" height="30" viewBox="0 0 30 30" aria-hidden="true"><ellipse cx="15" cy="7" rx="11" ry="4" fill="none" stroke="#C2A064" stroke-width="2"/><path d="M4 7v16c0 2.2 4.9 4 11 4s11-1.8 11-4V7" fill="none" stroke="#C2A064" stroke-width="2"/><path d="M4 15c0 2.2 4.9 4 11 4s11-1.8 11-4" fill="none" stroke="#C2A064" stroke-width="2"/></svg>'''
FAVICON = "data:image/svg+xml," + "%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Crect width='32' height='32' rx='4' fill='%230C1B2E'/%3E%3Cellipse cx='16' cy='9' rx='9' ry='3.3' fill='none' stroke='%23C2A064' stroke-width='2'/%3E%3Cpath d='M7 9v13c0 1.8 4 3.3 9 3.3s9-1.5 9-3.3V9M7 15.5c0 1.8 4 3.3 9 3.3s9-1.5 9-3.3' fill='none' stroke='%23C2A064' stroke-width='2'/%3E%3C/svg%3E"

NAV = [("index.html","Início"),("advocacia.html","Advocacia"),("contabilidade.html","Contabilidade"),("varejo-food-service.html","Varejo e food service"),("sobre.html","Sobre")]

def header(active):
    links = "".join(f'<a href="{h}"{" aria-current=\"page\"" if h==active else ""}>{t}</a>' for h,t in NAV)
    return f'''<a class="skip" href="#conteudo">Pular para o conteúdo</a>
<header class="site-head"><div class="wrap">
<a class="brand" href="index.html" aria-label="TDBASES, página inicial">{LOGO}<span class="brand-name">TDBASES</span></a>
<button class="nav-toggle" aria-expanded="false" aria-controls="nav">Menu</button>
<nav class="nav" id="nav" aria-label="Principal">{links}<a class="btn btn-gold btn-sm" href="contato.html"{" aria-current=\"page\"" if active=="contato.html" else ""}>Agendar Raio-X de Dados</a></nav>
</div></header>'''

FOOTER = f'''<footer class="site-foot"><div class="wrap">
<div class="foot-grid">
<div><a class="brand" href="index.html">{LOGO}<span class="brand-name">TDBASES</span></a>
<p style="margin-top:16px">Engenharia e arquitetura de dados para pequenas e médias empresas, com o rigor de quem construiu dados para instituições que não podem errar.</p></div>
<div><h4>Soluções</h4><ul><li><a href="advocacia.html">Escritórios de advocacia</a></li><li><a href="contabilidade.html">Contabilidade</a></li><li><a href="varejo-food-service.html">Varejo, bares e restaurantes</a></li><li><a href="contato.html">Raio-X de Dados</a></li></ul></div>
<div><h4>Contato</h4><ul><li><a href="mailto:{EMAIL}">{EMAIL}</a></li><li><a href="https://wa.me/{WA}" rel="noopener">WhatsApp +55 61 99135-8553</a></li><li><a href="sobre.html">Sobre a TDBASES</a></li></ul></div>
</div>
<div class="legal">
<p>THALES DIAS BRAGA CONSULTORIA EM TECNOLOGIA DA INFORMAÇÃO LTDA. CNPJ 66.785.647/0001-84.</p>
<p>Astrea, EasyJur, Projuris, Legal One, SAJ, iFood e Rappi são marcas de seus respectivos titulares, citadas apenas para indicar sistemas com os quais a TDBASES sabe trabalhar. Não há parceria, afiliação ou endosso dessas empresas.</p>
</div></div></footer>'''

JS_NAV = '''<script>
(function(){var b=document.querySelector('.nav-toggle'),n=document.getElementById('nav');if(!b)return;b.addEventListener('click',function(){var o=n.classList.toggle('open');b.setAttribute('aria-expanded',o?'true':'false');});})();
</script>'''

def page(fname, title, desc, body, extra_head="", extra_js=""):
    canon = BASE + "/" + ("" if fname=="index.html" else fname)
    html = f'''<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{canon}">
<meta property="og:type" content="website">
<meta property="og:locale" content="pt_BR">
<meta property="og:site_name" content="TDBASES">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{canon}">
<meta name="theme-color" content="#0C1B2E">
<link rel="icon" href="{FAVICON}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600&family=Spectral:wght@400;500;600&display=swap" rel="stylesheet">
<style>{CSS}</style>
{extra_head}
</head>
<body>
{header(fname)}
<main id="conteudo">
{body}
</main>
{FOOTER}
{JS_NAV}
{extra_js}
</body>
</html>'''
    with open(os.path.join(OUT, fname), "w", encoding="utf-8") as f:
        f.write(html)

def cta_band(title, text, seg=""):
    q = f"?segmento={seg}" if seg else ""
    return f'''<section class="cta-band"><div class="wrap">
<div><h2>{title}</h2><p class="lede" style="color:#B7C3D1;margin:0">{text}</p></div>
<div class="actions"><a class="btn btn-gold" href="contato.html{q}">Agendar Raio-X de Dados</a></div>
</div></section>'''

# ---------------- HERO SVG ----------------
srcs = ["Sistema jurídico","ERP contábil","PDV do caixa","iFood e Rappi","Extrato bancário","Planilhas soltas"]
g = []
for i,s in enumerate(srcs):
    y = 20 + i*62
    d = 0.15*i
    g.append(f'<g class="src" style="animation-delay:{d:.2f}s"><rect x="4" y="{y}" width="150" height="36" rx="3"/><text x="18" y="{y+23}">{s}</text></g>')
    g.append(f'<path class="f" style="animation-delay:{0.5+0.1*i:.2f}s" d="M154 {y+18} C 210 {y+18}, 220 205, 262 205"/>')
bars = [(40,"b"),(62,"b"),(30,"b"),(78,"g"),(52,"b")]
bh = []
for i,(h,c) in enumerate(bars):
    x = 416 + i*18
    bh.append(f'<rect class="bar{" g" if c=="g" else ""}" x="{x}" y="{300-h}" width="12" height="{h}" style="animation-delay:{2.1+0.08*i:.2f}s"/>')
HERO_SVG = f'''<svg class="flow-svg" viewBox="0 0 530 400" role="img" aria-label="Diagrama: dados de sistemas separados, como sistema jurídico, ERP, PDV, aplicativos de delivery, extrato bancário e planilhas, convergem para uma base única que alimenta um painel de indicadores.">
{''.join(g)}
<g class="hub"><rect x="262" y="160" width="124" height="90" rx="3"/><text class="t1" x="278" y="198">Base única</text><text class="t2" x="278" y="220">integrada e</text><text class="t2" x="278" y="236">documentada</text></g>
<path class="f" style="animation-delay:1.7s" d="M386 205 L 402 205"/>
<g class="panel"><rect class="frame" x="402" y="150" width="120" height="166" rx="3"/><text x="414" y="172">Margem por canal</text><line x1="414" y1="300" x2="508" y2="300" stroke="#9AA7B6"/>{''.join(bh)}</g>
</svg>'''

# ---------------- HOME ----------------
home = f'''
<section class="hero"><div class="wrap">
<div>
<h1>Sua empresa decide todos os dias. Com base em quais dados?</h1>
<p class="lede">Vendas num sistema, financeiro em outro, planilha paralela no computador de alguém. A TDBASES junta o que está espalhado numa base única e entrega um painel que mostra quanto cada cliente, produto e área realmente dá de lucro.</p>
<div class="actions"><a class="btn btn-gold" href="contato.html">Agendar Raio-X de Dados</a><a class="btn btn-line" href="#como-funciona">Ver como funciona</a></div>
<p class="hero-note">Arquitetura de dados com a mesma disciplina aplicada na solução de BI da Polícia Federal e em pesquisas oficiais de estatística pública.</p>
</div>
<div>{HERO_SVG}</div>
</div></section>

<section><div class="wrap">
<div class="head-block">
<h2>Dado espalhado é decisão no escuro</h2>
<p class="lede">A maioria das pequenas e médias empresas tem dados de sobra. O problema é que eles moram em sistemas que não conversam, e ninguém consegue cruzar venda com custo, cliente com margem, esforço com resultado. Aí a decisão vira intuição, e intuição não aparece no balanço até ser tarde.</p>
</div>
<div class="risks">
<div><h3>A concorrência já decide com números</h3><p>Quem sabe qual cliente dá prejuízo corta ou reprecifica antes. Quem não sabe continua atendendo esse cliente com o mesmo empenho, e descobre no fim do ano.</p></div>
<div><h3>O dinheiro vaza sem fazer barulho</h3><p>Taxa de aplicativo que come a margem, honorário que não cobre as horas gastas, estoque que some sem registro. Nada disso aparece no relatório fiscal, mas tudo aparece no caixa.</p></div>
<div><h3>A LGPD não aceita improviso</h3><p>Empresa que não sabe onde estão os dados pessoais que trata também não consegue provar que os protege. Um inventário de dados deixou de ser luxo de grande empresa.</p></div>
</div>
</div></section>

<section class="bg-navy"><div class="wrap">
<div class="head-block">
<h2>Rigor de quem trabalhou onde errar não é opção</h2>
<p class="lede">A TDBASES é a consultoria de Thales Dias Braga, arquiteto e engenheiro de dados com 20 anos de carreira. O que ele leva para o seu negócio foi testado em ambientes onde um dado errado tem consequência institucional.</p>
</div>
<div class="dossier">
<div><strong>Polícia Federal e INTERPOL</strong><span>13 anos como analista sênior de dados, DBA e arquiteto de dados construindo a solução de Business Intelligence da Polícia Federal, em cooperação com a INTERPOL.</span></div>
<div><strong>Sete países da América Latina</strong><span>Projetos de dados no Brasil, Peru, Argentina, Panamá, Jamaica, Chile e Honduras, em português, inglês e espanhol.</span></div>
<div><strong>Estatística pública oficial</strong><span>Analista de dados no IPEDF Codeplan, no projeto InfoDF 2.0, apoiando pesquisas de larga escala como a PDAD e a PED.</span></div>
<div><strong>Pesquisa, formação e certificações</strong><span>Mestrado em Computação Aplicada, área de Ciência de Dados, na UnB, artigo científico publicado pela Sociedade Brasileira de Computação em 2025 e certificações Oracle Database Administration, Linux LPIC 2 e ITIL Foundation.</span></div>
</div>
<p><a href="sobre.html">Conheça a trajetória completa</a></p>
</div></section>

<section id="como-funciona"><div class="wrap">
<div class="head-block">
<h2>Três etapas, sem salto no escuro</h2>
<p class="lede">Você não precisa apostar alto antes de saber o que vai receber. Cada etapa tem escopo, prazo e preço definidos antes de começar, e a seguinte só acontece se fizer sentido para o seu negócio.</p>
</div>
<div class="ladder">
<div><span class="step-n">1</span><h3>Raio-X de Dados</h3><span class="step-meta">Diagnóstico pago, de 3 a 5 dias úteis</span>
<p>Mapeamos onde os dados do seu negócio nascem, por onde passam e onde se perdem. Você recebe um relatório com os problemas em ordem de prioridade e um orçamento fechado para resolver.</p>
<p class="why">Investimento baixo para decidir com informação, e não com uma proposta genérica.</p></div>
<div><span class="step-n">2</span><h3>Implementação</h3><span class="step-meta">Escopo fechado, de 2 a 6 semanas</span>
<p>Construímos a infraestrutura de dados e um painel de indicadores feito para o seu tipo de negócio, com os números que você realmente precisa acompanhar.</p>
<p class="why">Entrega tangível: base integrada, painel funcionando e documentação.</p></div>
<div><span class="step-n">3</span><h3>Sustentação e governança</h3><span class="step-meta">Contrato mensal</span>
<p>Mantemos as cargas rodando, os dados atualizados e o painel evoluindo conforme o negócio muda. Sistema troca de versão, cadastro muda, surge pergunta nova.</p>
<p class="why">Dado sem manutenção apodrece rápido. A recorrência existe por isso, não para prender ninguém.</p></div>
</div>
</div></section>

<section class="bg-paper"><div class="wrap">
<div class="head-block">
<h2>Soluções por tipo de negócio</h2>
<p class="lede">Cada segmento tem sistemas, vocabulário e perguntas próprias. Por isso o método é o mesmo, mas o produto não.</p>
</div>
<div class="seg-grid">
<div class="seg-main">
<span class="tag">Carro-chefe</span>
<h3>Escritórios de advocacia</h3>
<p>Data Warehouse Jurídico e Painel de Indicadores de Gestão. Os dados do seu sistema de gestão jurídica, do financeiro e das planilhas paralelas numa base única, enriquecida com dados públicos do CNJ.</p>
<ul><li>Aging de prazos e carteira por fase</li><li>Produtividade por advogado</li><li>Taxa de êxito por área do direito</li><li>Rentabilidade por cliente e por área</li><li>Mapeamento de dados pessoais para a LGPD</li></ul>
<a class="btn btn-gold" href="advocacia.html">Ver a solução para advocacia</a>
</div>
<div class="seg-side"><h3>Contabilidade</h3><p>Uma ponte entre o ERP contábil e um painel gerencial de fluxo de caixa e DRE, além de conciliação automatizada entre extrato, notas fiscais e lançamentos.</p><a class="more" href="contabilidade.html">Ver a solução para contabilidade</a></div>
<div class="seg-side"><h3>Varejo, bares e restaurantes</h3><p>PDV, iFood, Rappi e estoque num só lugar, com CMV e margem reais por produto ou prato e ticket médio por canal de venda.</p><a class="more" href="varejo-food-service.html">Ver a solução para varejo e food service</a></div>
</div>
</div></section>
''' + cta_band("Comece pelo Raio-X de Dados", "Em 3 a 5 dias úteis você sabe onde estão os problemas dos seus dados, o que resolver primeiro e quanto custa.")

ld = {"@context":"https://schema.org","@type":"ProfessionalService","name":"TDBASES","legalName":"THALES DIAS BRAGA CONSULTORIA EM TECNOLOGIA DA INFORMAÇÃO LTDA","taxID":"66.785.647/0001-84","url":BASE,"email":EMAIL,"telephone":"+55-61-99135-8553","areaServed":"BR","founder":{"@type":"Person","name":"Thales Dias Braga","jobTitle":"Arquiteto e engenheiro de dados"},"description":"Engenharia e arquitetura de dados para pequenas e médias empresas: diagnóstico, data warehouse, painéis de indicadores e governança de dados."}
page("index.html","TDBASES | Engenharia e arquitetura de dados para pequenas e médias empresas",
     "A TDBASES integra os dados espalhados da sua empresa numa base única e entrega painéis de gestão para advocacia, contabilidade, varejo e food service. Comece pelo Raio-X de Dados.",
     home, extra_head=f'<script type="application/ld+json">{json.dumps(ld,ensure_ascii=False)}</script>')

# ---------------- SEGMENT BUILDER ----------------
def segment(fname, seg, title, desc, crumb, h1, lede, pains_h, pains, stages, extra, faq, cta_t, cta_p):
    pl = "".join(f"<li>{p}</li>" for p in pains)
    st = ""
    for i,s in enumerate(stages,1):
        items = "".join(f"<li>{x}</li>" for x in s["items"])
        st += f'''<div class="stage"><div><span class="step-n">{i}</span></div><div>
<h3>{s["t"]}</h3><span class="step-meta">{s["meta"]}</span><p>{s["p"]}</p>
<div class="cols"><div><ul>{items}</ul></div><div class="box"><h4>{s["bh"]}</h4><p>{s["bp"]}</p></div></div>
</div></div>'''
    fq = "".join(f"<details><summary>{q}</summary><p>{a}</p></details>" for q,a in faq)
    body = f'''
<section class="page-hero"><div class="wrap">
<span class="crumb"><a href="index.html">Início</a> / {crumb}</span>
<h1>{h1}</h1><p class="lede">{lede}</p>
<div class="actions"><a class="btn btn-gold" href="contato.html?segmento={seg}">Agendar Raio-X de Dados</a><a class="btn btn-line" href="#etapas">Ver as três etapas</a></div>
</div></section>
<section><div class="wrap"><div class="head-block"><h2>{pains_h}</h2></div><ul class="pains">{pl}</ul></div></section>
<section class="bg-paper" id="etapas"><div class="wrap"><div class="head-block"><h2>Como funciona, etapa por etapa</h2><p class="lede">Cada etapa tem entrega, prazo e preço definidos antes de começar. Você pode parar em qualquer uma delas.</p></div>
<div class="stages">{st}</div></div></section>
{extra}
<section><div class="wrap"><div class="head-block"><h2>Perguntas frequentes</h2></div><div class="faq" style="max-width:820px">{fq}</div></div></section>
''' + cta_band(cta_t, cta_p, seg)
    page(fname, title, desc, body)

# ---------- ADVOCACIA ----------
adv_extra = '''
<section class="bg-navy"><div class="wrap split">
<div>
<h2>Dados públicos do CNJ trabalhando para o seu escritório</h2>
<p>O Conselho Nacional de Justiça mantém a API pública do DataJud, com metadados de processos dos tribunais brasileiros. A TDBASES integra essa fonte ao data warehouse do escritório para completar classe, assunto, órgão julgador e movimentações, e para apontar divergências entre o que o seu sistema registra e o que consta no tribunal.</p>
<p>Consumir uma API pública de grande volume, tratar inconsistências de cadastro e cruzar tudo com a base interna é trabalho de engenharia de dados. É o tipo de entrega que a TI genérica, focada em rede e suporte, normalmente não tem estrutura para fazer.</p>
<p class="fine">A cobertura e a atualização dos dados dependem da disponibilização pelo CNJ e pelos tribunais.</p>
</div>
<div>
<h3>Sistemas com os quais sabemos trabalhar</h3>
<ul class="systems"><li>Astrea</li><li>EasyJur</li><li>Projuris</li><li>Legal One</li><li>SAJ</li><li>Planilhas e financeiro</li></ul>
<p class="fine">A extração é feita por API, exportação ou acesso a banco, conforme o que o seu sistema e o seu plano permitem. Nomes citados apenas como referência técnica, sem parceria ou endosso das empresas.</p>
<div class="callout"><p>Os indicadores são calculados a partir dos seus dados, com regras documentadas. Você sabe de onde vem cada número.</p></div>
</div>
</div></section>

<section><div class="wrap">
<div class="head-block"><h2>Indicadores que o painel entrega</h2><p class="lede">O conjunto final é definido no Raio-X, conforme a realidade do escritório. Estes são os indicadores de base.</p></div>
<div class="table-wrap"><table class="ind">
<thead><tr><th scope="col">Indicador</th><th scope="col">Pergunta que responde</th></tr></thead>
<tbody>
<tr><td>Aging de prazos</td><td>Quantos prazos estão em cada faixa de vencimento, por responsável, e onde está o gargalo.</td></tr>
<tr><td>Produtividade por advogado</td><td>Volume de peças, audiências e tarefas concluídas por pessoa, comparável ao longo do tempo.</td></tr>
<tr><td>Taxa de êxito por área</td><td>Em quais áreas do direito o escritório ganha mais, e em quais o resultado não justifica a carteira.</td></tr>
<tr><td>Rentabilidade por cliente</td><td>Quanto cada cliente paga frente ao esforço que consome, incluindo contratos de partido mensal.</td></tr>
<tr><td>Rentabilidade por área</td><td>Quais áreas sustentam o escritório e quais dependem de subsídio das outras.</td></tr>
<tr><td>Carteira por fase processual</td><td>Onde estão os processos, quanto tempo ficam em cada fase e quando tendem a gerar honorário de êxito.</td></tr>
</tbody></table></div>
</div></section>

<section class="bg-paper"><div class="wrap split">
<div>
<h2>Mapeamento de Dados para LGPD</h2>
<p>Escritório de advocacia trata dado pessoal de terceiros o tempo todo, e boa parte dele é sensível: saúde em ações previdenciárias e trabalhistas, dados de menores em família, informações financeiras em cobrança. Raramente existe um inventário formal de onde esses dados entram, onde ficam, quem acessa e por quanto tempo são guardados.</p>
<p>A TDBASES faz o levantamento técnico que sustenta o trabalho do encarregado e da área jurídica do escritório: fontes, fluxos, locais de armazenamento, acessos e retenção, organizados como base para o registro das operações de tratamento exigido pelo artigo 37 da LGPD.</p>
</div>
<div>
<h3>O que você recebe</h3>
<ul>
<li>Inventário de dados pessoais e sensíveis por sistema, pasta e planilha</li>
<li>Mapa de fluxos: por onde o dado entra, circula e sai do escritório</li>
<li>Pontos de exposição priorizados, como pastas compartilhadas sem controle e cópias locais</li>
<li>Base estruturada para o registro de operações de tratamento</li>
</ul>
<p class="fine">Pode ser contratado isoladamente ou junto com o data warehouse, aproveitando o mesmo levantamento.</p>
</div>
</div></section>
'''
segment("advocacia.html","advocacia","Data Warehouse Jurídico e painel de gestão para escritórios | TDBASES",
 "Consolide os dados do seu sistema de gestão jurídica numa base única com aging de prazos, produtividade, êxito e rentabilidade por cliente e área. Mapeamento de dados para LGPD.",
 "Escritórios de advocacia",
 "Seu escritório sabe quantos processos tem. Sabe quais deles dão lucro?",
 "O Data Warehouse Jurídico da TDBASES reúne os dados do sistema de gestão, do financeiro e das planilhas paralelas numa base única, enriquecida com dados públicos do CNJ, e entrega um painel de gestão feito para a rotina de um escritório.",
 "A rotina que a gente conhece",
 ["Prazos controlados no sistema e, por garantia, numa planilha paralela que só uma pessoa entende.",
  "Produtividade medida pela impressão de quem parece mais ocupado, e não por número.",
  "Honorário fixado sem saber quanto tempo a equipe realmente gasta com aquele cliente.",
  "Relatório para os sócios montado à mão, toda semana, copiando dados de três lugares.",
  "Área que parece forte porque tem muito processo, mas que dá prejuízo quando se olha a margem.",
  "Dados pessoais e sensíveis de clientes e partes espalhados em pastas, e-mails e planilhas sem inventário."],
 [
  {"t":"Raio-X de Dados Jurídico","meta":"3 a 5 dias úteis","p":"Um diagnóstico curto e pago que mostra a real condição dos dados do escritório antes de qualquer investimento maior.",
   "items":["Levantamento do sistema de gestão jurídica, do financeiro e das planilhas em uso","Avaliação da qualidade dos cadastros: processo sem área, cliente duplicado, prazo sem responsável","Identificação de quais indicadores já são possíveis e quais dependem de ajuste de cadastro","Primeira leitura dos riscos de LGPD visíveis no processo"],
   "bh":"Entrega","bp":"Relatório priorizado com os problemas encontrados e orçamento fechado para a implementação, sem letra miúda."},
  {"t":"Data Warehouse Jurídico e Painel de Gestão","meta":"4 a 6 semanas, escopo fechado","p":"A implementação que transforma dados soltos em gestão. A base fica modelada por processo, cliente, advogado, área do direito e tempo, e alimenta um painel pronto para a reunião de sócios.",
   "items":["Extração automatizada do sistema de gestão jurídica e do financeiro","Modelagem dimensional documentada, com regras de cálculo explícitas","Enriquecimento com a API pública do DataJud, do CNJ","Painel com aging de prazos, produtividade, êxito e rentabilidade","Treinamento da equipe para leitura e uso do painel"],
   "bh":"Por que o prazo é maior aqui","bp":"Dado jurídico tem cadastro heterogêneo e muita informação em texto livre. O tempo extra vai para padronizar isso de forma que os números se sustentem numa reunião de sócios."},
  {"t":"Sustentação e governança","meta":"Contrato mensal","p":"Sistema jurídico muda de versão, o escritório abre área nova, sócio pede indicador novo. Sem manutenção, o painel perde a confiança da equipe em poucos meses.",
   "items":["Monitoramento das cargas e correção de falhas de extração","Atualização contínua da base e do enriquecimento com o CNJ","Evolução do painel com novos indicadores","Revisão periódica da qualidade dos cadastros com a equipe"],
   "bh":"Entrega","bp":"Painel confiável ao longo do tempo, com histórico preservado e documentação sempre atualizada."}
 ], adv_extra,
 [("Preciso trocar de sistema de gestão jurídica?","Não. A TDBASES trabalha a partir do sistema que o escritório já usa. O Raio-X confirma qual forma de extração é viável no seu caso."),
  ("Os dados do escritório ficam expostos?","O projeto é desenhado com controle de acesso e mínimo necessário de dados pessoais em cada camada. O próprio mapeamento para LGPD pode ser feito junto."),
  ("O escritório é pequeno. Isso faz sentido para nós?","O Raio-X existe justamente para responder isso com base nos seus dados. Se o investimento não se justificar, o relatório diz isso."),
  ("Vocês prestam consultoria jurídica sobre LGPD?","Não. O trabalho é técnico: inventário, fluxos e estrutura de dados. A interpretação jurídica continua com o escritório e o seu encarregado.")],
 "Descubra o que os dados do seu escritório já dizem", "Comece pelo Raio-X de Dados Jurídico: de 3 a 5 dias úteis, relatório priorizado e orçamento fechado.")

# ---------- CONTABILIDADE ----------
cont_extra = '''
<section class="bg-navy"><div class="wrap split">
<div>
<h2>Do fiscal ao gerencial: uma nova linha de serviço</h2>
<p>O escritório contábil já tem o dado mais valioso da empresa cliente: todos os lançamentos, organizados e conferidos. O que falta é transformá-lo em algo que o empresário entenda e use para decidir.</p>
<p>A ponte entre o ERP contábil e um painel gerencial permite ao escritório oferecer fluxo de caixa e DRE gerencial como serviço recorrente, com a própria marca, sem montar tudo à mão em planilha a cada mês.</p>
</div>
<div>
<div class="callout"><p>Relatório fiscal cumpre obrigação. Relatório gerencial ajuda o cliente a continuar existindo, e a continuar sendo seu cliente.</p></div>
<p class="fine">A integração com o ERP contábil é feita por exportação estruturada ou acesso ao banco de dados, conforme o sistema e o licenciamento do escritório.</p>
</div>
</div></section>

<section><div class="wrap">
<div class="head-block"><h2>Conciliação automatizada</h2><p class="lede">Conferir extrato bancário contra notas fiscais e lançamentos, linha a linha, consome horas da equipe todo mês. A conciliação automatizada faz o cruzamento por regras e deixa para a equipe só o que realmente precisa de olho humano.</p></div>
<div class="table-wrap"><table class="ind">
<thead><tr><th scope="col">Fonte</th><th scope="col">Como entra na conciliação</th></tr></thead>
<tbody>
<tr><td>Extrato bancário</td><td>Arquivos OFX ou exportações do banco, padronizados numa mesma estrutura.</td></tr>
<tr><td>Notas fiscais</td><td>XML de NF-e e NFS-e, com emitente, valores, datas e chaves de acesso.</td></tr>
<tr><td>Lançamentos contábeis</td><td>Exportação do ERP contábil, ligada ao plano de contas.</td></tr>
<tr><td>Fila de exceções</td><td>O que não casou por regra aparece separado, com o motivo provável, para análise da equipe.</td></tr>
</tbody></table></div>
</div></section>
'''
segment("contabilidade.html","contabilidade","Painel gerencial e conciliação automatizada para contabilidade | TDBASES",
 "Transforme os dados do ERP contábil em fluxo de caixa e DRE gerencial para seus clientes, e automatize a conciliação entre extrato bancário, notas fiscais e lançamentos.",
 "Contabilidade",
 "Você entrega o fiscal em dia. E o gerencial do seu cliente?",
 "A TDBASES liga o ERP contábil a um painel de fluxo de caixa e DRE gerencial, e automatiza a conciliação entre extrato, notas e lançamentos. Menos conferência manual para a sua equipe, mais valor percebido pelo seu cliente.",
 "A rotina que a gente conhece",
 ["Equipe gastando dias do fechamento conferindo extrato contra lançamento, linha a linha.",
  "Cliente pede um DRE para entender o negócio e recebe um balancete que não sabe ler.",
  "Relatório gerencial montado em planilha, cliente por cliente, sem padrão e sem histórico.",
  "Dados presos no ERP contábil, acessíveis só por relatórios prontos que ninguém pediu.",
  "Honorário pressionado para baixo porque o cliente enxerga só a obrigação acessória.",
  "Erro de conciliação descoberto meses depois, quando corrigir já dá muito mais trabalho."],
 [
  {"t":"Raio-X de Dados Contábil","meta":"3 a 5 dias úteis","p":"Diagnóstico da rotina de dados do escritório e de uma amostra de clientes, para medir onde está o retrabalho e o que pode virar produto gerencial.",
   "items":["Levantamento do ERP contábil, formas de exportação e bancos utilizados","Mapeamento do fluxo atual de conciliação e do tempo gasto","Avaliação do plano de contas para uso gerencial","Seleção dos clientes com melhor perfil para o painel piloto"],
   "bh":"Entrega","bp":"Relatório priorizado e orçamento fechado para a implementação, com escopo por número de clientes atendidos."},
  {"t":"Painel gerencial e conciliação automatizada","meta":"3 a 5 semanas, escopo fechado","p":"Construção da ponte entre o ERP contábil e o painel, com plano de contas gerencial mapeado ao contábil, e da rotina automatizada de conciliação.",
   "items":["Extração estruturada do ERP contábil","Mapeamento do plano de contas contábil para uma visão gerencial","Painel de fluxo de caixa e DRE gerencial por cliente","Conciliação por regras entre extrato, notas fiscais e lançamentos","Fila de exceções para a equipe revisar só o que precisa"],
   "bh":"Caixa e competência","bp":"O painel deixa explícito o que é regime de caixa e o que é competência. É a confusão mais comum quando o empresário lê número contábil, e a que mais gera desconfiança."},
  {"t":"Sustentação e governança","meta":"Contrato mensal","p":"Novos clientes entrando, plano de contas mudando, banco trocando o formato do arquivo. A sustentação mantém tudo rodando sem que sua equipe precise virar equipe de TI.",
   "items":["Monitoramento das cargas e das regras de conciliação","Inclusão de novos clientes no painel","Ajuste de regras conforme novos padrões de lançamento","Evolução dos indicadores gerenciais"],
   "bh":"Entrega","bp":"Rotina estável, histórico preservado e um serviço gerencial que o escritório pode vender de forma recorrente."}
 ], cont_extra,
 [("Preciso trocar de ERP contábil?","Não. O trabalho parte do sistema que o escritório já usa. O Raio-X confirma a melhor forma de extração."),
  ("O painel pode levar a marca do meu escritório?","Sim, o painel pode ser apresentado aos seus clientes como serviço do escritório."),
  ("A conciliação substitui o contador?","Não. Ela elimina a conferência repetitiva e deixa para o profissional as exceções, que são onde está o julgamento técnico."),
  ("Como fica o sigilo dos dados dos meus clientes?","Acesso restrito por perfil, separação por cliente e tratamento conforme a LGPD fazem parte do desenho da solução.")],
 "Descubra quanto tempo sua equipe perde conferindo dados", "Comece pelo Raio-X de Dados Contábil: de 3 a 5 dias úteis, relatório priorizado e orçamento fechado.")

# ---------- VAREJO ----------
var_extra = '''
<section class="bg-navy"><div class="wrap split">
<div>
<h2>Margem de verdade, por canal</h2>
<p>Um prato que dá boa margem no salão pode dar prejuízo no delivery depois da comissão do aplicativo, da taxa de pagamento e da embalagem. Sem cruzar PDV, aplicativos e ficha técnica, isso não aparece em lugar nenhum.</p>
<p>A solução da TDBASES calcula o CMV a partir da ficha técnica e da compra real de insumos, e desconta os custos de cada canal para mostrar a margem que realmente sobra.</p>
</div>
<div>
<h3>Fontes que unificamos</h3>
<ul class="systems"><li>PDV do caixa</li><li>iFood</li><li>Rappi</li><li>Controle de estoque</li><li>Notas de compra</li><li>Fichas técnicas</li></ul>
<p class="fine">Integração por API, relatório exportado ou banco de dados, conforme o que cada sistema oferece. Marcas citadas apenas como referência técnica, sem parceria ou endosso.</p>
</div>
</div></section>

<section><div class="wrap">
<div class="head-block"><h2>Indicadores que o painel entrega</h2><p class="lede">O conjunto final é definido no Raio-X, conforme o tipo de operação.</p></div>
<div class="table-wrap"><table class="ind">
<thead><tr><th scope="col">Indicador</th><th scope="col">Pergunta que responde</th></tr></thead>
<tbody>
<tr><td>CMV real por produto ou prato</td><td>Quanto cada item custa de verdade, com base na ficha técnica e no preço pago pelos insumos.</td></tr>
<tr><td>Margem por canal de venda</td><td>Quanto sobra em cada canal depois de comissão, taxa de pagamento e embalagem.</td></tr>
<tr><td>Ticket médio por canal</td><td>Quanto o cliente gasta no salão, no balcão e em cada aplicativo, por dia e por horário.</td></tr>
<tr><td>Curva ABC de produtos</td><td>Quais itens sustentam o faturamento e quais só ocupam cardápio, estoque e espaço.</td></tr>
<tr><td>Divergência de estoque</td><td>Diferença entre o consumo teórico, calculado pelas vendas, e o que de fato saiu do estoque.</td></tr>
</tbody></table></div>
</div></section>
'''
segment("varejo-food-service.html","varejo","Dados para varejo, bares e restaurantes: CMV, margem e delivery | TDBASES",
 "Unifique PDV, iFood, Rappi e estoque num painel com CMV real, margem por produto ou prato e ticket médio por canal de venda.",
 "Varejo, bares e restaurantes",
 "Você vende no salão, no balcão e no aplicativo. Qual canal realmente paga a conta?",
 "A TDBASES unifica os dados do PDV, dos aplicativos de delivery e do estoque, e calcula CMV e margem reais por produto ou prato, com ticket médio por canal de venda.",
 "A rotina que a gente conhece",
 ["Faturamento subindo e o caixa do fim do mês não acompanhando.",
  "Comissão e taxas do aplicativo misturadas no extrato, sem saber quanto pesam em cada pedido.",
  "Ficha técnica feita na abertura da casa e nunca mais atualizada, enquanto o preço dos insumos mudou.",
  "CMV estimado por percentual de mercado, e não calculado com os seus números.",
  "Estoque que não fecha e ninguém sabe se é desperdício, erro de lançamento ou desvio.",
  "Preço de cardápio definido pelo concorrente da esquina, não pela margem do prato."],
 [
  {"t":"Raio-X de Dados do negócio","meta":"3 a 5 dias úteis","p":"Um diagnóstico rápido de onde estão seus dados de venda, compra e estoque, e do que já dá para calcular com eles.",
   "items":["Levantamento do PDV, dos aplicativos de delivery e do controle de estoque","Avaliação das fichas técnicas e do cadastro de produtos","Verificação de como taxas e comissões aparecem nos repasses","Identificação dos indicadores viáveis com o que já existe"],
   "bh":"Entrega","bp":"Relatório priorizado e orçamento fechado para a implementação."},
  {"t":"Unificação de dados e painel de margem","meta":"2 a 4 semanas, escopo fechado","p":"Construção da base única de vendas, compras e estoque, com cálculo de CMV e margem por item e por canal.",
   "items":["Integração do PDV, do iFood, do Rappi e do estoque","Cadastro de produtos padronizado entre canais","CMV calculado pela ficha técnica e pelo custo real dos insumos","Painel de margem, ticket médio e curva ABC por canal","Treinamento rápido para o dono e o gerente"],
   "bh":"O ponto que mais dá trabalho","bp":"O mesmo prato costuma ter nomes diferentes no PDV e em cada aplicativo. Padronizar esse cadastro é o que torna a comparação entre canais confiável."},
  {"t":"Sustentação e governança","meta":"Contrato mensal","p":"Cardápio muda, preço de insumo muda, aplicativo muda relatório. Sem manutenção, o painel começa a mostrar número errado em poucas semanas.",
   "items":["Monitoramento das cargas diárias","Atualização de fichas técnicas e cadastro de novos itens","Ajuste quando algum canal muda formato de dados","Evolução do painel conforme a operação cresce"],
   "bh":"Entrega","bp":"Margem acompanhada de perto, mês a mês, com histórico para comparar temporadas e cardápios."}
 ], var_extra,
 [("Serve para quem tem só uma loja?","Sim. O Raio-X mostra se o volume de dados e de decisões justifica a implementação no seu caso."),
  ("Preciso trocar de PDV?","Não. O trabalho parte dos sistemas que você já usa. O Raio-X confirma a melhor forma de extração de cada um."),
  ("Não tenho ficha técnica. E agora?","Dá para começar pelos itens de maior venda. A montagem das fichas faltantes entra no plano de implementação."),
  ("O painel funciona no celular?","Sim. O painel é pensado para ser consultado no dia a dia da operação, inclusive pelo celular.")],
 "Descubra quanto cada canal realmente deixa no seu caixa", "Comece pelo Raio-X de Dados: de 3 a 5 dias úteis, relatório priorizado e orçamento fechado.")

# ---------------- SOBRE ----------------
sobre = '''
<section class="page-hero"><div class="wrap">
<span class="crumb"><a href="index.html">Início</a> / Sobre</span>
<h1>Arquitetura de dados de instituição, aplicada ao seu negócio</h1>
<p class="lede">A TDBASES é a consultoria de engenharia e arquitetura de dados de Thales Dias Braga. A proposta é simples: levar para a pequena e média empresa o mesmo rigor usado em instituições que não podem errar.</p>
</div></section>

<section><div class="wrap split">
<div>
<h2>Quem está por trás</h2>
<p>Thales Dias Braga trabalha com dados há 20 anos, como DBA, analista e arquiteto de dados. A maior parte dessa trajetória foi construída no setor público de alta exigência, onde um número errado não é um incômodo, é um problema institucional.</p>
<p>Foram 13 anos construindo a solução de Business Intelligence da Polícia Federal em cooperação com a INTERPOL, projetos em sete países da América Latina e atuação em pesquisas oficiais de estatística pública. Nesse caminho ficou clara uma lacuna: as empresas menores têm os mesmos problemas de dados das grandes, mas quase nunca têm acesso ao mesmo nível de engenharia.</p>
<p>A TDBASES existe para fechar essa lacuna, com escopo fechado, linguagem clara e entregas que o dono do negócio consegue usar.</p>
</div>
<div>
<div class="callout"><p>Os mesmos princípios que sustentam um sistema de BI policial sustentam o painel de um escritório: origem rastreável, regra documentada e dado que alguém mantém.</p></div>
<p class="fine">THALES DIAS BRAGA CONSULTORIA EM TECNOLOGIA DA INFORMAÇÃO LTDA, CNPJ 66.785.647/0001-84.</p>
</div>
</div></section>

<section class="bg-paper"><div class="wrap">
<div class="head-block"><h2>Trajetória</h2></div>
<ol class="timeline">
<li><span class="when">2012 a 2025</span><div><h3>IAFIS Group Biometric and Forensics, Brasília</h3><p>Analista sênior de dados, DBA e arquiteto de dados na construção da solução de Business Intelligence da Polícia Federal brasileira, em cooperação com a INTERPOL. No mesmo período, projetos internacionais de dados no Brasil, Peru, Argentina, Panamá, Jamaica, Chile e Honduras.</p></div></li>
<li><span class="when">2025</span><div><h3>Publicação científica</h3><p>Artigo publicado pela Sociedade Brasileira de Computação (SBC), em julho de 2025.</p></div></li>
<li><span class="when">2025 a 2026</span><div><h3>IPEDF Codeplan</h3><p>Analista de dados no Instituto de Planejamento, Pesquisa e Estatística do Distrito Federal, no projeto InfoDF 2.0, apoiando pesquisas oficiais de larga escala, como a PDAD e a PED.</p></div></li>
<li><span class="when">Dezembro de 2026</span><div><h3>Mestrado na UnB</h3><p>Conclusão prevista do mestrado em Computação Aplicada, área de Ciência de Dados, pela Universidade de Brasília.</p></div></li>
</ol>
</div></section>

<section><div class="wrap">
<div class="head-block"><h2>Formação e certificações</h2></div>
<div class="creds">
<div><h3>Pós-graduação</h3><ul><li>Mestrado em Computação Aplicada, Ciência de Dados, UnB (em andamento)</li><li>Engenharia de Software</li><li>Gestão de Projetos</li><li>Big Data e Ciência de Dados</li><li>Banco de Dados</li></ul></div>
<div><h3>Certificações</h3><ul><li>Oracle Database Administration</li><li>Linux LPIC 2</li><li>ITIL Foundation</li></ul></div>
<div><h3>Idiomas</h3><ul><li>Português, nativo</li><li>Inglês, avançado</li><li>Espanhol, avançado</li></ul></div>
</div>
</div></section>

<section class="bg-navy"><div class="wrap">
<div class="head-block"><h2>Como a TDBASES trabalha</h2></div>
<div class="principles">
<div><h3>Diagnóstico antes de orçamento</h3><p>Nenhuma proposta de implementação sai sem o Raio-X. Orçar sem olhar os dados é chutar, e o cliente paga pelo chute.</p></div>
<div><h3>Escopo fechado e prazo definido</h3><p>Você sabe o que vai receber, quando e por quanto antes de começar. Mudança de escopo é conversada, não descoberta na fatura.</p></div>
<div><h3>Regra documentada</h3><p>Cada indicador tem origem e cálculo descritos. Se alguém perguntar de onde veio o número, a resposta existe por escrito.</p></div>
<div><h3>Proteção de dados desde o desenho</h3><p>Controle de acesso e uso mínimo de dados pessoais fazem parte da arquitetura desde o primeiro dia, e não de um ajuste posterior.</p></div>
</div>
</div></section>
''' + cta_band("Vamos olhar os seus dados?", "O Raio-X de Dados leva de 3 a 5 dias úteis e termina com um relatório priorizado e um orçamento fechado.")
page("sobre.html","Sobre a TDBASES e Thales Dias Braga | TDBASES",
 "20 anos em dados, 13 deles na solução de BI da Polícia Federal com a INTERPOL. Conheça a trajetória por trás da TDBASES.", sobre)

# ---------------- CONTATO ----------------
contato = f'''
<section class="page-hero"><div class="wrap">
<span class="crumb"><a href="index.html">Início</a> / Contato</span>
<h1>Agende o seu Raio-X de Dados</h1>
<p class="lede">Conte em poucas linhas como a sua empresa funciona hoje. A partir disso, você recebe a proposta do Raio-X com prazo e valor fechados.</p>
</div></section>

<section><div class="wrap contact-grid">
<div>
<form class="lead" id="lead" novalidate>
<div class="row2">
<div class="field"><label for="nome">Seu nome</label><input id="nome" name="nome" autocomplete="name" required></div>
<div class="field"><label for="empresa">Empresa</label><input id="empresa" name="empresa" autocomplete="organization" required></div>
</div>
<div class="row2">
<div class="field"><label for="contato">WhatsApp ou e-mail</label><input id="contato" name="contato" autocomplete="email" required></div>
<div class="field"><label for="segmento">Tipo de negócio</label>
<select id="segmento" name="segmento" required>
<option value="">Selecione</option>
<option value="advocacia">Escritório de advocacia</option>
<option value="contabilidade">Contabilidade</option>
<option value="varejo">Varejo, bar ou restaurante</option>
<option value="outro">Outro</option>
</select></div>
</div>
<div class="field"><label for="dor">O que mais incomoda hoje nos seus dados? <span class="hint">Opcional</span></label><textarea id="dor" name="dor" placeholder="Por exemplo: não sei qual área do escritório dá lucro, ou o relatório de fechamento é feito à mão."></textarea></div>
<label class="consent"><input type="checkbox" id="aceite" required><span>Concordo que a TDBASES use estes dados apenas para responder a este contato, conforme o aviso de privacidade abaixo.</span></label>
<div class="form-actions">
<button class="btn btn-gold" type="submit">Enviar pelo WhatsApp</button>
<button class="btn btn-navy" type="button" id="via-email">Enviar por e-mail</button>
</div>
<p class="status" id="status" role="status" aria-live="polite"></p>
</form>
</div>
<aside class="side-box">
<h3>O que acontece depois</h3>
<ol class="next">
<li>Você envia o formulário.</li>
<li>Uma conversa curta para entender sistemas, equipe e objetivo.</li>
<li>Você recebe a proposta do Raio-X, com prazo e valor fechados.</li>
</ol>
<h3>Prefere falar direto?</h3>
<div class="direct"><a href="https://wa.me/{WA}" rel="noopener">WhatsApp +55 61 99135-8553</a><a href="mailto:{EMAIL}">{EMAIL}</a></div>
</aside>
</div></section>

<section class="bg-paper" id="privacidade"><div class="wrap">
<div class="head-block"><h2>Aviso de privacidade</h2></div>
<p>Os dados informados neste formulário, como nome, empresa, contato e descrição da necessidade, são usados exclusivamente para responder à sua solicitação e preparar a proposta do Raio-X de Dados. A base legal é o procedimento preliminar relacionado a contrato, a pedido do titular, prevista no artigo 7º, inciso V, da LGPD.</p>
<p>Os dados não são vendidos nem compartilhados com terceiros para fins de marketing. Ao enviar pelo WhatsApp ou por e-mail, a mensagem trafega pelos serviços desses provedores. Você pode pedir acesso, correção ou exclusão dos seus dados a qualquer momento pelo e-mail <a href="mailto:{EMAIL}">{EMAIL}</a>.</p>
<p class="fine">Controlador: THALES DIAS BRAGA CONSULTORIA EM TECNOLOGIA DA INFORMAÇÃO LTDA, CNPJ 66.785.647/0001-84.</p>
</div></section>
'''
contato_js = '''<script>
(function(){
var f=document.getElementById('lead'),st=document.getElementById('status');
try{var p=new URLSearchParams(location.search).get('segmento');if(p){var s=document.getElementById('segmento');for(var i=0;i<s.options.length;i++){if(s.options[i].value===p){s.value=p;}}}}catch(e){}
function msg(){
 var n=f.nome.value.trim(),e=f.empresa.value.trim(),c=f.contato.value.trim(),sg=f.segmento,d=f.dor.value.trim();
 var miss=[];if(!n)miss.push('seu nome');if(!e)miss.push('a empresa');if(!c)miss.push('WhatsApp ou e-mail');if(!sg.value)miss.push('o tipo de negócio');
 if(miss.length){st.className='status err';st.textContent='Preencha '+miss.join(', ')+' para continuar.';return null;}
 if(!document.getElementById('aceite').checked){st.className='status err';st.textContent='Marque a concordância com o aviso de privacidade para enviar.';return null;}
 var t='Olá, quero agendar um Raio-X de Dados.\\n\\nNome: '+n+'\\nEmpresa: '+e+'\\nContato: '+c+'\\nTipo de negócio: '+sg.options[sg.selectedIndex].text;
 if(d)t+='\\nO que mais incomoda: '+d;
 return t;
}
f.addEventListener('submit',function(ev){ev.preventDefault();var t=msg();if(!t)return;st.className='status ok';st.textContent='Abrindo o WhatsApp com a sua mensagem pronta. É só enviar.';window.open('https://wa.me/''' + WA + '''?text='+encodeURIComponent(t),'_blank','noopener');});
document.getElementById('via-email').addEventListener('click',function(){var t=msg();if(!t)return;st.className='status ok';st.textContent='Abrindo o seu aplicativo de e-mail com a mensagem pronta.';location.href='mailto:''' + EMAIL + '''?subject='+encodeURIComponent('Raio-X de Dados: '+f.empresa.value.trim())+'&body='+encodeURIComponent(t);});
})();
</script>'''
page("contato.html","Agendar Raio-X de Dados | TDBASES",
 "Agende o Raio-X de Dados da TDBASES: diagnóstico de 3 a 5 dias úteis com relatório priorizado e orçamento fechado.", contato, extra_js=contato_js)

# robots & sitemap
pages = ["","advocacia.html","contabilidade.html","varejo-food-service.html","sobre.html","contato.html"]
with open(os.path.join(OUT,"sitemap.xml"),"w") as f:
    f.write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'+"".join(f"<url><loc>{BASE}/{p}</loc></url>\n" for p in pages)+"</urlset>\n")
with open(os.path.join(OUT,"robots.txt"),"w") as f:
    f.write(f"User-agent: *\nAllow: /\nSitemap: {BASE}/sitemap.xml\n")
print("ok")
