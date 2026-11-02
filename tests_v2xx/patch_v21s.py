# v2.1.r のソースに当てると v2.1.s。python3 patch_v21s.py src.html new.html
# 見た目だけ(背景の観客席。乱数は使わない)。
#   ユーザーの「やっぱ途切れてるから、100% 描けない(少しでも途切れたら)場合は描かないという感じに」:
#   お客さんの帯を、区画の中で通路・バックスクリーンで区切られた「ひと続き」ごとに分け、まるごと入る人数 n(1人の幅 4)だけ並べる。
#   絵の横の位置は、ひと続きの長さを n 人ぶん(絵の 0〜n/10)に合わせて少し伸び縮みさせる → 端はいつも人と人の間。n=0 の所には置かない。
#   区画(ウェーブで動く単位)の境目も人と人の間になる。絵の中で腕・タオル・肩が隣の人の枠(25.6px)にはみ出さないよう、少し小さくした
import sys
s=open(sys.argv[1],encoding="utf-8").read()
def rep(a,b):
    global s
    k=s.count(a)
    if k!=1: raise SystemExit(f"count {k}: {a[:80]}")
    s=s.replace(a,b)
rep('const APP_VERSION="v2.1.r"; const BASE_V1="v1.4.b";','const APP_VERSION="v2.1.s"; const BASE_V1="v1.4.b";')
# 絵:はみ出さないように
rep("""const cx=12.8+k*25.6+(rnd()-.5)*5,""","""const cx=12.8+k*25.6+(rnd()-.5)*4,""")
rep("""g.lineWidth=4.5; g.lineCap="round"; g.beginPath(); g.moveTo(cx-7,44); g.lineTo(cx-10,hy-16); g.moveTo(cx+7,44); g.lineTo(cx+10,hy-16); g.stroke();
      g.fillStyle= p.towel? p.tc : (base || "#f4f1e8"); g.fillRect(cx-12,hy-22,24,6); }""",
"""g.lineWidth=4; g.lineCap="round"; g.beginPath(); g.moveTo(cx-6.5,44); g.lineTo(cx-8.5,hy-16); g.moveTo(cx+6.5,44); g.lineTo(cx+8.5,hy-16); g.stroke();
      g.fillStyle= p.towel? p.tc : (base || "#f4f1e8"); g.fillRect(cx-10,hy-22,20,6); }""")
# 帯:ひと続きごとに、まるごと入る人数だけ
a=s.index("""        const ns=Math.max(2,Math.ceil(segU/K)); for(let j=0;j<ns;j++){""")
b=s.index("""      const me=mesh(PG,pMat(tex(tk,tb,tm),tk));""",a)
s=s[:a]+"""        const ns=Math.max(2,Math.ceil(segU/K)), pcs=[];
        for(let j=0;j<ns;j++){ const a=u0+(u1-u0)*j/ns, b=u0+(u1-u0)*(j+1)/ns;
          if(skip && b>skip[0] && a<skip[1]){ pcs.push(null); continue; }
          const A0=P(a,v0), B0=P(b,v0), A1=P(a,v1), B1=P(b,v1), Am=P(a,vm), Bm=P(b,vm);
          quad(SEAT,[A0[0],y,A0[1]],[B0[0],y,B0[1]],[B1[0],y,B1[1]],[A1[0],y,A1[1]]);   // 座面
          quad(CON,[A1[0],y,A1[1]],[B1[0],y,B1[1]],[B1[0],y1,B1[1]],[A1[0],y1,A1[1]]);   // 段の立ち上がり
          const gap= aisle && j===0 && k>0 && k%aisle===0;   // 通路(区画の境目)
          if(gap){ quad(CON,[Am[0],y+.05,Am[1]],[Bm[0],y+.05,Bm[1]],[B1[0],y1+.05,B1[1]],[A1[0],y1+.05,A1[1]]); pcs.push(null); }   // 階段
          else pcs.push({Am,Bm,len:Math.hypot(Bm[0]-Am[0],Bm[1]-Am[1])}); }
        // v2.1.s:ひと続き(通路・バックスクリーンで切れない所)ごとに、まるごと入る人数 n だけ並べる(端は人と人の間。n=0 なら置かない)
        for(let j=0;j<pcs.length;){ if(!pcs[j]){ j++; continue; } let e=j, tot=0; while(e<pcs.length && pcs[e]){ tot+=pcs[e].len; e++; }
          const n=Math.floor(tot/4+.15); if(n>0){ let c=0; for(let q=j;q<e;q++){ const {Am,Bm,len}=pcs[q], ua=(c/tot)*n/10, ub=((c+len)/tot)*n/10; c+=len;
              quad(PG,[Am[0],y,Am[1]],[Bm[0],y,Bm[1]],[Bm[0],y+ph,Bm[1]],[Am[0],y+ph,Am[1]],[ua,0,ub,0,ub,1,ua,1]); } }
          j=e; } }
"""+s[b:]
rep("""    const segU=24, cum=new Array(N).fill(0);   // v2.1.r:列ごとの、絵の続きの位置(実際の長さを足し合わせる)""","""    const segU=24;""")
open(sys.argv[2],"w",encoding="utf-8").write(s)
print("ok")
