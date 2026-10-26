/* IVE RADAR: read-only chart feed renderer. Never fabricate unavailable history. */
const SOURCE_IDS = Object.freeze({
  Melon: { Realtime:'melon-top100', Daily:'melon-daily', Weekly:'melon-weekly' },
  Genie: { Realtime:'genie-realtime', Daily:'genie-daily' },
  Bugs: { Realtime:'bugs-realtime', Daily:'bugs-daily' },
  FLO: { Realtime:'flo-realtime' },
  YouTube: { Weekly:'youtube-kr-weekly' },
  Spotify: { Daily:'spotify-kr-daily' },
  'Apple Music': { Feed:'apple-music-kr-top-songs' }
});
const SELECTORS = Object.freeze([
  ['[data-chart]','chart'],['[data-cycle]','cycle'],
  ['[data-history]','history'],['[data-window]','window'],
  ['[data-sales]','sales'],['[data-stream]','stream']
]);
const state = { data:null, chart:'all', cycle:'Realtime', history:'Melon', window:'7D', sales:'Hanteo', stream:'YouTube' };
const $ = selector => document.querySelector(selector);
const $$ = selector => [...document.querySelectorAll(selector)];
const empty = value => value == null ? '—' : String(value);
const sampleTime = item => item?.collected_at || item?.observed_at || null;
const time = iso => {
  if (!iso || !Number.isFinite(Date.parse(iso))) return '—';
  return new Intl.DateTimeFormat('en-GB',{timeZone:'Asia/Seoul',month:'short',day:'numeric',hour:'2-digit',minute:'2-digit',hour12:false}).format(new Date(iso))+' KST';
};
const make = (tag,text,cls) => {
  const node = document.createElement(tag);
  if (text != null) node.textContent=String(text);
  if (cls) node.className=cls;
  return node;
};
function isValidObservation(item, charts, tracks){
  if (!item || typeof item !== 'object' || !charts.has(item.chart_id) || !tracks.has(item.track_id)) return false;
  if (!Number.isInteger(item.rank) || item.rank < 1 || item.rank > 200) return false;
  const apple = item.chart_id === 'apple-music-kr-top-songs';
  const stamp = sampleTime(item);
  if (typeof stamp !== 'string' || !/^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d[+-]\d\d:\d\d$/.test(stamp) || !Number.isFinite(Date.parse(stamp))) return false;
  if (apple) {
    if(item.verification!=='official-apple-rss' || item.rank>100 || item.song_id!==tracks.get(item.track_id).apple_music_kr_song_id || item.movement!==null) return false;
    try {
      const song = new URL(item.song_url);
      if(song.protocol!=='https:' || song.hostname!=='music.apple.com' || song.searchParams.get('i')!==item.song_id) return false;
    }catch{return false;}
  } else if(item.verification!=='official-chart-snapshot') return false;
  try {
    const source = new URL(item.source_url);
    if (source.protocol !== 'https:') return false;
    const expected = new URL(charts.get(item.chart_id).source_url);
    return source.hostname === expected.hostname;
  } catch { return false; }
}
function loadData(raw){
  if (!raw || raw.schema_version!==2 || !Array.isArray(raw.charts) || !Array.isArray(raw.tracks) || !Array.isArray(raw.observations)) throw Error('Unsupported or incomplete data schema');
  const charts=new Map(raw.charts.map(c=>[c.id,c]));
  const tracks=new Map(raw.tracks.map(t=>[t.id,t]));
  const observations=raw.observations.filter(o=>isValidObservation(o,charts,tracks));
  const unique=new Map();
  for (const o of observations) {
    const key=[o.track_id,o.chart_id,sampleTime(o)].join('|');
    if (!unique.has(key)) unique.set(key,o);
  }
  return { ...raw, observations:[...unique.values()].sort((a,b)=>Date.parse(sampleTime(a))-Date.parse(sampleTime(b))), chartsById:charts, tracksById:tracks };
}
function series(chartId){
  if (!chartId || !state.data) return [];
  return state.data.observations.filter(o=>o.chart_id===chartId && o.track_id===state.data.default_track_id);
}
function latest(chartId){const points=series(chartId);return points[points.length-1] || null;}
function selectedId(platform,cycle){return platform==='Apple Music' ? SOURCE_IDS['Apple Music'].Feed : (SOURCE_IDS[platform]?.[cycle] ?? null);}
function sourceLabel(id){
  const item=state.data?.chartsById.get(id);
  return item ? item.chart : 'Not available';
}
function renderScores(){
  $$('.score').forEach(card=>{
    const platform=card.dataset.name;
    const id=selectedId(platform,state.cycle);
    const points=series(id);
    const recent=points[points.length-1];
    const meta=card.querySelector('.meta');
    const small=card.querySelector('.scorehead small');
    const rank=card.querySelector('.rank');
    card.hidden=state.chart!=='all' && state.chart!==platform;
    small.textContent=sourceLabel(id);
    rank.textContent=recent ? '#'+recent.rank : '—';
    card.dataset.status=recent ? (Date.now()-Date.parse(sampleTime(recent))>(platform==='Apple Music'?12:3)*3600000?'stale':'available'):'missing';
    meta.replaceChildren();
    const peak=points.length?Math.min(...points.map(p=>p.rank)):null;
    const change=recent?.movement;
    const fields=[['Observed peak',peak?'#'+peak:'—'],['Movement',typeof change==='number'?(change>0?'↑ '+change:change<0?'↓ '+Math.abs(change):'—'):'—']];
    fields.forEach(([label,value])=>{meta.append(make('span',label),make('b',value));});
    card.querySelectorAll('.data-source').forEach(n=>n.remove());
    if (recent){
      const foot=make('div',null,'data-source');
      foot.append(make('span',(platform==='Apple Music'?'Captured ':'As of ')+time(sampleTime(recent))+' · '));
      const a=make('a',platform==='Apple Music'?'Apple Music ↗':'Source');a.href=platform==='Apple Music'?recent.song_url:recent.source_url;a.target='_blank';a.rel='noopener noreferrer';foot.append(a);card.append(foot);
    } else {
      card.append(make('div',id ? 'No verified observation' : 'Chart type unavailable','data-source'));
    }
  });
}
function updateHistory(){
  const id=selectedId(state.history,state.cycle);
  const reference=latest(id);
  const cutoff=state.window==='ALL'?-Infinity:Date.now()-(state.window==='7D'?7:30)*86400000;
  const points=series(id).filter(p=>Date.parse(sampleTime(p))>=cutoff);
  const emptyState=$('#history-empty');
  emptyState.hidden=points.length>=2;
  emptyState.textContent= !id ? 'This platform does not publish the selected chart type.' : points.length===0 ? 'No verified rank history for this chart yet.' : (state.history==='Apple Music'?'One feed capture recorded. A second is needed for a ranking curve.':'One verified observation recorded. A second is needed for a ranking curve.');
  const line=$('#example-line');const area=$('#example-area');const dots=$('#example-points');
  const name=$('#chart-label');name.textContent=state.history;
  $('#chart-source-label').lastChild.textContent=' · '+(id?sourceLabel(id):'Unavailable');
  $('#chart-timestamp').textContent=reference?(state.history==='Apple Music'?'Last feed capture: ':'Latest observation: ')+time(sampleTime(reference)):'No verified observations';
  $('.demo-stamp').textContent=state.history==='Apple Music'?'APPLE MUSIC RSS CAPTURES · NOT HOURLY':'VERIFIED CHART OBSERVATIONS';
  line.setAttribute('d','');area.setAttribute('d','');dots.replaceChildren();
  if (points.length < 2) return;
  const begin=Date.parse(sampleTime(points[0]));
  const duration=Math.max(1,Date.parse(sampleTime(points[points.length-1]))-begin);
  const vertices=points.map(p=>({x:42+(Date.parse(sampleTime(p))-begin)/duration*600,y:32+(p.rank-1)/99*182}));
  const path=vertices.map((p,i)=>(i?'L':'M')+p.x.toFixed(1)+' '+p.y.toFixed(1)).join(' ');
  line.setAttribute('d',path);
  area.setAttribute('d',path+' L642 214 L42 214 Z');
  for(const p of vertices){const c=document.createElementNS('http://www.w3.org/2000/svg','circle');c.setAttribute('cx',p.x);c.setAttribute('cy',p.y);c.setAttribute('r','4');dots.appendChild(c)}
  $('#preview-chart').setAttribute('aria-label',`Verified ${state.history} rank history with ${points.length} observations`);
}
function renderStats(){
  const id=selectedId(state.history,state.cycle);
  const points=series(id);
  const rows=$$('.key-panel .statrow');
  const recent=points.at(-1);
  const peak=points.length?Math.min(...points.map(p=>p.rank)):null;
  const days=new Set(points.map(p=>sampleTime(p).slice(0,10))).size;
  const values=[
    ['Highest observed rank',peak?'#'+peak:'—'],
    ['Latest observed rank',recent?'#'+recent.rank:'—'],
    ['Verified observations',String(points.length)],
    ['Observed chart dates',points.length?String(days):'—'],
    ['Hours in Top 20','—'],
    ['Hours in Top 50','—'],
    [id==='apple-music-kr-top-songs'?'Last feed capture':'Last observation',recent?time(sampleTime(recent)):'—']
  ];
  rows.forEach((row,i)=>{if(!values[i])return;row.firstElementChild.textContent=values[i][0];row.lastElementChild.textContent=values[i][1]});
  $('.key-panel .small-desc').textContent=id==='apple-music-kr-top-songs'?'Apple Music RSS snapshots are captured when checked, not published hourly chart periods. Peaks are observed only.':'Observed peaks are not lifetime chart peaks. Hour totals require complete, verified hourly coverage.';
}
function renderRecent(){
  const body=$('.bottomrow .data-table tbody');
  body.replaceChildren();
  const items=[...(state.data?.observations??[])].reverse().slice(0,8);
  if (!items.length){const tr=make('tr');const td=make('td','No verified observations yet.');td.colSpan=4;tr.append(td);body.append(tr);return;}
  items.forEach(observation=>{
    const tr=make('tr');const chart=state.data.chartsById.get(observation.chart_id);
    const track=state.data.tracksById.get(observation.track_id);
    tr.append(make('td',time(sampleTime(observation))),make('td',`${chart.platform} ${chart.chart}`),make('td',track.title));
    const td=make('td');const link=make('a','#'+observation.rank);link.href=observation.song_url || observation.source_url;link.target='_blank';link.rel='noopener noreferrer';td.append(link);tr.append(td);body.append(tr);
  });
}
function renderMilestones(){
  const points=series('melon-top100');
  const rows=$$('.bottomrow .panel:last-child .statrow');
  const map=[['#1 observed on Melon TOP100',1],['Top 10 observed on Melon',10],['Top 50 observed on Melon',50]];
  map.forEach(([label,bound],i)=>{
    const r=rows[i];if(!r)return;
    r.firstElementChild.textContent=label;
    r.lastElementChild.textContent=points.some(p=>p.rank<=bound)?'Observed':'—';
  });
  if (rows[3]) rows[3].lastElementChild.textContent='—';
}

