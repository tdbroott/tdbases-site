# Site TDBASES (tdbases.com.br)

Site estático, sem dependência de servidor de aplicação. Cada página é um HTML autocontido (CSS embutido), o que permite publicar em qualquer hospedagem estática.

## Estrutura

index.html, advocacia.html, contabilidade.html, varejo-food-service.html, sobre.html, contato.html, sitemap.xml, robots.txt.

## Publicação

Opções equivalentes para site estático: Cloudflare Pages, Netlify, GitHub Pages ou a hospedagem compartilhada do registro do domínio. Em qualquer uma, aponte o domínio tdbases.com.br (registro no Registro.br) para o serviço escolhido e ative HTTPS.

## Formulário de contato

O formulário não depende de backend: monta a mensagem e abre o WhatsApp (+55 61 99135-8553) ou o cliente de e-mail do visitante. Trade-off: não há registro automático do lead, e parte dos visitantes abandona na troca de aplicativo. Para captura com histórico, substituir o handler de submit por um POST para Formspree, Netlify Forms ou uma função serverless que grave numa planilha ou banco, mantendo o aviso de privacidade.

## Pendências antes de publicar

1. Avaliar a hospedagem local das fontes (Spectral e IBM Plex Sans) em vez do Google Fonts, por desempenho e coerência com o discurso de LGPD.
2. Cadastrar o site no Google Search Console e enviar o sitemap.xml.
3. Criar e-mail no domínio (contato@tdbases.com.br) e trocar o endereço atual no build.

## Demonstrações

A página demos.html reúne os painéis demonstrativos e o exemplo de relatório do Raio-X. Todos usam empresas fictícias e dados gerados por programa.

Arquivos publicados na raiz: demo-advocacia.html, demo-contabilidade.html, demo-varejo.html e demo-raio-x.html. Cada um é um HTML único, sem dependências externas, que abre por duplo clique.

Código-fonte em demo/:

- demo/core: CSS e JavaScript comuns (formatação, gráficos em SVG, tabelas com exportação CSV, abas e filtros).
- demo/contabilidade, demo/varejo, demo/raio-x: template, aplicação, gerador de dados e modelo de dados de cada demonstração.
- demo/advocacia: gerador e modelo de dados do painel jurídico. Esse painel é mantido como arquivo próprio; o gerador só reescreve o bloco de dados e a URL canônica.
- demo/build_demos.py: monta contabilidade, varejo e Raio-X na raiz, embutindo o núcleo, a aplicação e os dados.
- demo/verificar_demos.py: reconciliação de totais, recálculo em Python, textos, links, rede e layout em 375 e 1280 px.

Para alterar uma demonstração, edite os arquivos em demo/ e rode:

    python3 demo/build_demos.py
    python3 demo/verificar_demos.py

A verificação precisa do Playwright para Python com Chromium. As miniaturas da página de demonstrações ficam em img/demos.
