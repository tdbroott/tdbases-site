#!/usr/bin/env python3
"""
Monta os painéis demonstrativos da TDBASES como arquivos HTML únicos.

O código-fonte fica separado (demo/core para o que é comum, demo/<demo>/ para o
que é específico), e esta etapa junta tudo em um arquivo autocontido na raiz
do site, com CSS, JavaScript e dados embutidos. Assim cada demo abre por duplo
clique, não faz chamadas de rede e continua independente das demais páginas.

Uso:
    python3 demo/build_demos.py                 # gera todas as demos
    python3 demo/build_demos.py contabilidade   # gera só uma
"""
import importlib.util
import json
import sys
from pathlib import Path

DEMO = Path(__file__).resolve().parent
RAIZ = DEMO.parent
BASE_URL = "https://www.tdbases.com.br/"

# pasta de origem -> arquivo publicado na raiz
DEMOS = {
    "contabilidade": "demo-contabilidade.html",
    "varejo": "demo-varejo.html",
    "raio-x": "demo-raio-x.html",
}


def carregar_gerador(pasta):
    caminho = pasta / "gerar_dados.py"
    if not caminho.exists():
        return None
    spec = importlib.util.spec_from_file_location(f"gerador_{pasta.name}".replace("-", "_"), caminho)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def montar(nome):
    pasta = DEMO / nome
    saida = RAIZ / DEMOS[nome]
    html = (pasta / "template.html").read_text(encoding="utf-8")
    core_css = (DEMO / "core" / "demo-core.css").read_text(encoding="utf-8")
    core_js = (DEMO / "core" / "demo-core.js").read_text(encoding="utf-8")
    app_js = (pasta / "app.js").read_text(encoding="utf-8") if (pasta / "app.js").exists() else ""
    extra_css = (pasta / "app.css").read_text(encoding="utf-8") if (pasta / "app.css").exists() else ""
    for trecho, rotulo in ((core_js, "demo-core.js"), (app_js, "app.js")):
        if "</script" in trecho.lower():
            raise SystemExit(f"{rotulo} contém </script>, o que quebraria o HTML")
    dados = "{}"
    gen = carregar_gerador(pasta)
    if gen is not None:
        d = gen.gerar()
        (pasta / "dados.json").write_text(json.dumps(d, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
        dados = json.dumps(d, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    canonical = BASE_URL + DEMOS[nome]
    trocas = {
        "{{CORE_CSS}}": core_css + "\n" + extra_css,
        "{{CORE_JS}}": core_js,
        "{{APP_JS}}": app_js,
        "{{DADOS}}": dados,
        "{{CANONICAL}}": canonical,
    }
    for k, v in trocas.items():
        html = html.replace(k, v)
    restante = [k for k in trocas if k in html]
    if restante:
        raise SystemExit(f"marcadores não substituídos em {nome}: {restante}")
    saida.write_text(html, encoding="utf-8")
    tam = len(html.encode("utf-8"))
    print(f"{saida.name}: {tam / 1024:.1f} KB (dados {len(dados.encode('utf-8')) / 1024:.1f} KB)")


if __name__ == "__main__":
    alvos = sys.argv[1:] or list(DEMOS)
    for a in alvos:
        montar(a)
