(function(root,factory){
'use strict';
const api=factory();
if(typeof module!=='undefined'&&module.exports)module.exports=api;
root.WOFAlphaScreenSpaceMap=api;
})(typeof self!=='undefined'?self:globalThis,function(){
'use strict';

const VERSION='wof-alpha-screen-space-map-v1';
const NATIVE_WIDTH=384;
const NATIVE_HEIGHT=224;
const finite=Number.isFinite;
const confidenceValue=value=>finite(value)&&value>=0&&value<=1?value:null;

function fail(reason,extra={}){return{ok:false,reason,...extra};}

function contentRectOf(state){
  if(!state||!finite(state.width)||state.width<=0||!finite(state.height)||state.height<=0)return null;
  const rect=state.contentRect||{x:0,y:0,width:state.width,height:state.height};
  if(![rect.x,rect.y,rect.width,rect.height].every(finite)||rect.width<=0||rect.height<=0)return null;
  if(rect.x<0||rect.y<0||rect.x+rect.width>state.width||rect.y+rect.height>state.height)return null;
  return{x:rect.x,y:rect.y,width:rect.width,height:rect.height};
}

function stateFromViewport({width,height,viewport,sampleAt,confidence=1,epoch=null,projectionEpoch=epoch,mappingVersion=null,fullscreen=false}={}){
  if(!finite(width)||width<=0||!finite(height)||height<=0)return fail('INVALID_DRAWING_BUFFER');
  if(!Array.isArray(viewport)||viewport.length!==4||!viewport.every(finite))return fail('INVALID_WEBGL_VIEWPORT');
  const [vpX,vpY,vpWidth,vpHeight]=viewport;
  if(vpWidth<=0||vpHeight<=0)return fail('INVALID_WEBGL_VIEWPORT');
  const viewportTop=height-(vpY+vpHeight);
  if(!finite(viewportTop)||vpX<0||viewportTop<0||vpX+vpWidth>width||viewportTop+vpHeight>height)return fail('WEBGL_VIEWPORT_OUT_OF_BOUNDS');
  if(confidenceValue(confidence)===null)return fail('INVALID_DRAWING_BUFFER_CONFIDENCE');
  const state={
    width,height,
    contentRect:{x:vpX,y:viewportTop,width:vpWidth,height:vpHeight},
    viewport:{x:vpX,y:vpY,width:vpWidth,height:vpHeight,top:viewportTop,origin:'webgl-bottom-left'},
    sampleAt,confidence,epoch,projectionEpoch,
    mappingVersion:mappingVersion??[width,height,vpX,vpY,vpWidth,vpHeight].join(':'),
    fullscreen:!!fullscreen,
    coordinateSpace:'webgl-drawing-buffer-top-left'
  };
  return{ok:true,reason:null,state};
}

function mappingKeyOf(state,version=''){
  const rect=contentRectOf(state);if(!rect)return null;
  return[state.width,state.height,rect.x,rect.y,rect.width,rect.height,state.mappingVersion??'',state.fullscreen?'fs':'win',version??''].join(':');
}

function mapNativePoint({xNative,yNative,nativeWidth=NATIVE_WIDTH,nativeHeight=NATIVE_HEIGHT,drawingBufferState}={}){
  if(![xNative,yNative,nativeWidth,nativeHeight].every(finite)||nativeWidth<=0||nativeHeight<=0)return fail('INVALID_NATIVE_POINT');
  const rect=contentRectOf(drawingBufferState);if(!rect)return fail('INVALID_DRAWING_BUFFER');
  const xDb=rect.x+xNative/nativeWidth*rect.width;
  const yDb=rect.y+yNative/nativeHeight*rect.height;
  if(![xDb,yDb].every(finite))return fail('DRAWING_BUFFER_PROJECTION_NONFINITE');
  return{ok:true,reason:null,xDb,yDb,rect,scaleX:rect.width/nativeWidth,scaleY:rect.height/nativeHeight};
}

function mapNativeRect({xNative,yNative,widthNative,heightNative,nativeWidth=NATIVE_WIDTH,nativeHeight=NATIVE_HEIGHT,drawingBufferState}={}){
  if(![widthNative,heightNative].every(finite)||widthNative<0||heightNative<0)return fail('INVALID_NATIVE_RECT');
  const point=mapNativePoint({xNative,yNative,nativeWidth,nativeHeight,drawingBufferState});
  if(!point.ok)return point;
  return{ok:true,reason:null,xDb:point.xDb,yDb:point.yDb,widthDb:widthNative*point.scaleX,heightDb:heightNative*point.scaleY,rect:point.rect};
}

return{VERSION,NATIVE_WIDTH,NATIVE_HEIGHT,contentRectOf,stateFromViewport,mappingKeyOf,mapNativePoint,mapNativeRect};
});
