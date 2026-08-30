(()=>{
  'use strict';
  try{window.WOFCANVAS?.stop?.();}catch(_){}

  const target=window.I_n3jTY;
  const ctx=window.I_KkacD;
  const pad=window.I_QKG4Q?.Pad;
  const src=window.I_Aj3M8;
  if(typeof target!=='function')throw new Error('I_n3jTY render function not found');
  if(!ctx||typeof ctx.fillText!=='function')throw new Error('I_KkacD canvas context not found');
  if(!pad||!src)throw new Error('game pad/source canvas not found');

  const original=target;
  let running=true;
  function draw(){
    if(!running)return;
    const x=(+pad.X||0)+12;
    const y=(+pad.Y||0)+24;
    ctx.save();
    ctx.globalAlpha=1;
    ctx.fillStyle='rgba(0,0,0,.72)';
    ctx.fillRect(x-6,y-17,92,23);
    ctx.strokeStyle='rgba(255,255,255,.95)';
    ctx.lineWidth=2;
    ctx.strokeRect(x-6,y-17,92,23);
    ctx.fillStyle='#fff';
    ctx.font='bold 14px sans-serif';
    ctx.textBaseline='alphabetic';
    ctx.fillText('WOF HUD OK',x,y);
    ctx.restore();
  }

  const wrapped=function(){
    const r=original.apply(this,arguments);
    try{draw();}catch(_){}
    return r;
  };
  window.I_n3jTY=wrapped;

  window.WOFCANVAS={
    version:'canvas-probe-v1',
    status(){return {running,renderWrapped:window.I_n3jTY===wrapped,pad:{x:pad.X,y:pad.Y},source:{w:src.width,h:src.height}};},
    draw,
    stop(){running=false;if(window.I_n3jTY===wrapped)window.I_n3jTY=original;delete window.WOFCANVAS;console.log('⛔ WOF canvas probe stopped');}
  };
  console.log('✅ WOF canvas probe v1 installed',window.WOFCANVAS.status());
})();
