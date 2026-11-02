# v2.1.k のソースに当てると v2.1.l。python3 patch_v21l.py src.html new.html
# 試合画面の背景の球場(v2.1.j)の続き。見た目だけ(試合の計算・記録・セーブには触らない。乱数は使わない)。
#   ① 昼の空:明るい配色(html の color-scheme が light)と、スタイル「デーゲームの球場」「夏の大会」は昼(青空・雲・強い日差し・照明は消す・星なし)。
#      夜のスタイル(ナイター・月)はいつも夜。v1 の試合に昼・夜の記録はないので、見た目の設定で決める
#   ② スコアボードを外野の電光掲示板に:スコアボード(v1 の .matchup。CSS は変えない)の後ろに飾りの箱 .hl3sb を置く
#      (取り付け枠・上の両端の照明・下の2本の支柱)。位置はボードに合わせて動かす(hl3dBgAim と同じ時に)
import sys
s=open(sys.argv[1],encoding="utf-8").read()
def rep(a,b):
    global s
    k=s.count(a)
    if k!=1: raise SystemExit(f"count {k}: {a[:80]}")
    s=s.replace(a,b)
rep('const APP_VERSION="v2.1.k"; const BASE_V1="v1.4.b";','const APP_VERSION="v2.1.l"; const BASE_V1="v1.4.b";')

# ===== CSS:電光掲示板の飾り =====
rep(""".hl3bgOn .matchup{box-shadow:0 10px 26px rgba(0,0,0,.45);margin-bottom:var(--hl3bgGap,72px)}""",
""".hl3bgOn .matchup{box-shadow:0 10px 26px rgba(0,0,0,.45);margin-bottom:var(--hl3bgGap,72px)}
/* v2.1.l:スコアボードを外野の電光掲示板に見立てる飾り(ボードの後ろ。ボードの CSS は v1 のまま) */
.hl3sb{position:absolute;left:0;top:0;width:100%;height:100%;z-index:-1;pointer-events:none}
.hl3sb>i{position:absolute;display:block}
.hl3sb .sbFrame{border-radius:8px;background:linear-gradient(#2b3036,#16191d);box-shadow:0 0 0 1px rgba(255,255,255,.08) inset,0 14px 30px rgba(0,0,0,.55)}
.hl3sb .sbPost{width:14px;background:linear-gradient(90deg,#1a1e22,#3a4148 45%,#1a1e22);-webkit-mask-image:linear-gradient(#000 55%,transparent);mask-image:linear-gradient(#000 55%,transparent)}
.hl3sb .sbLamp{width:44px;height:26px;border-radius:5px;background:#20252b;box-shadow:0 0 0 1px rgba(0,0,0,.4)}
.hl3sb .sbLamp::before{content:"";position:absolute;inset:4px 5px;background:radial-gradient(circle,#fffbe8 0 3.2px,transparent 3.8px) 0 0/11.5px 9px;filter:drop-shadow(0 0 4px rgba(255,240,190,.95))}
.hl3sb.day .sbLamp::before{background:radial-gradient(circle,#d9dde2 0 3.2px,transparent 3.8px) 0 0/11.5px 9px;filter:none}""")

