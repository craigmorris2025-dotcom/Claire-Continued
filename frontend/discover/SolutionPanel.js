(function(ns){
  ns.buildSolutions=function(gaps){
    return (gaps||[]).map(function(gap,index){
      return {
        id:'solution-'+(index+1)+'-'+ns.slug(gap.title),
        title:gap.title.replace('decision gap','opportunity engine'),
        gapId:gap.id,
        gapTitle:gap.title,
        summary:'Build a focused intelligence surface that turns '+gap.clusterLabel+' signals into a scored opportunity recommendation.',
        why:'It exists because '+gap.explanation.charAt(0).toLowerCase()+gap.explanation.slice(1),
        supportingSignals:gap.evidence||[]
      };
    });
  };

  ns.SolutionPanel=function(props){
    const esc=ns.escapeHtml;
    const compact=ns.compactText;
    const solutions=props.solutions||[];
    const sourceCount=props.sourceCount||0;
    return [
      '<section class="discoverStage solutionStage" data-stage="solutions">',
        '<div class="discoverStageHead">',
          '<span class="discoverStageNo">04</span>',
          '<div><h3>Solutions</h3><p>Opportunity candidates produced by the flow.</p></div>',
          '<span class="badge">'+solutions.length+' solutions</span>',
        '</div>',
        '<div class="discoverStageBody">',
          solutions.map(function(solution,index){
            return [
              '<details class="discoverItem" '+(index===0?'open':'')+'>',
                '<summary>',
                  '<strong>'+esc(solution.title)+'</strong>',
                  '<span>opportunity</span>',
                '</summary>',
                '<p>'+esc(compact(solution.summary,170))+'</p>',
                '<div class="discoverFact"><b>Why it exists</b><span>'+esc(compact(solution.why,180))+'</span></div>',
                '<div class="discoverLineage"><b>Trace</b><span>'+esc(solution.supportingSignals.join(' → ')+' → '+solution.gapTitle+' → '+solution.title)+'</span></div>',
              '</details>'
            ].join('');
          }).join(''),
        '</div>',
        '<div class="discoverHandoff">'+sourceCount+' gaps resolved into opportunities</div>',
      '</section>'
    ].join('');
  };
})(window.ClaireDiscover=window.ClaireDiscover||{});
