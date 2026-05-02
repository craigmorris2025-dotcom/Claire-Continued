(function(ns){
  ns.escapeHtml=function(value){
    return String(value===undefined||value===null?'':value).replace(/[&<>"']/g,function(ch){
      return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[ch];
    });
  };
  ns.compactText=function(value,limit){
    const text=String(value===undefined||value===null?'':value).replace(/\s+/g,' ').trim();
    const max=limit||150;
    return text.length>max?text.slice(0,max-1)+'...':text;
  };
  ns.score=function(value){
    const n=Number(value);
    if(!Number.isFinite(n)) return value===undefined||value===null?'-':String(value);
    return n>=0&&n<=1?String(Math.round(n*100))+'%':String(Math.round(n));
  };

  async function safe(api,path,fallback){
    try{return await api(path);}catch(e){return fallback;}
  }
  async function loadContext(api){
    const status=await safe(api,'/api/live-intelligence/status',{status:'unavailable'});
    const latest=await safe(api,'/api/live-intelligence/latest',{});
    const history=await safe(api,'/api/live-intelligence/history',{runs:[]});
    const plan=await safe(api,'/api/live-intelligence/scan-plan',{scan_items:[]});
    return {status,latest,history,plan};
  }
  function render(root,context,selectedIndex){
    const events=ns.buildMonitorEvents?ns.buildMonitorEvents(context):[];
    const selected=events[selectedIndex]||events[0]||{};
    root.innerHTML=[
      '<div class="monitorSurface">',
        ns.MonitorStatusBar(context),
        '<div class="monitorLayout">',
          ns.MonitorTimeline({events:events}),
          ns.MonitorDetailPanel({event:selected,latest:context.latest}),
        '</div>',
      '</div>'
    ].join('');
    root.querySelectorAll('[data-monitor-event]').forEach(function(node){
      node.onclick=function(){render(root,context,Number(node.dataset.monitorEvent)||0);};
      node.onkeydown=function(ev){if(ev.key==='Enter'||ev.key===' '){ev.preventDefault();node.onclick();}};
      node.classList.toggle('active',Number(node.dataset.monitorEvent)===selectedIndex);
    });
  }

  ns.initMonitorSurface=async function(root,options){
    if(!root) return;
    const api=(options&&options.api)||window.api;
    root.innerHTML='<div class="status">Loading Monitor timeline...</div>';
    const context=await loadContext(api);
    render(root,context,0);
  };
})(window.ClaireMonitor=window.ClaireMonitor||{});
