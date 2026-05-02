const state={runs:[],selected:null,files:[],active:null,timer:null,cursor:0,catalog:null};
const el=id=>document.getElementById(id); const fmt=(v,f='-')=>(v===undefined||v===null||v==='')?f:String(v);
function stat(id,msg,err=false){const node=el(id);if(!node) return;node.textContent=msg;node.style.color=err?'#f85149':'#8b949e'}
function setLayer(layer,badge,status){
  const badgeNode=el(`layer${layer}Badge`);
  const statusNode=el(`layer${layer}Status`);
  if(badgeNode) badgeNode.textContent=fmt(badge);
  if(statusNode) statusNode.textContent=fmt(status);
}
async function api(path,opt={}){const r=await fetch(path,opt);if(!r.ok)throw new Error(await r.text());const ct=r.headers.get('content-type')||'';return ct.includes('json')?r.json():r.text()}
function option(sel,id,name,extra=''){const o=document.createElement('option');o.value=id;o.textContent=extra?`${name} - ${extra}`:name;sel.appendChild(o)}
async function loadCatalog(){state.catalog=await api('/api/commands');const wf=el('workflowSelect'), em=el('executionModeSelect'), mu=el('marketUniverseSelect'), ind=el('industryDomainSelect'), buyer=el('buyerSegmentSelect'), obj=el('objectiveSelect'), cmd=el('commandSelect');state.catalog.workflow_modes.forEach(x=>option(wf,x.id,x.name));state.catalog.execution_modes.forEach(x=>option(em,x.id,x.name));state.catalog.market_universes.forEach(x=>option(mu,x.id,x.name,x.coverage_count_label));state.catalog.industry_domains.forEach(x=>option(ind,x.id,x.name,x.classification));state.catalog.buyer_segments.forEach(x=>option(buyer,x.id,x.name));state.catalog.opportunity_objectives.forEach(x=>option(obj,x.id,x.name));function fillCmd(){cmd.innerHTML='';state.catalog.commands.filter(c=>c.workflow===wf.value).forEach(c=>option(cmd,c.id,c.name))}wf.onchange=fillCmd;fillCmd();setLayer('Core','command ready',`${state.catalog.commands.length} command(s), ${state.catalog.market_universes.length} market universe(s), ${state.catalog.industry_domains.length} domain(s).`)}
async function applyDesktopLiveMode(){try{const h=await api('/api/health');if(!h.desktop_live)return;const em=el('executionModeSelect'),mu=el('marketUniverseSelect'),ind=el('industryDomainSelect'),obj=el('objectiveSelect');if(em)em.value='hybrid';if(mu)mu.value='sp500_public';if(ind)ind.value='information_technology';if(obj)obj.value='discover_market_gaps';stat('launchStatus','Desktop live mode is enabled. Hybrid mode and public-company universe are selected.')}catch(e){}}
function payload(){return {workflow:el('workflowSelect').value,execution_mode:el('executionModeSelect').value,market_universe:el('marketUniverseSelect').value,industry_domain:el('industryDomainSelect').value,buyer_segment:el('buyerSegmentSelect').value,objective:el('objectiveSelect').value,command_id:el('commandSelect').value,signal:el('rawInput').value,count:5}}
function enrichmentHtml(c){
  const e=c.connected_enrichment||{};
  if(!e || !e.safe_to_enrich) return '<div class="field muted"><b>Connected Enrichment:</b> no safe normalized signal match yet</div>';
  const types=(e.top_signal_types||[]).slice(0,3).join(', ')||'connected signal';
  return `<div class="enrichmentBox"><b>Connected Enrichment</b><div>Relevance: ${fmt(e.opportunity_relevance)} (${fmt(e.enrichment_score)}) · Timing: ${fmt(e.timing_window)} · Signals: ${fmt(e.matched_signal_count,0)}</div><div>Types: ${types}</div><div>${fmt(e.connected_thesis)}</div></div>`;
}
function fusionHtml(c){
  const f=c.hybrid_fusion||{};
  if(!f || !f.hybrid_score) return '';
  const cls=f.status==='hybrid_ready'?'fusionBox ready':'fusionBox';
  return `<div class="${cls}"><b>Hybrid Fusion</b><div>Readiness: ${fmt(f.hybrid_readiness)} - Score: ${fmt(f.hybrid_score)} - Mode: ${fmt(f.recommended_mode)}</div><div>${fmt(f.fusion_summary)}</div></div>`;
}
function cardHtml(c, isCandidate=true){return `<div class="candidate"><strong>${fmt(c.title)}</strong><div class="field"><b>Market Gap:</b> ${fmt(c.market_gap)}</div><div class="field"><b>Needed Solution:</b> ${fmt(c.needed_solution)}</div><div class="field"><b>Opportunity Direction:</b> ${fmt(c.opportunity_direction)}</div><div class="field"><b>Why Now:</b> ${fmt(c.why_now)}</div>${isCandidate?enrichmentHtml(c):''}${isCandidate?fusionHtml(c):''}${isCandidate?`<div class="field"><b>Selection Score:</b> ${fmt(c.selection_score)} - ${fmt(c.confidence_label)}</div><button data-run="${c.candidate_id}">Run This Opportunity</button>`:''}</div>`}
async function needed(){stat('launchStatus','Searching market-wide needed solution areas...');setLayer('Core','searching','Searching market-wide needed solution directions from the selected command context.');const x=await api('/api/opportunities/search-needed-solutions',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload())});const box=el('candidateList');box.innerHTML='';(x.directions||[]).forEach(c=>{const wrap=document.createElement('div');wrap.innerHTML=cardHtml(c,false);box.appendChild(wrap.firstChild)});setLayer('Core','needs found',`${(x.directions||[]).length} needed solution direction(s) ready for candidate generation.`);stat('launchStatus',`Found ${(x.directions||[]).length} needed solution direction(s).`)}
async function generate(){stat('launchStatus','Generating protected opportunity selection...');setLayer('Core','generating','Producing protected opportunity cards from the active workflow, market universe, and buyer context.');const x=await api('/api/opportunities/generate',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload())});const box=el('candidateList');box.innerHTML='';(x.candidates||[]).forEach(c=>{const wrap=document.createElement('div');wrap.innerHTML=cardHtml(c,true);const node=wrap.firstChild;node.querySelector('button').onclick=()=>runCandidate(c.candidate_id);box.appendChild(node)});const ce=x.connected_enrichment||{};const hf=x.hybrid_fusion||{};setLayer('Core','cards ready',`${(x.candidates||[]).length} candidate(s), ${fmt(ce.enriched_candidate_count,0)} enriched, ${fmt(hf.hybrid_candidate_count,0)} hybrid-ready.`);stat('launchStatus',`Generated ${(x.candidates||[]).length} opportunity candidate(s). Connected enrichment: ${fmt(ce.enriched_candidate_count,0)}/${fmt((x.candidates||[]).length,0)} enriched from ${fmt(ce.normalized_signal_count,0)} normalized signal(s). Hybrid-ready: ${fmt(hf.hybrid_candidate_count,0)}. Internal construction protected.`)}
async function runCandidate(id){resetEvents();stat('launchStatus','Launching selected opportunity...');setLayer('Core','running','Running the selected opportunity through Claire and watching live events.');const x=await api('/api/opportunities/run-candidate',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({candidate_id:id})});if(x.status==='blocked'){stat('launchStatus','Blocked by governance hard stop. See audit panel.',true);setLayer('Trust','blocked','Governance blocked this opportunity before launch.');loadAuditLog();return}state.active=x.event_run_id;watch()}
function title(r){return r.category_name||r.sector||r.folder_name||r.run_id||'Claire run'}
function renderRuns(){const list=el('runList');const count=el('runCount');if(count) count.textContent=state.runs.length;if(!list) return;list.innerHTML='';if(!state.runs.length){list.innerHTML='<div class="status">No runs found.</div>';return} state.runs.forEach(r=>{const d=document.createElement('div');d.className='runCard'+(state.selected&&state.selected.run_id===r.run_id?' active':'');d.innerHTML=`<strong>${fmt(title(r))}</strong><div class="meta">${fmt(r.created_at)}<br>Sector: ${fmt(r.sector)}<br>Decision: ${fmt(r.decision_classification)} · Files: ${fmt(r.written_file_count)}</div>`;d.onclick=()=>selectRun(r);list.appendChild(d)})}
function renderCards(r){const c=[['Run ID',r.run_id],['Output Folder',r.output_dir],['Domain',r.domain],['Sector',r.sector],['Category',r.category_name],['Decision',r.decision_classification],['Breakthrough',r.breakthrough_classification],['Portfolio Score',r.portfolio_score],['Export Level',r.export_package_level],['Export Score',r.export_package_score],['Documents',r.document_count],['Written Files',r.written_file_count]];el('summaryCards').innerHTML=c.map(([a,b])=>`<div class="card"><h3>${a}</h3><p>${fmt(b)}</p></div>`).join('')}
async function preview(name){if(!state.selected||!name)return;el('fileSelect').value=name;el('previewBox').textContent='Loading...';try{const x=await api(`/api/runs/${encodeURIComponent(state.selected.run_id)}/files/${encodeURIComponent(name)}?max_chars=120000`);el('previewBox').textContent=typeof x==='string'?x:(x.content||JSON.stringify(x,null,2));tab('preview')}catch(e){el('previewBox').textContent=e.message}}
function tab(name){document.querySelectorAll('.tab').forEach(b=>b.classList.toggle('active',b.dataset.tab===name));['summary','files','preview','raw'].forEach(t=>el(t+'Tab').classList.toggle('hidden',t!==name))}

