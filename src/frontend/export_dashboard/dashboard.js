const state={runs:[],selected:null,files:[],active:null,timer:null,cursor:0,catalog:null};
const el=id=>document.getElementById(id); const fmt=(v,f='—')=>(v===undefined||v===null||v==='')?f:String(v);
function stat(id,msg,err=false){el(id).textContent=msg;el(id).style.color=err?'#f85149':'#8b949e'}
async function api(path,opt={}){const r=await fetch(path,opt);if(!r.ok)throw new Error(await r.text());const ct=r.headers.get('content-type')||'';return ct.includes('json')?r.json():r.text()}
function option(sel,id,name,extra=''){const o=document.createElement('option');o.value=id;o.textContent=extra?`${name} — ${extra}`:name;sel.appendChild(o)}
async function loadCatalog(){state.catalog=await api('/api/commands');const wf=el('workflowSelect'), em=el('executionModeSelect'), mu=el('marketUniverseSelect'), ind=el('industryDomainSelect'), buyer=el('buyerSegmentSelect'), obj=el('objectiveSelect'), cmd=el('commandSelect');state.catalog.workflow_modes.forEach(x=>option(wf,x.id,x.name));state.catalog.execution_modes.forEach(x=>option(em,x.id,x.name));state.catalog.market_universes.forEach(x=>option(mu,x.id,x.name,x.coverage_count_label));state.catalog.industry_domains.forEach(x=>option(ind,x.id,x.name,x.classification));state.catalog.buyer_segments.forEach(x=>option(buyer,x.id,x.name));state.catalog.opportunity_objectives.forEach(x=>option(obj,x.id,x.name));function fillCmd(){cmd.innerHTML='';state.catalog.commands.filter(c=>c.workflow===wf.value).forEach(c=>option(cmd,c.id,c.name))}wf.onchange=fillCmd;fillCmd()}
function payload(){return {workflow:el('workflowSelect').value,execution_mode:el('executionModeSelect').value,market_universe:el('marketUniverseSelect').value,industry_domain:el('industryDomainSelect').value,buyer_segment:el('buyerSegmentSelect').value,objective:el('objectiveSelect').value,command_id:el('commandSelect').value,signal:el('rawInput').value,count:5}}
function cardHtml(c, isCandidate=true){return `<div class="candidate"><strong>${fmt(c.title)}</strong><div class="field"><b>Market Gap:</b> ${fmt(c.market_gap)}</div><div class="field"><b>Needed Solution:</b> ${fmt(c.needed_solution)}</div><div class="field"><b>Opportunity Direction:</b> ${fmt(c.opportunity_direction)}</div><div class="field"><b>Why Now:</b> ${fmt(c.why_now)}</div>${isCandidate?`<div class="field"><b>Selection Score:</b> ${fmt(c.selection_score)} · ${fmt(c.confidence_label)}</div><button data-run="${c.candidate_id}">Run This Opportunity</button>`:''}</div>`}
async function needed(){stat('launchStatus','Searching market-wide needed solution areas...');const x=await api('/api/opportunities/search-needed-solutions',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload())});const box=el('candidateList');box.innerHTML='';(x.directions||[]).forEach(c=>{const wrap=document.createElement('div');wrap.innerHTML=cardHtml(c,false);box.appendChild(wrap.firstChild)});stat('launchStatus',`Found ${(x.directions||[]).length} needed solution direction(s).`)}
async function generate(){stat('launchStatus','Generating protected opportunity selection...');const x=await api('/api/opportunities/generate',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload())});const box=el('candidateList');box.innerHTML='';(x.candidates||[]).forEach(c=>{const wrap=document.createElement('div');wrap.innerHTML=cardHtml(c,true);const node=wrap.firstChild;node.querySelector('button').onclick=()=>runCandidate(c.candidate_id);box.appendChild(node)});stat('launchStatus',`Generated ${(x.candidates||[]).length} opportunity candidate(s). Internal construction protected.`)}
async function runCandidate(id){resetEvents();stat('launchStatus','Launching selected opportunity...');const x=await api('/api/opportunities/run-candidate',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({candidate_id:id})});if(x.status==='blocked'){stat('launchStatus','Blocked by governance hard stop. See audit panel.',true);loadAuditLog();return}state.active=x.event_run_id;watch()}
function title(r){return r.category_name||r.sector||r.folder_name||r.run_id||'Claire run'}
function renderRuns(){const list=el('runList');list.innerHTML='';el('runCount').textContent=state.runs.length;if(!state.runs.length){list.innerHTML='<div class="status">No runs found.</div>';return} state.runs.forEach(r=>{const d=document.createElement('div');d.className='runCard'+(state.selected&&state.selected.run_id===r.run_id?' active':'');d.innerHTML=`<strong>${fmt(title(r))}</strong><div class="meta">${fmt(r.created_at)}<br>Sector: ${fmt(r.sector)}<br>Decision: ${fmt(r.decision_classification)} · Files: ${fmt(r.written_file_count)}</div>`;d.onclick=()=>selectRun(r);list.appendChild(d)})}
function renderCards(r){const c=[['Run ID',r.run_id],['Output Folder',r.output_dir],['Domain',r.domain],['Sector',r.sector],['Category',r.category_name],['Decision',r.decision_classification],['Breakthrough',r.breakthrough_classification],['Portfolio Score',r.portfolio_score],['Export Level',r.export_package_level],['Export Score',r.export_package_score],['Documents',r.document_count],['Written Files',r.written_file_count]];el('summaryCards').innerHTML=c.map(([a,b])=>`<div class="card"><h3>${a}</h3><p>${fmt(b)}</p></div>`).join('')}
function renderFiles(files){state.files=files||[];el('filesValue').textContent=state.files.length||'—';el('fileList').innerHTML='';el('fileSelect').innerHTML='';state.files.forEach(f=>{const row=document.createElement('div');row.className='fileRow';row.innerHTML=`<div><strong>${f.filename}</strong><div class="muted">${fmt(f.format)} · ${fmt(f.size_bytes)} bytes</div></div><button>Preview</button><button>Open</button>`;row.children[1].onclick=()=>preview(f.filename);row.children[2].onclick=()=>window.open(`/api/runs/${encodeURIComponent(state.selected.run_id)}/files/${encodeURIComponent(f.filename)}?raw=1`,'_blank');el('fileList').appendChild(row);const o=document.createElement('option');o.value=f.filename;o.textContent=f.filename;el('fileSelect').appendChild(o)})}
async function selectRun(r){state.selected=r;renderRuns();el('emptyState').classList.add('hidden');el('detailState').classList.remove('hidden');el('selectedSector').textContent=fmt(r.sector);el('selectedTitle').textContent=title(r);el('selectedMeta').textContent=`${fmt(r.run_id)} · ${fmt(r.created_at)}`;el('decisionValue').textContent=fmt(r.decision_classification);el('exportValue').textContent=fmt(r.export_package_level);renderCards(r);el('rawBox').textContent=JSON.stringify(r,null,2);try{const x=await api(`/api/runs/${encodeURIComponent(r.run_id)}/files`);renderFiles(x.files||[]);const p=['run_summary.md','portfolio_binder.md','README.md'].find(n=>state.files.some(f=>f.filename===n));if(p)preview(p)}catch(e){el('previewBox').textContent=e.message}}
async function preview(name){if(!state.selected||!name)return;el('fileSelect').value=name;el('previewBox').textContent='Loading...';try{const x=await api(`/api/runs/${encodeURIComponent(state.selected.run_id)}/files/${encodeURIComponent(name)}?max_chars=120000`);el('previewBox').textContent=typeof x==='string'?x:(x.content||JSON.stringify(x,null,2));tab('preview')}catch(e){el('previewBox').textContent=e.message}}
function tab(name){document.querySelectorAll('.tab').forEach(b=>b.classList.toggle('active',b.dataset.tab===name));['summary','files','preview','raw'].forEach(t=>el(t+'Tab').classList.toggle('hidden',t!==name))}
async function loadRuns(id=null){stat('statusBox','Loading...');try{const x=await api('/api/runs');state.runs=x.runs||[];renderRuns();stat('statusBox',`Loaded ${state.runs.length} run(s).`);const target=id?state.runs.find(r=>r.run_id===id||r.folder_name===id):null;if(target)selectRun(target);else if(state.runs.length&&!state.selected)selectRun(state.runs[0])}catch(e){stat('statusBox','Failed: '+e.message,true)}}
async function rescan(){await api('/api/rescan',{method:'POST'});await loadRuns()}
function resetEvents(){state.cursor=0;el('eventList').innerHTML='';el('progressBar').style.width='0%';el('liveBadge').textContent='running'}
function addEvents(events){for(const ev of events){const d=document.createElement('div');d.className='event '+(ev.event_type==='complete'?'complete':ev.level==='error'?'error':'');d.innerHTML=`<strong>${fmt(ev.stage)} · ${fmt(ev.event_type)}</strong><div>${fmt(ev.message)}</div><div class="muted">${fmt(ev.timestamp)}</div>`;el('eventList').prepend(d);if(ev.progress!==undefined&&ev.progress!==null)el('progressBar').style.width=Math.max(0,Math.min(100,ev.progress))+'%'}}
async function poll(){if(!state.active)return;try{const x=await api(`/api/events/${state.active}?since=${state.cursor}`);addEvents(x.events||[]);state.cursor=x.event_count||state.cursor;if(x.status==='complete'||x.status==='error'){clearInterval(state.timer);state.timer=null;el('liveBadge').textContent=x.status;if(x.result){await loadRuns(x.result.run_id||x.result.folder_name)}stat('launchStatus',x.status==='complete'?'Run complete.':'Run failed: '+fmt(x.error),x.status==='error')}}catch(e){}}
function watch(){stat('launchStatus','Run started. Watching live events...');if(state.timer)clearInterval(state.timer);state.timer=setInterval(poll,900);poll()}
async function launch(){const raw=el('rawInput').value.trim();if(!raw){stat('launchStatus','Add raw input before launching.',true);return}const gov=await governanceCheck();if(gov.decision==='block'){stat('launchStatus','Blocked by governance hard stop. See audit panel.',true);return}const activation=await feedActivationCheck();if(activation.decision==='block'){stat('launchStatus','Feed activation blocked. See activation panel.',true);return}el('runBtn').disabled=true;resetEvents();try{const p=payload();p.raw_input=raw;const x=await api('/api/evaluate/async',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(p)});state.active=x.event_run_id;watch()}catch(e){stat('launchStatus','Run failed to start: '+e.message,true)}finally{setTimeout(()=>{el('runBtn').disabled=false},1200)}}

