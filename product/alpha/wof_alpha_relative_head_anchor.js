(function(root,factory){
'use strict';
const api=factory();
if(typeof module!=='undefined'&&module.exports)module.exports=api;
root.WOFAlphaRelativeHeadAnchor=api;
})(typeof self!=='undefined'?self:globalThis,function(){
'use strict';

const VERSION='wof-alpha-relative-head-anchor-v1';
const NATIVE_WIDTH=384,NATIVE_HEIGHT=224;
const Y_MODELS=Object.freeze(['Y-Z','Y+Z','Y']);
const SIGNS=Object.freeze([1,-1]);
const finite=Number.isFinite;
const clamp=(v,a,b)=>Math.min(b,Math.max(a,v));

function baseY(y,z,model){
  if(!finite(y)||!finite(z)||!Y_MODELS.includes(model))return null;
  if(model==='Y-Z')return y-z;
  if(model==='Y+Z')return y+z;
  return y;
}

function nativeFromCss({x,y,cssWidth,cssHeight,drawingBufferState}={}){
  const db=drawingBufferState,rect=db?.contentRect;
  if(![x,y,cssWidth,cssHeight,db?.width,db?.height,rect?.x,rect?.y,rect?.width,rect?.height].every(finite))return null;
  if(cssWidth<=0||cssHeight<=0||db.width<=0||db.height<=0||rect.width<=0||rect.height<=0)return null;
  const xDb=x/cssWidth*db.width,yDb=y/cssHeight*db.height;
  if(xDb<rect.x||xDb>rect.x+rect.width||yDb<rect.y||yDb>rect.y+rect.height)return null;
  return{
    x:(xDb-rect.x)/rect.width*NATIVE_WIDTH,
    y:(yDb-rect.y)/rect.height*NATIVE_HEIGHT,
    xDb,yDb
  };
}

function spread(values){
  if(!Array.isArray(values)||!values.length)return Infinity;
  const mean=values.reduce((a,b)=>a+b,0)/values.length;
  return Math.sqrt(values.reduce((a,b)=>a+(b-mean)*(b-mean),0)/values.length);
}

function range(values){return values.length?Math.max(...values)-Math.min(...values):0;}

function fitVertical(samples,{minSamples=6,minYRange=5,minZRange=5,maxResidual=2.5,minGap=0.75}={}){
  const rows=(Array.isArray(samples)?samples:[]).filter(s=>[s?.headNativeY,s?.worldY,s?.worldZ].every(finite));
  if(rows.length<minSamples)return{ok:false,reason:'INSUFFICIENT_SAMPLES',sampleCount:rows.length};
  const yRange=range(rows.map(r=>r.worldY)),zRange=range(rows.map(r=>r.worldZ));
  if(Math.max(yRange,zRange)<minYRange)return{ok:false,reason:'INSUFFICIENT_VERTICAL_MOTION',sampleCount:rows.length,yRange,zRange};
  const ranked=[];
  for(const sign of SIGNS){
    for(const model of Y_MODELS){
      const offsets=[];
      for(const row of rows){const b=baseY(row.worldY,row.worldZ,model);if(!finite(b))continue;offsets.push(row.headNativeY-sign*b);}
      ranked.push({sign,model,residual:spread(offsets),offset:offsets.reduce((a,b)=>a+b,0)/Math.max(1,offsets.length)});
    }
  }
  ranked.sort((a,b)=>a.residual-b.residual);
  const best=ranked[0],second=ranked[1];
  if(!best||best.residual>maxResidual)return{ok:false,reason:'NO_STABLE_VERTICAL_MODEL',sampleCount:rows.length,yRange,zRange,ranked};
  const signPeers=ranked.filter(r=>r.sign===best.sign);
  const oppositeBest=ranked.find(r=>r.sign!==best.sign);
  if(oppositeBest&&oppositeBest.residual-best.residual<minGap)return{ok:false,reason:'AMBIGUOUS_Y_AXIS_SIGN',sampleCount:rows.length,yRange,zRange,ranked};
  const modelResolved=zRange>=minZRange && (!second||second.residual-best.residual>=minGap);
  return{
    ok:true,reason:modelResolved?'STABLE_MODEL':'SIGN_ONLY_Z_NOT_SEPARATED',sampleCount:rows.length,yRange,zRange,
    sign:best.sign,model:modelResolved?best.model:null,preferredModel:best.model,residual:best.residual,offset:best.offset,ranked:ranked.slice(0,4)
  };
}

function projectEnemyRelative({enemy,p1,p1HeadNative,fit,extraClearanceNative=0}={}){
  if(!enemy||!p1||!p1HeadNative||!fit?.ok)return{ok:false,reason:'RELATIVE_AUTHORITY_MISSING'};
  if(![enemy.x,enemy.y,enemy.z,p1.x,p1.y,p1.z,p1HeadNative.x,p1HeadNative.y,extraClearanceNative].every(finite))return{ok:false,reason:'NONFINITE_RELATIVE_INPUT'};
  const sign=fit.sign;
  if(sign!==1&&sign!==-1)return{ok:false,reason:'Y_AXIS_SIGN_UNRESOLVED'};
  let dy;
  if(fit.model){
    const eb=baseY(enemy.y,enemy.z,fit.model),pb=baseY(p1.y,p1.z,fit.model);
    if(!finite(eb)||!finite(pb))return{ok:false,reason:'INVALID_Y_MODEL'};
    dy=sign*(eb-pb);
  }else{
    if(Math.abs(enemy.z-p1.z)>1.5)return{ok:false,reason:'Z_MODEL_UNRESOLVED'};
    dy=sign*(enemy.y-p1.y);
  }
  const x=p1HeadNative.x+(enemy.x-p1.x);
  const y=p1HeadNative.y+dy-extraClearanceNative;
  if(![x,y].every(finite))return{ok:false,reason:'RELATIVE_PROJECTION_NONFINITE'};
  if(x<0||x>=NATIVE_WIDTH||y<0||y>=NATIVE_HEIGHT)return{ok:false,reason:'RELATIVE_PROJECTION_OUT_OF_BOUNDS'};
  return{ok:true,x,y,sign,model:fit.model||null,preferredModel:fit.preferredModel||null,extraClearanceNative};
}

function nativeToDb(point,drawingBufferState){
  const rect=drawingBufferState?.contentRect;
  if(!point?.ok||![rect?.x,rect?.y,rect?.width,rect?.height].every(finite)||rect.width<=0||rect.height<=0)return null;
  return{x:rect.x+point.x/NATIVE_WIDTH*rect.width,y:rect.y+point.y/NATIVE_HEIGHT*rect.height};
}

function labelRect(pointDb,drawingBufferState,width=30,height=18){
  const rect=drawingBufferState?.contentRect;
  if(!pointDb||![pointDb.x,pointDb.y,rect?.x,rect?.y,rect?.width,rect?.height,width,height].every(finite))return null;
  const w=Math.min(width,rect.width),h=Math.min(height,rect.height);
  return{x:clamp(pointDb.x-w/2,rect.x,rect.x+Math.max(0,rect.width-w)),y:clamp(pointDb.y-h/2,rect.y,rect.y+Math.max(0,rect.height-h)),width:w,height:h};
}

return{VERSION,NATIVE_WIDTH,NATIVE_HEIGHT,Y_MODELS,SIGNS,baseY,nativeFromCss,fitVertical,projectEnemyRelative,nativeToDb,labelRect};
});
