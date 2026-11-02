# hl3d-billboard:3D の観戦と試合画面の背景の選手を「2D の絵の板(ビルボード)」に替える(v2.2.l に当てる)
#   使い方:python3 patch_hl3d-billboard.py 元.html 出力.html
#   変えるのは絵の部分だけ(hl3d* の層)。試合の計算・乱数・セーブ・2.5D の絵には触らない。APP_VERSION も変えない
import sys
s=open(sys.argv[1],encoding="utf-8").read()
def rep(a,b):
    global s
    k=s.count(a)
    if k!=1: raise SystemExit(f"見つかった数 {k}(1 のはず): {a[:90]!r}")
    s=s.replace(a,b)

# ① 板の形(足元が原点。幅 8・高さ 16。絵の 248px 目=足の裏が地面)
rep("""k==="rolering"? new T.RingGeometry(2.7,3.5,24)   /* v2.2.b:帽子・つば・ベルト・役割のリング */""",
    """k==="rolering"? new T.RingGeometry(2.7,3.5,24)   /* v2.2.b:帽子・つば・ベルト・役割のリング */
    : k==="bill"? new T.PlaneGeometry(8,16).translate(0,7.5,0)   /* hl3d-billboard:選手の絵の板(足元が原点) */""")

# ② 人の絵(Canvas 2D)・板・姿勢・カメラへ向ける
rep("""function hl3dMan(col,own,glv,uni,role){""",
r"""/* ===== hl3d-billboard:選手を 2D の絵の板(ビルボード)に =====
   絵は Canvas 2D でその場で描く(128×256。2.5 頭身・右向きの 3/4)。色と柄は hl3dUniform の結果そのまま(縦縞・胸の帯は U.tex の絵を模様にして塗る)。
   姿勢 pose:stand 立つ/throw 投げる・捕る/run1・run2 走る 2 コマ/crouch しゃがむ(捕手・ベンチ)。打者は立つ絵でバット、野手はグラブ。
   絵は「ユニフォームの型×姿勢×グラブ×バット」で使い回す(hl3dBillC。多くなったら古いものから捨てる)。セーブには何も足さない */
const hl3dBillC=new Map(), HL3D_BILL_MAX=160;
const HL3D_BILL_TOP={stand:14, throw:14, run1:16, run2:16, crouch:82};   /* 絵の上端(px。帽子のてっぺん)。足の裏は 248 */
function hl3dBillTex(U,role,pose,glv){
  const bat= role==="b" && pose==="stand", hx=n=>"#"+((n>>>0)&0xffffff).toString(16).padStart(6,"0"),
    key=[U.body,U.cap,U.trim,U.sleeve,U.brim,U.skin,U.style,U.tex? 1 : 0,pose,glv? 1 : 0,bat? 1 : 0].join("|");
  if(hl3dBillC.has(key)){ const t=hl3dBillC.get(key); hl3dBillC.delete(key); hl3dBillC.set(key,t); return t; }
  const cv=document.createElement("canvas"); cv.width=128; cv.height=256; const g=cv.getContext("2d");
  const OL="#1b1b22", body=hx(U.body), capC=hx(U.cap), trim=hx(U.trim), slv=hx(U.sleeve), brim=hx(U.brim==null? U.cap : U.brim), skin=hx(U.skin), SHOE="#2b2b33", GLV="#8a5426", BAT="#d0a868";
  g.lineJoin="round"; g.lineCap="round";
  const pat= (U.tex && U.tex.image)? g.createPattern(U.tex.image,"repeat") : null;
  const uni=(x,y,h,torso)=>{ if(!pat || (U.style===3 && !torso)) return body; pat.setTransform(new DOMMatrix(U.style===3? [1,0,0,h/64,x,y] : [.9,0,0,1,x,y])); return pat; };   /* 縦縞は上下とも、胸の帯は胴だけ */
  const limb=(pts,w,col)=>{ g.beginPath(); g.moveTo(pts[0][0],pts[0][1]); for(let i=1;i<pts.length;i++) g.lineTo(pts[i][0],pts[i][1]);
    g.strokeStyle=OL; g.lineWidth=w+6; g.stroke(); g.strokeStyle=col; g.lineWidth=w; g.stroke(); };
  const rr=(x,y,w,h,r)=>{ g.beginPath(); g.moveTo(x+r,y); g.arcTo(x+w,y,x+w,y+h,r); g.arcTo(x+w,y+h,x,y+h,r); g.arcTo(x,y+h,x,y,r); g.arcTo(x,y,x+w,y,r); g.closePath(); };
  const fill=c=>{ g.fillStyle=c; g.fill(); g.strokeStyle=OL; g.lineWidth=5; g.stroke(); };
  const dot=(x,y,r,c)=>{ g.beginPath(); g.arc(x,y,r,0,Math.PI*2); fill(c); };
  /* 姿勢ごとの関節(脚=腰・膝・足、腕=肩・肘・手)。dy=上半身を下げる量、lx=前へ倒す量 */
  const P={
    stand:{dy:0,lx:0, legs:[[[54,160],[52,198],[50,232]],[[76,160],[79,198],[81,232]]], R:[[46,112],[38,134],[38,154]], L:[[86,112],[94,134],[96,152]]},
    throw:{dy:2,lx:0, legs:[[[54,160],[38,196],[24,232]],[[76,160],[96,192],[104,232]]], R:[[46,112],[28,96],[20,62]], L:[[86,112],[100,114],[106,104]]},
    run1:{dy:4,lx:6, legs:[[[56,162],[44,198],[24,226]],[[74,162],[96,184],[94,222]]], R:[[48,114],[36,132],[24,128]], L:[[86,114],[98,128],[104,116]]},
    run2:{dy:4,lx:6, legs:[[[56,162],[78,184],[78,222]],[[74,162],[64,198],[40,228]]], R:[[48,114],[62,130],[78,122]], L:[[86,114],[76,132],[62,140]]},
    crouch:{dy:68,lx:0, legs:[[[52,226],[30,210],[36,232]],[[78,226],[100,210],[92,232]]], R:[[46,180],[30,200],[30,216]], L:[[86,180],[100,192],[104,184]]} }[pose] || null;
  const Q=P||{dy:0,lx:0,legs:[],R:[[46,112],[38,134],[38,154]],L:[[86,112],[94,134],[96,152]]}, tx=Q.lx, ty=Q.dy, off=p=> pose==="crouch"? p : [p[0]+tx,p[1]+ty];   /* しゃがむ絵の腕は下げた所に書いてある */
  const arm=(A,glove,ball)=>{ limb(A,12,slv); const h=A[2]; dot(h[0],h[1],7,skin);
    if(glove){ g.beginPath(); g.ellipse(h[0]+3,h[1]+1,12,14,.3,0,Math.PI*2); fill(GLV); g.beginPath(); g.moveTo(h[0]-3,h[1]-6); g.lineTo(h[0]+7,h[1]+6); g.strokeStyle="#4a2a10"; g.lineWidth=2.5; g.stroke(); }
    if(ball) dot(h[0],h[1]-6,5,"#ffffff"); };
  const leg=L=>{ const [h,k,f]=L, s=[k[0]+(f[0]-k[0])*.45,k[1]+(f[1]-k[1])*.45];
    limb([h,k,f],17,uni(h[0]-9,h[1],70,false)); limb([s,f],14,trim);   /* ズボン(胴の色・縦縞)と、膝下はストッキング(ベルトの色) */
    g.beginPath(); g.ellipse(f[0]+6,f[1]+8,14,8,0,0,Math.PI*2); fill(SHOE); };
  /* 奥の腕(グラブの手)→ 脚 → 胴 → バット → 手前の腕(投げる手)→ 頭 */
  arm(Q.L.map(off),!!glv,false);
  Q.legs.forEach(leg);
  rr(38+tx,98+ty,54,66,15); fill(uni(38+tx,98+ty,66,true));   /* 胴(ユニフォーム) */
  rr(38+tx,152+ty,54,10,3); fill(trim);   /* ベルト */
  g.beginPath(); g.moveTo(58+tx,104+ty); g.lineTo(65+tx,116+ty); g.lineTo(72+tx,104+ty); g.strokeStyle=OL; g.lineWidth=3; g.stroke();   /* 襟 */
  if(bat){ limb([[66,132],[38,66],[20,22]],9,BAT); limb([[38,66],[20,22]],14,BAT); dot(66,134,5,BAT); }   /* バット(肩にかつぐ) */
  const Rr=Q.R.map(off); if(bat){ limb([Rr[0],[54,128],[64,130]],12,slv); dot(64,130,7,skin); dot(70,134,6,skin); } else arm(Rr,false,pose==="throw");
  /* 頭(肌は hl3dUniform の skin)・耳・髪・顔(目・眉・口)・帽子とつば(右向き) */
  const cx=64+tx, cy=60+ty;
  g.beginPath(); g.arc(cx,cy,37,0,Math.PI*2); g.fillStyle=skin; g.fill();
  g.save(); g.beginPath(); g.arc(cx,cy,37,0,Math.PI*2); g.clip(); g.fillStyle="#3a2a20"; g.beginPath(); g.moveTo(cx-40,cy-8); g.lineTo(cx-12,cy-8); g.lineTo(cx-20,cy+20); g.lineTo(cx-40,cy+24); g.closePath(); g.fill(); g.restore();
  g.beginPath(); g.arc(cx,cy,37,0,Math.PI*2); g.strokeStyle=OL; g.lineWidth=5; g.stroke();
  dot(cx-17,cy+8,7,skin);   /* 耳 */
  g.fillStyle=OL; [[cx+9,cy+7],[cx+27,cy+7]].forEach(([x,y])=>{ g.beginPath(); g.ellipse(x,y,3.6,5.4,0,0,Math.PI*2); g.fill(); });
  g.strokeStyle=OL; g.lineWidth=3; g.beginPath(); g.moveTo(cx+3,cy-4); g.lineTo(cx+14,cy-5); g.moveTo(cx+22,cy-5); g.lineTo(cx+32,cy-3); g.stroke();
  g.beginPath(); g.arc(cx+19,cy+18,6,.25,Math.PI-.25); g.stroke();
  g.fillStyle="rgba(230,110,110,.35)"; g.beginPath(); g.arc(cx+4,cy+19,5,0,Math.PI*2); g.fill();
  g.beginPath(); g.ellipse(cx-1,cy-6,39,36,0,Math.PI,0); g.closePath(); fill(capC);   /* 帽子 */
  dot(cx-1,cy-41,3,capC);
  rr(cx+8,cy-11,44,10,5); fill(brim);   /* つば(右へ) */
  const tx2=hl3dNR(()=>new THREE.CanvasTexture(cv)); tx2.minFilter=THREE.LinearMipmapLinearFilter;
  hl3dBillC.set(key,tx2); if(hl3dBillC.size>HL3D_BILL_MAX){ const k0=hl3dBillC.keys().next().value, t0=hl3dBillC.get(k0); hl3dBillC.delete(k0); try{ t0.dispose(); }catch(e){} }
  return tx2; }
/* 選手の板。足元の丸い影・役割のリング(打者=赤・走者=黄)は地面に寝かせたまま、絵の板だけを子の pv に入れてカメラへ向ける。
   o.pose=初めの姿勢、o.ring=false でリングなし(待つ打者)。userData.arm・glv は今の腕の角度の置き場(hl3d_pose.py が読む) */
function hl3dBill(own,glv,uni,role,o){ const T=THREE, g=new T.Group(), U=uni||hl3dUniform(null,true), op=o||{};
  const sm=new T.MeshBasicMaterial({color:0x000000,transparent:true,opacity:.32,depthWrite:false}); own.push(sm); const mats=[sm], ops=[.32];
  const sh=new T.Mesh(hl3dGeo("shadow"),sm); sh.rotation.x=-Math.PI/2; sh.position.y=.15; g.add(sh);
  if((role==="b" || role==="r") && op.ring!==false){ const rm=new T.MeshBasicMaterial({color: role==="b"? 0xc0392b : 0xf2c94c,transparent:true,opacity:.9,side:T.DoubleSide,depthWrite:false}); own.push(rm); mats.push(rm); ops.push(.9);
    const rg=new T.Mesh(hl3dGeo("rolering"),rm); rg.rotation.x=-Math.PI/2; rg.position.y=.22; g.add(rg); }
  const pose=op.pose||"stand", pm=new T.MeshBasicMaterial({map:hl3dBillTex(U,role,pose,glv),transparent:true,alphaTest:.4,side:T.DoubleSide}); own.push(pm); mats.push(pm); ops.push(1);   /* 透明は alphaTest で切る(深さも書く) */
  const pv=new T.Group(); pv.add(new T.Mesh(hl3dGeo("bill"),pm)); g.add(pv); g.scale.setScalar(1.4);
  g.userData.bill={U,role,glv,pm,pv,pose,flip:1,dir:null,pen:0}; g.userData.arm=new T.Object3D(); g.userData.glv=new T.Object3D(); g.userData.mats=mats; g.userData.op=ops; return g; }
function hl3dBillPose(m,pose){ const B=m && m.userData.bill; if(!B || B.pose===pose) return; B.pose=pose; B.pm.map=hl3dBillTex(B.U,B.role,pose,B.glv); }
/* 板をカメラへ向ける:横(Y)はカメラへ、上下はカメラの見下ろしの 7 割だけ倒す。dir=向いている向き(atan2(dx,dz))が
   カメラから見て左なら左右反転(はっきり左右のときだけ切り替える)。dv=飛びつき(向きの側へ倒す) */
function hl3dBillFace(m,cam,dir,dv){ const B=m && m.userData.bill; if(!B) return; const pv=B.pv, p=m.position, c=cam.position, dx=c.x-p.x, dz=c.z-p.z;
  pv.rotation.order="YXZ"; pv.rotation.y=Math.atan2(dx,dz); pv.rotation.x=-Math.atan2(c.y-p.y,Math.hypot(dx,dz))*.7;
  const d= dir!=null? dir : B.dir; if(d!=null){ const e=cam.matrixWorld.elements, sx=Math.sin(d)*e[0]+Math.cos(d)*e[2]; if(sx<-.2) B.flip=-1; else if(sx>.2) B.flip=1; }
  pv.scale.x=B.flip; pv.rotation.z=-(dv||0)*1.1*B.flip; }
/* 観戦の姿勢:台本の捕る・投げる(it.poses。hl3dArm と同じ時刻)と飛びつき → throw、走る速さ → run1/run2(移動の位相)、捕手は打つ前 → crouch */
function hl3dBillAct(P,t){ return (P||[]).some(o=>{ const u=t-o.t; return o.k==="c"? (u>-.22 && u<.45) : (u>-.28 && u<.3); }); }
function hl3dBillPoseOf(S,it,t,dv){ if(dv>.15 || hl3dBillAct(it.poses,t)) return "throw";
  if((it.sp||0)>8) return (Math.floor((it.ph||0)/4)%2)? "run2" : "run1";
  if(it.b.dataset.pos==="捕" && (!S.fly || t<.5)) return "crouch";
  return "stand"; }
function hl3dMan(col,own,glv,uni,role){""")

