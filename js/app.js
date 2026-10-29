(() => {
 const API_BASE=(window.KUNDLI_API_BASE||'https://kundali-software-ej6w.onrender.com').replace(/\/+$/, '');
 const translations=window.KUNDLI_TRANSLATIONS;
 const signsEn=translations.en.signs, signsHi=translations.hi.signs;
 const short={Ascendant:'Asc',Sun:'Su',Moon:'Mo',Mars:'Ma',Mercury:'Me',Jupiter:'Ju',Venus:'Ve',Saturn:'Sa',Rahu:'Ra',Ketu:'Ke'};
 const hiNames={Ascendant:'लग्न',Sun:'सूर्य',Moon:'चन्द्र',Mars:'मंगल',Mercury:'बुध',Jupiter:'गुरु',Venus:'शुक्र',Saturn:'शनि',Rahu:'राहु',Ketu:'केतु'};
 const buttons=[...document.querySelectorAll('.house')];
 let lang='en',result=null,selected=1,activeVarga='D1';
 const chartData=()=>!result?null:activeVarga==='D1'?result:result.vargas?.[activeVarga];
 const t=k=>translations[lang][k]||translations.en[k]||k;
 function sign(i){return (lang==='hi'?signsHi:signsEn)[i%12]}
 function planetsAt(n){return chartData()?.planets.filter(p=>p.house===n)||[]}
 function render(){
  document.documentElement.lang=lang;
  document.querySelectorAll('[data-i18n]').forEach(el=>{if(translations[lang][el.dataset.i18n] && !['sampleCaption','sampleData','privacy','footer','placeHelp','houseNote','prepareChart'].includes(el.dataset.i18n))el.textContent=t(el.dataset.i18n)});
  const asc=result?chartData().planets[0].sign_index:0;
  buttons.forEach(b=>{let n=+b.dataset.house, ps=planetsAt(n);b.querySelector('.house-number').textContent=n;b.querySelector('.house-sign').textContent=sign((asc+n-1)%12);b.querySelector('.planet-list').textContent=result?(ps.map(p=>short[p.name]).join(' · ')||'—'):'—';b.classList.toggle('selected',n===selected);b.setAttribute('aria-label',`${t('house')} ${n}`)});
  document.querySelector('.chart-heading h2').textContent=(activeVarga==='D1'?'Lagna Kundli':document.querySelector(`.varga-tab[data-varga="${activeVarga}"]`)?.textContent.split('·').slice(1).join('·').trim()||'Divisional Chart')+' · '+activeVarga;
  document.querySelector('.chart-center small').textContent=activeVarga;
  document.querySelectorAll('.varga-tab').forEach(b=>{const on=b.dataset.varga===activeVarga;b.classList.toggle('active',on);b.setAttribute('aria-pressed',String(on))});
  document.getElementById('detail-title').textContent=`${t('house')} ${selected}`;
  document.getElementById('detail-sign').textContent=sign((asc+selected-1)%12);
  document.getElementById('detail-planets').textContent=planetsAt(selected).map(p=>lang==='hi'?hiNames[p.name]:p.name).join(', ')||'—';
  const tbody=document.getElementById('planet-table');tbody.replaceChildren();
  if(result)chartData().planets.forEach(p=>{const tr=document.createElement('tr');[lang==='hi'?hiNames[p.name]:p.name,sign(p.sign_index),`${p.degree==null?'—':p.degree.toFixed(3)+'°'}${p.retrograde?' ℞':''}`,`${p.nakshatra} (${p.pada})`].forEach(value=>{const td=document.createElement('td');td.textContent=value;tr.append(td)});tbody.append(tr)});
  else {const tr=document.createElement('tr'),td=document.createElement('td');td.colSpan=4;td.textContent='Enter birth details to calculate planetary positions.';tr.append(td);tbody.append(tr)}
 }
 document.querySelectorAll('.varga-tab').forEach(b=>b.addEventListener('click',()=>{activeVarga=b.dataset.varga;selected=1;render()}));
 buttons.forEach(b=>b.addEventListener('click',()=>{selected=+b.dataset.house;render()}));
 document.getElementById('language').addEventListener('change',e=>{lang=e.target.value;render();if(result)renderDasha(false)});
 document.getElementById('birth-form').addEventListener('submit',async e=>{
  e.preventDefault();const status=document.getElementById('form-status');status.textContent='Calculating…';
  const get=id=>document.getElementById(id).value;
  const body={name:get('person-name'),date:get('birth-date'),time:get('birth-time'),place:get('birth-place'),latitude:Number(get('latitude')),longitude:Number(get('longitude')),timezone:get('timezone'),ayanamsha:get('ayanamsha'),nodes:get('nodes')};
  try {const response=await fetch(`${API_BASE}/api/chart`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});let data;try{data=await response.json()}catch{data={}}if(!response.ok)throw Error(typeof data.detail==='string'?data.detail:`API request failed (HTTP ${response.status})`);result=data;selected=1;document.getElementById('chart-caption').textContent=`${body.name||'Birth chart'} · ${body.place} · ${body.date} ${body.time} · ${data.ascendant_sign} Lagna`;
   status.textContent=`Calculated successfully · ${data.ayanamsha} · ${data.house_system}`;render();renderDasha();renderAnalysis();renderAshta();
  }catch(err){const message=err instanceof TypeError?'Could not reach the Kundli API. Check your internet connection, Render deployment status, and backend CORS settings.':err.message;status.textContent=`Error: ${message}`;}
 });
 const mdSelect=document.getElementById('mahadasha-select'),adSelect=document.getElementById('antardasha-select');
 const fmt=iso=>{if(!iso)return '—';const date=new Date(/(?:Z|[+-]\d\d:\d\d)$/.test(iso)?iso:iso+'Z');return new Intl.DateTimeFormat(lang==='hi'?'hi-IN':'en-GB',{timeZone:result?.local_time?getZone(): 'UTC',year:'numeric',month:'short',day:'2-digit'}).format(date)};
 const getZone=()=>document.getElementById('timezone').value||'UTC';
 const fill=(id,items)=>{const tbody=document.getElementById(id);tbody.replaceChildren();items.forEach(item=>{const tr=document.createElement('tr');[item.lord,fmt(item.start_utc),fmt(item.end_utc)].forEach(v=>{const td=document.createElement('td');td.textContent=v;tr.append(td)});tbody.append(tr)})};
 const selectFill=(select,items)=>{select.replaceChildren();items.forEach((item,i)=>{const o=document.createElement('option');o.value=i;o.textContent=`${item.lord} · ${fmt(item.start_utc)} – ${fmt(item.end_utc)}`;select.append(o)});select.disabled=false};
 function renderDasha(reset=true,keepMd=false){if(!result?.vimshottari)return;const data=result.vimshottari,periods=data.mahadashas;
  if(reset&&!keepMd){selectFill(mdSelect,periods);const birth=Date.parse(result.utc_time.endsWith("Z")?result.utc_time:result.utc_time+"Z");let idx=periods.findIndex(p=>Date.parse(p.start_utc+"Z")<=birth&&birth<Date.parse(p.end_utc+"Z"));mdSelect.value=String(idx<0?0:idx)}
  const md=periods[mdSelect.selectedIndex>=0?mdSelect.selectedIndex:0];if(reset){selectFill(adSelect,md.antardashas);const birth=Date.parse(result.utc_time.endsWith("Z")?result.utc_time:result.utc_time+"Z");let idx=md.antardashas.findIndex(p=>Date.parse(p.start_utc+"Z")<=birth&&birth<Date.parse(p.end_utc+"Z"));adSelect.value=String(idx<0?0:idx)}
  const ad=md.antardashas[adSelect.selectedIndex>=0?adSelect.selectedIndex:0];fill('mahadasha-body',periods);fill('antardasha-body',md.antardashas);fill('pratyantardasha-body',ad.pratyantardashas);
  document.getElementById('dasha-summary').textContent=`Birth Nakshatra: ${data.birth_nakshatra} · Lord: ${data.birth_nakshatra_lord} · Balance at birth: ${data.balance_at_birth_years.toFixed(4)} years`;
  document.getElementById('dasha-current').textContent=`Selected: ${md.lord} Mahadasha → ${ad.lord} Antardasha (${fmt(ad.start_utc)} – ${fmt(ad.end_utc)})`;
 }
 mdSelect.addEventListener('change',()=>renderDasha(true,true));adSelect.addEventListener('change',()=>renderDasha(false));
 function renderAnalysis(){
  const a=result?.analysis;if(!a)return;
  const tbody=document.getElementById('aspect-body');tbody.replaceChildren();
  a.graha_drishti.aspects.forEach(item=>{const tr=document.createElement('tr');[lang==='hi'?hiNames[item.planet]:item.planet,`${item.offset}th`,item.target_sign,String(item.target_house),item.occupants.join(', ')||'—'].forEach(value=>{const td=document.createElement('td');td.textContent=value;tr.append(td)});tbody.append(tr)});
  const box=document.getElementById('yoga-results');box.replaceChildren();
  if(!a.yoga_checks.matches.length){box.textContent='No matches among the selected basic rules.';return}
  a.yoga_checks.matches.forEach(item=>{const div=document.createElement('div');div.className='yoga-item';const strong=document.createElement('strong');strong.textContent=item.name;const desc=document.createElement('p');desc.textContent=item.rule;div.append(strong,desc);box.append(div)});
 }

 function renderAshta(){
  const a=result?.ashtakavarga;if(!a)return;
  document.getElementById('ashta-summary').textContent=`${a.method} · ${a.total} total bindus`;
  const grid=document.getElementById('sav-grid');grid.replaceChildren();
  a.sav.forEach((n,i)=>{const cell=document.createElement('div');cell.className='ashta-cell';
    const name=document.createElement('small');name.textContent=sign(i);
    const value=document.createElement('strong');value.textContent=n;
    const bar=document.createElement('div');bar.className='ashta-bar';const fill=document.createElement('i');fill.style.width=(n/56*100)+'%';bar.append(fill);cell.append(name,value,bar);grid.append(cell)});
  const head=document.getElementById('bav-head');head.replaceChildren();const hr=document.createElement('tr');
  ['Graha',...signsEn.map(x=>x.slice(0,3)),'Total'].forEach(v=>{const th=document.createElement('th');th.textContent=v;hr.append(th)});head.append(hr);
  const body=document.getElementById('bav-body');body.replaceChildren();
  for(const [graha,values] of Object.entries(a.bav)){
    const tr=document.createElement('tr');[graha,...values,values.reduce((x,y)=>x+y,0)].forEach(v=>{const td=document.createElement('td');td.textContent=v;tr.append(td)});body.append(tr)
  }
  const tr=document.createElement('tr');['SAV',...a.sav,a.total].forEach(v=>{const td=document.createElement('td');td.textContent=v;tr.append(td)});body.append(tr);
 }
 render();
})();
