# Site TDBASES (www.tdbases.com.br)

Site estático publicado no Vercel a partir da branch main. Cada página é um HTML autocontido, com CSS embutido. A única parte executada no servidor é a função do formulário de contato.

## Estrutura

- Páginas institucionais: index.html, advocacia.html, contabilidade.html, varejo-food-service.html, sobre.html, contato.html, demos.html, privacidade.html e 404.html.
- api/contato.js: função serverless que recebe o formulário de contato.
- package.json: única dependência, o nodemailer, usado pela função.
- vercel.json: cabeçalhos de segurança e cache das imagens.
- img/: miniaturas das demonstrações e a imagem de compartilhamento (og-tdbases.png).
- sitemap.xml e robots.txt, com URLs em www.tdbases.com.br, que é o endereço canônico.
- demo-*.html e demo/: demonstrações, descritas abaixo.

Os HTMLs da raiz são a fonte de verdade. O arquivo _build.py está defasado (usa outro e-mail e caminhos de outra máquina) e não deve ser executado: ele sobrescreveria as páginas com uma versão antiga.

## Formulário de contato

contato.html envia os dados por fetch para /api/contato. A função valida os campos, descarta envios de robôs pelo campo isca e entrega a mensagem por SMTP ao e-mail corporativo, sem gravar em banco de dados. Se o envio falhar, a página mostra links com a mensagem já preenchida para WhatsApp e e-mail, e o botão "Prefiro enviar pelo WhatsApp" continua disponível o tempo todo.

Variáveis de ambiente, em Vercel, Settings, Environment Variables:

- SMTP_HOST: servidor SMTP do e-mail corporativo.
- SMTP_USER: usuário da caixa que envia.
- SMTP_PASS: senha ou senha de aplicativo dessa caixa.
- MAIL_TO: endereço que recebe os contatos (contato@tdbases.com.br).
- SMTP_PORT: opcional, padrão 465 (SSL). Use 587 se o provedor exigir STARTTLS.

Sem essas variáveis a função responde erro 500 e a página oferece WhatsApp e e-mail.

Respostas da função: 405 para método diferente de POST, 403 para origem não permitida, 400 para dados inválidos, 500 para configuração ausente, 502 para falha no SMTP e 200 para sucesso. A versão do aviso de privacidade aceito é registrada no texto do e-mail; ao mudar a política, atualize a data no topo de privacidade.html e a versão em api/contato.js.

## Analytics

Vercel Web Analytics, só visualizações de página, sem eventos personalizados. O snippet fica antes de </head> nas páginas institucionais e não é usado nas demonstrações. Ele só funciona depois de habilitar o Analytics no painel do Vercel; localmente, /_vercel/insights/script.js responde 404, o que é esperado.

## Privacidade

privacidade.html descreve dados, finalidades, bases legais, prazos (contatos sem contratação são guardados por até 6 meses após o último contato), operadores (Vercel, Zoho e WhatsApp) e direitos do titular. O resumo da página de contato remete a ela.

## Pendências

1. Hospedar as fontes (Spectral e IBM Plex Sans) no próprio domínio, em vez do Google Fonts, por desempenho e para retirar o Google da lista de terceiros.
2. Cadastrar o site no Google Search Console e enviar o sitemap.xml.
3. Revisão jurídica do texto da política de privacidade.

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