# ③ 観戦:人を板に。向き・姿勢は台本のまま(位置・時刻・結果には触らない)
rep("""      it.man=hl3dMan(isF? 0xece8dc : role==="b"? 0xc0392b : 0xf2c94c, own, isF, tm? hl3dUniform(tm, tm===hl3Teams.home) : null, role); sc.add(it.man); }""",
    """      it.man=hl3dBill(own, isF, tm? hl3dUniform(tm, tm===hl3Teams.home) : null, role); sc.add(it.man); }   /* hl3d-billboard:絵の板 */""")
rep("""  hl3dCur=S; hl3dSize(S); hl3dPoses(S);   // v2.1.e:捕る・投げる形""",
    """  S.bills=[]; sc.traverse(o=>{ if(o.userData && o.userData.bill && !items.some(it=>it.man===o)) S.bills.push(o); });   /* hl3d-billboard:球場の人(ベンチ)の板。毎コマカメラへ向ける */
  hl3dCur=S; hl3dSize(S); hl3dPoses(S);   // v2.1.e:捕る・投げる形""")
rep("""  if(mvEnd>0) setTimeout(()=>hl3Declutter(st,true), Math.max(mvEnd+420, S.camEnd*1000+60));   // v2.1.c:本塁に還った走者が消え、得点の +N が出たあとにもう一度
}""",
    """  if(mvEnd>0) setTimeout(()=>hl3Declutter(st,true), Math.max(mvEnd+420, S.camEnd*1000+60));   // v2.1.c:本塁に還った走者が消え、得点の +N が出たあとにもう一度
  lab.querySelectorAll(".hl3tag").forEach(e=>e.remove());   /* hl3d-billboard:3D では名前の札を出さない(絵の板と重なる)。最後まで作れたときだけ外す(途中で失敗したら 2.5D に札ごと戻る)。hl3Declutter は札のない人を飛ばす */
}""")
rep("""  S.cam.updateMatrixWorld();
  if(S.burst){""",
    """  S.cam.updateMatrixWorld();
  (S.bills||[]).forEach(m=>hl3dBillFace(m,S.cam));   /* hl3d-billboard:ベンチなどの板 */
  if(S.burst){""")
