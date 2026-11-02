# bcv-figures の確かめ:打席の画面(AI の絵がオフのときの SVG の図)の打者・投手
# 使い方: python3 bcv_check.py 新.html 元.html [写しの出力フォルダ]
#   元=パッチを当てる前(v2.2.l)。同じ乱数で同じ打席を出して、印・ゾーン・時間が前と同じかも比べる。
#   par_v2.py(v1 との一致)は別に回す(README)。
import sys, os, json
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "tests_v2xx"))
from h import *
NEW, BASE = [os.path.abspath(x) for x in sys.argv[1:3]]
SHOTS = sys.argv[3] if len(sys.argv) > 3 else os.path.join(HERE, "shots")
os.makedirs(SHOTS, exist_ok=True)
res = []
def ok(name, cond, info=""):
    res.append(bool(cond)); print(("OK " if cond else "NG ") + name + ("" if cond else "  " + str(info)[:400]), flush=True)

# 自チームの試合を進めて、条件に合う打席(カウント場面)を出す。lb=左打者か・sw=途中に振る球があるか・home=打者がホームか(None=どちらでも)
FIND = """([lb,sw,home])=>{ for(let g=0; g<160 && gameIdx<schedule.length; g++){ if(typeof cupBusy==="function" && cupBusy()){ cupAuto(); continue; }
    const x=simScheduledGame(); if(!x||!x.isMy) continue;
    const q=pickHighlights((x.r.log&&x.r.log.events)||[], league[myTeam].name);
    const k=q.findIndex(ev=>{ if(!Array.isArray(ev.pn) || !bcEachOn(ev)) return false; const bc=bcOfEv(ev); if(!bc || bc.seq.length<3) return false;
      const d=bczDetail(ev,bc,x.r); if(lb!==null && (d.side===1)!==lb) return false; if(sw && !d.p.slice(0,-1).some(p=>p.t==="w"||p.t==="f")) return false;
      if(home!==null && (ev.half==="裏")!==home) return false; return true; });
    if(k<0) continue;
    const t=q[k]; startHighlightReel(x.r); const j=highlightQueue.findIndex(e=>e.inn===t.inn && e.half===t.half && e.batter===t.batter && e.pitcher===t.pitcher && e.po===t.po && e.kind===t.kind); if(j<0){ closeHighlights(); continue; }
    window.__ev=t; window.__r=x.r; highlightIdx=j; renderHighlightScene(); return {k:j, inn:t.inn, half:t.half, batter:t.batter, pitcher:t.pitcher}; }
  return null; }"""
# 10ms ごとに、投手のコマ・スイング・印・球の大きさを記録する
LOG = """()=>{ window.__log=[]; const t0=performance.now(); window.__lt=setInterval(()=>{ const sc=document.getElementById("bcvScene");
    const p=document.getElementById("bcfPit"), b=document.getElementById("bcfBat"), m=document.getElementById("bcvMarks"), ball=document.getElementById("bcvBall");
    __log.push([Math.round(performance.now()-t0), !!sc, p? p.getAttribute("data-f") : null, b? (b.classList.contains("sw")? "sw" : b.classList.contains("fo")? "fo" : "") : null, m? m.children.length : -1, ball? +ball.getAttribute("r") : -1, ball? [+ball.getAttribute("cx"),+ball.getAttribute("cy")] : null]); },10); }"""
