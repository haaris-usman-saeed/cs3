(function(root){
  'use strict';
  function sigmoid(z){return z>=0?1/(1+Math.exp(-z)):Math.exp(z)/(1+Math.exp(z));}
  function softplus(z){return Math.max(0,z)+Math.log1p(Math.exp(-Math.abs(z)));}
  function logLoss(z,y){return y===1?softplus(-z):softplus(z);}
  function gradients(rows,b,w){
    let gb=0,gw=0,loss=0;
    for(const row of rows){const z=b+w*row.x,p=sigmoid(z),e=p-row.y;gb+=e;gw+=e*row.x;loss+=logLoss(z,row.y);}
    return {gb:gb/rows.length,gw:gw/rows.length,loss:loss/rows.length};
  }
  function step(rows,b,w,eta){const g=gradients(rows,b,w);return {b:b-eta*g.gb,w:w-eta*g.gw,...g};}
  function metrics(rows,threshold=.5){
    let tp=0,fp=0,tn=0,fn=0;
    for(const row of rows){if(row.p>=threshold){if(row.y===1)tp++;else fp++;}else{if(row.y===1)fn++;else tn++;}}
    return countMetrics(tp,fp,tn,fn);
  }
  function countMetrics(tp,fp,tn,fn){const n=tp+fp+tn+fn;return {tp,fp,tn,fn,n,accuracy:n?(tp+tn)/n:null,error:n?(fp+fn)/n:null,precision:tp+fp?tp/(tp+fp):null,recall:tp+fn?tp/(tp+fn):null,fnr:tp+fn?fn/(tp+fn):null};}
  function seededSplit(penguins,seed=42){
    let state=seed>>>0;const random=()=>{state=(Math.imul(state,1664525)+1013904223)>>>0;return state/4294967296;};
    const rows=penguins.map(r=>({mass:r.mass,x:(r.mass-4000)/1000,y:r.species==='Gentoo'?1:0}));
    for(let i=rows.length-1;i>0;i--){const j=Math.floor(random()*(i+1));[rows[i],rows[j]]=[rows[j],rows[i]];}
    return {train:rows.slice(0,191),test:rows.slice(191)};
  }
  function ols(rows){const mx=rows.reduce((s,r)=>s+r.x,0)/rows.length,my=rows.reduce((s,r)=>s+r.y,0)/rows.length;let num=0,den=0;rows.forEach(r=>{num+=(r.x-mx)*(r.y-my);den+=(r.x-mx)**2;});const w=num/den;return {b:my-w*mx,w};}
  const api={sigmoid,softplus,logLoss,gradients,step,metrics,countMetrics,seededSplit,ols};
  if(typeof module==='object'&&module.exports)module.exports=api;else root.LM=api;
})(typeof window!=='undefined'?window:globalThis);