rep("""    if(it.man && it.kf){ it.man.rotation.order="YXZ"; it.man.rotation.y=it.hd; it.man.rotation.x=dv*1.35; }""",
    """    if(it.man && it.kf) it.fd=it.hd;   /* hl3d-billboard:向きは板を回さず、左右反転に使う */""")
rep("""      if(!it.kf && mv>.05){ it.man.rotation.order="YXZ"; it.man.rotation.y=Math.atan2(dx,dy); }   // 走者も走る向きを向く
      const q=hl3dArm(it.poses,t,it.sp,it.ph,dv); it.man.userData.arm.rotation.x=q.a; it.man.userData.glv.rotation.x=q.l; if(q.d!=null){ it.man.rotation.order="YXZ"; it.man.rotation.y=q.d; } }   // v2.1.e/f""",
    """      if(!it.kf && mv>.05) it.fd=Math.atan2(dx,dy);   /* 走者も走る向き */
      const q=hl3dArm(it.poses,t,it.sp,it.ph,dv); it.man.userData.arm.rotation.x=q.a; it.man.userData.glv.rotation.x=q.l; if(q.d!=null) it.fd=q.d;   /* v2.1.e/f */
      hl3dBillPose(it.man, hl3dBillPoseOf(S,it,t,dv)); }   /* hl3d-billboard:姿勢の絵 */""")
