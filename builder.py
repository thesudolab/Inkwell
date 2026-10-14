import os
import sys
import shutil
import subprocess
import threading
import http.server
import socketserver
from webview import create_window, start

# Embedded HTML / JavaScript App Code
HTML_CONTENT = """<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>Inkwell PDF Viewer & Editor</title>
<style>
:root{--bg:#f4f4f2;--surface:#fff;--text:#1d1d1b;--muted:#6b6b66;--line:#d9d9d4;--accent:#2f5bea;--accent-t:#fff;--pagebg:#e6e6e2;
box-sizing:border-box;padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#17171a;--surface:#222226;--text:#ececea;--muted:#9a9a96;--line:#38383d;--accent:#7b9bff;--accent-t:#0b1020;--pagebg:#101012}}
:root[data-theme="dark"]{--bg:#17171a;--surface:#222226;--text:#ececea;--muted:#9a9a96;--line:#38383d;--accent:#7b9bff;--accent-t:#0b1020;--pagebg:#101012}
*{box-sizing:border-box}html,body{height:100%;margin:0}
body{background:var(--bg);color:var(--text);font:14px/1.4 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;display:flex;flex-direction:column}
.bar{display:flex;flex-wrap:wrap;gap:6px;align-items:center;padding:8px 10px;background:var(--surface);border-bottom:1px solid var(--line)}
.bar .sep{width:1px;align-self:stretch;background:var(--line);margin:0 4px}
button,label.btn{font:inherit;color:var(--text);background:var(--bg);border:1px solid var(--line);border-radius:8px;padding:6px 10px;cursor:pointer}
button:hover,label.btn:hover{border-color:var(--accent)}
button.on{background:var(--accent);color:var(--accent-t);border-color:var(--accent)}
button:disabled{opacity:.4;cursor:default}
input[type=color]{width:30px;height:30px;padding:0;border:1px solid var(--line);border-radius:8px;background:none}
input[type=number]{width:54px;font:inherit;padding:5px;border:1px solid var(--line);border-radius:8px;background:var(--bg);color:var(--text)}
#stage{flex:1;overflow:auto;background:var(--pagebg);padding:16px;display:flex;justify-content:center;align-items:flex-start}
#wrap{position:relative;box-shadow:0 2px 14px rgba(0,0,0,.25);background:#fff;display:none}
#wrap canvas{display:block}#ov{position:absolute;left:0;top:0}
#tin{position:absolute;display:none;border:1px dashed var(--accent);background:rgba(255,255,255,.85);color:#000;font-family:Helvetica,Arial,sans-serif;padding:0;margin:0;outline:none;min-width:80px}
#empty{margin:auto;text-align:center;color:var(--muted);padding:40px;border:2px dashed var(--line);border-radius:16px;max-width:420px}
#empty.drag{border-color:var(--accent);color:var(--text)}
#msg{color:var(--muted);margin-left:auto;font-size:13px}

.prop-bar{display:none;background:rgba(47,91,234,0.08);padding:4px 8px;border-radius:6px;gap:6px;align-items:center;font-size:13px}
.prop-bar.active{display:flex}
.prop-bar input[type=number]{width:60px}

.modal{position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,0.5);display:none;justify-content:center;align-items:center;z-index:1000}
.modal-content{background:var(--surface);padding:20px;border-radius:12px;width:400px;max-width:90%;box-shadow:0 4px 20px rgba(0,0,0,0.3)}
.modal-content h3{margin-top:0;margin-bottom:12px}
.modal-tabs{display:flex;gap:5px;margin-bottom:12px}
.modal-tabs button{flex:1}
.sig-panel{display:none}
.sig-panel.active{display:block}
#sig-canvas{border:1px solid var(--line);background:#fff;width:100%;height:150px;touch-action:none;border-radius:6px;cursor:crosshair}
.modal-actions{display:flex;justify-content:flex-end;gap:8px;margin-top:16px}
</style></head><body>
<div class="bar">
  <label class="btn">Open PDF<input id="file" type="file" accept="application/pdf" hidden></label>
  <button id="prev" disabled>◀</button>
  <span><input id="pg" type="number" min="1" value="1"> / <span id="tot">0</span></span>
  <button id="next" disabled>▶</button>
  <button id="zo" disabled>−</button><span id="zv">100%</span><button id="zi" disabled>+</button>
  <span class="sep"></span>
  <button data-tool="view" class="on">View</button>
  <button data-tool="text">Text</button>
  <button data-tool="draw">Draw</button>
  <button data-tool="hl">Highlight</button>
  <button data-tool="white">Cover</button>
  <button data-tool="rm" title="Erase existing content for good">Remove</button>
  <button data-tool="blur" title="Blur existing content for good">Blur</button>
  <label class="btn" title="Insert Image">Image<input id="img-file" type="file" accept="image/*" hidden></label>
  <button id="open-sig" title="Add Signature">Sign</button>
  <span class="sep"></span>
  
  <div id="prop-bar" class="prop-bar">
    <span><b>Selected:</b></span>
    <span>X: <input id="prop-x" type="number" step="1"></span>
    <span>Y: <input id="prop-y" type="number" step="1"></span>
    <span>W: <input id="prop-w" type="number" step="1"></span>
    <span>H: <input id="prop-h" type="number" step="1"></span>
    <button id="prop-del" title="Delete selected element" style="color:#d11a2a;border-color:#d11a2a">Delete</button>
  </div>

  <input id="col" type="color" value="#d11a2a" title="Colour for text and drawing">
  <input id="fill" type="color" value="#ffffff" title="Fill colour for Cover and Remove"><button id="pick" title="Click page to pick colour">Pick</button>
  <span class="sep"></span>
  <button id="undo" disabled>Undo</button>
  <button id="del" disabled>Delete page</button>
  <button id="save" disabled>Save PDF</button>
  <button id="encrypt" disabled title="Save PDF with a password">Lock PDF</button>
  <span id="msg"></span>
</div>
<div id="stage">
  <div id="empty">Drop a PDF here or use <b>Open PDF</b>.<br><small>Files stay in your browser.</small></div>
  <div id="wrap"><canvas id="cv"></canvas><canvas id="ov"></canvas><input id="tin"></div>
</div>

<div id="sig-modal" class="modal">
  <div class="modal-content">
    <h3>Create Signature</h3>
    <div class="modal-tabs">
      <button class="on" data-tab="type">Type</button>
      <button data-tab="draw-tab">Draw</button>
      <button data-tab="upload-tab">Upload</button>
    </div>
    <div id="panel-type" class="sig-panel active">
      <input type="text" id="sig-text-input" placeholder="Type your name" style="width:100%;padding:8px;font-size:16px;border:1px solid var(--line);border-radius:6px;background:var(--bg);color:var(--text);margin-bottom:10px;">
      <select id="sig-font" style="width:100%;padding:8px;border:1px solid var(--line);border-radius:6px;background:var(--bg);color:var(--text)">
        <option value="Cursive">Cursive Style</option>
        <option value="Georgia">Classic Serif</option>
      </select>
    </div>
    <div id="panel-draw-tab" class="sig-panel">
      <canvas id="sig-canvas"></canvas>
      <button id="sig-clear" style="margin-top:8px;width:100%">Clear Canvas</button>
    </div>
    <div id="panel-upload-tab" class="sig-panel">
      <input type="file" id="sig-file-input" accept="image/*" style="width:100%">
    </div>
    <div class="modal-actions">
      <button id="sig-cancel">Cancel</button>
      <button id="sig-insert" class="on">Insert Signature</button>
    </div>
  </div>
</div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/pdf-lib/1.17.1/pdf-lib.min.js"></script>
<script>
pdfjsLib.GlobalWorkerOptions.workerSrc="https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js";
const $=id=>document.getElementById(id);
let doc=null,bytes=null,order=[],cur=0,zoom=1.25,tool="view",ann={},vp=null,task=null,name="document.pdf";
let selectedIndex=null;
const cv=$("cv"),ov=$("ov"),tin=$("tin");
const say=t=>{$("msg").textContent=t;clearTimeout(say.t);say.t=setTimeout(()=>$("msg").textContent="",4000)};
function hexRGB(h){return[parseInt(h.slice(1,3),16)/255,parseInt(h.slice(3,5),16)/255,parseInt(h.slice(5,7),16)/255]}

async function load(buf,fname){
  bytes=new Uint8Array(buf);
  try{
    const t=pdfjsLib.getDocument({data:bytes.slice()});
    t.onPassword=(update,reason)=>{
      const p=prompt(reason===pdfjsLib.PasswordResponses.INCORRECT_PASSWORD?"Wrong password. Try again:":"This PDF is password-protected. Enter the password:");
      if(p===null){t.destroy();return}
      update(p);
    };
    doc=await t.promise;
  }catch(e){say(e&&e.name==="PasswordException"?"Password required to open this PDF":"Could not open that PDF");return}
  name=fname||name;order=[...Array(doc.numPages).keys()];ann={};cur=0;selectedIndex=null;
  $("empty").style.display="none";$("wrap").style.display="block";
  ["prev","next","zo","zi","del","save","encrypt"].forEach(i=>$(i).disabled=false);
  render();
}
async function render(){
  if(!doc)return;
  selectedIndex=null; updatePropBar();
  $("tot").textContent=order.length;$("pg").value=cur+1;$("pg").max=order.length;
  $("zv").textContent=Math.round(zoom*80)+"%";
  $("prev").disabled=cur===0;$("next").disabled=cur>=order.length-1;$("del").disabled=order.length<2;
  const page=await doc.getPage(order[cur]+1);
  vp=page.getViewport({scale:zoom});
  const r=window.devicePixelRatio||1;
  cv.width=ov.width=vp.width*r;cv.height=ov.height=vp.height*r;
  cv.style.width=ov.style.width=vp.width+"px";cv.style.height=ov.style.height=vp.height+"px";
  if(task)try{task.cancel()}catch(e){}
  task=page.render({canvasContext:cv.getContext("2d"),viewport:page.getViewport({scale:zoom*r})});
  try{await task.promise}catch(e){}
  paint();
}
function applyFx(c,src,a,W,H){
  const x=a.x*W,y=a.y*H,w=a.w*W,h=a.h*H;
  if(a.t==="rm"){c.fillStyle=a.f||"#ffffff";c.fillRect(x,y,w,h);return}
  const rad=Math.max(6,Math.min(w,h)*.3);
  c.save();c.beginPath();c.rect(x,y,w,h);c.clip();
  if("filter" in c){c.filter="blur("+rad+"px)";c.drawImage(src,0,0,W,H)}
  else{const s=Math.max(4,rad),t=document.createElement("canvas");t.width=Math.max(1,w/s);t.height=Math.max(1,h/s);
    t.getContext("2d").drawImage(src,x,y,w,h,0,0,t.width,t.height);c.imageSmoothingEnabled=false;c.drawImage(t,0,0,t.width,t.height,x,y,w,h)}
  c.restore();
}
const list=()=>ann[order[cur]]||(ann[order[cur]]=[]);

const loadedImages={};
function getCachedImage(imgObj){
  if(loadedImages[imgObj.src])return loadedImages[imgObj.src];
  const img=new Image();img.src=imgObj.src;
  loadedImages[imgObj.src]=img;
  return img;
}

function paint(extra){
  const c=ov.getContext("2d"),r=window.devicePixelRatio||1,W=vp.width*r,H=vp.height*r;
  c.clearRect(0,0,ov.width,ov.height);
  const items=[...list(),...(extra?[extra]:[])];
  items.forEach((a, idx)=>{
    if(a.t==="hl"||a.t==="white"){c.globalAlpha=a.t==="hl"?.35:1;c.fillStyle=a.t==="hl"?"#ffe600":(a.f||"#ffffff");
      c.fillRect(a.x*W,a.y*H,a.w*W,a.h*H);c.globalAlpha=1}
    else if(a.t==="rm"||a.t==="blur"){applyFx(c,cv,a,ov.width,ov.height)}
    else if(a.t==="draw"){c.strokeStyle=a.c;c.lineWidth=2*zoom*r;c.lineCap=c.lineJoin="round";c.beginPath();
      a.p.forEach(([x,y],i)=>i?c.lineTo(x*W,y*H):c.moveTo(x*W,y*H));c.stroke()}
    else if(a.t==="text"){c.fillStyle=a.c;c.font=`${a.s*zoom*r*1.0}px Helvetica,Arial,sans-serif`;c.textBaseline="top";c.fillText(a.v,a.x*W,a.y*H)}
    else if(a.t==="image"||a.t==="sig"){
      const img=getCachedImage(a);
      if(img.complete)c.drawImage(img,a.x*W,a.y*H,a.w*W,a.h*H);
      else img.onload=()=>paint();
    }
    if(idx===selectedIndex && tool==="view" && a.t!=="draw" && a.t!=="text" && a.t!=="hl"){
      c.save();c.strokeStyle="#2f5bea";c.lineWidth=2*r;
      c.strokeRect(a.x*W, a.y*H, a.w*W, a.h*H);
      c.fillStyle="#2f5bea";c.fillRect((a.x+a.w)*W - 6*r, (a.y+a.h)*H - 6*r, 12*r, 12*r);
      c.restore();
    }
  });
  $("undo").disabled=!list().length;
}

const pos=e=>{const b=ov.getBoundingClientRect();return[(e.clientX-b.left)/b.width,(e.clientY-b.top)/b.height]};
let cd=null,picking=false,draggingItem=null,resizingItem=null,dragOffset={x:0,y:0};

$("pick").onclick=()=>{if(!doc)return;picking=true;$("pick").classList.add("on");ov.style.cursor="crosshair";ov.style.touchAction="auto";say("Click page to pick colour")};

ov.addEventListener("pointerdown",e=>{
  if(picking&&doc){const [px,py]=pos(e),d=cv.getContext("2d").getImageData(Math.floor(px*cv.width),Math.floor(py*cv.height),1,1).data;
    $("fill").value="#"+[d[0],d[1],d[2]].map(v=>v.toString(16).padStart(2,"0")).join("");
    picking=false;$("pick").classList.remove("on");ov.style.cursor=tool==="view"?"default":"crosshair";say("Colour picked");return}
  const [x,y]=pos(e);
  if(tool==="view"&&doc){
    const items=list();
    let foundIdx=-1;
    for(let i=items.length-1; i>=0; i--){
      const a=items[i];
      if(a.t!=="draw" && a.t!=="text" && a.t!=="hl" && x>=a.x && x<=a.x+a.w && y>=a.y && y<=a.y+a.h){foundIdx=i; break;}
    }
    if(foundIdx>=0){
      selectedIndex=foundIdx;updatePropBar();paint();
      const a=items[selectedIndex];ov.setPointerCapture(e.pointerId);
      const isResize = (x >= a.x+a.w-0.03 && x <= a.x+a.w+0.01 && y >= a.y+a.h-0.03 && y <= a.y+a.h+0.01);
      if(isResize){resizingItem=a;}else{draggingItem=a;dragOffset={x:x-a.x, y:y-a.y};}
      return;
    }else{selectedIndex=null;updatePropBar();paint();}
  }
  if(tool==="view"||!doc)return;
  if(tool==="text"){openText(e,x,y);return}
  ov.setPointerCapture(e.pointerId);
  cd=tool==="draw"?{t:"draw",c:$("col").value,p:[[x,y]]}:{t:tool,x,y,w:0,h:0,x0:x,y0:y,f:$("fill").value};
});

ov.addEventListener("pointermove",e=>{
  const [x,y]=pos(e);
  if(draggingItem){draggingItem.x=Math.max(0, Math.min(1-draggingItem.w, x-dragOffset.x));draggingItem.y=Math.max(0, Math.min(1-draggingItem.h, y-dragOffset.y));updatePropBar();paint();return;}
  if(resizingItem){resizingItem.w=Math.max(0.02, x-resizingItem.x);resizingItem.h=Math.max(0.02, y-resizingItem.y);updatePropBar();paint();return;}
  if(!cd)return;
  if(cd.t==="draw")cd.p.push([x,y]);
  else{cd.x=Math.min(x,cd.x0);cd.y=Math.min(y,cd.y0);cd.w=Math.abs(x-cd.x0);cd.h=Math.abs(y-cd.y0)}
  paint(cd);
});

const end=()=>{
  if(draggingItem||resizingItem){draggingItem=null;resizingItem=null;paint();return;}
  if(!cd)return;const ok=cd.t==="draw"?cd.p.length>1:cd.w>.003&&cd.h>.003;
  if(ok){list().push(cd);if(cd.t==="blur"||cd.t==="white"||cd.t==="rm"){selectedIndex=list().length-1;updatePropBar();}}
  cd=null;paint();
};
ov.addEventListener("pointerup",end);ov.addEventListener("pointercancel",end);

function updatePropBar(){
  const bar=$("prop-bar");
  if(selectedIndex!==null && list()[selectedIndex]){
    bar.classList.add("active");
    const a=list()[selectedIndex];
    $("prop-x").value=Math.round(a.x*1000);$("prop-y").value=Math.round(a.y*1000);
    $("prop-w").value=Math.round(a.w*1000);$("prop-h").value=Math.round(a.h*1000);
  }else{bar.classList.remove("active");}
}

["prop-x","prop-y","prop-w","prop-h"].forEach(id=>{
  $(id).oninput=()=>{
    if(selectedIndex===null||!list()[selectedIndex])return;
    const a=list()[selectedIndex];
    a.x=+$("prop-x").value/1000;a.y=+$("prop-y").value/1000;
    a.w=Math.max(0.02, +$("prop-w").value/1000);a.h=Math.max(0.02, +$("prop-h").value/1000);
    paint();
  };
});
$("prop-del").onclick=()=>{if(selectedIndex!==null){list().splice(selectedIndex,1);selectedIndex=null;updatePropBar();paint();}};

function openText(e,x,y){
  commitText();const w=$("wrap").getBoundingClientRect();
  tin.style.display="block";tin.style.left=(e.clientX-w.left)+"px";tin.style.top=(e.clientY-w.top)+"px";
  tin.style.fontSize=(14*zoom)+"px";tin.style.color=$("col").value;tin.value="";
  tin._p=[x,y];setTimeout(()=>tin.focus(),0);
}
function commitText(){
  if(tin.style.display!=="block")return;
  const v=tin.value.trim();tin.style.display="none";
  if(v){list().push({t:"text",x:tin._p[0],y:tin._p[1],v,s:14,c:$("col").value});paint()}
}
tin.addEventListener("keydown",e=>{if(e.key==="Enter"){e.preventDefault();commitText()}if(e.key==="Escape"){tin.value="";commitText()}});
tin.addEventListener("blur",commitText);

document.querySelectorAll("[data-tool]").forEach(b=>b.onclick=()=>{
  commitText();tool=b.dataset.tool;selectedIndex=null;updatePropBar();
  document.querySelectorAll("[data-tool]").forEach(x=>x.classList.toggle("on",x===b));
  ov.style.cursor=tool==="view"?"default":tool==="text"?"text":"crosshair";
  ov.style.touchAction=tool==="view"||tool==="text"?"auto":"none";
  paint();
});

$("img-file").onchange=async e=>{
  const f=e.target.files[0];if(!f||!doc)return;
  const reader=new FileReader();
  reader.onload=evt=>{
    const src=evt.target.result;const img=new Image();
    img.onload=()=>{
      const aspect=img.height/img.width;const w=0.25;const h=w*aspect*(vp.width/vp.height);
      list().push({t:"image",src,x:0.1,y:0.1,w,h});
      selectedIndex=list().length-1;updatePropBar();paint();say("Image added");
    };
    img.src=src;
  };
  reader.readAsDataURL(f);e.target.value="";
};

const sigModal=$("sig-modal");
let activeSigTab="type";
document.querySelectorAll(".modal-tabs button").forEach(b=>{
  b.onclick=()=>{
    document.querySelectorAll(".modal-tabs button").forEach(x=>x.classList.remove("on"));
    document.querySelectorAll(".sig-panel").forEach(x=>x.classList.remove("active"));
    b.classList.add("on");activeSigTab=b.dataset.tab;document.getElementById(`panel-${activeSigTab}`).classList.add("active");
  }
});
$("open-sig").onclick=()=>{if(!doc)return;sigModal.style.display="flex";};
$("sig-cancel").onclick=()=>{sigModal.style.display="none";};

const sigCanvas=$("sig-canvas");const sigCtx=sigCanvas.getContext("2d");let sigDrawing=false;
sigCanvas.width=360;sigCanvas.height=150;
sigCanvas.onpointerdown=e=>{sigDrawing=true;sigCtx.beginPath();sigCtx.moveTo(e.offsetX,e.offsetY)};
sigCanvas.onpointermove=e=>{if(!sigDrawing)return;sigCtx.lineTo(e.offsetX,e.offsetY);sigCtx.stroke()};
sigCanvas.onpointerup=()=>sigDrawing=false;
$("sig-clear").onclick=()=>sigCtx.clearRect(0,0,sigCanvas.width,sigCanvas.height);

$("sig-insert").onclick=()=>{
  let src="";
  if(activeSigTab==="type"){
    const text=$("sig-text-input").value.trim();if(!text){say("Enter signature text");return;}
    const c=document.createElement("canvas");c.width=400;c.height=120;const ctx=c.getContext("2d");
    ctx.font=$("sig-font").value==="Cursive"?"48px 'Brush Script MT', cursive, sans-serif":"40px Georgia, serif";
    ctx.fillStyle="#0b2545";ctx.textBaseline="middle";ctx.fillText(text,20,60);src=c.toDataURL();
  }else if(activeSigTab==="draw-tab"){src=sigCanvas.toDataURL();}
  else if(activeSigTab==="upload-tab"){
    const f=$("sig-file-input").files[0];if(!f){say("Select an image file");return;}
    const reader=new FileReader();reader.onload=evt=>addSigToPage(evt.target.result);reader.readAsDataURL(f);
    sigModal.style.display="none";return;
  }
  if(src)addSigToPage(src);sigModal.style.display="none";
};

fn addSigToPage(src){
  const img=new Image();
  img.onload=()=>{
    const aspect=img.height/img.width;const w=0.3;const h=w*aspect*(vp.width/vp.height);
    list().push({t:"sig",src,x:0.15,y:0.15,w,h});selectedIndex=list().length-1;updatePropBar();paint();say("Signature added");
  };
  img.src=src;
}

$("undo").onclick=()=>{list().pop();selectedIndex=null;updatePropBar();paint()};
document.addEventListener("keydown",e=>{if((e.ctrlKey||e.metaKey)&&e.key==="z"&&e.target!==tin){list().pop();selectedIndex=null;updatePropBar();paint()}});
$("prev").onclick=()=>{commitText();cur--;render()};
$("next").onclick=()=>{commitText();cur++;render()};
$("pg").onchange=()=>{cur=Math.min(order.length,Math.max(1,+$("pg").value||1))-1;render()};
$("zi").onclick=()=>{zoom=Math.min(4,zoom+.25);render()};
$("zo").onclick=()=>{zoom=Math.max(.5,zoom-.25);render()};
$("del").onclick=()=>{if(order.length<2)return;if(!confirm("Delete page?"))return;order.splice(cur,1);cur=Math.min(cur,order.length-1);render()};
$("file").onchange=async e=>{const f=e.target.files[0];if(f)load(await f.arrayBuffer(),f.name)};
const em=$("empty");
["dragover","dragenter"].forEach(t=>document.addEventListener(t,e=>{e.preventDefault();em.classList.add("drag")}));
["dragleave","drop"].forEach(t=>document.addEventListener(t,e=>{e.preventDefault();em.classList.remove("drag")}));
document.addEventListener("drop",async e=>{const f=e.dataTransfer.files[0];if(f&&/pdf/i.test(f.type+f.name))load(await f.arrayBuffer(),f.name)});

async function generatePdfBytes(){
  commitText();
  const {PDFDocument,StandardFonts,rgb}=PDFLib;
  let orig=null;try{orig=await PDFDocument.load(bytes)}catch(e){}
  const src=await PDFDocument.create();
  for(const i of order){
    const fx=(ann[i]||[]).filter(a=>a.t==="rm"||a.t==="blur"||a.t==="white");
    if(orig&&!fx.length&&!(ann[i]||[]).some(a=>a.t==="image"||a.t==="sig"||a.t==="text"||a.t==="draw"||a.t==="hl")){
      const [cp]=await src.copyPages(orig,[i]);src.addPage(cp);continue;
    }
    const p=await doc.getPage(i+1),v=p.getViewport({scale:2}),c=document.createElement("canvas");
    c.width=v.width;c.height=v.height;const x=c.getContext("2d");
    await p.render({canvasContext:x,viewport:v}).promise;
    for(const a of fx){
      if(a.t==="rm"||a.t==="white"||a.t==="blur"){
        const t=document.createElement("canvas");t.width=c.width;t.height=c.height;t.getContext("2d").drawImage(c,0,0);
        applyFx(x,t,a,c.width,c.height);
      }
    }
    const blob=await new Promise(r=>c.toBlob(r,"image/jpeg",.92));
    const img=await src.embedJpg(await blob.arrayBuffer());
    const base=p.getViewport({scale:1});
    const pg=src.addPage([base.width,base.height]);
    pg.drawImage(img,{x:0,y:0,width:base.width,height:base.height});
  }
  const font=await src.embedFont(StandardFonts.Helvetica);
  const pages=src.getPages();
  for(let k=0; k<order.length; k++){
    const i=order[k];const pg=pages[k],{width:W,height:H}=pg.getSize();
    for(const a of (ann[i]||[])){
      if(a.t==="hl")pg.drawRectangle({x:a.x*W,y:H-(a.y+a.h)*H,width:a.w*W,height:a.h*H,color:rgb(1,.9,0),opacity:.35});
      else if(a.t==="draw"){const [r,g,b]=hexRGB(a.c);for(let idx=1;idx<a.p.length;idx++)
        pg.drawLine({start:{x:a.p[idx-1][0]*W,y:H-a.p[idx-1][1]*H},end:{x:a.p[idx][0]*W,y:H-a.p[idx][1]*H},thickness:2,color:rgb(r,g,b)})}
      else if(a.t==="text"){const [r,g,b]=hexRGB(a.c);pg.drawText(a.v,{x:a.x*W,y:H-a.y*H-a.s*.85,size:a.s,font,color:rgb(r,g,b)})}
      else if(a.t==="image"||a.t==="sig"){
        const subBytes=await fetch(a.src).then(res=>res.arrayBuffer());
        let embeddedImage = a.src.includes("image/png") || a.src.startsWith("data:image/png") ? await src.embedPng(subBytes) : await src.embedJpg(subBytes);
        pg.drawImage(embeddedImage,{x:a.x*W,y:H-(a.y+a.h)*H,width:a.w*W,height:a.h*H});
      }
    }
  }
  return await src.save();
}

$("save").onclick=async()=>{
  try{
    say("Building PDF…");
    const data=await generatePdfBytes();
    const blob=new Blob([data], {type: "application/pdf"});
    const url=URL.createObjectURL(blob);
    const a=document.createElement("a");
    a.href=url;
    a.download=name.replace(/\\.pdf$/i,"")+"-edited.pdf";
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    say("Saved successfully");
  }catch(e){say(e&&e.message&&e.message.includes("cancelled")?"Save cancelled":"Save failed: "+(e.message||e))}
};

$("encrypt").onclick=async()=>{
  const pwd=prompt("Enter a password to encrypt/lock this PDF:");
  if(!pwd)return;
  try{
    say("Encrypting PDF…");
    const data=await generatePdfBytes();
    // Load into a fresh pdf-lib document and encrypt with the password
    const pdfDoc = await PDFLib.PDFDocument.load(data);
    pdfDoc.encrypt({
      userPassword: pwd,
      ownerPassword: pwd,
      permissions: { printing: 'high', modifying: false, copying: false }
    });
    const encryptedBytes = await pdfDoc.save();

    const blob=new Blob([encryptedBytes], {type: "application/pdf"});
    const url=URL.createObjectURL(blob);
    const a=document.createElement("a");
    a.href=url;
    a.download=name.replace(/\\.pdf$/i,"")+"-locked.pdf";
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    say("PDF encrypted and saved successfully!");
  }catch(e){say("Encryption failed: "+(e.message||e))}
};
</script></body></html>
"""

class SimpleHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

def start_server(directory, port):
    os.chdir(directory)
    handler = SimpleHTTPRequestHandler
    httpd = socketserver.TCPServer(("127.0.0.1", port), handler)
    httpd.serve_forever()

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def main():
    target_dir = resource_path(".")
    html_file = os.path.join(target_dir, "index.html")
    
    with open(html_file, "w", encoding="utf-8") as f:
        f.write(HTML_CONTENT)

    port = 8765
    server_thread = threading.Thread(target=start_server, args=(target_dir, port), daemon=True)
    server_thread.start()

    if len(sys.argv) > 1 and sys.argv[1] == "--build":
        print("[*] Building standalone binary inside 'inkwell' folder...")
        script_path = os.path.abspath(__file__)
        html_path = os.path.abspath(html_file)
        
        spec_content = f"""
# -*- mode: python ; coding: utf-8 -*-
block_cipher = None
a = Analysis(
    [r'{script_path}'],
    pathex=[],
    binaries=[],
    datas=[(r'{html_path}', '.')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure)
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='Inkwell',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    icon=None,
)
"""
        with open("inkwell.spec", "w", encoding="utf-8") as spec_file:
            spec_file.write(spec_content)
        
        subprocess.run(["pyinstaller", "--clean", "inkwell.spec"])

        script_dir = os.path.dirname(os.path.abspath(__file__))
        inkwell_output_dir = os.path.join(script_dir, "inkwell")
        dist_dir = os.path.join(script_dir, "dist")

        if os.path.exists(inkwell_output_dir):
            shutil.rmtree(inkwell_output_dir)
        os.makedirs(inkwell_output_dir, exist_ok=True)

        if os.path.exists(dist_dir):
            for item in os.listdir(dist_dir):
                s = os.path.join(dist_dir, item)
                d = os.path.join(inkwell_output_dir, item)
                if os.path.isdir(s):
                    shutil.copytree(s, d, dirs_exist_ok=True)
                else:
                    shutil.copy2(s, d)

        print(f"\n[✔] Build complete! Your standalone 'Inkwell' binary is located in: {inkwell_output_dir}")
    else:
        create_window(
            title="Inkwell PDF Viewer & Editor",
            url=f"http://127.0.0.1:{port}/index.html",
            width=1280,
            height=800,
            resizable=True,
            min_size=(800, 600)
        )
        start()

if __name__ == "__main__":
    main()