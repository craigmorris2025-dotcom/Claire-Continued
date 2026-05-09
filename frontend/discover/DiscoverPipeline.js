(function(ns){
  const fallbackSignals=[
    {
      id:'signal-governance-pressure',
      title:'Governed AI intake demand',
      summary:'Teams need a clearer way to evaluate AI ideas before budget, procurement, or implementation review.',
      source:'Claire deterministic seed',
      signal_type:'market_pressure',
      strength:'high',
      why:'Creates demand for an explainable opportunity filter before teams commit resources.'
    },
    {
      id:'signal-readiness-gap',
      title:'Implementation readiness is unclear',
      summary:'Buyers struggle to compare technical feasibility, integration burden, and risk in one decision surface.',
      source:'Claire deterministic seed',
      signal_type:'workflow_gap',
      strength:'medium',
      why:'Turns scattered due diligence into a measurable gap.'
    },
    {
      id:'signal-evidence-friction',
      title:'Evidence is fragmented',
      summary:'Signals, constraints, and solution claims often live in separate tools and do not converge into a single opportunity view.',
      source:'Claire deterministic seed',
      signal_type:'evidence_gap',
      strength:'medium',
      why:'Supports a flow that connects source signals to final opportunity rationale.'
    }
  ];

  ns.escapeHtml=function(value){
    return String(value===undefined||value===null?'':value).replace(/[&<>"']/g,function(ch){
      return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[ch];
    });
  };
  ns.compactText=function(value,limit){
    const text=String(value===undefined||value===null?'':value).replace(/\s+/g,' ').trim();
    const max=limit||140;
    return text.length>max?text.slice(0,max-1)+'...':text;
  };
  ns.slug=function(value){
    return String(value||'stage').toLowerCase().replace(/[^a-z0-9]+/g,'-').replace(/^-|-$/g,'')||'stage';
  };

  function normalizeSignal(signal,index){
    const id=signal.id||signal.signal_id||('signal-'+index);
    return {
      id:ns.slug(id),
      title:signal.title||signal.name||signal.signal_type||('Signal '+(index+1)),
      summary:signal.summary||signal.description||signal.connected_thesis||signal.snippet||'Signal captured for Discover analysis.',
      source:signal.source_category||signal.source||signal.market_universe||'local context',
      signal_type:signal.signal_type||signal.type||signal.opportunity_relevance||'market_signal',
      strength:signal.signal_strength||signal.opportunity_relevance||signal.strength||'observed',
      why:signal.why||signal.opportunity_direction||signal.opportunity_relevance_reason||'This signal helps explain why an opportunity may exist.'
    };
  }

  async function loadSignals(api){
    try{
      const payload=await api('/api/signals/normalized');
      const signals=(payload.signals||[]).map(normalizeSignal);
      return signals.length?signals:fallbackSignals;
    }catch(e){
      return fallbackSignals;
    }
  }

  function buildContext(signals){
    const clusters=ns.buildClusters?ns.buildClusters(signals):[];
    const gaps=ns.buildGaps?ns.buildGaps(clusters):[];
    const solutions=ns.buildSolutions?ns.buildSolutions(gaps):[];
    return {signals,clusters,gaps,solutions};
  }

  ns.DiscoverPipeline=function(context){
    const signals=context.signals||[];
    const clusters=context.clusters||[];
    const gaps=context.gaps||[];
    const solutions=context.solutions||[];
    return [
      '<div class="discover-pipeline" aria-label="Discover pipeline">',
        '<div class="discoverFlowRail">',
          ns.SignalPanel({signals:signals,nextCount:clusters.length}),
          '<div class="discoverConnector" aria-hidden="true">→</div>',
          ns.ClusterPanel({clusters:clusters,sourceCount:signals.length,nextCount:gaps.length}),
          '<div class="discoverConnector" aria-hidden="true">→</div>',
          ns.GapPanel({gaps:gaps,sourceCount:clusters.length,nextCount:solutions.length}),
          '<div class="discoverConnector" aria-hidden="true">→</div>',
          ns.SolutionPanel({solutions:solutions,sourceCount:gaps.length}),
        '</div>',
      '</div>'
    ].join('');
  };

  ns.initDiscoverPipeline=async function(root,options){
    if(!root) return;
    const api=(options&&options.api)||window.api;
    root.innerHTML='<div class="status">Loading Discover pipeline...</div>';
    const signals=await loadSignals(api);
    const context=buildContext(signals);
    root.innerHTML=ns.DiscoverPipeline(context);
  };
})(window.ClaireDiscover=window.ClaireDiscover||{});
