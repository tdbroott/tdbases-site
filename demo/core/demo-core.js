/* Núcleo compartilhado dos painéis demonstrativos da TDBASES.
   Formatação pt-BR, gráficos em SVG, tabelas ordenáveis com CSV, abas e filtros.
   Sem dependências externas e sem armazenamento no navegador. */
var TD=(function(){
"use strict";
var TD={};
var MES_ABR=["jan","fev","mar","abr","mai","jun","jul","ago","set","out","nov","dez"];
var MES_EXT=["janeiro","fevereiro","março","abril","maio","junho","julho","agosto","setembro","outubro","novembro","dezembro"];
var nf0=new Intl.NumberFormat("pt-BR",{maximumFractionDigits:0});
var nf1=new Intl.NumberFormat("pt-BR",{minimumFractionDigits:1,maximumFractionDigits:1});
var nf2=new Intl.NumberFormat("pt-BR",{minimumFractionDigits:2,maximumFractionDigits:2});
TD.MES_ABR=MES_ABR;TD.MES_EXT=MES_EXT;
TD.n0=function(v){return nf0.format(Math.round(v));};
TD.n1=function(v){return nf1.format(v);};
TD.brl=function(v){return (v<0?"-":"")+"R$ "+nf0.format(Math.round(Math.abs(v)));};
TD.brl2=function(v){return (v<0?"-":"")+"R$ "+nf2.format(Math.abs(v));};
TD.brlC=function(v){var a=Math.abs(v),s=v<0?"-":"";if(a>=1e6)return s+"R$ "+nf1.format(a/1e6)+" mi";if(a>=1e4)return s+"R$ "+nf0.format(a/1e3)+" mil";if(a>=1e3)return s+"R$ "+nf1.format(a/1e3)+" mil";return s+"R$ "+nf0.format(a);};
TD.pct=function(v,d){return (d===0?nf0:nf1).format(v*100)+"%";};
TD.pp=function(v){var r=Math.round(v*1000)/10;return (r>0?"+":"")+nf1.format(r===0?0:r)+" p.p.";};
TD.dataBR=function(iso){var p=iso.split("-");return p[2]+"/"+p[1]+"/"+p[0];};
TD.esc=function(s){return String(s).replace(/[&<>"]/g,function(c){return {"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c];});};
TD.soma=function(a){var s=0;for(var i=0;i<a.length;i++)s+=a[i];return s;};
TD.zeros=function(n){var a=new Array(n);for(var i=0;i<n;i++)a[i]=0;return a;};

/* ---------- meses e períodos ---------- */
TD.meses=function(lista){
 var M={lista:lista,n:lista.length};
 M.lab=function(i){var p=lista[i].split("-");return MES_ABR[+p[1]-1]+"/"+p[0].slice(2);};
 M.ext=function(i){var p=lista[i].split("-");return MES_ABR[+p[1]-1]+"/"+p[0];};
 M.periodos=function(opcoes){
  var L=lista.length-1,out=[];
  function r(a,b){var x=[];for(var i=Math.max(0,a);i<=b;i++)x.push(i);return x;}
  (opcoes||[12,6,3,24]).forEach(function(n){if(n<=lista.length)out.push({id:n+"m",lab:"Últimos "+n+" meses",m:r(L-n+1,L)});});
  out.push({id:"mes",lab:"Último mês ("+M.ext(L)+")",m:[L]});
  var anos={};lista.forEach(function(m,i){var y=m.slice(0,4);(anos[y]=anos[y]||[]).push(i);});
  Object.keys(anos).sort().forEach(function(y){var ms=anos[y];if(ms.length===12)out.push({id:y,lab:"Ano de "+y,m:ms});else if(ms[ms.length-1]===L)out.push({id:y,lab:y+" até "+MES_EXT[+lista[L].slice(5)-1],m:ms});});
  out.forEach(function(p){p.desc=p.m.length===1?M.ext(p.m[0]):M.ext(p.m[0])+" a "+M.ext(p.m[p.m.length-1]);});
  return out;
 };
 return M;
};

/* ---------- SVG ---------- */
var SVGNS="http://www.w3.org/2000/svg";
TD.wOf=function(el){return Math.max(280,Math.floor(el.clientWidth||600));};
TD.svgOpen=function(w,h,label,defs){return '<svg xmlns="'+SVGNS+'" viewBox="0 0 '+w+' '+h+'" width="'+w+'" height="'+h+'" role="img" aria-label="'+TD.esc(label)+'">'+(defs?"<defs>"+defs+"</defs>":"");};
TD.hach=function(id,cor,fundo){return '<pattern id="'+id+'" width="6" height="6" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><rect width="6" height="6" fill="'+cor+'"/><line x1="0" y1="0" x2="0" y2="6" stroke="'+(fundo||"#F4D8D2")+'" stroke-width="2"/></pattern>';};
TD.niceMax=function(v){if(v<=0)return 1;var p=Math.pow(10,Math.floor(Math.log10(v))),n=v/p;return (n<=1?1:n<=2?2:n<=2.5?2.5:n<=5?5:10)*p;};
TD.marca=function(tipo,x,y,s,cor){
 if(tipo==="square")return '<rect x="'+(x-s)+'" y="'+(y-s)+'" width="'+2*s+'" height="'+2*s+'" fill="'+cor+'"/>';
 if(tipo==="diamond")return '<path d="M'+x+' '+(y-s*1.3)+'L'+(x+s*1.3)+' '+y+'L'+x+' '+(y+s*1.3)+'L'+(x-s*1.3)+' '+y+'Z" fill="'+cor+'"/>';
 if(tipo==="triangle")return '<path d="M'+x+' '+(y-s*1.3)+'L'+(x+s*1.2)+' '+(y+s)+'L'+(x-s*1.2)+' '+(y+s)+'Z" fill="'+cor+'"/>';
 if(tipo==="cross")return '<path d="M'+(x-s)+' '+(y-s)+'L'+(x+s)+' '+(y+s)+'M'+(x+s)+' '+(y-s)+'L'+(x-s)+' '+(y+s)+'" stroke="'+cor+'" stroke-width="2.6"/>';
 if(tipo==="none")return "";
 return '<circle cx="'+x+'" cy="'+y+'" r="'+s+'" fill="'+cor+'"/>';
};
TD.legenda=function(el,itens){
 el.innerHTML=itens.map(function(i){
  var ic;
  if(i.tipo==="linha")ic='<svg width="30" height="12" aria-hidden="true"><line x1="1" y1="6" x2="29" y2="6" stroke="'+i.cor+'" stroke-width="2.4"'+(i.tracejado?' stroke-dasharray="6 4"':'')+'/>'+TD.marca(i.marca||"circle",15,6,3.4,i.cor)+'</svg>';
  else if(i.tipo==="hach")ic='<svg width="14" height="14" aria-hidden="true"><defs>'+TD.hach("lg"+i.id,i.cor,i.fundo)+'</defs><rect width="14" height="14" fill="url(#lg'+i.id+')"/></svg>';
  else ic='<svg width="14" height="14" aria-hidden="true"><rect width="14" height="14" fill="'+i.cor+'"/></svg>';
  return '<li>'+ic+TD.esc(i.nome)+'</li>';
 }).join("");
};
TD.passo=function(v){if(v<=0)return 1;var p=Math.pow(10,Math.floor(Math.log10(v))),n=v/p;return (n<=1?1:n<=2?2:n<=2.5?2.5:n<=5?5:10)*p;};
function eixoY(min,max){var st=TD.passo((Math.max(max,0)-Math.min(min,0))/4||1),lo=min<0?-Math.ceil(-min/st-1e-9)*st:0,hi=max>0?Math.ceil(max/st-1e-9)*st:0;if(hi===lo)hi=lo+st;return {lo:lo,hi:hi,st:st};}

/* linhas: {rotulos[], series:[{nome,valores,cor,tracejado,marca}], fmt, label, h} */
TD.linhas=function(el,o){
 var w=TD.wOf(el),h=o.h||(w<500?220:260),pl=w<500?54:66,pr=14,pt=14,pb=34,n=o.rotulos.length;
 var all=[];o.series.forEach(function(s){all=all.concat(s.valores);});
 var ax=eixoY(Math.min.apply(null,all.concat([0])),Math.max.apply(null,all.concat([0])));
 if(o.min!==undefined)ax.lo=o.min;if(o.max!==undefined){ax.hi=o.max;ax.st=(ax.hi-ax.lo)/4;}
 var x=function(k){return pl+(n===1?(w-pl-pr)/2:(w-pl-pr)*k/(n-1));},y=function(v){return pt+(h-pt-pb)*(1-(v-ax.lo)/(ax.hi-ax.lo));};
 var s=TD.svgOpen(w,h,o.label);
 for(var g=ax.lo;g<=ax.hi+1e-9;g+=ax.st){var gy=y(g);s+='<line x1="'+pl+'" x2="'+(w-pr)+'" y1="'+gy+'" y2="'+gy+'" stroke="'+(Math.abs(g)<1e-9?"#9AA6B5":"#E1E6EC")+'"/><text x="'+(pl-6)+'" y="'+(gy+4)+'" text-anchor="end" font-size="11">'+TD.esc((o.fmtEixo||o.fmt)(g))+'</text>';}
 var step=Math.ceil(n/(w<500?4:8));
 o.rotulos.forEach(function(r,k){if(k%step===0||k===n-1)s+='<text x="'+x(k)+'" y="'+(h-12)+'" text-anchor="middle" font-size="11">'+TD.esc(r)+'</text>';});
 o.series.forEach(function(se){
  var d="";se.valores.forEach(function(v,k){d+=(k?"L":"M")+x(k).toFixed(1)+" "+y(v).toFixed(1);});
  s+='<path d="'+d+'" fill="none" stroke="'+se.cor+'" stroke-width="2.4"'+(se.tracejado?' stroke-dasharray="6 4"':'')+'/>';
  se.valores.forEach(function(v,k){s+=TD.marca(se.marca||"circle",x(k),y(v),3.4,se.cor);});
 });
 el.innerHTML=s+"</svg>";
};

/* colunas agrupadas com valores positivos e negativos, linha opcional: {rotulos, series:[{nome,valores,cor,hach}], linha:{nome,valores,cor}, fmt, label} */
TD.colunas=function(el,o){
 var w=TD.wOf(el),h=o.h||(w<500?230:270),pl=w<500?54:66,pr=14,pt=14,pb=34,n=o.rotulos.length,ns=o.series.length;
 var all=[0];o.series.forEach(function(s){all=all.concat(s.valores);});if(o.linha)all=all.concat(o.linha.valores);
 var ax=eixoY(Math.min.apply(null,all),Math.max.apply(null,all));
 var y=function(v){return pt+(h-pt-pb)*(1-(v-ax.lo)/(ax.hi-ax.lo));};
 var gw=(w-pl-pr)/n,bw=Math.max(2,Math.min(26,(gw*0.78)/ns));
 var defs="";o.series.forEach(function(se,i){if(se.hach)defs+=TD.hach("ch"+el.id+i,se.cor,se.fundo);});
 var s=TD.svgOpen(w,h,o.label,defs);
 for(var g=ax.lo;g<=ax.hi+1e-9;g+=ax.st){var gy=y(g);s+='<line x1="'+pl+'" x2="'+(w-pr)+'" y1="'+gy+'" y2="'+gy+'" stroke="'+(Math.abs(g)<1e-9?"#9AA6B5":"#E1E6EC")+'"/><text x="'+(pl-6)+'" y="'+(gy+4)+'" text-anchor="end" font-size="11">'+TD.esc((o.fmtEixo||o.fmt)(g))+'</text>';}
 var step=Math.ceil(n/(w<500?4:8));
 for(var k=0;k<n;k++){
  var cx=pl+gw*k+gw/2,x0=cx-bw*ns/2;
  o.series.forEach(function(se,i){var v=se.valores[k],y0=y(0),y1=y(v);s+='<rect x="'+(x0+i*bw).toFixed(1)+'" y="'+Math.min(y0,y1).toFixed(1)+'" width="'+(bw-1).toFixed(1)+'" height="'+Math.max(0.5,Math.abs(y1-y0)).toFixed(1)+'" fill="'+(se.hach?"url(#ch"+el.id+i+")":se.cor)+'"/>';});
  if(k%step===0||k===n-1)s+='<text x="'+cx+'" y="'+(h-12)+'" text-anchor="middle" font-size="11">'+TD.esc(o.rotulos[k])+'</text>';
 }
 if(o.linha){var d="";o.linha.valores.forEach(function(v,k){d+=(k?"L":"M")+(pl+gw*k+gw/2).toFixed(1)+" "+y(v).toFixed(1);});s+='<path d="'+d+'" fill="none" stroke="'+o.linha.cor+'" stroke-width="2.4"/>';o.linha.valores.forEach(function(v,k){s+=TD.marca("diamond",pl+gw*k+gw/2,y(v),4,o.linha.cor);});}
 el.innerHTML=s+"</svg>";
};

/* barras horizontais: itens [{lab,v,txt,cor,hach}] */
TD.hbars=function(el,itens,o){
 var w=TD.wOf(el),lw=Math.min(o.labW||150,Math.round(w*0.4)),rh=o.rh||30,top=4,h=top+itens.length*rh+6;
 var maxLab=Math.max.apply(null,itens.map(function(i){return String(i.lab).length;}).concat([0]));
 if(maxLab*6.7>lw-8){
  // rótulos longos em tela estreita: rótulo acima de cada barra
  var rh2=rh+16,h2=top+itens.length*rh2+6,max2=Math.max.apply(null,itens.map(function(i){return i.v;}).concat([1e-9])),bw2=w-(o.valW||90);
  var defs2="";itens.forEach(function(it,k){if(it.hach)defs2+=TD.hach("hb"+el.id+k,it.cor,it.fundo);});
  var s2=TD.svgOpen(w,h2,o.label,defs2);
  itens.forEach(function(it,k){var y=top+k*rh2,bh=rh-12,len=Math.max(it.v>0?2:0,bw2*it.v/max2);
   s2+='<text x="0" y="'+(y+12)+'" font-size="12.5">'+TD.esc(it.lab)+'</text>';
   s2+='<rect x="0" y="'+(y+18)+'" width="'+len+'" height="'+bh+'" fill="'+(it.hach?"url(#hb"+el.id+k+")":(it.cor||"#1B3556"))+'"/>';
   s2+='<text x="'+(len+6)+'" y="'+(y+18+bh/2+5)+'" font-size="12.5" font-weight="600">'+TD.esc(it.txt)+'</text>';});
  el.innerHTML=s2+"</svg>";return;
 }
 var max=Math.max.apply(null,itens.map(function(i){return i.v;}).concat([1e-9]));
 var bw=w-lw-(o.valW||90);
 var defs="";itens.forEach(function(it,k){if(it.hach)defs+=TD.hach("hb"+el.id+k,it.cor,it.fundo);});
 var s=TD.svgOpen(w,h,o.label,defs);
 itens.forEach(function(it,k){
  var y=top+k*rh,bh=rh-12,len=Math.max(it.v>0?2:0,bw*it.v/max);
  s+='<text x="'+(lw-8)+'" y="'+(y+bh/2+5)+'" text-anchor="end" font-size="12.5">'+TD.esc(it.lab)+'</text>';
  s+='<rect x="'+lw+'" y="'+(y+2)+'" width="'+len+'" height="'+bh+'" fill="'+(it.hach?"url(#hb"+el.id+k+")":(it.cor||"#1B3556"))+'"/>';
  s+='<text x="'+(lw+len+6)+'" y="'+(y+bh/2+5)+'" font-size="12.5" font-weight="600">'+TD.esc(it.txt)+'</text>';
 });
 el.innerHTML=s+"</svg>";
};

/* barras divergentes (positivo à direita escuro, negativo à esquerda hachurado): grupos [{titulo, itens:[{lab,v}]}] */
TD.divergente=function(el,grupos,o){
 var w=TD.wOf(el),rh=26,itens=[];grupos.forEach(function(g){itens=itens.concat(g.itens);});
 var h=14+itens.length*rh+grupos.length*18+10;
 var lw=Math.min(o.labW||150,Math.round(w*0.36)),vw=w<500?66:92,half=(w-lw-vw*2)/2,zx=lw+vw+half;
 var mx=Math.max.apply(null,itens.map(function(i){return Math.abs(i.v);}).concat([1e-9]));
 var s=TD.svgOpen(w,h,o.label,TD.hach("dv"+el.id,"#9B2C2C"));
 s+='<line x1="'+zx+'" x2="'+zx+'" y1="10" y2="'+(h-6)+'" stroke="#9AA6B5"/>';
 var y=14;
 grupos.forEach(function(g){
  s+='<text x="'+lw+'" y="'+(y+2)+'" font-size="11.5" font-weight="600">'+TD.esc(g.titulo)+'</text>';y+=10;
  g.itens.forEach(function(it){
   var len=half*Math.abs(it.v)/mx;
   s+='<text x="'+(lw-8)+'" y="'+(y+13)+'" text-anchor="end" font-size="12">'+TD.esc(it.lab)+'</text>';
   if(it.v>=0)s+='<rect x="'+zx+'" y="'+(y+3)+'" width="'+len+'" height="'+(rh-10)+'" fill="#1B3556"/><text x="'+(zx+len+5)+'" y="'+(y+13)+'" font-size="11.5" font-weight="600">'+TD.esc(o.fmt(it.v))+'</text>';
   else s+='<rect x="'+(zx-len)+'" y="'+(y+3)+'" width="'+len+'" height="'+(rh-10)+'" fill="url(#dv'+el.id+')"/><text x="'+(zx-len-5)+'" y="'+(y+13)+'" text-anchor="end" font-size="11.5" font-weight="600" fill="#9B2C2C">'+TD.esc(o.fmt(it.v))+'</text>';
   y+=rh;
  });
  y+=8;
 });
 el.innerHTML=s+"</svg>";
};

/* cascata: passos [{lab, v, total:bool}] */
TD.cascata=function(el,passos,o){
 var w=TD.wOf(el),vert=w<560,n=passos.length;
 var acc=0,bars=[];passos.forEach(function(p){if(p.total){bars.push({a:0,b:p.v,p:p});acc=p.v;}else{bars.push({a:acc,b:acc+p.v,p:p});acc+=p.v;}});
 var lo=Math.min(0,Math.min.apply(null,bars.map(function(b){return Math.min(b.a,b.b);}))),hi=Math.max.apply(null,bars.map(function(b){return Math.max(b.a,b.b);}).concat([1e-9]));
 var defs=TD.hach("cc"+el.id,"#9B2C2C");
 var s,h;
 if(!vert){
  h=o.h||280;var pl=12,pr=12,pt=26,pb=48,gw=(w-pl-pr)/n,bw=Math.min(70,gw*0.62);
  var y=function(v){return pt+(h-pt-pb)*(1-(v-lo)/(hi-lo));};
  s=TD.svgOpen(w,h,o.label,defs);
  s+='<line x1="'+pl+'" x2="'+(w-pr)+'" y1="'+y(0)+'" y2="'+y(0)+'" stroke="#9AA6B5"/>';
  bars.forEach(function(b,k){
   var cx=pl+gw*k+gw/2,y1=y(Math.max(b.a,b.b)),y2=y(Math.min(b.a,b.b)),neg=!b.p.total&&b.p.v<0;
   var fill=b.p.total?(b.p.v<0?"url(#cc"+el.id+")":"#1B3556"):neg?"url(#cc"+el.id+")":"#5B7FA6";
   s+='<rect x="'+(cx-bw/2)+'" y="'+y1+'" width="'+bw+'" height="'+Math.max(1,y2-y1)+'" fill="'+fill+'"/>';
   if(k<n-1){var nx=pl+gw*(k+1)+gw/2;s+='<line x1="'+(cx+bw/2)+'" x2="'+(nx-bw/2)+'" y1="'+y(b.b)+'" y2="'+y(b.b)+'" stroke="#9AA6B5" stroke-dasharray="3 3"/>';}
   s+='<text x="'+cx+'" y="'+(y1-6)+'" text-anchor="middle" font-size="11.5" font-weight="600"'+(neg||(b.p.total&&b.p.v<0)?' fill="#9B2C2C"':'')+'>'+TD.esc((b.p.total||b.p.v<0?"":"+")+o.fmt(b.p.v))+'</text>';
   var words=b.p.lab.split(" "),l1="",l2="";words.forEach(function(wd){if((l1+" "+wd).trim().length<=14&&!l2)l1=(l1+" "+wd).trim();else l2=(l2+" "+wd).trim();});
   s+='<text x="'+cx+'" y="'+(h-pb+18)+'" text-anchor="middle" font-size="11">'+TD.esc(l1)+'</text>'+(l2?'<text x="'+cx+'" y="'+(h-pb+32)+'" text-anchor="middle" font-size="11">'+TD.esc(l2)+'</text>':'');
  });
 }else{
  var rh=30,lw=Math.round(w*0.42),vw=74;h=8+n*rh;
  var x=function(v){return lw+(w-lw-vw)*((v-lo)/(hi-lo));};
  s=TD.svgOpen(w,h,o.label,defs);
  s+='<line x1="'+x(0)+'" x2="'+x(0)+'" y1="2" y2="'+(h-2)+'" stroke="#9AA6B5"/>';
  bars.forEach(function(b,k){
   var yy=4+k*rh,x1=x(Math.min(b.a,b.b)),x2=x(Math.max(b.a,b.b)),neg=!b.p.total&&b.p.v<0;
   var fill=b.p.total?(b.p.v<0?"url(#cc"+el.id+")":"#1B3556"):neg?"url(#cc"+el.id+")":"#5B7FA6";
   s+='<text x="'+(lw-8)+'" y="'+(yy+16)+'" text-anchor="end" font-size="11.5"'+(b.p.total?' font-weight="600"':'')+'>'+TD.esc(b.p.lab)+'</text>';
   s+='<rect x="'+x1+'" y="'+(yy+4)+'" width="'+Math.max(1,x2-x1)+'" height="'+(rh-12)+'" fill="'+fill+'"/>';
   s+='<text x="'+(x2+5)+'" y="'+(yy+16)+'" font-size="11" font-weight="600"'+(neg||(b.p.total&&b.p.v<0)?' fill="#9B2C2C"':'')+'>'+TD.esc((b.p.total||b.p.v<0?"":"+")+o.fmt(b.p.v))+'</text>';
  });
 }
 el.innerHTML=s+"</svg>";
};

/* pareto: acumulado [0..1] */
TD.pareto=function(el,cum,o){
 var w=TD.wOf(el),h=w<500?230:260,pl=44,pr=16,pt=14,pb=38,n=cum.length,metade=0;
 for(var i=0;i<n;i++){if(cum[i]>=0.5-1e-12){metade=i+1;break;}}
 var x=function(k){return pl+(w-pl-pr)*(n<=1?1:k/(n-1));},y=function(v){return pt+(h-pt-pb)*(1-v);};
 var s=TD.svgOpen(w,h,o.label);
 [0,0.25,0.5,0.75,1].forEach(function(v){s+='<line x1="'+pl+'" x2="'+(w-pr)+'" y1="'+y(v)+'" y2="'+y(v)+'" stroke="#E1E6EC"/><text x="'+(pl-6)+'" y="'+(y(v)+4)+'" text-anchor="end" font-size="11">'+TD.pct(v,0)+'</text>';});
 if(o.faixas)o.faixas.forEach(function(f){s+='<line x1="'+pl+'" x2="'+(w-pr)+'" y1="'+y(f)+'" y2="'+y(f)+'" stroke="#C2A064" stroke-dasharray="2 3"/>';});
 if(n){
  var d="";cum.forEach(function(v,k){d+=(k?"L":"M")+x(k).toFixed(1)+" "+y(v).toFixed(1);});
  s+='<path d="'+d+'" fill="none" stroke="#1B3556" stroke-width="2.4"/>';
  if(metade){var mx=x(metade-1);s+='<line x1="'+mx+'" x2="'+mx+'" y1="'+y(0.5)+'" y2="'+y(0)+'" stroke="#7A5C2C" stroke-dasharray="4 3" stroke-width="1.6"/><line x1="'+pl+'" x2="'+mx+'" y1="'+y(0.5)+'" y2="'+y(0.5)+'" stroke="#7A5C2C" stroke-dasharray="4 3" stroke-width="1.6"/>'+TD.marca("diamond",mx,y(0.5),5,"#7A5C2C")+'<text x="'+(mx+8)+'" y="'+(y(0.5)+18)+'" font-size="12" font-weight="600">'+TD.esc(metade+" "+(metade===1?o.unidade1:o.unidade)+" = 50%")+'</text>';}
  s+='<text x="'+pl+'" y="'+(h-12)+'" font-size="11">1º</text><text x="'+(w-pr)+'" y="'+(h-12)+'" text-anchor="end" font-size="11">'+n+'º</text>';
 }
 el.innerHTML=s+"</svg>";
 return metade;
};

/* fluxo de arquitetura: fontes[] -> etapas[[t1,t2]] */
TD.arquitetura=function(el,fontes,etapas){
 var w=TD.wOf(el),vert=w<700,s,h;
 function box(x,y,bw,bh,t1,t2,dark){return '<rect x="'+x+'" y="'+y+'" width="'+bw+'" height="'+bh+'" rx="3" fill="'+(dark?"#12263F":"#FFFFFF")+'" stroke="'+(dark?"#C2A064":"#9AA6B5")+'" stroke-width="1.4"/><text x="'+(x+12)+'" y="'+(y+(t2?bh/2-2:bh/2+5))+'" font-size="13" font-weight="600" fill="'+(dark?"#FFFFFF":"#12263F")+'">'+TD.esc(t1)+'</text>'+(t2?'<text x="'+(x+12)+'" y="'+(y+bh/2+15)+'" font-size="11.5" fill="'+(dark?"#C9D3DF":"#4F5B6A")+'">'+TD.esc(t2)+'</text>':'');}
 function seta(x1,y1,x2,y2){return '<line x1="'+x1+'" y1="'+y1+'" x2="'+x2+'" y2="'+y2+'" stroke="#7A5C2C" stroke-width="1.6" marker-end="url(#ponta'+el.id+')"/>';}
 var defs='<marker id="ponta'+el.id+'" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0L10 5L0 10z" fill="#7A5C2C"/></marker>';
 var lab="Diagrama do fluxo de dados: "+fontes.join(", ")+" são extraídos para o PostgreSQL, passam pelas camadas staging, intermediate e marts do dbt e alimentam o painel.";
 if(!vert){
  var fw=Math.min(236,w*0.24),fh=40,gap=14;h=Math.max(fontes.length*(fh+gap)+30,120);
  s=TD.svgOpen(w,h,lab,defs);
  var sx=fw+60,ew=(w-sx-10-(etapas.length-1)*24)/etapas.length,ey=h/2-30,eh=60;
  var oy=(h-(fontes.length*(fh+gap)-gap))/2;
  fontes.forEach(function(f,i){var y=oy+i*(fh+gap);s+=box(0,y,fw,fh,f,"",false)+seta(fw,y+fh/2,sx-4,ey+eh/2);});
  etapas.forEach(function(e,i){var x=sx+i*(ew+24);s+=box(x,ey,ew,eh,e[0],e[1],i>0);if(i<etapas.length-1)s+=seta(x+ew,ey+eh/2,x+ew+22,ey+eh/2);});
  s+='<text x="'+(sx+ew+24)+'" y="'+(ey-12)+'" font-size="11.5" fill="#4F5B6A">transformação documentada e testada</text>';
 }else{
  var bw=w-20,bh=50,g=22,fy=10;h=fy+fontes.length*36+18+etapas.length*(bh+g);
  s=TD.svgOpen(w,h,lab,defs);
  fontes.forEach(function(f,i){s+=box(10,fy+i*36,bw,30,f,"",false);});
  var y0=fy+fontes.length*36+16;
  s+=seta(w/2,y0-14,w/2,y0-2);
  etapas.forEach(function(e,i){var y=y0+i*(bh+g);s+=box(10,y,bw,bh,e[0],e[1],i>0);if(i<etapas.length-1)s+=seta(w/2,y+bh,w/2,y+bh+g-2);});
 }
 el.innerHTML=s+"</svg>";
};

/* ---------- tabelas ---------- */
var TAB={};TD.TAB=TAB;
function ordena(st,rows){
 if(st.sort===null||!st.opt.sortable)return rows;
 var c=st.cols[st.sort];
 return rows.slice().sort(function(a,b){var x=c.v(a),y=c.v(b);if(typeof x==="string")return st.dir*x.localeCompare(y,"pt-BR");return st.dir*(x-y);});
}
TD.tabela=function(id,cols,rows,opt){
 opt=opt||{};
 var st=TAB[id]||{sort:opt.sort===undefined?null:opt.sort,dir:opt.dir||-1,all:false};
 st.cols=cols;st.rows=rows;st.opt=opt;TAB[id]=st;
 desenha(id);
};
function desenha(id){
 var st=TAB[id],cols=st.cols,opt=st.opt,rows=ordena(st,st.rows);
 var lim=opt.limit&&!st.all?opt.limit:rows.length,vis=rows.slice(0,lim);
 var maxes=cols.map(function(c){return c.bar?Math.max.apply(null,rows.map(function(r){return Math.abs(c.v(r));}).concat([1e-9])):0;});
 var h='<table'+(opt.cls?' class="'+opt.cls+'"':'')+'><caption class="sr">'+TD.esc(opt.caption||"")+'</caption><thead><tr>';
 cols.forEach(function(c,i){
  var cls=(c.num?"num":"")+(c.wrap?" wrapcell":"");cls=cls?' class="'+cls.trim()+'"':'';
  if(opt.sortable&&c.sort!==false){var as=st.sort===i?(st.dir>0?"ascending":"descending"):"none";
   h+='<th scope="col"'+cls+' aria-sort="'+as+'"><button class="sort" type="button" data-t="'+id+'" data-c="'+i+'">'+TD.esc(c.l)+'<span class="arr" aria-hidden="true">'+(st.sort===i?(st.dir>0?"▲":"▼"):"")+'</span></button></th>';}
  else h+='<th scope="col"'+cls+'>'+TD.esc(c.l)+'</th>';
 });
 h+='</tr></thead><tbody>';
 vis.forEach(function(r){
  h+='<tr'+(opt.rowClass?' class="'+opt.rowClass(r)+'"':'')+'>';
  cols.forEach(function(c,i){
   var txt=c.f?c.f(r):TD.esc(c.v(r));
   var cls=((c.num?"num":"")+(c.wrap?" wrapcell":"")+(c.cls?" "+c.cls(r):"")).trim();
   var sty=c.style?' style="'+c.style(r)+'"':'';
   if(c.bar){var pr=Math.max(0,Math.min(100,100*Math.abs(c.v(r))/maxes[i]));txt='<span class="barcell">'+txt+'<span class="track" aria-hidden="true"><span style="width:'+pr.toFixed(1)+'%"'+(c.alt?' class="alt"':'')+'></span></span></span>';}
   if(i===0&&opt.rowHeader)h+='<th scope="row"'+(cls?' class="'+cls+'"':'')+sty+'>'+txt+'</th>';else h+='<td'+(cls?' class="'+cls+'"':'')+sty+'>'+txt+'</td>';
  });
  h+='</tr>';
 });
 h+='</tbody>';
 if(opt.foot)h+='<tfoot><tr>'+opt.foot.map(function(x,i){return '<td class="'+(cols[i]&&cols[i].num?"num":"")+'">'+x+'</td>';}).join("")+'</tr></tfoot>';
 h+='</table>';
 document.getElementById(opt.el).innerHTML=h;
 if(opt.limit&&opt.more){
  var m=document.getElementById(opt.more);
  m.innerHTML=rows.length>opt.limit?'<button type="button" class="btn btn-line btn-sm" data-more="'+id+'">'+(st.all?"Mostrar só os "+opt.limit+" primeiros":"Mostrar todos ("+rows.length+")")+'</button>':"";
 }
}
function csvNum(v){return typeof v==="number"?String(Math.round(v*100)/100).replace(".",","):v;}
TD.exportarCSV=function(id){
 var st=TAB[id];if(!st)return;
 var rows=ordena(st,st.rows);
 var q=function(s){s=String(s);return /[;"\n]/.test(s)?'"'+s.replace(/"/g,'""')+'"':s;};
 var lines=[st.cols.map(function(c){return q(c.l);}).join(";")];
 rows.forEach(function(r){lines.push(st.cols.map(function(c){return q(csvNum(c.csv?c.csv(r):c.v(r)));}).join(";"));});
 var blob=new Blob(["﻿"+lines.join("\r\n")],{type:"text/csv;charset=utf-8"});
 var a=document.createElement("a");a.href=URL.createObjectURL(blob);a.download=(TD.slug||"demo")+"-"+id+"-"+(TD.F&&TD.F.per||"")+".csv";
 document.body.appendChild(a);a.click();setTimeout(function(){URL.revokeObjectURL(a.href);a.remove();},500);
};
document.addEventListener("click",function(ev){
 var b=ev.target.closest&&ev.target.closest("button.sort");
 if(b){var st=TAB[b.dataset.t],c=+b.dataset.c;if(st.sort===c)st.dir=-st.dir;else{st.sort=c;st.dir=st.cols[c].num?-1:1;}desenha(b.dataset.t);var nb=document.querySelector('button.sort[data-t="'+b.dataset.t+'"][data-c="'+c+'"]');if(nb)nb.focus();return;}
 var mb=ev.target.closest&&ev.target.closest("button[data-more]");
 if(mb){var s2=TAB[mb.dataset.more];s2.all=!s2.all;desenha(mb.dataset.more);return;}
 var cb=ev.target.closest&&ev.target.closest("button[data-csv]");
 if(cb)TD.exportarCSV(cb.dataset.csv);
});

/* ---------- cartões ---------- */
TD.kpis=function(el,lista){document.getElementById(el).innerHTML=lista.map(function(x){return '<div class="card kpi '+(x.cls||"")+'"><span class="lab">'+TD.esc(x.l)+'</span><span class="val">'+TD.esc(x.v)+'</span><span class="sub">'+TD.esc(x.s||"")+'</span></div>';}).join("");};
TD.achados=function(el,lista){document.getElementById(el).innerHTML=lista.map(function(x){return '<article class="card achado"><h3>'+TD.esc(x.t)+'</h3><p>'+TD.esc(x.p)+'</p><span class="acao">'+TD.esc(x.a)+'</span></article>';}).join("");};
TD.preencher=function(sel,ops){ops.forEach(function(x){var o=document.createElement("option");o.value=x[0];o.textContent=x[1];sel.appendChild(o);});};

/* ---------- aplicação: filtros, abas e estado ---------- */
TD.iniciar=function(cfg){
 TD.slug=cfg.slug;
 var F=JSON.parse(JSON.stringify(cfg.padrao)),dirty={},ativa=cfg.inicial;
 TD.F=F;
 var API={};
 function atualizar(){
  var t0=performance.now();
  TD.M=cfg.calcular(F);
  Object.keys(cfg.render).forEach(function(k){dirty[k]=true;});
  cfg.render[ativa]();dirty[ativa]=false;
  var sc=document.getElementById("scope");if(sc)sc.textContent=cfg.escopo(TD.M,F);
  API.ultimoMs=performance.now()-t0;
 }
 cfg.filtros.forEach(function(f){
  var sel=document.getElementById(f.el);sel.value=String(F[f.campo]);
  sel.addEventListener("change",function(){F[f.campo]=f.num?+sel.value:sel.value;if(cfg.aoMudar)cfg.aoMudar(f.campo,F);atualizar();});
 });
 var lp=document.getElementById("f-limpar");
 if(lp)lp.addEventListener("click",function(){Object.keys(cfg.padrao).forEach(function(k){F[k]=cfg.padrao[k];});cfg.filtros.forEach(function(f){document.getElementById(f.el).value=String(F[f.campo]);});if(cfg.aoMudar)cfg.aoMudar("*",F);atualizar();});
 var tabs=[].slice.call(document.querySelectorAll('[role="tab"]'));
 function abrir(tab,foco){
  tabs.forEach(function(t){var on=t===tab;t.setAttribute("aria-selected",on?"true":"false");t.tabIndex=on?0:-1;document.getElementById(t.getAttribute("aria-controls")).hidden=!on;});
  ativa=tab.id.slice(2);if(dirty[ativa]!==false){cfg.render[ativa]();dirty[ativa]=false;}
  if(foco)tab.focus();
 }
 tabs.forEach(function(t,i){
  t.addEventListener("click",function(){abrir(t,false);});
  t.addEventListener("keydown",function(e){var k=e.key,j=null;if(k==="ArrowRight")j=(i+1)%tabs.length;else if(k==="ArrowLeft")j=(i-1+tabs.length)%tabs.length;else if(k==="Home")j=0;else if(k==="End")j=tabs.length-1;if(j!==null){e.preventDefault();abrir(tabs[j],true);}});
 });
 var rt=null,lastW=window.innerWidth;
 window.addEventListener("resize",function(){if(Math.abs(window.innerWidth-lastW)<20)return;lastW=window.innerWidth;clearTimeout(rt);rt=setTimeout(function(){Object.keys(cfg.render).forEach(function(k){dirty[k]=true;});cfg.render[ativa]();dirty[ativa]=false;},150);});
 API.calcular=cfg.calcular;API.periodos=cfg.periodos;API.dados=cfg.dados;
 API.renderTodas=function(){Object.keys(cfg.render).forEach(function(k){var p=document.getElementById("p-"+k),hid=p.hidden;p.hidden=false;cfg.render[k]();p.hidden=hid;dirty[k]=false;});};
 API.aplicar=function(f){Object.keys(f).forEach(function(k){F[k]=f[k];});if(cfg.aoMudar)cfg.aoMudar("*",F);cfg.filtros.forEach(function(fl){document.getElementById(fl.el).value=String(F[fl.campo]);});atualizar();};
 API.abrir=function(id){abrir(document.getElementById("t-"+id),false);};
 API.estado=function(){return TD.M;};
 API.verificar=cfg.verificar;
 window.DEMO=API;
 atualizar();
 return API;
};
return TD;
})();
