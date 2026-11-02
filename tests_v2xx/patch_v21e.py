# v2.1.d のソースに当てると v2.1.e。python3 patch_v21e.py src.html new.html
# 見た目だけ。試合の計算・記録・セーブには触らない(乱数は使わない)。
#   ① 送りバント・バントの失敗(野選):投手・捕手・一塁手・三塁手が前へ出て、打球にいちばん近い野手が捕って投げる(0.94 秒に着く)。
#      ほかの3人は打球のほうへ 45% 出る。二塁手は一塁へ入る(1.0 秒)。2.5D・3D とも(台本の chase)
#   ② 捕る形・投げる形(3D だけ):人に腕を1本付けた。
#      捕る:打球が落ちた所(0.9 秒)にいる野手と、送球の行き先にいる野手が、腕を上げて前に出す
#      投げる:送球の始まりにいる野手が、送球の行き先を向いて、腕を後ろへ引いてから前へ振る
#   ③ ベースカバー:塁へ投げる場面で、その塁の野手が走って入る(二塁は投げる側の反対の二遊間、三塁・本塁・一塁)
#      誰が捕る・投げるかは、その時刻の野手の位置(追う動きを含む)から、いちばん近い野手(捕る 12・投げる 14・送球を受ける 26 以内)
import sys
s=open(sys.argv[1],encoding="utf-8").read()
def rep(a,b):
    global s
    k=s.count(a)
    if k!=1: raise SystemExit(f"count {k}: {a[:80]}")
    s=s.replace(a,b)
rep('const APP_VERSION="v2.1.d"; const BASE_V1="v1.2.v";','const APP_VERSION="v2.1.e"; const BASE_V1="v1.2.v";')

# ===== ① バント =====
rep("""    if(m["捕"]) out+=hl3Bb(HL_HX+22,HL_HY+8,0,c,`<div class="hl3cap f"></div>${hl3TagHtml("",m["捕"])}`,"hl3f");""",
    """    if(m["捕"]) out+=hl3Bb(HL_HX+22,HL_HY+8,0,c,`<div class="hl3cap f"></div>${hl3TagHtml("",m["捕"])}`,"hl3f").replace('class="hl3bb hl3f"','class="hl3bb hl3f" data-pos="捕"');   // v2.1.e:捕手も動かす""")
rep("""  const P=pos=>hlPt(HL_POS[pos][0],HL_POS[pos][1]), D=""","""  const P=pos=> pos==="捕"? [HL_HX+22,HL_HY+8] : hlPt(HL_POS[pos][0],HL_POS[pos][1]), D=""")
rep("""  if(k==="SH"||k==="FC") return out;   // バント:今は動かさない""",
    """  if(k==="SH"||k==="FC"){   // v2.1.e:バント。投・捕・一・三が前へ出て、打球にいちばん近い野手が捕る。二塁手は一塁へ入る
    const cand=["投","一","三","捕"], f=cand.reduce((m,p)=> (!m || D(P(p),L)<D(P(m),L))? p : m, null);
    run(f,L,.94);
    cand.filter(p=>p!==f).forEach(p=>{ const F=P(p); run(p,[F[0]+(L[0]-F[0])*.45, F[1]+(L[1]-F[1])*.45],.9); });
    run("二",hlPt(45,64),1.0);
    return out; }""")

# ===== ② 腕と形(3D) =====
rep("""    : k==="shadow"? new T.CircleGeometry(3.2,16) : k==="ball"? new T.SphereGeometry(1.9,12,8) : k==="disc"? new T.CircleGeometry(2.4,12) : new T.RingGeometry(5,6.4,32);""",
    """    : k==="shadow"? new T.CircleGeometry(3.2,16) : k==="ball"? new T.SphereGeometry(1.9,12,8) : k==="disc"? new T.CircleGeometry(2.4,12)
    : k==="arm"? new T.CylinderGeometry(.6,.6,4.8,6).translate(0,-2.4,0) : new T.RingGeometry(5,6.4,32);   // v2.1.e:腕(付け根が肩)""")
rep("""b.position.y=3.2; h.position.y=8; sh.rotation.x=-Math.PI/2; sh.position.y=.15; g.add(sh,b,h); g.scale.setScalar(1.4); /* v2.1.d:1.4 倍 */ g.userData.mats=[m,sm];""",
    """b.position.y=3.2; h.position.y=8; sh.rotation.x=-Math.PI/2; sh.position.y=.15; g.add(sh,b,h); g.scale.setScalar(1.4); /* v2.1.d:1.4 倍 */
  const sp=new T.Group(); sp.position.set(2.7,6.2,0); sp.rotation.x=.15; sp.add(new T.Mesh(hl3dGeo("arm"),m)); g.add(sp); g.userData.arm=sp; /* v2.1.e:腕 */ g.userData.mats=[m,sm];""")
