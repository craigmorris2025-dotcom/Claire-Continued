(function(ns){
  ns.buildClusters=function(signals){
    const grouped=new Map();
    (signals||[]).forEach(function(signal){
      const key=signal.signal_type||'market_signal';
      if(!grouped.has(key)){
        grouped.set(key,{
          id:'cluster-'+ns.slug(key),
          label:key.replace(/_/g,' '),
          signals:[],
          summary:''
        });
      }
      grouped.get(key).signals.push(signal);
    });
    return Array.from(grouped.values()).map(function(cluster){
      const first=cluster.signals[0]||{};
      cluster.summary='Signals around '+cluster.label+' point to '+(first.why||first.summary||'a repeated market pattern')+'.';
      cluster.evidence=cluster.signals.map(function(signal){return signal.title;});
      return cluster;
    });
  };

  ns.ClusterPanel=function(props){
    const esc=ns.escapeHtml;
    const compact=ns.compactText;
    const clusters=props.clusters||[];
    const sourceCount=props.sourceCount||0;
    const nextCount=props.nextCount||0;
    return [
      '<section class="discoverStage clusterStage" data-stage="clusters">',
        '<div class="discoverStageHead">',
          '<span class="discoverStageNo">02</span>',
          '<div><h3>Clusters</h3><p>Related signals grouped into readable themes.</p></div>',
          '<span class="badge">'+clusters.length+' clusters</span>',
        '</div>',
        '<div class="discoverStageBody">',
          clusters.map(function(cluster,index){
            return [
              '<details class="discoverItem" '+(index===0?'open':'')+'>',
                '<summary>',
                  '<strong>'+esc(cluster.label)+'</strong>',
                  '<span>'+cluster.signals.length+' signal'+(cluster.signals.length===1?'':'s')+'</span>',
                '</summary>',
                '<p>'+esc(compact(cluster.summary,150))+'</p>',
                '<div class="discoverLineage"><b>Built from</b><span>'+esc(cluster.evidence.join(' → '))+'</span></div>',
              '</details>'
            ].join('');
          }).join(''),
        '</div>',
        '<div class="discoverHandoff">'+sourceCount+' signals → '+nextCount+' gap'+(nextCount===1?'':'s')+'</div>',
      '</section>'
    ].join('');
  };
})(window.ClaireDiscover=window.ClaireDiscover||{});
