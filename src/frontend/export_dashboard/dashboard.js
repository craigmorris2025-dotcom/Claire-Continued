const state={runs:[],selectedRun:null,files:[]};
const el=id=>document.getElementById(id);
function setStatus(msg,err=false){el('statusBox').textContent=msg;el('statusBox').style.color=err?'#f85149':'#8b949e'}
async function api(path,opt={}){const r=await fetch(path,opt);if(!r.ok)throw new Error(await r.text());const ct=r.headers.get('content-type')||'';return ct.includes('json')?r.json():r.text()}
const fmt=(v,f='—')=>(v===undefined||v===null||v==='')?f:String(v);
function runTitle(r){return r.category_name||r.sector||r.folder_name||r.run_id||'Claire run'}
function renderRuns(){const list=el('runList');list.innerHTML='';el('runCount').textContent=state.runs.length;
 if(!state.runs.length){list.innerHTML='<div class="status">No runs found. Run Claire or click Rescan Exports.</div>';return}
 state.runs.forEach(r=>{const d=document.createElement('div');d.className='run-card'+(state.selectedRun&&state.selectedRun.run_id===r.run_id?' active':'');
 d.innerHTML=`<strong>${fmt(runTitle(r))}</strong><div class="meta">${fmt(r.created_at)}<br>Sector: ${fmt(r.sector)}<br>Decision: ${fmt(r.decision_classification)} · Files: ${fmt(r.written_file_count)}</div>`;
 d.onclick=()=>selectRun(r);list.appendChild(d)})}
function cards(r){const c=[['Run ID',r.run_id],['Output Folder',r.output_dir],['Domain',r.domain],['Sector',r.sector],['Category',r.category_name],['Decision',r.decision_classification],['Breakthrough',r.breakthrough_classification],['Portfolio Score',r.portfolio_score],['Export Level',r.export_package_level],['Export Score',r.export_package_score],['Documents',r.document_count],['Written Files',r.written_file_count]];
 el('summaryCards').innerHTML=c.map(([a,b])=>`<div class="card"><h3>${a}</h3><p>${fmt(b)}</p></div>`).join('')}
function renderFiles(files){state.files=files||[];el('filesValue').textContent=state.files.length||'—';el('fileList').innerHTML='';el('fileSelect').innerHTML='';
 if(!state.files.length){el('fileList').innerHTML='<div class="status">No files found.</div>';return}
 state.files.forEach(f=>{const row=document.createElement('div');row.className='file-row';row.innerHTML=`<div><strong>${f.filename}</strong><div class="file-meta">${fmt(f.format)} · ${fmt(f.size_bytes)} bytes</div></div><button>Preview</button><button>Open</button>`;
 row.children[1].onclick=()=>preview(f.filename);row.children[2].onclick=()=>window.open(`/api/runs/${encodeURIComponent(state.selectedRun.run_id)}/files/${encodeURIComponent(f.filename)}?raw=1`,'_blank');el('fileList').appendChild(row);
 const o=document.createElement('option');o.value=f.filename;o.textContent=f.filename;el('fileSelect').appendChild(o)})}
async function selectRun(r){state.selectedRun=r;renderRuns();el('emptyState').classList.add('hidden');el('detailState').classList.remove('hidden');
 el('selectedSector').textContent=fmt(r.sector,'unknown sector');el('selectedTitle').textContent=runTitle(r);el('selectedMeta').textContent=`${fmt(r.run_id)} · ${fmt(r.created_at)}`;el('decisionValue').textContent=fmt(r.decision_classification);el('exportValue').textContent=fmt(r.export_package_level);cards(r);
 try{const x=await api(`/api/runs/${encodeURIComponent(r.run_id)}/files`);renderFiles(x.files||[]);const p=['run_summary.md','portfolio_binder.md','README.md'].find(n=>state.files.some(f=>f.filename===n));if(p)preview(p)}catch(e){renderFiles([]);el('previewBox').textContent=e.message}}
async function preview(name){if(!state.selectedRun||!name)return;el('fileSelect').value=name;el('previewBox').textContent='Loading preview...';
 try{const x=await api(`/api/runs/${encodeURIComponent(state.selectedRun.run_id)}/files/${encodeURIComponent(name)}?max_chars=100000`);el('previewBox').textContent=typeof x==='string'?x:(x.content||JSON.stringify(x,null,2));tab('preview')}catch(e){el('previewBox').textContent=e.message}}
function tab(name){document.querySelectorAll('.tab').forEach(b=>b.classList.toggle('active',b.dataset.tab===name));['summary','files','preview'].forEach(t=>el(t+'Tab').classList.toggle('hidden',t!==name))}
async function load(){setStatus('Loading run history...');try{const r=await api('/api/runs');state.runs=r.runs||[];renderRuns();setStatus(`Loaded ${state.runs.length} run(s).`);if(state.runs.length&&!state.selectedRun)selectRun(state.runs[0])}catch(e){setStatus('Failed: '+e.message,true)}}
async function rescan(){setStatus('Rescanning exports...');try{await api('/api/rescan',{method:'POST'});await load()}catch(e){setStatus('Rescan failed: '+e.message,true)}}
document.addEventListener('DOMContentLoaded',()=>{el('refreshBtn').onclick=load;el('rescanBtn').onclick=rescan;el('loadPreviewBtn').onclick=()=>preview(el('fileSelect').value);document.querySelectorAll('.tab').forEach(b=>b.onclick=()=>tab(b.dataset.tab));load()});