rep("""    if(it.man){ it.man.position.copy(hl3dP(x,y,0)); if(op!==it.op){""",
    """    if(it.man){ it.man.position.copy(hl3dP(x,y,0)); hl3dBillFace(it.man,S.cam,it.fd,dv); if(op!==it.op){""")

# ④ 球場の人(待つ打者・ブルペンの投手と捕手 2 型・ベンチ)
rep("""        const m=hl3dMan(0xece8dc,own,false,hl3dUniform(home,true)); m.scale.setScalar(.8); m.position.set(x,0,z); m.rotation.y=Math.PI; m.userData.k="ondeck"; sc.add(m); }); }""",
    """        const m=hl3dBill(own,false,hl3dUniform(home,true),"b",{ring:false}); m.scale.setScalar(.8); m.position.set(x,0,z); m.userData.bill.dir=Math.PI; m.userData.k="ondeck"; sc.add(m); }); }   /* hl3d-billboard:バットを持って待つ */""")
rep("""          const ang=Math.atan2(m1[0]-m0[0],m1[1]-m0[1]), pm=hl3dMan(0xece8dc,own,false,hl3dUniform(home,true)); pm.scale.setScalar(.8); pm.position.set(m0[0],fy+.7,m0[1]); pm.rotation.y=ang; pm.userData.k="pen"; sc.add(pm);
          const cm=hl3dMan(0xece8dc,own,false,hl3dUniform(home,true)); cm.scale.set(.8,.5,.8); cm.position.set(m1[0],fy+.3,m1[1]); cm.rotation.y=ang+Math.PI; cm.userData.k="pen"; sc.add(cm); }); }); }""",
    """          const ang=Math.atan2(m1[0]-m0[0],m1[1]-m0[1]), pm=hl3dBill(own,true,hl3dUniform(home,true),"f"); pm.scale.setScalar(.8); pm.position.set(m0[0],fy+.7,m0[1]); pm.userData.bill.dir=ang; pm.userData.bill.pen=1+ro/7+f0/50; pm.userData.k="pen"; sc.add(pm);
          const cm=hl3dBill(own,true,hl3dUniform(home,true),"f",{pose:"crouch"}); cm.scale.setScalar(.8); cm.position.set(m1[0],fy+.3,m1[1]); cm.userData.bill.dir=ang+Math.PI; cm.userData.k="pen"; sc.add(cm); }); }); }   /* hl3d-billboard:投げる投手・しゃがむ捕手 */""")
