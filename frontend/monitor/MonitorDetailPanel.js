(function(ns){
  function detailRows(detail){
    if(!detail||typeof detail!=='object') return [];
    const keys=['entity_name','ticker','signal_type','urgency','trend_type','trajectory','market_gap','needed_solution','solution_score','gap_score','status','connector_records','signals','clusters','gaps','solutions','live_opportunities_ready'];
    return keys.filter(function(key){return detail[key]!==undefined&&detail[key]!==null&&detail[key]!=='';}).map(function(key){
      return [key.replace(/_/g,' '),Array.isArray(detail[key])?detail[key].join(', '):String(detail[key])];
    });
  }

  ns.MonitorDetailPanel=function(props){
    const esc=ns.escapeHtml;
    const compact=ns.compactText;
    const event=props.event||{};
    const latest=props.latest||{};
    const top=(latest.result||{}).top_candidate||{};
    const rows=detailRows(event.detail);
    return [
      '<aside class="monitorDetailPanel" aria-label="Monitor detail">',
        '<div class="monitorPanelHead">',
          '<div><h3>Detail</h3><p>Selected update and current top opportunity.</p></div>',
          '<span class="badge">'+esc(event.type||'latest')+'</span>',
        '</div>',
        '<section class="monitorDetailCard">',
          '<span>'+esc(event.type||'monitor update')+'</span>',
          '<h4>'+esc(event.title||latest.monitor_run_id||'Live monitor')+'</h4>',
          '<p>'+esc(compact(event.summary||'No monitor update selected yet.',190))+'</p>',
          rows.length?'<div class="monitorDetailFacts">'+rows.slice(0,8).map(function(row){return '<div><b>'+esc(row[0])+'</b><em>'+esc(row[1])+'</em></div>';}).join('')+'</div>':'',
        '</section>',
        '<section class="monitorDetailCard opportunity">',
          '<span>Current Opportunity</span>',
          '<h4>'+esc(top.title||((latest.summary||{}).top_candidate_title)||'No candidate yet')+'</h4>',
          '<p>'+esc(compact(top.market_gap||top.why_now||'Monitor history has not produced a top candidate yet.',190))+'</p>',
          '<div class="monitorDetailFacts">',
            '<div><b>score</b><em>'+esc(ns.score(top.solution_score))+'</em></div>',
            '<div><b>status</b><em>'+esc(top.status||'watching')+'</em></div>',
            '<div><b>why now</b><em>'+esc(compact(top.why_now||'waiting for next monitor pass',120))+'</em></div>',
          '</div>',
        '</section>',
      '</aside>'
    ].join('');
  };
})(window.ClaireMonitor=window.ClaireMonitor||{});