async function loadFeedStatus(){
  try{
    const x=await api('/api/feeds/status');
    el('feedBadge').textContent=x.feed_layer||'scaffold';
    el('feedStatusBox').textContent=`Connected ingestion: ${x.connected_ingestion_enabled?'enabled':'not enabled'} · Deterministic fallback: ${x.deterministic_fallback_enabled?'ready':'unavailable'} · Coverage universes: ${x.coverage_count}`;
    const list=el('feedCoverageList'); list.innerHTML='';
    (x.coverage||[]).forEach(item=>{
      const d=document.createElement('div'); d.className='feedItem';
      d.innerHTML=`<strong>${item.display_name}</strong><div class="coverage">${item.coverage_target}</div><div class="offline">Connected feed: ${item.connected_feed_enabled?'enabled':'offline scaffold'} · Fallback: ${item.deterministic_fallback?'ready':'unavailable'}</div>`;
      list.appendChild(d);
    });
  }catch(e){
    if(el('feedStatusBox')) el('feedStatusBox').textContent='Feed status unavailable: '+e.message;
  }
}


async function governanceCheck(){
  const p=payload();
  p.raw_input=el('rawInput').value;
  try{
    const x=await api('/api/governance/evaluate',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(p)});
    const d=x.decision||{};
    el('governanceBadge').textContent=d.decision||'allow';
    el('governanceStatusBox').textContent=`Decision: ${fmt(d.decision)}\nDefense Classification: ${fmt(d.defense_classification)}\nLegal Status: ${fmt(d.legal_status)}\nSeverity: ${fmt(d.severity)}\nAction: ${fmt(d.recommended_action)}\nReason: ${fmt(d.reason_summary)}`;
    loadAuditLog();
    return d;
  }catch(e){
    el('governanceStatusBox').textContent='Governance check unavailable: '+e.message;
    return {decision:'allow'};
  }
}
async function loadAuditLog(){
  try{
    const x=await api('/api/governance/audit');
    const list=el('auditList'); if(!list) return;
    list.innerHTML='';
    (x.events||[]).slice(0,8).forEach(ev=>{
      const d=document.createElement('div');
      const decision=ev.decision||'allow';
      d.className='auditItem '+(decision==='block'?'block':decision==='review'?'review':'allow');
      d.innerHTML=`<strong>${fmt(ev.event_type)} · ${fmt(decision)}</strong><div>${fmt(ev.defense_classification)} · ${fmt(ev.legal_status)}</div><div class="muted">${fmt(ev.timestamp)}</div>`;
      list.appendChild(d);
    });
  }catch(e){}
}


