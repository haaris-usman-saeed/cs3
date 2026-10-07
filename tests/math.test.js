'use strict';
const assert=require('node:assert/strict');
const test=require('node:test');
const fs=require('node:fs');
const vm=require('node:vm');
const M=require('../math.js');
const near=(actual,expected,tolerance=1e-10)=>assert.ok(Math.abs(actual-expected)<tolerance,`${actual} != ${expected}`);

test('lecture probability, odds, and both recorded-species losses',()=>{
  const z=-.2+1.4*.5,p=M.sigmoid(z);
  near(z,.5);near(p,.6224593312018546);
  near(p/(1-p),Math.exp(z));
  near(M.logLoss(z,1),.4740769841801067);
  near(M.logLoss(z,0),.9740769841801067);
});
test('score-based log loss remains finite for extreme scores',()=>{
  for(const z of [-1000,-10,0,10,1000]){
    assert.ok(M.sigmoid(z)>=0&&M.sigmoid(z)<=1);
    for(const y of [0,1])assert.ok(Number.isFinite(M.logLoss(z,y))&&M.logLoss(z,y)>=0);
  }
  near(M.logLoss(1000,0),1000);near(M.logLoss(-1000,1),1000);
});
test('analytical gradients agree with numerical derivatives on mixed rows',()=>{
  const rows=[{x:-1.2,y:0},{x:.3,y:1},{x:2,y:0},{x:-.4,y:1}],b=-.2,w=.7,h=1e-5;
  const g=M.gradients(rows,b,w);
  near(g.gb,(M.gradients(rows,b+h,w).loss-M.gradients(rows,b-h,w).loss)/(2*h),1e-8);
  near(g.gw,(M.gradients(rows,b,w+h).loss-M.gradients(rows,b,w-h).loss)/(2*h),1e-8);
});
test('lecture simultaneous average-gradient update',()=>{
  const rows=[{x:-1,y:0},{x:0,y:0},{x:1,y:1}],g=M.gradients(rows,0,0),s=M.step(rows,0,0,.3);
  near(g.gb,1/6);near(g.gw,-1/3);near(g.loss,Math.log(2));
  near(s.b,-.05);near(s.w,.1);
  assert.ok(M.gradients(rows,s.b,s.w).loss<g.loss);
});
test('lecture confusion matrix and undefined denominators',()=>{
  const s=M.countMetrics(32,2,44,5);
  near(s.accuracy,76/83);near(s.error,7/83);near(s.precision,32/34);near(s.recall,32/37);
  near(s.fnr,5/37);near(s.fnr+s.recall,1);
  assert.equal(M.countMetrics(0,0,5,2).precision,null);
  assert.equal(M.countMetrics(0,3,5,0).recall,null);
});
test('cutoff ties go to positive, and recall cannot increase with cutoff',()=>{
  const rows=[{p:.5,y:1},{p:.9,y:0},{p:.3,y:1}];
  assert.equal(M.metrics(rows,.5).tp,1);
  assert.ok(M.metrics(rows,.8).recall<=M.metrics(rows,.5).recall);
});
test('real penguin split is reproducible, disjoint, and learns without test labels',()=>{
  const context={window:{}};vm.runInNewContext(fs.readFileSync(require.resolve('../data/penguins.js'),'utf8'),context);
  const rows=context.window.PENGUINS;assert.equal(rows.length,274);
  const split=M.seededSplit(rows),again=M.seededSplit(rows);
  assert.equal(split.train.length,191);assert.equal(split.test.length,83);
  assert.deepEqual(split,again);
  assert.ok(split.train.every(r=>!split.test.includes(r)));
  let b=0,w=0,initial=M.gradients(split.train,b,w).loss;
  for(let i=0;i<1000;i++){({b,w}=M.step(split.train,b,w,.08));}
  assert.ok(M.gradients(split.train,b,w).loss<initial);
  assert.ok(w>0);
  console.log('Live seeded fit:',{b,w,trainingLoss:M.gradients(split.train,b,w).loss,test:M.metrics(split.test.map(r=>({...r,p:M.sigmoid(b+w*r.x)})))});
});
