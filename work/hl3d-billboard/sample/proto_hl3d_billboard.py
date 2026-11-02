# 見本(捨てる作り):観戦の 3D と背景の選手を「2D の絵の板(ビルボード)」に。python3 proto_bb.py src.html out.html
import sys
s=open(sys.argv[1],encoding="utf-8").read()
def rep(a,b):
    global s
    k=s.count(a)
    if k!=1: raise SystemExit(f"count {k}: {a[:80]}")
    s=s.replace(a,b)
# ① 絵と板
rep("""function hl3dMan(col,own,glv,uni,role){""",
r"""/* 見本:選手のビルボード。U=hl3dUniform の結果、role f/b/r、pose stand/throw/run1/run2 */
const hl3dBillC=new Map(); let HL3D_BILL=true;
function hl3dBillTex(U,role,pose,glv){ const hx=n=>"#"+(n>>>0).toString(16).padStart(6,"0"), key=[U.body,U.cap,U.trim,U.sleeve,U.brim,U.skin,U.style,role,pose,glv?1:0].join("|"); if(hl3dBillC.has(key)) return hl3dBillC.get(key);
  const W=128,H=192, cv=document.createElement("canvas"); cv.width=W; cv.height=H; const g=cv.getContext("2d"); g.lineWidth=3; g.strokeStyle="#1b1b22"; g.lineJoin="round"; g.lineCap="round";
  const body=hx(U.body), cap=hx(U.cap), trim=hx(U.trim), slv=hx(U.sleeve), brim=hx(U.brim==null? U.cap : U.brim), skin=hx(U.skin), acc= U.style===1? hx((U.body===0xf4f2ec)? U.cap : (U.cap)) : (U.style===3? hx(U.body===0xf4f2ec? U.cap : 0xf4f2ec) : null);
  const rr=(x,y,w,h,r,fill,pat)=>{ g.beginPath(); g.moveTo(x+r,y); g.arcTo(x+w,y,x+w,y+h,r); g.arcTo(x+w,y+h,x,y+h,r); g.arcTo(x,y+h,x,y,r); g.arcTo(x,y,x+w,y,r); g.closePath(); g.fillStyle=fill; g.fill();
    if(pat){ g.save(); g.clip(); pat(x,y,w,h); g.restore(); } g.stroke(); };
  const stripes=(x,y,w,h)=>{ if(U.style===1){ g.fillStyle=acc; for(let sx=x+6;sx<x+w;sx+=11) g.fillRect(sx,y,3,h); } };
  const run= pose==="run1"? 1 : pose==="run2"? -1 : 0, thr= pose==="throw";
  // 脚(ズボン=胴の色。走るときは前後)
  const crouch= pose==="crouch"; if(crouch){ g.translate(0,28); }   /* しゃがむ:全体を下げて脚を短く */
  const leg=(cx,ang)=>{ g.save(); g.translate(cx,128); g.rotate(ang); rr(-9,0,18,crouch? 16 : 44,6,body,stripes); rr(-11,crouch? 12 : 40,24,13,6,"#2a2a30"); g.restore(); };
  leg(52, crouch? -.6 : run*.5); leg(76, crouch? .6 : -run*.5);
  // 腕(袖の色。手=肌。グラブ/バット)
  const arm=(sx,ang,hand)=>{ g.save(); g.translate(64+sx*24,86); g.rotate(ang); rr(-7,-4,14,42,6,slv); g.beginPath(); g.arc(0,42,8,0,Math.PI*2); g.fillStyle=skin; g.fill(); g.stroke();
    if(hand==="glv"){ g.beginPath(); g.arc(0,46,11,0,Math.PI*2); g.fillStyle="#7a4a22"; g.fill(); g.stroke(); g.beginPath(); g.moveTo(-6,40); g.lineTo(6,40); g.stroke(); }
    if(hand==="bat"){ g.save(); g.translate(0,42); g.rotate(-.5); rr(-4,-78,8,80,4,"#c8a064"); g.restore(); } g.restore(); };
  const rA= thr? -2.6 : run? -.9*run : .18, lA= thr? -.9 : run? .9*run : -.18;   // 右=投げる腕、左=グラブ
  arm(1, rA, role==="b"? "bat" : null); arm(-1, lA, glv? "glv" : null);
  // 胴(ユニフォーム)・ベルト
  rr(36,76,56,56,10,body,(x,y,w,h)=>{ stripes(x,y,w,h); if(U.style===3){ g.fillStyle=acc; g.fillRect(x,y+18,w,14); } }); rr(36,126,56,9,3,trim);
  // 頭・顔・帽子
  g.beginPath(); g.arc(64,46,34,0,Math.PI*2); g.fillStyle=skin; g.fill(); g.stroke();
  g.fillStyle="#1b1b22"; [[52,50],[76,50]].forEach(([x,y])=>{ g.beginPath(); g.arc(x,y,3.2,0,Math.PI*2); g.fill(); });
  g.beginPath(); g.moveTo(46,41); g.lineTo(57,43); g.moveTo(82,41); g.lineTo(71,43); g.stroke(); g.beginPath(); g.arc(64,60,6,.2,Math.PI-.2); g.stroke();
  g.beginPath(); g.arc(64,42,36,Math.PI,0); g.closePath(); g.fillStyle=cap; g.fill(); g.stroke(); rr(26,36,76,10,5,brim);
  const tx=hl3dNR(()=>new THREE.CanvasTexture(cv)); tx.minFilter=THREE.LinearMipmapLinearFilter; hl3dBillC.set(key,tx); return tx; }
function hl3dBill(col,own,glv,uni,role){ const T=THREE, g=new T.Group(), U=uni||hl3dUniform(null,true), sm=new T.MeshBasicMaterial({color:0x000000,transparent:true,opacity:.32,depthWrite:false}); own.push(sm);
  const mats=[sm], ops=[.32]; const sh=new T.Mesh(hl3dGeo("shadow"),sm); sh.rotation.x=-Math.PI/2; sh.position.y=.15; g.add(sh);
  if(role==="b" || role==="r"){ const rm=new T.MeshBasicMaterial({color: role==="b"? 0xc0392b : 0xf2c94c,transparent:true,opacity:.9,side:T.DoubleSide,depthWrite:false}); own.push(rm); mats.push(rm); ops.push(.9); const rg=new T.Mesh(hl3dGeo("rolering"),rm); rg.rotation.x=-Math.PI/2; rg.position.y=.22; g.add(rg); }
  const pm=new T.MeshBasicMaterial({map:hl3dBillTex(U,role,"stand",glv),transparent:true,alphaTest:.5,side:T.DoubleSide}); own.push(pm); mats.push(pm); ops.push(1);
  const pg=new T.PlaneGeometry(9.6,14.4).translate(0,7.2,0); own.push(pg); const pl=new T.Mesh(pg,pm); g.add(pl); g.scale.setScalar(1.4);
  g.userData.bill={U,role,glv,pm,pose:"stand"}; g.userData.arm=new T.Object3D(); g.userData.glv=new T.Object3D(); g.userData.mats=mats; g.userData.op=ops; return g; }
function hl3dBillPose(m,pose){ const B=m.userData.bill; if(!B || B.pose===pose) return; B.pose=pose; B.pm.map=hl3dBillTex(B.U,B.role,pose,B.glv); B.pm.needsUpdate=true; }
function hl3dBillFace(m,cam){ if(!m.userData.bill) return; const dx=cam.position.x-m.position.x, dz=cam.position.z-m.position.z, dy=cam.position.y-m.position.y; m.rotation.order="YXZ"; m.rotation.set(-Math.atan2(dy,Math.hypot(dx,dz))*.7, Math.atan2(dx,dz), 0); }   /* 横はカメラへ。上下はカメラの見下ろしの 7 割だけ倒して、上から見ても絵が潰れないように */
function hl3dMan(col,own,glv,uni,role){""")
# ② 観戦で使う
rep("""      it.man=hl3dMan(isF? 0xece8dc : role==="b"? 0xc0392b : 0xf2c94c, own, isF, tm? hl3dUniform(tm, tm===hl3Teams.home) : null, role); sc.add(it.man); }""",
"""      it.man=(HL3D_BILL? hl3dBill : hl3dMan)(isF? 0xece8dc : role==="b"? 0xc0392b : 0xf2c94c, own, isF, tm? hl3dUniform(tm, tm===hl3Teams.home) : null, role); sc.add(it.man); }""")
rep("""    if(it.man){ it.man.position.copy(hl3dP(x,y,0)); if(op!==it.op){ it.man.visible=op>.01; it.man.userData.mats.forEach((m,j)=>{ m.opacity=it.man.userData.op[j]*op; }); } }""",
"""    if(it.man){ it.man.position.copy(hl3dP(x,y,0)); if(op!==it.op){ it.man.visible=op>.01; it.man.userData.mats.forEach((m,j)=>{ m.opacity=it.man.userData.op[j]*op; }); }
      if(it.man.userData.bill){ const q=it.man.userData, up=q.arm.rotation.x<-1.4 || q.glv.rotation.x<-1.8; hl3dBillPose(it.man, up? "throw" : (it.sp||0)>8? (Math.floor((it.ph||0)/1.3)%2? "run2" : "run1") : "stand"); hl3dBillFace(it.man,S.cam); if(dv>0) it.man.rotation.x-=dv*.9; } }""")
