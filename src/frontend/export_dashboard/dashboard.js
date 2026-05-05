const state={runs:[],selected:null,files:[],active:null,timer:null,cursor:0,catalog:null};
state.researchResults=[];
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
function payload(){return {run_type:el('runTypeSelect')?el('runTypeSelect').value:'evaluate_opportunity',workflow:el('workflowSelect').value,execution_mode:el('executionModeSelect').value,market_universe:el('marketUniverseSelect').value,industry_domain:el('industryDomainSelect').value,buyer_segment:el('buyerSegmentSelect').value,objective:el('objectiveSelect').value,command_id:el('commandSelect').value,signal:el('rawInput').value,count:5}}
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
function renderRuns(){const list=el('runList');const count=el('runCount');if(count) count.textContent=state.runs.length;if(!list) return;list.innerHTML='';if(!state.runs.length){list.innerHTML='<div class="status">No runs found.</div>';renderFunctionalSurfaces(state.selected&&state.selected.core_output||{},state.selected||{});return} state.runs.forEach(r=>{const d=document.createElement('div');d.className='runCard'+(state.selected&&state.selected.run_id===r.run_id?' active':'');d.innerHTML=`<strong>${fmt(r.headline||title(r))}</strong><div class="meta">${fmt(r.created_at)}<br>Route: ${fmt(r.route_selected||r.decision_classification)}<br>Status: ${fmt(r.status)} | Confidence: ${fmt(r.confidence||r.portfolio_score)} | Package: ${fmt(r.export_package_level||r.export_level||'unknown')}</div>`;d.onclick=()=>selectRun(r);list.appendChild(d)});renderFunctionalSurfaces(state.selected&&state.selected.core_output||{},state.selected||{})}
function renderCards(r){const c=[['Run ID',r.run_id],['Output Folder',r.output_dir],['Domain',r.domain],['Sector',r.sector],['Category',r.category_name],['Decision',r.decision_classification],['Breakthrough',r.breakthrough_classification],['Portfolio Score',r.portfolio_score],['Export Level',r.export_package_level],['Export Score',r.export_package_score],['Documents',r.document_count],['Written Files',r.written_file_count]];el('summaryCards').innerHTML=c.map(([a,b])=>`<div class="card"><h3>${a}</h3><p>${fmt(b)}</p></div>`).join('')}
async function preview(name){if(!state.selected||!name)return;el('fileSelect').value=name;el('previewBox').textContent='Loading...';try{const x=await api(`/api/runs/${encodeURIComponent(state.selected.run_id)}/files/${encodeURIComponent(name)}?max_chars=120000`);el('previewBox').textContent=typeof x==='string'?x:(x.content||JSON.stringify(x,null,2));tab('preview')}catch(e){el('previewBox').textContent=e.message}}
function tab(name){
  document.querySelectorAll('.tab').forEach(b=>b.classList.toggle('active',b.dataset.tab===name));
  ['summary','files','preview','raw'].forEach(t=>el(t+'Tab').classList.toggle('hidden',t!==name));
  if(name==='raw') loadFullRunJsonOnDemand();
}

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
  const core=data&&data.core_output||{};
  const u=core.user_facing_result||{};
  const c=u.confidence||{};
  const summary=core.run_summary||{};
  return Object.assign(
    {},
    r&&r.domain_scores||{},
    r&&r.scores||{},
    data&&data.domain_scores||{},
    data&&data.scores||{},
    {
      _confidence:c.overall||summary.confidence,
      trend_discovery_score:c.trend,
      thesis_score:c.thesis,
      portfolio_score:c.portfolio||summary.portfolio_score,
      portfolio_optimization_score:c.portfolio_optimization,
      breakthrough_score:c.breakthrough,
      feasibility_score:c.validation,
      acquisition_score:c.acquisition,
      knowledge_quality_score:nested(core,'signal_basis.knowledge_ingestion.knowledge_quality_score.score'),
      coverage_score:nested(core,'signal_basis.knowledge_ingestion.coverage_assessment.score'),
      source_quality_score:nested(core,'signal_basis.knowledge_ingestion.source_quality.score'),
      signal_quality_score:nested(core,'signal_basis.signal_extraction.signal_quality_score.score'),
      semantic_density_score:nested(core,'signal_basis.signal_extraction.semantic_profile.semantic_density_score'),
      routing_confidence_score:nested(core,'signal_basis.signal_extraction.routing_evidence.routing_confidence_score')
    }
  );
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
function nested(obj,path,fallback=null){
  let cur=obj||{};
  for(const part of path.split('.')){
    if(!cur||typeof cur!=='object'||!(part in cur)) return fallback;
    cur=cur[part];
  }
  return cur===undefined||cur===null?fallback:cur;
}
function routeLabel(route){
  return fmt(route,'pending').replace(/_/g,' ');
}
function userFacingResult(data,r={}){
  const core=data&&data.core_output||{};
  if(core.user_facing_result) return core.user_facing_result;
  const trend=data&&data.trend_discovery||{};
  const thesis=data&&data.thesis_formation||{};
  const portfolio=data&&data.portfolio_optimization||{};
  const scores=pipelineScores(data,r);
  const route=core.route_selected||nested(data,'core_lifecycle.route')||portfolio.portfolio_path||'trend_thesis';
  const trends=trend.discovered_trends||[];
  const trendName=(trends[0]&&trends[0].name)||r.category_name||r.sector||'market intelligence opportunity';
  const summary=thesis.thesis_statement||`Claire detected ${trendName} and formed an initial intelligence output.`;
  return {
    headline: `${trendName}: ${routeLabel(route)}`,
    summary,
    route_selected: route,
    trend,
    thesis,
    portfolio:{portfolio_optimization:portfolio,portfolio_score:scores.portfolio_score,optimization_score:scores.portfolio_optimization_score},
    breakthrough:{is_breakthrough:scoreOf(scores,['breakthrough_score'])>=0.65,score:scoreOf(scores,['breakthrough_score']),route_recommendation:thesis.route_recommendation},
    advancement_path:{route_selected:route,portfolio_path:portfolio.portfolio_path},
    solution:{applicable:!!(data&&data.design_output&&data.design_output.status==='success'),solution_output:data&&data.design_output||{}},
    strategy:{strategic_positioning:data&&data.strategic_positioning||{},moat:data&&data.moat||{},business_model:data&&data.business_model||{}},
    acquisition:{deal_exit_modeling:data&&data.deal_exit_modeling||{},acquirer_matches:data&&data.acquirer_matches||[]},
    final_package:{package_profile:data&&data.package_profile||{},export_writer:data&&data.export_writer||{}},
    confidence:{overall:scoreOf(scores,['_confidence','portfolio_score']),trend:scoreOf(scores,['trend_discovery_score']),thesis:scoreOf(scores,['thesis_score']),portfolio:scoreOf(scores,['portfolio_score']),breakthrough:scoreOf(scores,['breakthrough_score'])},
    next_actions:[{action:'review intelligence output',purpose:'decide whether to validate, optimize, escalate, or package the opportunity',priority:'high'}]
  };
}
function requiredResultSections(){
  return ['headline','summary','route_selected','trend','thesis','portfolio','breakthrough','advancement_path','solution','strategy','acquisition','final_package','confidence','next_actions'];
}
function renderCoreOutputUnavailable(message='Core output not available for this run.'){
  const empty=el('userResultEmpty'), stateNode=el('userResultState');
  if(empty) empty.classList.add('hidden');
  if(stateNode) stateNode.classList.remove('hidden');
  if(el('resultRouteBadge')) el('resultRouteBadge').textContent='output unavailable';
  if(el('userResultHeadline')) el('userResultHeadline').textContent='Core output not available';
  if(el('userResultSummary')) el('userResultSummary').textContent=message;
  if(el('resultPathRail')) el('resultPathRail').innerHTML='';
  if(el('resultInsightGrid')) el('resultInsightGrid').innerHTML='<article class="resultInsight"><h3>Missing Contract</h3><p>Run history loaded, but this run does not include core_run_output.json yet.</p></article>';
  if(el('nextActionList')) el('nextActionList').innerHTML='<div class="nextAction"><strong>rerun or export with core output enabled</strong><div>The dashboard needs core_run_output.json to render the user-facing result.</div><div class="muted">high</div></div>';
}
function renderCoreOutputIncomplete(core,r={}){
  const u=core.user_facing_result||{};
  const missing=requiredResultSections().filter(k=>!(k in u));
  const gate=nested(core,'lifecycle_summary.completion_gate',{});
  const next=(u.next_actions&&u.next_actions[0])||(core.next_actions&&core.next_actions[0])||{action:'complete missing output sections',purpose:'repair the core output contract before presenting this run.',priority:'critical'};
  const empty=el('userResultEmpty'), stateNode=el('userResultState');
  if(empty) empty.classList.add('hidden');
  if(stateNode) stateNode.classList.remove('hidden');
  if(el('userResultHeadline')) el('userResultHeadline').textContent=fmt(u.headline||core.route_selected,'Incomplete core output');
  if(el('userResultSummary')) el('userResultSummary').textContent=fmt(u.summary,'Core output exists but is missing required presentation sections.');
  if(el('resultPathRail')) el('resultPathRail').innerHTML='';
  if(el('resultRouteBadge')) el('resultRouteBadge').textContent=`${routeLabel(core.route_selected)} incomplete`;
  if(el('resultInsightGrid')){
    el('resultInsightGrid').innerHTML=`<article class="resultInsight"><h3>Incomplete Output</h3><p>Route: ${esc(routeLabel(core.route_selected))}</p>${resultMetric('Lifecycle',gate.status||core.status,`Missing sections: ${missing.join(', ')||'none reported'}`)}</article>`;
  }
  if(el('nextActionList')) el('nextActionList').innerHTML=`<div class="nextAction"><strong>${esc(next.action)}</strong><div>${esc(next.purpose)}</div><div class="muted">${esc(next.priority||'high')}</div></div>`;
}
function resultMetric(title,value,note){
  return `<div class="metricLine"><span>${esc(title)}</span><b>${esc(scoreText(value))}</b></div>${note?`<p>${esc(compactText(note,150))}</p>`:''}`;
}
function line(label,value){return `<div><b>${esc(label)}:</b> ${esc(fmt(value,'not produced for this route'))}</div>`}
function listItems(items,empty='Not produced for this route'){
  const arr=Array.isArray(items)?items.filter(Boolean):[];
  return arr.length?`<ul>${arr.slice(0,6).map(v=>`<li>${esc(typeof v==='object'?compactText(JSON.stringify(v),160):v)}</li>`).join('')}</ul>`:`<div class="muted">${esc(empty)}</div>`;
}
function sectionHtml(title,body){return `<h4>${esc(title)}</h4>${body}`}
function setText(id,value){const node=el(id); if(node) node.textContent=value}
function setHtml(id,value){const node=el(id); if(node) node.innerHTML=value}
function trendStage(confidence, breakthrough){
  const c=Number(confidence||0);
  if(breakthrough) return 'breakthrough-level';
  if(c>=0.72) return 'validated';
  if(c>=0.42) return 'forming';
  return 'weak';
}
function renderCorePanels(core={},r={}){
  const u=core.user_facing_result||core||{};
  const confidence=core.confidence||u.confidence||{};
  const trend=core.trend_discovery||u.trend||{};
  const thesis=core.thesis||u.thesis||{};
  const discovery=core.discovery||u.discovery||{};
  const signalBasis=core.signal_basis||{};
  const portfolio=core.portfolio||u.portfolio||{};
  const breakthrough=core.breakthrough||u.breakthrough||{};
  const advancement=core.advancement_path||u.advancement_path||{};
  const technology=core.technology_intelligence||u.technology_intelligence||{};
  const autodesign=core.autodesign||u.autodesign||{};
  const designPortal=core.design_portal||u.design_portal||{};
  const solution=core.solution||u.solution||{};
  const acquisition=core.acquisition||u.acquisition||{};
  const finalPackage=core.final_package||u.final_package||{};
  const stages=nested(core,'lifecycle_summary.stages',[]);
  const skipped=(stages||[]).filter(s=>s.status==='skipped_by_route').map(s=>`${s.number}. ${s.name}`);
  const required=(stages||[]).filter(s=>['complete','failed','blocked','insufficient_data'].includes(s.status)).slice(0,8).map(s=>`${s.number}. ${s.name} (${s.status})`);
  const scan=core.scan_iterations||[];
  if(el('scanProgressBadge')) el('scanProgressBadge').textContent=scan.length?`${scan.length} iteration(s)`:fmt(discovery.scan_terminal_state,'waiting');
  if(el('scanProgressList')){
    el('scanProgressList').innerHTML=scan.length?scan.map(it=>`<div class="scanIteration"><strong>Iteration ${esc(it.iteration)}</strong><div class="scanIterationGrid"><span>Signals<b>${esc(fmt(it.signals_found,0))}</b></span><span>Trend<b>${esc(scoreText(it.trend_confidence))}</b></span><span>Discovery<b>${esc(scoreText(it.discovery_confidence))}</b></span><span>Breakthrough<b>${esc(scoreText(it.breakthrough_confidence))}</b></span><span>Decision<b>${esc(fmt(it.route_decision))}</b></span><span>Terminal<b>${esc(fmt(core.status))}</b></span></div><div class="muted">${esc(fmt(it.terminal_reason))}</div></div>`).join(''):'<div class="muted">Waiting for scan continuation output.</div>';
  }
  if(el('routeDecisionBadge')) el('routeDecisionBadge').textContent=routeLabel(core.route_selected||u.route_selected);
  if(el('routeDecisionBox')) el('routeDecisionBox').innerHTML=[
    line('Selected route',routeLabel(core.route_selected||u.route_selected)),
    line('Reason',discovery.scan_terminal_reason||breakthrough.route_recommendation||nested(core,'signal_basis.source_summary.scan_terminal_reason')),
    line('Breakthrough trigger',breakthrough.is_breakthrough?'triggered':'not triggered'),
    line('Design trigger',solution.applicable?'triggered':'not triggered'),
    line('Design required',designPortal.required?'yes':'no'),
    line('AutoDesign',autodesign.status||'skipped by route'),
    line('Design Portal',designPortal.status||'skipped by route'),
    line('Next route',nested(advancement,'downstream_action')||(u.next_actions||[])[0]?.action),
  ].join('');
  const trendName=nested(trend,'discovered_trends.0.name','No trend discovered yet');
  if(el('trendThesisBadge')) el('trendThesisBadge').textContent=trendStage(confidence.trend,breakthrough.is_breakthrough);
  if(el('trendThesisBox')) el('trendThesisBox').innerHTML=[
    line('Trend',trendName),
    line('Strength',scoreText(nested(trend,'discovery_score.score',confidence.trend))),
    line('Stage',trendStage(nested(trend,'discovery_score.score',confidence.trend),breakthrough.is_breakthrough)),
    line('Why now',nested(trend,'timing_rationale',nested(trend,'why_now','Timing evidence not produced'))),
    line('Thesis',thesis.thesis_statement||u.summary),
    line('Confidence',scoreText(confidence.thesis||confidence.trend)),
    '<b>Supporting signals:</b>'+listItems(nested(trend,'supporting_signals',nested(trend,'discovered_trends',[])),'No supporting signals exported yet.'),
  ].join('');
  const pOpt=portfolio.portfolio_optimization||portfolio;
  if(el('portfolioBadge')) el('portfolioBadge').textContent=pOpt.portfolio_path?'produced':'not produced';
  if(el('portfolioBox')) el('portfolioBox').innerHTML=pOpt.portfolio_path?[
    line('Portfolio thesis',pOpt.portfolio_thesis||thesis.thesis_statement),
    line('Portfolio logic',pOpt.portfolio_logic||pOpt.portfolio_path),
    line('Recommended action',(u.next_actions||[])[0]?.action),
    line('Confidence',scoreText(confidence.portfolio||portfolio.portfolio_score)),
    '<b>Priority ranking:</b>'+listItems(pOpt.priority_ranking||nested(portfolio,'opportunity_map.opportunities',[]),'No ranked opportunities exported.'),
    '<b>Risk / exposure notes:</b>'+listItems(pOpt.risk_notes||portfolio.exposure_notes||pOpt.constraints,'No risk or exposure notes exported.'),
  ].join(''):'No portfolio action produced yet.\nReason: insufficient trend confidence, missing signals, or route selected elsewhere.';
  if(el('breakthroughBadge')) el('breakthroughBadge').textContent=breakthrough.is_breakthrough?'detected':'not detected';
  if(el('breakthroughBox')) el('breakthroughBox').innerHTML=[
    line('Breakthrough detected',breakthrough.is_breakthrough?'yes':'no'),
    line('Primary type',breakthrough.primary_type),
    line('Secondary types',(breakthrough.secondary_types||[]).join(', ')||'none'),
    line('Rationale',breakthrough.classification_rationale),
    line('Route recommendation',breakthrough.route_recommendation),
    '<b>Trigger signals:</b>'+listItems(breakthrough.trigger_signals,'No breakthrough trigger signals exported.'),
  ].join('');
  if(el('advancementBadge')) el('advancementBadge').textContent=fmt(advancement.route_selected||core.route_selected,'pending');
  if(el('advancementBox')) el('advancementBox').innerHTML=[
    line('Advancement path selected',routeLabel(advancement.route_selected||core.route_selected)),
    line('Reason selected',advancement.downstream_action||discovery.scan_terminal_reason),
    line('Design required',designPortal.required?'yes':'no'),
    line('Downstream output expected',solution.applicable||designPortal.required?'solution/design output':'portfolio, acquisition, or trend package output'),
    '<b>Stages required:</b>'+listItems(required,'No required stages loaded.'),
    '<b>Stages skipped by route:</b>'+listItems(skipped,'No route skips reported.'),
  ].join('');
  if(el('autodesignBadge')) el('autodesignBadge').textContent=autodesign.status||'not required';
  if(el('autodesignBox')){
    el('autodesignBox').innerHTML=autodesign.triggered?[
      line('Triggered',autodesign.triggered?'yes':'no'),
      line('Trigger source',autodesign.trigger_source),
      line('Advancement path',autodesign.selected_advancement_path||core.route_selected),
      line('Design type',autodesign.design_type),
      line('Concept',autodesign.concept),
      '<b>Core components:</b>'+listItems(autodesign.components,'No components exported.'),
      '<b>Dependencies:</b>'+listItems(autodesign.dependencies,'No dependencies exported.'),
      '<b>Constraints:</b>'+listItems(autodesign.constraints,'No constraints exported.'),
      '<b>Risks:</b>'+listItems(autodesign.risks,'No risks exported.'),
      line('Next design action',designPortal.required?'review design portal output':'no design action required'),
    ].join(''):(autodesign.status==='blocked'?'AutoDesign blocked: insufficient breakthrough / solution data.':autodesign.status==='insufficient_data'?'AutoDesign unavailable: missing design output.':'AutoDesign skipped by route.');
  }
  if(el('designPortalBadge')) el('designPortalBadge').textContent=designPortal.status||'not required';
  if(el('designPortalBox')){
    el('designPortalBox').innerHTML=designPortal.required||designPortal.available?[
      line('Output available',designPortal.available?'yes':'no'),
      line('Blueprint/spec summary',designPortal.blueprint_summary),
      line('Architecture summary',designPortal.architecture_summary),
      '<b>Component map:</b>'+listItems(designPortal.component_map,'No component map exported.'),
      '<b>Dependency map:</b>'+listItems(designPortal.dependency_map,'No dependency map exported.'),
      '<b>Implementation phases:</b>'+listItems(designPortal.build_phases,'No implementation phases exported.'),
      line('Validation status',designPortal.validation_status),
      line('Export/package link',designPortal.export_path||nested(finalPackage,'export_writer.output_dir')),
    ].join(''):(designPortal.status==='blocked'?'Design output blocked by failed buildability / viability / deployability check.':'Design Portal not required for this route.');
  }
  if(el('technologySurfaceBadge')) el('technologySurfaceBadge').textContent=technology.status||'skipped';
  if(el('technologySurfaceBox')) el('technologySurfaceBox').innerHTML=technology.required?[
    line('Required',technology.required?'yes':'no'),
    line('Status',technology.status),
    line('Integration complexity',technology.integration_complexity),
    line('Confidence',scoreText(technology.confidence)),
    sectionHtml('Technologies considered',listItems(technology.technologies_considered,'Technology Intelligence missing.')),
    sectionHtml('Selected stack',technology.selected_stack&&Object.keys(technology.selected_stack).length?`<pre>${esc(JSON.stringify(technology.selected_stack,null,2))}</pre>`:'<div class="muted">No selected stack exported.</div>'),
    sectionHtml('Component matches',listItems(technology.component_matches,'No component matches exported.')),
    sectionHtml('Compatibility notes',listItems(technology.compatibility_notes,'No compatibility notes exported.')),
    sectionHtml('Dependency notes',listItems(technology.dependency_notes,'No dependency notes exported.')),
    sectionHtml('Buildability notes',listItems(technology.buildability_notes,'No buildability notes exported.')),
  ].join(''):'Technology Intelligence skipped by route.';
  if(el('packageBadge')) el('packageBadge').textContent=finalPackage.status||((r.export_writer||{}).status?'available':'missing');
  if(el('packageBox')) el('packageBox').innerHTML=[
    line('Core output available',core.run_id?'yes':'no'),
    line('Package available',finalPackage.status||'unknown'),
    line('Export path',nested(finalPackage,'export_writer.output_dir',nested(r,'export_writer.output_dir'))),
    line('Last generated package',nested(finalPackage,'package_profile.category_name',u.headline)),
  ].join('');
  const failures=core.failures||[];
  if(el('failureBadge')) el('failureBadge').textContent=failures.length||['blocked','failed','insufficient_data'].includes(core.status)?fmt(core.status):'clear';
  if(el('failureBox')) el('failureBox').innerHTML=(failures.length||['blocked','failed','insufficient_data'].includes(core.status))?[
    line('Status',core.status),
    line('Stage where stopped',nested(failures,'0.stage','not specified')),
    line('Reason',nested(failures,'0.type',discovery.scan_terminal_reason)),
    '<b>Missing data:</b>'+listItems(nested(failures,'0.missing_data',[]),'Missing data was not specified.'),
    '<b>Next scan action:</b>'+listItems(core.next_actions||u.next_actions,'No next action exported.'),
  ].join(''):'No blocking failure reported.';
  renderFunctionalSurfaces(core,r);
}
function renderFunctionalSurfaces(core={},r={}){
  const u=core.user_facing_result||core||{};
  const confidence=core.confidence||u.confidence||{};
  const trend=core.trend_discovery||u.trend||{};
  const thesis=core.thesis||u.thesis||{};
  const discovery=core.discovery||u.discovery||{};
  const portfolio=core.portfolio||u.portfolio||{};
  const breakthrough=core.breakthrough||u.breakthrough||{};
  const advancement=core.advancement_path||u.advancement_path||{};
  const autodesign=core.autodesign||u.autodesign||{};
  const designPortal=core.design_portal||u.design_portal||{};
  const technology=core.technology_intelligence||u.technology_intelligence||{};
  const acquisition=core.acquisition||u.acquisition||{};
  const finalPackage=core.final_package||u.final_package||{};
  const stages=nested(core,'lifecycle_summary.stages',[]);
  const skipped=(stages||[]).filter(s=>s.status==='skipped_by_route').map(s=>`${s.number}. ${s.name}`);
  const required=(stages||[]).filter(s=>['complete','failed','blocked','insufficient_data'].includes(s.status)).slice(0,10).map(s=>`${s.number}. ${s.name} (${s.status})`);
  const scan=core.scan_iterations||[];
  const failures=core.failures||[];
  const reviewRequired=failures.length||['blocked','failed','insufficient_data','incomplete'].includes(core.status);
  if(el('runAutonomyBox')){
    el('runAutonomyBox').textContent=[
      `Current route: ${fmt(core.route_selected||u.route_selected,'waiting for run')}`,
      `Status: ${fmt(core.status,'waiting')}`,
      `Terminal state: ${fmt(discovery.scan_terminal_state||nested(signalBasis,'source_summary.scan_terminal_state'),'waiting')}`,
      `Scan iterations: ${fmt(scan.length,0)}`,
      `Review required: ${reviewRequired?'yes':'no'}`,
      `Autonomous execution: ${scan.length?'scan continuation ran until terminal state or guard':'waiting for scan result'}`
    ].join('\n');
  }
  setText('commandRouteBadge',routeLabel(core.route_selected||u.route_selected||'ready'));
  setText('discoverSurfaceBadge',discovery.scan_terminal_state||core.route_selected||'waiting');
  setHtml('discoverSurfaceBox',[
    `<h3>${esc(discovery.scan_terminal_state||'Discovery status pending')}</h3>`,
    line('Discoveries generated',nested(discovery,'opportunity_discovery.opportunity_count',nested(discovery,'opportunity_discovery.opportunity_score.level','not produced'))),
    line('Gap qualification',nested(core,'signal_basis.source_summary.scan_terminal_reason',discovery.scan_terminal_reason)),
    line('Why discovery reached / not reached',discovery.scan_terminal_reason||'Waiting for scan result.'),
    line('Discovery confidence',scoreText(discovery.confidence||confidence.overall)),
    line('Next action',(core.next_actions||u.next_actions||[])[0]?.action),
    sectionHtml('Failure or missing data',listItems((core.failures||[]).map(f=>`${f.stage||f.type}: ${(f.missing_data||[]).join(', ')}`),'No discovery failure reported.')),
  ].join(''));
  const governed=nested(signalBasis,'source_summary.accepted_signal_count',nested(signalBasis,'governed_signals.accepted_signal_count'));
  setText('signalBasisSurfaceBadge',governed!==undefined&&governed!==null?`${governed} governed`:'waiting');
  setHtml('signalBasisSurfaceBox',[
    line('Governed signal count',governed),
    line('Source count',nested(signalBasis,'source_summary.source_count')),
    line('Connector sources present',nested(signalBasis,'source_summary.connector_sources_present')),
    line('Terminal state',nested(signalBasis,'source_summary.scan_terminal_state')),
    sectionHtml('Signal basis',signalBasis&&Object.keys(signalBasis).length?`<pre>${esc(JSON.stringify(signalBasis,null,2))}</pre>`:'<div class="muted">No signal basis exported.</div>'),
  ].join(''));
  setText('trendSurfaceBadge',trendStage(confidence.trend,breakthrough.is_breakthrough));
  setHtml('trendSurfaceBox',[
    `<h3>${esc(nested(trend,'discovered_trends.0.name','Trend not discovered yet'))}</h3>`,
    line('Stage',trendStage(nested(trend,'discovery_score.score',confidence.trend),breakthrough.is_breakthrough)),
    line('Why now',nested(trend,'why_now',nested(trend,'timing_rationale','Waiting for trend evidence.'))),
    line('Momentum',nested(trend,'momentum',nested(core,'signal_basis.source_summary.accepted_signal_count','not produced'))),
    line('Trend confidence',scoreText(confidence.trend)),
    line('Thesis created',thesis.thesis_statement||'No thesis formed yet.'),
    sectionHtml('Supporting signals',listItems(nested(trend,'supporting_signals',nested(trend,'discovered_trends',[])),'No supporting signals exported yet.')),
    sectionHtml('Affected sectors/entities/themes',listItems(nested(trend,'affected_sectors',core.keywords||[]),'No affected themes exported yet.')),
    line('Next action',(core.next_actions||u.next_actions||[])[0]?.action),
  ].join(''));
  setText('scanSurfaceBadge',scan.length?`${scan.length} iteration(s)`:fmt(discovery.scan_terminal_state,'waiting'));
  setHtml('scanSurfaceBox',scan.length?scan.map(it=>[
    `<h4>Scan iteration ${esc(it.iteration)}</h4>`,
    line('Signals found',it.signals_found),
    line('Governed signal count',it.governed_signal_count),
    line('Trend confidence',scoreText(it.trend_confidence)),
    line('Discovery confidence',scoreText(it.discovery_confidence)),
    line('Breakthrough confidence',scoreText(it.breakthrough_confidence)),
    line('Continue/enrich status',it.route_decision==='continue_scan'?'continue/enrich':it.route_decision),
    line('Stop reason',it.terminal_reason),
  ].join('')).join('<hr>'):'No scan iterations loaded. Waiting for run, scan in progress, or core_run_output.json missing.');
  const pOpt=portfolio.portfolio_optimization||portfolio;
  setText('portfolioSurfaceBadge',pOpt.portfolio_path?'produced':'not produced');
  setHtml('portfolioSurfaceBox',pOpt.portfolio_path?[
    `<h3>${esc(pOpt.portfolio_path||'Portfolio action')}</h3>`,
    line('Portfolio thesis',pOpt.portfolio_thesis||thesis.thesis_statement),
    line('Portfolio logic',pOpt.portfolio_logic||pOpt.allocation_hypothesis||pOpt.portfolio_path),
    sectionHtml('Included themes/entities/opportunities',listItems(pOpt.included_themes||nested(portfolio,'opportunity_map.opportunities',[]),'No included opportunities exported.')),
    sectionHtml('Priority ranking',listItems(pOpt.priority_ranking||nested(portfolio,'opportunity_map.opportunities',[]),'No priority ranking exported.')),
    line('Suggested portfolio action',(core.next_actions||u.next_actions||[])[0]?.action),
    line('Confidence',scoreText(confidence.portfolio||portfolio.portfolio_score)),
  ].join(''):'Portfolio not produced for this route.\nReason: insufficient trend confidence, missing signals, waiting for portfolio engine, or route selected elsewhere.');
  setText('portfolioRiskBadge',pOpt.portfolio_path?'available':'not produced');
  setHtml('portfolioRiskBox',[sectionHtml('Exposure notes',listItems(portfolio.exposure_notes||pOpt.exposure_notes,'No exposure notes exported.')),sectionHtml('Risk notes',listItems(pOpt.risk_notes||pOpt.constraints,'No risk notes exported.'))].join(''));
  setText('breakthroughSurfaceBadge',breakthrough.is_breakthrough?'detected':'not detected');
  setHtml('breakthroughSurfaceBox',[
    `<h3>${esc(breakthrough.is_breakthrough?'Breakthrough detected':'Breakthrough not triggered')}</h3>`,
    line('Primary type',breakthrough.primary_type),
    line('Secondary types',(breakthrough.secondary_types||[]).join(', ')||'none'),
    line('Classification rationale',breakthrough.classification_rationale),
    line('Why triggered / not triggered',breakthrough.is_breakthrough?breakthrough.classification_rationale:'Breakthrough threshold was not met or selected route does not require escalation.'),
    line('Route recommendation',breakthrough.route_recommendation),
    sectionHtml('Trigger signals',listItems(breakthrough.trigger_signals,'No trigger signals exported.')),
  ].join(''));
  setText('advancementSurfaceBadge',routeLabel(advancement.route_selected||core.route_selected||'pending'));
  setHtml('advancementSurfaceBox',[
    line('Advancement path selected',routeLabel(advancement.route_selected||core.route_selected)),
    line('Reason selected',advancement.downstream_action||discovery.scan_terminal_reason),
    line('Downstream output expected',designPortal.required?'design/package':'portfolio, acquisition, trend, or insufficient-data output'),
    line('Why invention/design triggered',designPortal.required?'Design route requires construction output.':'AutoDesign skipped by route; Design Portal not required.'),
    sectionHtml('Stages required',listItems(required,'No required stages loaded.')),
    sectionHtml('Stages skipped_by_route',listItems(skipped,'No skipped stages reported.')),
  ].join(''));
  setText('designSurfaceBadge',designPortal.required?'design route':'not required');
  setText('autodesignSurfaceBadge',autodesign.status||'not required');
  setHtml('autodesignSurfaceBox',autodesign.triggered?[
    line('Triggered',autodesign.triggered?'yes':'no'),
    line('Trigger source',autodesign.trigger_source),
    line('Design type',autodesign.design_type),
    line('System type',autodesign.system_type||autodesign.design_type),
    line('Generated concept',autodesign.concept),
    line('Intended function',autodesign.intended_function||'Minimum viable design function exported when available.'),
    sectionHtml('Components',listItems(autodesign.components,'No components exported.')),
    sectionHtml('Dependencies',listItems(autodesign.dependencies,'No dependencies exported.')),
    sectionHtml('Constraints',listItems(autodesign.constraints,'No constraints exported.')),
    sectionHtml('Risks',listItems(autodesign.risks,'No risks exported.')),
    sectionHtml('Selected technologies',listItems(autodesign.selected_technologies,'No selected technologies exported.')),
    line('Selected stack',autodesign.selected_stack&&Object.keys(autodesign.selected_stack).length?JSON.stringify(autodesign.selected_stack):'No stack selected.'),
    line('Next design action',designPortal.required?'Review Design Portal output and validation gates.':'No design action required.'),
  ].join(''):`AutoDesign skipped by route.\nReason: ${esc(autodesign.status||'not_required')}`);
  setText('designPortalSurfaceBadge',designPortal.status||'not required');
  setHtml('designPortalSurfaceBox',designPortal.required||designPortal.available?[
    line('Design output available',designPortal.available?'yes':'no'),
    line('Architecture summary',designPortal.architecture_summary),
    line('Blueprint/spec summary',designPortal.blueprint_summary),
    sectionHtml('Component map',listItems(designPortal.component_map,'No component map exported.')),
    sectionHtml('Dependency map',listItems(designPortal.dependency_map,'No dependency map exported.')),
    line('Technology stack',designPortal.technology_stack&&Object.keys(designPortal.technology_stack).length?JSON.stringify(designPortal.technology_stack):'No technology stack exported.'),
    sectionHtml('Implementation phases',listItems(designPortal.build_phases,'No implementation phases exported.')),
    line('Build plan summary',designPortal.blueprint_summary||'Build plan summary not produced.'),
    line('Validation status',designPortal.validation_status),
    line('Export/package link',designPortal.export_path||nested(finalPackage,'export_writer.output_dir')),
  ].join(''):'Design Portal not required for this route.');
  setText('technologySurfaceBadge',technology.status||'skipped');
  setHtml('technologySurfaceBox',technology.required?[
    line('Required',technology.required?'yes':'no'),
    line('Status',technology.status),
    line('Integration complexity',technology.integration_complexity),
    line('Confidence',scoreText(technology.confidence)),
    sectionHtml('Technologies considered',listItems(technology.technologies_considered,'Technology Intelligence missing.')),
    line('Selected stack',technology.selected_stack&&Object.keys(technology.selected_stack).length?JSON.stringify(technology.selected_stack):'No selected stack exported.'),
    sectionHtml('Component matches',listItems(technology.component_matches,'No component matches exported.')),
    sectionHtml('Compatibility notes',listItems(technology.compatibility_notes,'No compatibility notes exported.')),
    sectionHtml('Dependency notes',listItems(technology.dependency_notes,'No dependency notes exported.')),
    sectionHtml('Buildability notes',listItems(technology.buildability_notes,'No buildability notes exported.')),
  ].join(''):'Technology Intelligence skipped by route.');
  setText('packageSurfaceBadge',finalPackage.status||'package status');
  setHtml('packageSurfaceBox',[
    `<h3>${esc(u.headline||'Package output')}</h3>`,
    line('Package available',finalPackage.status||'unknown'),
    line('Opportunity summary',u.summary),
    line('Market position',nested(core,'strategy.strategic_positioning.positioning_statement','not produced')),
    line('Moat / differentiation',nested(core,'strategy.moat.moat_type.type','not produced')),
    line('Business model / value capture',nested(core,'strategy.business_model.value_capture.model','not produced')),
    line('Acquirer targets',(acquisition.acquirer_matches||[]).length),
    line('Acquisition readiness',nested(finalPackage,'export_readiness.level','not produced')),
    line('Export path',nested(finalPackage,'export_writer.output_dir',nested(r,'export_writer.output_dir'))),
    sectionHtml('Risks / objections',listItems(nested(core,'strategy.risk_regulation.risks',[]),'No package risks exported.')),
  ].join(''));
  setText('historySurfaceBadge',state.runs.length?`${state.runs.length} run(s)`:'empty');
  setHtml('historySurfaceBox',state.runs.length?state.runs.slice(0,8).map(run=>`<div><b>${esc(title(run))}</b><br>${esc(fmt(run.created_at))} | ${esc(fmt(run.route_selected||run.decision_classification))} | ${esc(fmt(run.confidence||run.portfolio_score))}</div>`).join('<hr>'):'No runs found.');
  setText('monitorRunBadge',core.status||'waiting');
  setHtml('monitorRunBox',[
    line('Active scans',scan.length?`${scan.length} iteration(s) in selected run`:'No active scan selected.'),
    line('Current scan pass',scan.length?scan[scan.length-1].iteration:'waiting'),
    line('Last run status',core.status||r.status),
    line('Last export status',nested(finalPackage,'export_writer.status',nested(r,'export_writer.status'))),
    line('Terminal state',discovery.scan_terminal_state||nested(signalBasis,'source_summary.scan_terminal_state')),
    sectionHtml('Scan iteration progress',scan.length?scan.map(it=>`<div>Iteration ${esc(it.iteration)}: ${esc(it.route_decision)} | trend ${esc(scoreText(it.trend_confidence))} | discovery ${esc(scoreText(it.discovery_confidence))} | breakthrough ${esc(scoreText(it.breakthrough_confidence))}</div>`).join(''):'<div class="muted">No scan iteration progress loaded.</div>'),
  ].join(''));
  setText('monitorActivityBadge',state.runs.length?'history ready':'idle');
  setHtml('monitorActivityBox',[
    line('Run history',`${state.runs.length} run(s)`),
    line('Selected run',r.run_id||core.run_id),
    line('Last export path',nested(finalPackage,'export_writer.output_dir',nested(r,'export_writer.output_dir'))),
    line('Known errors',failures.length?`${failures.length} issue(s)`:'none in selected core output'),
  ].join(''));
}
function renderUserFacingResult(data,r={}){
  const empty=el('userResultEmpty'), stateNode=el('userResultState');
  if(!data){
    if(empty) empty.classList.remove('hidden');
    if(stateNode) stateNode.classList.add('hidden');
    if(el('resultRouteBadge')) el('resultRouteBadge').textContent='route pending';
    renderCorePanels({},r);
    return;
  }
  const out=userFacingResult(data,r);
  const missing=requiredResultSections().filter(k=>!(k in out));
  if(missing.length&&data&&data.core_output){
    return renderCoreOutputIncomplete(data.core_output,r);
  }
  if(empty) empty.classList.add('hidden');
  if(stateNode) stateNode.classList.remove('hidden');
  if(el('resultRouteBadge')) el('resultRouteBadge').textContent=routeLabel(out.route_selected);
  if(el('userResultHeadline')) el('userResultHeadline').textContent=fmt(out.headline,'Intelligence output ready');
  if(el('userResultSummary')) el('userResultSummary').textContent=fmt(out.summary,'Claire produced a route-aware intelligence result.');
  const activeRoute=String(out.route_selected||'');
  const path=[
    ['Trend','trend_thesis'],
    ['Portfolio','portfolio_creation_optimization'],
    ['Breakthrough','breakthrough_escalation'],
    ['Design','solution_design'],
    ['Acquisition','acquisition_package'],
    ['Package','complete']
  ];
  if(el('resultPathRail')){
    el('resultPathRail').innerHTML=path.map(([label,key])=>`<div class="pathStep ${activeRoute.includes(key)||activeRoute===key?'active':''}"><strong>${esc(label)}</strong><span>${esc(key.replace(/_/g,' '))}</span></div>`).join('');
  }
  const trend=out.trend||{}, thesis=out.thesis||{}, discovery=out.discovery||{}, portfolio=(out.portfolio||{}).portfolio_optimization||out.portfolio||{}, breakthrough=out.breakthrough||{};
  const acquisition=out.acquisition||{}, finalPackage=out.final_package||{}, confidence=out.confidence||{};
  const cards=[
    ['Trend Detected', resultMetric('Score',nested(trend,'discovery_score.score',confidence.trend), nested(trend,'discovered_trends.0.name','Trend evidence available'))],
    ['Thesis', resultMetric('Score',nested(thesis,'thesis_score.score',confidence.thesis), thesis.thesis_statement||out.summary)],
    ['Discovery Result', resultMetric('Confidence',discovery.confidence||confidence.overall, discovery.scan_terminal_reason||nested(discovery,'opportunity_discovery.opportunity_type','Discovery evidence available'))],
    ['Portfolio Output', resultMetric('Score',nested(portfolio,'portfolio_optimization_score.score',confidence.portfolio), portfolio.portfolio_path||'Portfolio path not selected')],
    ['Breakthrough Result', resultMetric('Score',breakthrough.score||confidence.breakthrough, breakthrough.classification_rationale||breakthrough.route_recommendation||'Breakthrough not selected as primary route')],
    ['Acquisition Layer', resultMetric('Score',nested(acquisition,'scores.acquisition_score',confidence.acquisition), `${fmt((acquisition.acquirer_matches||[]).length,0)} acquirer match(es)`)],
    ['Final Package', resultMetric('Confidence',confidence.overall, nested(finalPackage,'export_readiness.level','Package readiness available'))]
  ];
  if(el('resultInsightGrid')){
    el('resultInsightGrid').innerHTML=cards.map(([title,body])=>`<article class="resultInsight"><h3>${esc(title)}</h3>${body}</article>`).join('');
  }
  const actions=out.next_actions||[];
  if(el('nextActionList')){
    el('nextActionList').innerHTML=actions.length?actions.map(a=>`<div class="nextAction"><strong>${esc(a.action||'review output')}</strong><div>${esc(a.purpose||'Review the route-aware result.')}</div><div class="muted">${esc(a.priority||'medium')}</div></div>`).join(''):'<div class="muted">No next action exported.</div>';
  }
  renderCorePanels(data.core_output||data,r);
}
function renderSystemLayer(data,r={}){
  const core=data&&data.core_output||{};
  const lifecycle=data&&data.core_lifecycle||{};
  const gate=core.lifecycle_summary&&core.lifecycle_summary.completion_gate || data&&data.core_completion_gate || {};
  if(el('systemLifecycleBadge')) el('systemLifecycleBadge').textContent=fmt(gate.status,'no run');
  if(el('systemLifecycleSummary')){
    el('systemLifecycleSummary').textContent=data?`Route: ${fmt(lifecycle.route||core.route_selected)}\nStages: ${fmt(lifecycle.stage_count||nested(core,'lifecycle_summary.stage_count'))}\nGate: ${fmt(gate.status)}\nInsufficient: ${fmt(gate.insufficient_data_stage_count,0)}\nBlocked: ${fmt(gate.blocking_stage_count,0)}`:'Select or run an evaluation to inspect lifecycle metadata.';
  }
  const stages=(lifecycle.stages||nested(core,'lifecycle_summary.stages',[])||[]);
  if(el('systemLifecycleList')){
    el('systemLifecycleList').innerHTML=stages.length?stages.map(s=>`<div class="systemStage ${esc(s.status)}"><strong>${fmt(s.number)}. ${esc(s.name||s.id)}</strong><div>Status: ${esc(s.status)}</div><div class="muted">${esc((s.missing_outputs||[]).join(', ')||'No missing outputs')}</div></div>`).join(''):'<div class="status">No lifecycle stages loaded.</div>';
  }
  if(el('systemContractBadge')) el('systemContractBadge').textContent=nested(core,'contract_validation.status','pending');
  if(el('systemContractSummary')) el('systemContractSummary').textContent=`Route selected: ${fmt(core.route_selected)}\nStatus: ${fmt(core.status)}\nFailures: ${fmt((core.failures||[]).length,0)}\nEvidence items: ${fmt((core.evidence||[]).length,0)}`;
  if(el('systemCoreOutputBox')) el('systemCoreOutputBox').textContent=data?JSON.stringify(core||{},null,2):'No core output loaded.';
  if(el('systemRawOutputBox')){el('systemRawOutputBox').classList.add('hidden');el('systemRawOutputBox').textContent='Full raw JSON loads on demand.'}
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
async function loadFullRunJsonOnDemand(run=null){
  const selected=run||state.selected;
  const runId=selected&&(selected.run_id||selected.folder_name);
  if(!runId) return null;
  if(el('rawBox')) el('rawBox').textContent='Loading full raw JSON...';
  if(el('systemRawOutputBox')){el('systemRawOutputBox').classList.remove('hidden');el('systemRawOutputBox').textContent='Loading full raw JSON...'}
  for(const name of ['full_pipeline_output.json','pipeline_output.json']){
    try{
      const x=await api(`/api/runs/${encodeURIComponent(runId)}/files/${encodeURIComponent(name)}?max_chars=5000000`);
      if(x&&x.status==='success'&&x.content){
        const parsed=JSON.parse(x.content);
        if(el('rawBox')) el('rawBox').textContent=JSON.stringify(parsed,null,2);
        if(el('systemRawOutputBox')) el('systemRawOutputBox').textContent=JSON.stringify(parsed,null,2);
        return parsed;
      }
    }catch(e){
      if(el('rawBox')) el('rawBox').textContent=`Full raw JSON unavailable: ${e.message}`;
      if(el('systemRawOutputBox')) el('systemRawOutputBox').textContent=`Full raw JSON unavailable: ${e.message}`;
    }
  }
  if(el('rawBox')) el('rawBox').textContent='Full raw JSON not available for this run.';
  if(el('systemRawOutputBox')) el('systemRawOutputBox').textContent='Full raw JSON not available for this run.';
  return null;
}
async function loadCoreRunOutput(r){
  const runId=r&&(r.run_id||r.folder_name);
  if(!runId) return {status:'missing',error:'No run id provided.'};
  try{
    const x=await api(`/api/runs/${encodeURIComponent(runId)}/files/${encodeURIComponent('core_run_output.json')}?max_chars=1200000`);
    if(x&&x.status==='success'&&x.content) return {status:'success',core_output:JSON.parse(x.content)};
  }catch(e){
    return {status:'missing',error:e.message};
  }
  return {status:'missing',error:'core_run_output.json is missing or empty.'};
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
  renderUserFacingResult(null,r);
  renderSystemLayer(null,r);
  el('rawBox').textContent='Raw JSON loads on demand from Raw Output / Debug.';
  const core=await loadCoreRunOutput(r);
  if(state.selected&&state.selected.run_id===r.run_id){
    if(core&&core.status==='success'){
      state.selected.core_output=core.core_output||{};
      renderDecision(r,core);
      renderPipeline(core,r);
      renderUserFacingResult(core,r);
      renderSystemLayer(core,r);
    }else{
      renderCoreOutputUnavailable(core&&core.error?`Core output not available for this run. ${core.error}`:'Core output not available for this run.');
      renderPipeline(null,r);
      renderSystemLayer(null,r);
    }
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
    const scanIterations=x.scan_iterations||[];
    const pipelineRun=x.core_pipeline_run||{};
    el('liveIntelligenceBadge').textContent=fmt(x.terminal_state||(x.live_opportunities_ready?'opportunities ready':x.status));
    el('liveIntelligenceStatusBox').textContent=`Status: ${fmt(x.status)}\nTerminal State: ${fmt(x.terminal_state)}\nTerminal Reason: ${fmt(x.terminal_reason)}\nScan Iterations: ${fmt(scanIterations.length,0)}\nConnector Records: ${fmt((x.connectors||{}).record_count,0)}\nExtracted Signals: ${fmt((x.extracted||{}).signal_count,0)}\nTrend Clusters: ${fmt((x.clusters||{}).cluster_count,0)}\nGaps: ${fmt((x.gaps||{}).gap_count,0)}\nSolutions: ${fmt(solutions.length,0)}\nRunnable Cards: ${fmt(activated.length,0)}`;
    setLayer('Live',fmt(x.terminal_state||(x.live_opportunities_ready?'opportunities ready':x.status)),`${fmt(scanIterations.length,0)} scan iteration(s), ${fmt((x.extracted||{}).signal_count,0)} signals, ${fmt((x.clusters||{}).cluster_count,0)} clusters, ${fmt((x.gaps||{}).gap_count,0)} gaps, ${fmt(activated.length,0)} runnable cards.`);
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
    if(pipelineRun.run_id||pipelineRun.folder_name){
      await loadRuns(pipelineRun.run_id||pipelineRun.folder_name);
    }
    stat('launchStatus',`Live monitor reached ${fmt(x.terminal_state,'scan result')} after ${scanIterations.length||1} iteration(s) and produced ${solutions.length} solution candidate(s).`);
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
function researchCardHtml(result,index){
  return `<div class="researchCard"><strong>${esc(result.title)}</strong><p>${esc(result.summary||'No summary available.')}</p><div class="researchMeta"><span>Source<b>${esc(result.source_type)}</b></span><span>Relevance<b>${esc(scoreText(result.relevance))}</b></span><span>Credibility<b>${esc(scoreText(result.source_credibility))}</b></span><span>Freshness<b>${esc(scoreText(result.freshness))}</b></span><span>Route<b>${esc(routeLabel(result.related_lifecycle_route))}</b></span><span>Entities<b>${esc((result.extracted_entities||[]).length)}</b></span></div><div class="muted">${esc(result.url||result.internal_path||'No openable source path')}</div><div class="researchActions"><button data-research-action="open" data-index="${index}">Open</button><button data-research-action="save" data-index="${index}">Save Evidence</button><button data-research-action="scan" data-index="${index}">Send Scan</button><button data-research-action="trend" data-index="${index}">Trend</button><button data-research-action="portfolio" data-index="${index}">Portfolio</button><button data-research-action="breakthrough" data-index="${index}">Breakthrough</button><button data-research-action="design" data-index="${index}">AutoDesign</button><button data-research-action="package" data-index="${index}">Package</button></div></div>`;
}
function bindResearchActions(){
  document.querySelectorAll('[data-research-action]').forEach(btn=>{
    btn.onclick=async()=>{
      const result=state.researchResults[Number(btn.dataset.index)];
      if(!result) return;
      const action=btn.dataset.researchAction;
      if(action==='open'){
        const target=result.url||result.internal_path;
        if(target) window.open(target,'_blank');
        return;
      }
      if(action==='save'){
        await api('/api/research/evidence/add',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({result})});
        await loadEvidenceBasket();
        stat('researchStatusBox','Result saved to evidence basket.');
        return;
      }
      const route={scan:'scan',trend:'trend_discovery',portfolio:'portfolio_review',breakthrough:'breakthrough_review',design:'autodesign',package:'package'}[action]||'scan';
      const x=await api('/api/research/send-to-pipeline',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({result,route})});
      stat('researchStatusBox',`Sent to pipeline marker: ${fmt(x.route)}. This is ready as governed signal input.`);
    };
  });
}
async function runResearchSearch(){
  const query=(el('researchQueryInput')&&el('researchQueryInput').value||'').trim();
  const scope=el('researchScopeSelect')?el('researchScopeSelect').value:'all';
  if(!query){stat('researchStatusBox','Enter a research command first.',true);return}
  setText('researchStatusBadge','searching');
  try{
    const x=await api('/api/research/search',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({query,scope,limit:24})});
    state.researchResults=x.results||[];
    setText('researchResultCount',String(state.researchResults.length));
    setText('researchStatusBadge',x.status||'success');
    const unavailable=(x.unavailable_sources||[]).map(u=>u.reason).join(' ');
    stat('researchStatusBox',`${state.researchResults.length} result(s). ${unavailable||'Internal research sources searched.'}`);
    setHtml('researchResultList',state.researchResults.length?state.researchResults.map(researchCardHtml).join(''):'<div class="status">No results found.</div>');
    bindResearchActions();
    await loadEvidenceBasket();
  }catch(e){
    stat('researchStatusBox','Research search failed: '+e.message,true);
  }
}
async function loadEvidenceBasket(){
  try{
    const x=await api('/api/research/evidence');
    const items=x.items||[];
    setText('evidenceBasketBadge',`${items.length} saved`);
    setHtml('evidenceBasketList',items.length?items.map(item=>`<div class="researchCard"><strong>${esc(item.title)}</strong><p>${esc(item.summary)}</p><div class="muted">${esc(item.source_type)} | credibility ${esc(scoreText(item.credibility))}</div></div>`).join(''):'<div class="status">No saved evidence.</div>');
  }catch(e){
    setHtml('evidenceBasketList','<div class="status">Evidence basket unavailable.</div>');
  }
}
async function clearEvidenceBasket(){
  await api('/api/research/evidence/clear',{method:'POST'});
  await loadEvidenceBasket();
  stat('researchStatusBox','Evidence basket cleared.');
}
async function basketToPipeline(){
  const x=await api('/api/research/evidence/pipeline-input',{method:'POST'});
  setText('basketPipelineBox',`Evidence basket ready for pipeline.\nEvidence count: ${fmt(x.evidence_count,0)}\nGoverned signal candidates: ${fmt((x.governed_signal_candidates||[]).length,0)}`);
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
    loadEvidenceBasket();
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
  bind('loadRawOutputBtn',()=>loadFullRunJsonOnDemand());
  bind('researchSearchBtn',runResearchSearch);
  bind('researchClearBtn',clearEvidenceBasket);
  bind('basketPipelineBtn',basketToPipeline);
  loadEvidenceBasket();
  document.querySelectorAll('.tab').forEach(b=>b.onclick=()=>tab(b.dataset.tab));
  ['marketUniverseSelect','industryDomainSelect','buyerSegmentSelect','objectiveSelect'].forEach(id=>{
    const node=el(id);
    if(node) node.addEventListener('change',initDiscoverPipeline);
  });
  const modeSel=el('executionModeSelect');
  if(modeSel) modeSel.addEventListener('change',loadModeStatus);
});
