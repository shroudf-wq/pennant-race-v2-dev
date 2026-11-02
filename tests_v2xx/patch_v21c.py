# v2.1.b のソースに当てると v2.1.c。python3 patch_v21c.py src.html new.html
# 見た目だけ。試合の計算・記録・セーブには触らない(3D の物を作るのは hl3dNR の中=試合の乱数を使わない)。
#   ① 「立体」の初めの設定を「3D」に(実機で 2.5D と重さが変わらなかったため。2026-10-22)。前に「あり」などを選んだ端末はそのまま。読めない・WebGL がないときは 2.5D
#   ② 3D の球場:ファウルゾーンの観客席(両翼の線の外)・観客の点の模様・照明塔(屋根つきは無し)・観客席とフェンスの上の帯に本拠地の球団の色
#   ③ カメラが打球を追う:本塁打はバックネット裏から打球の後ろを追って外野へ行き、落ちたあと外野席(C)へ回る(暗転なし)。
#      長打・外野フライ(高さ 20 以上)は、見る点を打球へ少し寄せる。カメラが止まってから、札の重なりをもう一度ほどく
import sys
s=open(sys.argv[1],encoding="utf-8").read()
def rep(a,b):
    global s
    k=s.count(a)
    if k!=1: raise SystemExit(f"count {k}: {a[:80]}")
    s=s.replace(a,b)
rep('const APP_VERSION="v2.1.b"; const BASE_V1="v1.2.v";','const APP_VERSION="v2.1.c"; const BASE_V1="v1.2.v";')

# ===== ① 初めの設定は 3D =====
rep("""let HL3D="on"; try{ const v=localStorage.getItem("pennantHl3d"); if(v==="on"||v==="weak"||v==="off"||v==="3d") HL3D=v; }catch(e){}""",
    """let HL3D="3d"; try{ const v=localStorage.getItem("pennantHl3d"); if(v==="on"||v==="weak"||v==="off"||v==="3d") HL3D=v; }catch(e){}   // v2.1.c:初めは 3D(読めないときは「あり」)""")

# ===== ② 本拠地の名前を覚える(観客席の色に使う。読むだけ) =====
rep("""function hl3ParkFor(homeName){
  if(""","""let hl3Home=null;   // v2.1.c:いまの観戦・采配の本拠地の球団名(3D の観客席の色)
function hl3ParkFor(homeName){
  hl3Home=homeName||null;
  if(""")
rep("""  const stands=add(new T.CylinderGeometry(FR+86,FR+5,40,48,1,true,th0,thL), new T.MeshLambertMaterial({color:(pk&&pk.dome)? 0x1a2027 : 0x2b3540,side:T.DoubleSide})); stands.position.y=20;""",
r"""  // v2.1.c:観客席は観客の点の模様に本拠地の色を薄く重ねる。ファウルゾーンにも席(両翼の線の外)。フェンスの上に本拠地の色の帯
  const hc=(()=>{ try{ return new T.Color(String((typeof teamColorMap!=="undefined" && hl3Home && teamColorMap[hl3Home])||"#888888")); }catch(e){ return new T.Color(0x888888); } })();
  const crowd=hl3dCrowdTex(), dome=!!(pk&&pk.dome), sc0=new T.Color(0xffffff).lerp(hc,.35).multiplyScalar(dome? .55 : .8);
  const smat=new T.MeshLambertMaterial({color:sc0,map:crowd,side:T.DoubleSide}); own.push(smat);
  const sgeo=new T.CylinderGeometry(FR+86,FR+5,40,48,1,true,th0,thL); own.push(sgeo); const stands=new T.Mesh(sgeo,smat); sc.add(stands); stands.position.y=20;
  const band=add(new T.CylinderGeometry(FR+.3,FR+.3,1.4,48,1,true,th0,thL), new T.MeshLambertMaterial({color:hc,side:T.DoubleSide})); band.position.y=7.4;
  [[1,1],[-1,1]].forEach(([sx])=>{   // sx=1:一塁側(45°の線)、−1:三塁側(135°の線)
    const d=[sx*Math.SQRT1_2,-Math.SQRT1_2], n=[sx*Math.SQRT1_2,Math.SQRT1_2], P=(s_,o,h)=>[d[0]*s_+n[0]*o, h, d[1]*s_+n[1]*o];
    const s0=28, s1=FR-8, A=P(s0,26,1), B=P(s1,26,1), C=P(s1,66,30), D=P(s0,66,30);
    const g=new T.BufferGeometry(); g.setAttribute("position",new T.BufferAttribute(new Float32Array([...A,...B,...C,...A,...C,...D]),3));
    g.setAttribute("uv",new T.BufferAttribute(new Float32Array([0,0, 6,0, 6,1.4, 0,0, 6,1.4, 0,1.4]),2)); g.computeVertexNormals(); own.push(g);
    sc.add(new T.Mesh(g,smat)); });
  if(!dome) [[20,FR+24],[66,FR+80],[114,FR+80],[160,FR+24]].forEach(([a,r])=>{   // 照明塔(屋根つきの球場には無い)
    const p=hl3dP(...hlPt(a,r),0), pole=add(new T.CylinderGeometry(1.1,1.6,68,6), new T.MeshLambertMaterial({color:0x7d868f})); pole.position.set(p.x,34,p.z);
    const head=add(new T.BoxGeometry(15,8,1.6), new T.MeshBasicMaterial({color:0xfff2c2})); head.position.set(p.x,70,p.z); head.lookAt(0,40,-60); });""")
