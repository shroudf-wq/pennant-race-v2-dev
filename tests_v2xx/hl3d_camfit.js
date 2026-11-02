// 3D のカメラの位置を選ぶ(v2.1.b)。node hl3d_camfit.js(three の npm 版 build/three.js が要る。下の require の場所を合わせる)
// 本塁・捕手・打者と、いちばん広い球場(半径200)のフェンスが、枠(300:230)の 9 割に収まり、見下ろす角度が目安(B 52°・G 42°・C 44°)に近い中で、いちばん近い所を選ぶ。
// B は上の 15% を名前の帯のためにあける(上下 −0.93〜0.70)。G・C は上下の真ん中に。E は G の左右を逆に
const T=require('/home/claude/v2/vendor/package/build/three.js');
const A=300/230;
const P=(ang,d,y=0)=>{const r=ang*Math.PI/180; return new T.Vector3(d*Math.cos(r), y, -d*Math.sin(r));};
function proj(c,pts){ const cam=new T.PerspectiveCamera(c.fov,A,1,3000); cam.position.set(...c.p); cam.lookAt(...c.t); cam.updateMatrixWorld(); cam.updateProjectionMatrix(); return pts.map(v=>v.clone().project(cam)); }
const R=200, core=[new T.Vector3(0,0,8),new T.Vector3(22,12,10),new T.Vector3(-14,12,-6)];
const fence=a=>P(a,R,8);
const fams={
 B:{need:[...core,fence(135),fence(45),fence(90),fence(112),fence(68),P(90,168,12)], gen:(h,d,tz)=>({p:[0,h,d],t:[0,0,tz]})},
 G:{need:[...core,fence(90),fence(68),fence(45),fence(112),P(135,64,12),P(45,64,12)], gen:(h,d,tz)=>({p:[d*0.85,h,d*0.53],t:[10,0,tz]})},
 C:{need:[...core,P(90,R+10,12),P(112,R+10,12),P(68,R+10,12),P(135,64,12),P(45,64,12)], gen:(h,d,tz)=>({p:[0,h,-R-d],t:[0,0,tz]})},
};
for(const [k,F] of Object.entries(fams)){ let best=null;
  for(let h=40;h<=320;h+=5) for(let d=0;d<=300;d+=5) for(let tz=-140;tz<=-20;tz+=5){ const c=Object.assign(F.gen(h,d,tz),{fov:45});
    const q=proj(c,F.need); if(q.some(v=>v.z>1)) continue; const worst=Math.max(...q.map(v=>Math.max(Math.abs(v.x),Math.abs(v.y))));
    if(worst>0.92) continue; const el=Math.atan2(h, Math.hypot(...c.p.map((v,i)=>i===1?0:v-c.t[i])))*180/Math.PI;
    // 低めの視点(25〜40°)で、枠いっぱい(worst 大)を選ぶ
    const tgt={B:52,G:42,C:44}[k]; if(worst<0.80 || Math.abs(el-tgt)>2) continue; const ys=q.map(v=>v.y); if(k==='B'){ if(Math.max(...ys)>0.70 || Math.min(...ys)<-0.93) continue; } else if(Math.abs(Math.max(...ys)+Math.min(...ys))>0.12) continue; const dist=Math.hypot(...c.p.map((v,i)=>v-c.t[i])); const score=-dist;
    if(!best||score>best.score) best={score,c,el:+el.toFixed(1),worst:+worst.toFixed(2)}; }
  console.log(k, JSON.stringify(best)); }
