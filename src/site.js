/* AM by Mu — JS común (idioma, eventos, horario de hoy, cursor). Generado por build.py */
(function(){
  var root=document.documentElement; root.classList.add('js');
  /* ---- idioma ES/EN ---- */
  function setLang(l){root.setAttribute('data-lang',l);root.lang=l==='en'?'en':'es-MX';
    document.querySelectorAll('[data-set-lang]').forEach(function(b){b.setAttribute('aria-pressed',b.dataset.setLang===l)});
    try{localStorage.setItem('am-lang',l)}catch(e){}
    document.dispatchEvent(new CustomEvent('am:lang',{detail:l}));}
  var saved=null;try{saved=localStorage.getItem('am-lang')}catch(e){}
  var q=(location.search.match(/[?&]lang=(es|en)/)||[])[1];
  var bot=/bot|crawl|spider|google|bing|lighthouse/i.test(navigator.userAgent);
  document.querySelectorAll('[data-set-lang]').forEach(function(b){b.addEventListener('click',function(){setLang(b.dataset.setLang)})});
  window.AM={setLang:setLang};
  setLang(q||saved||(bot?'es':((navigator.language||'es').slice(0,2)==='es'?'es':'en')));
  /* ---- medición: cada CTA con data-ev → dataLayer + gtag (sin GTM) ---- */
  window.dataLayer=window.dataLayer||[];
  document.addEventListener('click',function(e){var a=e.target.closest&&e.target.closest('[data-ev]');if(!a)return;
    var ev=a.getAttribute('data-ev'),br=a.getAttribute('data-branch')||'';
    window.dataLayer.push({event:'cta_click',cta:ev,branch:br,page:location.pathname,href:a.getAttribute('href')||''});
    if(typeof gtag==='function'){gtag('event',ev,{branch:br,page_path:location.pathname});}},{passive:true});
  /* ---- horario: marcar el día de hoy (hora de Cancún) ---- */
  var d=new Date(new Date().toLocaleString('en-US',{timeZone:'America/Cancun'})).getDay();
  document.querySelectorAll('table.hours tr[data-d="'+d+'"]').forEach(function(r){r.classList.add('today')});
  var y=document.getElementById('y'); if(y) y.textContent=new Date().getFullYear();
})();
/* ---- cursor de matcha (solo mouse) ---- */

(function(){
  if(!matchMedia('(pointer:fine)').matches) return;
  var w=document.createElement('div');w.innerHTML='<div class="mcur" aria-hidden="true"><div class="spin"><svg viewBox="0 0 64 64" width="64" height="64" aria-hidden="true"><path d="M20 6 34 26" stroke="#1E4029" stroke-width="7" stroke-linecap="round"/><path d="M20 6 34 26" stroke="#F7F0E3" stroke-width="3.5" stroke-linecap="round"/><path d="M14 22h36l-5 32a4 4 0 0 1-4 3.4H23a4 4 0 0 1-4-3.4z" fill="#F7F0E3" stroke="#1E4029" stroke-width="3.2" stroke-linejoin="round"/><path d="M17.2 32h29.6l-3.3 20.4a2 2 0 0 1-2 1.7H22.5a2 2 0 0 1-2-1.7z" fill="#A8C47F"/><path class="foam" d="M15.6 24.4h32.8l-1.2 7.6H16.8z" fill="#F7F0E3"/><path d="M22 46c3 3 6 3 9 0s6-3 9 0" fill="none" stroke="#F7F0E3" stroke-width="2.4" stroke-linecap="round"/></svg></div></div><div class="mcur-dot" aria-hidden="true"></div>';while(w.firstChild)document.body.appendChild(w.firstChild);var c=document.querySelector('.mcur'),d=document.querySelector('.mcur-dot');
  document.documentElement.classList.add('has-mcur');
  var x=-100,y=-100,cx=x,cy=y,raf=0;
  function loop(){cx+=(x-cx)*.22;cy+=(y-cy)*.22;c.style.transform='translate('+cx+'px,'+cy+'px)';
    if(Math.abs(x-cx)>.3||Math.abs(y-cy)>.3) raf=requestAnimationFrame(loop); else raf=0}
  addEventListener('mousemove',function(e){x=e.clientX;y=e.clientY;d.style.transform='translate('+x+'px,'+y+'px)';
    c.classList.add('on');d.classList.add('on');
    var t=e.target.closest&&e.target.closest('a,button,summary,[role=tab],label,input,select');
    c.classList.toggle('hover',!!t); if(!raf) raf=requestAnimationFrame(loop)},{passive:true});
  document.addEventListener('mouseleave',function(){c.classList.remove('on');d.classList.remove('on')});
  addEventListener('mousedown',function(){c.classList.add('down')});
  addEventListener('mouseup',function(){c.classList.remove('down')});
})();