# ③' ブルペン・ベンチ・待つ打者(6 か所)と、しゃがむ捕手
s=s.replace("hl3dMan(0xece8dc,own,false,hl3dUniform(home,true))","(HL3D_BILL? hl3dBill : hl3dMan)(0xece8dc,own,false,hl3dUniform(home,true))")
s=s.replace("cm.scale.set(.8,.5,.8);","if(cm.userData.bill){ hl3dBillPose(cm,\"crouch\"); cm.scale.setScalar(.8); } else cm.scale.set(.8,.5,.8);")
rep("""        const man=(HL3D_BILL? hl3dBill : hl3dMan)(0xece8dc,own,false,hl3dUniform(home,true)); man.scale.setScalar(.9);""","""        const man=(HL3D_BILL? hl3dBill : hl3dMan)(0xece8dc,own,false,hl3dUniform(home,true)); man.scale.setScalar(.9); if(man.userData.bill){ hl3dBillPose(man,"crouch"); man.scale.setScalar(.6); }""")
rep("""man.position.set(d[0]*sp+n[0]*o,-4.8,d[1]*sp+n[1]*o);""","""man.position.set(d[0]*sp+n[0]*o,man.userData.bill? -2.4 : -4.8,d[1]*sp+n[1]*o);""")
rep("""  { const c=hl3dMan(0xece8dc,own,true,UNI); c.scale.setScalar(.8);""","""  { const c=(HL3D_BILL? hl3dBill : hl3dMan)(0xece8dc,own,true,UNI); c.scale.setScalar(.8); if(c.userData.bill) hl3dBillPose(c,"crouch");""")
# 全部の板をカメラに向ける(背景・観戦)
rep("""  hl3dBgS={key,box,sc,cam,own,men,""","""  const bills=[]; sc.traverse(o=>{ if(o.userData && o.userData.bill) bills.push(o); });
  hl3dBgS={key,box,sc,cam,own,men,bills,""")