rep("""        const man=hl3dMan(0xece8dc,own,false,hl3dUniform(home,true)); man.scale.setScalar(.9); man.position.set(d[0]*sp+n[0]*o,-4.8,d[1]*sp+n[1]*o); man.rotation.y=Math.atan2(-n[0],-n[1]); sc.add(man); });""",
    """        const man=hl3dBill(own,false,hl3dUniform(home,true),"f",{pose:"crouch"}); man.scale.setScalar(.6); man.position.set(d[0]*sp+n[0]*o,-2.4,d[1]*sp+n[1]*o); man.userData.bill.dir=Math.atan2(-n[0],-n[1]); man.userData.k="bench"; sc.add(man); });   /* hl3d-billboard:座る(屋根 4.6 に頭が届かない大きさ) */""")
rep("""          const ang=Math.atan2(d[0],d[1]), pm=hl3dMan(0xece8dc,own,false,hl3dUniform(home,true)); pm.scale.setScalar(.8); pm.position.set(m0[0],.7,m0[1]); pm.rotation.y=ang; pm.userData.k="pen"; sc.add(pm);
          const cm=hl3dMan(0xece8dc,own,false,hl3dUniform(home,true)); cm.scale.set(.8,.5,.8); cm.position.set(m1[0],.3,m1[1]); cm.rotation.y=ang+Math.PI; cm.userData.k="pen"; sc.add(cm); });""",
    """          const ang=Math.atan2(d[0],d[1]), pm=hl3dBill(own,true,hl3dUniform(home,true),"f"); pm.scale.setScalar(.8); pm.position.set(m0[0],.7,m0[1]); pm.userData.bill.dir=ang; pm.userData.bill.pen=1+o/5+(sx>0? .9 : 0); pm.userData.k="pen"; sc.add(pm);
          const cm=hl3dBill(own,true,hl3dUniform(home,true),"f",{pose:"crouch"}); cm.scale.setScalar(.8); cm.position.set(m1[0],.3,m1[1]); cm.userData.bill.dir=ang+Math.PI; cm.userData.k="pen"; sc.add(cm); });   /* hl3d-billboard */""")

