# 試合画面の背景の球場(v2.1.j)を確かめる。python3 hl3d_bg.py <URL> <three.min.js の写し> <撮る先>
#   ① 3D:試合タブのカードに背景が入り、描いている(コマが進む)・ホームチームの球場とキーが合う
#   ② ほかのタブ(編成)では止まる → 試合タブに戻ると動く
#   ③ 観戦の窓を開くと止まる → 閉じると動く
#   ④ 設定でオフ → 背景が消える・カードの class が戻る/オン → 戻る
#   ⑤ 立体「あり」(2.5D)では背景なし
#   ⑥ 1シーズン進めてオフ(ドラフトの画面など)でもエラーなし・背景は自チームの球場
#   ⑦ 3D が読めない(HL3D_FAIL)ときは背景なし・エラーなし
#   ⑧ 幅 320・390・1366 でボタンが押せる(背景が前に出ていない)
#   ㉕ v2.2.k:エキサイトシートの赤い席・段の mesh が 2、低い(高さ 6 未満)人の区画が 2 以上
#   ㉔ v2.2.j:カードの空いた所を上下にドラッグすると hl3dBgTilt が変わる(下へ=見上げる +、上へ=見下ろす −0.35 まで)。ボタンの上から始めても変わらず、ボタンは押せる(試合が進む。v2.2.l:v1.6.b から同じ日の前の試合も一緒に進むので 1 つとは限らない)。外野手 3 人はフェンスの 75%、内野手は違う
#   ㉓ v2.2.i:フェンス裏型のブルペンの箱の壁がフェンス+.5(低いフェンスで 7.5)。外の地面の円が MeshBasic で絵の色(2a5534 のままでない)
#   ㉒ v2.2.g:型を強制して scene 0/1/2 で外の景色(scenery)1・外の地面(farGround)1・月 2・星 240(夜)。屋根の影:roof 2・1 で暗い材質の区画がある、0 でない。ドームでは景色・月なし
#   ㉑ v2.2.f:フェンスの看板(ads 1・鏡 repeat.x=−1)・リボンビジョン(外野 2 階席があれば 2、なければ 1)・バックスクリーンのビジョン(512 px の絵)。勝敗を変えて updateMatchup すると絵が描き直される(球場はそのまま)。観戦の作り(ofFull)にも看板とビジョン(リボンなし)
#   ⑳ v2.2.c:ユニフォームの型(0〜3 を上書きして人を作る:縦縞・胸の帯は胴が絵(材質の配列)、ラグランは袖が暗い、つば別色はつばが帽子と違う色)
#   ⑲ v2.2.b:背景の野手にユニフォーム(部品 8 つ以上・帽子が本拠地のチームカラー)
#   ⑱ v2.2.a:ブルペン(型を強制して、ファウルゾーン型は投手・捕手 8(2 レーン×両側)と箱 0、フェンス裏型は 8 と箱 2)
#   ⑰ v2.1.z:内野席とファウルゾーンの席の内縁(hl3dBowlEdge)がひと続き(長さ 400 以上・両端はライン沿い・真ん中は本塁の後ろ)。背景の野手は .8 倍
#   ⑯ v2.1.y:地面の絵に芝の縞の印(__stripes)・バックネットの格子 1・待つ打者 2
#   ⑮ v2.1.x:型を強制して、フェンスの高さ(7/11)・外野 2 階席の有無・照明塔の本数(0→6・1→4・2→6)が合う
#   ⑭ v2.1.w:外野席の種類(型を 0 ベンチ/1 芝生/2 テラスに強制して、芝生の斜面(lawn)・テラスの低いフェンス(terrace)の有無が合う)
#   ⑬ v2.1.v:内野席の大屋根の数が hl3dParkLook の型(0 なし/1 部分/2 全面)と合い、屋根つきでは内野側の照明塔が屋根の上(y>50)。ドームでは大屋根なし。型は本拠地ごとに毎回同じ
#   ⑫ v2.1.u:ドームの本拠地では屋根(userData.k=domeRoof)があり照明塔(tower)がない。屋外では屋根なし・照明塔 6
#   ⑪ v2.1.r:観客の動きの設定(初めはあり=タオル・ウェーブ・旗。オフで止まり背景を作り直す。オンで戻る)
#   ⑩ v2.1.n:「ボードを隠す」でボードが消え(ボタンの位置は動かない)、試合を進めても隠したまま、「ボードを出す」で戻る。ボードの中に操作がある画面ではボタンなし
#   ⑨ v2.1.l:電光掲示板の飾り(枠・照明・支柱)がボードを囲む/明るい配色・デーゲームの球場で昼、ナイターで夜
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
URL, LOCAL, OUT = sys.argv[1], sys.argv[2], sys.argv[3]; os.makedirs(OUT, exist_ok=True)
os.environ["HL3D_LOCAL"]=LOCAL
from h3 import *
bad=0
def ok(n,c,x=""):
    global bad
    if not c: bad+=1
    print(("PASS " if c else "FAIL ")+n, str(x)[:300], flush=True)
