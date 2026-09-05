(function(root,factory){
'use strict';
let enemyPlanner=root.WOFAlphaEnemyTargetLabels;
let playerPlanner=root.WOFAlphaPlayerHeadWarning;
if(typeof module!=='undefined'&&module.exports){
  try{enemyPlanner=require('./wof_alpha_enemy_target_labels.js');}catch(_){}
  try{playerPlanner=require('./wof_alpha_player_head_warning.js');}catch(_){}
}
const api=factory(enemyPlanner,playerPlanner);
if(typeof module!=='undefined'&&module.exports)module.exports=api;
root.WOFAlphaCanonicalOverlayPlan=api;
})(typeof self!=='undefined'?self:globalThis,function(defaultEnemyPlanner,defaultPlayerPlanner){
'use strict';

const SCHEMA='wof-alpha-canonical-overlay-plan-v1';
const VERSION='wof-alpha-canonical-overlay-product-plan-v1';
const MODE='canonical-render-anchor';
const COORDINATE_SPACE='webgl-drawing-buffer';
const FALLBACK='NONE';

const arrayOf=value=>Array.isArray(value)?value:[];

function plannerDependencies(enemyPlanner,playerPlanner){
  const missing=[];
  if(!enemyPlanner||typeof enemyPlanner.buildCanonicalPlan!=='function')missing.push('P6_ENEMY_CANONICAL_PLANNER_MISSING');
  if(!playerPlanner||typeof playerPlanner.buildCanonicalPlan!=='function')missing.push('P7_PLAYER_CANONICAL_PLANNER_MISSING');
  return{ok:missing.length===0,missing};
}

function canonicalBindingOf(canonicalAuthority,authorityBinding){
  if(canonicalAuthority&&authorityBinding){
    const keys=['authorityKey','runtimeEpoch','rendererEpoch'];
    if(keys.some(key=>canonicalAuthority[key]!==authorityBinding[key])){
      return{ok:false,reason:'CANONICAL_AUTHORITY_BINDING_MISMATCH',binding:null};
    }
  }
  const binding=canonicalAuthority||authorityBinding||null;
  if(!binding||typeof binding!=='object'){
    return{ok:false,reason:'CANONICAL_AUTHORITY_MISSING',binding:null};
  }
  return{ok:true,reason:null,binding};
}

function validateBinding(binding,enemyPlanner,playerPlanner){
  if(!binding)return{ok:false,reason:'CANONICAL_AUTHORITY_MISSING'};
  if(typeof enemyPlanner?.validateCanonicalAuthority==='function'){
    const result=enemyPlanner.validateCanonicalAuthority(binding);
    if(!result?.ok)return{ok:false,reason:result?.reason||'CANONICAL_AUTHORITY_INVALID'};
  }else{
    return{ok:false,reason:'P6_CANONICAL_AUTHORITY_VALIDATOR_MISSING'};
  }
  if(typeof playerPlanner?.validAuthorityBinding!=='function'){
    return{ok:false,reason:'P7_CANONICAL_AUTHORITY_VALIDATOR_MISSING'};
  }
  if(playerPlanner.validAuthorityBinding(binding)!==true){
    return{ok:false,reason:'CANONICAL_AUTHORITY_INVALID'};
  }
  return{ok:true,reason:null};
}

function callPlanner(planner,args,kind){
  try{
    const plan=planner.buildCanonicalPlan(args);
    if(!plan||typeof plan!=='object')return{ok:false,reason:kind+'_PLAN_INVALID',plan:null};
    if(plan.mode!==MODE)return{ok:false,reason:kind+'_PLAN_MODE_INVALID',plan};
    if(plan.coordinateSpace!==COORDINATE_SPACE)return{ok:false,reason:kind+'_PLAN_COORDINATE_SPACE_INVALID',plan};
    return{ok:true,reason:null,plan};
  }catch(error){
    return{ok:false,reason:kind+'_PLAN_EXCEPTION',detail:String(error?.message||error),plan:null};
  }
}

function countReasons(rows){
  const counts={};
  for(const row of arrayOf(rows)){
    const reason=typeof row?.reason==='string'&&row.reason?row.reason:'UNKNOWN';
    counts[reason]=(counts[reason]||0)+1;
  }
  return counts;
}

function channelState(requested,emitted,plannerOk){
  if(!plannerOk)return'SUPPRESSED';
  if(emitted>0||requested===0)return'READY';
  return'SUPPRESSED';
}

function createPlanner({enemyPlanner=defaultEnemyPlanner,playerPlanner=defaultPlayerPlanner}={}){
  function buildCanonicalPlan({
    enemy={},
    player={},
    canonicalAuthority,
    authorityBinding,
    drawingBufferState,
    nowMs
  }={}){
    const dependencies=plannerDependencies(enemyPlanner,playerPlanner);
    const bindingResult=canonicalBindingOf(canonicalAuthority,authorityBinding);
    const binding=bindingResult.binding;
    const bindingValidation=dependencies.ok&&bindingResult.ok
      ?validateBinding(binding,enemyPlanner,playerPlanner)
      :{ok:false,reason:bindingResult.reason||dependencies.missing[0]||'CANONICAL_DEPENDENCY_INVALID'};

    const globalSuppressed=[];
    for(const reason of dependencies.missing)globalSuppressed.push({reason});
    if(!bindingResult.ok)globalSuppressed.push({reason:bindingResult.reason});
    else if(!bindingValidation.ok)globalSuppressed.push({reason:bindingValidation.reason});

    let enemyResult={ok:false,reason:'P6_ENEMY_CANONICAL_PLANNER_MISSING',plan:null};
    let playerResult={ok:false,reason:'P7_PLAYER_CANONICAL_PLANNER_MISSING',plan:null};

    if(dependencies.ok){
      enemyResult=callPlanner(enemyPlanner,{
        markers:enemy.markers,
        canonicalAnchors:enemy.canonicalAnchors,
        canonicalAuthority:binding,
        drawingBufferState,
        nowMs,
        markerMaxAgeMs:enemy.markerMaxAgeMs,
        canonicalAnchorMaxAgeMs:enemy.canonicalAnchorMaxAgeMs,
        drawingBufferMaxAgeMs:enemy.drawingBufferMaxAgeMs,
        labelWidth:enemy.labelWidth,
        labelHeight:enemy.labelHeight
      },'P6_ENEMY_CANONICAL');
      playerResult=callPlanner(playerPlanner,{
        warnings:player.warnings,
        canonicalAnchors:player.canonicalAnchors,
        playerGenerations:player.playerGenerations,
        authorityBinding:binding,
        drawingBufferState,
        nowMs,
        warningSampleAt:player.warningSampleAt,
        anchorMaxAgeMs:player.anchorMaxAgeMs,
        boxWidth:player.boxWidth,
        boxHeight:player.boxHeight
      },'P7_PLAYER_CANONICAL');
      if(!enemyResult.ok)globalSuppressed.push({reason:enemyResult.reason,detail:enemyResult.detail||null});
      if(!playerResult.ok)globalSuppressed.push({reason:playerResult.reason,detail:playerResult.detail||null});
    }

    const authorityReady=dependencies.ok&&bindingResult.ok&&bindingValidation.ok;
    const enemyPlan=enemyResult.plan||{};
    const playerPlan=playerResult.plan||{};
    const enemyRequested=arrayOf(enemy.markers).length;
    const playerRequested=arrayOf(player.warnings).length;

    const enemyLabels=authorityReady&&enemyResult.ok?arrayOf(enemyPlan.labels).slice():[];
    const playerWarnings=authorityReady&&playerResult.ok?arrayOf(playerPlan.anchored).slice():[];
    const enemySuppressed=arrayOf(enemyPlan.suppressed);
    const playerSuppressed=arrayOf(playerPlan.suppressed);

    const drawIntents=[];
    for(const payload of enemyLabels){
      drawIntents.push(Object.freeze({kind:'enemy-target-label',source:'P6',payload}));
    }
    for(const payload of playerWarnings){
      drawIntents.push(Object.freeze({kind:'player-danger-warning',source:'P7',payload}));
    }

    const requested=enemyRequested+playerRequested;
    const mappingKeys={
      enemy:enemyResult.ok&&typeof enemyPlan.mappingKey==='string'?enemyPlan.mappingKey:null,
      player:playerWarnings.map(row=>row?.anchor?.mappingKey||null).filter(value=>typeof value==='string'&&value)
    };

    const finalState=globalSuppressed.length>0
      ?'SUPPRESSED'
      :(drawIntents.length>0||requested===0?'READY':'SUPPRESSED');
    const finalReason=finalState==='SUPPRESSED'
      ?(globalSuppressed[0]?.reason||'NO_READY_CANONICAL_DRAW_INTENTS')
      :null;

    return{
      schema:SCHEMA,
      version:VERSION,
      mode:MODE,
      coordinateSpace:COORDINATE_SPACE,
      state:finalState,
      reason:finalReason,
      canonical:true,
      fallback:FALLBACK,
      readOnly:true,
      ramWrites:0,
      inputInjection:false,
      authority:bindingValidation.ok?{
        authorityKey:binding.authorityKey,
        runtimeEpoch:binding.runtimeEpoch,
        rendererEpoch:binding.rendererEpoch
      }:null,
      drawIntents,
      enemyTargetLabels:enemyLabels,
      playerDangerWarnings:playerWarnings,
      suppression:{
        global:globalSuppressed,
        enemy:enemySuppressed,
        player:playerSuppressed
      },
      diagnostics:{
        requested:{enemyTargetLabels:enemyRequested,playerDangerWarnings:playerRequested,total:requested},
        emitted:{enemyTargetLabels:enemyLabels.length,playerDangerWarnings:playerWarnings.length,total:drawIntents.length},
        suppressed:{enemy:enemySuppressed.length,player:playerSuppressed.length,global:globalSuppressed.length},
        suppressionReasons:{
          enemy:countReasons(enemySuppressed),
          player:countReasons(playerSuppressed),
          global:countReasons(globalSuppressed)
        },
        channels:{
          enemy:channelState(enemyRequested,enemyLabels.length,authorityReady&&enemyResult.ok),
          player:channelState(playerRequested,playerWarnings.length,authorityReady&&playerResult.ok)
        },
        mappingKeys,
        dependencyVersions:{
          p6:enemyPlanner?.CANONICAL_PLAN_VERSION||enemyPlanner?.VERSION||null,
          p7:playerPlanner?.CANONICAL_GEOMETRY_VERSION||playerPlanner?.VERSION||null
        }
      }
    };
  }
  return{buildCanonicalPlan};
}

const defaultPlanner=createPlanner();
return{
  SCHEMA,VERSION,MODE,COORDINATE_SPACE,FALLBACK,
  createPlanner,
  buildCanonicalPlan:defaultPlanner.buildCanonicalPlan
};
});
