# v2.1.e のソースに当てると v2.1.f。python3 patch_v21f.py src.html new.html
# 見た目だけ(3D だけ)。試合の計算・記録・セーブには触らない(乱数は使わない)。
#   腕を2本にした。右が投げる腕、左がグラブの腕(野手だけ、手の先に茶色のグラブ)
#   ① 走る:野手・走者とも、動く速さに合わせて左右の腕を交互に振る(振りの位相は走った道のりから決める)。走者も走る向きを向く
#   ② 捕る:グラブの腕を上げて前に出し、投げる腕も添える(両手で捕る)
#   ③ 投げる:投げる腕を後ろへ引くあいだ、グラブの腕を投げる先へ向け、振り下ろすときに体へ引きつける
#   ④ 飛びつく:両腕を前へ伸ばす
#   userData.arm は投げる腕(右)のまま(hl3d_pose.py が読む)。グラブの腕は userData.glv
import sys
s=open(sys.argv[1],encoding="utf-8").read()
def rep(a,b):
    global s
    k=s.count(a)
    if k!=1: raise SystemExit(f"count {k}: {a[:80]}")
    s=s.replace(a,b)
rep('const APP_VERSION="v2.1.e"; const BASE_V1="v1.2.v";','const APP_VERSION="v2.1.f"; const BASE_V1="v1.2.v";')

rep("""    : k==="arm"? new T.CylinderGeometry(.6,.6,4.8,6).translate(0,-2.4,0) : new T.RingGeometry(5,6.4,32);   // v2.1.e:腕(付け根が肩)""",
    """    : k==="arm"? new T.CylinderGeometry(.6,.6,4.8,6).translate(0,-2.4,0) : k==="glove"? new T.SphereGeometry(1.15,8,6).translate(0,-5,0) : new T.RingGeometry(5,6.4,32);   // v2.1.e:腕(付け根が肩)/v2.1.f:グラブ""")

rep("""function hl3dMan(col,own){ const T=THREE, g=new T.Group(), m=new T.MeshLambertMaterial({color:col,transparent:true}), sm=new T.MeshBasicMaterial({color:0x000000,transparent:true,opacity:.32,depthWrite:false});""",
    """function hl3dMan(col,own,glv){ const T=THREE, g=new T.Group(), m=new T.MeshLambertMaterial({color:col,transparent:true}), sm=new T.MeshBasicMaterial({color:0x000000,transparent:true,opacity:.32,depthWrite:false});""")
rep("""  const sp=new T.Group(); sp.position.set(2.7,6.2,0); sp.rotation.x=.15; sp.add(new T.Mesh(hl3dGeo("arm"),m)); g.add(sp); g.userData.arm=sp; /* v2.1.e:腕 */ g.userData.mats=[m,sm]; g.userData.op=[1,.32]; return g; }""",
    """  const mk=sx=>{ const a=new T.Group(); a.position.set(2.7*sx,6.2,0); a.rotation.x=.15; a.rotation.z=.2*sx; a.add(new T.Mesh(hl3dGeo("arm"),m)); g.add(a); return a; };   // v2.1.f:腕を2本(右=投げる・左=グラブ)
  const sp=mk(1), gl=mk(-1); g.userData.arm=sp; g.userData.glv=gl; g.userData.mats=[m,sm]; g.userData.op=[1,.32];
  if(glv){ const gm=new T.MeshLambertMaterial({color:0x7a4a22,transparent:true}); own.push(gm); gl.add(new T.Mesh(hl3dGeo("glove"),gm)); g.userData.mats.push(gm); g.userData.op.push(1); }
  return g; }""")
rep("""    if(cap){ it.man=hl3dMan(cap.classList.contains("f")? 0xece8dc : cap.classList.contains("b")? 0xc0392b : 0xf2c94c, own); sc.add(it.man); }""",
    """    if(cap){ it.man=hl3dMan(cap.classList.contains("f")? 0xece8dc : cap.classList.contains("b")? 0xc0392b : 0xf2c94c, own, cap.classList.contains("f")); sc.add(it.man); }""")

