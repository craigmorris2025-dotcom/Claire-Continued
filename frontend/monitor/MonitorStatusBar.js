(function(ns){
  ns.MonitorStatusBar=function(context){
    const esc=ns.escapeHtml;
    const status=context.status||{};
    const latest=context.latest||{};
    const plan=context.plan||{};
    const registry=status.registry||{};
    const monitor=status.monitor||{};
    const summary=latest.summary||{};
    const due=(plan.scan_items||[]).filter(function(item){return item.status==='due';}).length;
    return [
      '<section class="monitorStatusBar" aria-label="Monitor freshness and scan status">',
        '<div class="monitorStatusCell">',
          '<span>Freshness</span>',
          '<strong>'+esc(due)+' due</strong>',
          '<small>'+esc(plan.planned_at||'not planned')+'</small>',
        '</div>',
        '<div class="monitorStatusCell">',
          '<span>Scan Status</span>',
          '<strong>'+esc(monitor.ready?'ready':(monitor.status||'checking'))+'</strong>',
          '<small>'+esc((plan.scan_item_count||0)+' scan items')+'</small>',
        '</div>',
        '<div class="monitorStatusCell">',
          '<span>Latest Run</span>',
          '<strong>'+esc(latest.monitor_run_id||plan.latest_monitor_run||'none')+'</strong>',
          '<small>'+esc(latest.recorded_at||plan.latest_recorded_at||'no history')+'</small>',
        '</div>',
        '<div class="monitorStatusCell">',
          '<span>Live Surface</span>',
          '<strong>'+esc(summary.live_opportunities_ready?'opportunities ready':'watching')+'</strong>',
          '<small>'+esc((registry.entity_count||0)+' entities · '+((status.connectors||{}).connector_count||0)+' connectors')+'</small>',
        '</div>',
      '</section>'
    ].join('');
  };
})(window.ClaireMonitor=window.ClaireMonitor||{});