function esc(v){
  return fmt(v).replace(/[&<>"']/g,ch=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[ch]));
}
function scoreOf(scores,names){
  for(const name of names){
    const v=scores&&scores[name];
    if(v!==undefined&&v!==null&&v!=='') return v;
  }
  return null;
}
function scoreText(v){
  if(v===undefined||v===null||v==='') return '-';
  const n=Number(v);
  if(!Number.isFinite(n)) return fmt(v);
  if(n>=0&&n<=1) return `${Math.round(n*100)}%`;
  if(Math.abs(n)<10) return n.toFixed(1);
  return String(Math.round(n));
}
function cleanDecision(v){
  return fmt(v,'Pending').replace(/_/g,' ').replace(/\s+/g,' ').trim().toUpperCase();
}
function decisionTone(v){
  const d=String(v||'').toLowerCase();
  if(d.includes('block')||d.includes('no')||d.includes('fail')||d.includes('reject')) return 'no-go';
  if(d.includes('go')||d.includes('approve')||d.includes('pass')) return 'go';
  return '';
}
function firstText(obj,keys,fallback='ready'){
  if(!obj) return fallback;
  if(typeof obj==='string') return obj;
  for(const k of keys){
    const v=obj[k];
    if(typeof v==='string'&&v.trim()) return v.trim();
  }
  return fallback;
}
function compactText(text,limit=120){
  const s=fmt(text).replace(/\s+/g,' ').trim();
  return s.length>limit?s.slice(0,limit-1)+'...':s;
}
function pipelineScores(data,r){
  return Object.assign({},r&&r.domain_scores||{},r&&r.scores||{},data&&data.domain_scores||{},data&&data.scores||{});
}
function engineGroups(data,r){
  const scores=pipelineScores(data,r);
  const detail=(key,fb)=>firstText(data&&data[key],['summary','assessment','recommendation','gap_explanation','market_gap','status','rationale'],fb);
  return [
    {
      label:'Market',
      score:scoreOf(scores,['opportunity_score','market_formation_score','trend_trajectory_score','discovery_score']),
      items:[
        ['Market gap',scoreOf(scores,['opportunity_score','discovery_score']),detail('market_gap','gap detection complete')],
        ['Opportunity discovery',scoreOf(scores,['opportunity_priority_score','opportunity_score']),detail('opportunity_discovery','opportunity path mapped')],
        ['Strategic positioning',scoreOf(scores,['strategic_positioning_score','narrative_strength_score']),detail('strategic_positioning','positioning assessed')]
      ]
    },
    {
      label:'Technical',
      score:scoreOf(scores,['technical_feasibility_score','architecture_readiness_score','buildability_score']),
      items:[
        ['Technical feasibility',scoreOf(scores,['technical_feasibility_score','feasibility_score']),detail('technical_feasibility','feasibility assessed')],
        ['Architecture readiness',scoreOf(scores,['architecture_readiness_score','integration_readiness_score']),'architecture readiness scored'],
        ['Buildability',scoreOf(scores,['buildability_score','implementation_complexity_score']),'build path evaluated']
      ]
    },
    {
      label:'Financial',
      score:scoreOf(scores,['portfolio_score','acquisition_score','acquirer_positioning_score','matching_score']),
      items:[
        ['Portfolio fit',scoreOf(scores,['portfolio_score','packaging_readiness_score']),detail('portfolio_binder','portfolio package assessed')],
        ['Acquirer matching',scoreOf(scores,['acquirer_positioning_score','matching_score']),detail('acquirer_matches','buyer and acquirer fit checked')],
        ['Deal readiness',scoreOf(scores,['acquisition_score','productization_score']),detail('deal_exit_modeling','deal path modeled')]
      ]
    },
    {
      label:'Regulatory',
      score:scoreOf(scores,['validation_burden_score','control_signal_score','evidence_signal_score']),
      items:[
        ['Validation burden',scoreOf(scores,['validation_burden_score','data_readiness_score']),'validation load assessed'],
        ['Control signals',scoreOf(scores,['control_signal_score','evidence_signal_score']),'evidence and controls reviewed'],
        ['Governance evidence',scoreOf(scores,['source_quality_score','knowledge_quality_score']),'source quality and evidence boundaries checked']
      ]
    }
  ];
}
function pipelineModel(data,r={}){
  const selected=!!(data||(r&&r.run_id));
  const scores=pipelineScores(data,r);
  const status=selected?'done':'idle';
  return {
    ingestion:{label:'Ingestion',status,score:scoreOf(scores,['knowledge_quality_score','coverage_score','source_quality_score','source_count']),metrics:[
      ['Knowledge quality',scoreOf(scores,['knowledge_quality_score']),'source context captured'],
      ['Coverage',scoreOf(scores,['coverage_score','source_count']),'market and evidence coverage'],
      ['Source quality',scoreOf(scores,['source_quality_score']),'input trust posture']
    ]},
    semantic:{label:'Semantic',status,score:scoreOf(scores,['semantic_density_score','signal_quality_score','routing_confidence_score']),metrics:[
      ['Semantic density',scoreOf(scores,['semantic_density_score']),'meaning extraction strength'],
      ['Signal quality',scoreOf(scores,['signal_quality_score','evidence_signal_score']),'signal clarity'],
      ['Routing confidence',scoreOf(scores,['routing_confidence_score']),'domain and workflow routing']
    ]},
    fusion:{label:'Fusion',status,score:scoreOf(scores,['portfolio_score','optimization_score','viability_score','opportunity_priority_score']),metrics:[
      ['Portfolio score',scoreOf(scores,['portfolio_score']),'cross-engine fit'],
      ['Viability',scoreOf(scores,['viability_score','analysis_score']),'solution viability'],
      ['Opportunity priority',scoreOf(scores,['opportunity_priority_score','opportunity_score']),'ranked opportunity strength']
    ]},
    engines:{label:'Domain Engines',status,score:scoreOf(scores,['technical_feasibility_score','opportunity_score','portfolio_score','validation_burden_score']),groups:engineGroups(data,r)},
    decision:{label:'Decision',status,score:scoreOf(scores,['_confidence','breakthrough_score','breakthrough_synthesis_score']),metrics:[
      ['Decision class',cleanDecision(r.decision_classification||(data&&data.decision_classification)),'classification output'],
      ['Breakthrough',fmt(r.breakthrough_classification||(data&&data.breakthrough_classification)),'breakthrough classification'],
      ['Domain',fmt((data&&data.domain)||r.domain||r.sector),'resolved domain']
    ]}
  };
}
function renderPipelineDetail(key,stage){
  const box=el('pipelineDetail'); if(!box||!stage) return;
  if(stage.status==='idle'){
    box.innerHTML=`<strong>${esc(stage.label)}</strong><div class="muted">Run Claire or select a completed run to inspect this stage.</div>`;
    return;
  }
  if(key==='engines'){
    box.innerHTML=`<strong>Domain Engines</strong><div class="muted">Grouped engine output. Open a group to inspect the underlying checks.</div><div class="pipelineDetailGrid">${(stage.groups||[]).map((g,i)=>`<details class="engineGroup" ${i===0?'open':''}><summary>${esc(g.label)} <span class="muted">${scoreText(g.score)}</span></summary><ul>${g.items.map(([label,score,note])=>`<li><b>${esc(label)}</b> ${scoreText(score)}<br><span>${esc(compactText(note))}</span></li>`).join('')}</ul></details>`).join('')}</div>`;
    return;
  }
  box.innerHTML=`<strong>${esc(stage.label)}</strong><div class="pipelineDetailGrid">${(stage.metrics||[]).map(([label,score,note])=>`<div class="pipelineMetric"><b>${esc(label)}</b><div>${scoreText(score)}</div><span class="muted">${esc(note)}</span></div>`).join('')}</div>`;
}
function renderPipeline(data,r={}){
  const model=pipelineModel(data,r);
  const keys=['ingestion','semantic','fusion','engines','decision'];
  const active=keys.includes(state.pipelineStage)?state.pipelineStage:'ingestion';
  state.pipelineStage=active;
  keys.forEach(key=>{
    const btn=document.querySelector(`.pipelineStage[data-stage="${key}"]`);
    const stage=model[key];
    if(!btn||!stage) return;
    btn.classList.remove('idle','running','done','active');
    btn.classList.add(stage.status||'idle');
    btn.classList.toggle('active',key===active);
    const score=btn.querySelector('b');
    if(score) score.textContent=stage.score!==null&&stage.score!==undefined?scoreText(stage.score):fmt(stage.status);
    btn.onclick=()=>{
      state.pipelineStage=key;
      document.querySelectorAll('.pipelineStage').forEach(n=>n.classList.toggle('active',n.dataset.stage===key));
      renderPipelineDetail(key,model[key]);
    };
  });
  if(el('pipelineBadge')) el('pipelineBadge').textContent=keys.every(k=>model[k].status==='done')?'done':'idle';
  renderPipelineDetail(active,model[active]);
}
function pushSignal(list,label,value){
  if(Array.isArray(value)){value.forEach(v=>pushSignal(list,label,v));return}
  if(value&&typeof value==='object'){
    pushSignal(list,label,value.title||value.summary||value.name||value.term);
    return;
  }
  const text=compactText(value,96);
  if(!text||text==='-') return;
  const key=(label+'|'+text).toLowerCase();
  if(list.some(x=>(x.label+'|'+x.text).toLowerCase()===key)) return;
  list.push({label,text});
}
function topSignals(data,r={}){
  const sx=data&&data.signal_extraction||{};
  const gap=data&&data.market_gap||{};
  const out=[];
  pushSignal(out,'Evidence',(sx.evidence_signals||{}).matched_terms);
  pushSignal(out,'Control',(sx.control_signals||{}).matched_terms);
  pushSignal(out,'Keyword',sx.extracted_keywords||data&&data.keywords);
  pushSignal(out,'Gap',gap.gap_type||gap.gap_explanation);
  pushSignal(out,'Domain',(data&&data.domain)||r.domain||r.sector);
  pushSignal(out,'Breakthrough',r.breakthrough_classification||(data&&data.breakthrough_classification));
  return out.slice(0,5);
}
function renderDecision(r={},data=null){
  const decision=cleanDecision(r.decision_classification||(data&&data.decision_classification));
  const breakthrough=fmt(r.breakthrough_classification||(data&&data.breakthrough_classification)||r.export_package_level);
  const domain=fmt((data&&data.domain)||r.domain||r.sector);
  const scores=pipelineScores(data,r);
  const confidence=scoreOf(scores,['_confidence','routing_confidence_score','breakthrough_score']);
  const hero=el('decisionHero');
  if(hero){hero.textContent=decision;hero.className=`decisionHero ${decisionTone(decision)}`.trim()}
  if(el('decisionConfidence')) el('decisionConfidence').textContent=confidence!==null?`confidence ${scoreText(confidence)}`:'classified';
  el('decisionValue').textContent=decision;
  el('exportValue').textContent=breakthrough;
  el('filesValue').textContent=domain;
  el('selectedSector').textContent='';
  el('selectedTitle').textContent='';
  el('selectedMeta').textContent='';
  const list=el('topSignalList');
  if(list){
    const signals=topSignals(data,r);
    list.innerHTML=signals.length?signals.map(s=>`<div class="topSignal"><b>${esc(s.label)}</b><span>${esc(s.text)}</span></div>`).join(''):'<div class="muted">Signal summary not exported for this run.</div>';
  }
}
async function loadFullPipeline(r){
  const runId=r&&(r.run_id||r.folder_name);
  if(!runId) return null;
  for(const name of ['full_pipeline_output.json','pipeline_output.json']){
    try{
      const x=await api(`/api/runs/${encodeURIComponent(runId)}/files/${encodeURIComponent(name)}?max_chars=1500000`);
      if(x&&x.status==='success'&&x.content) return JSON.parse(x.content);
    }catch(e){}
  }
  return null;
}
function renderFiles(files){
  state.files=files||[];
  el('fileList').innerHTML='';
  el('fileSelect').innerHTML='';
  state.files.forEach(f=>{
    const row=document.createElement('div');
    row.className='fileRow';
    row.innerHTML=`<div><strong>${esc(f.filename)}</strong><div class="muted">${esc(f.format)} - ${esc(f.size_bytes)} bytes</div></div><button>Preview</button><button>Open</button>`;
    row.children[1].onclick=()=>preview(f.filename);
    row.children[2].onclick=()=>window.open(`/api/runs/${encodeURIComponent(state.selected.run_id)}/files/${encodeURIComponent(f.filename)}?raw=1`,'_blank');
    el('fileList').appendChild(row);
    const o=document.createElement('option');
    o.value=f.filename;
    o.textContent=f.filename;
    el('fileSelect').appendChild(o);
  });
}
async function selectRun(r){
  state.selected=r;
  renderRuns();
  el('emptyState').classList.add('hidden');
  el('detailState').classList.remove('hidden');
  setLayer('Core',fmt(r.decision_classification,'selected'),`${title(r)} selected. Decision: ${fmt(r.decision_classification)}. Files: ${fmt(r.written_file_count,r.document_count||0)}.`);
  renderCards(r);
  renderDecision(r,null);
  renderPipeline(null,r);
  el('rawBox').textContent='Raw JSON hidden until dev mode.';
  const full=await loadFullPipeline(r);
  if(state.selected&&state.selected.run_id===r.run_id){
    renderDecision(r,full);
    renderPipeline(full,r);
  }
  try{
    const x=await api(`/api/runs/${encodeURIComponent(r.run_id)}/files`);
    renderFiles(x.files||[]);
  }catch(e){
    state.files=[];
    el('fileList').innerHTML='';
    el('fileSelect').innerHTML='';
    el('previewBox').textContent=e.message;
  }
}
async function loadRuns(id=null){stat('statusBox','Loading...');try{const x=await api('/api/runs');state.runs=x.runs||[];renderRuns();stat('statusBox',`Loaded ${state.runs.length} run(s).`);const target=id?state.runs.find(r=>r.run_id===id||r.folder_name===id):null;if(target)selectRun(target);else if(state.runs.length&&!state.selected)selectRun(state.runs[0])}catch(e){stat('statusBox','Failed: '+e.message,true)}}
async function rescan(){await api('/api/rescan',{method:'POST'});await loadRuns()}
function addEvents(events){for(const ev of events){const d=document.createElement('div');d.className='event '+(ev.event_type==='complete'?'complete':ev.level==='error'?'error':'');d.innerHTML=`<strong>${fmt(ev.stage)} · ${fmt(ev.event_type)}</strong><div>${fmt(ev.message)}</div><div class="muted">${fmt(ev.timestamp)}</div>`;el('eventList').prepend(d);if(ev.progress!==undefined&&ev.progress!==null)el('progressBar').style.width=Math.max(0,Math.min(100,ev.progress))+'%'}}
async function poll(){if(!state.active)return;try{const x=await api(`/api/events/${state.active}?since=${state.cursor}`);addEvents(x.events||[]);state.cursor=x.event_count||state.cursor;if(x.status==='complete'||x.status==='error'){clearInterval(state.timer);state.timer=null;el('liveBadge').textContent=x.status;setLayer('Core',x.status,x.status==='complete'?'Run complete. Export artifacts are ready for review.':'Run failed. Check run events for the failing stage.');if(x.result){await loadRuns(x.result.run_id||x.result.folder_name)}stat('launchStatus',x.status==='complete'?'Run complete.':'Run failed: '+fmt(x.error),x.status==='error')}}catch(e){}}
function watch(){stat('launchStatus','Run started. Watching live events...');if(state.timer)clearInterval(state.timer);state.timer=setInterval(poll,900);poll()}
async function launch(){const raw=el('rawInput').value.trim();if(!raw){stat('launchStatus','Add raw input before launching.',true);return}const gov=await governanceCheck();if(gov.decision==='block'){stat('launchStatus','Blocked by governance hard stop. See audit panel.',true);return}const activation=await feedActivationCheck();if(activation.decision==='block'){stat('launchStatus','Feed activation blocked. See activation panel.',true);return}el('runBtn').disabled=true;resetEvents();try{const p=payload();p.raw_input=raw;const x=await api('/api/evaluate/async',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(p)});state.active=x.event_run_id;watch()}catch(e){stat('launchStatus','Run failed to start: '+e.message,true)}finally{setTimeout(()=>{el('runBtn').disabled=false},1200)}}

function setPipelineRunning(){
  const keys=['ingestion','semantic','fusion','engines','decision'];
  state.pipelineStage='ingestion';
  if(el('pipelineBadge')) el('pipelineBadge').textContent='running';
  keys.forEach((key,i)=>{
    const btn=document.querySelector(`.pipelineStage[data-stage="${key}"]`);
    if(!btn) return;
    btn.classList.remove('idle','running','done','active');
    btn.classList.add(i===0?'running':'idle');
    btn.classList.toggle('active',i===0);
    const score=btn.querySelector('b');
    if(score) score.textContent=i===0?'running':'idle';
    btn.onclick=()=>{
      state.pipelineStage=key;
      document.querySelectorAll('.pipelineStage').forEach(n=>n.classList.toggle('active',n.dataset.stage===key));
      const label=fmt(btn.querySelector('span')&&btn.querySelector('span').textContent,key);
      el('pipelineDetail').innerHTML=`<strong>${esc(label)}</strong><div class="muted">${key==='ingestion'?'Claire is receiving and preparing the input.':'Waiting for the active run to reach this stage.'}</div>`;
    };
  });
  el('pipelineDetail').innerHTML='<strong>Ingestion</strong><div class="muted">Claire is receiving and preparing the input.</div>';
}
function resetEvents(){
  state.cursor=0;
  if(el('eventList')) el('eventList').innerHTML='';
  if(el('progressBar')) el('progressBar').style.width='0%';
  if(el('liveBadge')) el('liveBadge').textContent='running';
  setPipelineRunning();
  setLayer('Core','running','Claire run events are active.');
}

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
    setLayer('Trust',d.decision||'allow',`Legal: ${fmt(d.legal_status)}. Defense: ${fmt(d.defense_classification)}. Action: ${fmt(d.recommended_action)}.`);
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
    setLayer('Trust',d.decision||'ready',`Feed ${fmt(d.feed_status)}. Connected ingestion ${d.connected_ingestion_allowed?'allowed':'held'}. Deterministic fallback ${d.deterministic_fallback_allowed?'ready':'unavailable'}.`);
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

function renderLiveSourceCatalogSources(sources){
  const list=el('liveSourceCatalogList'); if(!list) return;
  list.innerHTML='';
  if(!(sources||[]).length){
    list.innerHTML='<div class="status">No catalog sources resolved yet.</div>';
    return;
  }
  (sources||[]).forEach(src=>{
    const d=document.createElement('div');
    d.className='liveSourceItem';
    d.innerHTML=`<strong>${fmt(src.name)}</strong><div>${fmt(src.source_id)} · ${fmt(src.source_type)} · ${fmt(src.domain)}</div><div class="url">${fmt(src.url)}</div>`;
    list.appendChild(d);
  });
}
async function loadLiveSourceCatalogStatus(){
  try{
    const x=await api('/api/feeds/live-source-catalog/status');
    el('liveSourceCatalogBadge').textContent=x.resolver_enabled?'active':'offline';
    const counts=x.universe_source_counts||{};
    el('liveSourceCatalogStatusBox').textContent=`Catalog: ${fmt(x.catalog_version)}\nPacks: ${fmt(x.source_pack_count,0)}\nActive Sources: ${fmt(x.active_source_count,0)}\nValid Sources: ${fmt(x.valid_source_count,0)}\nS&P 500: ${fmt(counts.sp500_public,0)} · DJIA: ${fmt(counts.djia_public,0)} · NASDAQ: ${fmt(counts.nasdaq_composite,0)}`;
    setLayer('Live',x.resolver_enabled?'catalog active':'catalog offline',`${fmt(x.active_source_count,0)} active source(s), ${fmt(x.valid_source_count,0)} valid source(s).`);
  }catch(e){
    if(el('liveSourceCatalogStatusBox')) el('liveSourceCatalogStatusBox').textContent='Live source catalog unavailable: '+e.message;
  }
}
async function resolveLiveSourceCatalog(){
  const p=payload();
  p.limit=5;
  try{
    const x=await api('/api/feeds/live-source-catalog/resolve',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(p)});
    renderLiveSourceCatalogSources(x.sources||[]);
    if(el('publicSourceUrls')) el('publicSourceUrls').value=(x.source_urls||[]).join('\n');
    el('liveSourceCatalogBadge').textContent=x.status||'resolved';
    el('liveSourceCatalogStatusBox').textContent=`Resolved: ${fmt(x.source_count,0)} source(s)\nUniverse: ${fmt(x.market_universe)}\nCatalog: ${fmt(x.catalog_version)}\nSafe Metadata Only: ${x.safe_metadata_only?'yes':'no'}`;
    setLayer('Live',x.status||'resolved',`${fmt(x.source_count,0)} source(s) resolved for ${fmt(x.market_universe)}.`);
  }catch(e){
    el('liveSourceCatalogStatusBox').textContent='Live source resolve failed: '+e.message;
  }
}
async function checkLiveSourceHealth(){
  const p=payload();
  p.limit=5;
  p.fetch_live=false;
  try{
    const x=await api('/api/feeds/live-source-catalog/health-check',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(p)});
    renderLiveSourceCatalogSources(x.sources||[]);
    el('liveSourceCatalogBadge').textContent=x.status||'checked';
    el('liveSourceCatalogStatusBox').textContent=`Health: ${fmt(x.healthy_count,0)}/${fmt(x.source_count,0)} catalog-valid\nWarnings: ${fmt(x.warning_count,0)}\nLive Fetch: ${x.live_fetch_performed?'performed':'not performed'}\nChecked: ${fmt(x.checked_at)}`;
    setLayer('Live',x.status||'checked',`${fmt(x.healthy_count,0)}/${fmt(x.source_count,0)} catalog source(s) healthy.`);
  }catch(e){
    el('liveSourceCatalogStatusBox').textContent='Live source health check failed: '+e.message;
  }
}