# ===== 昼・夜 =====
rep("""function hl3dBgWant(){""","""// v2.1.l:昼の空にするか(明るい配色・デーゲームの球場・夏の大会。夜のスタイルはいつも夜)
const HL3D_BG_DAY=["ballpark","natsu"], HL3D_BG_NIGHT=["night","tsuki"];
function hl3dBgIsDay(){ const st=document.documentElement.dataset.style||""; if(HL3D_BG_NIGHT.includes(st)) return false; if(HL3D_BG_DAY.includes(st)) return true;
  try{ const cs=(document.documentElement.style.colorScheme||getComputedStyle(document.documentElement).colorScheme||"").trim(); return cs==="light"; }catch(e){ return false; } }
function hl3dBgWant(){""")
rep("""  const key=[home, pk? pk.s+"/"+pk.turf+"/"+pk.dome : "-", document.documentElement.dataset.style||"", (typeof teamColorMap!=="undefined" && teamColorMap[home])||""].join("|");""",
"""  const day=hl3dBgIsDay(), key=[home, pk? pk.s+"/"+pk.turf+"/"+pk.dome : "-", document.documentElement.dataset.style||"", (typeof teamColorMap!=="undefined" && teamColorMap[home])||"", day? "day" : "night"].join("|");""")
rep("""    try{ hl3dNR(()=>hl3dBgBuild(box,home,pk,key)); }catch(e){ hl3dBgOff=true; hl3dBgOffNow(card); } }, hl3dBgS? 120 : 0);""",
"""    try{ hl3dNR(()=>hl3dBgBuild(box,home,pk,key,day)); }catch(e){ hl3dBgOff=true; hl3dBgOffNow(card); } }, hl3dBgS? 120 : 0);""")
rep("""function hl3dBgSkyTex(dome){ const cv=document.createElement("canvas"); cv.width=4; cv.height=128; const g=cv.getContext("2d"), gr=g.createLinearGradient(0,0,0,128);
  if(dome){ gr.addColorStop(0,"#1c2026"); gr.addColorStop(1,"#3a424c"); } else { gr.addColorStop(0,"#070c18"); gr.addColorStop(.6,"#121c33"); gr.addColorStop(1,"#26365a"); }
  g.fillStyle=gr; g.fillRect(0,0,4,128); return new THREE.CanvasTexture(cv); }""",
"""function hl3dBgSkyTex(dome,day){ const cv=document.createElement("canvas"); cv.width=256; cv.height=128; const g=cv.getContext("2d"), gr=g.createLinearGradient(0,0,0,128);
  if(dome){ gr.addColorStop(0,day? "#5b636d" : "#1c2026"); gr.addColorStop(1,day? "#8b949e" : "#3a424c"); }
  else if(day){ gr.addColorStop(0,"#3f86d0"); gr.addColorStop(.62,"#8cc2ec"); gr.addColorStop(1,"#d9ecf8"); }
  else { gr.addColorStop(0,"#070c18"); gr.addColorStop(.6,"#121c33"); gr.addColorStop(1,"#26365a"); }
  g.fillStyle=gr; g.fillRect(0,0,256,128);
  if(day && !dome){ let x=97531; const rnd=()=>{ x=(Math.imul(x,1103515245)+12345)&0x7fffffff; return x/0x7fffffff; };   // 雲(決まった数列。試合の乱数は使わない)
    for(let k=0;k<7;k++){ const cx=rnd()*256, cy=18+rnd()*52, w=26+rnd()*40; g.fillStyle="rgba(255,255,255,.55)";
      for(let j=0;j<6;j++){ g.beginPath(); g.ellipse(cx+(rnd()-.5)*w, cy+(rnd()-.5)*6, w*(.22+rnd()*.18), 4+rnd()*4, 0, 0, Math.PI*2); g.fill(); } } }
  return new THREE.CanvasTexture(cv); }""")
rep("""function hl3dBgBuild(box,home,pk,key){
  const T=THREE, R=hl3dBgRenderer(); if(hl3dBgS){ hl3dBgStop(); hl3dBgS.own.forEach(o=>{ try{ o.dispose(); }catch(e){} }); }
  const own=[], sc=new T.Scene(), dome=!!(pk&&pk.dome), sky=hl3dBgSkyTex(dome); own.push(sky); sc.background=sky;
  sc.add(new T.AmbientLight(0xffffff,.72)); const dl=new T.DirectionalLight(0xfff4dc,.55); dl.position.set(40,160,120); sc.add(dl);""",
"""function hl3dBgBuild(box,home,pk,key,day){
  const T=THREE, R=hl3dBgRenderer(); if(hl3dBgS){ hl3dBgStop(); hl3dBgS.own.forEach(o=>{ try{ o.dispose(); }catch(e){} }); }
  const own=[], sc=new T.Scene(), dome=!!(pk&&pk.dome), sky=hl3dBgSkyTex(dome,day); own.push(sky); sc.background=sky;
  sc.add(new T.AmbientLight(0xffffff,day? .9 : .72)); const dl=new T.DirectionalLight(day? 0xffffff : 0xfff4dc,day? .75 : .55); dl.position.set(day? -90 : 40,day? 220 : 160,120); sc.add(dl);   // 昼は日差しを強く(三塁側の上から)""")