rep("""function hl3dMan(col,own){""",r"""// v2.1.c:観客の点の模様(1枚を使い回す。点の並びは決まった数列で作り、試合の乱数は使わない)
let hl3dCrowdT=null;
function hl3dCrowdTex(){ if(hl3dCrowdT) return hl3dCrowdT;
  const cv=document.createElement("canvas"); cv.width=256; cv.height=64; const g=cv.getContext("2d"); g.fillStyle="#2c343d"; g.fillRect(0,0,256,64);
  let x=12345; const rnd=()=>{ x=(Math.imul(x,1103515245)+12345)&0x7fffffff; return x/0x7fffffff; };
  const cols=["#cfc8b8","#8e9aa6","#b5463c","#d9b24a","#5a7fa8","#ece8de","#6b6f74","#3f7a55"];
  for(let i=0;i<1500;i++){ g.globalAlpha=.5+rnd()*.5; g.fillStyle=cols[Math.floor(rnd()*cols.length)]; g.fillRect(Math.floor(rnd()*256),Math.floor(rnd()*64),2,2); }
  g.globalAlpha=1; const t=new THREE.CanvasTexture(cv); t.wrapS=t.wrapT=THREE.RepeatWrapping; t.repeat.set(10,3); return hl3dCrowdT=t; }
function hl3dMan(col,own){""")

# ===== ③ カメラが打球を追う =====
rep("""  const cam=new T.PerspectiveCamera(C1.fov,1.3,1,3000);""","""  const cam=new T.PerspectiveCamera(C1.fov,1.3,1,3000);
  // v2.1.c:本塁打はバックネット裏から打球を追う(暗転はやめる)。長打・外野フライは見る点を打球へ寄せる
  const hr=!!(fly && burst); if(hr){ const ct=st.querySelector(".hl3cut"); if(ct) ct.remove(); }""")
rep("""  const S={st,sc,cam,items,fly,burst,pulse,own,C0,C1,t0:performance.now(),raf:0,W:300,H:230,frame:null};""",
    """  const S={st,sc,cam,items,fly,burst,pulse,own,C0,C1,t0:performance.now(),raf:0,W:300,H:230,frame:null,
    chase: hr? {B:HL3D_CAMS.B, C:HL3D_CAMS.C} : null, track: !hr && !!fly && fly.h>=20};
  S.camEnd= hr? 1.75 : S.track? 1.35 : (C0!==C1? .45 : 0);   // カメラが止まる時刻(打球へ寄せるのは 1.3 秒まで)""")
rep("""  setTimeout(()=>hl3Declutter(st,true), C0!==C1? 520 : 40);
  if(mvEnd>0) setTimeout(()=>hl3Declutter(st,true), Math.max(mvEnd+40,560));""",
    """  setTimeout(()=>hl3Declutter(st,true), C0!==C1? 520 : 40);
  if(mvEnd>0) setTimeout(()=>hl3Declutter(st,true), Math.max(mvEnd+40,560));
  if(S.camEnd>.5 && S.camEnd*1000+60>mvEnd+40) setTimeout(()=>hl3Declutter(st,true), S.camEnd*1000+60);   // v2.1.c:カメラが止まってから
  if(mvEnd>0) setTimeout(()=>hl3Declutter(st,true), Math.max(mvEnd+420, S.camEnd*1000+60));   // v2.1.c:本塁に還った走者が消え、得点の +N が出たあとにもう一度""")
