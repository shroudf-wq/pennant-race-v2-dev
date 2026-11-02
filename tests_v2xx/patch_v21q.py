# v2.1.p のソースに当てると v2.1.q。python3 patch_v21q.py src.html new.html
# 見た目だけ(背景の観客席の絵。乱数は使わない)。
#   ユーザーの「波打ちのときとタオルをあげるときに服の色まで変わってるのが気になる」:
#   お客さんの絵 hl3dPeopleTex は、腕を上げた絵を別の数列で描いていたので、腕を上げると別の人(服・帽子・顔の色)に入れ替わっていた。
#   先に10人ぶんの姿(位置・服・顔・帽子か髪・タオルの色・腕を上げるか)を決めてから描き、2枚の絵は同じ人たちにする。
#   腕を上げた絵は、腕とタオルを描き足すだけ。首にタオルをかけている人は、その同じタオルを持ち上げる
import sys
s=open(sys.argv[1],encoding="utf-8").read()
def rep(a,b):
    global s
    k=s.count(a)
    if k!=1: raise SystemExit(f"count {k}: {a[:80]}")
    s=s.replace(a,b)
rep('const APP_VERSION="v2.1.p"; const BASE_V1="v1.4.b";','const APP_VERSION="v2.1.q"; const BASE_V1="v1.4.b";')
a=s.index("function hl3dPeopleTex(base,mix,up){"); b=s.index("function hl3dStandsFull(",a)
s=s[:a]+r'''function hl3dPeopleTex(base,mix,up){   // base=寄せる色(null なら寄せない)、mix=その割合、up=腕(タオル)を上げた絵。v2.1.q:up でも同じ人たち
  const cv=document.createElement("canvas"); cv.width=256; cv.height=64; const g=cv.getContext("2d");
  let x=(base? parseInt(String(base).replace("#",""),16)|0 : 4242)+Math.round(mix*100)*131; const rnd=()=>{ x=(Math.imul(x,1103515245)+12345)&0x7fffffff; return x/0x7fffffff; };
  const shirts=["#e8e4dc","#2b4f8c","#b8312f","#f2c230","#3d8b4f","#1d1d1f","#7a4fa0","#e07a2e","#5aa3d8","#d6d0c4","#8c8c8c","#f08fb0"], skin=["#f0c9a0","#e2b48a","#c99a72","#f5d5b5"], hair=["#1c1712","#3b2a1e","#2a2522","#6b4a2e"];
  const pick=a=>a[Math.floor(rnd()*a.length)];
  // 先に10人の姿を決める(up でも同じ数列なので同じ人)
  const P=[]; for(let k=0;k<10;k++){ const cx=12.8+k*25.6+(rnd()-.5)*5, sh= (base && rnd()<mix)? base : pick(shirts), hy=24+rnd()*6, sk=pick(skin), r=rnd();
    const cap= r<.35? ((base && rnd()<.6)? base : pick(shirts)) : null, hr= (!cap && r<.8)? pick(hair) : null;
    const towel= rnd()<.18, tc= base && rnd()<.7? base : "#f4f1e8", raise= rnd()<.85;
    P.push({cx,sh,hy,sk,cap,hr,towel,tc,raise}); }
  g.fillStyle="#2a2f37"; g.fillRect(0,0,256,64);   // 座席の背もたれ(人のすき間)
  P.forEach(p=>{ const {cx,sh,hy}=p;
    g.fillStyle=sh; g.beginPath(); g.ellipse(cx,64,10.5,30-(hy-24),0,Math.PI,0); g.fill();   // 肩と胴
    if(up && p.raise){ g.strokeStyle=sh; g.lineWidth=4.5; g.lineCap="round"; g.beginPath(); g.moveTo(cx-7,44); g.lineTo(cx-10,hy-16); g.moveTo(cx+7,44); g.lineTo(cx+10,hy-16); g.stroke();
      g.fillStyle= p.towel? p.tc : (base || "#f4f1e8"); g.fillRect(cx-12,hy-22,24,6); }   // 腕とタオル(首のタオルがある人はそれを持ち上げる)
    g.fillStyle=p.sk; g.beginPath(); g.arc(cx,hy,7,0,Math.PI*2); g.fill();   // 顔
    if(p.cap){ g.fillStyle=p.cap; g.beginPath(); g.arc(cx,hy-1.5,7.4,Math.PI,0); g.fill(); g.fillRect(cx-1,hy-3,10,3); }   // 帽子
    else if(p.hr){ g.fillStyle=p.hr; g.beginPath(); g.arc(cx,hy-2,7.2,Math.PI*1.05,-Math.PI*.05); g.fill(); }   // 髪
    if(p.towel && !(up && p.raise)){ g.fillStyle=p.tc; g.fillRect(cx-9,50,18,5); } });   // 首にかけたタオル
  const t=new THREE.CanvasTexture(cv); t.wrapS=THREE.RepeatWrapping; t.anisotropy=4; return t; }
'''+s[b:]
open(sys.argv[2],"w",encoding="utf-8").write(s)
print("ok")