def wait_scene(pg, ms=8000):
    for _ in range(ms // 50):
        if pg.evaluate("()=>!!document.getElementById('bcvScene')"): return True
        pg.wait_for_timeout(50)
    return False
def run_scene(br, url, lb, sw, home, seed, w=390, h=844, shot=None, mid=None, want=True):
    pg = open_page(br, url, seed=seed, w=w, h=h)
    create(pg, {"tacSel": "off"})
    pg.evaluate("()=>{ HLO.speed='normal'; HLO.bc='each'; HLO.bcv='bat'; }")
    pg.evaluate(LOG)
    f = pg.evaluate(FIND, [lb, sw, home])
    got = wait_scene(pg) if f else False
    info = None
    if got:
        pg.wait_for_timeout(60)
        if shot: pg.locator("#highlightOverlay").screenshot(path=os.path.join(SHOTS, shot))
        info = pg.evaluate(INFO) if want else True
        if mid:   # 振った瞬間の写し(スイングが付くまで待つ)
            for _ in range(200):
                if pg.evaluate("()=>{ const b=document.getElementById('bcfBat'); return !!(b && b.classList.contains('sw')); }"): break
                pg.wait_for_timeout(15)
            pg.locator("#highlightOverlay").screenshot(path=os.path.join(SHOTS, mid))
        for _ in range(300):   # 打席の画面が終わるまで
            if not pg.evaluate("()=>!!document.getElementById('bcvScene')"): break
            pg.wait_for_timeout(50)
    log = pg.evaluate("()=>{ clearInterval(__lt); return __log; }")
    return pg, f, info, log
# 打席の画面のようす
INFO = """()=>{ const sc=document.getElementById("bcvScene"), r=__r, ev=__ev, top=ev.half==="表";
  const B=bczPl(r,ev.batter), P=bczPl(r,ev.pitcher), bt= top? r.awayTeam : r.homeTeam, pt= top? r.homeTeam : r.awayTeam;
  const bat=document.getElementById("bcfBat"), pit=document.getElementById("bcfPit");
  const txt=bat? [...bat.querySelectorAll("text.bcfNum")] : [];
  const mir=e=>{ for(let x=e.parentElement; x && x!==bat; x=x.parentElement){ if((x.getAttribute("transform")||"").includes("scale(-1")) return true; } return false; };
  const ctmA=e=>{ const m=e.getCTM(); return m? m.a : 0; };
  const helmet=bat? [...bat.querySelectorAll(".bcfSt path")].map(p=>p.getAttribute("fill")) : [];
  const hand=pit? pit.querySelector(".bcfF2 circle[r='1.1']") : null;
  let hp=null; if(hand){ const m=hand.getCTM(), svg=hand.ownerSVGElement, sm=svg.getCTM(); const pt0=svg.createSVGPoint(); pt0.x=+hand.getAttribute("cx"); pt0.y=+hand.getAttribute("cy"); const q=pt0.matrixTransform(sm.inverse().multiply(m)); hp=[+q.x.toFixed(2),+q.y.toFixed(2)]; }
  const dir= P && P.throws==="左"? -1 : 1;
  return {lefty:sc.classList.contains("lefty"), old:!!sc.querySelector(".bcvBatter,.bcvPitcher,#bcvBat"), bat:!!bat, pit:!!pit, st:bat&&bat.dataset.st, stance:bcfStance(B),
    no:B? B.no : null, nums:txt.map(t=>t.textContent), mirrored:txt.some(mir), ctm:txt.map(ctmA), teamC:bcfHex(teamColorMap[bt.name]||bt.color), pitC:bcfHex(teamColorMap[pt.name]||pt.color), helmet,
    pitHelmet: pit? [...pit.querySelectorAll(".bcfF0 path")].map(p=>p.getAttribute("fill")) : [], skin:bcfSkin(B), face: (()=>{ try{ return FACE.forPlayer(B,{}); }catch(e){ return ""; } })(),
    hand:hp, start:bcvStart(dir), lp:dir<0, zone:(()=>{ const z=sc.querySelector(".bcvZone"); return z? ["x","y","width","height"].map(a=>z.getAttribute(a)) : null; })(),
    bHome:!top, uni:bcfUni(bt,!top) }; }"""
MARKS = "()=>{ const m=document.getElementById('bcvMarks'); return m? m.innerHTML : null; }"

with sync_playwright() as p:
    br = p.chromium.launch()
    shots = {}
    # 1) 右打者・ホーム・振る球あり
    pg, f, I, logN = run_scene(br, "file://" + NEW, False, True, True, 31, shot="new_R_home_stance_390.png", mid="new_R_home_swing_390.png")
    ok("1-1 右打者・ホームの打席が出る", f and I, f)
    if I:
        ok("1-2 前の人形(.bcvBatter・.bcvPitcher・#bcvBat)が無く、部品の打者と投手がある", I["bat"] and I["pit"] and not I["old"], I)
        ok("1-3 右打者は図の左(lefty でない)", not I["lefty"])
        ok("1-4 番号=その選手の背番号(構えの胸・打った瞬間と振り切りの背中の3つ)", I["no"] is not None and I["nums"] == [str(I["no"])] * 3, (I["no"], I["nums"]))
        ok("1-5 番号は反転の外(鏡文字にならない。CTM の a>0)", not I["mirrored"] and all(a > 0 for a in I["ctm"]), I["ctm"])
        ok("1-6 ヘルメットは打者の球団の色・ホームは白のユニフォーム", I["teamC"] in I["helmet"] and I["uni"]["jer"] == "#f4f2ec", (I["teamC"], I["helmet"][:8]))
        ok("1-7 投手の帽子は投手の球団の色", I["pitC"] in I["pitHelmet"], (I["pitC"], I["pitHelmet"]))
        ok("1-8 肌の色は似顔(FACE)と同じ", I["skin"] in I["face"], I["skin"])
        ok("1-9 構えは能力から(bcfStance と同じ)", I["st"] == I["stance"], (I["st"], I["stance"]))
        ok("1-10 リリースの手=球の出どころ(bcvStart)", I["hand"] and abs(I["hand"][0] - I["start"][0]) < .6 and abs(I["hand"][1] - I["start"][1]) < .6, (I["hand"], I["start"]))
        fs = [x[2] for x in logN if x[2] is not None]
        seq = [fs[0]] + [b for a, b in zip(fs, fs[1:]) if a != b] if fs else []
        ok("1-11 投手が セット→脚上げ→リリース→セット と動く", "0" in seq and "1" in seq and "2" in seq and any(seq[i:i+3] == ["1", "2", "0"] for i in range(len(seq))), seq[:12])
        ss = [x[3] for x in logN if x[3] is not None]; ch = [ss[0]] + [b for a, b in zip(ss, ss[1:]) if a != b] if ss else []
        ok("1-12 振る球で 構え→打った瞬間(背中)→振り切り→構え と変わる", any(ch[i:i+4] == ["", "sw", "fo", ""] for i in range(len(ch))), ch[:12])
        rel = [x for i, x in enumerate(logN) if i and x[2] == "2" and logN[i-1][2] != "2"]
        ball0 = [x for i, x in enumerate(logN) if i and x[5] > 0 and logN[i-1][5] <= 0]
        ok("1-13 リリースのコマが、球が出るのと同じころ(±60ms)", rel and ball0 and abs(rel[0][0] - ball0[0][0]) <= 60, (rel[:1], ball0[:1]))
        ok("1-14 エラーなし", not pg.errs, pg.errs[:2])
    pg.context.close()
    # 同じ乱数の元の版で同じ打席:印・ゾーン・時間
    pgB, fB, _, logB = run_scene(br, "file://" + BASE, False, True, True, 31, shot="old_R_home_390.png", want=False)
    pgB.context.close()
    ok("2-1 元の版でも同じ打席が出る", fB == f, (fB, f))
    def lands(log):   # 印が増えたとき・画面が消えたとき(打席の画面が出た時刻から数える)
        out = []; last = None
        t0 = next((x[0] for x in log if x[1]), 0); log = [[x[0] - t0] + x[1:] for x in log if x[0] >= t0]
        for x in log:
            if x[4] != last: out.append((x[0], x[4])); last = x[4]
        end = next((x[0] for x in log if out and x[0] > out[0][0] and not x[1]), None)
        return out, end
    lN, eN = lands(logN); lB, eB = lands(logB)
    ok("2-2 印の数の移り変わりが同じ", [k for _, k in lN] == [k for _, k in lB], (lN, lB))
    ok("2-3 印が付く時刻が同じ(±80ms)", len(lN) == len(lB) and all(abs(a[0] - b[0]) <= 80 for a, b in zip(lN, lB)), (lN, lB))
    ok("2-4 打席の画面が終わる時刻が同じ(±80ms)", eN and eB and abs(eN - eB) <= 80, (eN, eB))
    bN = [x[6] for x in logN if x[5] > 0][:40]; bB = [x[6] for x in logB if x[5] > 0][:40]
    ok("2-5 球の通り道が同じ(最初の球の出どころ)", bN and bB and abs(bN[0][0] - bB[0][0]) < 1.5 and abs(bN[0][1] - bB[0][1]) < 1.5, (bN[:1], bB[:1]))

    # 3) 左打者・ビジター(見逃しの多い打席でも可)
    pg, f, I, _ = run_scene(br, "file://" + NEW, True, False, False, 33, shot="new_L_away_stance_390.png")
    ok("3-1 左打者・ビジターの打席が出る", f and I, f)
    if I:
        ok("3-2 左打者は図の右(lefty)・番号は反転しない", I["lefty"] and not I["mirrored"] and all(a > 0 for a in I["ctm"]), I)
        ok("3-3 番号=その選手の背番号", I["nums"] == [str(I["no"])] * 3, (I["no"], I["nums"]))
        u = I["uni"]
        ok("3-4 ビジターは球団の色か灰色(白ではない)", u["jer"] != "#f4f2ec" and (u["jer"] == I["teamC"] or u["jer"] == "#a9aeb3"), u)
        ok("3-5 エラーなし", not pg.errs, pg.errs[:2])
    pg.context.close()
    # 左投手:リリースの手が反転側(157)
    pg = open_page(br, "file://" + NEW, seed=35); create(pg, {"tacSel": "off"})
    r = pg.evaluate("""()=>{ const det={side:-1,p:[]}; baCtx=null; const st=document.createElement("div"); st.innerHTML=bcfPitcherSvg(det,{P:{throws:"左"},pt:league[0],bHome:true});
      const svg=document.createElementNS("http://www.w3.org/2000/svg","svg"); svg.setAttribute("viewBox","0 0 300 230"); svg.style.width="300px"; svg.style.height="230px"; svg.innerHTML=st.innerHTML; document.body.appendChild(svg);
      const g=svg.querySelector("#bcfPit"); g.setAttribute("data-f","2"); const h=svg.querySelector(".bcfF2 circle[r='1.1']"), m=h.getCTM(), sm=svg.getCTM(); const q=svg.createSVGPoint(); q.x=+h.getAttribute("cx"); q.y=+h.getAttribute("cy");
      const o=q.matrixTransform(sm.inverse().multiply(m)); svg.remove(); return [o.x,o.y,150+7]; }""")
    ok("3-6 左投げはリリースの手が反対側(157,110)=bcvStart(-1)", abs(r[0] - r[2]) < .6 and abs(r[1] - 110) < .6, r)
    # 4) 構えの割合(能力から)・場面の情報が無いときの形
    d = pg.evaluate("""()=>{ const c={std:0,kan:0,nek:0}; allTeamsEverywhere().forEach(t=>[...(t.batters||[]),...(t.bench||[])].forEach(p=>{ c[bcfStance(p)]++; })); return c; }""")
    tot = sum(d.values())
    ok("4-1 構えは3通りとも出る(ふつうが多め)", all(d[k] > 0 for k in d) and d["std"] >= max(d["kan"], d["nek"]), d)
    print("   構えの割合(1軍とベンチの野手):", {k: f"{v}人 {v*100/tot:.0f}%" for k, v in d.items()})
    z = pg.evaluate("()=>{ baCtx=null; const h=bcvSceneHtml({side:1,p:[]}); return [h.includes('bcfBat'), h.includes('bcfPit'), !h.includes('bcfNum'), !h.includes('Math')]; }")
    ok("4-2 打席の情報が無くても描ける(番号は省く)", all(z), z)
    ok("4-3 絵の打席が読めないときの戻り先(baOrigScene)も部品の人物", pg.evaluate("()=>{ baCtx=null; return typeof baOrigScene==='function' && baOrigScene({side:-1,p:[]}).includes('bcfBat'); }"))
    src = open(NEW, encoding="utf-8").read()
    a = src.index("/* ===== bcv-figures"); b = src.index("function bcvMarksHtml(det,upto){")
    ok("4-4 足した所に Math.random を使っていない", "Math.random(" not in src[a:b] and "Math.random(" not in src[src.index("{ const o=bcvThrow; bcvThrow=function(det,k,dir,dur,then){\n    try{ if(document.getElementById(\"bcfPit\")"):src.index("let baOrigScene=null;")])
    ok("4-5 版の名前は変えていない(v2.2.l)", pg.evaluate("APP_VERSION") == "v2.2.l")
    pg.context.close()
    # 5) PC 幅の写し
    pg, f, I, _ = run_scene(br, "file://" + NEW, False, True, None, 31, w=1200, h=900, shot="new_R_stance_pc.png", mid="new_R_swing_pc.png")
    ok("5-1 PC 幅でも出てエラーなし", f and I and not pg.errs, pg.errs[:2])
    pg.context.close()
    pg, f, _, _ = run_scene(br, "file://" + BASE, False, True, None, 31, w=1200, h=900, shot="old_R_pc.png", want=False)
    pg.context.close()
    br.close()
n = sum(res); print(f"\n{n}/{len(res)} OK")