# 腕の角度:投げる腕(r)とグラブの腕(l)。sp=走る速さ・ph=振りの位相・dv=飛びつき
rep("""function hl3dArm(P,t){ let a=.15, d=null;
  (P||[]).forEach(o=>{ const u=t-o.t;
    if(o.k==="c"){ if(u>-.3 && u<.55){ const up= u<0? Math.min(1,(u+.3)/.22) : u<.25? 1 : Math.max(0,1-(u-.25)/.3); a=.15-2.9*up; if(up>0 && o.dir!=null) d=o.dir; } }
    else if(u>-.28 && u<.4){ a= u<-.08? .15+1.7*((u+.28)/.2) : u<.06? 1.85-3.1*((u+.08)/.14) : -1.25+1.4*Math.min(1,(u-.06)/.34); d=o.dir; } });
  return {a,d}; }""",
    """function hl3dArm(P,t,sp,ph,dv){ const amp=Math.min(1,(sp||0)/45)*.95, sw=Math.sin(ph||0)*amp, D=Math.min(1,(dv||0)*1.6);
  let a=.15+sw, l=.15-sw, d=null;   // v2.1.f:走るときは左右を交互に振る
  if(D>0){ a+=(-2.6-a)*D; l+=(-2.9-l)*D; }   // 飛びつく:両腕を前へ
  (P||[]).forEach(o=>{ const u=t-o.t;
    if(o.k==="c"){ if(u>-.3 && u<.55){ const up= u<0? Math.min(1,(u+.3)/.22) : u<.25? 1 : Math.max(0,1-(u-.25)/.3);
        l+=(-2.75-l)*up; a+=(-1.9-a)*up; if(up>0 && o.dir!=null) d=o.dir; } }   // 捕る:グラブを上げ、投げる腕を添える
    else if(u>-.28 && u<.4){ a= u<-.08? .15+1.7*((u+.28)/.2) : u<.06? 1.85-3.1*((u+.08)/.14) : -1.25+1.4*Math.min(1,(u-.06)/.34);
      l= u<-.08? .15-1.75*((u+.28)/.2) : u<.06? -1.6+2.2*((u+.08)/.14) : .6-.45*Math.min(1,(u-.06)/.34); d=o.dir; } });   // 投げる:グラブを投げる先へ向け、振るときに引きつける
  return {a,l,d}; }""")

rep("""    if(it.man && it.poses){ const q=hl3dArm(it.poses,t); it.man.userData.arm.rotation.x=q.a; if(q.d!=null){ it.man.rotation.order="YXZ"; it.man.rotation.y=q.d; } }   // v2.1.e""",
    """    if(it.man){ const dx= it.lx==null? 0 : x-it.lx, dy= it.lx==null? 0 : y-it.ly, dt=Math.max(.001,t-(it.lt==null? t : it.lt)), mv=Math.hypot(dx,dy);   // v2.1.f:走る速さと道のり
      it.sp=(it.sp||0)*.75+(it.lt==null || t<=it.lt? 0 : mv/dt)*.25; it.ph=(it.ph||0)+mv*.42; it.lx=x; it.ly=y; it.lt=t;
      if(!it.kf && mv>.05){ it.man.rotation.order="YXZ"; it.man.rotation.y=Math.atan2(dx,dy); }   // 走者も走る向きを向く
      const q=hl3dArm(it.poses,t,it.sp,it.ph,dv); it.man.userData.arm.rotation.x=q.a; it.man.userData.glv.rotation.x=q.l; if(q.d!=null){ it.man.rotation.order="YXZ"; it.man.rotation.y=q.d; } }   // v2.1.e/f""")

open(sys.argv[2],"w",encoding="utf-8").write(s)
print("ok")
