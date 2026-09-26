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
