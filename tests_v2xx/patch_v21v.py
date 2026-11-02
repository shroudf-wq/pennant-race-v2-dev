# v2.1.u のソースに当てると v2.1.v。python3 patch_v21v.py src.html new.html
# 試合画面の背景の球場:内野席の大屋根(A-2)。見た目だけ(背景 opt.full のときだけ。計算・観戦の 3D・セーブには触らない)。
#   ① hl3dParkLook(home,pk):球団ごとの見た目の型。ドームと同じく球団名のハッシュで決めて固定(セーブに足さない)。
#      roof: 0=なし / 1=部分(2 階席の上段だけ) / 2=全面(2 階席の全部)。forteHash(名前+"大屋根")>>>3 を 3 で割った余り。ドームは 0
#   ② hl3dBigRoof:銀色の庇(前の縁 y0 → 後ろ y1 へ少し上がる)+前の縁の梁(白)+後ろの支柱(2 階席の後ろ)+全面型は通路(r 98・y 16)からの前の支柱。
#      全面:r 99〜150・f 186〜354・y 56→63。部分:r 118〜150・f 210〜330・y 58→64
#   ③ 屋根つきの球場では内野側の照明塔を屋根の上に載せる(柱 40・屋根の後ろの縁 y1 から)。屋根は userData.k="bigRoof"
#   テスト:hl3d_bg.py ⑬(屋根の数が hl3dParkLook の型と合う・屋根つきでは内野側の照明塔が屋根の上。ドームでは大屋根なし)
import sys
s=open(sys.argv[1],encoding="utf-8").read()
def rep(a,b):
    global s
    k=s.count(a)
    if k!=1: raise SystemExit(f"count {k}: {a[:80]}")
    s=s.replace(a,b)
rep('const APP_VERSION="v2.1.u"; const BASE_V1="v1.4.b";','const APP_VERSION="v2.1.v"; const BASE_V1="v1.4.b";')
rep("""// v2.1.u:ドームの屋根(背景だけ)。""","""// v2.1.v:球団ごとの見た目の型(背景だけ)。球団名のハッシュで決めて固定。セーブには足さない。roof:0 なし/1 部分/2 全面(ドームは 0)
function hl3dParkLook(home,pk){ const dome=!!(pk&&pk.dome), h=s=>(forteHash(String(home||"")+s)>>>3);
  return {roof: dome? 0 : h("大屋根")%3}; }
// v2.1.v:内野席の大屋根。r0〜r1(本塁から)・f0〜f1・前の縁 y0 → 後ろ y1。後ろの支柱 nc 本、全面型は通路(r 98・y 16)からの前の支柱 8 本
function hl3dBigRoof(sc,own,add,kind){ const T=THREE, full= kind===2, r0= full? 99 : 118, r1=150, f0= full? 186 : 210, f1= full? 354 : 330, y0= full? 56 : 58, y1= full? 63 : 64, seg=30;
  const fx=(f,r)=>{ const t=(f+90)*Math.PI/180; return [r*Math.sin(t), r*Math.cos(t)]; }, p=[];
  for(let j=0;j<seg;j++){ const a=f0+(f1-f0)*j/seg, b=f0+(f1-f0)*(j+1)/seg, A=fx(a,r0), B=fx(b,r0), A2=fx(a,r1), B2=fx(b,r1);
    p.push(A[0],y0,A[1], B[0],y0,B[1], B2[0],y1,B2[1], A[0],y0,A[1], B2[0],y1,B2[1], A2[0],y1,A2[1]); }
  const g=new T.BufferGeometry(); g.setAttribute("position",new T.BufferAttribute(new Float32Array(p),3)); g.computeVertexNormals(); own.push(g);
  const rm=new T.MeshLambertMaterial({color:0xb9c1c8,side:T.DoubleSide}); own.push(rm); const roof=new T.Mesh(g,rm); roof.userData.k="bigRoof"; sc.add(roof);
  const em=new T.MeshLambertMaterial({color:0xdde3e8}), cm=new T.MeshLambertMaterial({color:0x8d959d}); own.push(em,cm);
  for(let j=0;j<seg;j++){ const a=f0+(f1-f0)*(j+.5)/seg, A=fx(a,r0+.4), L=2*Math.PI*r0*((f1-f0)/seg)/360+.4, e=add(new T.BoxGeometry(L,2.2,1.2),em); e.position.set(A[0],y0-.6,A[1]); e.rotation.y=Math.atan2(A[0],A[1]); }
  const nc= full? 13 : 9; for(let i=0;i<=nc;i++){ const a=f0+(f1-f0)*i/nc, P=fx(a,r1-2), c=add(new T.CylinderGeometry(1.1,1.3,16,8),cm); c.position.set(P[0],y1-8,P[1]); }
  if(full) for(let i=0;i<=8;i++){ const a=f0+2+(f1-f0-4)*i/8, P=fx(a,98), c=add(new T.CylinderGeometry(.9,1.1,40,8),cm); c.position.set(P[0],36,P[1]); }
  return {r0,r1,f0,f1,y1}; }
// v2.1.u:ドームの屋根(背景だけ)。""")
rep("""    hl3dStandsFull(sc,own,FR,hc,opt,dome);   // v2.1.p:段のある席・お客さん・応援旗""",
"""    hl3dStandsFull(sc,own,FR,hc,opt,dome);   // v2.1.p:段のある席・お客さん・応援旗
    const LOOK=hl3dParkLook(home,pk), ROOF= LOOK.roof? hl3dBigRoof(sc,own,add,LOOK.roof) : null;   // v2.1.v:内野席の大屋根(球団ごとの型)""")
rep("""    if(!dome) [[205,128+WD.bo],[335,128+WD.bo]].forEach(([a,r])=>{   // 内野側の照明塔(v2.1.t:席と一緒に後ろへ)
      const p=hl3dP(...hlPt(a,r),0), pole=add(new T.CylinderGeometry(1.1,1.6,68,6), new T.MeshLambertMaterial({color:0x7d868f})); pole.position.set(p.x,34,p.z); pole.userData.k="tower";
      const head=add(new T.BoxGeometry(15,8,1.6), new T.MeshBasicMaterial({color:0xfff2c2})); head.position.set(p.x,70,p.z); head.lookAt(0,40,-60); heads.push(head.position.clone()); });""",
"""    if(!dome) [[205,128+WD.bo],[335,128+WD.bo]].forEach(([a,r])=>{   // 内野側の照明塔(v2.1.t:席と一緒に後ろへ)。v2.1.v:大屋根の上なら屋根の後ろの縁から柱 40
      const on= !!(ROOF && a>=ROOF.f0 && a<=ROOF.f1 && r>=ROOF.r0 && r<=ROOF.r1), y0= on? ROOF.y1 : 0, hp= on? 40 : 68;
      const p=hl3dP(...hlPt(a,r),0), pole=add(new T.CylinderGeometry(1.1,1.6,hp,6), new T.MeshLambertMaterial({color:0x7d868f})); pole.position.set(p.x,y0+hp/2,p.z); pole.userData.k="tower";
      const head=add(new T.BoxGeometry(15,8,1.6), new T.MeshBasicMaterial({color:0xfff2c2})); head.position.set(p.x,y0+hp+2,p.z); head.lookAt(0,40,-60); heads.push(head.position.clone()); });""")
open(sys.argv[2],"w",encoding="utf-8").write(s)
print("ok")