async function loadFeedActivationStatus(){
  try{
    const x=await api('/api/feeds/activation-status');
    el('activationBadge').textContent=x.activation_layer||'ready';
    el('activationStatusBox').textContent=`Connected ingestion default: ${x.connected_ingestion_default?'enabled':'disabled'}\nDeterministic fallback default: ${x.deterministic_fallback_default?'ready':'unavailable'}\nPolicy: deterministic stays offline; connected/hybrid require allowlisted source and governance check.`;
    loadFeedAudit();
  }catch(e){
    if(el('activationStatusBox')) el('activationStatusBox').textContent='Feed activation status unavailable: '+e.message;
  }
}
async function feedActivationCheck(){
  const p=payload();
  p.raw_input=el('rawInput').value;
  p.signal=el('rawInput').value;
  try{
    const x=await api('/api/feeds/activation-check',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(p)});
    const d=x.activation_decision||{};
    el('activationBadge').textContent=d.decision||'ready';
    el('activationStatusBox').textContent=`Decision: ${fmt(d.decision)}\nFeed Status: ${fmt(d.feed_status)}\nConnected Allowed: ${d.connected_ingestion_allowed?'yes':'no'}\nDeterministic Fallback: ${d.deterministic_fallback_allowed?'yes':'no'}\nMode: ${fmt(d.execution_mode)}\nSource Category: ${fmt(d.source_category)}\nReason: ${fmt(d.reason)}`;
    loadFeedAudit();
    return d;
  }catch(e){
    el('activationStatusBox').textContent='Feed activation check unavailable: '+e.message;
    return {decision:'deterministic_only',connected_ingestion_allowed:false};
  }
}
async function loadFeedAudit(){
  try{
    const x=await api('/api/feeds/audit');
    const list=el('activationAuditList'); if(!list) return;
    list.innerHTML='';
    (x.events||[]).slice(0,8).forEach(ev=>{
      const d=document.createElement('div');
      const decision=ev.decision||'deterministic_only';
      d.className='activationDecision '+decision;
      d.innerHTML=`<strong>${fmt(ev.event_type)} · ${fmt(decision)}</strong><div>${fmt(ev.feed_status)} · ${fmt(ev.market_universe)}</div><div class="muted">${fmt(ev.timestamp)}</div>`;
      list.appendChild(d);
    });
  }catch(e){}
}


