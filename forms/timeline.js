/* timeline.js — Hunter's life as a single line that holds its length.
   The kinhin loop (the walked ground) is resampled to N arc-length-even points;
   the SAME points morph into a ring (circumference = loop length), a horizontal
   line, or a vertical column — a pure bend, never a stretch. Events ride the
   shape by year; a host can drive it via postMessage (shape:…). */
(function(){
  const TL=window.TL, SITE=window.SITE, G=SITE.G;
  // Timeline-local thread recolour: fold the gold "House" and the candy-blue
  // "Writing" into the archive's warm register, leaving the shared data file
  // (and the 3D site map that also reads it) untouched. Life/Practice/Zen/Art
  // already use Verso tokens, so they pass through unchanged.
  const THREAD_TINT={ house:'#b08145', writing:'#7c889e' };
  const TH={}; for(const k in TL.threads){ TH[k]=Object.assign({},TL.threads[k], THREAD_TINT[k]?{color:THREAD_TINT[k]}:{}); }
  // Parse a source string into a collection abbrev (terracotta stamp) + ref.
  // Only true archive items (HH-COLL-NNNN or CAA accessions) earn the stamp;
  // everything else (finding-aid refs, Wikidata) reads as quiet provenance.
  function srcMeta(e){ const s=(e.src||'').trim(); let coll=null; const m=s.match(/^HH-([A-Z]+)-/i);
    if(m) coll=m[1].toUpperCase(); else if(/^CAA\b/i.test(s)) coll='CAA';
    return { coll, ref:s, archive:!!coll||!!e.archive }; }
  const SPAN=TL.span, Y0=SPAN[0], Y1=SPAN[1];
  const N=240;                       // sample count around the loop
  const svg=document.getElementById('tl');
  const elShape=document.getElementById('shape'), elClosure=document.getElementById('closure');
  const gEvents=document.getElementById('events'), gTicks=document.getElementById('ticks'),
        gRanges=document.getElementById('ranges'), gLabels=document.getElementById('labels');
  const NS='http://www.w3.org/2000/svg';
  const elBg=document.getElementById('bg');

  // ---------- sample the kinhin loop, resample arc-length-even, normalise ----------
  function samplePath(d,step){ const p=document.createElementNS(NS,'path'); p.setAttribute('d',d);
    const L=p.getTotalLength(); const out=[]; for(let s=0;s<=L;s+=step){const q=p.getPointAtLength(s);out.push([q.x,q.y]);} return out; }
  function resample(pts,n,closed){ // even arc-length to n points
    const cum=[0]; for(let i=1;i<pts.length;i++)cum.push(cum[i-1]+Math.hypot(pts[i][0]-pts[i-1][0],pts[i][1]-pts[i-1][1]));
    const L=cum[cum.length-1]; const out=[];
    for(let k=0;k<n;k++){ const s=L*(k/(closed?n:(n-1))); let i=1; while(i<cum.length&&cum[i]<s)i++;
      const a=pts[i-1],b=pts[Math.min(i,pts.length-1)],seg=(cum[i]||L)-cum[i-1]||1,t=(s-cum[i-1])/seg;
      out.push([a[0]+(b[0]-a[0])*t, a[1]+(b[1]-a[1])*t]); }
    return {pts:out, len:L}; }
  const raw=samplePath(G.kinhin, 4);
  const rs=resample(raw, N, true);
  // centre + scale so perimeter = 1
  let cx=0,cy=0; rs.pts.forEach(p=>{cx+=p[0];cy+=p[1];}); cx/=N; cy/=N;
  const UL=1;                          // unit perimeter
  const k=UL/rs.len;
  let trail=rs.pts.map(p=>[(p[0]-cx)*k, (p[1]-cy)*k]);

  // ---------- the four shapes (all perimeter = UL) ----------
  const R=UL/(2*Math.PI);
  const ring=[], line=[], column=[];
  for(let i=0;i<N;i++){ const t=i/N, a=-Math.PI/2 + t*2*Math.PI;       // start at top, clockwise
    ring.push([R*Math.cos(a), R*Math.sin(a)]); }
  for(let i=0;i<N;i++){ const t=i/(N-1);
    line.push([(t-0.5)*UL, 0]);
    column.push([0,(t-0.5)*UL]); }
  // align the trail's winding + phase to the ring so morphs are a clean bend, never a flip
  (function(){ const area=p=>{let a=0;for(let i=0;i<p.length;i++){const q=p[(i+1)%p.length];a+=p[i][0]*q[1]-q[0]*p[i][1];}return a;};
    if(Math.sign(area(trail))!==Math.sign(area(ring))) trail.reverse();
    let bestK=0,bestD=Infinity; for(let kk=0;kk<N;kk++){ let d=0; for(let i=0;i<N;i+=6){ const a=trail[(i+kk)%N],b=ring[i]; d+=(a[0]-b[0])*(a[0]-b[0])+(a[1]-b[1])*(a[1]-b[1]); } if(d<bestD){bestD=d;bestK=kk;} }
    if(bestK) trail=trail.slice(bestK).concat(trail.slice(0,bestK)); })();
  const SHAPES={trail, ring, line, column};
  const CLOSED={trail:1, ring:1, line:0, column:0};

  // ---------- morph state ----------
  let fromS=trail.map(p=>p.slice()), toS=ring, cur=trail.map(p=>p.slice());
  let morph=1, fromClosed=1, toClosed=1, t0=0, DUR=1300, animing=false, shapeName='ring';
  const ease=t=>t<.5?4*t*t*t:1-Math.pow(-2*t+2,3)/2;
  function goShape(name){ if(!SHAPES[name]||name===shapeName&&morph>=1)return;
    fromS=cur.map(p=>p.slice()); toS=SHAPES[name];
    fromClosed=lerpClosed(); toClosed=CLOSED[name];
    morph=0; t0=performance.now(); shapeName=name; animing=true;
    [...document.querySelectorAll('#modes button')].forEach(b=>b.classList.toggle('on',b.dataset.shape===name));
    requestAnimationFrame(loop); }
  function lerpClosed(){ return fromClosed+(toClosed-fromClosed)*ease(Math.min(1,morph)); }

  // ---------- fit transform (uniform; keeps slick bend, always on-screen) ----------
  let W=0,H=0;
  function resize(){ W=innerWidth; H=innerHeight; svg.setAttribute('viewBox',`0 0 ${W} ${H}`); }
  addEventListener('resize',()=>{ resize(); draw(); });
  resize();
  function fit(pts){ let minx=1e9,miny=1e9,maxx=-1e9,maxy=-1e9;
    for(const p of pts){ if(p[0]<minx)minx=p[0]; if(p[0]>maxx)maxx=p[0]; if(p[1]<miny)miny=p[1]; if(p[1]>maxy)maxy=p[1]; }
    const bw=Math.max(maxx-minx,1e-3), bh=Math.max(maxy-miny,1e-3);
    const PADX=258, PADY=120;   // PADX clears the 212px margin columns (+26 inset) so the shape sits between them
    const s=Math.min((W-2*PADX)/bw, (H-2*PADY)/bh);
    const ox=W/2 - s*(minx+maxx)/2, oy=H/2 - s*(miny+maxy)/2;
    return {s,ox,oy}; }
  const SX=(p,f)=>p[0]*f.s+f.ox, SY=(p,f)=>p[1]*f.s+f.oy;

  // ---------- events ----------
  const EVENTS=TL.events.slice().sort((a,b)=>a.y-b.y);
  EVENTS.forEach((e,i)=>{ e.id=i; });   // stable id = sorted index (the data carries none)
  const tOf=y=>Math.max(0,Math.min(1,(y-Y0)/(Y1-Y0)));
  function ptAtT(t,scr){ const f=t*(N-1); let i=Math.floor(f); if(i>=N-1)i=N-2; const fr=f-i;
    return [scr[i][0]+(scr[i+1][0]-scr[i][0])*fr, scr[i][1]+(scr[i+1][1]-scr[i][1])*fr]; }
  const threadOn={}; TL.order.forEach(k=>threadOn[k]=true);
  let selId=null;

  // build event DOM once
  const evEls=EVENTS.map(e=>{ const c=TH[e.thread].color;
    let range=null;
    if(e.y2 && e.y2>e.y){ range=document.createElementNS(NS,'path'); range.setAttribute('class','ev-range'); range.setAttribute('stroke',c); gRanges.appendChild(range); }
    const dot=document.createElementNS(NS,'circle'); dot.setAttribute('class','ev-dot'+(e.key?' key':'')); dot.setAttribute('r',e.key?5:4); dot.setAttribute('fill',c);
    dot.addEventListener('click',ev=>{ev.stopPropagation();select(e.id);});
    dot.addEventListener('mouseenter',()=>{ if(selId==null)showLabel(e.id,true); });
    dot.addEventListener('mouseleave',()=>{ if(selId!==e.id)showLabel(e.id,false); });
    gEvents.appendChild(dot);
    const lab=document.createElementNS(NS,'text'); lab.setAttribute('class','ev-lab'); lab.textContent=e.short||e.title; gLabels.appendChild(lab);
    return {e,dot,range,lab,c}; });

  // decade ticks
  const ticks=[]; for(let y=1930;y<=2020;y+=10){ const ln=document.createElementNS(NS,'line'); ln.setAttribute('class','tick-line'); gTicks.appendChild(ln);
    const tx=document.createElementNS(NS,'text'); tx.setAttribute('class','tick-txt'); tx.setAttribute('text-anchor','middle'); tx.textContent="'"+String(y).slice(2); gTicks.appendChild(tx);
    ticks.push({y,ln,tx}); }

  function showLabel(id,on){ const it=evEls[id]; if(it)it.lab.classList.toggle('show',on); }

  // ---------- two-column entry index ----------
  // All events lifted into two reading columns (earlier years left, later
  // right). Each entry links to its dot both ways; selecting expands the note
  // inline. Independent of the active shape — the columns are fixed chrome.
  const cols=document.getElementById('tl-cols'),
        colL=document.getElementById('tl-col-l'), colR=document.getElementById('tl-col-r');
  const mid=Math.ceil(EVENTS.length/2);
  // compact column stamp: a year or a short range ("1970–73"); the full date
  // (e.date, e.g. "4 November 1930") is reserved for the expanded detail.
  const shortYr=e=>e.y2?(e.y+'–'+String(e.y2).slice(-2)):(''+e.y);
  EVENTS.forEach((e,i)=>{ const th=TH[e.thread]; const it=evEls[i];
    const row=document.createElement('div'); row.className='tl-entry'; row.dataset.i=i;
    row.tabIndex=0; row.setAttribute('role','button'); row.style.color=th.color;
    const sm=srcMeta(e); const placeOk=e.place&&e.place!=='—';
    const kv=[];
    if(placeOk) kv.push('<div class="row"><span class="k2">place</span><span class="v">'+e.place+'</span></div>');
    if(sm.ref) kv.push('<div class="row"><span class="k2">source</span><span class="v'+(sm.coll?' archid':'')+'">'+sm.ref+'</span></div>');
    const foot=kv.length?('<div class="ev-kv">'+kv.join('')+'</div>'):'';
    row.innerHTML='<span class="te-yr"><i class="te-dot"></i>'+shortYr(e)+'</span>'+
      '<span class="te-ti">'+(e.short||e.title)+'</span>'+
      '<div class="tl-detail">'+
        '<div class="te-k"><span style="color:'+th.color+'">'+th.label+'</span> · '+(e.date||e.y)+'</div>'+
        '<h3>'+(e.title||e.short)+'</h3>'+
        (e.note?'<p>'+e.note+'</p>':'')+foot+'</div>';
    const toggle=()=>{ (selId===i)?deselect():select(i); };
    row.addEventListener('click',ev=>{ ev.stopPropagation(); toggle(); });
    row.addEventListener('keydown',ev=>{ if(ev.key==='Enter'||ev.key===' '){ ev.preventDefault(); toggle(); } });
    row.addEventListener('mouseenter',()=>{ if(selId==null){ showLabel(i,true); it.dot.classList.add('hl'); } });
    row.addEventListener('mouseleave',()=>{ if(selId!==i){ showLabel(i,false); it.dot.classList.remove('hl'); } });
    // two-way: hovering the dot lights its entry
    it.dot.addEventListener('mouseenter',()=>{ if(selId==null)row.classList.add('hl'); });
    it.dot.addEventListener('mouseleave',()=>{ if(selId!==i)row.classList.remove('hl'); });
    (i<mid?colL:colR).appendChild(row);
    it.entry=row;
  });

  // ---------- draw ----------
  // scrOverride: explicit screen-space points (used by the kinhin hand-off so the
  // line can start at the map's exact pixels). clOverride: closure amount 0..1.
  function draw(scrOverride, clOverride){
    let scr;
    if(scrOverride){ scr=scrOverride; }
    else { const f=fit(cur); scr=cur.map(p=>[p[0]*f.s+f.ox, p[1]*f.s+f.oy]); }
    // shape path
    let d=''; for(let i=0;i<N;i++){ d+=(i?'L':'M')+scr[i][0].toFixed(1)+' '+scr[i][1].toFixed(1); }
    elShape.setAttribute('d', d);
    // closure segment (fades as it unrolls)
    const cl=(clOverride!=null)?clOverride:lerpClosed();
    if(cl>0.01){ elClosure.style.display=''; elClosure.style.opacity=(0.5*cl).toFixed(2);
      elClosure.setAttribute('d','M'+scr[N-1][0].toFixed(1)+' '+scr[N-1][1].toFixed(1)+'L'+scr[0][0].toFixed(1)+' '+scr[0][1].toFixed(1)); }
    else elClosure.style.display='none';
    const ccx=W/2, ccy=H/2;
    // events
    for(const it of evEls){ const e=it.e; const on=threadOn[e.thread];
      const p=ptAtT(tOf(e.y),scr), sx=p[0], sy=p[1];
      it.dot.setAttribute('cx',sx.toFixed(1)); it.dot.setAttribute('cy',sy.toFixed(1));
      it.dot.style.display=on?'':'none';
      if(it.range){ if(on){ it.range.style.display=''; let rd=''; const i1=Math.max(0,Math.floor(tOf(e.y)*(N-1))), i2=Math.min(N-1,Math.ceil(tOf(e.y2)*(N-1)));
          for(let i=i1;i<=i2;i++){ rd+=(i===i1?'M':'L')+scr[i][0].toFixed(1)+' '+scr[i][1].toFixed(1); } it.range.setAttribute('d',rd); }
        else it.range.style.display='none'; }
      if(it.lab.classList.contains('show')||selId===e.id){ let nx=sx-ccx, ny=sy-ccy; const nl=Math.hypot(nx,ny)||1; nx/=nl; ny/=nl;
        it.lab.setAttribute('x',(sx+nx*14).toFixed(1)); it.lab.setAttribute('y',(sy+ny*14+3).toFixed(1));
        it.lab.setAttribute('text-anchor', nx<-0.3?'end':(nx>0.3?'start':'middle')); }
    }
    // decade ticks along outward normal
    for(const tk of ticks){ const p=ptAtT(tOf(tk.y),scr), sx=p[0],sy=p[1]; let nx=sx-ccx,ny=sy-ccy; const nl=Math.hypot(nx,ny)||1; nx/=nl;ny/=nl;
      tk.ln.setAttribute('x1',sx.toFixed(1)); tk.ln.setAttribute('y1',sy.toFixed(1)); tk.ln.setAttribute('x2',(sx+nx*9).toFixed(1)); tk.ln.setAttribute('y2',(sy+ny*9).toFixed(1));
      tk.tx.setAttribute('x',(sx+nx*22).toFixed(1)); tk.tx.setAttribute('y',(sy+ny*22+3).toFixed(1)); }
  }

  function loop(now){ if(!animing)return; morph=Math.min(1,(now-t0)/DUR); const e=ease(morph);
    for(let i=0;i<N;i++){ cur[i][0]=fromS[i][0]+(toS[i][0]-fromS[i][0])*e; cur[i][1]=fromS[i][1]+(toS[i][1]-fromS[i][1])*e; }
    fromClosed_cur=fromClosed+(toClosed-fromClosed)*e;
    draw();
    if(morph<1)requestAnimationFrame(loop); else { animing=false; } }
  let fromClosed_cur=1;
  // override lerpClosed to use the eased value during/after morph
  // (re-defined cleanly)
  // ---------- kinhin hand-off: the map sends the trail's exact on-screen points;
  // we draw the line right there, align its winding+phase to the ring, then morph
  // the SAME line into the circle. One continuous element — no crossfade match. ----
  let introRAF=null;
  function area(p){ let a=0; for(let i=0;i<p.length;i++){ const q=p[(i+1)%p.length]; a+=p[i][0]*q[1]-q[0]*p[i][1]; } return a; }
  function alignScreen(src, ref){ let s=src.map(p=>p.slice());
    if(Math.sign(area(s))!==Math.sign(area(ref))) s.reverse();
    let bestK=0,bestD=Infinity; for(let kk=0;kk<N;kk++){ let dd=0; for(let i=0;i<N;i+=6){ const a=s[(i+kk)%N], b=ref[i]; dd+=(a[0]-b[0])*(a[0]-b[0])+(a[1]-b[1])*(a[1]-b[1]); } if(dd<bestD){bestD=dd;bestK=kk;} }
    if(bestK) s=s.slice(bestK).concat(s.slice(0,bestK)); return s; }
  function setExtras(v){ [gEvents,gRanges,gLabels,gTicks].forEach(g=>{ g.style.transition='opacity .55s ease'; g.style.opacity=v?'1':'0'; }); }
  function introFromScreen(pts, w, h){
    if(introRAF){ cancelAnimationFrame(introRAF); introRAF=null; }
    animing=false; deselect();
    const ax=W/(w||W), ay=H/(h||H);
    const scaled=pts.map(p=>[p[0]*ax, p[1]*ay]);
    const r=resample(scaled, N, true);
    const f=fit(ring); const ringScreen=ring.map(p=>[p[0]*f.s+f.ox, p[1]*f.s+f.oy]);
    const start=alignScreen(r.pts, ringScreen);
    // ring is the resting model, so the normal draw after intro lands pixel-identical
    cur=ring.map(p=>p.slice()); shapeName='ring'; morph=1; fromClosed=1; toClosed=1;
    [...document.querySelectorAll('#modes button')].forEach(b=>b.classList.toggle('on',b.dataset.shape==='ring'));
    setExtras(false); [gEvents,gRanges,gLabels,gTicks].forEach(g=>{ g.style.transition='none'; g.style.opacity='0'; });
    elShape.style.opacity='0.8'; elBg.style.opacity='1';   // opaque ground (the opaque map fades out ON TOP to reveal this)
    draw(start, 1);
    // ONE master motion, FRONT-LOADED (ease-out) so it starts the instant you click —
    // the loop grows + centres + rounds into the ring; line fades bright→resting;
    // events/ticks bloom in over the last stretch as the map finishes dissolving above.
    const introEase=t=>1-Math.pow(1-t,2.6);   // fast start, gentle settle — snappy off the click
    const DUR2=2400, T0=performance.now();
    (function step(now){
      let kk=Math.min(1,(now-T0)/DUR2); const e=introEase(kk);
      const interp=start.map((p,i)=>[p[0]+(ringScreen[i][0]-p[0])*e, p[1]+(ringScreen[i][1]-p[1])*e]);
      elShape.style.opacity=(0.8-0.3*e).toFixed(2);
      const ext=Math.max(0,Math.min(1,(kk-0.5)/0.42));   // extras overlap the tail of the round
      [gEvents,gRanges,gLabels,gTicks].forEach(g=>g.style.opacity=ext.toFixed(2));
      draw(interp, 1);
      if(kk<1) introRAF=requestAnimationFrame(step);
      else { introRAF=null; elShape.style.opacity=''; setExtras(true); draw(); }   // resume model-based draw (== ringScreen)
    })(performance.now());
  }

  // ---------- selection ----------
  // The two-column index is the detail surface now: selecting lights the dot +
  // label on the shape, highlights the entry, expands its note inline, and dims
  // the rest. (The old floating caption-card is retired — see .card display:none.)
  const hint=document.getElementById('hint');
  function select(id){ const it=evEls[id]; if(!it)return; selId=id;
    evEls.forEach(x=>{ x.dot.classList.toggle('sel',x.e.id===id); x.dot.classList.remove('hl');
      x.lab.classList.toggle('show',x.e.id===id);
      if(x.entry){ x.entry.classList.toggle('sel',x.e.id===id); x.entry.classList.remove('hl'); } });
    if(cols)cols.classList.add('has-sel');
    if(it.entry)it.entry.scrollIntoView({block:'nearest',behavior:'smooth'});
    if(hint)hint.style.opacity='0'; draw(); }
  function deselect(){ selId=null;
    evEls.forEach(it=>{ it.dot.classList.remove('sel','hl'); it.lab.classList.remove('show');
      if(it.entry)it.entry.classList.remove('sel','hl'); });
    if(cols)cols.classList.remove('has-sel');
    if(hint)hint.style.opacity=''; draw(); }
  svg.addEventListener('click',()=>{ if(selId!=null)deselect(); });

  // ---------- legend (thread filter) ----------
  const legend=document.getElementById('legend');
  TL.order.forEach(key=>{ const th=TH[key]; const row=document.createElement('div'); row.className='lg';
    row.innerHTML='<b>'+th.label+'</b><i style="background:'+th.color+'"></i>';
    row.addEventListener('click',()=>{ threadOn[key]=!threadOn[key]; row.classList.toggle('off',!threadOn[key]); draw(); });
    legend.appendChild(row); });

  // ---------- controls ----------
  document.querySelectorAll('#modes button').forEach(b=>b.addEventListener('click',()=>goShape(b.dataset.shape)));
  addEventListener('message',e=>{ const d=e&&e.data; if(d&&typeof d==='object'){
    if(d.type==='tl-shape')goShape(d.shape);
    else if(d.type==='kinhin-handoff'){ introFromScreen(d.pts, d.w, d.h); }
    else if(d.type==='tl-reset'){ if(introRAF){cancelAnimationFrame(introRAF);introRAF=null;} elBg.style.opacity='1'; setExtras(true); elShape.style.opacity=''; deselect(); animing=false; cur=ring.map(p=>p.slice()); fromClosed=1; toClosed=1; morph=1; shapeName='ring'; draw(); } } });

  // ---------- open: embedded rests at the ring; standalone plays the trail → ring intro ----------
  window.__tl={ goShape, select, deselect, introFromScreen };
  const EMBED = window.parent!==window;
  if(EMBED){
    cur=ring.map(p=>p.slice()); fromClosed=1; toClosed=1; morph=1; shapeName='ring';
    draw();
  } else {
    // standalone preview: ?shape=ring|line|column rests directly in that shape
    // (skips the trail intro); ?pick=N pre-selects an entry. The host drives
    // shape via postMessage, so this only affects direct/standalone viewing.
    const sp=new URLSearchParams(location.search), wantShape=sp.get('shape');
    cur=trail.map(p=>p.slice()); fromClosed=1; toClosed=1; shapeName='trail';
    draw();
    if(wantShape && SHAPES[wantShape]){
      cur=SHAPES[wantShape].map(p=>p.slice()); fromClosed=CLOSED[wantShape]; toClosed=CLOSED[wantShape]; morph=1; shapeName=wantShape;
      [...document.querySelectorAll('#modes button')].forEach(b=>b.classList.toggle('on',b.dataset.shape===wantShape));
      draw();
    } else setTimeout(()=>goShape('ring'), 480);
    const pick=sp.get('pick'); if(pick!=null && evEls[+pick]) setTimeout(()=>select(+pick), wantShape?80:1900);
  }
})();
