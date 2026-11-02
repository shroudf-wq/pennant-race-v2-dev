# v2.0.b のソースに当てると v2.0.c(2.5D の札の重なりを直す。引き継ぎ書 4.1 の「既知の粗さ」)。python3 patch_v20c.py src.html new.html
# 触るのは 2.5D の描画だけ(v2.0.b で足した hl3 の層)。試合の計算・記録・セーブ・2D の図には触らない。
#   ① 長い名前:助っ人の「名・姓」は姓だけを札に出す。6文字以上は字を少し小さく
#   ② 札の重なり:カメラが落ち着いたあと、画面の上の札の位置を測り、重なる札を上か横の空いた所へずらす(走者が止まったあとにもう一度)
import sys
s=open(sys.argv[1],encoding="utf-8").read()
def rep(a,b):
    global s
    k=s.count(a)
    if k!=1: raise SystemExit(f"count {k}: {a[:80]}")
    s=s.replace(a,b)
rep('const APP_VERSION="v2.0.b"; const BASE_V1="v1.1.y";','const APP_VERSION="v2.0.c"; const BASE_V1="v1.1.y";')

# ===== CSS:札をずらせるように(--ox/--oy。札は正面を向いているので、画面の上下左右と同じ向き) =====
rep(".hl3tag{position:absolute;left:0;bottom:12px;transform:translateX(-50%);",
    ".hl3tag{position:absolute;left:0;bottom:12px;transform:translateX(-50%) translate(var(--ox,0px),var(--oy,0px));transition:transform .18s ease-out;")
rep(".hl3txt{position:absolute;left:0;bottom:0;transform:translateX(-50%);",
    ".hl3txt{position:absolute;left:0;bottom:0;transform:translateX(-50%) translate(var(--ox,0px),var(--oy,0px));transition:transform .18s ease-out;")
rep(".hl3tag.run{background:#f2c94c;color:#1c1606;border-color:#6b5310;bottom:14px}",
    ".hl3tag.run{background:#f2c94c;color:#1c1606;border-color:#6b5310;bottom:14px}\n.hl3tag.lg{font-size:7.5px;letter-spacing:-.03em;padding:1px 3px}")

# ===== ① 長い名前 =====
rep("""function hl3Bb(x,y,z,c,inner,cls){""","""// v2.0.c:札に出す名前。助っ人の「名・姓」は姓だけ(ミゲル・メンドーサ → メンドーサ)。6文字以上は .lg で字を小さく
function hl3Sur(n){ const t=surnameOf(n), i=t.lastIndexOf("・"); return i>=0? t.slice(i+1) : t; }
function hl3TagHtml(cls,n){ const t=hl3Sur(n); return `<div class="hl3tag${cls||""}${[...t].length>=6? " lg" : ""}">${t}</div>`; }
function hl3Bb(x,y,z,c,inner,cls){""")
rep("""out+=hl3Bb(x,y,0,c,`<div class="hl3cap f"></div><div class="hl3tag">${sur(nm)}</div>`); });""",
    """out+=hl3Bb(x,y,0,c,`<div class="hl3cap f"></div>${hl3TagHtml("",nm)}`,"hl3f"); });""")
rep("""out+=hl3Bb(HL_HX+22,HL_HY+8,0,c,`<div class="hl3cap f"></div><div class="hl3tag">${sur(m["捕"])}</div>`);""",
    """out+=hl3Bb(HL_HX+22,HL_HY+8,0,c,`<div class="hl3cap f"></div>${hl3TagHtml("",m["捕"])}`,"hl3f");""")
rep("""`<div class="hl3cap b"></div><div class="hl3tag bat">${sur(ev.batter)}</div>`,"hl3bat");""",
    """`<div class="hl3cap b"></div>${hl3TagHtml(" bat",ev.batter)}`,"hl3bat");""")
