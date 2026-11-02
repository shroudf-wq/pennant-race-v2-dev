# じっくり采配の結果の場面(v2.0.g)を確かめる。python3 hl3_manage.py <v1のURL> <v2のURL> <幅> <撮る先のフォルダ>
#   ・同じ seed で、v1 と v2 で采配の試合を1つずつ最後まで進め、各場面の結果(res・得点・アウト・塁)が全部同じか(描画が試合を変えていないか)
#   ・v2(立体あり)の結果の場面:カメラ・動く走者の数・本塁へ還る走者の数=得点か・ボールの有無・札の重なり・はみ出し
#   ・動きのある場面を何枚か撮る
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from h import *
from h3 import open_page3   # v2.1.b:HL3D_LOCAL があれば v2 を「立体:3D」で
V1, V2, W, OUT = sys.argv[1], sys.argv[2], int(sys.argv[3]), sys.argv[4]
os.makedirs(OUT, exist_ok=True)
GAMES=int(sys.argv[5]) if len(sys.argv)>5 else 6
SEL={"numTeams":"6","parkSel":"on","importSel":"off","traitSel":"off"}
MEASURE="""()=>{ const st=document.querySelector('#mgStage.hl3'); if(!st) return null; const B=st.getBoundingClientRect();
  const ts=[...st.querySelectorAll('.hl3tag,.hl3txt.runs')].filter(t=>{ const b=t.closest('.hl3bb'); return parseFloat(getComputedStyle(b).opacity)>=.1 && getComputedStyle(b).visibility!=='hidden'; })
    .map(t=>{ const r=t.getBoundingClientRect(); return {n:t.textContent, x:r.left, y:r.top, w:r.width, h:r.height}; });
  let pairs=[], outs=[];
  for(let i=0;i<ts.length;i++){ const a=ts[i];
    if(a.x<B.left-2||a.y<B.top-2||a.x+a.w>B.right+2||a.y+a.h>B.bottom+2) outs.push(a.n);
    for(let j=i+1;j<ts.length;j++){ const b=ts[j]; const ix=Math.min(a.x+a.w,b.x+b.w)-Math.max(a.x,b.x), iy=Math.min(a.y+a.h,b.y+b.h)-Math.max(a.y,b.y);
      if(ix>0&&iy>0&&ix*iy>6) pairs.push(a.n+'×'+b.n); } }
  const mv=[...st.querySelectorAll('.hl3mv')].map(e=>e.dataset.mv), safe=[...st.querySelectorAll('.hl3mv:not([data-out])')].map(e=>e.dataset.mv);   // v2.0.j〜:data-out はアウトになる走者(本塁で刺される走者は数えない)
  return {d3:st.classList.contains('hl3d'), cam:st.dataset.to, mv, home:safe.filter(x=>x.endsWith(',4')).length, ball:!!st.querySelector('.hl3ball'), pairs, outs}; }"""
# 采配を進める:代打・継投などは「おまかせ」、バントは打たせる、盗塁は走らせる(結果の場面を増やす)。間(mgPause)は通さない
STEP="""()=>{ if(!mg) return {done:true}; const d=mg.dec; let ans=null;
  if(d.kind==="bunt") ans={bunt:false}; else if(d.kind==="steal") ans={steal:true};
  stepManaged(ans); if(!mg) return {done:true}; const e=mg.dec;
  return {done:false, kind:e.kind, res:e.res||null, from:e.from||null, ok:e.ok, scored:e.scored||0, outs:e.outs, rn:e.rn, inn:e.inn, half:e.half, cur:e.cur}; }"""
def run(url, hl3, shots):
    with sync_playwright() as p:
        br=p.chromium.launch()
        pg=open_page3(br,url,seed=21,w=W,h=844 if W<700 else 700,mode=hl3) if (hl3=="on" and shots is not None) else open_page(br,url,seed=21,w=W,h=844 if W<700 else 700,extra=f"localStorage.setItem('pennantHl3d','{hl3}');")
        create(pg,SEL)
        pg.evaluate("()=>{ try{ HLO.mgv='off'; }catch(e){} }")   # v2.2.l:v1.5.f の「采配の合間の見せ場」はテストでは止める(開くと試合の終わりで待つ)
        pg.evaluate("()=>{ for(let k=0;k<12;k++) simScheduledGame(); setManageMode(true); startManagedGame(); }")
        pg.wait_for_timeout(300)
        seq=[]; stat={"res":0,"bad":0,"pairs":0,"outs":0,"cams":{}}; n=0
        games=0
        for k in range(3000):
            r=pg.evaluate(STEP)
            if r["done"]:
                games+=1
                if games>=GAMES: break
                pg.evaluate("()=>{ try{ closeModal(); }catch(e){} try{ closeHighlights(); }catch(e){} startManagedGame(); }"); pg.wait_for_timeout(150); continue
            seq.append((r["kind"],r["res"],r["from"],r["ok"],r["scored"],r["outs"],str(r["rn"]),r["inn"],r["half"],str(r["cur"])))
            if shots is None or r["kind"]!="result": continue
            pg.wait_for_timeout(2700)
            m=pg.evaluate(MEASURE)
            if not m: continue
            stat["res"]+=1; stat["cams"][m["cam"]]=stat["cams"].get(m["cam"],0)+1; stat["3d"]=stat.get("3d",0)+(1 if m.get("d3") else 0)
            stat["pairs"]+=len(m["pairs"]); stat["outs"]+=len(m["outs"])
            exp= r["scored"] if r["from"]!="steal" else 0
            if m["home"]!=exp: stat["bad"]+=1; print("  得点と還った走者が合わない",r["res"],r["scored"],m)
            if m["pairs"] or m["outs"]: print("  ",r["inn"],r["half"],r["res"] or r["from"],"cam",m["cam"],"重なり",m["pairs"],"はみ出し",m["outs"])
            if (m["mv"] or m["ball"]) and n<10 and (m["cam"]!="B" or len(m["mv"])>=2):
                n+=1; pg.wait_for_timeout(200); pg.screenshot(path=f"{OUT}/mg{n}_{r['res'] or r['from']}_{m['cam']}.png")
        errs=pg.errs[:]; pg.context.close(); br.close()
        return seq, stat, errs
s1,_,e1=run(V1,"off",None)
s2,st,e2=run(V2,"on",True)
s3,_,e3=run(V2,"off",None)
print("場面", len(s1), len(s2), len(s3), "v1=v2(立体あり)", s1==s2, "v1=v2(立体なし)", s1==s3)
print("結果の場面", st, "errs", e1[:2], e2[:2], e3[:2])
