(function(ns){
  function signalEvents(result, when){
    return (((result.extracted||{}).signals)||[]).slice(0,4).map(function(signal){
      return {
        type:'new signal detected',
        tone:'signal',
        time:when,
        title:signal.title||signal.signal_type||'Live signal',
        summary:signal.summary||'A structured live signal entered the monitor stream.',
        meta:(signal.entity_name||signal.ticker||'source')+' · '+(signal.urgency||'observed'),
        detail:signal
      };
    });
  }
  function clusterEvents(result, when){
    return (((result.clusters||{}).clusters)||[]).slice(0,4).map(function(cluster){
      return {
        type:'trend strengthening',
        tone:'cluster',
        time:when,
        title:cluster.title||cluster.trend_type||'Trend cluster',
        summary:(cluster.trajectory||'forming')+' trend with '+(cluster.signal_count||0)+' signal(s) across '+(cluster.entity_count||0)+' entities.',
        meta:'strength '+ns.score(cluster.strength_score),
        detail:cluster
      };
    });
  }
  function gapEvents(result, when){
    return (((result.gaps||{}).gaps)||[]).slice(0,4).map(function(gap){
      return {
        type:'gap emerging',
        tone:'gap',
        time:when,
        title:gap.market_gap||'Market gap',
        summary:gap.why_now||'A monitored trend created a visible opportunity gap.',
        meta:(gap.urgency||'observed')+' · score '+ns.score(gap.gap_score),
        detail:gap
      };
    });
  }
  function solutionEvents(result, when){
    return (((result.solutions||{}).candidates)||[]).slice(0,4).map(function(solution){
      return {
        type:'solution ready',
        tone:'solution',
        time:when,
        title:solution.title||solution.needed_solution||'Solution opportunity',
        summary:solution.why_now||solution.market_gap||'A live opportunity candidate is ready for review.',
        meta:'score '+ns.score(solution.solution_score)+' · '+(solution.status||'candidate'),
        detail:solution
      };
    });
  }

  ns.buildMonitorEvents=function(context){
    const latest=context.latest||{};
    const result=latest.result||{};
    const history=((context.history||{}).runs)||[];
    const when=latest.recorded_at||result.generated_at||'latest';
    const events=[];
    if(latest.monitor_run_id){
      events.push({
        type:'monitor run recorded',
        tone:'run',
        time:when,
        title:latest.monitor_run_id,
        summary:'Latest monitor pass produced '+((latest.summary||{}).signals||0)+' signals, '+((latest.summary||{}).gaps||0)+' gaps, and '+((latest.summary||{}).solutions||0)+' solutions.',
        meta:((latest.summary||{}).top_candidate_title)||'live opportunity monitor',
        detail:latest.summary||{}
      });
    }
    events.push.apply(events,signalEvents(result,when));
    events.push.apply(events,clusterEvents(result,when));
    events.push.apply(events,gapEvents(result,when));
    events.push.apply(events,solutionEvents(result,when));
    history.slice(1,5).forEach(function(run){
      events.push({
        type:'history update',
        tone:'history',
        time:run.recorded_at,
        title:run.monitor_run_id,
        summary:'Prior monitor run retained in history with '+((run.summary||{}).solutions||0)+' solution candidate(s).',
        meta:((run.summary||{}).top_candidate_title)||'history store',
        detail:run.summary||{}
      });
    });
    return events;
  };

  ns.MonitorTimeline=function(props){
    const esc=ns.escapeHtml;
    const compact=ns.compactText;
    const events=props.events||[];
    return [
      '<section class="monitorTimelinePanel">',
        '<div class="monitorPanelHead"><div><h3>Live Timeline</h3><p>Signals, trends, gaps, and solution changes over time.</p></div><span class="badge">'+events.length+' updates</span></div>',
        '<div class="monitorTimeline" role="list">',
          events.map(function(event,index){
            return [
              '<article class="monitorTimelineItem '+esc(event.tone)+'" role="listitem" tabindex="0" data-monitor-event="'+index+'">',
                '<div class="monitorEventDot"></div>',
                '<div>',
                  '<div class="monitorEventTop"><span>'+esc(event.type)+'</span><time>'+esc(event.time||'latest')+'</time></div>',
                  '<h4>'+esc(event.title)+'</h4>',
                  '<p>'+esc(compact(event.summary,170))+'</p>',
                  '<small>'+esc(event.meta||'live intelligence')+'</small>',
                '</div>',
              '</article>'
            ].join('');
          }).join(''),
        '</div>',
      '</section>'
    ].join('');
  };
})(window.ClaireMonitor=window.ClaireMonitor||{});
