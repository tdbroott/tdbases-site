(function(){
"use strict";
var D=JSON.parse(document.getElementById("dados-demo").textContent);
var MS=TD.meses(D.meta.meses),NM=MS.n,L=NM-1,REF=D.meta.referencia;
var E=D.emp,NE=E.length;
var RB=0,DED=1,CUS=2,PES=3,OCU=4,COM=5,ADM=6,DEP=7,RF=8,IR=9;
var CX_ROT=["Recebimentos de clientes","Pagamentos a fornecedores","Impostos","Folha e encargos","Demais despesas","Resultado financeiro","Investimentos","Empréstimos"];
var PER=MS.periodos([12,6,3,24]);
var DRE_ROT=[["RB","Receita bruta",0],["DED","(-) Deduções e impostos sobre vendas",1],["RL","Receita líquida",2],["CUS","(-) Custo das mercadorias, produtos ou serviços",1],["LB","Lucro bruto",2],["PES","(-) Pessoal",1],["OCU","(-) Ocupação",1],["COM","(-) Comerciais",1],["ADM","(-) Administrativas",1],["EBITDA","EBITDA",2],["DEP","(-) Depreciação",1],["RF","Resultado financeiro",1],["LAIR","Resultado antes de IR e CSLL",2],["IR","(-) IR e CSLL",1],["LL","Resultado líquido",2]];
var FX=D.meta.faixas_simples;

document.getElementById("sub-ref").textContent="Painel gerencial da carteira de "+NE+" empresas clientes. Histórico de "+MS.ext(0)+" a "+MS.ext(L)+", posição de conciliação em "+TD.dataBR(REF)+".";
var selPer=document.getElementById("f-per"),selSeg=document.getElementById("f-seg"),selEmp=document.getElementById("f-emp");
TD.preencher(selPer,PER.map(function(p){return [p.id,p.lab];}));
TD.preencher(selSeg,[["-1","Todos os segmentos"]].concat(D.segmentos.map(function(s,i){return [String(i),s];})));
function opcoesEmpresa(seg){
 selEmp.innerHTML="";
 TD.preencher(selEmp,[["-1","Todas as empresas"]].concat(E.map(function(e,i){return [i,e];}).filter(function(x){return seg<0||x[1][1]===seg;}).map(function(x){return [String(x[0]),x[1][0]+" ("+D.regimes[x[1][2]]+")"];})));
}
opcoesEmpresa(-1);

function soma(i,j,ms){var a=D.dre[i][j],s=0;for(var k=0;k<ms.length;k++)s+=a[ms[k]];return s;}
function somaCx(i,j,ms){var a=D.cx[i][j],s=0;for(var k=0;k<ms.length;k++)s+=a[ms[k]];return s;}
function derivar(v){
 var o={RB:v[0],DED:v[1],CUS:v[2],PES:v[3],OCU:v[4],COM:v[5],ADM:v[6],DEP:v[7],RF:v[8],IR:v[9]};
 o.RL=o.RB-o.DED;o.LB=o.RL-o.CUS;o.EBITDA=o.LB-o.PES-o.OCU-o.COM-o.ADM;o.LAIR=o.EBITDA-o.DEP+o.RF;o.LL=o.LAIR-o.IR;return o;
}
function rbt12(i){var s=0;for(var m=NM-12;m<NM;m++)s+=D.dre[i][RB][m];return s;}
function proxFaixa(i){if(E[i][2]!==0)return null;var r=rbt12(i);for(var k=0;k<FX.length;k++){if(FX[k]>r)return {lim:FX[k],folga:(FX[k]-r)/FX[k],r:r,ultima:k===FX.length-1};}return {lim:null,folga:0,r:r};}

function calcular(F){
 var per=PER.filter(function(p){return p.id===F.per;})[0]||PER[0],ms=per.m,n=ms.length;
 var prev=[];for(var k=ms[0]-n;k<ms[0];k++)if(k>=0)prev.push(k);if(prev.length<n)prev=null;
 var emp=[];for(var i=0;i<NE;i++){if(F.emp>=0?i===F.emp:(F.seg<0||E[i][1]===F.seg))emp.push(i);}
 var M={per:per,ms:ms,prev:prev,emp:emp,F:F};
 var tot=TD.zeros(10),totP=TD.zeros(10),cxl=TD.zeros(8);
 var mes={RB:TD.zeros(n),LL:TD.zeros(n),OP:TD.zeros(n),ent:TD.zeros(n),sai:TD.zeros(n),saldo:TD.zeros(n),linhas:[]};
 for(var j=0;j<8;j++)mes.linhas.push(TD.zeros(n));
 var saldo0=0;
 M.porEmp={};
 emp.forEach(function(i){
  var v=[],vp=[];for(var j=0;j<10;j++){v.push(soma(i,j,ms));vp.push(prev?soma(i,j,prev):0);tot[j]+=v[j];totP[j]+=vp[j];}
  var c=[];for(j=0;j<8;j++){c.push(somaCx(i,j,ms));cxl[j]+=c[j];}
  var sal=D.saldo_ini[i];for(var m=0;m<ms[0];m++)for(j=0;j<8;j++)sal+=D.cx[i][j][m];saldo0+=sal;
  var conc=TD.zeros(10);ms.forEach(function(m){var r=D.conc[i][m];for(var q=0;q<10;q++)conc[q]+=r[q];});
  var d=derivar(v),dp=prev?derivar(vp):null;
  // margem bruta nos 3 últimos meses do período e nos 3 anteriores
  var u3=[],a3=[];for(var q=Math.max(0,ms[n-1]-2);q<=ms[n-1];q++)u3.push(q);for(q=Math.max(0,ms[n-1]-5);q<=ms[n-1]-3;q++)a3.push(q);
  var mbU=derivar(D.dre[i].map(function(a){return u3.reduce(function(s,x){return s+a[x];},0);}));
  var mbA=derivar(D.dre[i].map(function(a){return a3.reduce(function(s,x){return s+a[x];},0);}));
  M.porEmp[i]={d:d,dp:dp,c:c,op:c[0]+c[1]+c[2]+c[3]+c[4]+c[5],conc:conc,
   mbTend:(mbU.RL>0&&mbA.RL>0)?mbU.LB/mbU.RL-mbA.LB/mbA.RL:0,mbU:mbU.RL>0?mbU.LB/mbU.RL:0,
   pend:0,atraso:D.atraso[i][L],faixa:proxFaixa(i)};
 });
 ms.forEach(function(m,k){
  emp.forEach(function(i){
   var d=D.dre[i];var ll=d[RB][m]-d[DED][m]-d[CUS][m]-d[PES][m]-d[OCU][m]-d[COM][m]-d[ADM][m]-d[DEP][m]+d[RF][m]-d[IR][m];
   mes.RB[k]+=d[RB][m];mes.LL[k]+=ll;
   for(var j=0;j<8;j++){var x=D.cx[i][j][m];mes.linhas[j][k]+=x;if(x>=0)mes.ent[k]+=x;else mes.sai[k]+=x;if(j<6)mes.OP[k]+=x;}
  });
 });
 var acc=saldo0;for(var k=0;k<n;k++){acc+=mes.ent[k]+mes.sai[k];mes.saldo[k]=acc;}
 M.saldo0=saldo0;M.mes=mes;M.tot=derivar(tot);M.totP=prev?derivar(totP):null;M.cx=cxl;
 M.op=cxl[0]+cxl[1]+cxl[2]+cxl[3]+cxl[4]+cxl[5];M.var=M.op+cxl[6]+cxl[7];
 // conciliação
 var cc=TD.zeros(10),auto=TD.zeros(n),lin=TD.zeros(n);
 emp.forEach(function(i){var r=M.porEmp[i].conc;for(var q=0;q<10;q++)cc[q]+=r[q];ms.forEach(function(m,k){var x=D.conc[i][m];lin[k]+=x[0];auto[k]+=x[1]+x[2]+x[3];});});
 M.conc=cc;M.autoMes=auto.map(function(a,k){return lin[k]?a/lin[k]:0;});
 var inE={};emp.forEach(function(i){inE[i]=1;});
 M.pend=D.pend.filter(function(p){return inE[p[0]];});
 M.pend.forEach(function(p){M.porEmp[p[0]].pend++;});
 M.pendMot=TD.zeros(5);M.pend.forEach(function(p){M.pendMot[p[4]]++;});
 return M;
}

function nomeE(i){return E[i][0];}
function lista(nomes){if(nomes.length<=1)return nomes.join("");return nomes.slice(0,-1).join(", ")+" e "+nomes[nomes.length-1];}

/* ---------- visão geral ---------- */
function renderGeral(){
 var M=TD.M,t=M.tot,c=M.conc,unica=M.emp.length===1;
 var autoPct=c[0]?(c[1]+c[2]+c[3])/c[0]:0,horas=(c[1]+c[2]+c[3])*D.meta.minutos_por_linha/60;
 TD.kpis("kpis",[
  {l:unica?"Empresa":"Empresas no recorte",v:unica?nomeE(M.emp[0]):TD.n0(M.emp.length),s:unica?D.regimes[E[M.emp[0]][2]]+", "+D.segmentos[E[M.emp[0]][1]].toLowerCase():"de "+NE+" na carteira"},
  {l:"Faturamento bruto",v:TD.brlC(t.RB),s:M.totP?"Período anterior: "+TD.brlC(M.totP.RB):"Sem período anterior comparável"},
  {l:"Margem líquida",v:t.RL?TD.pct(t.LL/t.RL):"Sem receita",s:"Resultado: "+TD.brlC(t.LL),cls:t.LL<0?"risco":""},
  {l:"Caixa das operações",v:TD.brlC(M.op),s:M.op<0?"Consumiu caixa no período":"Gerou caixa no período",cls:M.op<0?"risco":""},
  {l:"Conciliação automática",v:TD.pct(autoPct,0),s:TD.n0(M.pend.length)+" pendências abertas, cerca de "+TD.n0(horas)+" h de conferência evitadas"}
 ]);
 var A=[];
 if(!unica){
  var queda=M.emp.filter(function(i){return M.porEmp[i].mbTend<=-0.03;}).sort(function(a,b){return M.porEmp[a].mbTend-M.porEmp[b].mbTend;});
  A.push(queda.length?{t:"Margem bruta em queda",p:lista(queda.map(function(i){return nomeE(i)+" ("+TD.pp(M.porEmp[i].mbTend)+")";}))+(queda.length===1?" perdeu":" perderam")+" margem bruta nos últimos 3 meses do período, comparados aos 3 anteriores.",a:"Revisar custo de compra e tabela de preços com o cliente antes do próximo fechamento."}:{t:"Margem bruta estável",p:"Nenhuma empresa do recorte perdeu 3 pontos ou mais de margem bruta nos últimos 3 meses do período.",a:"Acompanhar no próximo fechamento."});
  var semCx=M.emp.filter(function(i){var p=M.porEmp[i];return p.d.LL>0&&p.op<0;}).sort(function(a,b){return M.porEmp[a].op-M.porEmp[b].op;});
  A.push(semCx.length?{t:"Lucro que não virou caixa",p:lista(semCx.map(nomeE))+(semCx.length===1?" teve":" tiveram")+" resultado positivo por competência e caixa das operações negativo no período. "+nomeE(semCx[0])+": resultado de "+TD.brlC(M.porEmp[semCx[0]].d.LL)+" e caixa das operações de "+TD.brlC(M.porEmp[semCx[0]].op)+".",a:"Abrir a ponte do resultado ao caixa: prazo de recebimento e estoque costumam explicar."}:{t:"Lucro e caixa alinhados",p:"Nenhuma empresa lucrativa do recorte consumiu caixa nas operações no período.",a:"Acompanhar prazos de recebimento."});
  var fx=M.emp.filter(function(i){var f=M.porEmp[i].faixa;return f&&f.lim&&f.folga<=0.10;}).sort(function(a,b){return M.porEmp[a].faixa.folga-M.porEmp[b].faixa.folga;});
  A.push(fx.length?{t:"Simples Nacional perto do limite da faixa",p:lista(fx.map(function(i){var f=M.porEmp[i].faixa;return nomeE(i)+" ("+TD.pct(1-f.folga,0)+" de "+TD.brlC(f.lim)+")";}))+(fx.length===1?" está":" estão")+" a menos de 10% da próxima faixa de receita bruta acumulada em 12 meses, na posição de "+TD.dataBR(REF)+".",a:"Simular a alíquota efetiva da faixa seguinte e o enquadramento do próximo ano."}:{t:"Enquadramento no Simples",p:"Nenhuma empresa do Simples no recorte está a menos de 10% da próxima faixa.",a:"Reavaliar no próximo trimestre."});
 }else{
  var i=M.emp[0],p=M.porEmp[i];
  A.push({t:"Margem bruta",p:"Nos últimos 3 meses do período a margem bruta foi "+TD.pct(p.mbU)+", "+(Math.abs(p.mbTend)<0.005?"estável":TD.pp(p.mbTend))+" em relação aos 3 meses anteriores.",a:p.mbTend<=-0.03?"Revisar custo de compra e preços com o cliente.":"Manter o acompanhamento mensal."});
  A.push({t:"Resultado e caixa",p:"Resultado por competência de "+TD.brlC(p.d.LL)+" e caixa das operações de "+TD.brlC(p.op)+" no período. A diferença é de "+TD.brlC(p.op-p.d.LL)+".",a:p.d.LL>0&&p.op<0?"Abrir a ponte do resultado ao caixa com o cliente.":"Ver a ponte na tela DRE e caixa."});
  var f=p.faixa;
  A.push(f?{t:"Enquadramento no Simples",p:"Receita bruta acumulada em 12 meses de "+TD.brlC(f.r)+(f.lim?", "+TD.pct(1-f.folga,0)+" da faixa de até "+TD.brlC(f.lim)+".":", acima do limite do regime."),a:f.lim&&f.folga<=0.1?"Simular a próxima faixa com o cliente.":"Reavaliar no próximo trimestre."}:{t:"Conciliação",p:TD.n0(p.pend)+" pendências abertas e "+(p.atraso?p.atraso+" dias de atraso na entrega dos documentos do último mês.":"documentos do último mês entregues no prazo."),a:p.pend>15?"Combinar com o cliente o envio dos comprovantes faltantes.":"Seguir a rotina de fechamento."});
 }
 TD.achados("achados",A);
 var rot=M.ms.map(MS.lab);
 TD.colunas(document.getElementById("ch-geral"),{rotulos:rot,series:[{nome:"Resultado por competência",valores:M.mes.LL,cor:"#1B3556"}],linha:{nome:"Caixa das operações",valores:M.mes.OP,cor:"#B07D1F"},fmt:TD.brlC,fmtEixo:function(v){return TD.brlC(v).replace("R$ ","");},label:"Colunas do resultado por competência e linha do caixa das operações, por mês, de "+M.per.desc+"."});
 document.getElementById("lg-geral").innerHTML='<li><svg width="14" height="14" aria-hidden="true"><rect width="14" height="14" fill="#1B3556"/></svg>Resultado por competência (colunas)</li><li><svg width="30" height="12" aria-hidden="true"><line x1="1" y1="6" x2="29" y2="6" stroke="#B07D1F" stroke-width="2.4"/>'+TD.marca("diamond",15,6,4,"#B07D1F")+'</svg>Caixa das operações (linha com losangos)</li>';
 var piorK=0;M.mes.OP.forEach(function(v,k){if(v-M.mes.LL[k]<M.mes.OP[piorK]-M.mes.LL[piorK])piorK=k;});
 document.getElementById("cap-geral").textContent="No período, o resultado soma "+TD.brl(t.LL)+" e o caixa das operações soma "+TD.brl(M.op)+". O mês com maior diferença foi "+MS.ext(M.ms[piorK])+", com caixa das operações "+TD.brl(Math.abs(M.mes.OP[piorK]-M.mes.LL[piorK]))+(M.mes.OP[piorK]<M.mes.LL[piorK]?" abaixo":" acima")+" do resultado"+([11,12].indexOf(+D.meta.meses[M.ms[piorK]].slice(5))>=0?", efeito típico do pagamento do 13º salário.":".");
}

/* ---------- fluxo ---------- */
function renderFluxo(){
 var M=TD.M,rot=M.ms.map(MS.lab);
 document.getElementById("nota-fluxo").textContent=(M.emp.length===1?nomeE(M.emp[0]):"Soma de "+M.emp.length+" empresas, útil para ver volume e sazonalidade; a leitura gerencial é por empresa")+". Saldo inicial do período: "+TD.brl(M.saldo0)+".";
 TD.colunas(document.getElementById("ch-fluxo"),{rotulos:rot,series:[{nome:"Entradas",valores:M.mes.ent,cor:"#1B3556"},{nome:"Saídas",valores:M.mes.sai,cor:"#9B2C2C",hach:true}],linha:{nome:"Saldo",valores:M.mes.saldo,cor:"#B07D1F"},fmt:TD.brlC,fmtEixo:function(v){return TD.brlC(v).replace("R$ ","");},label:"Colunas de entradas e saídas de caixa por mês e linha do saldo no fim do mês, de "+M.per.desc+"."});
 TD.legenda(document.getElementById("lg-fluxo"),[{nome:"Entradas (colunas para cima)",cor:"#1B3556"},{nome:"Saídas (colunas para baixo, hachuradas)",cor:"#9B2C2C",tipo:"hach",id:"f1"},{nome:"Saldo no fim do mês (linha com losangos)",cor:"#B07D1F",tipo:"linha",marca:"diamond"}]);
 var neg=M.mes.saldo.map(function(v,k){return [v,k];}).filter(function(x){return x[0]<0;});
 document.getElementById("cap-fluxo").textContent="Entradas somam "+TD.brl(TD.soma(M.mes.ent))+" e saídas "+TD.brl(-TD.soma(M.mes.sai))+". Saldo final de "+TD.brl(M.mes.saldo[M.mes.saldo.length-1])+"."+(neg.length?" O saldo ficou negativo em "+neg.length+(neg.length===1?" mês":" meses")+", a partir de "+MS.ext(M.ms[neg[0][1]])+".":"");
 var n=M.ms.length,rows=[];
 for(var j=0;j<6;j++)rows.push({rot:CX_ROT[j],v:M.mes.linhas[j],t:0});
 rows.push({rot:"Caixa das operações",v:M.mes.OP,t:1});
 rows.push({rot:CX_ROT[6],v:M.mes.linhas[6],t:0});rows.push({rot:CX_ROT[7],v:M.mes.linhas[7],t:0});
 var vari=M.mes.OP.map(function(v,k){return v+M.mes.linhas[6][k]+M.mes.linhas[7][k];});
 rows.push({rot:"Variação do caixa",v:vari,t:1});
 rows.push({rot:"Saldo no fim do mês",v:M.mes.saldo,t:2});
 var cols=[{l:"Linha",v:function(r){return r.rot;}}];
 M.ms.forEach(function(m,k){cols.push({l:MS.lab(m),num:true,v:function(r){return r.v[k];},f:function(r){return TD.brl(r.v[k]);},cls:function(r){return r.v[k]<0?"neg":"";}});});
 cols.push({l:"Total do período",num:true,v:function(r){return r.t===2?r.v[n-1]:TD.soma(r.v);},f:function(r){var x=r.t===2?r.v[n-1]:TD.soma(r.v);return TD.brl(x);},cls:function(r){return (r.t===2?r.v[n-1]:TD.soma(r.v))<0?"neg":"";}});
 TD.tabela("fluxo",cols,rows,{el:"tb-fluxo",cls:"fix1",rowHeader:true,caption:"Fluxo de caixa realizado por mês",rowClass:function(r){return r.t?"sub":"";}});
}

/* ---------- DRE ---------- */
function renderDRE(){
 var M=TD.M,t=M.tot,tp=M.totP;
 var rows=DRE_ROT.map(function(x){return {k:x[0],rot:x[1],tipo:x[2]};});
 var sinal=function(k){return ["DED","CUS","PES","OCU","COM","ADM","DEP","IR"].indexOf(k)>=0?-1:1;};
 var val=function(o,k){return o?o[k]*sinal(k):0;};
 var cols=[{l:"Linha",v:function(r){return r.rot;}},
  {l:"Período",num:true,v:function(r){return val(t,r.k);},f:function(r){return TD.brl(val(t,r.k));},cls:function(r){return val(t,r.k)<0&&r.tipo===2?"neg":"";}},
  {l:"% da receita líquida",num:true,v:function(r){return t.RL?val(t,r.k)/t.RL:0;},f:function(r){return r.k==="RB"?"":t.RL?TD.pct(val(t,r.k)/t.RL):"";},csv:function(r){return t.RL?Math.round(val(t,r.k)/t.RL*1000)/10:"";}},
  {l:"Período anterior",num:true,v:function(r){return val(tp,r.k);},f:function(r){return tp?TD.brl(val(tp,r.k)):"Sem base";}},
  {l:"Variação",num:true,v:function(r){return tp&&val(tp,r.k)?val(t,r.k)/val(tp,r.k)-1:0;},f:function(r){if(!tp||!val(tp,r.k))return "";var x=val(t,r.k)/val(tp,r.k)-1;return (x>0?"+":"")+TD.pct(x);},csv:function(r){return tp&&val(tp,r.k)?Math.round((val(t,r.k)/val(tp,r.k)-1)*1000)/10:"";}}];
 TD.tabela("dre",cols,rows,{el:"tb-dre",rowHeader:true,caption:"Demonstração do resultado gerencial por competência",rowClass:function(r){return r.tipo===2?"sub":r.tipo===1?"ind":"";}});
 document.getElementById("nota-dre").textContent=(M.emp.length===1?nomeE(M.emp[0])+". ":"Soma de "+M.emp.length+" empresas. ")+"Período: "+M.per.desc+(tp?"; período anterior: "+MS.ext(M.prev[0])+" a "+MS.ext(M.prev[M.prev.length-1])+".":"; não há período anterior de mesma duração no histórico.")+" Valores negativos representam despesas.";
 var c=M.cx,p=[
  {lab:"Resultado líquido",v:t.LL,total:true},
  {lab:"Depreciação",v:t.DEP},
  {lab:"Clientes a receber",v:c[0]-t.RB},
  {lab:"Fornecedores e estoque",v:t.CUS+c[1]},
  {lab:"Impostos a recolher",v:t.DED+t.IR+c[2]},
  {lab:"Folha e provisões",v:t.PES+c[3]},
  {lab:"Demais despesas",v:t.OCU+t.COM+t.ADM+c[4]},
  {lab:"Caixa das operações",v:M.op,total:true},
  {lab:"Investimentos",v:c[6]},
  {lab:"Empréstimos",v:c[7]},
  {lab:"Variação do caixa",v:M.var,total:true}];
 TD.cascata(document.getElementById("ch-ponte"),p,{fmt:TD.brlC,label:"Cascata do resultado líquido até a variação do caixa: "+p.map(function(x){return x.lab+" "+TD.brlC(x.v);}).join(", ")+"."});
 document.getElementById("lg-ponte").innerHTML='<li><svg width="14" height="14" aria-hidden="true"><rect width="14" height="14" fill="#1B3556"/></svg>Totais</li><li><svg width="14" height="14" aria-hidden="true"><rect width="14" height="14" fill="#5B7FA6"/></svg>Aumenta o caixa</li><li><svg width="14" height="14" aria-hidden="true"><defs>'+TD.hach("lgp","#9B2C2C")+'</defs><rect width="14" height="14" fill="url(#lgp)"/></svg>Reduz o caixa (hachurado)</li>';
 var maior=p.slice(1,7).sort(function(a,b){return a.v-b.v;})[0];
 document.getElementById("cap-ponte").textContent="Resultado de "+TD.brl(t.LL)+" e caixa das operações de "+TD.brl(M.op)+". "+(maior.v<0?"O item que mais segurou caixa foi "+maior.lab.toLowerCase()+", com "+TD.brl(maior.v)+".":"Nenhum item de capital de giro consumiu caixa no período.")+" A soma das etapas fecha exatamente na variação do caixa: "+TD.brl(M.var)+".";
}

/* ---------- conciliação ---------- */
function renderConcil(){
 var M=TD.M,c=M.conc,auto=c[1]+c[2]+c[3],exc=c[5]+c[6]+c[7]+c[8]+c[9];
 document.getElementById("nota-concil").textContent="Período: "+M.per.desc+". A fila de pendências é a posição em "+TD.dataBR(REF)+" e não depende do filtro de período. Horas evitadas: premissa da demonstração de "+TD.n1(D.meta.minutos_por_linha).replace(",0","")+" minuto por linha que seria conferida manualmente; no Raio-X, a premissa é medida na rotina do escritório.";
 TD.kpis("kpis-concil",[
  {l:"Linhas de extrato",v:TD.n0(c[0]),s:"No período"},
  {l:"Conciliadas por regra",v:c[0]?TD.pct(auto/c[0],0):"0%",s:TD.n0(auto)+" linhas, cerca de "+TD.n0(auto*D.meta.minutos_por_linha/60)+" h evitadas"},
  {l:"Conciliadas pela equipe",v:TD.n0(c[4]),s:c[0]?TD.pct(c[4]/c[0])+" das linhas":""},
  {l:"Exceções geradas",v:TD.n0(exc),s:c[0]?TD.pct(exc/c[0])+" das linhas":""},
  {l:"Pendências abertas",v:TD.n0(M.pend.length),s:"Em "+TD.dataBR(REF),cls:M.pend.length?"risco":""}
 ]);
 TD.linhas(document.getElementById("ch-auto"),{rotulos:M.ms.map(MS.lab),series:[{nome:"Automático",valores:M.autoMes,cor:"#1B3556"}],fmt:function(v){return TD.pct(v,0);},min:0.6,max:1,label:"Linha do percentual de linhas de extrato conciliadas por regra, por mês, de "+M.per.desc+"."});
 document.getElementById("cap-auto").textContent="Regras usadas: "+D.regras.map(function(r,k){return r.toLowerCase()+" ("+(auto?TD.pct(c[1+k]/auto,0):"0%")+")";}).join(", ")+".";
 var ord=D.motivos.map(function(m,k){return k;}).sort(function(a,b){return M.pendMot[b]-M.pendMot[a];});
 TD.hbars(document.getElementById("ch-motivo"),ord.map(function(k){return {lab:D.motivos[k],v:M.pendMot[k],txt:TD.n0(M.pendMot[k]),cor:k===ord[0]?"#9B2C2C":"#1B3556"};}),{label:"Barras das pendências abertas por motivo: "+ord.map(function(k){return D.motivos[k]+" "+M.pendMot[k];}).join(", ")+".",labW:250,valW:50});
 var porEmp={};M.pend.forEach(function(p){porEmp[p[0]]=(porEmp[p[0]]||0)+1;});
 var top=Object.keys(porEmp).sort(function(a,b){return porEmp[b]-porEmp[a];}).slice(0,3);
 var topN=top.reduce(function(s,k){return s+porEmp[k];},0);
 document.getElementById("cap-motivo").textContent=M.pend.length?(top.length>1&&M.emp.length>3?lista(top.map(function(k){return nomeE(+k);}))+" concentram "+TD.n0(topN)+" das "+TD.n0(M.pend.length)+" pendências ("+TD.pct(topN/M.pend.length,0)+"). ":"")+"O motivo mais frequente é "+D.motivos[ord[0]].toLowerCase()+".":"Sem pendências abertas no recorte.";
 var refD=new Date(REF+"T12:00:00Z");
 var dias=function(p){return Math.round((refD-new Date(p[1]+"T12:00:00Z"))/864e5);};
 TD.tabela("pend",[
  {l:"Em aberto há",num:true,v:dias,f:function(p){var d=dias(p);return d>30?'<span class="badge alert">'+d+' dias</span>':d+" dias";},csv:dias},
  {l:"Data",v:function(p){return p[1];},f:function(p){return TD.dataBR(p[1]);},csv:function(p){return TD.dataBR(p[1]);}},
  {l:"Empresa",v:function(p){return nomeE(p[0]);}},
  {l:"Descrição no extrato",v:function(p){return p[2];}},
  {l:"Valor",num:true,v:function(p){return p[3];},f:function(p){return TD.brl2(p[3]);},cls:function(p){return p[3]<0?"neg":"";}},
  {l:"Motivo provável",v:function(p){return D.motivos[p[4]];}}
 ],M.pend,{el:"tb-pend",sortable:true,sort:0,dir:-1,more:"more-pend",limit:15,caption:"Fila de pendências de conciliação na data de referência"});
}

/* ---------- carteira ---------- */
function renderCarteira(){
 var M=TD.M;
 var mb=function(i){var d=M.porEmp[i].d;return d.RL?d.LB/d.RL:0;};
 var vmb=function(i){var p=M.porEmp[i];return p.dp&&p.dp.RL&&p.d.RL?p.d.LB/p.d.RL-p.dp.LB/p.dp.RL:null;};
 var status=function(i){var p=M.porEmp[i],lin=D.conc[i][L][0];if(p.atraso>5)return "Aguardando documentos";if(lin&&p.pend/lin>=0.05)return "Pendências acima do normal";if(p.d.LL>0&&p.op<0)return "Atenção ao caixa";if(p.mbTend<=-0.03)return "Margem em queda";if(p.faixa&&p.faixa.lim&&p.faixa.folga<=0.1)return "Perto da faixa do Simples";return "Em dia";};
 var stCls=function(s){return s==="Em dia"?"ok":s==="Aguardando documentos"||s==="Atenção ao caixa"?"alert":"warn";};
 var cols=[
  {l:"Empresa",v:nomeE},
  {l:"Segmento",v:function(i){return D.segmentos[E[i][1]];}},
  {l:"Regime",v:function(i){return D.regimes[E[i][2]];}},
  {l:"Situação",v:status,f:function(i){var s=status(i);return '<span class="badge '+stCls(s)+'">'+s+'</span>';}},
  {l:"Faturamento",num:true,bar:true,v:function(i){return M.porEmp[i].d.RB;},f:function(i){return TD.brlC(M.porEmp[i].d.RB);},csv:function(i){return M.porEmp[i].d.RB;}},
  {l:"Margem bruta",num:true,v:mb,f:function(i){return TD.pct(mb(i));},csv:function(i){return Math.round(mb(i)*1000)/10;}},
  {l:"Variação da margem",num:true,v:function(i){var x=vmb(i);return x===null?-9:x;},f:function(i){var x=vmb(i);return x===null?"Sem base":TD.pp(x);},cls:function(i){var x=vmb(i);return x!==null&&x<=-0.03?"neg":"";},csv:function(i){var x=vmb(i);return x===null?"":Math.round(x*1000)/10;}},
  {l:"Resultado",num:true,v:function(i){return M.porEmp[i].d.LL;},f:function(i){return TD.brlC(M.porEmp[i].d.LL);},cls:function(i){return M.porEmp[i].d.LL<0?"neg":"";},csv:function(i){return M.porEmp[i].d.LL;}},
  {l:"Caixa das operações",num:true,v:function(i){return M.porEmp[i].op;},f:function(i){return TD.brlC(M.porEmp[i].op);},cls:function(i){return M.porEmp[i].op<0?"neg":"";},csv:function(i){return M.porEmp[i].op;}},
  {l:"Conciliação automática",num:true,v:function(i){var c=M.porEmp[i].conc;return c[0]?(c[1]+c[2]+c[3])/c[0]:0;},f:function(i){var c=M.porEmp[i].conc;return c[0]?TD.pct((c[1]+c[2]+c[3])/c[0],0):"";},csv:function(i){var c=M.porEmp[i].conc;return c[0]?Math.round((c[1]+c[2]+c[3])/c[0]*1000)/10:"";}},
  {l:"Pendências",num:true,v:function(i){return M.porEmp[i].pend;},f:function(i){return TD.n0(M.porEmp[i].pend);}},
  {l:"Atraso (dias)",num:true,v:function(i){return M.porEmp[i].atraso;},f:function(i){var a=M.porEmp[i].atraso;return a>5?'<span class="neg">'+a+'</span>':String(a);}},
  {l:"RBT12",num:true,v:function(i){var f=M.porEmp[i].faixa;return f?f.r:-1;},f:function(i){var f=M.porEmp[i].faixa;return f?TD.brlC(f.r)+(f.lim?" ("+TD.pct(1-f.folga,0)+" da faixa)":""):"Não se aplica";},csv:function(i){var f=M.porEmp[i].faixa;return f?f.r:"";}}
 ];
 var t=M.tot;
 TD.tabela("carteira",cols,M.emp,{el:"tb-carteira",cls:"fix1",sortable:true,sort:4,dir:-1,rowHeader:true,caption:"Carteira de empresas clientes do escritório",foot:["Total ("+M.emp.length+")","","","",TD.brlC(t.RB),t.RL?TD.pct(t.LB/t.RL):"",M.totP&&M.totP.RL?TD.pp(t.LB/t.RL-M.totP.LB/M.totP.RL):"",TD.brlC(t.LL),TD.brlC(M.op),M.conc[0]?TD.pct((M.conc[1]+M.conc[2]+M.conc[3])/M.conc[0],0):"",TD.n0(M.pend.length),"",""]});
}

function renderComo(){
 TD.arquitetura(document.getElementById("ch-arq"),["ERP contábil (lançamentos e plano de contas)","Extratos bancários (OFX)","Notas fiscais (XML de NF-e e NFS-e)","Planilhas de controle do escritório"],[["PostgreSQL","camada bruta (raw)"],["dbt: staging","limpeza e tipagem"],["dbt: intermediate","plano gerencial e regras"],["dbt: marts","DRE, caixa e conciliação"],["Painel","indicadores e fila"]]);
}

function escopo(M,F){
 var t="Exibindo "+M.per.lab.toLowerCase()+" ("+M.per.desc+")";
 t+=F.emp>=0?", empresa "+nomeE(F.emp):F.seg>=0?", segmento "+D.segmentos[F.seg]+" ("+M.emp.length+" empresas)":", toda a carteira ("+M.emp.length+" empresas)";
 return t+".";
}

TD.iniciar({slug:"demo-contabilidade",dados:D,periodos:PER,inicial:"geral",padrao:{per:"12m",seg:-1,emp:-1},
 filtros:[{el:"f-per",campo:"per"},{el:"f-seg",campo:"seg",num:true},{el:"f-emp",campo:"emp",num:true}],
 aoMudar:function(campo,F){
  if(campo==="seg"||campo==="*"){var atual=F.emp;opcoesEmpresa(F.seg);if(atual>=0&&F.seg>=0&&E[atual][1]!==F.seg)F.emp=-1;selEmp.value=String(F.emp);}
  if(campo==="emp"&&F.emp>=0&&F.seg>=0&&E[F.emp][1]!==F.seg){F.seg=-1;selSeg.value="-1";}
 },
 calcular:calcular,escopo:escopo,
 render:{geral:renderGeral,fluxo:renderFluxo,dre:renderDRE,concil:renderConcil,carteira:renderCarteira,como:renderComo}});
})();