rep("""  if(!dome){ const gt=hl3dBgGlowTex(); own.push(gt); heads.forEach(p=>{""","""  if(!dome && !day){ const gt=hl3dBgGlowTex(); own.push(gt); heads.forEach(p=>{""")
rep("""  hl3dBgS={key,box,sc,cam,own,men,raf:0,t0:performance.now(),last:0,W:0,H:0,io:true};""","""  hl3dBgS={key,box,sc,cam,own,men,raf:0,t0:performance.now(),last:0,W:0,H:0,io:true,day:!!day};
  hl3dSbDeco();""")

# ===== 電光掲示板の飾りを置く =====
rep("""function hl3dBgAim(){ const S=hl3dBgS; if(!S) return; const m=document.getElementById("matchup"), bar=document.getElementById("actionBar");""",
"""// v2.1.l:スコアボードの後ろの飾り(取り付け枠・照明・支柱)。ボードの位置に合わせて置く
function hl3dSbDeco(){ const S=hl3dBgS; if(!S) return; const card=S.box.parentElement, m=document.getElementById("matchup"), bar=document.getElementById("actionBar"); if(!card || !m) return;
  let d=card.querySelector(":scope > .hl3sb"); if(!d){ d=document.createElement("div"); d.className="hl3sb"; d.innerHTML='<i class="sbPost"></i><i class="sbPost"></i><i class="sbFrame"></i><i class="sbLamp"></i><i class="sbLamp"></i>'; S.box.after(d); }
  d.classList.toggle("day",!!S.day);
  const c0=card.getBoundingClientRect(), r=m.getBoundingClientRect(); if(!r.width || !r.height){ d.style.display="none"; return; } d.style.display="";
  const x=r.left-c0.left, y=r.top-c0.top, w=r.width, h=r.height, gb= bar? Math.max(0,bar.getBoundingClientRect().top-r.bottom) : 60;
  const [p1,p2,fr,l1,l2]=d.children, px=v=>Math.round(v)+"px";
  Object.assign(fr.style,{left:px(x-7),top:px(y-7),width:px(w+14),height:px(h+14)});
  [[p1,.24],[p2,.76]].forEach(([p,f])=>Object.assign(p.style,{left:px(x+w*f-7),top:px(y+h),height:px(gb*.62)}));
  Object.assign(l1.style,{left:px(x-2),top:px(y-38)}); Object.assign(l2.style,{left:px(x+w-42),top:px(y-38)}); }
function hl3dBgAim(){ const S=hl3dBgS; if(!S) return; try{ hl3dSbDeco(); }catch(e){} const m=document.getElementById("matchup"), bar=document.getElementById("actionBar");""")
rep("""  if(card){ card.classList.remove("hl3bgCard","hl3bgOn"); const b=card.querySelector(":scope > .hl3dBg"); if(b) b.remove(); } }""",
"""  if(card){ card.classList.remove("hl3bgCard","hl3bgOn"); const b=card.querySelector(":scope > .hl3dBg"); if(b) b.remove(); const d=card.querySelector(":scope > .hl3sb"); if(d) d.remove(); } }""")
open(sys.argv[2],"w",encoding="utf-8").write(s)
print("ok")