function renderStreaming(){
  const panel=$('#streaming');
  if(!panel)return;
  const rows=panel.querySelectorAll('.card-rows .statrow');
  if(rows.length<2)return;
  const count=rows[0].querySelector('strong');
  const updated=rows[1].querySelector('strong');
  const description=panel.querySelector('.small-desc');
  const platform=state.stream;
  $('#stream-metric').textContent=platform==='YouTube'?'YouTube views':platform==='Spotify'?'Spotify streams':'Apple Music plays';
  count.textContent='—';
  updated.textContent='—';
  if(platform!=='YouTube'){
    description.textContent=platform+' stream totals are not connected.';
    return;
  }
  const points=(state.data?.streaming||[]).filter(x=>
    x && x.platform==='YouTube' && x.metric==='view_count' &&
    x.track_id===state.data.default_track_id && x.verification==='youtube-data-api-v3' &&
    Number.isSafeInteger(x.value) && x.value>=0 && Number.isFinite(Date.parse(x.collected_at))
  ).sort((a,b)=>Date.parse(a.collected_at)-Date.parse(b.collected_at));
  const latest=points.at(-1);
  if(!latest){
    description.textContent='Official YouTube MV counter awaiting API connection.';
    return;
  }
  count.textContent=latest.value.toLocaleString('en-US');
  updated.textContent=time(latest.collected_at);
  description.replaceChildren(make('span','Official MV views collected '+time(latest.collected_at)+' · '));
  const link=make('a','Video source ↗');
  link.href='https://www.youtube.com/watch?v=rsNhWkC4neE';
  link.target='_blank';link.rel='noopener noreferrer';
  description.append(link);
}