# 更新:ボールを先に決めてから、カメラ(追う)
rep("""  // カメラ
  const k= S.C0===S.C1? 1 : hl3dCamE(Math.min(1,t/.45)), L=(a,b)=>a+(b-a)*k;
  S.cam.position.set(L(S.C0.p[0],S.C1.p[0]),L(S.C0.p[1],S.C1.p[1]),L(S.C0.p[2],S.C1.p[2]));
  S.cam.fov=hl3dFov(L(S.C0.fov,S.C1.fov),S.cam.aspect); S.cam.updateProjectionMatrix();
  S.cam.lookAt(L(S.C0.t[0],S.C1.t[0]),L(S.C0.t[1],S.C1.t[1]),L(S.C0.t[2],S.C1.t[2])); S.cam.updateMatrixWorld();
""","")
rep("""    F.bm.position.copy(hl3dP(x,y,z+1.9)); F.bs.position.copy(hl3dP(x,y,.25)); F.bs.material.opacity=Math.max(.12,.4-z/150); }""",
r"""    F.bm.position.copy(hl3dP(x,y,z+1.9)); F.bs.position.copy(hl3dP(x,y,.25)); F.bs.material.opacity=Math.max(.12,.4-z/150); }
  // カメラ
  const ball= F? F.bm.position : null;
  if(S.chase && F){   // v2.1.c:本塁打。0〜0.95 秒は本塁の後ろ上から打球の後ろを追って外野の上へ、1.2 秒から 0.5 秒で外野席(C)へ
    const B=S.chase.B, C=S.chase.C, Lp=hl3dP(F.ex,F.ey,0), P1=[Lp.x*.55, 120, Lp.z*.45+40];
    let pos, tg, fov=B.fov;
    if(t<=.95){ const u=hl3dCamE(Math.min(1,t/.95)), w=Math.min(1,t/.25); pos=B.p.map((v,i)=>v+(P1[i]-v)*u); tg=[B.t[0]+(ball.x-B.t[0])*w, B.t[1]+(ball.y-B.t[1])*w, B.t[2]+(ball.z-B.t[2])*w]; }
    else if(t<1.2){ pos=P1; tg=[Lp.x,0,Lp.z]; }
    else { const k=hl3dCamE(Math.min(1,(t-1.2)/.5)); pos=P1.map((v,i)=>v+(C.p[i]-v)*k); tg=[Lp.x+(C.t[0]-Lp.x)*k, C.t[1]*k, Lp.z+(C.t[2]-Lp.z)*k]; fov=B.fov+(C.fov-B.fov)*k; }
    S.cam.position.set(...pos); S.cam.fov=hl3dFov(fov,S.cam.aspect); S.cam.updateProjectionMatrix(); S.cam.lookAt(...tg);
  } else {
    const k= S.C0===S.C1? 1 : hl3dCamE(Math.min(1,t/.45)), L=(a,b)=>a+(b-a)*k;
    S.cam.position.set(L(S.C0.p[0],S.C1.p[0]),L(S.C0.p[1],S.C1.p[1]),L(S.C0.p[2],S.C1.p[2]));
    S.cam.fov=hl3dFov(L(S.C0.fov,S.C1.fov),S.cam.aspect); S.cam.updateProjectionMatrix();
    let tg=[L(S.C0.t[0],S.C1.t[0]),L(S.C0.t[1],S.C1.t[1]),L(S.C0.t[2],S.C1.t[2])];
    if(S.track && ball && t<1.3){ const w=.35*Math.sin(Math.PI*Math.min(1,t/1.3)); tg=[tg[0]+(ball.x-tg[0])*w, tg[1]+(ball.y-tg[1])*w, tg[2]+(ball.z-tg[2])*w]; }   // v2.1.c:長打・外野フライは打球へ寄せる
    S.cam.lookAt(...tg);
  }
  S.cam.updateMatrixWorld();""")
open(sys.argv[2],"w",encoding="utf-8").write(s)
print("ok")
