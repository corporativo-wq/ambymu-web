(function(){
var tabsEl=document.querySelector('.tabs');if(!tabsEl)return;
var tabs=[].slice.call(tabsEl.querySelectorAll('[data-tab]')),panels=document.querySelectorAll('[data-panel]');
var ind=document.createElement('span');ind.className='tab-ind';
var wrapT=document.createElement('div');wrapT.className='tabs-wrap';tabs.forEach(function(b){wrapT.appendChild(b)});wrapT.prepend(ind);tabsEl.appendChild(wrapT);
var cur=tabs[0].dataset.tab;
function moveInd(){var b=tabs.find(function(t){return t.dataset.tab===cur});if(!b)return;ind.style.width=b.offsetWidth+'px';ind.style.transform='translateX('+b.offsetLeft+'px)';
if(tabsEl.scrollWidth>tabsEl.clientWidth)tabsEl.scrollTo({left:b.offsetLeft-20,behavior:'smooth'})}
var io='IntersectionObserver' in window?new IntersectionObserver(function(es){es.forEach(function(e){if(e.isIntersecting){e.target.classList.add('in');io.unobserve(e.target)}})},{rootMargin:'0px 0px -8% 0px'}):null;
function reveal(scope){[].forEach.call(scope.querySelectorAll('.item,.rv'),function(el,i){el.classList.remove('in');el.style.transitionDelay=Math.min(i,10)*45+'ms';if(io)io.observe(el);else el.classList.add('in')})}
function show(t,scroll){cur=t;tabs.forEach(function(b){b.setAttribute('aria-selected',b.dataset.tab===t)});
panels.forEach(function(p){var on=p.dataset.panel===t;p.classList.toggle('on',on);if(on)reveal(p)});moveInd();
if(scroll){var m=document.getElementById('menu');if(m&&m.getBoundingClientRect().top<0)m.scrollIntoView({behavior:'smooth'})}}
tabs.forEach(function(b){b.addEventListener('click',function(){show(b.dataset.tab,true);history.replaceState(null,'','#'+b.dataset.tab)})});
function step(d){var i=tabs.findIndex(function(t){return t.dataset.tab===cur});var n=tabs[(i+d+tabs.length)%tabs.length].dataset.tab;show(n,true);history.replaceState(null,'','#'+n)}
var nx=document.getElementById('nextTab');if(nx)nx.addEventListener('click',function(){step(1)});
var sx=0,sy=0,area=document.getElementById('menu');
if(area&&document.body.classList.contains('page-menu')){
area.addEventListener('touchstart',function(e){sx=e.touches[0].clientX;sy=e.touches[0].clientY},{passive:true});
area.addEventListener('touchend',function(e){var dx=e.changedTouches[0].clientX-sx,dy=e.changedTouches[0].clientY-sy;if(Math.abs(dx)>70&&Math.abs(dx)>Math.abs(dy)*1.6&&!e.target.closest('.tabs'))step(dx<0?1:-1)},{passive:true});
}
var h=location.hash.slice(1); show(tabs.some(function(t){return t.dataset.tab===h})?h:cur);
var hero=document.querySelector('.m-hero');if(hero)reveal(hero);
addEventListener('resize',moveInd);document.addEventListener('am:lang',moveInd);
if(document.fonts)document.fonts.ready.then(moveInd);
var top=document.querySelector('.top');
if(top)addEventListener('scroll',function(){top.classList.toggle('show',scrollY>900)},{passive:true});
})();