async function loadPublicCompanyLiveScanStatus(){
  try{
    const x=await api('/api/feeds/public-company-live/status');
    el('publicLiveScanBadge').textContent=x.live_enabled?'enabled':'disabled';
    el('publicLiveScanStatusBox').textContent=`Scanner: ${fmt(x.scanner)}\nLive Enabled: ${x.live_enabled?'yes':'no'}\nSafe Metadata Only: ${x.safe_metadata_only?'yes':'no'}\nRequires Feed Activation: ${x.requires_feed_activation?'yes':'no'}\nEnable: CLAIRE_ENABLE_LIVE_FEEDS=1 before starting dashboard`;
    setLayer('Live',x.live_enabled?'scan enabled':'safe offline',`Public scan: ${fmt(x.scanner)}. Metadata-only: ${x.safe_metadata_only?'yes':'no'}.`);
  }catch(e){
    if(el('publicLiveScanStatusBox')) el('publicLiveScanStatusBox').textContent='Live scan status unavailable: '+e.message;
  }
}
function renderNormalizedSignals(signals, summary={}){
  const list=el('normalizedSignalList'); if(!list) return;
  list.innerHTML='';
  el('normalizedSignalBadge').textContent=String((signals||[]).length);
  el('normalizedSignalStatusBox').textContent=`Normalized: ${(signals||[]).length}\nSafe to enrich: ${fmt(summary.safe_to_enrich_count,0)}\nTop signal type: ${fmt(summary.top_signal_type || (summary.signal_types||[])[0])}\nAverage strength: ${fmt(summary.average_strength_score)}`;
  setLayer('Trust',`${fmt(summary.safe_to_enrich_count,0)} safe`,`${(signals||[]).length} normalized signal(s). Top type: ${fmt(summary.top_signal_type || (summary.signal_types||[])[0])}.`);
  if(!(signals||[]).length){
    list.innerHTML='<div class="status">Run a public metadata scan or normalize signals to populate this panel.</div>';
    return;
  }
  (signals||[]).forEach(sig=>{
    const d=document.createElement('div');
    const gov=sig.governance_status||'unknown';
    d.className='normalizedSignal '+(sig.safe_to_enrich?'safe':gov==='block'?'block':'review');
    d.innerHTML=`<strong>${fmt(sig.title)}</strong><div>${fmt(sig.summary)}</div><div class="grid"><div><b>Signal Type</b>${fmt(sig.signal_type)}</div><div><b>Market Universe</b>${fmt(sig.market_universe)}</div><div><b>Industry / Domain</b>${fmt(sig.industry_domain)}</div><div><b>Source Category</b>${fmt(sig.source_category)}</div><div><b>Governance Status</b>${fmt(sig.governance_status)}</div><div><b>Opportunity Relevance</b>${fmt(sig.opportunity_relevance)} (${fmt(sig.opportunity_relevance_score)})</div><div><b>Signal Strength</b>${fmt(sig.signal_strength)} (${fmt(sig.signal_strength_score)})</div><div><b>Safe to Enrich</b>${sig.safe_to_enrich?'yes':'no'}</div></div>`;
    list.appendChild(d);
  });
}
async function loadNormalizedSignals(){
  try{
    const x=await api('/api/signals/normalized');
    renderNormalizedSignals(x.signals||[], x.summary||{});
  }catch(e){
    if(el('normalizedSignalStatusBox')) el('normalizedSignalStatusBox').textContent='Normalized signals unavailable: '+e.message;
  }
}
function renderLifecycle(registry, provenance){
  const list=el('lifecycleList'); if(!list) return;
  const stages=(registry&&registry.stages)||[];
  const rules=(provenance&&provenance.threshold_rules)||[];
  const inputs=(provenance&&provenance.calibration_inputs)||[];
  el('lifecycleBadge').textContent=`${stages.length} stages`;
  el('lifecycleStatusBox').textContent=`Stages: ${stages.length}\nThreshold rules: ${rules.length}\nCalibration inputs: ${inputs.length}`;
  list.innerHTML='';
  stages.slice(0,21).forEach(s=>{
    const d=document.createElement('div');
    d.className='lifecycleItem';
    d.innerHTML=`<strong><span class="stageNo">${fmt(s.stage)}.</span> ${fmt(s.name)}</strong><div><span class="category">${fmt(s.category)}</span> · ${fmt(s.output_key)}</div><div>${fmt(s.objective)}</div>`;
    list.appendChild(d);
  });
  rules.slice(0,5).forEach(r=>{
    const d=document.createElement('div');
    d.className='lifecycleItem';
    d.innerHTML=`<strong class="rule">${fmt(r.id)}</strong><div>${fmt(r.metric)}: ${fmt(r.rule)}</div><div>${fmt(r.purpose)}</div>`;
    list.appendChild(d);
  });
}
async function loadLifecycleProvenance(){
  try{
    const registry=await api('/api/lifecycle/stage-registry');
    const provenance=await api('/api/lifecycle/threshold-provenance');
    renderLifecycle(registry, provenance);
  }catch(e){
    if(el('lifecycleStatusBox')) el('lifecycleStatusBox').textContent='Lifecycle provenance unavailable: '+e.message;
  }
}
function renderModeStatus(status){
  const list=el('modeProfileList'); if(!list) return;
  const selected=el('executionModeSelect') ? el('executionModeSelect').value : status.default_mode;
  const profiles=status.profiles||[];
  el('modeBadge').textContent=selected||status.default_mode||'deterministic';
  el('modeStatusBox').textContent=`Controller: ${fmt(status.controller)}\nDefault: ${fmt(status.default_mode)}\nModes: ${(status.supported_modes||[]).join(', ')}`;
  setLayer('Trust',selected||status.default_mode||'deterministic',`Mode controller active. Supported modes: ${(status.supported_modes||[]).join(', ')}.`);
  list.innerHTML='';
  profiles.forEach(p=>{
    const d=document.createElement('div');
    d.className='modeProfile'+(p.mode===selected?' active':'');
    d.innerHTML=`<strong>${fmt(p.name)}</strong><div>Connected: ${fmt(p.connected_ingestion)} · Core: ${fmt(p.deterministic_core)} · Fusion: ${fmt(p.hybrid_fusion)}</div><div class="posture">${fmt(p.safety_posture)}</div>`;
    list.appendChild(d);
  });
}
async function loadModeStatus(){
  try{
    const status=await api('/api/modes/status');
    renderModeStatus(status);
  }catch(e){
    if(el('modeStatusBox')) el('modeStatusBox').textContent='Mode governance unavailable: '+e.message;
  }
}
function renderSystemStatus(status){
  const list=el('systemStatusList'); if(!list) return;
  const subs=status.subsystems||[];
  el('systemStatusBadge').textContent=fmt(status.completion_posture);
  el('systemStatusBox').textContent=`Ready: ${fmt(status.ready_subsystem_count,0)}/${fmt(status.subsystem_count,0)}\nNext: ${fmt((status.next_focus||{}).name)}\n${fmt((status.next_focus||{}).reason)}`;
  setLayer('Runtime',fmt(status.completion_posture),`${fmt(status.ready_subsystem_count,0)}/${fmt(status.subsystem_count,0)} subsystems ready. Next: ${fmt((status.next_focus||{}).name)}.`);
  list.innerHTML='';
  subs.forEach(s=>{
    const d=document.createElement('div');
    d.className='systemItem '+fmt(s.state);
    d.innerHTML=`<strong>${fmt(s.name)}</strong><div><span class="state">${fmt(s.state)}</span></div><div>${fmt(s.detail)}</div>`;
    list.appendChild(d);
  });
}
async function loadSystemStatus(){
  try{
    const status=await api('/api/dashboard/system-status');
    renderSystemStatus(status);
  }catch(e){
    if(el('systemStatusBox')) el('systemStatusBox').textContent='System status unavailable: '+e.message;
  }
}
async function runPublicCompanyLiveScan(){
  stat('launchStatus','Running public-company metadata scan readiness check...');
  const p=payload();
  p.signal=el('rawInput').value;
  p.source_urls=(el('publicSourceUrls').value||'').split(/\r?\n/).map(x=>x.trim()).filter(Boolean);
  p.catalog_limit=5;
  try{
    const x=await api('/api/feeds/public-company-live/scan',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(p)});
    const list=el('publicLiveScanList'); list.innerHTML='';
    el('publicLiveScanBadge').textContent=x.status||'checked';
    if(x.status!=='success'){
      const d=document.createElement('div'); d.className='publicSignal '+(x.status||'disabled');
      d.innerHTML=`<strong>${fmt(x.status)}</strong><div>${(x.warnings||[]).join(' ') || fmt((x.activation_decision||{}).reason)}</div>`;
      list.appendChild(d);
    }
    (x.signals||[]).forEach(sig=>{
      const d=document.createElement('div'); d.className='publicSignal '+(sig.status||'success');
      d.innerHTML=`<strong>${fmt(sig.title)}</strong><div>${fmt(sig.snippet)}</div><div class="url">${fmt(sig.source_url)}</div>`;
      list.appendChild(d);
    });
    renderNormalizedSignals(x.normalized_signals||[], x.normalized_summary||{});
    if(x.catalog_resolution) renderLiveSourceCatalogSources(x.catalog_resolution.sources||[]);
    const catalogUsed=x.catalog_sources_used?'yes':'no';
    el('publicLiveScanStatusBox').textContent=`Status: ${fmt(x.status)}\nRecords: ${fmt(x.record_count || (x.signals||[]).length,0)}\nConnected Allowed: ${((x.activation_decision||{}).connected_ingestion_allowed)?'yes':'no'}\nCatalog Sources Used: ${catalogUsed}\nWarnings: ${(x.warnings||[]).join(' ')}`;
    setLayer('Live',fmt(x.status),`${fmt(x.record_count || (x.signals||[]).length,0)} public metadata record(s), catalog used: ${catalogUsed}.`);
    loadFeedAudit();
  }catch(e){
    el('publicLiveScanStatusBox').textContent='Live scan failed: '+e.message;
  }
}

