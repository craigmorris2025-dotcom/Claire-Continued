(function(ns){
  ns.SignalPanel=function(props){
    const esc=ns.escapeHtml;
    const compact=ns.compactText;
    const signals=props.signals||[];
    const count=signals.length;
    const nextCount=props.nextCount||0;
    return [
      '<section class="discoverStage signalStage" data-stage="signals">',
        '<div class="discoverStageHead">',
          '<span class="discoverStageNo">01</span>',
          '<div><h3>Signals</h3><p>Observed inputs that start the opportunity chain.</p></div>',
          '<span class="badge">'+count+' signals</span>',
        '</div>',
        '<div class="discoverStageBody">',
          signals.map(function(signal,index){
            return [
              '<details class="discoverItem" '+(index===0?'open':'')+'>',
                '<summary>',
                  '<strong>'+esc(signal.title)+'</strong>',
                  '<span>'+esc(signal.strength)+'</span>',
                '</summary>',
                '<p>'+esc(compact(signal.summary,150))+'</p>',
                '<div class="discoverFact"><b>Source</b><span>'+esc(signal.source)+'</span></div>',
                '<div class="discoverFact"><b>Why it matters</b><span>'+esc(compact(signal.why,150))+'</span></div>',
              '</details>'
            ].join('');
          }).join(''),
        '</div>',
        '<div class="discoverHandoff">Feeds '+nextCount+' cluster'+(nextCount===1?'':'s')+'</div>',
      '</section>'
    ].join('');
  };
})(window.ClaireDiscover=window.ClaireDiscover||{});