rep("""hd:0};   // v2.1.d:追う野手""","""hd:0, fld: !!(cap && cap.classList.contains("f"))};   // v2.1.d:追う野手(v2.1.e:fld=野手)""")
rep("""  hl3dCur=S; hl3dSize(S);""","""  hl3dCur=S; hl3dSize(S); hl3dPoses(S);   // v2.1.e:捕る・投げる形""")
rep("""function hl3dStop(){""",r"""/* v2.1.e:捕る・投げる形。it.poses=[{k:"c"捕る/"t"投げる, t:時刻, dir:向き(atan2(dx,dz))}]。誰が捕る・投げるかは、その時刻の野手の位置から決める */
function hl3dPoses(S){
  const F=S.fly; if(!F) return;
  const fl=S.items.filter(it=>it.fld && it.man);
  const at=(it,t)=>{ if(!it.kf) return [it.x,it.y]; const K=it.kf; let i=0; while(i<K.length-1 && t>=K[i+1][0]) i++;
    if(i>=K.length-1) return [K[i][1],K[i][2]]; const a=K[i], b=K[i+1], f=Math.max(0,Math.min(1,(t-a[0])/Math.max(.001,b[0]-a[0]))); return [a[1]+(b[1]-a[1])*f, a[2]+(b[2]-a[2])*f]; };
  const nearest=(x,y,t,lim)=>{ let m=null, md=lim; fl.forEach(it=>{ const p=at(it,t), d=Math.hypot(p[0]-x,p[1]-y); if(d<md){ md=d; m=it; } }); return m; };
  const add=(it,o)=>{ if(it) (it.poses=it.poses||[]).push(o); };
  add(nearest(F.ex,F.ey,.9,12),{k:"c",t:.9,dir:null});   // 打球を捕る
  F.legs.forEach(([x0,y0,x1,y1,t0,t1])=>{
    add(nearest(x0,y0,t0,14),{k:"t",t:t0,dir:Math.atan2(x1-x0,y1-y0)});    // 投げる
    add(nearest(x1,y1,t1,26),{k:"c",t:t1,dir:Math.atan2(x0-x1,y0-y1)}); });  // 送球を受ける
}
// 腕の角度(前へ倒すと負。0.15=下ろしたまま、−2.75=上げて前、+1.85=後ろへ引く、−1.25=前へ振り下ろす)と、そのときの向き
function hl3dArm(P,t){ let a=.15, d=null;
  (P||[]).forEach(o=>{ const u=t-o.t;
    if(o.k==="c"){ if(u>-.3 && u<.55){ const up= u<0? Math.min(1,(u+.3)/.22) : u<.25? 1 : Math.max(0,1-(u-.25)/.3); a=.15-2.9*up; if(up>0 && o.dir!=null) d=o.dir; } }
    else if(u>-.28 && u<.4){ a= u<-.08? .15+1.7*((u+.28)/.2) : u<.06? 1.85-3.1*((u+.08)/.14) : -1.25+1.4*Math.min(1,(u-.06)/.34); d=o.dir; } });
  return {a,d}; }
function hl3dStop(){""")
rep("""    if(it.man && it.kf){ it.man.rotation.order="YXZ"; it.man.rotation.y=it.hd; it.man.rotation.x=dv*1.35; }""",
    """    if(it.man && it.kf){ it.man.rotation.order="YXZ"; it.man.rotation.y=it.hd; it.man.rotation.x=dv*1.35; }
    if(it.man && it.poses){ const q=hl3dArm(it.poses,t); it.man.userData.arm.rotation.x=q.a; if(q.d!=null){ it.man.rotation.order="YXZ"; it.man.rotation.y=q.d; } }   // v2.1.e""")
# ③ 送球を受ける野手が塁に入る(ベースカバー)。台本の送球の区間(legs)を見て、塁へ投げる場面でその塁の野手が走って入る
#    二塁:三塁側から投げたら二塁手、一塁側からなら遊撃手。三塁:三塁手。本塁:捕手。一塁:一塁手(一塁手が打球を捕って動いていたら投手)
rep("""function hl3Chase(ev,tr3,o){""","""function hl3Chase(ev,tr3,o){   // v2.1.e:追う野手+ベースカバー
  const out=hl3Chase0(ev,tr3,o); if(!tr3) return out;
  const P=pos=> pos==="捕"? [HL_HX+22,HL_HY+8] : hlPt(HL_POS[pos][0],HL_POS[pos][1]), busy=new Set(out.map(c=>c.pos));
  const near=(a,b)=>Math.hypot(a[0]-b[0],a[1]-b[1])<8, B1=hlPt(45,64), B2=hlPt(90,90.5), B3=hlPt(135,64), HM=[HL_HX,HL_HY];
  (o.legs||[]).forEach(l=>{ const e=[l.x,l.y+3]; let pos=null;
    if(near(e,B2)) pos= (l.x0<HL_HX)? "二" : "遊"; else if(near(e,B3)) pos="三"; else if(near(e,HM)) pos="捕"; else if(near(e,B1)) pos= busy.has("一")? "投" : "一";
    if(!pos || busy.has(pos) || !(pos==="捕" || HL_POS[pos])) return;
    const F=P(pos), to=[l.x,l.y], d=Math.hypot(to[0]-F[0],to[1]-F[1]), t1=Math.max(HL3_REACT+.05, Math.min(l.t1-.06, HL3_REACT+Math.max(.15,d/HL3_FSP)));
    out.push({pos, kf:[[0,F[0],F[1],0],[HL3_REACT,F[0],F[1],0],[t1,to[0],to[1],0]]}); busy.add(pos); });
  return out;
}
function hl3Chase0(ev,tr3,o){""")
rep("""  const chase= isPc? [] : hl3Chase(ev,tr3,{pick: F.legs.length? F.legs[0].t0 : null, pos:o.fpos||null});""",
    """  const chase= isPc? [] : hl3Chase(ev,tr3,{pick: F.legs.length? F.legs[0].t0 : null, pos:o.fpos||null, legs:F.legs});""")
open(sys.argv[2],"w",encoding="utf-8").write(s)
print("ok")
