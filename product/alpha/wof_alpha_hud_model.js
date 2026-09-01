(function(root){
'use strict';
const VERSION='wof-alpha-hud-model-rc2';
const SIDE_ZH={LEFT:'左侧',RIGHT:'右侧',CENTER:'近身'};
const TARGET_ORDER={P1:1,P2:2,P3:3};
function summarizeWarnings(input){
  const warnings=Array.isArray(input)?input.filter(Boolean):[];
  const groups=new Map();
  for(const w of warnings){
    const target=['P1','P2','P3'].includes(w.target)?w.target:'?';
    const side=SIDE_ZH[w.threatSide]||'方向未知';
    const key=target+'|'+side;
    let g=groups.get(key);
    if(!g){g={target,side,count:0,dangerOnly:false,attacks:new Set()};groups.set(key,g);}
    g.count++;
    if(w.attackSpecific&&Number.isFinite(+w.attack))g.attacks.add('A'+(+w.attack));
    else g.dangerOnly=true;
  }
  const rows=[...groups.values()].sort((a,b)=>(TARGET_ORDER[a.target]||9)-(TARGET_ORDER[b.target]||9)||a.side.localeCompare(b.side,'zh-CN')).map(g=>{
    const details=[...(g.dangerOnly?['危险']:[]),...[...g.attacks].sort()].join('/');
    const suffix=g.count>1?' ×'+g.count:'';
    return{target:g.target,side:g.side,count:g.count,attacks:[...g.attacks].sort(),dangerOnly:g.dangerOnly,label:`${g.target} ${g.side} ${details||'危险'}${suffix}`};
  });
  return{count:warnings.length,groupCount:rows.length,groups:rows,lines:rows.map(x=>x.label)};
}
const api={VERSION,summarizeWarnings};
if(typeof module!=='undefined'&&module.exports)module.exports=api;
root.WOFAlphaHudModel=api;
})(typeof self!=='undefined'?self:globalThis);