function renderHeader(){
  const obs=state.data?.observations || [];
  const label=$('#source-status');
  if(!obs.length){label.textContent='NO VERIFIED DATA YET';return;}
  const recent=obs.at(-1);
  label.textContent=(Date.now()-Date.parse(sampleTime(recent))>12*3600000?'HISTORICAL DATA · ':'LATEST VERIFIED DATA · ')+time(sampleTime(recent));
}
function render(){renderScores();updateHistory();renderStats();renderRecent();renderMilestones();renderStreaming();renderHeader()}
for(const [selector,key] of SELECTORS){
  $$(selector).forEach(button=>button.addEventListener('click',()=>{
    const value=button.getAttribute('data-'+key);
    $$(selector).forEach(x=>x.setAttribute('aria-pressed',String(x===button)));
    state[key]=value;
    if(key==='chart'){
      if(value!=='all'){
        const history=$$('[data-history]').find(x=>x.dataset.history===value);
        if(history){state.history=value;$$('[data-history]').forEach(x=>x.setAttribute('aria-pressed',String(x===history)));}
      }
    }
    if(key==='sales')$('#sales-label').textContent=value+' · awaiting verified sales source';
    if(key==='stream')renderStreaming();
    if(['chart','cycle','history','window'].includes(key))render();
  }));
}
$$('.side-items a,.topnav a').forEach(link=>link.addEventListener('click',()=>{
  const group=link.parentElement;
  group.querySelectorAll('a').forEach(item=>item.classList.remove('active'));
  link.classList.add('active');
}));
// Poll static published JSON every five minutes while the website is open.
// Collector runs separately in GitHub Actions; no credentials in the browser.
let loading=false;
async function refreshData(){
  if(document.hidden || loading)return;
  loading=true;
  try{
    const response=await fetch('./data.json',{cache:'no-store'});
    if(!response.ok)throw Error('Data feed unavailable');
    state.data=loadData(await response.json());
    render();
  }catch(error){
    console.warn('IVE RADAR data refresh unavailable:',error);
    if(!state.data){
      $('#source-status').textContent='DATA FEED UNAVAILABLE';
      $('#history-empty').textContent='Unable to load verified observations.';
    }
  }finally{loading=false;}
}
refreshData();
setInterval(refreshData,5*60*1000);
document.addEventListener('visibilitychange',()=>{if(!document.hidden)refreshData()});