rep("""out+=hl3Bb(x,y-6,0,c,`<div class="hl3cap"></div><div class="hl3tag run">${sur(runners[i])}</div>`); });""",
    """out+=hl3Bb(x,y-6,0,c,`<div class="hl3cap"></div>${hl3TagHtml(" run",runners[i])}`,"hl3run"); });""")
rep("""    const inner= a===0? `<div class="hl3cap b"></div>${nm? `<div class="hl3tag bat">${sur(nm)}</div>` : ""}` : `<div class="hl3cap"></div>${nm? `<div class="hl3tag run">${sur(nm)}</div>` : ""}`;""",
    """    const inner= a===0? `<div class="hl3cap b"></div>${nm? hl3TagHtml(" bat",nm) : ""}` : `<div class="hl3cap"></div>${nm? hl3TagHtml(" run",nm) : ""}`;""")

# ===== ② 札の重なりをほどく =====
rep("""let hl3RO=null;""","""/* v2.0.c:札の重なりをほどく。画面の上の札の四角を測り、優先の高い順に置いていく。重なる札は、近い順に「上・横・斜め上」の空いた所へずらす。
   優先:得点(+N)→ 打者 → 走者 → 捕手・投手・野手(手前ほど先)。打者の名前のカードの下に隠れた札は、2回目に空いた所があれば移す。三振の K・四球などの大きな文字は札をよけさせない(重なっても読める)。
   withMovers=走り終えた走者も入れる。ずらす量は札の正面の向きの px(--ox/--oy)。測る間は transition を止める */
function hl3Declutter(st,withMovers){
  if(!st || !st.isConnected) return;
  const box=st.getBoundingClientRect(); if(!box.width || !box.height) return;
  const top=box.top+2, left=box.left+1, right=box.right-1, bottom=box.bottom-1;
  const items=[];
  st.querySelectorAll(".hl3bb").forEach(b=>{
    const mv=b.classList.contains("hl3mv"); if(mv && !withMovers) return;
    if(mv && parseFloat(getComputedStyle(b).opacity)<.1) return;   // 本塁に還った走者
    const t=b.querySelector(".hl3tag,.hl3txt.runs"); if(!t) return;
    t.style.transition="none"; items.push({b,t,mv});
  });
  if(!items.length) return;
  items.forEach(o=>{ const r=o.t.getBoundingClientRect(), k= o.t.offsetWidth? r.width/o.t.offsetWidth : 1;
    const ox=parseFloat(o.t.style.getPropertyValue("--ox"))||0, oy=parseFloat(o.t.style.getPropertyValue("--oy"))||0;
    o.k=k||1; o.r={x:r.left-ox*o.k, y:r.top-oy*o.k, w:r.width, h:r.height};   // ずらす前の場所
    o.p= o.t.classList.contains("hl3txt")? 0 : o.b.classList.contains("hl3bat")? 1 : (o.b.classList.contains("hl3run")||o.mv)? 2 : 3; });
  items.sort((a,b)=> a.p-b.p || (b.r.y+b.r.h)-(a.r.y+a.r.h));   // 同じ優先なら手前(画面の下)から
  const placed=[], gap=1;
  const hit=(a,b)=> Math.max(0,Math.min(a.x+a.w,b.x+b.w)-Math.max(a.x,b.x)+gap) * Math.max(0,Math.min(a.y+a.h,b.y+b.h)-Math.max(a.y,b.y)+gap);
  const out=a=> Math.max(0,left-a.x)+Math.max(0,a.x+a.w-right)+Math.max(0,top-a.y)+Math.max(0,a.y+a.h-bottom);
  const candsOf=o=>{ const {w,h}=o.r, cs=[];
    for(const dy of [0,-(h+gap),-2*(h+gap),(h+gap),2*(h+gap)]) for(const dx of [0,-(w*.55+gap),(w*.55+gap),-(w+gap),(w+gap),-(w*1.6+gap),(w*1.6+gap)]) cs.push([dx,dy,Math.abs(dx)*.7+Math.abs(dy)+(dy>0? h : 0)]);
    return cs.sort((a,b)=>a[2]-b[2]); };
  // 1回目:札どうしの重なりをほどく
  items.forEach(o=>{
    const {w,h}=o.r; let best=null;
    for(const [dx,dy,cost] of candsOf(o)){
      const a={x:o.r.x+dx, y:o.r.y+dy, w, h}, ov=placed.reduce((s,p)=>s+hit(a,p),0)+out(a)*h*4;
      if(!best || ov<best.ov-.5 || (Math.abs(ov-best.ov)<=.5 && cost<best.cost)) best={dx,dy,ov,cost,a};
      if(ov<=.5) break;   // 近い順に見ているので、最初に空いていた所に決める
    }
    placed.push(best.a); o.a=best.a; o.dx=best.dx; o.dy=best.dy;
  });
  // 2回目:打者・投手の名前のカード(プレー前)の下に隠れた札を、札にもカードにも重ならない所が近くにあれば、そこへ移す(なければそのまま。札どうしは重ねない)
  const cut=st.querySelector(".hlCutin:not(.out)");
  if(cut){ const cr={x:box.left+cut.offsetLeft, y:box.top+cut.offsetTop, w:cut.offsetWidth, h:cut.offsetHeight};
    items.forEach(o=>{ if(hit(o.a,cr)<=.5) return; const {w,h}=o.r;
      for(const [dx,dy] of candsOf(o)){ const a={x:o.r.x+dx, y:o.r.y+dy, w, h};
        if(hit(a,cr)>.5 || out(a)>0 || items.some(q=>q!==o && hit(a,q.a)>.5)) continue;
        o.a=a; o.dx=dx; o.dy=dy; break; } }); }
  items.forEach(o=>{ o.t.style.setProperty("--ox",(o.dx/o.k).toFixed(1)+"px"); o.t.style.setProperty("--oy",(o.dy/o.k).toFixed(1)+"px"); });
  void st.offsetWidth; items.forEach(o=>{ o.t.style.transition=""; });
}
let hl3RO=null;""")
# カメラが落ち着いたら 1回目、走者が止まったら 2回目
rep("""  if(to!==from){ requestAnimationFrame(()=>{ if(!st.isConnected) return; st.classList.add("sw"); st.style.cssText+=";"+hl3Vars(c); st.dataset.cam=to; place(); setTimeout(()=>st.classList.remove("sw"),500); }); }
  hl3Cam=to;""","""  if(to!==from){ requestAnimationFrame(()=>{ if(!st.isConnected) return; st.classList.add("sw"); st.style.cssText+=";"+hl3Vars(c); st.dataset.cam=to; place(); setTimeout(()=>st.classList.remove("sw"),500); }); }
  hl3Cam=to;
  setTimeout(()=>hl3Declutter(st,false), (to!==from)? 520 : 40);   // v2.0.c:カメラが落ち着いてから札の重なりをほどく""")
rep("""    try{ el.animate(kf,{duration:n*per,delay:stt,fill:"forwards"}); if(b===4) el.animate([{opacity:1},{opacity:0}],{duration:250,delay:stt+n*per,fill:"forwards"}); }catch(e){}
  });
}""","""    try{ el.animate(kf,{duration:n*per,delay:stt,fill:"forwards"}); if(b===4) el.animate([{opacity:1},{opacity:0}],{duration:250,delay:stt+n*per,fill:"forwards"}); }catch(e){}
    mvEnd=Math.max(mvEnd,stt+n*per+(b===4? 260 : 0));
  });
  if(mvEnd>0) setTimeout(()=>hl3Declutter(st,true), Math.max(mvEnd+40,560));   // v2.0.c:走り終えた走者の札も入れて、もう一度
}""")
rep("""  // 走者(塁の線を滑る。時間は hlMovingRunners と同じ)
  const bp=HL_BP();""","""  // 走者(塁の線を滑る。時間は hlMovingRunners と同じ)
  const bp=HL_BP(); let mvEnd=0;""")
open(sys.argv[2],"w",encoding="utf-8").write(s)
print("ok")
