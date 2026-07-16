/* explore-3d.js — the Hunter House site as an orbitable contour model.
   The survey's contour lines are floated at height (no shading, lines only)
   to give the ground real relief; the plan — house, kinhin loop, lake,
   oaks, features — drapes onto that terrain. Drag to orbit, scroll to zoom,
   click a place to fly the camera in. Same tiers as the flat version:
     kinhin → TIMELINE · house → PANEL · spring/lake → CAPTION · tree/fig → ZOOM.
   Heights here are a smooth synthetic field (vertical ×1.6) standing in for
   the real Rhino z until that geometry lands; everything below swaps cleanly. */
(function(){
  const TL=HK.TL, SITE=window.SITE, G=SITE.G, M=SITE.meta;

  // ---- smooth the hand-drawn NE-corner of the site boundary into ONE continuous
  // curve. The corner is the lot path with the most vertices (a jagged freehand
  // run); replace it with a cubic Bézier tangent to the two adjoining straight
  // edges, so the boundary rounds the corner cleanly instead of wobbling. ----
  (function(){ const lot=G&&G.lot; if(!lot||!lot.length)return;
    const num=s=>s.match(/-?[\d.]+/g).map(Number);
    let ci=-1,cn=3; lot.forEach((d,i)=>{ const m=d.match(/-?[\d.]+/g); const np=m?m.length/2:0; if(np>cn){cn=np;ci=i;} });
    if(ci<0)return;
    const cp=num(lot[ci]); const P0=[cp[0],cp[1]], P3=[cp[cp.length-2],cp[cp.length-1]];
    const near=(a,b)=>Math.hypot(a[0]-b[0],a[1]-b[1])<2.5;
    const norm=v=>{const L=Math.hypot(v[0],v[1])||1;return[v[0]/L,v[1]/L];};
    let Tin=null,Tout=null;
    lot.forEach((d,i)=>{ if(i===ci)return; const n=num(d); const a=[n[0],n[1]], b=[n[n.length-2],n[n.length-1]];
      if(near(b,P0))Tin=[P0[0]-a[0],P0[1]-a[1]]; if(near(a,P3))Tout=[b[0]-P3[0],b[1]-P3[1]]; });
    if(!Tin)Tin=[P3[0]-P0[0],P3[1]-P0[1]]; if(!Tout)Tout=[P3[0]-P0[0],P3[1]-P0[1]];
    Tin=norm(Tin); Tout=norm(Tout);
    const chord=Math.hypot(P3[0]-P0[0],P3[1]-P0[1]), h=chord*0.5;
    const P1=[P0[0]+Tin[0]*h,P0[1]+Tin[1]*h], P2=[P3[0]-Tout[0]*h,P3[1]-Tout[1]*h];
    const N=18, parts=[]; for(let k=0;k<=N;k++){ const t=k/N,u=1-t;
      const x=u*u*u*P0[0]+3*u*u*t*P1[0]+3*u*t*t*P2[0]+t*t*t*P3[0];
      const y=u*u*u*P0[1]+3*u*u*t*P1[1]+3*u*t*t*P2[1]+t*t*t*P3[1];
      parts.push((k?'L':'M')+x.toFixed(1)+' '+y.toFixed(1)); }
    lot[ci]=parts.join(' ');
    // remove any duplicate jagged twin spanning the SAME corner endpoints (the old
    // hand-drawn NE corner that was left alongside the smoothed one)
    for(let i=lot.length-1;i>=0;i--){ if(i===ci)continue; const n=num(lot[i]);
      const a=[n[0],n[1]], b=[n[n.length-2],n[n.length-1]];
      if((near(a,P0)&&near(b,P3))||(near(a,P3)&&near(b,P0))) lot.splice(i,1); }
  })();
  const detail=HK.makeDetail(document.getElementById('detail'));
  const overlay=document.getElementById('overlay');
  // dim-future beads rule
  const st=document.createElement('style'); st.textContent='.bead.dim{opacity:.16}'; document.head.appendChild(st);

  // ---------- height field: REAL surveyed elevations ----------
  // Lifted from site_for_web.dxf — the CONTOUR_LINES layer carries true z
  // (0 m at Prospect Lake, rising to ~41 m on the house knoll). site-contours.js
  // holds the contours (at real z) + a baked DEM. elevAt() bilinearly samples
  // the real ground; everything drapes on it. Vertical exaggeration is ×VE.
  const SC=window.SITE_CONTOURS, DEM=SC.dem;
  const HOUSE=[701.56,434.57];
  const gdx=(DEM.x1-DEM.x0)/(DEM.nx-1), gdy=(DEM.y1-DEM.y0)/(DEM.ny-1);
  function elevAt(x,y){ const fi=(x-DEM.x0)/gdx, fj=(y-DEM.y0)/gdy;
    const i=Math.max(0,Math.min(DEM.nx-2,Math.floor(fi))), j=Math.max(0,Math.min(DEM.ny-2,Math.floor(fj)));
    const tx=Math.max(0,Math.min(1,fi-i)), ty=Math.max(0,Math.min(1,fj-j)), z=DEM.z, w=DEM.nx;
    const z00=z[j*w+i],z10=z[j*w+i+1],z01=z[(j+1)*w+i],z11=z[(j+1)*w+i+1];
    return (z00*(1-tx)+z10*tx)*(1-ty)+(z01*(1-tx)+z11*tx)*ty; }
  const VE=2.4, FOOT=0.3048, MULT=SC.scale*FOOT*VE;   // 1-ft contours, XY in m; ×VE exaggeration
  const ground=(x,y)=>elevAt(x,y)*MULT;
  const P3=(x,y,up=0)=>new THREE.Vector3(x-750, ground(x,y)+up, y-525);

  // ---------- three setup ----------
  const host=document.getElementById('scene');
  const scene=new THREE.Scene();
  const camera=new THREE.PerspectiveCamera(42, innerWidth/innerHeight, 1, 9000);
  const renderer=new THREE.WebGLRenderer({antialias:true,alpha:true});
  renderer.setPixelRatio(Math.min(2,devicePixelRatio)); renderer.setSize(innerWidth,innerHeight);
  host.appendChild(renderer.domElement);
  const controls=new THREE.OrbitControls(camera,renderer.domElement);
  controls.enableDamping=true; controls.dampingFactor=.08; controls.enablePan=true;
  controls.mouseButtons={LEFT:THREE.MOUSE.ROTATE, MIDDLE:THREE.MOUSE.DOLLY, RIGHT:THREE.MOUSE.PAN};
  controls.screenSpacePanning=true; controls.panSpeed=.9;
  controls.minDistance=140; controls.maxDistance=2800; controls.maxPolarAngle=1.46; controls.rotateSpeed=.7; controls.zoomSpeed=.8;
  // shift = pan, otherwise orbit — decided at pointerdown (capture phase, before OrbitControls reads it)
  renderer.domElement.addEventListener('pointerdown',e=>{ controls.mouseButtons.LEFT = e.shiftKey?THREE.MOUSE.PAN:THREE.MOUSE.ROTATE; }, true);

  // ---------- custom line-work cursors (triangle base, no crosshair) ----------
  const svgCur=(svg,hx,hy)=>"url(\"data:image/svg+xml,"+encodeURIComponent(svg)+"\") "+hx+" "+hy+", auto";
  const _ink='#d6d1c4', _dk='#120f0c';
  const wrap2=(inner)=>"<svg xmlns='http://www.w3.org/2000/svg' width='26' height='26'><g fill='none' stroke='"+_dk+"' stroke-width='1.9' opacity='.28' stroke-linejoin='round'>"+inner+"</g><g fill='none' stroke='"+_ink+"' stroke-width='1' stroke-linejoin='round'>"+inner+"</g></svg>";
  const tri="M13 8 L8.5 17.5 L17.5 17.5 Z";
  // idle / orbit hover: small triangle outline
  const curOrbit=svgCur(wrap2("<path d='"+tri+"'/>"),13,14);
  // hover clickable: triangle fills in
  const curPick=svgCur("<svg xmlns='http://www.w3.org/2000/svg' width='26' height='26'><path d='"+tri+"' fill='"+_dk+"' fill-opacity='.28' stroke='"+_dk+"' stroke-opacity='.28' stroke-width='1.9' stroke-linejoin='round'/><path d='"+tri+"' fill='"+_ink+"' stroke='"+_ink+"' stroke-width='1' stroke-linejoin='round'/></svg>",13,14);
  // orbiting (left-drag): a circle surrounds the triangle
  const curRotate=svgCur(wrap2("<path d='"+tri+"'/><circle cx='13' cy='13' r='9' stroke-dasharray='2 2.6'/>"),13,14);
  // panning (right / shift-drag): corner-bracket frame around the triangle
  const curPan=svgCur(wrap2("<path d='"+tri+"'/><path d='M4 7 V4 H7 M19 4 H22 V7 M22 19 V22 H19 M7 22 H4 V19'/>"),13,14);
  let curDragging=false, curHover=false, curDragMode='orbit';
  function refreshCursor(){ host.style.cursor = curDragging ? (curDragMode==='pan'?curPan:curRotate) : (curHover?curPick:curOrbit); }
  refreshCursor();

  // overview pose
  const OVR={tar:new THREE.Vector3(0,40,-40), dir:new THREE.Vector3(0,1,0.06).normalize(), dist:1320};  // top-down plan view (home); drag tilts into 3D
  function applyPose(p){ controls.target.copy(p.tar); camera.position.copy(p.tar.clone().add(p.dir.clone().multiplyScalar(p.dist))); camera.lookAt(controls.target); controls.update(); }
  applyPose(OVR);

  // ---- opening establishing shot: park the camera wide on a slowly turning
  // model; the working plan-view (OVR) is flown in when the visitor enters. ----
  const INTRO={ tar:OVR.tar.clone(), dist:2520, tilt:0.06 };   // top-down (matches plan view); entry just zooms in
  const EMBED=new URLSearchParams(location.search).get('embed')==='1';   // shown inside browse: splash = holding screen, notify host on enter
  let introActive=false, introAz=0;
  function introPose(az){ const s=Math.sin(INTRO.tilt), c=Math.cos(INTRO.tilt);
    const dir=new THREE.Vector3(s*Math.sin(az), c, s*Math.cos(az));
    controls.target.copy(INTRO.tar); camera.position.copy(INTRO.tar.clone().add(dir.multiplyScalar(INTRO.dist))); camera.lookAt(controls.target); }
  { const _qs=new URLSearchParams(location.search), _enter=_qs.get('enter');
    if(_qs.get('intro')==='0' || _enter==='now'){
      document.body.classList.remove('intro-active'); const _i0=document.getElementById('intro'); if(_i0)_i0.classList.add('gone');
    } else if(_enter==='hold' || _enter==='zoom'){
      // embedded mode: hold a wide top-down frame with NO splash copy; the host
      // (browse) triggers the zoom-in via postMessage once the frame is full-bleed.
      introActive=true; controls.enabled=false; introPose(introAz);
      const _i0=document.getElementById('intro'); if(_i0)_i0.style.display='none';
      if(_enter==='zoom') setTimeout(function(){ enterSite(); }, 480);
    } else {
      introActive=true; controls.enabled=false; introPose(introAz);
    }
  }

  // ---------- path sampler ----------
  const NS='http://www.w3.org/2000/svg';
  const offsvg=document.createElementNS(NS,'svg'); offsvg.setAttribute('width','0'); offsvg.setAttribute('height','0');
  offsvg.style.cssText='position:absolute;width:0;height:0;overflow:hidden'; document.body.appendChild(offsvg);
  const offp=document.createElementNS(NS,'path'); offsvg.appendChild(offp);
  function sample(d,step=8){ offp.setAttribute('d',d); const L=offp.getTotalLength(); if(!L)return[]; const out=[]; for(let s=0;s<=L;s+=step){const p=offp.getPointAtLength(s);out.push([p.x,p.y]);}
    const e=offp.getPointAtLength(L), last=out[out.length-1]; if(!last||Math.hypot(last[0]-e.x,last[1]-e.y)>0.01)out.push([e.x,e.y]); return out; }  // always include the exact endpoint (so corners close)

  // ---------- materials ----------
  const mat={
    contour:new THREE.LineBasicMaterial({color:0xffffff,transparent:true,opacity:.15,vertexColors:true,depthTest:false,depthWrite:false}),
    lot:    new THREE.LineBasicMaterial({color:0xc4826e,transparent:true,opacity:1}),
    cov:    new THREE.LineBasicMaterial({color:0xa78bbf,transparent:true,opacity:.85}),
    house:  new THREE.LineBasicMaterial({color:0xe6c067,transparent:true,opacity:1}),
    lake:   new THREE.LineBasicMaterial({color:0x7ba0d6,transparent:true,opacity:.5}),
    lakeFill:new THREE.MeshBasicMaterial({color:0x3a5680,transparent:true,opacity:.3,side:THREE.DoubleSide,depthWrite:false}),
    stream: new THREE.LineBasicMaterial({color:0x6f93c9,transparent:true,opacity:.75}),
    northL: new THREE.LineBasicMaterial({color:0x9a958b,transparent:true,opacity:.75}),
    corr:   new THREE.LineBasicMaterial({color:0xc9a44e,transparent:true,opacity:.6}),
    rock:   new THREE.LineBasicMaterial({color:0x9a958b,transparent:true,opacity:.68}),
    path:   new THREE.LineBasicMaterial({color:0xb9b3a8,transparent:true,opacity:.68}),
    tree:   new THREE.LineBasicMaterial({color:0x7aaa98,transparent:true,opacity:.82}),
    trunk:  new THREE.LineBasicMaterial({color:0x7aaa98,transparent:true,opacity:.95}),
  };

  // ---------- fig "unseen ocean": contour vertex swell ----------
  // A slow, heavy ground-swell radiating from the dead fig. Amplitude peaks at
  // the fig and dies off outward (smoothstep inner→outer), gated by figAmt so it
  // only wakes when the fig is the focus. Driven per-frame from the render loop.
  const lakeUni={ uTime:{value:0}, uAmp:{value:0} };   // lake motion OFF (set figFx.lake>0 to enable)
  const figUni={ uTime:{value:0}, uSwell:{value:0}, uMode:{value:0}, uCursor:{value:0},
    uFig:{value:new THREE.Vector2(G.points.fig.x-750, G.points.fig.y-525)},
    uInner:{value:6}, uOuter:{value:980},
    uBreeze:{value:1}, uWind:{value:new THREE.Vector2(1,0.42).normalize()} };
  // recall the last-chosen fig effect (0 = radial tremor, 1 = vertical swell)
  { const m=parseFloat(localStorage.getItem('hh3d-fig-mode')); if(!isNaN(m))figUni.uMode.value=m; }
  mat.contour.onBeforeCompile=(sh)=>{
    sh.uniforms.uTime=figUni.uTime; sh.uniforms.uSwell=figUni.uSwell; sh.uniforms.uMode=figUni.uMode;
    sh.uniforms.uFig=figUni.uFig; sh.uniforms.uInner=figUni.uInner; sh.uniforms.uOuter=figUni.uOuter;
    sh.uniforms.uBreeze=figUni.uBreeze; sh.uniforms.uWind=figUni.uWind; sh.uniforms.uCursor=figUni.uCursor;
    sh.vertexShader='uniform float uTime;uniform float uSwell;uniform float uMode;uniform vec2 uFig;uniform float uInner;uniform float uOuter;uniform float uBreeze;uniform vec2 uWind;uniform float uCursor;varying vec2 vWorldXZ;\n'+sh.vertexShader;
    sh.vertexShader=sh.vertexShader.replace('#include <begin_vertex>',
      '#include <begin_vertex>\n'+
      // ambient breeze across the whole drawing — a gentle directional drift with
      // slow gusts rolling across the land (wave phase travels along the wind).
      // Elevation held fixed; this is the land "blowing" like the fig.
      'float _wp=dot(transformed.xz,uWind)*0.013 - uTime*1.2;\n'+
      'float _wg=0.6 + 0.4*sin(uTime*0.27 + transformed.x*0.004 + transformed.z*0.003);\n'+
      'transformed.xz += uWind*(sin(_wp)+0.3*sin(_wp*2.1))*_wg*uBreeze*2.6;\n'+
      'vec2 _rel=transformed.xz-uFig; float _d=length(_rel);\n'+
      'vec2 _dir = _d>0.001 ? _rel/_d : vec2(0.0);\n'+
      'float _amp=(1.0-smoothstep(uInner,uOuter,_d))*uSwell;\n'+
      'if(uMode<0.5){\n'+
      // MODE 0 — electric tremor: a subtle, high-frequency radial jitter that
      // crackles along the line to the fig. Hashed (not smooth) so it reads as
      // current, not liquid; an intermittent envelope makes it spark. y held fixed.
      '  float _trav=sin(_d*0.9 - uTime*11.0);\n'+
      '  float _jit=fract(sin(_d*13.3 + floor(uTime*17.0)*2.7)*43758.5453)*2.0-1.0;\n'+
      '  float _spark=pow(max(0.0,sin(uTime*3.6 + _d*0.18)),8.0);\n'+
      '  float _w=(_trav*0.45 + _jit*0.9)*(0.35 + 0.9*_spark)*2.6;\n'+
      '  transformed.xz += _dir*_w*_amp;\n'+
      '} else {\n'+
      // MODE 1 — vertical swell (saved): slow heavy ground-swell lifting the
      // terrain in y. Detaches from fixed geometry, but kept for recall.
      '  float _w=sin(_d*0.042 - uTime*1.5)*11.0 + sin(_d*0.017 + uTime*0.8)*6.0;\n'+
      '  transformed.y += _w*_amp;\n'+
      '}\n'+
      // pass world xz to the fragment stage for the cursor GLOW (no displacement).
      'vWorldXZ = position.xz;');
    // ---- cursor GLOW (fragment): brighten the contour lines near the pointer.
    // No movement — a pool of light following the cursor, gated by uCursor so
    // it's dark unless a host drives it. Warm (copper/gold) to match the lens. ----
    sh.fragmentShader='uniform vec2 uFig;uniform float uInner;uniform float uOuter;uniform float uCursor;varying vec2 vWorldXZ;\n'+sh.fragmentShader;
    sh.fragmentShader=sh.fragmentShader.replace('#include <color_fragment>',
      '#include <color_fragment>\n'+
      'float _gd=length(vWorldXZ-uFig);\n'+
      'float _g=(1.0-smoothstep(uInner,uOuter,_gd))*uCursor;\n'+
      'diffuseColor.rgb += _g*vec3(1.0,0.86,0.55)*1.3;\n'+
      'diffuseColor.a = clamp(diffuseColor.a + _g*0.95, 0.0, 1.0);');
  };
  mat.contour.needsUpdate=true;
  // ---- easy recall: window.figFx.mode = 0 (radial tremor) | 1 (vertical swell) ----
  let breezeBase=1;
  window.figFx={ get mode(){return figUni.uMode.value;},
    set mode(v){ figUni.uMode.value=v; try{localStorage.setItem('hh3d-fig-mode',v);}catch(e){} },
    get breeze(){return breezeBase;},
    set breeze(v){ breezeBase=v; try{localStorage.setItem('hh3d-breeze',v);}catch(e){} },
    get lake(){return lakeUni.uAmp.value;},
    set lake(v){ lakeUni.uAmp.value=v; try{localStorage.setItem('hh3d-lake-amp',v);}catch(e){} },
    modes:{radialTremor:0, verticalSwell:1} };
  { const b=parseFloat(localStorage.getItem('hh3d-breeze')); if(!isNaN(b))breezeBase=b; }
  { const la=parseFloat(localStorage.getItem('hh3d-lake-amp')); if(!isNaN(la))lakeUni.uAmp.value=0; }

  // every plan line drapes per-vertex on the surface (no floating/tangling)
  function drape(d,m,step=6,up=0,close=false,parent){ const pts=sample(d,step); if(pts.length<2)return; const a=[];
    pts.forEach(p=>a.push(p[0]-750,ground(p[0],p[1])+up,p[1]-525));
    if(close)a.push(pts[0][0]-750,ground(pts[0][0],pts[0][1])+up,pts[0][1]-525);
    const g=new THREE.BufferGeometry(); g.setAttribute('position',new THREE.Float32BufferAttribute(a,3)); const l=new THREE.Line(g,m); (parent||scene).add(l); return l; }

  // ---------- LAYERS: every object lives in a named group for on/off control ----------
  const LK=['contours','boundary','house','trees','trail','paths','lake','stream','covenant','roads','labels','annotations','north'];
  const LAYERS={}; LK.forEach(k=>{LAYERS[k]=new THREE.Group();scene.add(LAYERS[k]);});
  const LKEYS=LK;
  let LSTATE={}; LKEYS.forEach(k=>LSTATE[k]=true); LSTATE.labels=false; LSTATE.annotations=false;
  try{const s=JSON.parse(localStorage.getItem('hh3d-layers'));if(s)Object.assign(LSTATE,s);}catch(e){}
  function applyLayers(){ LKEYS.forEach(k=>{ if(LAYERS[k])LAYERS[k].visible=LSTATE[k]; }); try{localStorage.setItem('hh3d-layers',JSON.stringify(LSTATE));}catch(e){} if(window.__updReadout)window.__updReadout(); }

  // ---------- build the model ----------
  // real contours, each drawn FLAT at its surveyed elevation (spacing = steepness)
  // ---------- site-boundary mask: fade contours to nothing outside the parcel ----------
  // Build ONE ordered ring by chaining the lot segments end-to-end. (The lot is
  // stored as many separate edge paths in arbitrary order; naively concatenating
  // their points makes a scrambled, self-intersecting polygon — which broke
  // inPoly/clampInside and mangled the kinhin dots. Chain by matching endpoints.)
  const BND=(()=>{
    const segs=[...new Set(G.lot)].map(d=>sample(d,10)).filter(s=>s.length>1);
    if(!segs.length)return [];
    const used=new Array(segs.length).fill(false); used[0]=true;
    const ring=segs[0].slice();
    const tail=()=>ring[ring.length-1], head=()=>ring[0];
    const near=(a,b)=>Math.hypot(a[0]-b[0],a[1]-b[1]);
    for(let guard=0;guard<segs.length*2;guard++){
      let bi=-1,brev=false,bend=false,bd=12;   // 12-unit join tolerance
      for(let i=0;i<segs.length;i++){ if(used[i])continue; const s=segs[i],a=s[0],b=s[s.length-1];
        let d;
        d=near(tail(),a); if(d<bd){bd=d;bi=i;brev=false;bend=true;}
        d=near(tail(),b); if(d<bd){bd=d;bi=i;brev=true;bend=true;}
        d=near(head(),b); if(d<bd){bd=d;bi=i;brev=false;bend=false;}
        d=near(head(),a); if(d<bd){bd=d;bi=i;brev=true;bend=false;}
      }
      if(bi<0)break; used[bi]=true; let s=segs[bi].slice(); if(brev)s.reverse();
      if(bend) ring.push(...s.slice(1)); else ring.unshift(...s.slice(0,-1));
    }
    // de-dupe near-coincident neighbours
    const out=[]; ring.forEach(p=>{ if(!out.length||near(p,out[out.length-1])>0.5)out.push(p); });
    return out;
  })();
  function inPoly(x,y){ let c=false; for(let i=0,j=BND.length-1;i<BND.length;j=i++){ const xi=BND[i][0],yi=BND[i][1],xj=BND[j][0],yj=BND[j][1];
    if(((yi>y)!=(yj>y)) && (x<(xj-xi)*(y-yi)/(yj-yi)+xi)) c=!c; } return c; }
  function distOut(x,y){ if(inPoly(x,y))return 0; let m=1e9;
    for(let i=0,j=BND.length-1;i<BND.length;j=i++){ const ax=BND[j][0],ay=BND[j][1],bx=BND[i][0],by=BND[i][1],dx=bx-ax,dy=by-ay,l2=dx*dx+dy*dy||1;
      let t=((x-ax)*dx+(y-ay)*dy)/l2; t=t<0?0:t>1?1:t; m=Math.min(m,Math.hypot(x-(ax+t*dx),y-(ay+t*dy))); } return m; }
  const _bc=BND.reduce((s,p)=>[s[0]+p[0],s[1]+p[1]],[0,0]), BCX=_bc[0]/BND.length, BCY=_bc[1]/BND.length;
  function clampInside(x,y,margin){
    // nearest boundary edge + its inward (perpendicular) normal
    let best=1e9,px0=x,py0=y,inN=[0,0];
    for(let i=0,j=BND.length-1;i<BND.length;j=i++){ const ax=BND[j][0],ay=BND[j][1],bx=BND[i][0],by=BND[i][1],dx=bx-ax,dy=by-ay,l2=dx*dx+dy*dy||1;
      let t=((x-ax)*dx+(y-ay)*dy)/l2; t=t<0?0:t>1?1:t; const px=ax+t*dx,py=ay+t*dy,d=Math.hypot(x-px,y-py);
      if(d<best){ best=d; px0=px; py0=py; let nx=-dy,ny=dx; const tcx=BCX-px,tcy=BCY-py; if(nx*tcx+ny*tcy<0){nx=dy;ny=-dx;} const nl=Math.hypot(nx,ny)||1; inN=[nx/nl,ny/nl]; } }
    // safely inside and clear of the line -> leave it; otherwise seat it `margin` inside the nearest edge
    if(inPoly(x,y) && best>=margin) return [x,y];
    return [px0+inN[0]*margin, py0+inN[1]*margin]; }
  const FADE=1e12, baseC=new THREE.Color(0xf3efe6), bgC=new THREE.Color(0x242220);
  function fadeCol(x,y){ let t=Math.min(1,distOut(x,y)/FADE); t=t*t*(3-2*t); return [baseC.r*(1-t)+bgC.r*t, baseC.g*(1-t)+bgC.g*t, baseC.b*(1-t)+bgC.b*t]; }

  // real contours, each FLAT at its surveyed elevation.
  // ?extendw=1 (mock landing only) adds a FABRICATED westward extension: the
  // survey mirrored across its west edge, giving the framing room to centre the
  // house. NOT applied to the live archive's site view — it stays truthful.
  const EXTW = new URLSearchParams(location.search).get('extendw')==='1';
  // reflect across the contours' ACTUAL western edge (min survey x), so the
  // mirror continues seamlessly from where the drawing runs out — not from the
  // DEM edge (which left a gap and put the extension off to the far west).
  let CMINX = Infinity;
  if(EXTW) SC.contours.forEach(c=>c.pts.forEach(p=>{ if(p[0]<CMINX)CMINX=p[0]; }));
  function addContour(c, refl){ const y=c.z*MULT, a=[], col=[];
    const rx=px=> refl ? (2*CMINX - px) : px;
    const addv=(px,py)=>{ a.push(rx(px)-750,y,py-525); const cc=fadeCol(px,py); col.push(cc[0],cc[1],cc[2]); };
    c.pts.forEach(p=>addv(p[0],p[1])); if(c.closed&&c.pts.length)addv(c.pts[0][0],c.pts[0][1]);
    const g=new THREE.BufferGeometry(); g.setAttribute('position',new THREE.Float32BufferAttribute(a,3));
    g.setAttribute('color',new THREE.Float32BufferAttribute(col,3)); const cl=new THREE.Line(g,mat.contour); cl.renderOrder=-10; LAYERS.contours.add(cl); }
  SC.contours.forEach(c=>{ addContour(c,false); if(EXTW) addContour(c,true); });
  [...new Set(G.lot)].forEach(d=>drape(d,mat.lot,7,0,false,LAYERS.boundary));   // site boundary (red)
  G.stream.forEach(d=>drape(d,mat.stream,6,0,false,LAYERS.stream));
  // lake — flat water FILL (no outline), at the lowest contour level.
  // Subdivided so it has interior vertices, then given a tiny lapping ripple
  // in the vertex shader (see lakeUni / mat.lakeFill patch below).
  // Mirrored west too when ?extendw=1 (mock landing), matching the contours.
  function addLake(refl){ const raw=G.lake[0].match(/-?[\d.]+/g).map(Number); const C=[];
    let lminx=Infinity; for(let i=0;i<raw.length;i+=2) if(raw[i]<lminx)lminx=raw[i];
    for(let i=0;i+1<raw.length;i+=2)C.push(new THREE.Vector2(refl?(2*lminx-raw[i]):raw[i],raw[i+1])); if(C.length<3)return;
    const tris=THREE.ShapeUtils.triangulateShape(C,[]); let a=[];
    tris.forEach(t=>t.forEach(idx=>{ const p=C[idx]; a.push(p.x-750,0,p.y-525); }));
    // midpoint-subdivide each triangle a few times → fine, planar interior mesh
    function subdiv(arr){ const out=[]; for(let i=0;i<arr.length;i+=9){
      const v0=[arr[i],arr[i+1],arr[i+2]], v1=[arr[i+3],arr[i+4],arr[i+5]], v2=[arr[i+6],arr[i+7],arr[i+8]];
      const m=(p,q)=>[(p[0]+q[0])/2,(p[1]+q[1])/2,(p[2]+q[2])/2];
      const a01=m(v0,v1), a12=m(v1,v2), a20=m(v2,v0);
      [v0,a01,a20, a01,v1,a12, a20,a12,v2, a01,a12,a20].forEach(v=>out.push(v[0],v[1],v[2])); }
      return out; }
    for(let i=0;i<3;i++)a=subdiv(a);     // 4^3 = 64× denser
    const g=new THREE.BufferGeometry(); g.setAttribute('position',new THREE.Float32BufferAttribute(a,3));
    LAYERS.lake.add(new THREE.Mesh(g,mat.lakeFill)); }
  addLake(false); if(EXTW) addLake(true);
  // tiny lapping: a few low-amplitude crossing wavelets nudging the surface in y
  mat.lakeFill.onBeforeCompile=(sh)=>{
    sh.uniforms.uTime=lakeUni.uTime; sh.uniforms.uAmp=lakeUni.uAmp;
    sh.vertexShader='uniform float uTime;uniform float uAmp;\n'+sh.vertexShader;
    sh.vertexShader=sh.vertexShader.replace('#include <begin_vertex>',
      '#include <begin_vertex>\n'+
      'float _lap=sin(position.x*0.10 + uTime*1.7)*0.6\n'+
      '         + sin(position.z*0.13 - uTime*1.3)*0.5\n'+
      '         + sin((position.x+position.z)*0.07 + uTime*0.9)*0.4\n'+
      '         + sin((position.x-position.z)*0.16 + uTime*2.2)*0.25;\n'+
      'transformed.y += _lap*uAmp;');
  };
  mat.lakeFill.needsUpdate=true;
  G.house.forEach(d=>drape(d,mat.house,4,2,false,LAYERS.house));
  // house footprint: a SOLID fill in the background colour, drawn OVER the
  // contours (renderOrder above them) so the ground reads clean inside the
  // footprint. Host hover fades it to the slightest yellow + brightens the line.
  let houseFillMat=null, HOUSE_POLY=null, HOUSE_N=0, HOUSE_ERR='', houseMeshRef=null;
  // mask-based inHouse() — filled by the fill builder below (grid + bbox in drawing coords)
  let HMASK=null, HM_x0=0, HM_y0=0, HM_cell=1, HM_gw=0, HM_gh=0;
  (function(){ try{
    // EXACT footprint by RASTER FLOOD-FILL, not ring-chaining. The old chain-and-
    // triangulate method sampled walls at 6u and dropped every wall shorter than
    // that (31 of 59) — so rings couldn't close at corners and closed with long
    // chords (spikes + a triangular notch), and the round room filled as its own
    // stray disc. Instead: sample ALL walls finely, paint them into a mask, flood
    // the OUTSIDE from the border, and take the enclosed region as the footprint.
    // Robust to open linework, interior partitions and the round room.
    const segs=[]; G.house.forEach(d=>{ const s=sample(d,1.2); if(s.length)segs.push(s); });
    if(!segs.length){ HOUSE_ERR='no-segs'; return; }
    let minx=1e9,miny=1e9,maxx=-1e9,maxy=-1e9;
    segs.forEach(s=>s.forEach(p=>{ if(p[0]<minx)minx=p[0]; if(p[0]>maxx)maxx=p[0]; if(p[1]<miny)miny=p[1]; if(p[1]>maxy)maxy=p[1]; }));
    const PAD=6, CELL=0.6, BRUSH=2.2, x0=minx-PAD, y0=miny-PAD;   // BRUSH bridges sampling gaps at wall joints
    const gw=Math.ceil((maxx-minx+2*PAD)/CELL), gh=Math.ceil((maxy-miny+2*PAD)/CELL);
    const cv=document.createElement('canvas'); cv.width=gw; cv.height=gh; const g2=cv.getContext('2d');
    g2.fillStyle='#000'; g2.fillRect(0,0,gw,gh);
    g2.strokeStyle='#fff'; g2.lineCap='round'; g2.lineJoin='round'; g2.lineWidth=Math.max(1,BRUSH/CELL);
    const GX=x=>(x-x0)/CELL, GY=y=>(y-y0)/CELL;
    segs.forEach(s=>{ g2.beginPath(); s.forEach((p,i)=>i?g2.lineTo(GX(p[0]),GY(p[1])):g2.moveTo(GX(p[0]),GY(p[1]))); g2.stroke(); });
    const px=g2.getImageData(0,0,gw,gh).data, wall=new Uint8Array(gw*gh);
    for(let i=0;i<gw*gh;i++) wall[i]=px[i*4]>80?1:0;
    // flood the outside from every border cell
    const out=new Uint8Array(gw*gh), st=[];
    for(let x=0;x<gw;x++){ st.push(x,0,x,gh-1); } for(let y=0;y<gh;y++){ st.push(0,y,gw-1,y); }
    while(st.length){ const y=st.pop(), x=st.pop(); if(x<0||y<0||x>=gw||y>=gh)continue; const i=y*gw+x; if(out[i]||wall[i])continue; out[i]=1; st.push(x+1,y,x-1,y,x,y+1,x,y-1); }
    let inside=new Uint8Array(gw*gh); for(let i=0;i<gw*gh;i++) inside[i]=out[i]?0:1;   // wall + enclosed = inside (fills to outer wall edge)
    // erode ~half the brush so the tint edge lands on the wall centre-line, not proud of it
    const ER=Math.max(0,Math.round((BRUSH*0.5)/CELL));
    for(let it=0;it<ER;it++){ const nx=new Uint8Array(gw*gh);
      for(let y=1;y<gh-1;y++)for(let x=1;x<gw-1;x++){ const i=y*gw+x; if(inside[i]&&inside[i-1]&&inside[i+1]&&inside[i-gw]&&inside[i+gw]) nx[i]=1; } inside=nx; }
    let icnt=0; for(let i=0;i<gw*gh;i++) if(inside[i])icnt++;
    if(!icnt){ HOUSE_ERR='empty'; return; }
    // fill mesh from horizontal runs of inside cells (one quad per run), draped on terrain
    const a=[], WX=gx=>x0+gx*CELL, WY=gy=>y0+gy*CELL, V=(X,Y)=>[X-750, ground(X,Y)+1.0, Y-525];
    for(let y=0;y<gh;y++){ let x=0; while(x<gw){ if(!inside[y*gw+x]){x++;continue;} let x2=x; while(x2<gw&&inside[y*gw+x2])x2++;
      const X0=WX(x),X1=WX(x2),Y0=WY(y),Y1=WY(y+1), p00=V(X0,Y0),p10=V(X1,Y0),p11=V(X1,Y1),p01=V(X0,Y1);
      a.push(...p00,...p10,...p11, ...p00,...p11,...p01); x=x2; } }
    const g=new THREE.BufferGeometry(); g.setAttribute('position',new THREE.Float32BufferAttribute(a,3));
    houseFillMat=new THREE.MeshBasicMaterial({color:0x242220,transparent:true,opacity:1,side:THREE.DoubleSide,depthWrite:false,depthTest:false});
    const mesh=new THREE.Mesh(g,houseFillMat); mesh.renderOrder=-5; houseMeshRef=mesh; LAYERS.house.add(mesh);
    HMASK=inside; HM_x0=x0; HM_y0=y0; HM_cell=CELL; HM_gw=gw; HM_gh=gh;
    HOUSE_N=icnt; HOUSE_ERR='ok mask '+gw+'x'+gh+' in='+icnt; }
    catch(e){ HOUSE_ERR=(e&&e.message)||'throw'; console.warn('house fill failed',e); } })();
  function inHouse(wx,wz){ if(!HMASK)return false; const gx=Math.floor((wx+750-HM_x0)/HM_cell), gy=Math.floor((wz+525-HM_y0)/HM_cell);
    if(gx<0||gy<0||gx>=HM_gw||gy>=HM_gh)return false; return HMASK[gy*HM_gw+gx]===1; }
  // restored DWG layers (parsed but previously undrawn)
  if(G.covenant) G.covenant.forEach(d=>drape(d,mat.cov,7,0,false,LAYERS.covenant));   // covenant area
  // garden path near house — clamp inside the property line; its tail wandered SW
  // toward the lake and poked across the boundary, so seat any stray point on-property.
  // Clamping snaps stray points onto the edge, which leaves kinks — so run a few
  // Chaikin corner-cutting passes to round it back into a smooth curve. Chaikin stays
  // within the polyline's hull, so the smoothed line never pokes back across the edge.
  const chaikin=(pts,iter)=>{ let p=pts; for(let it=0;it<iter;it++){ const out=[p[0]];
      for(let i=0;i<p.length-1;i++){ const a=p[i],b=p[i+1];
        out.push([a[0]*0.75+b[0]*0.25,a[1]*0.75+b[1]*0.25],[a[0]*0.25+b[0]*0.75,a[1]*0.25+b[1]*0.75]); }
      out.push(p[p.length-1]); p=out; } return p; };
  // Laplacian relaxation — pull each interior point toward the midpoint of its
  // neighbours. Unlike Chaikin (which preserves tight radii), this WIDENS tight
  // bends, and because it moves points toward the local average it pulls inward,
  // so the relaxed curve stays on-property. Endpoints pinned.
  const relax=(pts,iter,k)=>{ let p=pts.map(q=>q.slice()); for(let it=0;it<iter;it++){ const out=p.map(q=>q.slice());
      for(let i=1;i<p.length-1;i++){ out[i][0]=p[i][0]+k*((p[i-1][0]+p[i+1][0])*0.5-p[i][0]);
        out[i][1]=p[i][1]+k*((p[i-1][1]+p[i+1][1])*0.5-p[i][1]); } p=out; } return p; };
  if(G.trails)   G.trails.forEach(d=>{ let cl=sample(d,3).map(p=>clampInside(p[0],p[1],6));
    cl=relax(chaikin(cl,2),24,0.5);
    drape('M'+cl.map(p=>p[0].toFixed(2)+' '+p[1].toFixed(2)).join(' L'),mat.path,1.5,1,false,LAYERS.paths); });

  // ---------- survey text, laid FLAT on the ground at its surveyed position ----------
  // (the title block + the lake label, exactly where they sit in the DXF, draped on terrain)
  const TXm=X=>(X-468040.82)*3.3744+122.9, TYm=Y=>(5376253.55-Y)*3.3938+42.2, FTH=3.3938;
  function groundText(lines, X, Y, wDXF, opt={}, parent){
    const vx=TXm(X), vy=TYm(Y), Wvb=wDXF*3.3744, lineH=FTH*1.7, Hvb=lines.length*lineH;
    const CW=2048, CH=Math.max(96,Math.round(CW*Hvb/Wvb)), cv=document.createElement('canvas');
    cv.width=CW; cv.height=CH; const cx=cv.getContext('2d'); cx.textBaseline='middle'; cx.textAlign='left';
    const rowH=CH/lines.length;
    lines.forEach((ln,i)=>{ let f=rowH*(opt.fs||0.58); cx.font=`${opt.weight||500} ${f}px "JetBrains Mono",monospace`;
      while(cx.measureText(ln).width>CW*0.985&&f>6){f-=1;cx.font=`${opt.weight||500} ${f}px "JetBrains Mono",monospace`;}
      cx.fillStyle=opt.color||'rgba(240,237,230,0.82)'; cx.fillText(ln, CW*0.006, (i+0.5)*rowH); });
    const tex=new THREE.CanvasTexture(cv); tex.anisotropy=8;
    const nx=28, ny=Math.max(2,Math.round(nx*Hvb/Wvb)), pos=[],uv=[],idx=[];
    for(let j=0;j<=ny;j++)for(let i=0;i<=nx;i++){ const fx=i/nx,fy=j/ny,Xv=vx+fx*Wvb,Yv=vy+fy*Hvb;
      pos.push(Xv-750, ground(Xv,Yv)+2.2, Yv-525); uv.push(fx,1-fy); }
    for(let j=0;j<ny;j++)for(let i=0;i<nx;i++){ const a=j*(nx+1)+i,b=a+1,c=a+nx+1,d=c+1; idx.push(a,c,b,b,c,d); }
    const g=new THREE.BufferGeometry(); g.setAttribute('position',new THREE.Float32BufferAttribute(pos,3));
    g.setAttribute('uv',new THREE.Float32BufferAttribute(uv,2)); g.setIndex(idx);
    (parent||scene).add(new THREE.Mesh(g,new THREE.MeshBasicMaterial({map:tex,transparent:true,opacity:opt.op||0.9,depthWrite:false,side:THREE.DoubleSide})));
  }



  // road labels — single line, laid flat & draped on terrain, kerned mono, light
  function roadLabel(text, cx, cy, lenVb, opt={}){
    const rot=(opt.rot||0)*Math.PI/180, hw=lenVb/2, hh=(opt.h||24)/2;
    const dxu=Math.cos(rot), dyu=Math.sin(rot), px=-dyu, py=dxu;
    const CW=2048, CH=Math.max(64,Math.round(CW*(2*hh)/(2*hw))), cv=document.createElement('canvas');
    cv.width=CW; cv.height=CH; const c=cv.getContext('2d'); const fs=CH*0.6;
    c.font=`${opt.weight||300} ${fs}px "JetBrains Mono",monospace`;
    try{c.letterSpacing=(fs*(opt.ls!=null?opt.ls:0.34))+'px';}catch(e){}
    c.textAlign='center'; c.textBaseline='middle'; c.fillStyle=opt.color||'rgba(240,237,230,0.5)';
    c.fillText(text, CW/2, CH/2+CH*0.02);
    const tex=new THREE.CanvasTexture(cv); tex.anisotropy=8;
    const nu=Math.max(8,Math.round(lenVb/14)), nv=2, pos=[],uv=[],idx=[];
    for(let j=0;j<=nv;j++)for(let i=0;i<=nu;i++){ const fu=i/nu, fv=j/nv, u=-hw+fu*2*hw, v=-hh+fv*2*hh, X=cx+u*dxu+v*px, Y=cy+u*dyu+v*py;
      pos.push(X-750, ground(X,Y)+(opt.up||2), Y-525); uv.push(fu,1-fv); }
    for(let j=0;j<nv;j++)for(let i=0;i<nu;i++){ const a=j*(nu+1)+i,b=a+1,cc=a+nu+1,d=cc+1; idx.push(a,cc,b,b,cc,d); }
    const g=new THREE.BufferGeometry(); g.setAttribute('position',new THREE.Float32BufferAttribute(pos,3));
    g.setAttribute('uv',new THREE.Float32BufferAttribute(uv,2)); g.setIndex(idx);
    const m=new THREE.Mesh(g,new THREE.MeshBasicMaterial({map:tex,transparent:true,opacity:opt.op||0.9,depthWrite:false,side:THREE.DoubleSide}));
    (opt.layer||LAYERS.roads).add(m); return m;
  }
  const lblGoward=roadLabel('GOWARD RD', 669, 302, 360, {rot:5.9, h:26});   // aligned to north frontage (seg5), tucked just outside
  const lblEcho=roadLabel('ECHO DR', 1014, 564, 120, {rot:-40.4, h:22});    // seated on the long SE property line (139.6° axis), running SW→NE
  const plLabel=roadLabel('PROSPECT LAKE', 255, 775, 232, {rot:50, h:22, color:'rgba(132,168,224,0.85)', layer:LAYERS.lake});  // blue, 50°, SW of polygon centre

  // text running ALONG a path (centered), draped on terrain — used for the covenant line
  function pathLabel(text, d, opt={}){
    const h=opt.h||12, hh=h/2, ls=opt.ls!=null?opt.ls:0.22, perChar=h*(0.6+ls), textLen=text.length*perChar;
    const pts=sample(d,3); if(pts.length<2)return;
    const cum=[0]; for(let i=1;i<pts.length;i++)cum.push(cum[i-1]+Math.hypot(pts[i][0]-pts[i-1][0],pts[i][1]-pts[i-1][1]));
    const ptot=cum[cum.length-1], s0=Math.max(0,Math.min(ptot-textLen,(ptot-textLen)/2+(opt.shift||0))), s1=Math.min(ptot,s0+textLen);
    function ptAt(s){ let i=1; while(i<cum.length&&cum[i]<s)i++; const a=pts[i-1],b=pts[Math.min(i,pts.length-1)],seg=(cum[i]||ptot)-cum[i-1]||1,t=(s-cum[i-1])/seg; return [a[0]+(b[0]-a[0])*t,a[1]+(b[1]-a[1])*t]; }
    function tanAt(s){ const p0=ptAt(Math.max(s0,s-2)),p1=ptAt(Math.min(s1,s+2)); let tx=p1[0]-p0[0],ty=p1[1]-p0[1],l=Math.hypot(tx,ty)||1; return [tx/l,ty/l]; }
    const N=Math.max(10,Math.round((s1-s0)/4)), pos=[],uv=[],idx=[], off=opt.offset||0;
    for(let k=0;k<=N;k++){ const s=s0+(s1-s0)*k/N, p=ptAt(s), tg=tanAt(s), px=-tg[1], py=tg[0];
      const cx2=p[0]+px*off, cy2=p[1]+py*off, u=opt.flipU?1-(s-s0)/((s1-s0)||1):(s-s0)/((s1-s0)||1);
      const lx=cx2+px*hh, ly=cy2+py*hh, rx=cx2-px*hh, ry=cy2-py*hh;
      pos.push(lx-750,ground(lx,ly)+(opt.up||2),ly-525); uv.push(u,opt.flipV?0:1);
      pos.push(rx-750,ground(rx,ry)+(opt.up||2),ry-525); uv.push(u,opt.flipV?1:0); }
    for(let k=0;k<N;k++){ const a=k*2,b=a+1,c2=a+2,d2=a+3; idx.push(a,c2,b,b,c2,d2); }
    const CW=1024, CH=Math.max(32,Math.round(CW*h/((s1-s0)||h))), cv=document.createElement('canvas');
    cv.width=CW; cv.height=CH; const c=cv.getContext('2d'); const fs=CH*0.64;
    c.font=`${opt.weight||400} ${fs}px "JetBrains Mono",monospace`; try{c.letterSpacing=(fs*ls)+'px';}catch(e){}
    c.textAlign='center'; c.textBaseline='middle'; c.fillStyle=opt.color||'rgba(178,150,205,0.8)'; c.fillText(text, CW/2, CH/2);
    const tex=new THREE.CanvasTexture(cv); tex.anisotropy=8;
    const g=new THREE.BufferGeometry(); g.setAttribute('position',new THREE.Float32BufferAttribute(pos,3));
    g.setAttribute('uv',new THREE.Float32BufferAttribute(uv,2)); g.setIndex(idx);
    (opt.layer||LAYERS.covenant).add(new THREE.Mesh(g,new THREE.MeshBasicMaterial({map:tex,transparent:true,opacity:opt.op||0.92,depthWrite:false,side:THREE.DoubleSide})));
  }
  pathLabel('COVENANT LINE', 'M753.71 530.71 L869.84 338.49', {h:10, ls:0.18, offset:7, shift:34, flipU:false, flipV:true, color:'rgba(178,150,205,0.85)', layer:LAYERS.covenant});  // along the NE run east of the house, below the line
  // seasonal stream label — west side of the stream, matched to the covenant text (h/ls/offset)
  pathLabel('SEASONAL STREAM', G.stream[1], {h:10, ls:0.18, offset:7, shift:130, flipU:true, flipV:false, color:'rgba(132,168,224,0.85)', layer:LAYERS.stream});

  // oaks: a trunk + a canopy ring, standing up off the ground
  function ring(x,y,r,upTop,m,parent){ const seg=22,a=[]; for(let i=0;i<=seg;i++){const th=i/seg*Math.PI*2; a.push((x+Math.cos(th)*r)-750, ground(x,y)+upTop, (y+Math.sin(th)*r)-525);} const g=new THREE.BufferGeometry(); g.setAttribute('position',new THREE.Float32BufferAttribute(a,3)); (parent||scene).add(new THREE.Line(g,m)); }
  G.trees.filter(t=>t.x!=null).forEach(t=>{ const top=t.kind==='conif'?16:13, r=t.kind==='conif'?7:11;
    const tg=new THREE.BufferGeometry(); tg.setAttribute('position',new THREE.Float32BufferAttribute([t.x-750,ground(t.x,t.y),t.y-525, t.x-750,ground(t.x,t.y)+top,t.y-525],3)); LAYERS.trees.add(new THREE.Line(tg,mat.trunk));
    ring(t.x,t.y,r,top,mat.tree,LAYERS.trees); });

  // north arrow on the ground (points to survey north = −y / −Z)
  const NARR=[1490,150];
  (function(){ const ax=NARR[0], ay=NARR[1];
    const tip=[ax,ay-46], tail=[ax,ay+46], hl=[ax-9,ay-28], hr=[ax+9,ay-28];
    function seg(a,b){ const A=P3(a[0],a[1],2),B=P3(b[0],b[1],2); const g=new THREE.BufferGeometry();
      g.setAttribute('position',new THREE.Float32BufferAttribute([A.x,A.y,A.z,B.x,B.y,B.z],3)); LAYERS.north.add(new THREE.Line(g,mat.northL)); }
    seg(tail,tip); seg(tip,hl); seg(tip,hr);
    const yt=ay-70, yb=ay-52, xl=ax-7, xr=ax+7;        // 'N' integrated just north of the arrowhead
    seg([xl,yb],[xl,yt]); seg([xl,yt],[xr,yb]); seg([xr,yt],[xr,yb]); })();

  // kinhin trail — draped dotted line (stepping stones) + a length map for the walk
  const traw=sample(G.kinhin,3).map(p=>clampInside(p[0],p[1],8));   // keep the walked loop on-property

  const tpos=traw.map(p=>P3(p[0],p[1],3));
  const tcum=[0]; for(let i=1;i<tpos.length;i++)tcum.push(tcum[i-1]+tpos[i].distanceTo(tpos[i-1]));
  const TLEN=tcum[tcum.length-1];
  function trailAt(t){ const d=((t%1)+1)%1*TLEN; let i=1; while(i<tcum.length&&tcum[i]<d)i++; const a=tpos[i-1],b=tpos[Math.min(i,tpos.length-1)]; const seg=(tcum[i]||TLEN)-tcum[i-1]||1; const k=(d-tcum[i-1])/seg; return a.clone().lerp(b,k); }
  // trail dots
  (function(){ const dots=sample(G.kinhin,9).map(p=>clampInside(p[0],p[1],8)); const a=[]; dots.forEach(p=>{const v=P3(p[0],p[1],3);a.push(v.x,v.y,v.z);});
    const g=new THREE.BufferGeometry(); g.setAttribute('position',new THREE.Float32BufferAttribute(a,3));
    const tex=dotTex('#f0ede6'); const pm=new THREE.PointsMaterial({size:6,map:tex,transparent:true,opacity:.55,depthWrite:false,sizeAttenuation:true});
    LAYERS.trail.add(new THREE.Points(g,pm)); })();
  function dotTex(col){ const c=document.createElement('canvas'); c.width=c.height=64; const x=c.getContext('2d'); const g=x.createRadialGradient(32,32,0,32,32,32); g.addColorStop(0,col); g.addColorStop(.5,col); g.addColorStop(1,'rgba(0,0,0,0)'); x.fillStyle=g; x.beginPath(); x.arc(32,32,32,0,7); x.fill(); const t=new THREE.CanvasTexture(c); return t; }

  // walker
  const walker=new THREE.Sprite(new THREE.SpriteMaterial({map:dotTex('#c9a44e'),transparent:true,opacity:.95,depthWrite:false,depthTest:false}));
  walker.scale.set(26,26,1); walker.visible=false; LAYERS.trail.add(walker);

  // ---------- overlay (projected HTML) ----------
  const OV=[];
  function addOV(el,v3,opt={}){ el.style.position='absolute'; el.style.left='0'; el.style.top='0'; el.style.willChange='transform'; overlay.appendChild(el); const o=Object.assign({el,v3},opt); OV.push(o); return o; }
  function projectOverlays(){ const W=innerWidth,Ht=innerHeight; const cd=camera.position;
    for(const o of OV){ if(o.onlyKinhin&&mode!=='kinhin'){o.el.style.display='none';continue;}
      if(o.kind==='anno'&&!LSTATE.annotations){o.el.style.display='none';continue;}
      if(o.kind==='label')o.el.classList.toggle('showtext',LSTATE.labels);
      const v=o.v3.clone().project(camera);
      if(v.z>1){o.el.style.display='none';continue;}
      o.el.style.display='';
      const x=Math.round((v.x*.5+.5)*W), y=Math.round((-v.y*.5+.5)*Ht);
      o.el.style.transform='translate3d('+x+'px,'+y+'px,0) translate(-50%,-50%)';  // GPU transform (no layout reflow) keeps labels locked to the canvas
    } }

  // ============================ TIMELINE BEADS ============================
  const Y0=1930,Y1=2024, tOf=y=>(Math.max(Y0,Math.min(Y1,y))-Y0)/(Y1-Y0);
  let mode='overview';
  const beads=[];
  TL.events.slice().sort((a,b)=>a.y-b.y).forEach(e=>{ const t=tOf(e.y), c=HK.col(e);
    const b=document.createElement('div'); b.className='bead'+(e.key?' key':'')+((e.arch||e.archive)?' arch':'');
    b.style.background=(e.arch||e.archive)?'var(--scene)':c; b.style.borderColor=c; b.style.color=c;
    b.addEventListener('click',ev=>{ev.stopPropagation();detail.select(e,b);});
    const o=addOV(b,trailAt(t),{onlyKinhin:true}); o._t=t; b._t=t; beads.push(o);
  });

  const slider=document.getElementById('slider'), now=document.getElementById('now');
  function setWalk(t){ walker.position.copy(trailAt(t)); now.textContent=Math.round(Y0+t*(Y1-Y0)); slider.style.setProperty('--p',(t*100)+'%');
    beads.forEach(o=>o.el.classList.toggle('dim',o._t>t+0.004)); }
  slider.addEventListener('input',()=>setWalk(slider.value/1000));

  // ============================ PLACES ============================
  const lakeC=(()=>{const n=G.lake[0].match(/-?[\d.]+/g).map(Number);let sx=0,sy=0,c=0;for(let i=0;i+1<n.length;i+=2){sx+=n[i];sy+=n[i+1];c++;}return[sx/c,sy/c];})();
  const trailC=(()=>{let sx=0,sy=0;traw.forEach(p=>{sx+=p[0];sy+=p[1];});return[sx/traw.length,sy/traw.length];})();
  const Pt=G.points;
  const PLACES=[
    { id:'kinhin', tier:'timeline', label:'Kinhin trail', kind:'Trail', col:'#f0ede6', sq:false, noLabel:true,
      anchor:P3(trailC[0],trailC[1],82), focus:P3(trailC[0],trailC[1],8), dist:1040, pin:0,
      detail:{title:'Kinhin Trail',kind:'WALKING MEDITATION',_c:'#f0ede6',place:'203 Goward Rd',
        note:'Kinhin is walking zazen — meditation in motion. The loop Hunter wore into his own ground becomes the spine of the timeline: walk it, and you walk his life from 1930 onward.'} },
    { id:'house', tier:'panel', label:'Hunter House', kind:'', col:'#c9a44e', sq:true, noLabel:true,
      anchor:P3(HOUSE[0],HOUSE[1],26), focus:P3(HOUSE[0],HOUSE[1],8), dist:660, pin:0,
      panel:{ kind:'Hunter House', dt:'1970–73 · 203 Goward Rd, Saanich', title:'Hunter House',
        img:'../assets/hunter-house-1970.png', imgtag:'Hunter Residence · c.1970',
        body:'Architect, client and resident, all Hunter. He drew it, built it, and reworked it for fifty years — the single footprint the whole archive turns around. The house sits on the knoll, set <em>into</em> the Garry oak meadow, the ground falling away toward the lake.',
        stats:[['59','surveyed segments'],['1970','first built'],['203','Goward Rd']] } },
    { id:'spring', tier:'caption', label:'Spring', kind:'Covenant map', col:'#6f93c9', sq:false, noLabel:true,
      anchor:P3(Pt.spring.x,Pt.spring.y,16), focus:P3(Pt.spring.x,Pt.spring.y,6), dist:300, pin:14,
      detail:{title:'Spring',kind:'COVENANT MAP',_c:'#6f93c9',place:'203 Goward Rd',
        note:'A spring rising at the eastern edge of the property — the far, high turn of the walk, where the loop bends back toward the house.'} },
    { id:'lake', tier:'caption', label:'Prospect Lake', kind:'Borrowed view', col:'#6f93c9', sq:false, noLabel:true,
      anchor:P3(lakeC[0],lakeC[1],18), focus:P3(lakeC[0],lakeC[1],6), dist:720, pin:0,
      detail:{title:'Prospect Lake',kind:'BORROWED VIEW (SHAKKEI)',_c:'#6f93c9',place:'203 Goward Rd',
        note:'The borrowed view, and the lowest ground. The covenant written into the title exists for one reason: to keep the sightline from the house down to the water open, forever.'} },
    { id:'largeTree', tier:'zoom', label:'Large Tree', kind:'Covenant map', col:'#7aaa98', sq:false, hidden:true,
      anchor:P3(Pt.largeTree.x,Pt.largeTree.y,18), focus:P3(Pt.largeTree.x,Pt.largeTree.y,8), dist:440, pin:16 },
    { id:'fig', tier:'zoom', label:'Dead Fig', kind:'Covenant map', col:'#9a958b', sq:false, noLabel:true,
      anchor:P3(Pt.fig.x,Pt.fig.y,16), focus:P3(Pt.fig.x,Pt.fig.y,8), dist:440, pin:14 },
  ];
  const plMap={};
  // ---------- fixed 3D icons (real geometry — never billboard to camera) ----------
  function icon3d(kind,x,y,colHex){
    const g=new THREE.Group(); const z=ground(x,y); g.position.set(x-750,z,y-525);
    const m=new THREE.LineBasicMaterial({color:colHex,transparent:true,opacity:.85});
    const mk=arr=>{ const b=new THREE.BufferGeometry(); b.setAttribute('position',new THREE.Float32BufferAttribute(arr,3)); g.add(new THREE.Line(b,m)); };
    const ring=(cx,cy,cz,r,seg=26)=>{ const a=[]; for(let i=0;i<=seg;i++){const t=i/seg*Math.PI*2;a.push(cx+Math.cos(t)*r,cy,cz+Math.sin(t)*r);} mk(a); };
    // text curved along a circle, laid FLAT on the ground (orbits naturally with the model)
    function curvedText(text,radius,opt={}){ const h=opt.h||3.6, ls=opt.ls!=null?opt.ls:0.34;
      const perChar=h*1.7*(0.55+ls), arc=Math.min(Math.PI*1.7,(text.length*perChar)/radius);
      const c0=(opt.center!=null?opt.center:Math.PI/2), a0=c0-arc/2, a1=c0+arc/2, N=Math.max(20,text.length*5);
      const pos=[],uv=[],idx=[];
      for(let k=0;k<=N;k++){ const t=k/N, th=a0+(a1-a0)*t, ct=Math.cos(th), st=Math.sin(th);
        pos.push(ct*(radius+h),(opt.y||1),st*(radius+h)); uv.push(t,opt.flip?1:0);
        pos.push(ct*(radius-h),(opt.y||1),st*(radius-h)); uv.push(t,opt.flip?0:1); }
      for(let k=0;k<N;k++){ const a=k*2,b=a+1,c=a+2,d=a+3; idx.push(a,c,b,b,c,d); }
      const CW=1024, CH=Math.max(40,Math.round(CW*(2*h)/(((a1-a0)*radius)||1))), cv=document.createElement('canvas');
      cv.width=CW; cv.height=CH; const cx=cv.getContext('2d'); const fs=CH*0.62;
      cx.font='400 '+fs+'px "JetBrains Mono",monospace'; try{cx.letterSpacing=(fs*ls)+'px';}catch(e){}
      cx.textAlign='center'; cx.textBaseline='middle'; cx.fillStyle=opt.color||'rgba(132,168,224,0.9)'; cx.fillText(text,CW/2,CH/2);
      const tex=new THREE.CanvasTexture(cv); tex.anisotropy=8;
      const bg=new THREE.BufferGeometry(); bg.setAttribute('position',new THREE.Float32BufferAttribute(pos,3));
      bg.setAttribute('uv',new THREE.Float32BufferAttribute(uv,2)); bg.setIndex(idx);
      g.add(new THREE.Mesh(bg,new THREE.MeshBasicMaterial({map:tex,transparent:true,opacity:opt.op||0.92,depthWrite:false,side:THREE.DoubleSide}))); }
    if(kind==='spring'){
      // Hunter's spring, drawn as a fan emblem (tuned in spring-lab): symmetric
      // PAIRS of jets leave the basin almost vertical, then flare up & outward like
      // a trumpet opening — static strokes at the site's line weight, with a
      // detached droplet tick floating above the centre. Pool matched to the
      // stream connector. No label. (Opacity driven on focus in updFx.)
      const SP={ count:4, spread:220, height:9, reach:7, steep:0.9 };
      let _seed=7; const rnd=()=>{ _seed=(_seed*9301+49297)%233280; return _seed/233280-0.5; };
      function jetCurve(f){
        const a=Math.abs(f), dir=f<0?-1:1;
        const lean=0.45+0.55*(SP.spread/360);
        const reachX=dir*(0.35+a*SP.reach)*lean*a + dir*0.25*a;   // ∝ a → inner jets stay near-vertical
        const tipY=SP.height*(1.05-0.45*a);                       // inner streams tallest, outer shorter & flared
        const zj=rnd()*0.35;                                      // faint depth jitter
        const S=new THREE.Vector3(f*0.30,0.15,zj);
        const E=new THREE.Vector3(reachX,tipY,zj);
        const C=new THREE.Vector3(reachX*0.16, tipY*(0.82-0.24*(SP.steep-0.9)), zj+rnd()*0.2);
        return new THREE.QuadraticBezierCurve3(S,C,E);
      }
      const jets=[]; g.userData.jets=jets;
      const n=SP.count, maxRank=Math.ceil(n/2);
      for(let j=0;j<n;j++){
        const rank=Math.floor(j/2)+1, side=(j%2===0)?-1:1, f=side*(rank/maxRank);   // ±… across the fan, never dead-centre
        const cpts=jetCurve(f).getPoints(46), arr=[];
        cpts.forEach(p=>arr.push(p.x,p.y,p.z));
        const lg=new THREE.BufferGeometry(); lg.setAttribute('position',new THREE.Float32BufferAttribute(arr,3));
        const pm=m.clone(); g.add(new THREE.Line(lg,pm)); jets.push({mat:pm});
      }
      // detached droplet tick floating above the centre
      { const y0=SP.height*1.06, y1=y0+Math.max(1.1,SP.height*0.12);
        const tg=new THREE.BufferGeometry(); tg.setAttribute('position',new THREE.Float32BufferAttribute([0,y0,0, 0,y1,0],3));
        const tm=m.clone(); g.add(new THREE.Line(tg,tm)); jets.push({mat:tm}); }
      // small source pool — outline matched to Prospect Lake (0x7ba0d6 @ .6) + faint fill.
      // PERFECT CIRCLE: radius chosen so the stream connector (SVG 1094.9,447.6) still
      // meets the edge — center SVG (1101.16,446.23), scale 1.95 → 3.286 local units.
      const R=3.286, rad=t=>R;
      const out=[]; for(let i=0;i<=64;i++){ const t=i/64*Math.PI*2, r=rad(t); out.push(Math.cos(t)*r,0.2,Math.sin(t)*r); }
      const og=new THREE.BufferGeometry(); og.setAttribute('position',new THREE.Float32BufferAttribute(out,3));
      g.add(new THREE.Line(og,new THREE.LineBasicMaterial({color:0x7ba0d6,transparent:true,opacity:0.6})));
      const verts=[0,0.12,0],idx=[]; for(let i=0;i<=64;i++){ const t=i/64*Math.PI*2, r=rad(t); verts.push(Math.cos(t)*r,0.12,Math.sin(t)*r); }
      for(let i=1;i<=64;i++) idx.push(0,i,i+1);
      const fg=new THREE.BufferGeometry(); fg.setAttribute('position',new THREE.Float32BufferAttribute(verts,3)); fg.setIndex(idx);
      g.add(new THREE.Mesh(fg,new THREE.MeshBasicMaterial({color:0x3a5680,transparent:true,opacity:0.16,side:THREE.DoubleSide,depthWrite:false})));
    } else if(kind==='fig'){
      // dead fig — a LOW, WIDE sprawl: many gnarled stems from near the ground,
      // arching out 360° and drooping at the tips (wider than tall), per the photo.
      const stub=[0,2.5,0]; mk([0,0,0, stub[0],stub[1],stub[2]]);     // barely-there trunk
      const N=9;
      for(let i=0;i<N;i++){ const ang=(i/N)*Math.PI*2 + (i*0.7), reach=10+(i%3)*3.5;
        const dx=Math.cos(ang), dz=Math.sin(ang);
        // stems arch out then keep climbing — tips head UP, not drooping
        const a1=[stub[0]+dx*reach*0.5, stub[1]+4+(i%2)*1.5, stub[2]+dz*reach*0.5];
        const a2=[stub[0]+dx*reach*0.85, stub[1]+8.5-(i%2), stub[2]+dz*reach*0.85];
        const tip=[stub[0]+dx*reach, stub[1]+13.5, stub[2]+dz*reach];  // rises at the end
        mk([stub[0],stub[1],stub[2], a1[0],a1[1],a1[2]]);
        mk([a1[0],a1[1],a1[2], a2[0],a2[1],a2[2]]);
        mk([a2[0],a2[1],a2[2], tip[0],tip[1],tip[2]]);
        // a forked twig, also continuing upward
        const fk=[a2[0]+dx*3, a2[1]+3.5, a2[2]+dz*3 + (i%2?2.5:-2.5)];
        mk([a2[0],a2[1],a2[2], fk[0],fk[1],fk[2]]);
        mk([fk[0],fk[1],fk[2], fk[0]+dx*1.5, fk[1]+3.5, fk[2]+dz*1.5]);  // twig tip rises
      }
    }
    scene.add(g); return g;
  }
  const springIcon=icon3d('spring', Pt.spring.x, Pt.spring.y, 0x6f93c9); springIcon.scale.setScalar(1.95);
  // connector: an organic S-curve from the EDGE of the spring pond to a definite
  // point on the seasonal stream (1044,459), arriving at an acute angle heading
  // south. Draped flush on the terrain (up=0, same as the stream) so they touch.
  (function(){ drape('M1094.9 447.6 C 1078 452 1051 438 1044 459', mat.stream, 2, 0, false, LAYERS.stream);
  })();
  const figIcon=icon3d('fig',    Pt.fig.x,    Pt.fig.y,    0x9a958b); figIcon.scale.setScalar(0.72);

  PLACES.forEach(pl=>{ plMap[pl.id]=pl;
    if(pl.hidden){ pl._lab={classList:{add(){},remove(){},toggle(){}}}; return; }   // hidden place: no marker, not shown
    // survey pin (vertical tick) for point places
    if(pl.pin){ const x=pl.anchor.x+750, y=pl.anchor.z+525; const g=new THREE.BufferGeometry();
      g.setAttribute('position',new THREE.Float32BufferAttribute([x-750,ground(x,y),y-525, x-750,ground(x,y)+pl.pin,y-525],3));
      LAYERS.labels.add(new THREE.Line(g,new THREE.LineBasicMaterial({color:parseInt(pl.col.slice(1),16),transparent:true,opacity:.55}))); }
    if(pl.noLabel){ pl._lab={classList:{add(){},remove(){},toggle(){}}}; return; }   // no floating dot/label (e.g. spring uses its ground logo)
    const el=document.createElement('div'); el.className='plab'+(pl.sq?' sq':''); el.style.color=pl.col; el.style.cursor=curPick;
    el.innerHTML='<span class="dot"></span><span class="tx">'+(pl.kind?'<b>'+pl.kind+'</b>':'')+pl.label+'</span>';
    el.addEventListener('mouseenter',()=>el.classList.add('hot'));
    el.addEventListener('mouseleave',()=>{if(mode!==pl.id)el.classList.remove('hot');});
    el.addEventListener('click',ev=>{ev.stopPropagation();enter(pl);});
    addOV(el,pl.anchor,{kind:'label'}); pl._lab=el;
  });

  // in-world annotations (non-interactive): meadow, address, north
  const annos=[];
  function anno(cls,txt,x,y,up){ const el=document.createElement('div'); el.className='anno '+cls; el.textContent=txt;
    const o=addOV(el,P3(x,y,up),{kind:'anno'}); annos.push(o); return o; }
  anno('meadow','Garry Oak Meadow', HOUSE[0]-255, HOUSE[1]+45, 18);

  // ============================ FLY / STATE ============================
  let flying=0;
  function flyTo(focus,dist,dur=1150,forceDir){ flying++; controls.enabled=false;
    const fromP=camera.position.clone(), fromT=controls.target.clone();
    let dir; if(forceDir){dir=forceDir.clone().normalize();} else {dir=fromP.clone().sub(fromT); if(dir.length()<1)dir.copy(OVR.dir); dir.normalize();}
    const toT=focus.clone(), toP=toT.clone().add(dir.multiplyScalar(dist));
    const t0=performance.now(), id=flying;
    (function fr(nw){ if(id!==flying)return; let k=Math.min(1,(nw-t0)/dur); k=k<.5?4*k*k*k:1-Math.pow(-2*k+2,3)/2;
      camera.position.lerpVectors(fromP,toP,k); controls.target.lerpVectors(fromT,toT,k); camera.lookAt(controls.target);
      if(k<1)requestAnimationFrame(fr); else {controls.enabled=true; controls.update();} })(t0);
  }

  const crumbs=document.getElementById('crumbs'), backbtn=document.getElementById('backbtn'),
        panel=document.getElementById('panel'), panelcard=document.getElementById('panelcard'),
        bar=document.getElementById('bar'), hint=document.getElementById('hint'), orbithint=document.getElementById('orbithint');

  function buildPanel(pl){ const p=pl.panel;
    panelcard.innerHTML=`<button class="dx" aria-label="Close">×</button>`+
      (p.img?`<div class="ph"><img src="${p.img}" alt=""><div class="ph-tag">${p.imgtag||''}</div></div>`:'')+
      `<div class="body"><div class="k">${p.kind}</div><div class="dt">${p.dt}</div><h2>${p.title}</h2><p>${p.body}</p>`+
      (p.stats?`<div class="stats">${p.stats.map(s=>`<div class="stat"><div class="n">${s[0]}</div><div class="l">${s[1]}</div></div>`).join('')}</div>`:'')+`</div>`;
    panelcard.querySelector('.dx').addEventListener('click',ev=>{ev.stopPropagation();toOverview();});
  }

  function enter(pl){ mode=pl.id; detail.deselect();
    flyTo(pl.focus,pl.dist);
    crumbs.innerHTML=`<span class="root">Whole site</span><span class="sep">/</span><span class="here">${pl.label}</span>`;
    crumbs.classList.add('on'); backbtn.classList.add('on'); topbtn.classList.remove('on'); hint.classList.add('gone'); orbithint.classList.add('gone');
    annos.forEach(a=>a.el.classList.add('gone'));
    PLACES.forEach(p=>{ p._lab.classList.toggle('faded',p.id!==pl.id); p._lab.classList.toggle('hot',p.id===pl.id); });
    panel.classList.toggle('on',pl.tier==='panel');
    bar.classList.toggle('on',pl.tier==='timeline');
    walker.visible=(pl.tier==='timeline');
    if(pl.tier==='panel') buildPanel(pl);
    if(pl.tier==='timeline'){ slider.value=1000; setWalk(1); }
    if(pl.tier==='caption') detail.select(pl.detail,null);
    if(window.parent!==window){ try{ parent.postMessage({type:'site-place', label:pl.label},'*'); }catch(e){} }   // breadcrumb in browse
  }
  function toOverview(){ mode='overview'; flyTo(OVR.tar,OVR.dist,1150,OVR.dir); detail.deselect();
    if(window.parent!==window){ try{ parent.postMessage({type:'site-place', label:null},'*'); }catch(e){} }   // clear breadcrumb in browse
    crumbs.classList.remove('on'); backbtn.classList.remove('on'); topbtn.classList.add('on'); hint.classList.remove('gone'); orbithint.classList.remove('gone');
    annos.forEach(a=>a.el.classList.remove('gone'));
    panel.classList.remove('on'); bar.classList.remove('on'); walker.visible=false;
    PLACES.forEach(p=>{ p._lab.classList.remove('faded'); p._lab.classList.remove('hot'); });
  }
  // click the house → contours go haywire, then the zoom tapers and eases into a
  // near-top-down perch above the roof as the lines settle. Burst + fly share DUR.
  function enterHouse(){ if(mode==='house')return; mode='house'; detail.deselect();
    const DUR=2200;
    kickHouseFx(DUR);
    const dir=new THREE.Vector3(0, Math.cos(0.30), Math.sin(0.30)).normalize();   // mostly overhead, a slight south tilt
    flyTo(P3(HOUSE[0],HOUSE[1],8), 285, DUR, dir);
    crumbs.innerHTML=`<span class="root">Whole site</span><span class="sep">/</span><span class="here">Hunter House</span>`;
    crumbs.classList.add('on'); backbtn.classList.add('on'); topbtn.classList.remove('on'); hint.classList.add('gone'); orbithint.classList.add('gone');
    annos.forEach(a=>a.el.classList.add('gone'));
    PLACES.forEach(p=>{ p._lab.classList.toggle('faded',p.id!=='house'); p._lab.classList.toggle('hot',p.id==='house'); });
    if(window.parent!==window){ try{ parent.postMessage({type:'site-place', label:'Hunter House'},'*'); }catch(e){} }
  }
  backbtn.addEventListener('click',toOverview);

  // ---- kinhin → timeline: project the trail's vertices to the exact pixels they
  // occupy on screen, hand them to the timeline (which redraws the line right there
  // and morphs it into the ring). The camera DIVES straight down into the loop —
  // centring and zooming until it fills the frame — while everything else abstracts
  // away to the dark; then the loop's screen points hand off to the timeline. ----
  let lifting=false, liftBase=null, liftLine=null;
  const _ease=t=>t<.5?4*t*t*t:1-Math.pow(-2*t+2,3)/2;
  function collectFadeMats(){ const set=new Map();
    scene.traverse(o=>{ const m=o.material; if(!m)return; (Array.isArray(m)?m:[m]).forEach(mm=>{ if(mm&&mm.transparent&&!set.has(mm)) set.set(mm,mm.opacity); }); });
    return set; }
  function projectTrail(){ const w=innerWidth,h=innerHeight,out=[],v=new THREE.Vector3();
    for(const p of tpos){ v.copy(p).project(camera); out.push([(v.x*0.5+0.5)*w,(-v.y*0.5+0.5)*h]); } return {pts:out,w,h}; }
  function kinhinLiftoff(){
    if(lifting)return; lifting=true; mode='lift'; controls.enabled=false; detail.deselect();
    overlay.style.transition='opacity .4s ease'; overlay.style.opacity='0';      // hide projected HTML beads
    icontip.classList.remove('on');          // drop the "Kinhin trail" hover label at once
    LAYERS.trail.visible=false;              // the original loop vanishes INSTANTLY on click — the timeline's
                                             // line (handed off below, at the exact same screen position) is the
                                             // single loop that morphs into the ring. No lingering map loop.
    const hand=projectTrail();
    if(window.parent!==window){ try{ parent.postMessage({type:'open-timeline', handoff:hand},'*'); }catch(_e){} }
    setTimeout(resetLift, 2700);   // restore once the parent has faded this layer out and hidden it
  }
  function resetLift(){ if(liftLine){ scene.remove(liftLine); liftLine.geometry.dispose(); liftLine.material.dispose(); liftLine=null; }
    LAYERS.trail.visible=true;
    if(liftBase){ liftBase.forEach((b,m)=>{ m.opacity=b; }); liftBase=null; }
    overlay.style.transition=''; overlay.style.opacity=''; if(mode==='lift')mode='overview'; controls.enabled=true; lifting=false; applyPose(OVR); }


  // ---- splash → site: fly the wide title pose down into the working plan view;
  // panels slide back in from their edges (the reverse of the splash exit) ----
  function enterSite(){ if(!introActive)return; introActive=false;
    const _i=document.getElementById('intro'); if(_i)_i.classList.add('gone');
    document.body.classList.remove('intro-active');
    flyTo(OVR.tar, OVR.dist, 2000, OVR.dir);
    if(EMBED){ try{ parent.postMessage({type:'site-entered'},'*'); }catch(e){} }   // tell browse to go full-bleed
  }
  function replayIntro(){ if(introActive)return; mode='overview';
    detail.deselect(); panel.classList.remove('on'); bar.classList.remove('on'); walker.visible=false;
    crumbs.classList.remove('on'); backbtn.classList.remove('on');
    PLACES.forEach(p=>{ p._lab.classList.remove('faded'); p._lab.classList.remove('hot'); });
    const _i=document.getElementById('intro'); if(_i)_i.classList.remove('gone');
    document.body.classList.add('intro-active');
    flying++; controls.enabled=false; introActive=true;   // loop's intro motion eases the camera back out to the title pose
  }
  { const ie=document.getElementById('i-enter'); if(ie)ie.addEventListener('click',enterSite); }
  renderer.domElement.addEventListener('pointerdown',()=>{ if(introActive)enterSite(); }, true);
  addEventListener('wheel',()=>{ if(introActive)enterSite(); }, {passive:true});
  addEventListener('keydown',e=>{ if(introActive && e.key!=='Escape')enterSite(); });
  { const ftag=document.querySelector('.formtag'); if(ftag){ ftag.style.cursor='pointer'; ftag.title='Replay the opening'; ftag.addEventListener('click',replayIntro); } }

  // host (browse) messages: zoom in from the held wide frame, or reset back to it
  function _northUp(){ const off=camera.position.clone().sub(controls.target); const dist=off.length()||1;
    const horiz=Math.max(1e-3,Math.hypot(off.x,off.z)); const dir=new THREE.Vector3(0,off.y,horiz).normalize();
    flyTo(controls.target.clone(), dist, 900, dir); }   // keep tilt+zoom, reorient so north (−Z) is up
  let _is3D=false;
  function _planToggle(){ _is3D=!_is3D;
    if(_is3D){ const dir=new THREE.Vector3(0,Math.cos(0.92),Math.sin(0.92)).normalize(); flyTo(OVR.tar.clone(), OVR.dist*0.82, 1000, dir); }
    else { flyTo(OVR.tar.clone(), OVR.dist, 1000, OVR.dir.clone()); } }
  addEventListener('message',function(e){ const d=e&&e.data; if(!d||typeof d!=='object')return;
    if(d.type==='site-zoom'){ enterSite(); }                                   // fly in from the held wide frame
    else if(d.type==='site-reset'){ resetLift(); introActive=true; controls.enabled=false; introPose(0); document.body.classList.add('intro-active'); const _i=document.getElementById('intro'); if(_i){ _i.style.display=''; _i.classList.remove('gone'); } }  // snap back to the splash/holding frame (sync)
    else if(d.type==='site-fit'){ _is3D=false; if(mode!=='overview')toOverview(); else flyTo(OVR.tar,OVR.dist,900,OVR.dir); }   // whole-site view
    else if(d.type==='site-north'){ _northUp(); }
    else if(d.type==='site-plan'){ _planToggle(); }
  });
  const topbtn=document.getElementById('topbtn'); topbtn.addEventListener('click',toOverview); topbtn.classList.add('on');
  const recenterbtn=document.getElementById('recenterbtn'); recenterbtn.classList.add('on');
  recenterbtn.addEventListener('click',()=>{ mode='overview'; const f=P3(HOUSE[0],HOUSE[1],8);
    crumbs.classList.remove('on'); backbtn.classList.remove('on'); topbtn.classList.add('on'); hint.classList.remove('gone'); orbithint.classList.remove('gone');
    panel.classList.remove('on'); bar.classList.remove('on'); walker.visible=false; detail.deselect();
    PLACES.forEach(p=>{ p._lab.classList.remove('faded'); p._lab.classList.remove('hot'); });
    flyTo(f, 520); });
  document.addEventListener('keydown',ev=>{ if(ev.key==='Escape'){ if(mode!=='overview')toOverview(); else if(window.parent!==window){ try{parent.postMessage({type:'site-close'},'*');}catch(e){} } } });

  // background click (not a drag, not on a label) → enter the icon under the cursor
  // (spring or fig — both are real line geometry) or back out
  const raycaster=new THREE.Raycaster(); raycaster.params.Line.threshold=5;
  // returns the place id whose icon is under the pointer, or null
  const kinhinHit=new THREE.Line(new THREE.BufferGeometry().setFromPoints(tpos), new THREE.LineBasicMaterial({visible:false})); scene.add(kinhinHit);
  function hitIcon(e){ const r=renderer.domElement.getBoundingClientRect();
    const mx=((e.clientX-r.left)/r.width)*2-1, my=-((e.clientY-r.top)/r.height)*2+1;
    raycaster.setFromCamera({x:mx,y:my},camera);
    if(raycaster.intersectObject(springIcon,true).length>0) return 'spring';
    if(raycaster.intersectObject(figIcon,true).length>0) return 'fig';
    if(raycaster.intersectObject(kinhinHit).length>0) return 'kinhin';
    if(houseMeshRef && raycaster.intersectObject(houseMeshRef).length>0) return 'house';
    return null; }
  let downXY=null;
  renderer.domElement.addEventListener('pointerdown',e=>{downXY=[e.clientX,e.clientY];curDragging=true;curDragMode=(e.shiftKey||e.button===2)?'pan':'orbit';refreshCursor();});
  // hover tooltip for the point features (replaces the old focus-pull blur)
  const icontip=document.createElement('div'); icontip.className='icontip'; document.body.appendChild(icontip);
  const ICONDESC={ fig:'Dead Fig Tree', spring:'A Spring', kinhin:'Kinhin trail', house:'Hunter House' };
  function descFor(id){ return ICONDESC[id] || (plMap[id]&&plMap[id].label) || ''; }
  renderer.domElement.addEventListener('pointermove',e=>{ if(introActive)return; if(curDragging)return;
    const h=hitIcon(e); curHover=!!h; refreshCursor();
    if(h){ icontip.textContent=descFor(h); icontip.style.left=(e.clientX+15)+'px'; icontip.style.top=(e.clientY+16)+'px'; icontip.classList.add('on'); }
    else icontip.classList.remove('on'); });
  addEventListener('pointerup',e=>{ if(introActive){curDragging=false;return;} curDragging=false; if(!downXY){refreshCursor();return;} const moved=Math.hypot(e.clientX-downXY[0],e.clientY-downXY[1]); const onCanvas=e.target===renderer.domElement; downXY=null;
    const hit=hitIcon(e); curHover=!!hit; refreshCursor();
    if(moved<5&&onCanvas){
      if(hit==='kinhin'){ if(window.parent!==window){ kinhinLiftoff(); } else if(mode!=='kinhin') enter(plMap.kinhin); return; }   // kinhin → lift-off → timeline
      if(hit==='house'){ enterHouse(); return; }   // house → haywire contours + ease in above the roof
      if(hit&&mode!==hit){ enter(plMap[hit]); return; } if(mode!=='overview')toOverview(); else detail.deselect(); } });

  // ---------- layer control panel (persisted on/off state) ----------
  (function(){
    const NAMES={contours:'Contours',boundary:'Site boundary',house:'House',trees:'Garry oaks',trail:'Kinhin trail',paths:'Garden path',lake:'Lake',stream:'Stream',covenant:'Covenant area',roads:'Roads',labels:'Place labels',annotations:'Notes (meadow)',north:'North arrow'};
    const wrap=document.createElement('div'); wrap.className='layers'; wrap.innerHTML='<div class="lh">Layers</div>';
    const list=document.createElement('div'); list.className='llist'; wrap.appendChild(list);
    LKEYS.forEach(k=>{ const row=document.createElement('button'); row.className='lrow'; row.dataset.k=k;
      row.innerHTML='<span class="lsw"></span><span class="lnm">'+NAMES[k]+'</span>';
      row.addEventListener('click',()=>{ LSTATE[k]=!LSTATE[k]; applyLayers(); sync(); });
      list.appendChild(row); });
    // contour opacity slider (live + persisted)
    let cOp=parseFloat(localStorage.getItem('hh3d-contour-op')); if(isNaN(cOp))cOp=mat.contour.opacity; mat.contour.opacity=cOp;
    const sl=document.createElement('div'); sl.className='lslider'; sl.innerHTML='<div class="lsl-lab">Contour opacity <b>'+cOp.toFixed(2)+'</b></div>';
    const inp=document.createElement('input'); inp.type='range'; inp.min='0'; inp.max='0.7'; inp.step='0.01'; inp.value=cOp;
    inp.addEventListener('input',()=>{ const v=parseFloat(inp.value); mat.contour.opacity=v; sl.querySelector('b').textContent=v.toFixed(2); try{localStorage.setItem('hh3d-contour-op',v);}catch(e){} });
    sl.appendChild(inp); wrap.appendChild(sl);
    // water (lake) opacity slider
    let wOp=parseFloat(localStorage.getItem('hh3d-lake-op')); if(isNaN(wOp))wOp=mat.lakeFill.opacity; mat.lakeFill.opacity=wOp;
    const sl2=document.createElement('div'); sl2.className='lslider'; sl2.innerHTML='<div class="lsl-lab">Water opacity <b>'+wOp.toFixed(2)+'</b></div>';
    const inp2=document.createElement('input'); inp2.type='range'; inp2.min='0'; inp2.max='1'; inp2.step='0.01'; inp2.value=wOp;
    inp2.addEventListener('input',()=>{ const v=parseFloat(inp2.value); mat.lakeFill.opacity=v; sl2.querySelector('b').textContent=v.toFixed(2); try{localStorage.setItem('hh3d-lake-op',v);}catch(e){} });
    sl2.appendChild(inp2); wrap.appendChild(sl2);
    if(typeof plLabel!=='undefined'&&plLabel){
      let pOp=parseFloat(localStorage.getItem('hh3d-plake-op')); if(isNaN(pOp))pOp=plLabel.material.opacity; plLabel.material.opacity=pOp;
      const sl3=document.createElement('div'); sl3.className='lslider'; sl3.innerHTML='<div class="lsl-lab">Lake label opacity <b>'+pOp.toFixed(2)+'</b></div>';
      const inp3=document.createElement('input'); inp3.type='range'; inp3.min='0'; inp3.max='1'; inp3.step='0.01'; inp3.value=pOp;
      inp3.addEventListener('input',()=>{ const v=parseFloat(inp3.value); plLabel.material.opacity=v; sl3.querySelector('b').textContent=v.toFixed(2); try{localStorage.setItem('hh3d-plake-op',v);}catch(e){} });
      sl3.appendChild(inp3); wrap.appendChild(sl3);
    }
    const read=document.createElement('div'); read.className='lstate'; read.title='click to copy state';
    read.addEventListener('click',()=>{ try{navigator.clipboard.writeText(JSON.stringify(LSTATE));}catch(e){} });
    wrap.appendChild(read); document.body.appendChild(wrap);
    function sync(){ [...list.children].forEach(r=>r.classList.toggle('off',!LSTATE[r.dataset.k])); }
    window.__updReadout=function(){ read.textContent='on — '+LKEYS.filter(k=>LSTATE[k]).join(' · '); };
    sync();
  })();
  applyLayers();

  // ---------- post: focus-pull blur centered on the fig ----------
  // Sharp at the fig's screen position, blurring + draining color toward the
  // edges. A 16-tap golden-angle disk whose radius grows with screen-distance
  // from the fig and with figAmt; periphery also desaturates ("the world quiets").
  const FocusShader={
    uniforms:{ tDiffuse:{value:null}, uCenter:{value:new THREE.Vector2(0.5,0.5)},
      uAmt:{value:0}, uAspect:{value:innerWidth/innerHeight} },
    vertexShader:'varying vec2 vUv;void main(){vUv=uv;gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.0);}',
    fragmentShader:[
      'uniform sampler2D tDiffuse;uniform vec2 uCenter;uniform float uAmt;uniform float uAspect;varying vec2 vUv;',
      'void main(){',
      '  vec2 d=vUv-uCenter; d.x*=uAspect; float dist=length(d);',
      '  float focus=smoothstep(0.05,0.5,dist);',
      '  float radius=focus*uAmt*0.033;',
      '  if(radius<0.0006){ gl_FragColor=texture2D(tDiffuse,vUv); return; }',
      '  vec4 sum=vec4(0.0);',
      '  for(int i=0;i<16;i++){ float fi=float(i); float ang=fi*2.3999632;',
      '    float r=sqrt((fi+0.5)/16.0)*radius; vec2 off=vec2(cos(ang),sin(ang))*r; off.x/=uAspect;',
      '    sum+=texture2D(tDiffuse, vUv+off); }',
      '  vec4 c=sum/16.0;',
      '  float lum=dot(c.rgb, vec3(0.299,0.587,0.114));',
      '  c.rgb=mix(c.rgb, vec3(lum)*0.8, focus*uAmt*0.55);',
      '  gl_FragColor=c;',
      '}'
    ].join('\n')
  };
  const composer=new THREE.EffectComposer(renderer);
  composer.addPass(new THREE.RenderPass(scene,camera));
  const focusPass=new THREE.ShaderPass(FocusShader); focusPass.renderToScreen=true; composer.addPass(focusPass);

  let figAmt=0, springAmt=0;
  const _figWorld=new THREE.Vector3(), _fw=new THREE.Vector3();
  // Host-driven contour excitation (e.g. the tilt landing): a tight, subtle
  // radial tremor in the contour lines under a world point. Dormant (amt 0)
  // unless a parent page calls window.__setCursorFx — the normal lens is
  // untouched. Reuses the (otherwise idle) fig-swell uniforms.
  const cursorFx={x:0,z:0,amt:0,inner:4,outer:120};
  window.__setCursorFx=function(x,z,amt,outer){ cursorFx.x=x; cursorFx.z=z;
    cursorFx.amt=amt||0; if(outer)cursorFx.outer=outer; };
  // house-click burst: kicked by enterHouse(), consumed each frame in updFx. One
  // eased timeline (same dur as the fly-to) — contours go haywire, then settle.
  const houseFx={ t0:0, dur:0, active:false };
  function kickHouseFx(dur){ houseFx.t0=performance.now(); houseFx.dur=dur; houseFx.active=true; }
  function updFx(){
    figUni.uSwell.value=0;       // contours held still (tremor disabled)
    figUni.uBreeze.value=0;
    figUni.uTime.value=performance.now()/1000;
    lakeUni.uTime.value=figUni.uTime.value;   // tiny lapping on Prospect Lake
    const _t=figUni.uTime.value;
    // cursor excitation: a calm radial ripple of the contour lines under the
    // host's pointer (uCursor term; independent of the fig tremor/swell).
    figUni.uCursor.value=0;
    if(cursorFx.amt>0){ figUni.uFig.value.set(cursorFx.x,cursorFx.z);
      figUni.uInner.value=cursorFx.inner; figUni.uOuter.value=cursorFx.outer; figUni.uCursor.value=cursorFx.amt; }
    // house click → the whole contour field goes bonkers, then eases to calm as
    // the camera arrives above the roof (p:0→1 over the same dur as the fly-to).
    // env holds near-peak briefly (haywire) then smooth-decays to 0 (settle).
    if(houseFx.active){ const p=Math.min(1,(performance.now()-houseFx.t0)/houseFx.dur);
      const env=1.0-THREE.MathUtils.smoothstep(p,0.14,1.0);
      figUni.uMode.value=0;                                        // electric radial tremor
      figUni.uFig.value.set(HOUSE[0]-750, HOUSE[1]-525);           // centred on the house
      figUni.uInner.value=0; figUni.uOuter.value=1600;             // wide — reaches the far contours
      figUni.uSwell.value=2.6*env;                                 // haywire amplitude → 0
      figUni.uCursor.value=Math.max(figUni.uCursor.value, 0.9*env);// glow pool pulses with it
      if(p>=1) houseFx.active=false; }

    // fig sways in the breeze — slow lean with layered gusts, pivoting at its
    // planted base (tips travel, roots stay). Always on; a touch stronger when focused.
    figAmt += ((mode==='fig'?1:0)-figAmt)*0.06; if(Math.abs((mode==='fig'?1:0)-figAmt)<0.0015)figAmt=(mode==='fig'?1:0);
    const _gust=0.55+0.45*Math.sin(_t*0.31)+0.25*Math.sin(_t*0.13);
    const _br=(0.7+0.5*figAmt)*_gust;
    figIcon.rotation.z=(Math.sin(_t*0.9)*0.05 + Math.sin(_t*2.3+1.0)*0.018)*_br;
    figIcon.rotation.x=(Math.cos(_t*0.75)*0.038 + Math.sin(_t*1.9)*0.014)*_br;

    // spring — Hunter's fan emblem (tuned in spring-lab): static jet strokes that
    // brighten as the camera closes in on the spring.
    springAmt += ((mode==='spring'?1:0)-springAmt)*0.06; if(Math.abs((mode==='spring'?1:0)-springAmt)<0.0015)springAmt=(mode==='spring'?1:0);
    const _sd=springIcon.userData;
    if(_sd.jets){ const op=0.62+0.30*springAmt; _sd.jets.forEach(j=>{ j.mat.opacity=op; }); }

    // focus-pull blur follows whichever zoom target is active (fig or spring);
    // fades in by zoom — ~0 far, ramping up as the camera closes in.
    const _useSpring=springAmt>figAmt;
    const _icon=_useSpring?springIcon:figIcon, _amt=_useSpring?springAmt:figAmt;
    _icon.getWorldPosition(_fw);
    const camD=camera.position.distanceTo(_fw);
    const zoom=1.0-THREE.MathUtils.smoothstep(camD,330,860);
    focusPass.uniforms.uAmt.value=0;   // focus-pull blur removed (hover shows a text description instead)
    const fp=_fw.clone(); fp.y+=10; fp.project(camera);
    focusPass.uniforms.uCenter.value.set(fp.x*0.5+0.5, fp.y*0.5+0.5);
    focusPass.uniforms.uAspect.value=innerWidth/innerHeight;

    // the globe's stars belong to the oblique view: hidden looking straight down,
    // they fade in as the camera tilts up into the dome (polar 0 = top-down).
    if(starUni){
      starUni.uTime.value=_t;
      const polar=controls.getPolarAngle?controls.getPolarAngle():0;
      const show=THREE.MathUtils.smoothstep(polar,0.12,0.6);   // a gentle tilt off plan reveals globe+stars
      _fxShow += (show-_fxShow)*0.12;
      starUni.uOpacity.value=1.0*_fxShow;
      if(globeUni) globeUni.uOpacity.value=0.62*_fxShow;
    }
  }

  // ---------- loop / resize ----------
  // onMap(worldX,worldZ): is a ground point inside the drawn parcel? (world
  // coords are survey coords shifted by the DEM half-extents 750/525.) Lets a
  // host page gate interaction to the actual masked drawing, not the DEM box.
  window.__v={scene,camera,controls,renderer,P3,ground,elevAt,MULT,
    onMap:function(wx,wz){ return inPoly(wx+750, wz+525); },
    // parcel bbox in world coords (survey shifted by the DEM half-extents) — a
    // host can centre + size its framing on the DRAWN parcel, not the DEM box.
    parcel:(function(){ var ax=1e9,bx=-1e9,az=1e9,bz=-1e9;
      BND.forEach(function(p){ if(p[0]<ax)ax=p[0]; if(p[0]>bx)bx=p[0]; if(p[1]<az)az=p[1]; if(p[1]>bz)bz=p[1]; });
      return {cx:(ax+bx)/2-750, cz:(az+bz)/2-525, w:bx-ax, d:bz-az}; })(),
    matLake:mat.lake, matLakeFill:mat.lakeFill,
    labels:{goward:lblGoward, echo:lblEcho, lake:plLabel},
    houseFill:houseFillMat, houseLine:mat.house, houseMesh:houseMeshRef, inHouse:inHouse,
    houseDiag:{n:HOUSE_N, err:HOUSE_ERR}}; window.__liftoff=kinhinLiftoff;
  // ---------- the site as a sphere: a faint glass globe encloses the plan ----------
  // In plan view the globe's silhouette reads as a circle (its fresnel rim lights the
  // edge); the framing below sizes that circle top-edge→bottom-edge. Tilt the camera
  // up into the dome and a subtle field of stars on the inner upper hemisphere fades in.
  var SPHERE_R=600, SPHERE_C=new THREE.Vector3(0,0,0);
  var globeUni, starUni, _fxShow=0;
  (function buildSphere(){
    var box=new THREE.Box3().setFromObject(scene);          // site extent BEFORE the globe is added
    if(!isFinite(box.min.x)||!isFinite(box.max.x)) return;
    var cy=(box.min.y+box.max.y)/2;

    // ---- TEST CHECKPOINT: log the scene state immediately BEFORE anything sphere-
    // related is added, and keep a registry so the whole effect can be torn out with
    // window.__sphereFx.remove() if we decide against it. ----
    var _childrenBefore=scene.children.length;
    console.log('[sphereFx] pre-sphere scene state:', { children:_childrenBefore });
    var _fx=[];   // every object/material/geometry the effect adds
    function _track(obj){ _fx.push(obj); return obj; }

    // sphere sized TIGHT to the corners of the contour rectangle (the DEM extent):
    // world x in [x0-750 , x1-750], z in [y0-525 , y1-525]; the radius is its half-
    // diagonal so the rectangle's four corners sit exactly on the sphere.
    var demW=DEM.x1-DEM.x0, demD=DEM.y1-DEM.y0;
    SPHERE_R=0.5*Math.hypot(demW,demD);
    SPHERE_C=new THREE.Vector3((DEM.x0+DEM.x1)/2-750, cy, (DEM.y0+DEM.y1)/2-525);

    // --- opaque ground: the contour rectangle reads as a SOLID surface (coloured to
    // the scene background, so invisible in plan but it writes depth) — you cannot see
    // the sphere's far wall or the stars THROUGH the land; they only show above the
    // terrain's silhouette once you tilt. Built from the real DEM so it carries relief. ---
    (function buildGround(){
      var GX=120, GZ=84, gp=[], gi=[];
      for(var j=0;j<=GZ;j++){ for(var ii=0;ii<=GX;ii++){
        var sxv=DEM.x0+(ii/GX)*demW, syv=DEM.y0+(j/GZ)*demD;
        gp.push(sxv-750, ground(sxv,syv)-1.6, syv-525);     // a hair below the draped linework
      }}
      for(var j2=0;j2<GZ;j2++){ for(var i2=0;i2<GX;i2++){
        var a=j2*(GX+1)+i2, b=a+1, c=a+(GX+1), d=c+1; gi.push(a,c,b, b,c,d);
      }}
      var gg=new THREE.BufferGeometry();
      gg.setAttribute('position',new THREE.Float32BufferAttribute(gp,3)); gg.setIndex(gi);
      var gm=new THREE.MeshBasicMaterial({color:0x242220, side:THREE.DoubleSide,
        polygonOffset:true, polygonOffsetFactor:1.5, polygonOffsetUnits:1.5});
      var ground3d=new THREE.Mesh(gg,gm); ground3d.renderOrder=-20; scene.add(_track(ground3d));
    })();

    // --- glass globe (BackSide: ONLY the inner face ever renders; the outer/near face
    // is culled, so looking through it you never see the shell, only its far interior
    // wall — and the opaque ground hides that wall in plan). Fresnel lights the rim. ---
    globeUni={ uColor:{value:new THREE.Color(0x9fb1cc)}, uOpacity:{value:0.62} };
    var globeMat=new THREE.ShaderMaterial({
      uniforms:globeUni, transparent:true, depthWrite:false, side:THREE.BackSide,
      vertexShader:[
        'varying vec3 vN; varying vec3 vV;',
        'void main(){ vec4 mv=modelViewMatrix*vec4(position,1.0); vV=-mv.xyz; vN=normalMatrix*normal;',
        '  gl_Position=projectionMatrix*mv; }'
      ].join('\n'),
      fragmentShader:[
        'uniform vec3 uColor; uniform float uOpacity; varying vec3 vN; varying vec3 vV;',
        'void main(){ vec3 N=normalize(vN); vec3 V=normalize(vV);',
        '  float f=1.0-abs(dot(N,V)); f=pow(f,2.2);',          // bright at the grazing rim
        '  float a=uOpacity*(0.10+0.90*f);',
        '  gl_FragColor=vec4(uColor,a); }'
      ].join('\n')
    });
    var globe=new THREE.Mesh(new THREE.SphereGeometry(SPHERE_R,64,40),globeMat);
    globe.position.copy(SPHERE_C); globe.renderOrder=-10; scene.add(_track(globe));

    // --- stars across the inner surface (fibonacci scatter, soft round, twinkling) ---
    // Spread over (almost) the whole interior so that at ANY oblique angle the far
    // surface behind the landscape fills with them; the tilt-gate (below) keeps them
    // absent in plan view and fades them in only as the camera leans into the globe.
    var N=1150, pos=[], ph=[], sz2=[], pr=Math.min(2,devicePixelRatio||1);
    var ga=Math.PI*(3.0-Math.sqrt(5.0));
    for(var i=0;i<N;i++){
      var y=1.0-(i/(N-1))*2.0;                                // 1 .. -1
      if(y<-0.55) continue;                                   // drop only the deep floor (stays underground)
      var r=Math.sqrt(Math.max(0,1.0-y*y)), th=i*ga;
      var dx=Math.cos(th)*r, dz=Math.sin(th)*r;
      var rad=SPHERE_R*0.985;
      pos.push(SPHERE_C.x+dx*rad, SPHERE_C.y+y*rad, SPHERE_C.z+dz*rad);
      ph.push(Math.random());
      sz2.push((2.6+Math.random()*3.6)*pr);
    }
    var sg=new THREE.BufferGeometry();
    sg.setAttribute('position',new THREE.Float32BufferAttribute(pos,3));
    sg.setAttribute('aPhase',new THREE.Float32BufferAttribute(ph,1));
    sg.setAttribute('aSize',new THREE.Float32BufferAttribute(sz2,1));
    starUni={ uColor:{value:new THREE.Color(0xe3ecf7)}, uOpacity:{value:0.0}, uTime:{value:0} };
    var starMat=new THREE.ShaderMaterial({
      uniforms:starUni, transparent:true, depthWrite:false, depthTest:true,
      blending:THREE.AdditiveBlending,
      vertexShader:[
        'attribute float aPhase; attribute float aSize; uniform float uTime; varying float vTw;',
        'void main(){ vec4 mv=modelViewMatrix*vec4(position,1.0);',
        '  vTw=0.58+0.42*sin(uTime*1.3+aPhase*6.2831853);',     // per-star twinkle
        '  gl_PointSize=aSize*(0.6+0.4*vTw);',                  // constant-pixel = star-like, gentle size flicker
        '  gl_Position=projectionMatrix*mv; }'
      ].join('\n'),
      fragmentShader:[
        'uniform vec3 uColor; uniform float uOpacity; varying float vTw;',
        'void main(){ vec2 c=gl_PointCoord-0.5; float d=length(c); if(d>0.5) discard;',
        '  float halo=pow(smoothstep(0.5,0.0,d),1.5);',         // soft glow
        '  float core=pow(smoothstep(0.16,0.0,d),1.2);',        // bright pin-point centre
        '  float a=halo*0.8+core*0.9;',
        '  gl_FragColor=vec4(uColor, a*uOpacity*vTw); }'
      ].join('\n')
    });
    var stars=new THREE.Points(sg,starMat); stars.renderOrder=8; scene.add(_track(stars));

    // ---- single switch to pull the whole experiment out cleanly ----
    window.__sphereFx={
      objects:_fx, radius:SPHERE_R, center:SPHERE_C.clone(), childrenBefore:_childrenBefore,
      remove:function(){
        _fx.forEach(function(o){ if(o.parent)o.parent.remove(o);
          if(o.geometry)o.geometry.dispose(); if(o.material)o.material.dispose(); });
        globeUni=null; starUni=null; _fxShow=0;
        console.log('[sphereFx] removed; scene children now', scene.children.length, '(was', _childrenBefore, 'before sphere)');
      }
    };
  })();
  // Star sphere removed (per design): the build above still computes SPHERE_R/SPHERE_C
  // (the camera framing below needs SPHERE_C), but the visible globe + starfield + the
  // occluder ground are torn straight back out via the author's teardown switch, so the
  // site plan sits on the plain #242220 background — matching the image-viewer stage.
  if(window.__sphereFx) window.__sphereFx.remove();

  // Default framing: size the globe's circle to span the viewport top→bottom (max coverage).
  // Start framing: show the FULL map, tight to the left/right edges (the sphere is
  // invisible in plan, so we frame the contour rectangle itself, not the globe).
  function fitOverview(margin){
    var vfov=camera.fov*Math.PI/180, aspect=camera.aspect||(innerWidth/innerHeight);
    // Centre on the DRAWN content (linework bounds), not the DEM-extent / sphere centre.
    // The contours sit offset within the DEM, so targeting SPHERE_C left the plan riding
    // high and a touch right. Frame the linework's own bounds: target its centre and fit
    // its width to the viewport.
    var box=new THREE.Box3();
    scene.traverse(function(o){ if(o.type==='Line'||o.type==='LineSegments'){
      if(!o.geometry.boundingBox) o.geometry.computeBoundingBox();
      if(o.geometry.boundingBox) box.union(o.geometry.boundingBox.clone().applyMatrix4(o.matrixWorld)); } });
    var cx=SPHERE_C.x, cz=SPHERE_C.z, fitW=DEM.x1-DEM.x0;
    if(isFinite(box.min.x)&&isFinite(box.max.x)){
      cx=(box.min.x+box.max.x)/2; cz=(box.min.z+box.max.z)/2; fitW=box.max.x-box.min.x; }
    var d=((fitW/2)/Math.tan(vfov/2)/aspect)*(margin||1);     // fit content WIDTH to the viewport
    OVR.dist=Math.min(controls.maxDistance,Math.max(controls.minDistance,d));
    OVR.tar.set(cx,OVR.tar.y,cz);
  }
  fitOverview(1.4);
  if(mode==='overview' && !introActive) applyPose(OVR);
  addEventListener('resize',()=>{ camera.aspect=innerWidth/innerHeight; camera.updateProjectionMatrix(); renderer.setSize(innerWidth,innerHeight); composer.setSize(innerWidth,innerHeight); var ov=(mode==='overview'&&!introActive&&!flying); fitOverview(1.4); if(ov)applyPose(OVR); });
  (function loop(){ requestAnimationFrame(loop);
    if(introActive){ const s=Math.sin(INTRO.tilt),c=Math.cos(INTRO.tilt);
      const dir=new THREE.Vector3(s*Math.sin(introAz),c,s*Math.cos(introAz));
      const want=INTRO.tar.clone().add(dir.multiplyScalar(INTRO.dist));
      camera.position.lerp(want,0.045); controls.target.lerp(INTRO.tar,0.08); camera.lookAt(controls.target);
    } else if(controls.enabled){ controls.update(); }
    updFx(); projectOverlays(); composer.render(); })();
})();