# ⑤ 試合画面の背景:守備位置の野手・しゃがむ捕手。毎コマ全部の板をカメラへ向け、ブルペンの投手は投げる絵と立つ絵を繰り返す
rep("""m=hl3dMan(0xece8dc,own,true,UNI), p=hl3dP(...hlPt(a, "左中右".includes(k)? WD.Rf(a)*.75 : WD.warp(a,d)),0);""",
    """m=hl3dBill(own,true,UNI,"f"), p=hl3dP(...hlPt(a, "左中右".includes(k)? WD.Rf(a)*.75 : WD.warp(a,d)),0);""")
rep("""m.scale.setScalar(.8); /* v2.1.z:背景の人は小さく */ m.position.copy(p); m.rotation.order="YXZ"; m.rotation.y=Math.atan2(-p.x,-p.z); sc.add(m); men.push(m); });""",
    """m.scale.setScalar(.8); /* v2.1.z:背景の人は小さく */ m.position.copy(p); m.userData.bill.dir=Math.atan2(-p.x,-p.z); sc.add(m); men.push(m); });""")
rep("""  { const c=hl3dMan(0xece8dc,own,true,UNI); c.scale.setScalar(.8); c.position.copy(hl3dP(HL_HX,HL_HY+8,0)); c.rotation.y=Math.PI; sc.add(c); men.push(c); }""",
    """  { const c=hl3dBill(own,true,UNI,"f",{pose:"crouch"}); c.scale.setScalar(.8); c.position.copy(hl3dP(HL_HX,HL_HY+8,0)); c.userData.bill.dir=Math.PI; sc.add(c); men.push(c); }   /* hl3d-billboard:しゃがむ捕手 */""")
rep("""  hl3dBgS={key,box,sc,cam,own,men,raf:0,""",
    """  const bills=[]; sc.traverse(o=>{ if(o.userData && o.userData.bill) bills.push(o); });   /* hl3d-billboard:背景の板(野手・捕手・ベンチ・ブルペン・待つ打者) */
  hl3dBgS={key,box,sc,cam,own,men,bills,raf:0,""")
rep("""  S.men.forEach((m,i)=>{ m.position.y=Math.max(0,Math.sin(t*2.1+i*1.7))*.25; });""",
    """  S.men.forEach((m,i)=>{ m.position.y=Math.max(0,Math.sin(t*2.1+i*1.7))*.25; });
  (S.bills||[]).forEach(m=>{ const B=m.userData.bill; if(B.pen) hl3dBillPose(m, ((t+B.pen*1.7)%2.8)<.8? "throw" : "stand"); hl3dBillFace(m,S.cam); });   /* hl3d-billboard:カメラへ向ける・ブルペンの投球 */""")

open(sys.argv[2],"w",encoding="utf-8").write(s); print("ok")
