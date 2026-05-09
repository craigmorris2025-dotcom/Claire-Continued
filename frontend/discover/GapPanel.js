(function(ns){
  ns.buildGaps=function(clusters){
    return (clusters||[]).map(function(cluster,index){
      const label=cluster.label||'market pattern';
      return {
        id:'gap-'+(index+1)+'-'+ns.slug(label),
        title:label+' decision gap',
        clusterId:cluster.id,
        clusterLabel:label,
        explanation:'The '+label+' cluster shows a gap between observed buyer pressure and the tools available to convert that pressure into a confident decision.',
        evidence:(cluster.evidence||[]).slice(0,3),
        severity:cluster.signals&&cluster.signals.length>1?'strong':'emerging'
      };
    });
  };

  ns.GapPanel=function(props){
    const esc=ns.escapeHtml;
    const compact=ns.compactText;
    const gaps=props.gaps||[];
    const sourceCount=props.sourceCount||0;
    const nextCount=props.nextCount||0;
    return [
      '<section class="discoverStage gapStage" data-stage="gaps">',
        '<div class="discoverStageHead">',
          '<span class="discoverStageNo">03</span>',
          '<div><h3>Gaps</h3><p>Why the opportunity exists.</p></div>',
          '<span class="badge">'+gaps.length+' gaps</span>',
        '</div>',
        '<div class="discoverStageBody">',
          gaps.map(function(gap,index){
            return [
              '<details class="discoverItem" '+(index===0?'open':'')+'>',
                '<summary>',
                  '<strong>'+esc(gap.title)+'</strong>',
                  '<span>'+esc(gap.severity)+'</span>',
                '</summary>',
                '<p>'+esc(compact(gap.explanation,170))+'</p>',
                '<div class="discoverLineage"><b>Created by</b><span>'+esc(gap.clusterLabel)+'</span></div>',
                '<div class="discoverLineage"><b>Supporting signals</b><span>'+esc(gap.evidence.join(' → '))+'</span></div>',
              '</details>'
            ].join('');
          }).join(''),
        '</div>',
        '<div class="discoverHandoff">'+sourceCount+' clusters → '+nextCount+' solution'+(nextCount===1?'':'s')+'</div>',
      '</section>'
    ].join('');
  };
})(window.ClaireDiscover=window.ClaireDiscover||{});