async function loadPublicCompanySourceCatalog(){
  try{
    const x=await api('/api/feeds/public-company-sources');
    el('sourceCatalogBadge').textContent='cataloged';
    el('sourceCatalogStatusBox').textContent=`Public-company catalog ready.\nSources: ${x.source_count}\nUniverses: ${x.universe_count}\nLive ingestion: not enabled`;
    const list=el('sourceCatalogList'); list.innerHTML='';
    (x.universes||[]).forEach(u=>{
      const d=document.createElement('div'); d.className='sourceItem';
      d.innerHTML=`<strong>${fmt(u.name)}</strong><div class="coverage">${fmt(u.coverage_target)}</div><div class="statusLine">Source category: ${fmt(u.source_category)} · Connected scan: ${fmt(u.connected_scan_status)}</div>`;
      list.appendChild(d);
    });
  }catch(e){
    if(el('sourceCatalogStatusBox')) el('sourceCatalogStatusBox').textContent='Source catalog unavailable: '+e.message;
  }
}


async function loadOfflineUniverseResolver(){
  try{
    const status=await api('/api/feeds/offline-universe/status');
    const p=payload();
    const x=await api('/api/feeds/offline-universe/resolve',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(p)});
    const r=x.resolution||{};
    el('offlineResolverBadge').textContent=status.live_ingestion_enabled?'live':'offline';
    el('offlineResolverStatusBox').textContent=`Universe: ${fmt(r.name)}\nCoverage Target: ${fmt(r.coverage_target)}\nResolution: ${fmt(r.resolution_status)}\nConnected Scan: ${fmt(r.connected_scan_status)}\nDeterministic Fallback: ${r.deterministic_fallback?'ready':'unavailable'}`;
    const list=el('offlineResolverList'); list.innerHTML='';
    (r.coverage_buckets||[]).forEach(bucket=>{
      const d=document.createElement('div'); d.className='offlineBucket';
      d.innerHTML=`<strong>${fmt(bucket.name)}</strong><div>${fmt(bucket.purpose)}</div><div class="lens">${fmt(bucket.opportunity_lens)}</div>`;
      list.appendChild(d);
    });
  }catch(e){
    if(el('offlineResolverStatusBox')) el('offlineResolverStatusBox').textContent='Offline resolver unavailable: '+e.message;
  }
}

document.addEventListener('DOMContentLoaded',()=>{loadCatalog();loadPublicCompanySourceCatalog();loadOfflineUniverseResolver();loadFeedStatus();loadFeedActivationStatus();loadRuns();el('refreshBtn').onclick=()=>loadRuns();el('rescanBtn').onclick=rescan;el('neededBtn').onclick=needed;el('generateBtn').onclick=generate;el('runBtn').onclick=launch;el('clearBtn').onclick=()=>{el('rawInput').value='';el('candidateList').innerHTML='';stat('launchStatus','Ready.')};el('loadPreviewBtn').onclick=()=>preview(el('fileSelect').value);document.querySelectorAll('.tab').forEach(b=>b.onclick=()=>tab(b.dataset.tab));['marketUniverseSelect','industryDomainSelect','buyerSegmentSelect','objectiveSelect'].forEach(id=>{const node=el(id); if(node) node.addEventListener('change',()=>loadOfflineUniverseResolver())})});
