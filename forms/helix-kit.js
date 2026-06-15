/* helix-kit.js — shared behaviour: colours, the detail card (verbatim
   from the helix), and a bead placer for HTML overlays. Reads window.TL. */
window.HK = (function(){
  const TL = window.TL;
  const col = e => e.track==='house' ? '#c9a44e' : (TL.threads[e.thread] ? TL.threads[e.thread].color : '#f0ede6');
  const dateOf = e => e.date || (e.y2!=null ? e.y+'–'+String(e.y2).slice(2) : String(e.y));
  const kindOf = e => e.kind || (e.track==='house' ? 'HUNTER HOUSE' : (TL.threads[e.thread] ? TL.threads[e.thread].label.toUpperCase() : ''));

  function makeDetail(detailEl){
    let selEl=null;
    function deselect(){
      if(selEl){ selEl.classList.remove('sel'); if(selEl._lab) selEl._lab.classList.remove('hot'); selEl=null; }
      detailEl.classList.remove('show');
    }
    function select(e, markEl){
      deselect();
      if(markEl){ markEl.classList.add('sel'); if(markEl._lab) markEl._lab.classList.add('hot'); selEl=markEl; }
      const c = e._c || col(e);
      const link = e.wd ? `<a href="https://www.wikidata.org/wiki/${e.wd}" target="_blank" rel="noopener">${e.src} ↗</a>`
                        : (e.src ? `<span>${e.src}</span>` : '');
      detailEl.innerHTML =
        `<button class="dx" aria-label="Close">×</button>`+
        `<div class="d-kind" style="color:${c}">${kindOf(e)}</div>`+
        `<div class="d-date">${dateOf(e)}${e.place && e.place!=='—' ? ' · '+e.place : ''}</div>`+
        `<div class="d-title">${e.title}</div>`+
        (e.note ? `<div class="d-note">${e.note}</div>` : '')+
        (e.src ? `<div class="d-src">Source · ${link}</div>` : '');
      detailEl.classList.add('show');
      detailEl.querySelector('.dx').addEventListener('click', deselect);
    }
    document.addEventListener('keydown', ev=>{ if(ev.key==='Escape') deselect(); });
    detailEl.addEventListener('click', ev=> ev.stopPropagation());
    return { select, deselect };
  }

  // place an HTML bead over an overlay at xPct,yPct (0–100). label optional.
  function placeBead(overlay, e, xPct, yPct, detail, label){
    const c = col(e);
    const b = document.createElement('div');
    b.className = 'bead'+(e.key?' key':'')+((e.arch||e.archive)?' arch':'');
    b.style.left=xPct+'%'; b.style.top=yPct+'%';
    b.style.background=(e.arch||e.archive)?'var(--scene)':c;
    b.style.borderColor=c; b.style.color=c; b._e=e;
    overlay.appendChild(b);
    if(label){
      const lab=document.createElement('div');
      lab.className='blab'+(label.left?' left':'');
      lab.style.left='calc('+xPct+'% '+(label.left?'- ':'+ ')+(label.off||14)+'px)';
      lab.style.top=yPct+'%'; lab.style.color=c;
      lab.textContent=label.text||e.short;
      overlay.appendChild(lab); b._lab=lab;
    }
    b.addEventListener('mouseenter',()=>{ if(b._lab) b._lab.classList.add('hot'); });
    b.addEventListener('mouseleave',()=>{ if(!b.classList.contains('sel')&&b._lab) b._lab.classList.remove('hot'); });
    b.addEventListener('click', ev=>{ ev.stopPropagation(); detail.select(e,b); });
    return b;
  }

  return { TL, col, dateOf, kindOf, makeDetail, placeBead };
})();