function renderCommandItems(items){
  const list=el('commandCenterList'); if(!list) return;
  list.innerHTML='';
  (items||[]).forEach(item=>{
    const d=document.createElement('div');
    d.className='commandItem '+fmt(item.status,'ready');
    d.innerHTML=`<strong>${fmt(item.name)}</strong><div>${fmt(item.detail)}</div>`;
    list.appendChild(d);
  });
}
async function loadCommandCenter(){
  try{
    const health=await api('/api/health');
    const portable=await api('/api/portable/status');
    const shell=await api('/api/desktop-app/status');
    const orchestration=await api('/api/feeds/live-orchestration/status');
    el('commandCenterBadge').textContent=health.app_shell?'app shell':health.desktop_live?'desktop live':'local';
    el('commandCenterStatusBox').textContent=`Desktop Live: ${health.desktop_live?'yes':'no'}\nLive Connected: ${health.live_connected_enabled?'yes':'no'}\nPortable Ready: ${portable.ready_for_flash_drive_use?'yes':'needs check'}\nLive Intelligence: ${orchestration.desktop_live_ready?'ready':'needs catalog'}\nShell: ${shell.ready?'ready':'partial'}`;
    setLayer('Runtime',health.app_shell?'app shell':health.desktop_live?'desktop live':'local',`Portable ${portable.ready_for_flash_drive_use?'ready':'needs check'}, shell ${shell.ready?'ready':'partial'}, live ${orchestration.desktop_live_ready?'ready':'needs catalog'}.`);
    renderCommandItems([
      {name:'Portable Desktop',status:portable.status,detail:portable.recommended_launcher},
      {name:'Live Source Orchestration',status:orchestration.status,detail:`${fmt(orchestration.active_source_count,0)} active source(s)`},
      {name:'Desktop App Shell',status:shell.status,detail:shell.shell_type}
    ]);
  }catch(e){
    if(el('commandCenterStatusBox')) el('commandCenterStatusBox').textContent='Command center unavailable: '+e.message;
  }
}
async function loadEnhancedBridgeStatus(){
  try{
    const x=await api('/api/enhanced-interface/status');
    el('enhancedBridgeBadge').textContent=x.readiness||'mapped';
    el('enhancedBridgeStatusBox').textContent=`Upload: ${fmt(x.source_upload)}\nCapabilities: ${fmt(x.ready_or_starter_count,0)}/${fmt(x.capability_count,0)} service-backed\nKnown connector gaps: ${fmt(x.planned_count,0)}\nBridge: ${fmt(x.bridge_version)}`;
    const list=el('enhancedBridgeList'); if(!list) return;
    list.innerHTML='';
    (x.capabilities||[]).forEach(cap=>{
      const d=document.createElement('div');
      d.className='commandItem '+(cap.state==='planned'?'partial':'ready');
      d.innerHTML=`<strong>${fmt(cap.label)}</strong><div>${fmt(cap.section)} · ${fmt(cap.state)} · ${fmt(cap.service_package)}</div><div>${fmt(cap.backend_endpoint)}</div>`;
      list.appendChild(d);
    });
  }catch(e){
    if(el('enhancedBridgeStatusBox')) el('enhancedBridgeStatusBox').textContent='Enhanced upload bridge unavailable: '+e.message;
  }
}
async function loadLiveIntelligenceStatus(){
  try{
    const x=await api('/api/live-intelligence/status');
    const registry=x.registry||{}, connectors=x.connectors||{}, monitor=x.monitor||{};
    el('liveIntelligenceBadge').textContent=x.live_intelligence_version||'ready';
    el('liveIntelligenceStatusBox').textContent=`Entities: ${fmt(registry.entity_count,0)}\nConnectors: ${fmt(connectors.connector_count,0)}\nMonitor Ready: ${monitor.ready?'yes':'no'}\nChain: ${(x.completion_chain||[]).length} layer(s)`;
    setLayer('Live',x.live_intelligence_version||'ready',`${fmt(registry.entity_count,0)} entities, ${fmt(connectors.connector_count,0)} connectors, monitor ${monitor.ready?'ready':'not ready'}.`);
    const list=el('liveIntelligenceList'); if(!list) return;
    list.innerHTML='';
    (x.completion_chain||[]).forEach(step=>{
      const d=document.createElement('div');
      d.className='commandItem ready';
      d.innerHTML=`<strong>${fmt(step)}</strong><div>installed</div>`;
      list.appendChild(d);
    });
  }catch(e){
    if(el('liveIntelligenceStatusBox')) el('liveIntelligenceStatusBox').textContent='Live intelligence status unavailable: '+e.message;
  }
}
async function runLiveOpportunityMonitor(){
  const p=payload();
  p.signal=el('rawInput').value || 'AI governance market pressure';
  p.entity_limit=4;
  stat('launchStatus','Running live opportunity monitor...');
  try{
    const x=await api('/api/live-intelligence/monitor/run',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(p)});
    const solutions=(x.solutions||{}).candidates||[];
    const activated=x.activated_candidates||[];
    el('liveIntelligenceBadge').textContent=x.live_opportunities_ready?'opportunities ready':fmt(x.status);
    el('liveIntelligenceStatusBox').textContent=`Status: ${fmt(x.status)}\nConnector Records: ${fmt((x.connectors||{}).record_count,0)}\nExtracted Signals: ${fmt((x.extracted||{}).signal_count,0)}\nTrend Clusters: ${fmt((x.clusters||{}).cluster_count,0)}\nGaps: ${fmt((x.gaps||{}).gap_count,0)}\nSolutions: ${fmt(solutions.length,0)}\nRunnable Cards: ${fmt(activated.length,0)}`;
    setLayer('Live',x.live_opportunities_ready?'opportunities ready':fmt(x.status),`${fmt((x.extracted||{}).signal_count,0)} signals, ${fmt((x.clusters||{}).cluster_count,0)} clusters, ${fmt((x.gaps||{}).gap_count,0)} gaps, ${fmt(activated.length,0)} runnable cards.`);
    const list=el('liveIntelligenceList'); if(list){
      list.innerHTML='';
      solutions.slice(0,8).forEach(sol=>{
        const d=document.createElement('div');
        d.className='commandItem ready';
        d.innerHTML=`<strong>${fmt(sol.title)}</strong><div>${fmt(sol.market_gap)}</div><div>Score: ${fmt(sol.solution_score)} · ${fmt(sol.technical_feasibility)}</div>`;
        list.appendChild(d);
      });
    }
    if(activated.length){
      const box=el('candidateList');
      if(box){
        box.innerHTML='';
        activated.forEach(c=>{
          const wrap=document.createElement('div');
          wrap.innerHTML=cardHtml(c,true);
          const node=wrap.firstChild;
          node.querySelector('button').onclick=()=>runCandidate(c.candidate_id);
          box.appendChild(node);
        });
      }
    }
    stat('launchStatus',`Live monitor produced ${solutions.length} solution candidate(s).`);
  }catch(e){
    el('liveIntelligenceStatusBox').textContent='Live monitor failed: '+e.message;
    stat('launchStatus','Live monitor failed: '+e.message,true);
  }
}
async function prepareLiveIntelligence(){
  const p=payload();
  p.catalog_limit=5;
  p.signal=el('rawInput').value || 'public company market pressure';
  stat('launchStatus','Preparing governed live intelligence...');
  try{
    const x=await api('/api/feeds/live-orchestration/run',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(p)});
    const scan=x.scan||{};
    const resolved=x.resolved||{};
    renderLiveSourceCatalogSources(resolved.sources||[]);
    renderNormalizedSignals(x.normalized_signals||[], x.normalized_summary||{});
    el('commandCenterBadge').textContent=x.live_intelligence_ready?'live ready':fmt(x.status);
    el('commandCenterStatusBox').textContent=`Status: ${fmt(x.status)}\nResolved Sources: ${fmt(resolved.source_count,0)}\nScan Records: ${fmt(scan.record_count || (scan.signals||[]).length,0)}\nNormalized: ${fmt((x.normalized_signals||[]).length,0)}\nReady: ${x.live_intelligence_ready?'yes':'not yet'}`;
    setLayer('Live',x.live_intelligence_ready?'live ready':fmt(x.status),`${fmt(resolved.source_count,0)} source(s), ${fmt(scan.record_count || (scan.signals||[]).length,0)} record(s), ${fmt((x.normalized_signals||[]).length,0)} normalized signal(s).`);
    stat('launchStatus',`Live intelligence prepared: ${fmt((x.normalized_signals||[]).length,0)} normalized signal(s).`);
    loadFeedAudit();
  }catch(e){
    el('commandCenterStatusBox').textContent='Live intelligence preparation failed: '+e.message;
    stat('launchStatus','Live intelligence preparation failed: '+e.message,true);
  }
}
async function loadUpdaterStatus(){
  try{
    const x=await api('/api/updater/dashboard-status');
    el('updaterBadge').textContent=x.readiness||'ready';
    el('updaterStatusBox').textContent=`Readiness: ${fmt(x.readiness)}\nWorkflow: ${fmt(x.dashboard_workflow)}\nAllowed Sources: ${fmt((x.allowed_sources||{}).status)}\nRollback Backups: ${fmt(((x.recent_rollbacks||{}).backups||[]).length,0)}`;
    setLayer('Runtime',x.readiness||'ready',`Updater ${fmt(x.dashboard_workflow)}. Allowed sources: ${fmt((x.allowed_sources||{}).status)}.`);
  }catch(e){
    if(el('updaterStatusBox')) el('updaterStatusBox').textContent='Updater workflow unavailable: '+e.message;
  }
}
function renderUpdateResult(x){
  const list=el('updaterList'); if(!list) return;
  list.innerHTML='';
  const d=document.createElement('div');
  d.className='updateItem '+fmt(x.status,'success');
  const manifest=((x.verification||{}).manifest)||{};
  const plan=(x.plan||{}).plan || ((x.install||{}).installed_files)||[];
  d.innerHTML=`<strong>${fmt(x.status)} ${fmt(x.mode,'')}</strong><div>${fmt(manifest.update_name)} ${fmt(manifest.version)}</div><div>Files: ${fmt(plan.length,0)}</div><div>${fmt(x.audit_log)}</div>`;
  list.appendChild(d);
}
async function previewUpdate(){
  const url=el('updateUrlInput').value.trim();
  const expected_sha256=el('updateShaInput').value.trim();
  try{
    const x=await api('/api/updater/preview',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({url,expected_sha256})});
    renderUpdateResult(x);
    el('updaterBadge').textContent='preview';
    el('updaterStatusBox').textContent=`Preview ready.\nPackage: ${fmt((x.download||{}).package_path)}\nFiles: ${fmt((x.verification||{}).file_count,0)}`;
  }catch(e){
    el('updaterStatusBox').textContent='Update preview failed: '+e.message;
  }
}
async function installUpdate(){
  const url=el('updateUrlInput').value.trim();
  const expected_sha256=el('updateShaInput').value.trim();
  try{
    const x=await api('/api/updater/install',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({url,expected_sha256,confirm:true,run_baseline:true})});
    renderUpdateResult(x);
    el('updaterBadge').textContent=x.status||'installed';
    el('updaterStatusBox').textContent=`Install: ${fmt(x.status)}\nInstalled Files: ${fmt(((x.install||{}).installed_files||[]).length,0)}\nBaseline: ${fmt((x.baseline||{}).status,'not run')}`;
  }catch(e){
    el('updaterStatusBox').textContent='Update install failed: '+e.message;
  }
}

