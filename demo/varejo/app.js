(function(){
"use strict";
var D=JSON.parse(document.getElementById("dados-demo").textContent);
var MS=TD.meses(D.meta.meses),NM=MS.n,L=NM-1;
var IT=D.itens,NI=IT.length,NC=D.canais.length,INS=D.insumos,NS=INS.length;
var FE=[0,0.5,1,1];
var PER=MS.periodos([12,6,3,24]);
var CUSTO_C=D.custo.map(function(a){return a.map(function(v){return Math.round(v*100);});});
var EMB_C=D.embalagem.map(function(v){return Math.round(v*100);});
var PROMO={};D.promo.forEach(function(p){PROMO[(p[0]*NC+p[1])*NM+p[2]]=p[3];});
var COR_CANAL=["#1B3556","#5B7FA6","#B07D1F","#7A5C2C"];

document.getElementById("sub-ref").textContent="Painel de vendas, margem e estoque. Histórico de "+MS.ext(0)+" a "+MS.ext(L)+".";
var selPer=document.getElementById("f-per"),selCanal=document.getElementById("f-canal"),selCat=document.getElementById("f-cat");
TD.preencher(selPer,PER.map(function(p){return [p.id,p.lab];}));
TD.preencher(selCanal,[["-1","Todos os canais"]].concat(D.canais.map(function(c,i){return [String(i),c];})));
TD.preencher(selCat,[["-1","Todas as categorias"]].concat(D.categorias.map(function(c,i){return [String(i),c];})));

function novo(){return {q:0,bruto:0,desc:0,net:0,cmv:0,com:0,tx:0,emb:0,mc:0};}
function soma(a,b){a.q+=b.q;a.bruto+=b.bruto;a.desc+=b.desc;a.net+=b.net;a.cmv+=b.cmv;a.com+=b.com;a.tx+=b.tx;a.emb+=b.emb;a.mc+=b.mc;}
function linha(it,c,m){
 var q=D.Q[it][c][m];if(!q)return null;
 var o=novo();o.q=q;o.bruto=q*D.P[it][c][m];o.desc=PROMO[(it*NC+c)*NM+m]||0;o.net=o.bruto-o.desc;
 o.cmv=q*CUSTO_C[it][m];o.com=o.net*D.comissao[c];o.tx=o.net*D.taxa_pag[c];o.emb=q*EMB_C[IT[it][1]]*FE[c];
 o.mc=o.net-o.cmv-o.com-o.tx-o.emb;return o;
}
function periodoAnt(ms){var n=ms.length,p=[];for(var k=ms[0]-n;k<ms[0];k++)if(k>=0)p.push(k);return p.length===n?p:null;}

function calcular(F){
 var per=PER.filter(function(p){return p.id===F.per;})[0]||PER[0],ms=per.m,n=ms.length,prev=periodoAnt(ms);
 var canais=[];for(var c=0;c<NC;c++)if(F.canal<0||F.canal===c)canais.push(c);
 var itens=[];for(var i=0;i<NI;i++)if(F.cat<0||IT[i][1]===F.cat)itens.push(i);
 var M={per:per,ms:ms,prev:prev,canais:canais,itens:itens,F:F,tot:novo(),porCanal:[],porItem:{},porIC:{},porCat:[],mes:[],itemPrev:{}};
 for(c=0;c<NC;c++)M.porCanal.push(novo());
 for(i=0;i<D.categorias.length;i++)M.porCat.push(novo());
 ms.forEach(function(){M.mes.push(novo());});
 itens.forEach(function(it){
  M.porItem[it]=novo();M.itemPrev[it]=novo();
  canais.forEach(function(c){
   var k=it*NC+c,acc=novo();
   ms.forEach(function(m,j){var o=linha(it,c,m);if(!o)return;soma(acc,o);soma(M.mes[j],o);});
   M.porIC[k]=acc;soma(M.porItem[it],acc);soma(M.porCanal[c],acc);soma(M.porCat[IT[it][1]],acc);soma(M.tot,acc);
   if(prev)prev.forEach(function(m){var o=linha(it,c,m);if(o)soma(M.itemPrev[it],o);});
  });
 });
 // pedidos (todas as categorias)
 M.ped=0;M.recCel=0;M.cel=[];for(var d=0;d<7;d++){M.cel.push([]);for(var f=0;f<3;f++)M.cel[d].push({r:0,p:0});}
 M.pedCanal=TD.zeros(NC);M.recCanal=TD.zeros(NC);
 ms.forEach(function(m){canais.forEach(function(c){var x=D.cel[m][c];for(var k=0;k<21;k++){var cel=M.cel[Math.floor(k/3)][k%3];cel.r+=x[0][k];cel.p+=x[1][k];M.ped+=x[1][k];M.recCel+=x[0][k];M.pedCanal[c]+=x[1][k];M.recCanal[c]+=x[0][k];}});});
 // receita de todos os itens nos canais filtrados, para reconciliar com os pedidos
 M.netTodos=0;for(i=0;i<NI;i++)canais.forEach(function(c){ms.forEach(function(m){var o=linha(i,c,m);if(o)M.netTodos+=o.net;});});
 // ABC
 M.abc=itens.filter(function(it){return M.porItem[it].net>0;}).sort(function(a,b){return M.porItem[b].net-M.porItem[a].net||a-b;});
 var acc=0;M.cum=M.abc.map(function(it){acc+=M.porItem[it].net;return M.tot.net?acc/M.tot.net:0;});
 // estoque: consumo teórico com todas as vendas
 var m0=ms[0],m1=ms[n-1];
 M.est=INS.map(function(x,s){
  var teo=0,comp=0,preco=0;
  ms.forEach(function(m){comp+=D.compras[s][m];preco+=D.preco_ins[s][m];});
  preco/=n;
  var ei=m0===0?D.ei0[s]:D.ef[s][m0-1],ef=D.ef[s][m1];
  return {s:s,teo:0,real:ei+comp-ef,preco:preco,comp:comp};
 });
 for(i=0;i<NI;i++){ms.forEach(function(m){var q=0;for(var c2=0;c2<NC;c2++)q+=D.Q[i][c2][m];if(!q)return;D.ficha[i].forEach(function(fq){M.est[fq[0]].teo+=q*fq[1];});});}
 M.est.forEach(function(e){e.div=e.real-e.teo;e.pct=e.teo?e.div/e.teo:0;e.valor=e.div*e.preco;e.vTeo=e.teo*e.preco;e.vReal=e.real*e.preco;});
 return M;
}

var R=function(c){return c/100;};
function brlc(c){return TD.brl(c/100);}
function brlcC(c){return TD.brlC(c/100);}
function pctOf(a,b){return b?a/b:0;}

/* ---------- visão geral ---------- */
function renderGeral(){
 var M=TD.M,t=M.tot;
 TD.kpis("kpis",[
  {l:"Faturamento",v:brlcC(t.net),s:t.desc?"Após "+brlcC(t.desc)+" em promoções":"Sem promoções no recorte"},
  {l:"Pedidos",v:TD.n0(M.ped),s:M.F.cat>=0?"Todos os pedidos dos canais filtrados":"Média de "+TD.n0(M.ped/(M.ms.length*30.4))+" por dia"},
  {l:"Ticket médio",v:M.ped?TD.brl2(R(M.recCel)/M.ped):"Sem pedidos",s:"Por pedido, todas as categorias"},
  {l:"CMV",v:t.net?TD.pct(t.cmv/t.net):"Sem venda",s:"Custo pela ficha técnica",cls:t.net&&t.cmv/t.net>0.32?"risco":""},
  {l:"Margem de contribuição",v:t.net?TD.pct(t.mc/t.net):"Sem venda",s:brlcC(t.mc)+" no período",cls:t.mc<0?"risco":""}
 ]);
 var A=[];
 // 1. itens com margem baixa por canal
 var baixos=[];Object.keys(M.porIC).forEach(function(k){var o=M.porIC[k];if(o.net>0&&o.mc/o.net<0.10)baixos.push(+k);});
 baixos.sort(function(a,b){return M.porIC[a].mc/M.porIC[a].net-M.porIC[b].mc/M.porIC[b].net;});
 if(baixos.length){
  var k0=baixos[0],it0=Math.floor(k0/NC),c0=k0%NC,o0=M.porIC[k0];
  var sal=M.porIC[it0*NC]||(function(){var a=novo();M.ms.forEach(function(m){var o=linha(it0,0,m);if(o)soma(a,o);});return a;})();
  A.push({t:"Prato que quase não deixa margem",p:IT[it0][0]+" no "+D.canais[c0].toLowerCase()+" deixou "+TD.pct(o0.mc/o0.net)+" de margem de contribuição no período ("+brlc(o0.mc)+")"+(sal.net?"; no salão, o mesmo prato deixou "+TD.pct(sal.mc/sal.net)+".":".")+(baixos.length>1?" Há "+baixos.length+" pares de item e canal abaixo de 10%.":""),a:o0.desc?"Rever a promoção ou o preço desse prato no aplicativo.":"Rever o preço desse prato no canal."});
 }else A.push({t:"Margem por item e canal",p:"Nenhum item ficou abaixo de 10% de margem de contribuição em nenhum canal do recorte.",a:"Acompanhar quando o preço dos insumos subir."});
 // 2. CMV em alta
 var u3=M.ms.slice(-3),a3=u3.map(function(m){return m-12;}).filter(function(m){return m>=0;});
 if(a3.length<3)a3=M.ms.slice(0,3);
 var cU=novo(),cA=novo();M.itens.forEach(function(it){M.canais.forEach(function(c){u3.forEach(function(m){var o=linha(it,c,m);if(o)soma(cU,o);});a3.forEach(function(m){var o=linha(it,c,m);if(o)soma(cA,o);});});});
 var subida=INS.map(function(x,s){var gU=0;u3.forEach(function(m){gU+=D.preco_ins[s][m];});var gA=0;a3.forEach(function(m){gA+=D.preco_ins[s][m];});return {s:s,v:gU/gA-1,peso:M.est[s].vTeo};}).filter(function(x){return x.peso>0;});
 var gasto=TD.soma(subida.map(function(x){return x.peso;}));
 var top=subida.filter(function(x){return x.peso/gasto>0.03;}).sort(function(a,b){return b.v-a.v;}).slice(0,2);
 var rev=D.meta.revisao_preco;
 A.push({t:"CMV subindo sem reajuste de cardápio",p:"O CMV foi de "+TD.pct(pctOf(cU.cmv,cU.net))+" em "+MS.ext(u3[0])+" a "+MS.ext(u3[u3.length-1])+", contra "+TD.pct(pctOf(cA.cmv,cA.net))+" em "+MS.ext(a3[0])+" a "+MS.ext(a3[a3.length-1])+". Os insumos de peso que mais subiram foram "+top.map(function(x){return INS[x.s][0].toLowerCase()+" (+"+TD.pct(x.v,0)+")";}).join(" e ")+". O último reajuste do cardápio foi em "+MS.ext(rev)+".",a:"Revisar preço dos pratos que usam esses insumos, começando pela classe A."});
 // 3. estoque
 var ed=M.est.slice().sort(function(a,b){return b.valor-a.valor;}).slice(0,2);
 A.push({t:"Estoque saindo sem venda",p:ed.map(function(e){return INS[e.s][0]+" saiu "+TD.pct(e.pct)+" a mais do que as vendas explicam, cerca de "+TD.brl(e.valor);}).join("; ")+" no período.",a:"Conferir porcionamento, armazenamento e lançamento de compras desses itens."});
 TD.achados("achados",A);
 var rot=M.ms.map(MS.lab);
 TD.linhas(document.getElementById("ch-geral"),{rotulos:rot,series:[{nome:"Margem de contribuição",valores:M.mes.map(function(o){return pctOf(o.mc,o.net);}),cor:"#1B3556"},{nome:"CMV",valores:M.mes.map(function(o){return pctOf(o.cmv,o.net);}),cor:"#B07D1F",tracejado:true,marca:"square"}],fmt:function(v){return TD.pct(v,0);},min:0,max:0.8,label:"Linhas do CMV e da margem de contribuição em percentual do faturamento, por mês, de "+M.per.desc+"."});
 TD.legenda(document.getElementById("lg-geral"),[{nome:"Margem de contribuição (linha contínua, círculos)",cor:"#1B3556",tipo:"linha"},{nome:"CMV (linha tracejada, quadrados)",cor:"#B07D1F",tipo:"linha",tracejado:true,marca:"square"}]);
 var p0=M.mes[0],p1=M.mes[M.mes.length-1];
 document.getElementById("cap-geral").textContent="CMV de "+TD.pct(pctOf(p0.cmv,p0.net))+" em "+MS.ext(M.ms[0])+" e "+TD.pct(pctOf(p1.cmv,p1.net))+" em "+MS.ext(M.ms[M.ms.length-1])+". Margem de contribuição de "+TD.pct(pctOf(p0.mc,p0.net))+" para "+TD.pct(pctOf(p1.mc,p1.net))+".";
}

/* ---------- canais ---------- */
function renderCanal(){
 var M=TD.M,t=M.tot;
 var cols=[{l:"Canal",v:function(c){return D.canais[c];}},
  {l:"Bruto",num:true,v:function(c){return R(M.porCanal[c].bruto);},f:function(c){return brlc(M.porCanal[c].bruto);}},
  {l:"Promoções",num:true,v:function(c){return R(M.porCanal[c].desc);},f:function(c){return M.porCanal[c].desc?brlc(-M.porCanal[c].desc):"";}},
  {l:"Faturamento",num:true,v:function(c){return R(M.porCanal[c].net);},f:function(c){return brlc(M.porCanal[c].net);}},
  {l:"CMV",num:true,v:function(c){return R(M.porCanal[c].cmv);},f:function(c){return brlc(-M.porCanal[c].cmv);}},
  {l:"Comissão",num:true,v:function(c){return R(M.porCanal[c].com);},f:function(c){return M.porCanal[c].com?brlc(-M.porCanal[c].com):"";}},
  {l:"Taxa",num:true,v:function(c){return R(M.porCanal[c].tx);},f:function(c){return brlc(-M.porCanal[c].tx);}},
  {l:"Embalagem",num:true,v:function(c){return R(M.porCanal[c].emb);},f:function(c){return M.porCanal[c].emb?brlc(-M.porCanal[c].emb):"";}},
  {l:"Margem",num:true,v:function(c){return R(M.porCanal[c].mc);},f:function(c){return brlc(M.porCanal[c].mc);},cls:function(c){return M.porCanal[c].mc<0?"neg":"";}},
  {l:"Margem %",num:true,v:function(c){return pctOf(M.porCanal[c].mc,M.porCanal[c].net);},f:function(c){return TD.pct(pctOf(M.porCanal[c].mc,M.porCanal[c].net));},csv:function(c){return Math.round(pctOf(M.porCanal[c].mc,M.porCanal[c].net)*1000)/10;}},
  {l:"Pedidos",num:true,v:function(c){return M.pedCanal[c];},f:function(c){return TD.n0(M.pedCanal[c]);}},
  {l:"Ticket",num:true,v:function(c){return M.pedCanal[c]?R(M.recCanal[c])/M.pedCanal[c]:0;},f:function(c){return M.pedCanal[c]?TD.brl2(R(M.recCanal[c])/M.pedCanal[c]):"";}}];
 TD.tabela("canais",cols,M.canais,{el:"tb-canais",cls:"fix1",rowHeader:true,caption:"Composição da margem por canal de venda",foot:["Total",brlc(t.bruto),t.desc?brlc(-t.desc):"",brlc(t.net),brlc(-t.cmv),t.com?brlc(-t.com):"",brlc(-t.tx),t.emb?brlc(-t.emb):"",brlc(t.mc),TD.pct(pctOf(t.mc,t.net)),TD.n0(M.ped),M.ped?TD.brl2(R(M.recCel)/M.ped):""]});
 var alvo=M.canais.length===1?M.porCanal[M.canais[0]]:t,nome=M.canais.length===1?D.canais[M.canais[0]]:"todos os canais";
 document.getElementById("h-cascata").textContent="Para onde vai cada real vendido: "+nome.toLowerCase();
 var passos=[{lab:"Faturamento bruto",v:R(alvo.bruto),total:true}];
 if(alvo.desc)passos.push({lab:"Promoções",v:-R(alvo.desc)});
 passos.push({lab:"CMV",v:-R(alvo.cmv)});
 if(alvo.com)passos.push({lab:"Comissão",v:-R(alvo.com)});
 passos.push({lab:"Taxa de pagamento",v:-R(alvo.tx)});
 if(alvo.emb)passos.push({lab:"Embalagem",v:-R(alvo.emb)});
 passos.push({lab:"Margem de contribuição",v:R(alvo.mc),total:true});
 TD.cascata(document.getElementById("ch-cascata"),passos,{fmt:TD.brlC,label:"Cascata do faturamento bruto até a margem de contribuição em "+nome+": "+passos.map(function(p){return p.lab+" "+TD.brlC(p.v);}).join(", ")+"."});
 document.getElementById("lg-cascata").innerHTML='<li><svg width="14" height="14" aria-hidden="true"><rect width="14" height="14" fill="#1B3556"/></svg>Totais</li><li><svg width="14" height="14" aria-hidden="true"><defs>'+TD.hach("lgc","#9B2C2C")+'</defs><rect width="14" height="14" fill="url(#lgc)"/></svg>Deduções (hachurado)</li>';
 document.getElementById("cap-cascata").textContent="De cada R$ 100 de faturamento bruto, "+(alvo.desc?"R$ "+TD.n1(100*alvo.desc/alvo.bruto)+" vão para promoções, ":"")+"R$ "+TD.n1(100*alvo.cmv/alvo.bruto)+" para insumos, "+(alvo.com?"R$ "+TD.n1(100*alvo.com/alvo.bruto)+" para comissão, ":"")+"R$ "+TD.n1(100*alvo.tx/alvo.bruto)+" para taxa de pagamento"+(alvo.emb?", R$ "+TD.n1(100*alvo.emb/alvo.bruto)+" para embalagem":"")+" e ficam R$ "+TD.n1(100*alvo.mc/alvo.bruto)+" de margem de contribuição.";
 var baixos=Object.keys(M.porIC).map(Number).filter(function(k){var o=M.porIC[k];return o.net>0&&o.mc/o.net<0.10;});
 var u=function(k,c){var o=M.porIC[k];return o.q?R(o[c])/o.q:0;};
 TD.tabela("baixa",[
  {l:"Item",v:function(k){return IT[Math.floor(k/NC)][0];}},
  {l:"Canal",v:function(k){return D.canais[k%NC];}},
  {l:"Qtd.",num:true,v:function(k){return M.porIC[k].q;},f:function(k){return TD.n0(M.porIC[k].q);}},
  {l:"Preço",num:true,v:function(k){return u(k,"bruto");},f:function(k){return TD.brl2(u(k,"bruto"));}},
  {l:"Promoção por un.",num:true,v:function(k){return u(k,"desc");},f:function(k){return u(k,"desc")?TD.brl2(-u(k,"desc")):"";}},
  {l:"Custo por un.",num:true,v:function(k){return u(k,"cmv");},f:function(k){return TD.brl2(-u(k,"cmv"));}},
  {l:"Comissão e taxa por un.",num:true,v:function(k){return u(k,"com")+u(k,"tx");},f:function(k){return TD.brl2(-(u(k,"com")+u(k,"tx")));}},
  {l:"Embalagem por un.",num:true,v:function(k){return u(k,"emb");},f:function(k){return u(k,"emb")?TD.brl2(-u(k,"emb")):"";}},
  {l:"Margem por un.",num:true,v:function(k){return u(k,"mc");},f:function(k){return TD.brl2(u(k,"mc"));},cls:function(k){return M.porIC[k].mc<0?"neg":"";}},
  {l:"Margem %",num:true,v:function(k){return pctOf(M.porIC[k].mc,M.porIC[k].net);},f:function(k){return TD.pct(pctOf(M.porIC[k].mc,M.porIC[k].net));},cls:function(k){return M.porIC[k].mc<0?"neg":"";},csv:function(k){return Math.round(pctOf(M.porIC[k].mc,M.porIC[k].net)*1000)/10;}},
  {l:"Margem total",num:true,v:function(k){return R(M.porIC[k].mc);},f:function(k){return brlc(M.porIC[k].mc);},cls:function(k){return M.porIC[k].mc<0?"neg":"";}}
 ],baixos,{el:"tb-baixa",cls:"fix1",sortable:true,sort:9,dir:1,rowHeader:true,caption:"Pares de item e canal com margem de contribuição abaixo de 10%"});
 if(!baixos.length)document.getElementById("tb-baixa").innerHTML='<p class="nota" style="padding:14px 16px;margin:0">Nenhum item abaixo de 10% de margem de contribuição no recorte.</p>';
}

/* ---------- CMV ---------- */
function renderCMV(){
 var M=TD.M,mU=M.ms[M.ms.length-1],m0=M.ms[0];
 document.getElementById("nota-cmv").textContent="Período: "+M.per.desc+(M.prev?"; comparação com "+MS.ext(M.prev[0])+" a "+MS.ext(M.prev[M.prev.length-1])+".":"; não há período anterior de mesma duração no histórico.")+" Último reajuste do cardápio: "+MS.ext(D.meta.revisao_preco)+".";
 var subida=INS.map(function(x,s){return {s:s,v:D.preco_ins[s][mU]/D.preco_ins[s][m0]-1,peso:M.est[s].vTeo};}).filter(function(x){return x.peso>0;});
 var gasto=TD.soma(subida.map(function(x){return x.peso;}));
 var top=subida.filter(function(x){return x.peso/gasto>0.015;}).sort(function(a,b){return b.v-a.v;}).slice(0,8);
 TD.hbars(document.getElementById("ch-ins"),top.map(function(x){return {lab:INS[x.s][0],v:Math.max(0,x.v),txt:(x.v>0?"+":"")+TD.pct(x.v),cor:x.v>0.2?"#9B2C2C":"#1B3556"};}),{label:"Barras da variação de preço dos insumos de maior peso entre "+MS.ext(m0)+" e "+MS.ext(mU)+": "+top.map(function(x){return INS[x.s][0]+" "+TD.pct(x.v);}).join(", ")+".",labW:160,valW:70});
 document.getElementById("cap-ins").textContent="Variação de preço de compra entre "+MS.ext(m0)+" e "+MS.ext(mU)+", entre os insumos com pelo menos 1,5% do custo do período. Barras em vermelho: alta acima de 20%.";
 var cats=[];for(var c=0;c<D.categorias.length;c++)if(M.porCat[c].net>0)cats.push(c);
 TD.hbars(document.getElementById("ch-cat"),cats.map(function(c){var v=pctOf(M.porCat[c].cmv,M.porCat[c].net);return {lab:D.categorias[c],v:v,txt:TD.pct(v),cor:"#1B3556"};}),{label:"Barras do CMV em percentual do faturamento por categoria: "+cats.map(function(c){return D.categorias[c]+" "+TD.pct(pctOf(M.porCat[c].cmv,M.porCat[c].net));}).join(", ")+".",labW:150,valW:60});
 document.getElementById("cap-cat").textContent="CMV do período por categoria do cardápio, nos canais filtrados.";
 var cmvP=function(it){return pctOf(M.porItem[it].cmv,M.porItem[it].net);};
 var cmvA=function(it){var o=M.itemPrev[it];return o&&o.net?o.cmv/o.net:null;};
 var itens=M.itens.filter(function(it){return M.porItem[it].q>0;});
 TD.tabela("cmv",[
  {l:"Item",v:function(it){return IT[it][0];}},
  {l:"Categoria",v:function(it){return D.categorias[IT[it][1]];}},
  {l:"Preço no salão",num:true,v:function(it){return D.P[it][0][mU]/100;},f:function(it){return TD.brl2(D.P[it][0][mU]/100);}},
  {l:"Custo atual",num:true,v:function(it){return D.custo[it][mU];},f:function(it){return TD.brl2(D.custo[it][mU]);}},
  {l:"CMV atual no salão",num:true,v:function(it){return D.custo[it][mU]*100/D.P[it][0][mU];},f:function(it){var v=D.custo[it][mU]*100/D.P[it][0][mU];return v>0.4?'<span class="neg">'+TD.pct(v)+'</span>':TD.pct(v);},csv:function(it){return Math.round(D.custo[it][mU]*100/D.P[it][0][mU]*1000)/10;}},
  {l:"CMV do período",num:true,bar:true,v:cmvP,f:function(it){return TD.pct(cmvP(it));},csv:function(it){return Math.round(cmvP(it)*1000)/10;}},
  {l:"Variação",num:true,v:function(it){var a=cmvA(it);return a===null?-9:cmvP(it)-a;},f:function(it){var a=cmvA(it);return a===null?"Sem base":TD.pp(cmvP(it)-a);},cls:function(it){var a=cmvA(it);return a!==null&&cmvP(it)-a>=0.03?"neg":"";},csv:function(it){var a=cmvA(it);return a===null?"":Math.round((cmvP(it)-a)*1000)/10;}},
  {l:"Quantidade",num:true,v:function(it){return M.porItem[it].q;},f:function(it){return TD.n0(M.porItem[it].q);}},
  {l:"Faturamento",num:true,v:function(it){return R(M.porItem[it].net);},f:function(it){return brlc(M.porItem[it].net);}},
  {l:"Margem de contribuição",num:true,v:function(it){return R(M.porItem[it].mc);},f:function(it){return brlc(M.porItem[it].mc);},cls:function(it){return M.porItem[it].mc<0?"neg":"";}}
 ],itens,{el:"tb-cmv",cls:"fix1",sortable:true,sort:5,dir:-1,rowHeader:true,caption:"CMV e margem por item do cardápio",foot:["Total ("+itens.length+" itens)","","","","",TD.pct(pctOf(M.tot.cmv,M.tot.net)),"",TD.n0(M.tot.q),brlc(M.tot.net),brlc(M.tot.mc)]});
}

/* ---------- ticket ---------- */
function renderTicket(){
 var M=TD.M;
 var elT=document.getElementById("ch-ticket"),estreito=TD.wOf(elT)<560,CURTO=["Salão","Balcão","Aplicativo 1","Aplicativo 2"];
 TD.hbars(elT,M.canais.map(function(c){var v=M.pedCanal[c]?R(M.recCanal[c])/M.pedCanal[c]:0;return {lab:estreito?CURTO[c]:D.canais[c],v:v,txt:TD.brl2(v)+(estreito?"":" ("+TD.n0(M.pedCanal[c])+" pedidos)"),cor:COR_CANAL[c]};}),{labW:estreito?100:180,valW:estreito?84:190,label:"Barras do ticket médio por canal: "+M.canais.map(function(c){return D.canais[c]+" "+TD.brl2(M.pedCanal[c]?R(M.recCanal[c])/M.pedCanal[c]:0);}).join(", ")+"."});
 var maior=M.canais.slice().sort(function(a,b){return M.pedCanal[b]-M.pedCanal[a];})[0];
 document.getElementById("cap-ticket").textContent="Ticket médio de "+TD.brl2(M.ped?R(M.recCel)/M.ped:0)+" em "+TD.n0(M.ped)+" pedidos. O canal com mais pedidos foi "+D.canais[maior].toLowerCase()+".";
 var maxP=0;M.cel.forEach(function(l){l.forEach(function(c){if(c.p>maxP)maxP=c.p;});});
 var rows=D.dias.map(function(d,i){return i;});
 var cols=[{l:"Dia da semana",v:function(i){return D.dias[i];}}];
 D.faixas.forEach(function(f,j){cols.push({l:f,num:true,v:function(i){var c=M.cel[i][j];return c.p?R(c.r)/c.p:0;},csv:function(i){var c=M.cel[i][j];return c.p?Math.round(R(c.r)/c.p*100)/100:0;},
  f:function(i){var c=M.cel[i][j];return c.p?TD.brl2(R(c.r)/c.p)+"<small>"+TD.n0(c.p)+" pedidos</small>":"Sem pedidos";},
  style:function(i){var c=M.cel[i][j],a=maxP?c.p/maxP:0;var bg=a>0.66?"#C9D6E6":a>0.33?"#DFE7F1":"#F3F6FA";return "background:"+bg;}});
 });
 cols.forEach(function(c,k){if(k)c.cls=function(){return "hc";};});
 cols.push({l:"Pedidos no dia",num:true,v:function(i){return M.cel[i][0].p+M.cel[i][1].p+M.cel[i][2].p;},f:function(i){return TD.n0(M.cel[i][0].p+M.cel[i][1].p+M.cel[i][2].p);}});
 var fp=D.faixas.map(function(f,j){var r=0,p=0;M.cel.forEach(function(l){r+=l[j].r;p+=l[j].p;});return p?TD.brl2(R(r)/p):"";});
 TD.tabela("heat",cols,rows,{el:"tb-heat",cls:"heat",rowHeader:true,caption:"Ticket médio e pedidos por dia da semana e faixa horária",foot:["Todos os dias"].concat(fp).concat([TD.n0(M.ped)])});
}

/* ---------- ABC ---------- */
function renderABC(){
 var M=TD.M,n=M.abc.length;
 var classe=function(k){var prev=k?M.cum[k-1]:0;return prev<0.8-1e-12?"A":prev<0.95-1e-12?"B":"C";};
 var pos={};M.abc.forEach(function(it,k){pos[it]=k;});
 var nA=M.abc.filter(function(it,k){return classe(k)==="A";}).length,nB=M.abc.filter(function(it,k){return classe(k)==="B";}).length;
 TD.pareto(document.getElementById("ch-abc"),M.cum,{unidade:"itens",unidade1:"item",faixas:[0.8,0.95],label:"Curva de Pareto do faturamento por item. "+nA+" itens na classe A, "+nB+" na classe B e "+(n-nA-nB)+" na classe C."});
 document.getElementById("cap-abc").textContent="Itens ordenados do maior para o menor faturamento. Linhas pontilhadas em 80% e 95%. Classe A: "+nA+" de "+n+" itens ("+TD.pct(n?nA/n:0,0)+" do cardápio vendido).";
 TD.tabela("abc",[
  {l:"Posição",num:true,v:function(it){return pos[it]+1;},f:function(it){return TD.n0(pos[it]+1);}},
  {l:"Item",v:function(it){return IT[it][0];}},
  {l:"Categoria",v:function(it){return D.categorias[IT[it][1]];}},
  {l:"Classe",v:function(it){return classe(pos[it]);},f:function(it){var c=classe(pos[it]);return '<span class="badge '+(c==="A"?"ok":c==="B"?"sens":"warn")+'">'+c+'</span>';}},
  {l:"Faturamento",num:true,bar:true,v:function(it){return R(M.porItem[it].net);},f:function(it){return brlc(M.porItem[it].net);}},
  {l:"Participação",num:true,v:function(it){return pctOf(M.porItem[it].net,M.tot.net);},f:function(it){return TD.pct(pctOf(M.porItem[it].net,M.tot.net));},csv:function(it){return Math.round(pctOf(M.porItem[it].net,M.tot.net)*1000)/10;}},
  {l:"Acumulado",num:true,v:function(it){return M.cum[pos[it]];},f:function(it){return TD.pct(M.cum[pos[it]]);},csv:function(it){return Math.round(M.cum[pos[it]]*1000)/10;}},
  {l:"Margem de contribuição",num:true,v:function(it){return pctOf(M.porItem[it].mc,M.porItem[it].net);},f:function(it){return TD.pct(pctOf(M.porItem[it].mc,M.porItem[it].net));},csv:function(it){return Math.round(pctOf(M.porItem[it].mc,M.porItem[it].net)*1000)/10;}}
 ],M.abc,{el:"tb-abc",rowHeader:false,caption:"Curva ABC do cardápio",foot:["",n+" itens","","",brlc(M.tot.net),"100%","",TD.pct(pctOf(M.tot.mc,M.tot.net))]});
}

/* ---------- estoque ---------- */
function renderEstoque(){
 var M=TD.M,vt=0,vr=0;M.est.forEach(function(e){vt+=e.vTeo;vr+=e.vReal;});
 var acima=M.est.filter(function(e){return e.pct>0.03;}).length;
 TD.kpis("kpis-est",[
  {l:"Consumo teórico",v:TD.brlC(vt),s:"Pelas vendas e fichas técnicas"},
  {l:"Consumo real",v:TD.brlC(vr),s:"Estoque inicial, compras e contagem"},
  {l:"Divergência",v:TD.brlC(vr-vt),s:vt?TD.pct((vr-vt)/vt)+" do consumo teórico":"",cls:vr-vt>0?"risco":""},
  {l:"Insumos acima de 3%",v:TD.n0(acima),s:"de "+NS+" insumos controlados",cls:acima?"risco":""}
 ]);
 var top=M.est.slice().sort(function(a,b){return b.valor-a.valor;}).slice(0,8);
 TD.hbars(document.getElementById("ch-est"),top.map(function(e){return {lab:INS[e.s][0],v:Math.max(0,e.valor),txt:TD.brl(e.valor)+" ("+TD.pct(e.pct)+")",cor:e.pct>0.03?"#9B2C2C":"#1B3556",hach:e.pct>0.03};}),{label:"Barras das maiores divergências de estoque em valor: "+top.map(function(e){return INS[e.s][0]+" "+TD.brl(e.valor);}).join(", ")+".",labW:160,valW:140});
 document.getElementById("cap-est").textContent="Barras hachuradas em vermelho: divergência acima de 3% do consumo teórico. "+INS[top[0].s][0]+" responde por "+TD.pct(vr-vt?top[0].valor/(vr-vt):0,0)+" da divergência total em valor.";
 TD.tabela("estoque",[
  {l:"Insumo",v:function(e){return INS[e.s][0];}},
  {l:"Unidade",v:function(e){return INS[e.s][1];}},
  {l:"Consumo teórico",num:true,v:function(e){return e.teo;},f:function(e){return TD.n1(e.teo);}},
  {l:"Consumo real",num:true,v:function(e){return e.real;},f:function(e){return TD.n1(e.real);}},
  {l:"Diferença",num:true,v:function(e){return e.div;},f:function(e){return TD.n1(e.div);}},
  {l:"Divergência %",num:true,v:function(e){return e.pct;},f:function(e){return e.pct>0.03?'<span class="badge alert">'+TD.pct(e.pct)+'</span>':TD.pct(e.pct);},csv:function(e){return Math.round(e.pct*1000)/10;}},
  {l:"Preço médio",num:true,v:function(e){return e.preco;},f:function(e){return TD.brl2(e.preco);}},
  {l:"Divergência em valor",num:true,bar:true,v:function(e){return e.valor;},f:function(e){return TD.brl(e.valor);}}
 ],M.est,{el:"tb-est",cls:"fix1",sortable:true,sort:7,dir:-1,rowHeader:true,caption:"Consumo teórico e real por insumo",foot:["Total","","","","","",vt?TD.pct((vr-vt)/vt):"",TD.brl(vr-vt)]});
}

function renderComo(){
 TD.arquitetura(document.getElementById("ch-arq"),["PDV do salão e do balcão","Relatórios dos aplicativos de delivery","Notas de compra (XML de NF-e)","Fichas técnicas e contagens de estoque"],[["PostgreSQL","camada bruta (raw)"],["dbt: staging","limpeza e tipagem"],["dbt: intermediate","cadastro único e fichas"],["dbt: marts","vendas, CMV e estoque"],["Painel","indicadores e telas"]]);
}

function escopo(M,F){
 var t="Exibindo "+M.per.lab.toLowerCase()+" ("+M.per.desc+")";
 t+=F.canal>=0?", canal "+D.canais[F.canal].toLowerCase():", todos os canais";
 t+=F.cat>=0?", categoria "+D.categorias[F.cat].toLowerCase():", todas as categorias";
 return t+".";
}

TD.iniciar({slug:"demo-varejo",dados:D,periodos:PER,inicial:"geral",padrao:{per:"12m",canal:-1,cat:-1},
 filtros:[{el:"f-per",campo:"per"},{el:"f-canal",campo:"canal",num:true},{el:"f-cat",campo:"cat",num:true}],
 calcular:calcular,escopo:escopo,
 render:{geral:renderGeral,canal:renderCanal,cmv:renderCMV,ticket:renderTicket,abc:renderABC,estoque:renderEstoque,como:renderComo}});
})();