ST="()=>({bg:!!document.querySelector('#p-game .hl3bgCard > .hl3dBg canvas'), on:!!document.querySelector('.hl3bgOn'), raf:!!(hl3dBgS&&hl3dBgS.raf), last:hl3dBgS? Math.round(hl3dBgS.last) : null, key:hl3dBgS? hl3dBgS.key : null, home:hl3dBgHome()})"
with sync_playwright() as p:
    br=p.chromium.launch()
    for w in (390,320,1366):
        pg=open_page3(br,URL,seed=7,w=w,h=844); create(pg,{"numTeams":"6"})
        pg.evaluate("()=>{ for(let i=0;i<20;i++) simScheduledGame(); updateMatchup(); }"); pg.click("#mainNav [data-p=game]"); pg.wait_for_timeout(1200)
        a=pg.evaluate(ST); pg.wait_for_timeout(400); a2=pg.evaluate(ST)
        ok(f"① {w}px 背景が入って動く", a["bg"] and a["on"] and a2["last"]!=a["last"] and a["key"].startswith(a["home"]+"|"), [a,a2["last"]])
        box=pg.evaluate("()=>{ const b=document.getElementById('simBtn').getBoundingClientRect(); return [b.x+b.width/2,b.y+b.height/2]; }")
        top=pg.evaluate("([x,y])=>{ const e=document.elementFromPoint(x,y); return e && (e.id||e.className); }",box)
        ok(f"⑧ {w}px ボタンが前にある", top=="simBtn", top)
        pg.screenshot(path=f"{OUT}/bg_{w}.png")
        sb=pg.evaluate("""()=>{ const d=document.querySelector('#p-game .hl3sb'), m=document.getElementById('matchup'); if(!d) return null; const f=d.querySelector('.sbFrame').getBoundingClientRect(), r=m.getBoundingClientRect(), l=[...d.querySelectorAll('.sbLamp')].map(e=>e.getBoundingClientRect());
          return {around: f.left<=r.left && f.right>=r.right && f.top<=r.top && f.bottom>=r.bottom, lamps: l.every(q=>q.bottom<=r.top+2), n:d.children.length}; }""")
        ok(f"⑨ {w}px 電光掲示板の飾り", sb and sb["around"] and sb["lamps"] and sb["n"]==5, sb)
        y0=pg.evaluate("()=>document.getElementById('simBtn').getBoundingClientRect().top")
        pg.click(".hl3sbBtn"); pg.wait_for_timeout(500); y1=pg.evaluate("()=>document.getElementById('simBtn').getBoundingClientRect().top")
        t1=pg.evaluate("()=>[document.querySelector('.hl3bgCard').classList.contains('hl3sbHide'), getComputedStyle(document.getElementById('matchup')).visibility]")
        pg.click("#simBtn"); pg.wait_for_timeout(500); t2=pg.evaluate("()=>document.querySelector('.hl3bgCard').classList.contains('hl3sbHide')")
        pg.click(".hl3sbBtn"); pg.wait_for_timeout(300); t3=pg.evaluate("()=>[document.querySelector('.hl3bgCard').classList.contains('hl3sbHide'), getComputedStyle(document.getElementById('matchup')).visibility]")
        ok(f"⑩ {w}px ボードを隠す・出す", t1==[True,"hidden"] and abs(y0-y1)<1 and t2 and t3==[False,"visible"], [y0,y1,t1,t2,t3])
        if w==390:
            pg.click("#mainNav [data-p=lineup]"); pg.wait_for_timeout(700); b=pg.evaluate(ST); pg.wait_for_timeout(300); b2=pg.evaluate(ST)
            pg.click("#mainNav [data-p=game]"); pg.wait_for_timeout(1500); c=pg.evaluate(ST)
            ok("② ほかのタブでは止まり、戻ると動く", (not b["raf"]) and b2["last"]==b["last"] and c["raf"] and c["last"]!=b["last"], [b,b2["last"],c])
            pg.evaluate("()=>{ while(gameIdx<schedule.length){ const g=schedule[gameIdx]; if(g[0]===myTeam||g[1]===myTeam) break; simScheduledGame(); } updateMatchup(); }")
            pg.evaluate("()=>{ setManageMode(false); playNextGameHighlight(); }"); pg.wait_for_timeout(900); d=pg.evaluate(ST); pg.wait_for_timeout(300); d2=pg.evaluate(ST)
            pg.evaluate("()=>{ try{ skipHighlights(); }catch(e){} try{ closeHighlights(); }catch(e){} }"); pg.wait_for_timeout(1600); e=pg.evaluate(ST)
            ok("③ 観戦の窓では止まり、閉じると動く", (not d["raf"]) and d2["last"]==d["last"] and e["raf"], [d,d2["last"],e])
            m0=pg.evaluate("()=>[HL3D_BG_MOTION, document.getElementById('hl3dCrowdChk').checked]")
            pg.evaluate("()=>setHl3dCrowd(false)"); pg.wait_for_timeout(600); m1=pg.evaluate("()=>[HL3D_BG_MOTION, document.getElementById('hl3dCrowdChk').checked, localStorage.getItem('pennantHl3dCrowd'), hl3dBgS&&hl3dBgS.fx.sectors.every(me=>me.position.y===0)]")
            pg.evaluate("()=>setHl3dCrowd(true)"); pg.wait_for_timeout(600); m2=pg.evaluate("()=>[HL3D_BG_MOTION, document.getElementById('hl3dCrowdChk').checked]")
            ok("⑪ 観客の動きの設定", m0==["towel wave flags",True] and m1==["off",False,"off",True] and m2==["towel wave flags",True], [m0,m1,m2])
            CNT="()=>{ const c={domeRoof:0,tower:0}; hl3dBgS.sc.traverse(o=>{ if(o.userData && o.userData.k in c) c[o.userData.k]++; }); return [c.domeRoof,c.tower,!!(hl3ParkOf(hl3dBgHome())||{}).dome]; }"
            r0=pg.evaluate(CNT); pg.evaluate("()=>{ const t=allTeamsEverywhere().find(x=>x.name===hl3dBgHome()); t.park=Object.assign(t.park||{},{turf:true,dome:true}); updateMatchup(); }"); pg.wait_for_timeout(700); r1=pg.evaluate(CNT)
            pg.evaluate("()=>{ const t=allTeamsEverywhere().find(x=>x.name===hl3dBgHome()); t.park.dome=false; updateMatchup(); }"); pg.wait_for_timeout(700); r2=pg.evaluate(CNT)
            ok("⑫ ドームの屋根", r1==[1,0,True] and r2==[0,6,False] and (r0[0]==1)==r0[2], [r0,r1,r2])
            RF="()=>{ let n=0, tw=[]; hl3dBgS.sc.traverse(o=>{ if(o.userData.k==='bigRoof') n++; if(o.userData.k==='tower') tw.push(Math.round(o.position.y)); }); const lk=hl3dParkLook(hl3dBgHome(),hl3ParkOf(hl3dBgHome())); return {n, roof:lk.roof, tw, same: JSON.stringify(lk)===JSON.stringify(hl3dParkLook(hl3dBgHome(),hl3ParkOf(hl3dBgHome())))}; }"
            q=pg.evaluate(RF); hi=sorted(q["tw"])[-2:]
            ok("⑬ 内野席の大屋根", q["same"] and q["n"]==(1 if q["roof"] else 0) and ((q["roof"]>0 and hi[0]>50) or (q["roof"]==0 and hi[-1]<=34)), q)
            pg.evaluate("()=>{ const t=allTeamsEverywhere().find(x=>x.name===hl3dBgHome()); t.park=Object.assign(t.park||{},{turf:true,dome:true}); updateMatchup(); }"); pg.wait_for_timeout(700); q2=pg.evaluate(RF)
            pg.evaluate("()=>{ const t=allTeamsEverywhere().find(x=>x.name===hl3dBgHome()); t.park.dome=false; updateMatchup(); }"); pg.wait_for_timeout(700)
            ok("⑬ ドームでは大屋根なし", q2["n"]==0 and q2["roof"]==0, q2)
            OFC="()=>{ const c={lawn:0,terrace:0}; hl3dBgS.sc.traverse(o=>{ if(o.userData.k in c) c[o.userData.k]++; }); return [c.lawn,c.terrace]; }"
            pg.evaluate("()=>{ window.hl3dParkLook0=hl3dParkLook; }"); ofr=[]
            for of in (0,1,2):
                pg.evaluate("(of)=>{ hl3dParkLook=(h,pk)=>Object.assign(hl3dParkLook0(h,pk),{of}); hl3dBgS.key=''; updateMatchup(); }",of); pg.wait_for_timeout(700); ofr.append(pg.evaluate(OFC))
            pg.evaluate("()=>{ hl3dParkLook=hl3dParkLook0; hl3dBgS.key=''; updateMatchup(); }"); pg.wait_for_timeout(700)
            ok("⑭ 外野席の種類", ofr==[[0,0],[1,0],[0,1]], ofr)
            XC="()=>{ const c={fence:null,deck2:0,tower:0}; hl3dBgS.sc.traverse(o=>{ if(o.userData.k==='fence') c.fence=o.userData.h; if(o.userData.k==='deck2') c.deck2++; if(o.userData.k==='tower') c.tower++; }); return [c.fence,c.deck2,c.tower]; }"
            xr=[]
            for lk in ({"fence":0,"deck2":0,"lights":0},{"fence":1,"deck2":1,"lights":1},{"fence":1,"deck2":1,"lights":2}):
                pg.evaluate("(lk)=>{ hl3dParkLook=(h,pk)=>Object.assign(hl3dParkLook0(h,pk),lk); hl3dBgS.key=''; updateMatchup(); }",lk); pg.wait_for_timeout(700); xr.append(pg.evaluate(XC))
            pg.evaluate("()=>{ hl3dParkLook=hl3dParkLook0; hl3dBgS.key=''; updateMatchup(); }"); pg.wait_for_timeout(700)
            ok("⑮ フェンス・外野 2 階席・照明塔", xr==[[7,0,6],[11,1,4],[11,1,6]], xr)
            pg.wait_for_timeout(600); yr=pg.evaluate("()=>{ const c={net:0,ondeck:0}; let st=null; hl3dBgS.sc.traverse(o=>{ if(o.userData.k in c) c[o.userData.k]++; if(o.isMesh && o.material.map && o.material.map.image && o.material.map.image.width===1200) st=!!o.material.map.__stripes; }); return [st,c.net,c.ondeck]; }")
            ok("⑯ 芝の縞・バックネットの格子・待つ打者", yr==[True,1,2], yr)
            zr=pg.evaluate("()=>{ const E=hl3dBowlEdge(40,55,200), a=E.at(0), m=E.at(.5), b=E.at(1); const sc=hl3dBgS.men.map(x=>+x.scale.x.toFixed(2)); return [Math.round(E.L), a.s>150, m.s===0 && Math.abs(Math.hypot(m.p[0],m.p[1])-55)<1, b.s>150, sc.every(v=>v===0.8)]; }")
            ok("⑰ ひと続きの器・小さい野手", zr[0]>400 and all(zr[1:]), zr)
            PC="()=>{ const c={pen:0,penBox:0}; hl3dBgS.sc.traverse(o=>{ if(o.userData.k in c) c[o.userData.k]++; }); return [c.pen,c.penBox]; }"
            pr=[]
            for pen in (1,0):
                pg.evaluate("(pen)=>{ hl3dParkLook=(h,pk)=>Object.assign(hl3dParkLook0(h,pk),{pen,of:0}); hl3dBgS.key=''; updateMatchup(); }",pen); pg.wait_for_timeout(700); pr.append(pg.evaluate(PC))
            pg.evaluate("()=>{ hl3dParkLook=hl3dParkLook0; hl3dBgS.key=''; updateMatchup(); }"); pg.wait_for_timeout(700)
            ok("⑱ ブルペン", pr==[[8,0],[8,2]], pr)
            ur=pg.evaluate("()=>{ const m=hl3dBgS.men[0], cols=new Set(); m.traverse(o=>{ if(o.isMesh) cols.add(o.material.color.getHexString()); }); return [m.children.length, cols.has(new THREE.Color(teamColorMap[hl3dBgHome()]).getHexString()), cols.has('f4f2ec')]; }")
            ok("⑲ ユニフォーム", ur[0]>=8 and ur[1] and ur[2], ur)
            us=pg.evaluate("""()=>{ const own=[], out=[]; for(let st=0;st<4;st++){ for(const ba of [0,1]){ const u=hl3dUniform(hl3dBgHome(),true,st,ba), m=hl3dMan(0,own,false,u); const kids=m.children.filter(c=>c.geometry);
                const body=kids.find(c=>c.geometry.type==='CylinderGeometry'&&c.geometry.parameters.height===6), brim=kids.find(c=>c.geometry.type==='BoxGeometry'), cap=kids.find(c=>c.geometry.type==='SphereGeometry'&&c.geometry.parameters.thetaLength<2);
                out.push([st,ba,Array.isArray(body.material),(u.sleeve!==u.trim),brim.material.color.getHex()!==cap.material.color.getHex()]); } } own.forEach(o=>{ try{ o.dispose(); }catch(e){} }); return out; }""")
            exp=[[0,0,False,False,False],[0,1,False,False,True],[1,0,True,False,False],[1,1,True,False,True],[2,0,False,True,False],[2,1,False,True,True],[3,0,True,False,False],[3,1,True,False,True]]
            ok("⑳ ユニフォームの型", us==exp, us)
            VC="()=>{ const c={ads:0,ribbon:0,vision:0,deck2:0}; let mir=null, vis=null; hl3dBgS.sc.traverse(o=>{ if(o.userData.k in c) c[o.userData.k]++; if(o.userData.k==='ads') mir=o.material.map.repeat.x; if(o.userData.k==='vision') vis=o.material.map.image; }); return [c.ads,c.ribbon,c.vision,c.deck2,mir,vis? vis.width : 0, hl3dBgS.fx.vision.j]; }"
            v0=pg.evaluate(VC)
            pg.evaluate("()=>{ const t=allTeamsEverywhere().find(x=>x.name===hl3dBgHome()); t.w+=7; updateMatchup(); }"); pg.wait_for_timeout(300); v1=pg.evaluate(VC)
            pg.evaluate("()=>{ const t=allTeamsEverywhere().find(x=>x.name===hl3dBgHome()); t.w-=7; updateMatchup(); }"); pg.wait_for_timeout(300)
            vs=pg.evaluate("""()=>{ const own=[], sc=new THREE.Scene(), hn=hl3dBgHome(), vi=hl3dVisionMake(hl3dVisionInfo(hn,hl3dBgAway())); hl3dParkMeshes(sc,own,hl3ParkOf(hn),hn,{ofFull:true, vision:vi});
                const c={ads:0,ribbon:0,vision:0}; sc.traverse(o=>{ if(o.userData.k in c) c[o.userData.k]++; }); own.forEach(o=>{ try{ o.dispose(); }catch(e){} }); return [c.ads,c.ribbon,c.vision]; }""")
            SC="()=>{ const c={scenery:0,farGround:0,moon:0,stars:0}; let n=0, sh=0; hl3dBgS.sc.traverse(o=>{ if(o.userData.k in c) c[o.userData.k]++; if(o.userData.k==='stars') n=o.geometry.attributes.position.count; if(o.isMesh && o.material.userData && o.material.userData.shade) sh++; }); return [c.scenery,c.farGround,c.moon,n,sh,hl3dBgS.day]; }"
            sr=[]
            for lk in ({"scene":0,"roof":2},{"scene":1,"roof":1},{"scene":2,"roof":0}):
                pg.evaluate("(lk)=>{ hl3dParkLook=(h,pk)=>Object.assign(hl3dParkLook0(h,pk),lk); hl3dBgS.key=''; updateMatchup(); }",lk); pg.wait_for_timeout(700); sr.append(pg.evaluate(SC))
            pg.evaluate("()=>{ const t=allTeamsEverywhere().find(x=>x.name===hl3dBgHome()); t.park=Object.assign(t.park||{},{turf:true,dome:true}); hl3dParkLook=hl3dParkLook0; hl3dBgS.key=''; updateMatchup(); }"); pg.wait_for_timeout(700); sd=pg.evaluate(SC)
            pg.evaluate("()=>{ const t=allTeamsEverywhere().find(x=>x.name===hl3dBgHome()); t.park.dome=false; hl3dBgS.key=''; updateMatchup(); }"); pg.wait_for_timeout(700)
            pg.evaluate("()=>{ hl3dParkLook=(h,pk)=>Object.assign(hl3dParkLook0(h,pk),{pen:0,of:0,fence:0}); hl3dBgS.key=''; updateMatchup(); }"); pg.wait_for_timeout(900)
            gi=pg.evaluate("""()=>{ let wh=null, gr=null; hl3dBgS.sc.traverse(o=>{ if(o.userData.k==='penBox'){ const sib=o.parent.children[o.parent.children.indexOf(o)+1]; const P=sib.geometry.attributes.position.array; let m=0; for(let i=1;i<P.length;i+=3) m=Math.max(m,P[i]); wh=+m.toFixed(1); } });
                const g=hl3dBgS.fx.ground; return [wh, g? g.type : null, g? g.color.getHexString() : null]; }""")
            pg.evaluate("()=>{ hl3dParkLook=hl3dParkLook0; hl3dBgS.key=''; updateMatchup(); }"); pg.wait_for_timeout(700)
            pg.evaluate("()=>{ hl3dBgTilt=0; }"); r=pg.evaluate("()=>{ const c=document.querySelector('.hl3bgCard').getBoundingClientRect(); return [c.left+c.width/2-120, c.top+20]; }")
            pg.mouse.move(r[0],r[1]); pg.mouse.down(); pg.mouse.move(r[0],r[1]+80,steps=5); pg.mouse.up(); pg.wait_for_timeout(200); td=pg.evaluate("()=>hl3dBgTilt")
            pg.mouse.move(r[0],r[1]+80); pg.mouse.down(); pg.mouse.move(r[0],r[1]-300,steps=5); pg.mouse.up(); pg.wait_for_timeout(200); tu=pg.evaluate("()=>hl3dBgTilt")
            bb=pg.evaluate("()=>{ const b=document.getElementById('simBtn').getBoundingClientRect(); return [b.left+b.width/2,b.top+b.height/2]; }")
            pg.mouse.move(bb[0],bb[1]); pg.mouse.down(); pg.mouse.move(bb[0],bb[1]-60,steps=4); pg.mouse.up(); pg.wait_for_timeout(200); tb=pg.evaluate("()=>hl3dBgTilt")
            gi0=pg.evaluate("()=>gameIdx"); pg.click("#simBtn"); pg.wait_for_timeout(600); gi1=pg.evaluate("()=>gameIdx")
            of=pg.evaluate("()=>{ const WD=hl3dWide(hl3ParkOf(hl3dBgHome()).R), ks=Object.keys(HL_POS).filter(k=>k!=='投'); return ks.map((k,i)=>{ const m=hl3dBgS.men[i], r=Math.hypot(m.position.x,m.position.z); return [k, +(r/WD.Rf(HL_POS[k][0])).toFixed(2)]; }); }")
            pg.evaluate("()=>{ hl3dBgTilt=0; hl3dBgKick(); }")
            ex=pg.evaluate("()=>{ let red=0, ppl=0; hl3dBgS.sc.traverse(o=>{ if(o.userData.k==='excite') red++; }); hl3dBgS.fx.sectors.forEach(me=>{ const P=me.geometry.attributes.position.array; let mx=0; for(let i=1;i<P.length;i+=3) mx=Math.max(mx,P[i]); if(mx<6 && mx>2.5) ppl++; }); return [red,ppl]; }")
            ok("㉕ エキサイトシートの観客", ex[0]==2 and ex[1]>=2, ex)
            ok("㉔ 上下のドラッグ・外野手 75%", td>0.05 and tu==-0.35 and tb==tu and gi1>gi0 and all((v==0.75) == (k in "左中右") for k,v in of), [td,tu,tb,gi0,gi1,of])
            ok("㉓ フェンス裏のブルペンの壁・外の地面の色", gi[0]==7.5 and gi[1]=="MeshBasicMaterial" and gi[2] not in (None,"2a5534"), gi)
            ok("㉒ 外の景色・月・星・屋根の影", all(r[0]==1 and r[1]==1 and r[2]==2 and r[3]==240 and not r[5] for r in sr) and sr[0][4]>0 and sr[1][4]>0 and sr[2][4]==0 and sd[0]==0 and sd[1]==0 and sd[2]==0, [sr,sd])
            ok("㉑ 看板・リボンビジョン・ビジョン", v0[0]==1 and v0[1]==(2 if v0[3] else 1) and v0[2]==1 and v0[4]==-1 and v0[5]==512 and v1[6]!=v0[6] and v1[0]==1 and vs==[1,0,1], [v0,v1,vs])
            pg.evaluate("()=>setHl3dBg(false)"); pg.wait_for_timeout(300); f=pg.evaluate(ST)
            pg.evaluate("()=>setHl3dBg(true)"); pg.wait_for_timeout(900); g=pg.evaluate(ST)
            ok("④ 設定でオフ・オン", (not f["bg"]) and (not f["on"]) and g["bg"] and g["on"], [f,g])
            pg.evaluate("()=>setHl3d('on')"); pg.wait_for_timeout(300); h=pg.evaluate(ST)
            pg.evaluate("()=>setHl3d('3d')"); pg.wait_for_timeout(900); h2=pg.evaluate(ST)
            ok("⑤ 立体「あり」では背景なし(3D に戻すと出る)", (not h["bg"]) and h2["bg"], [h,h2])
            dn=[]
            for st,pal in (("board","day"),("ballpark","dayPark"),("night","nightGame"),("board","default")):
                pg.evaluate("([st,pal])=>{ document.documentElement.dataset.style=st; applyThemePreset(pal); ensureContrast(); updateMatchup(); }",[st,pal]); pg.wait_for_timeout(700)
                dn.append(pg.evaluate("()=>hl3dBgS? hl3dBgS.day : null"))
            ok("⑨ 昼・夜(明るい配色・デーゲーム=昼/ナイター・ふつう=夜)", dn==[True,True,False,False], dn)
            pg.evaluate(SEASON); pg.evaluate("()=>{ try{ startPostseason(); }catch(e){} for(let k=0;k<20 && post && post.active;k++){ try{ simPostGame&&simPostGame(false); }catch(e){ break; } } updateMatchup(); }"); pg.wait_for_timeout(900)
            k=pg.evaluate(ST); pg.screenshot(path=f"{OUT}/bg_off.png")
            pg.evaluate("()=>{ hl3dSbHidden=true; hl3dSbBtnSync(); }")
            nb=pg.evaluate("()=>{ const b=document.querySelector('.hl3sbBtn'), m=document.getElementById('matchup'); return {mside:!!m.querySelector('.mSide'), btn: b? getComputedStyle(b).display : null, hide:document.querySelector('.hl3bgCard').classList.contains('hl3sbHide')}; }")
            ok("⑩ ふつうの試合でない画面ではボタンなし・ボードは出る", nb["mside"] or (nb["btn"]=="none" and not nb["hide"]), nb)
            pg.evaluate("()=>{ hl3dSbHidden=false; hl3dSbBtnSync(); }")
            ok("⑥ シーズンのあと", (not pg.errs) and (k["home"] is not None), [k,pg.errs[:2]])
        ok(f"エラーなし {w}px", not pg.errs, pg.errs[:3]); pg.context.close()
    os.environ["HL3D_FAIL"]="1"
    pg=open_page3(br,URL,seed=7,w=390,h=844); create(pg,{"numTeams":"6"}); pg.click("#mainNav [data-p=game]"); pg.wait_for_timeout(1500)
    m=pg.evaluate(ST); ok("⑦ 3D が読めないときは背景なし", (not m["bg"]) and (not m["on"]) and not pg.errs, [m,pg.errs[:2]]); pg.context.close()
    del os.environ["HL3D_FAIL"]
    print("NG",bad); br.close()