function switchMode(mode){
  document.querySelectorAll('.modeTab').forEach(btn=>btn.classList.toggle('active',btn.dataset.mode===mode));
  document.querySelectorAll('.modeView').forEach(view=>view.classList.toggle('active',view.dataset.view===mode));
  const shell=document.querySelector('.modeShell');
  if(shell) shell.dataset.activeMode=mode;
}
function initModeLauncher(){
  document.querySelectorAll('.modeTab').forEach(btn=>btn.onclick=()=>switchMode(btn.dataset.mode));
  switchMode('evaluate');
}
function bind(id,handler){
  const node=el(id);
  if(node) node.onclick=handler;
}
function loadIf(id,handler){
  if(el(id)) handler();
}
function initDiscoverPipeline(){
  const root=el('discoverPipelineRoot');
  if(root&&window.ClaireDiscover&&window.ClaireDiscover.initDiscoverPipeline){
    window.ClaireDiscover.initDiscoverPipeline(root,{api});
  }
}
function initMonitorSurface(){
  const root=el('monitorSurfaceRoot');
  if(root&&window.ClaireMonitor&&window.ClaireMonitor.initMonitorSurface){
    window.ClaireMonitor.initMonitorSurface(root,{api});
  }
}

document.addEventListener('DOMContentLoaded',()=>{
  initModeLauncher();
  initDiscoverPipeline();
  initMonitorSurface();
  loadCatalog().then(applyDesktopLiveMode).then(loadModeStatus);
  loadIf('commandCenterBadge',loadCommandCenter);
  loadIf('enhancedBridgeBadge',loadEnhancedBridgeStatus);
  loadIf('liveIntelligenceBadge',loadLiveIntelligenceStatus);
  loadIf('updaterBadge',loadUpdaterStatus);
  loadIf('systemStatusBadge',loadSystemStatus);
  loadIf('lifecycleBadge',loadLifecycleProvenance);
  loadIf('feedBadge',loadFeedStatus);
  loadIf('activationBadge',loadFeedActivationStatus);
  loadRuns();
  bind('refreshBtn',()=>{
    loadRuns();
    loadIf('commandCenterBadge',loadCommandCenter);
    loadIf('enhancedBridgeBadge',loadEnhancedBridgeStatus);
    loadIf('liveIntelligenceBadge',loadLiveIntelligenceStatus);
    loadIf('updaterBadge',loadUpdaterStatus);
    loadIf('systemStatusBadge',loadSystemStatus);
    initDiscoverPipeline();
    initMonitorSurface();
  });
  bind('liveMonitorBtn',runLiveOpportunityMonitor);
  bind('liveIntelStatusBtn',loadLiveIntelligenceStatus);
  bind('prepareLiveIntelBtn',prepareLiveIntelligence);
  bind('portableCheckBtn',loadCommandCenter);
  bind('desktopShellCheckBtn',loadCommandCenter);
  bind('updatePreviewBtn',previewUpdate);
  bind('updateInstallBtn',installUpdate);
  bind('resolveLiveSourcesBtn',resolveLiveSourceCatalog);
  bind('checkLiveSourcesBtn',checkLiveSourceHealth);
  bind('publicLiveScanBtn',runPublicCompanyLiveScan);
  bind('neededBtn',needed);
  bind('generateBtn',generate);
  bind('rescanBtn',rescan);
  bind('runBtn',launch);
  bind('clearBtn',()=>{
    el('rawInput').value='';
    const candidateList=el('candidateList');
    if(candidateList) candidateList.innerHTML='';
    stat('launchStatus','Ready.');
  });
  bind('loadPreviewBtn',()=>preview(el('fileSelect').value));
  document.querySelectorAll('.tab').forEach(b=>b.onclick=()=>tab(b.dataset.tab));
  ['marketUniverseSelect','industryDomainSelect','buyerSegmentSelect','objectiveSelect'].forEach(id=>{
    const node=el(id);
    if(node) node.addEventListener('change',initDiscoverPipeline);
  });
  const modeSel=el('executionModeSelect');
  if(modeSel) modeSel.addEventListener('change',loadModeStatus);
});
