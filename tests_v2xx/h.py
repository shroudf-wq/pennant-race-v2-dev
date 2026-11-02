import json, sys
from playwright.sync_api import sync_playwright
SEED_JS="""(function(){ let s=(%d)>>>0; Math.random=function(){ s=s+0x6D2B79F5|0; let t=Math.imul(s^s>>>15,1|s); t=t+Math.imul(t^t>>>7,61|t)^t; return ((t^t>>>14)>>>0)/4294967296; }; })();
try{ (function(){ const F={pennantCampAuto:"1"}, D={};   /* F=上書きして見せる値(extra で決めたもの)、D=値がないときだけ見せる値 */
  (function(localStorage){ %s })({ setItem:(k,v)=>{ F[k]=String(v); }, getItem:k=>(k in F? F[k] : null), removeItem:k=>{ delete F[k]; } });
  D.pennantCampAuto=F.pennantCampAuto; delete F.pennantCampAuto;
  const S=Storage.prototype, gi=S.getItem, si=S.setItem, ri=S.removeItem, mine=s=>s===window.localStorage;
  S.getItem=function(k){ if(mine(this)){ if(k in F) return F[k]; const v=gi.call(this,k); return (v===null && k in D)? D[k] : v; } return gi.call(this,k); };
  S.setItem=function(k,v){ if(mine(this)) delete F[k]; return si.call(this,k,v); };
  S.removeItem=function(k){ if(mine(this)) delete F[k]; return ri.call(this,k); };
})(); }catch(e){}
/* 10/24(v1.4.b のテストの直し):init script(読み込みのいちばん最初)で端末の記録(localStorage)を読む・書くと、直前のページで書いたものが
   消えることがある(Chromium と init script の競合。ゲームなしのページでも 40回に3〜5回。ls_race_check.py)。init script では localStorage に触らない:
   キャンプのおまかせ(pennantCampAuto)は値がないときだけ「1」に見せ、extra の setItem で決めた値は、ページがその鍵を書く・消すまで読み出しで上書きして見せる */"""
SEASON="""()=>{ while(gameIdx<schedule.length){ if(typeof cupBusy==="function" && cupBusy()){ cupAuto(); continue; } simScheduledGame(); }
  if(leagueFormat==="twodiv" && league.some(t=>t.division) && !relegation.done){ startRelegation(); simRelegationAll(); }
  if(tierEligible() && !tierRelegation.done){ startTierRelegation(); simTierRelegationAll(); }
  if(pendingChaosDecision){ chaosContinue(); closeModal(); } startPostseason(); simPostseasonAll(); return year; }"""
OFF="""()=>{ startDraft(); finishDraft(); if(!ikuDraft.done){ if(!ikuDraft.active) startIkuseiDraft(); } startOffseason(); try{ closeModal(); }catch(e){} return year; }"""
def open_page(br,url,seed=11,w=390,h=844,extra="",reduced=False):
    ctx=br.new_context(viewport={"width":w,"height":h},reduced_motion=("reduce" if reduced else "no-preference"))
    pg=ctx.new_page(); pg.errs=[]
    pg.on("pageerror",lambda e: pg.errs.append(str(e)))
    pg.on("dialog",lambda d:(pg.errs.append("DIALOG:"+d.message),d.dismiss()))
    pg.add_init_script(SEED_JS%(seed,extra))
    pg.goto(url,wait_until="domcontentloaded"); pg.wait_for_timeout(400); return pg
# v1.6.d:「はじめる」のあとにモードを選ぶ画面が出る版では「通常」を選んでからリーグ設定へ(前の版では何もしない)
MP_NORMAL="()=>{ const m=document.getElementById('modePick'); if(m && !m.classList.contains('hidden')){ const b=m.querySelector('[data-mode=normal]'); if(b) b.click(); } }"
SCM_AUTO="()=>{ if(typeof scmSet==='function') scmSet('auto'); }"
WZ_LAST="()=>{ if(typeof wzGo==='function') wzGo(3); }"
def to_setup(pg,wait=200):
    pg.click("text=はじめる"); pg.wait_for_timeout(wait); pg.evaluate(MP_NORMAL); pg.wait_for_timeout(100)
def create(pg,sel=None):
    sel=dict(sel or {}); sel.setdefault("tbSel","off")   # v1.5.r:古いテストは「同率のときの順位」を今までどおりに(前の版と比べるため)。新しい決め方を確かめるテストは tbSel を渡す
    to_setup(pg)
    pg.evaluate("()=>document.querySelectorAll('#setup details').forEach(d=>d.open=true)")   # v1.2.m:折りたたみを開いてから選ぶ
    for k,v in (sel or {}).items():
        # v1.3.j:プルダウンがボタンになって見えない形で残るものがあるので、JS で値を入れて change を出す(select_option と同じ動き)
        pg.evaluate("([id,v])=>{ const s=document.getElementById(id); if(!s) return; s.value=v; s.dispatchEvent(new Event('input',{bubbles:true})); s.dispatchEvent(new Event('change',{bubbles:true})); }",[k,v])
    pg.evaluate(WZ_LAST)   # v1.6.e:リーグ設定が段に分かれた版では最後の段(「リーグを作成する」がある)へ
    pg.click("text=リーグを作成する"); pg.wait_for_timeout(300); pg.evaluate("try{ closeModal(); }catch(e){}")
    pg.evaluate(SCM_AUTO)   # v1.6.g:自チームの「調子での入れ替え」を今までどおり(おまかせ)に(前の版と比べるため)。新しい決め方を確かめるテストは自分で選ぶ
