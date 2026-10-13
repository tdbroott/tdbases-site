'use strict';

const nodemailer = require('nodemailer');

const ORIGENS = [
  'https://tdbases.com.br',
  'https://www.tdbases.com.br',
  'http://localhost:3000'
];

// Deploys de preview do Vercel usam outro endereço; aceita apenas o do próprio deploy.
function origemPermitida(origem) {
  if (ORIGENS.includes(origem)) return true;
  const proprios = [process.env.VERCEL_URL, process.env.VERCEL_BRANCH_URL]
    .filter(Boolean)
    .map(function (h) { return 'https://' + h; });
  return proprios.includes(origem);
}

function corpoDaRequisicao(req) {
  if (req.body && typeof req.body === 'object') return req.body;
  if (typeof req.body === 'string') {
    try {
      const j = JSON.parse(req.body);
      return j && typeof j === 'object' ? j : {};
    } catch (e) {
      return {};
    }
  }
  return {};
}

const SEGMENTOS = {
  advocacia: 'Escritório de advocacia',
  contabilidade: 'Contabilidade',
  varejo: 'Varejo, bar ou restaurante',
  outro: 'Outro'
};

function limpar(valor, max) {
  return String(valor == null ? '' : valor)
    .replace(/[\u0000-\u0008\u000B\u000C\u000E-\u001F\u007F]/g, ' ')
    .trim()
    .slice(0, max);
}

function umaLinha(valor) {
  return valor.replace(/[\r\n]+/g, ' ');
}

function contatoValido(c) {
  if (/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(c)) return true;
  return c.replace(/\D/g, '').length >= 10;
}

module.exports = async function handler(req, res) {
  res.setHeader('Cache-Control', 'no-store');

  if (req.method !== 'POST') {
    res.setHeader('Allow', 'POST');
    return res.status(405).json({ ok: false, erro: 'metodo' });
  }

  const origem = req.headers.origin;
  if (origem && !origemPermitida(origem)) {
    return res.status(403).json({ ok: false, erro: 'origem' });
  }

  const b = corpoDaRequisicao(req);

  // Campo isca: robôs preenchem, pessoas não veem. Responde como sucesso para não dar pista.
  if (limpar(b.website, 200)) {
    return res.status(200).json({ ok: true });
  }

  const nome = limpar(b.nome, 120);
  const empresa = limpar(b.empresa, 160);
  const contato = limpar(b.contato, 160);
  const segmento = Object.prototype.hasOwnProperty.call(SEGMENTOS, b.segmento) ? b.segmento : '';
  const dor = limpar(b.dor, 1500);

  if (!nome || !empresa || !contatoValido(contato) || !segmento || b.consent !== true) {
    return res.status(400).json({ ok: false, erro: 'dados' });
  }

  const { SMTP_HOST, SMTP_USER, SMTP_PASS } = process.env;
  if (!SMTP_HOST || !SMTP_USER || !SMTP_PASS) {
    console.error('contato: variaveis SMTP ausentes');
    return res.status(500).json({ ok: false, erro: 'config' });
  }

  const destino = process.env.MAIL_TO || SMTP_USER;
  const porta = Number(process.env.SMTP_PORT || 465);
  const agora = new Date().toISOString();

  const transporte = nodemailer.createTransport({
    host: SMTP_HOST,
    port: porta,
    secure: porta === 465,
    auth: { user: SMTP_USER, pass: SMTP_PASS }
  });

  const corpo = [
    'Novo contato pelo site tdbases.com.br',
    '',
    'Nome: ' + nome,
    'Empresa: ' + empresa,
    'Contato: ' + contato,
    'Tipo de negócio: ' + SEGMENTOS[segmento],
    'O que mais incomoda: ' + (dor || '(não informado)'),
    '',
    'Consentimento registrado em ' + agora + ' (aviso de privacidade, versão 2026-10-13).'
  ].join('\n');

  const mensagem = {
    from: '"Site TDBASES" <' + SMTP_USER + '>',
    to: destino,
    subject: 'Raio-X de Dados: ' + umaLinha(empresa),
    text: corpo
  };
  if (/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(contato)) {
    mensagem.replyTo = contato;
  }

  try {
    await transporte.sendMail(mensagem);
  } catch (e) {
    console.error('contato: falha no envio SMTP', e && e.code ? e.code : 'desconhecido');
    return res.status(502).json({ ok: false, erro: 'envio' });
  }

  return res.status(200).json({ ok: true });
};