rep("""  S.men.forEach((m,i)=>{ m.position.y=Math.max(0,Math.sin(t*2.1+i*1.7))*.25; });""","""  S.men.forEach((m,i)=>{ m.position.y=Math.max(0,Math.sin(t*2.1+i*1.7))*.25; }); (S.bills||[]).forEach(m=>hl3dBillFace(m,S.cam));""")
rep("""  hl3dCur=S; hl3dSize(S); hl3dPoses(S);""","""  S.bills=[]; sc.traverse(o=>{ if(o.userData && o.userData.bill && !items.some(it=>it.man===o)) S.bills.push(o); });   /* 球場の人(ベンチなど)の板 */
  hl3dCur=S; hl3dSize(S); hl3dPoses(S);""")
rep("""function hl3dUpdate(S,t){
  const T=THREE, bp=HL_BP();""","""function hl3dUpdate(S,t){
  const T=THREE, bp=HL_BP(); (S.bills||[]).forEach(m=>hl3dBillFace(m,S.cam));""")
# 名前の札を 3D では出さない(得点 +N・K・アウトの印は残す)
rep("""let hl3dBillC=new Map(); let HL3D_BILL=true;""".replace("let hl3dBillC","const hl3dBillC"),"""const hl3dBillC=new Map(); let HL3D_BILL=true;
document.head.insertAdjacentHTML("beforeend",'<style id="hl3dBillCss">.hl3d .hl3dLab .hl3tag{display:none}</style>');   /* 見本:3D では名前の札を出さない */""")
# ③ 背景の野手
rep("""  const men=[]; Object.keys(HL_POS).filter(k=>k!=="投").forEach(k=>{ const [a,d]=HL_POS[k], m=hl3dMan(0xece8dc,own,true,UNI),""",
"""  const men=[]; Object.keys(HL_POS).filter(k=>k!=="投").forEach(k=>{ const [a,d]=HL_POS[k], m=(HL3D_BILL? hl3dBill : hl3dMan)(0xece8dc,own,true,UNI),""")
rep("""    const v=hl3dP(x,y,it.man? 11*(1-.65*dv) : it.z).project(S.cam);""","""    const v=hl3dP(x,y,it.man? (it.man.userData.bill? 21 : 11)*(1-.65*dv) : it.z).project(S.cam);   /* 見本:板の人は札を頭の上(16)に */""")
open(sys.argv[2],"w",encoding="utf-8").write(s); print("ok")
