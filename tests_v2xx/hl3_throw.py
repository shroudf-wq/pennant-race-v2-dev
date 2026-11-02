# 送球とアウトの順番(v2.0.j)を確かめる。python3 hl3_throw.py <URL> <セーブ.json> <撮る先のフォルダ>
#   ① hl3Fielding に作った場面を渡し、野球の決まりどおりの順番になっているか(数字で)
#      ・タッチプレーで3つ目のアウト+得点:アウトの印 > 得点の走者が本塁を踏む時刻
#      ・フォースアウトで3つ目のアウト+得点(計算では出ない):本塁を踏む時刻 > アウトの印
#      ・アウトになる走者は、ボールが塁に届いたあとに着く。併殺は二塁 → 一塁の順
#   ② 同じ場面を観戦の 2.5D で描き、途中のコマを撮る(1.0・1.3・1.7・2.6 秒)
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from h import *
URL, SV, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
os.makedirs(OUT, exist_ok=True)
CASES={
 "dp":      {"kind":"OUT","dp":1,"pn":["一走",None,None],"po":0,"outs":2,"runs":0,"mv":[]},
 "goro":    {"kind":"OUT","pn":[None,None,None],"po":1,"outs":2,"runs":0,"mv":[]},
 "sh":      {"kind":"SH","pn":["一走",None,None],"po":0,"outs":1,"runs":0,"mv":[[1,2]]},
 "fc":      {"kind":"FC","pn":["一走","二走",None],"po":0,"outs":1,"runs":0,"mv":[[1,2],[0,1]]},
 "1b_out3": {"kind":"1B","pn":["一走",None,"三走"],"po":2,"outs":3,"runs":1,"mv":[[3,4],[0,1]]},          # 一塁走者が三塁で刺されて3アウト。三塁走者の得点は、踏んでからのアウトなので入る
 "1b_out3b":{"kind":"1B","pn":["一走","二走",None],"po":2,"outs":3,"runs":1,"mv":[[2,4],[0,1]]},          # 二塁走者(2つ走る)が還ってから
 "1b_home": {"kind":"1B","pn":[None,"二走","三走"],"po":0,"outs":1,"runs":1,"mv":[[3,4],[0,1]]},          # 二塁走者が本塁で刺される
 "2b_home": {"kind":"2B","pn":["一走",None,None],"po":1,"outs":2,"runs":0,"mv":[[0,2]]},                 # 一塁走者が本塁で刺される
 "force3":  {"kind":"OUT","dp":1,"pn":["一走",None,"三走"],"po":1,"outs":3,"runs":1,"mv":[[3,4]]},        # 計算では出ない組み合わせ(フォースで3アウト+得点)
 # v2.0.k:v1.2.v の作戦と走塁(af=打った後の塁、bp=打球、exp=アウトになる [元の塁,アウトの塁])
 "gg":      {"kind":"OUT","bp":"G遊","pn":[None,None,"三走"],"po":0,"outs":1,"runs":1,"mv":[[3,4]],"af":[0,0,0],"exp":[[0,1]]},          # ゴロゴー:打者は一塁でアウト、三塁走者が還る
 "ho":      {"kind":"OUT","bp":"G三","pn":[None,None,"三走"],"po":0,"outs":1,"runs":0,"mv":[[0,1]],"af":[1,0,0],"exp":[[3,4]]},          # 本塁でアウト(打者は一塁へ)
 "fo":      {"kind":"OUT","bp":"G二","pn":["一走",None,None],"po":0,"outs":1,"runs":0,"mv":[[0,1]],"af":[1,0,0],"exp":[[1,2]]},          # 二塁で封殺(打者は一塁に残る)
 "dbl":     {"kind":"OUT","bp":"F遊","pn":[None,None,"三走"],"po":0,"outs":2,"runs":0,"mv":[],"af":[0,0,0],"exp":[[3,3]]},               # ライナーで三塁走者が飛び出して併殺
 "dp_gg":   {"kind":"OUT","dp":1,"bp":"G遊","pn":["一走",None,"三走"],"po":0,"outs":2,"runs":1,"mv":[[3,4]],"af":[0,0,0],"exp":[[1,2],[0,1]]},  # 0アウトの併殺の間に三塁走者が還る
 "stay":    {"kind":"OUT","bp":"G二","pn":[None,"二走",None],"po":0,"outs":1,"runs":0,"mv":[],"af":[0,1,0],"exp":[[0,1]]},               # 作戦なし:二塁走者は動かない
}
CHECK="""(c)=>{ const out={}; for(const [k,e] of Object.entries(c)){
    const ev=Object.assign({inn:5,half:"表",batter:"打者",pitcher:"投手",fd:0},e), seed=37;
    const tr= hlTrajectory(ev,seed) || hl3Grounder(ev,seed,hl3Bip(ev));
    const F=hl3Fielding(ev,tr,e.af? e.af.map(Boolean) : undefined), st=.9, per=HL_PER;
    const home=(ev.mv||[]).filter(([,b])=>b===4).map(([a,b])=>{ const t=F.arr[a+","+b]; return t? t : st+(b-a)*per; });
    out[k]={legs:F.legs.map(l=>[+l.t0.toFixed(2),+l.t1.toFixed(2)]), marks:F.marks.map(m=>+m.t.toFixed(2)), mvOut:F.mvOut.map(x=>[x[0],x[1],+x[2].toFixed(2)]), home:home.map(t=>+t.toFixed(2)), gb: tr? tr.h : null};
  } return out; }"""
bad=0
with sync_playwright() as p:
    br=p.chromium.launch()
    pg=open_page(br,URL,seed=9,w=390,h=844,extra="localStorage.setItem('pennantHl3d','on');")
    pg.click("text=はじめる"); pg.wait_for_timeout(200); pg.evaluate("(t)=>loadFromText(t)",open(SV,encoding="utf-8").read())
    R=pg.evaluate(CHECK,CASES)
    for k,v in R.items():
        e=CASES[k]; msg=[]
        if "exp" in e and [x[:2] for x in v["mvOut"]]!=e["exp"]: msg.append(f"アウトの塁が違う {[x[:2] for x in v['mvOut']]} (想定 {e['exp']})")
        for (a,b,ra),(t0,t1),m in zip(v["mvOut"],v["legs"],v["marks"][len(v["marks"])-len(v["mvOut"]):]):
            if ra<t1: msg.append(f"走者{a}→{b}がボールより先")
        if len(v["legs"])>1 and not all(v["legs"][i][1]<=v["legs"][i+1][0] for i in range(len(v["legs"])-1)): msg.append("中継の順番")
        third=e["outs"]>=3 and e["runs"]>0
        if third and v["marks"]:
            force= e["kind"] in ("OUT","SH","FC")
            if not force and not (v["marks"][-1] > max(v["home"])): msg.append("タッチで3アウト:本塁より先にアウト")
            if force and not (min(v["home"]) > v["marks"][-1]): msg.append("フォースで3アウト:アウトより先に本塁")
        if not v["marks"]: msg.append("アウトの印がない")
        bad+=len(msg)
        print(f"{k:9s} 送球{v['legs']} 印{v['marks']} アウトの走者{v['mvOut']} 本塁{v['home']}", "NG "+", ".join(msg) if msg else "OK")
    # ② 観戦の 2.5D で描いて途中のコマを撮る
    pg.evaluate("""()=>{ for(;;){ while(gameIdx<schedule.length){ const g=schedule[gameIdx]; if(g[0]===myTeam||g[1]===myTeam) break; simScheduledGame(); }
        setManageMode(false); playNextGameHighlight(); if(highlightQueue.length) break; closeHighlights(); } hlClearTimers(); }""")
    for k in ("dp","1b_out3","ho","dbl","gg"):
        e=CASES[k]
        pg.evaluate("""([e])=>{ hlClearTimers(); const base=highlightQueue[0], r=highlightGameResult;
            const ev=Object.assign({},base,e,{bases:[null,null,null],rn:(e.af||[0,0,0]).map(Boolean),before:base.before,after:base.after,fw:undefined,fwLast:undefined});
            hl3Cam="B"; hlRenderPlay(r,ev); }""",[e])
        t0=0
        for t in (1.0,1.3,1.7,2.6):
            pg.wait_for_timeout(int((t-t0)*1000)); t0=t
            pg.locator("#hlStage").screenshot(path=f"{OUT}/{k}_{t:.1f}.png")
    print("errs",pg.errs[:3])
    pg.context.close(); br.close()
print("NG", bad)
