"""Deal Exit Modeling Engine v5.19 — sector-gated exit logic."""
from typing import Any, Dict, List, Optional
class DealExitModelingEngine:
    def analyze(self,text:str,domain:str='general',keywords:Optional[List[str]]=None,scores:Optional[Dict[str,Any]]=None,market_gap:Optional[Dict[str,Any]]=None,trend_trajectory:Optional[Dict[str,Any]]=None,market_formation:Optional[Dict[str,Any]]=None,moat:Optional[Dict[str,Any]]=None,risk_regulation:Optional[Dict[str,Any]]=None,business_model:Optional[Dict[str,Any]]=None,acquirer_matches:Optional[List[Dict[str,Any]]]=None,connector_sources:Optional[Dict[str,Any]]=None)->Dict[str,Any]:
        s=self._signals(scores or {},domain,market_gap or {},trend_trajectory or {},market_formation or {},moat or {},risk_regulation or {},business_model or {},acquirer_matches or [],connector_sources or {})
        buyers=self._buyers(s,acquirer_matches or [],market_gap or {}); fit=self._fit(s,buyers); ready=self._ready(s,fit); val=self._valuation(s,fit)
        return {'status':'success','domain':s['domain'],'sector':s['sector'],'exit_readiness':ready,'buyer_universe':buyers,'strategic_fit':fit,'valuation_logic':val,'deal_paths':self._paths(s),'diligence_requirements':self._diligence(s),'risk_adjustments':self._adjustments(s),'negotiation_levers':self._levers(s,buyers),'exit_narrative':self._narrative(s,buyers,fit,val),'deal_exit_thesis':self._thesis(s,ready,fit,val),'recommended_next_actions':self._actions(s,ready),'evidence_signals':s,'confidence':self._confidence(s,fit,ready)}
    def _signals(self,scores,domain,mg,tr,mf,moat,rr,bm,matches,ext):
        top=[float(m.get('match_score',0) or 0) for m in matches]; sector=mg.get('sector','general')
        return {'domain':self._dom(sector,domain),'sector':sector,'portfolio_score':float(scores.get('portfolio_score',0) or 0),'breakthrough_score':float(scores.get('breakthrough_score',0) or 0),'viability_score':float(scores.get('viability_score',0) or 0),'feasibility_score':float(scores.get('feasibility_score',0) or 0),'acquisition_score':float(scores.get('acquisition_score',0) or 0),'market_gap_confidence':float(mg.get('confidence',0) or 0),'buyer_pull_score':self._get(mf,'buyer_pull','score'),'category_creation_score':self._get(mf,'category_creation_score','score'),'timing_pressure':self._get(tr,'timing_pressure','score'),'market_momentum':self._get(tr,'market_momentum','score'),'moat_score':self._get(moat,'moat_type','moat_score'),'copy_risk_score':self._get(moat,'copy_risk','score'),'primary_moat':self._text(moat,'moat_type','primary_moat'),'risk_score':self._get(rr,'risk_profile','score'),'blocker_level':self._text(rr,'blocker_assessment','blocker_level') or 'unknown','revenue_model':self._text(bm,'revenue_model','primary_model'),'value_capture_score':self._get(bm,'value_capture','score'),'buyer_roi_score':self._get(bm,'buyer_roi','score'),'commercial_risk_score':self._get(bm,'commercial_risk','score'),'acquirer_count':len(matches),'top_acquirer_score':max(top,default=0),'avg_top_5_acquirer_score':sum(sorted(top,reverse=True)[:5])/max(1,min(5,len(top))),'buyer_segment_count':len(mg.get('buyer_segments',[])),'acquirer_category_count':len(mg.get('acquirer_categories',[])),'acquirer_categories':mg.get('acquirer_categories',[]),'market_growth':float(ext.get('market',{}).get('growth',0) or 0),'market_volatility':float(ext.get('market',{}).get('volatility',0) or 0),'financial_health':float(ext.get('financial',{}).get('health',0) or 0),'financial_risk':float(ext.get('financial',{}).get('risk',0) or 0)}
    def _buyers(self,s,matches,mg):
        depth='deep' if s['acquirer_count']>=8 and s['top_acquirer_score']>=.90 else 'moderate' if s['acquirer_count']>=4 else 'thin'
        return {'depth':depth,'acquirer_count':s['acquirer_count'],'top_match_score':round(s['top_acquirer_score'],4),'average_top_5_score':round(s['avg_top_5_acquirer_score'],4),'acquirer_categories':mg.get('acquirer_categories',[]),'buyer_types':self._types(s),'top_matches':matches[:10]}
    def _fit(self,s,buyers):
        score=self._b(.18+s['acquisition_score']*.14+s['top_acquirer_score']*.13+s['avg_top_5_acquirer_score']*.08+s['buyer_pull_score']*.12+s['category_creation_score']*.11+s['value_capture_score']*.11+s['moat_score']*.09+min(.06,s['acquirer_count']*.006)-s['commercial_risk_score']*.035)
        return {'level':'strong' if score>=.78 else 'moderate' if score>=.60 else 'early','score':round(score,4),'fit_drivers':self._fit_drivers(s),'strategic_rationale':f"{s['sector'].replace('_',' ')} has {buyers.get('depth')} strategic-buyer coverage, top acquirer score of {s['top_acquirer_score']:.4f}, buyer pull of {s['buyer_pull_score']:.4f}, and value capture of {s['value_capture_score']:.4f}."}
    def _ready(self,s,fit):
        score=self._b(.16+s['portfolio_score']*.15+fit.get('score',0)*.15+s['value_capture_score']*.11+s['buyer_roi_score']*.10+s['moat_score']*.10+(1-s['copy_risk_score'])*.06+min(.06,s['acquirer_count']*.006)-s['risk_score']*.04-s['commercial_risk_score']*.04-(.05 if s['blocker_level']=='conditional' else 0))
        state='exit_candidate_with_conditions' if s['blocker_level']=='conditional' else 'exit_ready' if score>=.80 else 'exit_candidate' if score>=.64 else 'needs_validation'
        return {'state':state,'score':round(score,4),'readiness_drivers':self._readiness_drivers(s),'missing_proof':self._missing(s)}
    def _valuation(self,s,fit):
        score=self._b(.20+s['value_capture_score']*.16+s['buyer_roi_score']*.13+s['moat_score']*.11+fit.get('score',0)*.12+s['category_creation_score']*.10+s['portfolio_score']*.09-s['risk_score']*.035-s['commercial_risk_score']*.035)
        return {'valuation_signal':{'strength':'premium_strategic' if score>=.78 else 'strategic_with_validation' if score>=.62 else 'early_option_value','score':round(score,4)},'primary_value_drivers':self._value_drivers(s),'valuation_methods':self._methods(s),'upside_cases':self._upsides(s),'discount_factors':self._discounts(s)}
    def _paths(self,s):
        if s['sector']=='climate_insurance': raw=[('strategic acquisition by insurance analytics or cat-modeling platform',.17,'catastrophe modeling, insurance analytics, risk-data, or core insurance software platforms','validated underwriting ROI, climate exposure data moat, and workflow adoption','high'),('commercial partnership to acquisition',.13,'reinsurers, brokers, or core software platforms that want proof before acquisition','design-partner pilot, channel validation, and repeated buyer demand','high'),('risk-data licensing / embedded underwriting module',.09,'insurance platforms wanting climate-risk intelligence without immediate acquisition','stable data products, APIs, and underwriting workflow integration','medium'),('growth financing before exit',.04,'scaling carrier adoption before strategic exit','validated retention, modules, and repeatable sales motion','medium')]
        elif s['sector']=='financial_market_intelligence': raw=[('strategic acquisition by financial data or risk analytics platform',.16,'financial data, market intelligence, risk analytics, or asset-management technology platforms','validated signal value, institutional workflow adoption, and data moat','high'),('commercial partnership to acquisition',.11,'strategic buyers who need proof before corporate-development action','partner integration and repeated buyer demand','medium'),('platform licensing / API distribution',.08,'platforms that want embedded signal intelligence','stable APIs and defensible signal modules','medium'),('growth financing before exit',.04,'scaling institutional adoption before strategic exit','validated retention and repeatable sales motion','medium')]
        elif s['sector']=='industrial_supply_chain': raw=[('strategic acquisition',.18,'ERP, industrial software, automation, or supply-chain platforms seeking category expansion','validated enterprise pilots and ROI proof','high'),('commercial partnership to acquisition',.12,'strategic buyers who need proof','partner integration and repeated buyer demand','medium'),('platform licensing / OEM',.08,'software or industrial platforms that want embedded intelligence','stable APIs and integration reliability','medium'),('growth financing before exit',.04,'scaling enterprise adoption before strategic exit','validated retention','medium')]
        else: raw=[('strategic acquisition',.14,'strategic platforms seeking product/category expansion','validated ROI and defensibility','high'),('commercial partnership to acquisition',.10,'strategic buyers needing proof','partner integration and repeated buyer demand','medium'),('platform licensing / OEM',.07,'platforms wanting embedded intelligence','stable APIs and modules','medium'),('growth financing before exit',.04,'scaling adoption before strategic exit','repeatable sales motion','medium')]
        return sorted([{'path':p,'fit':self._path_score(s,b),'best_for':bf,'trigger':tr,'priority':pr} for p,b,bf,tr,pr in raw],key=lambda x:x['fit'],reverse=True)
    def _diligence(self,s):
        r=[{'requirement':'customer ROI evidence','why':'Buyers need proof that the system reduces cost, risk, loss, or cycle time.','priority':'high'},{'requirement':'technical architecture and integration review','why':'Strategic buyers will review scalability, APIs, integration, and maintainability.','priority':'high'},{'requirement':'model performance validation','why':'Forecasting and recommendation quality must be proven with backtests and pilots.','priority':'high'},{'requirement':'data rights and governance review','why':'Data-loop defensibility depends on clear rights, lineage, permissions, and controls.','priority':'high'},{'requirement':'commercial model validation','why':'Pricing must be supported by willingness-to-pay and expansion proof.','priority':'high'}]
        if s['sector']=='climate_insurance': r += [{'requirement':'underwriting and loss-history validation','why':'Insurance buyers need proof against weather losses, exposure changes, and repricing outcomes.','priority':'high'},{'requirement':'catastrophe / climate model review','why':'Climate-risk intelligence must survive actuarial, underwriting, and risk-model scrutiny.','priority':'high'}]
        if s['blocker_level']=='conditional': r.append({'requirement':'human-review and deployment-control evidence','why':'Conditional blocker must be resolved or framed as manageable.','priority':'critical'})
        if s['moat_score']<.78: r.append({'requirement':'differentiation and copy-risk defense','why':'Strategic buyers discount generic features without proprietary data or workflow depth.','priority':'medium'})
        return self._dedupe(r,'requirement')
    def _adjustments(self,s):
        a=[]
        if s['blocker_level']=='conditional': a.append({'adjustment':'conditional deployment discount','impact':'Strategic buyers may require risk controls and human-review validation before premium valuation.','severity':'medium','mitigation':'Package blocker mitigation as diligence evidence.'})
        if s['moat_score']<.78: a.append({'adjustment':'moat maturity discount','impact':'Moderate moat may reduce premium unless data loops and workflow dependency are proven.','severity':'medium','mitigation':'Validate repeat usage, proprietary benchmarks, and integration depth.'})
        if s['commercial_risk_score']>=.42: a.append({'adjustment':'commercial execution discount','impact':'Long sales cycles or procurement friction may reduce near-term deal value.','severity':'medium','mitigation':'Show paid pilot conversion and expansion path.'})
        if s['acquirer_count']<4: a.append({'adjustment':'thin buyer universe discount','impact':'Limited acquirer universe can weaken deal tension.','severity':'high','mitigation':'Expand buyer map.'})
        return a or [{'adjustment':'no major deterministic deal discount surfaced','impact':'Maintain evidence discipline and validate with live market data.','severity':'low','mitigation':'Continue acquirer research and diligence preparation.'}]
    def _levers(self,s,buyers):
        if s['sector']=='climate_insurance': levers=[('underwriting ROI and avoided loss exposure','Anchor valuation to climate-risk pricing, portfolio exposure visibility, and risk-transfer planning.'),('catastrophe and climate data moat','Frame defensibility around proprietary exposure data, loss history, and scenario intelligence.'),('multi-buyer tension across insurers, reinsurers, brokers, and cat-modeling platforms','Use insurance analytics, reinsurance, risk-data, and core software buyer categories to create strategic tension.')]
        elif s['sector']=='financial_market_intelligence': levers=[('signal value and institutional workflow adoption','Anchor valuation to earlier risk detection and market intelligence advantage.'),('data advantage','Position defensibility around proprietary signals and benchmarks.'),('multi-acquirer tension','Use financial data, risk analytics, and asset-management technology categories to create tension.')]
        else: levers=[('buyer pain and ROI','Anchor valuation to measurable buyer value.'),('data and workflow moat','Position defensibility around proprietary data and recurring workflow use.'),('multi-acquirer tension','Create tension across strategic buyer categories.')]
        out=[{'lever':l,'use':u,'priority':'high'} for l,u in levers]
        if s['revenue_model']: out.append({'lever':'recurring revenue path','use':'Emphasize subscriptions, module expansion, and account growth.','priority':'high'})
        return out
    def _types(self,s):
        if s['sector']=='climate_insurance': return [{'type':'insurance analytics platforms','strategic_reason':'can add climate exposure intelligence to underwriting and risk workflows','priority':'high'},{'type':'catastrophe modeling companies','strategic_reason':'can expand peril, climate, and property exposure models','priority':'high'},{'type':'reinsurers','strategic_reason':'can use climate-risk intelligence for risk transfer and portfolio steering','priority':'high'},{'type':'insurance core software platforms','strategic_reason':'can embed repricing and exposure modules into policy and underwriting systems','priority':'medium'}]
        if s['sector']=='financial_market_intelligence': return [{'type':'financial data platforms','strategic_reason':'can add proprietary signal intelligence to terminal/data workflows','priority':'high'},{'type':'risk analytics companies','strategic_reason':'can expand credit, liquidity, and portfolio risk models','priority':'high'},{'type':'asset-management technology platforms','strategic_reason':'can embed signals into investment and risk workflows','priority':'high'}]
        if s['sector']=='industrial_supply_chain': return [{'type':'ERP / enterprise application platforms','strategic_reason':'can embed predictive intelligence into planning and procurement workflows','priority':'high'},{'type':'industrial automation and industrial software companies','strategic_reason':'can extend operations intelligence into supplier and bottleneck prediction','priority':'high'}]
        return [{'type':'strategic technology buyers','strategic_reason':'can acquire the opportunity for product expansion and data advantage','priority':'medium'}]
    def _fit_drivers(self,s):
        d=[]
        if s['acquirer_count']>=8:d.append('large acquirer universe')
        if s['top_acquirer_score']>=.90:d.append('high top-acquirer match score')
        if s['buyer_pull_score']>=.80:d.append('strong buyer pull')
        if s['value_capture_score']>=.75:d.append('strong value capture')
        if s['moat_score']>=.70:d.append('defensible workflow/data position')
        if s['category_creation_score']>=.80:d.append('platform/category creation potential')
        if s['blocker_level']=='conditional':d.append('deal requires deployment-control proof')
        return d or ['strategic fit requires more validation']
    def _readiness_drivers(self,s):
        d=['portfolio score available','acquirer matching available','business model available','risk/regulation profile available']
        if s['value_capture_score']>=.75:d.append('strong value capture')
        if s['buyer_roi_score']>=.75:d.append('high buyer ROI')
        if s['top_acquirer_score']>=.90:d.append('strong top acquirer fit')
        if s['blocker_level']=='conditional':d.append('readiness is conditional on blocker mitigation')
        return d
    def _missing(self,s):
        m=[]
        if s['blocker_level']=='conditional':m.append('documented mitigation of human-review / deployment-control blocker')
        if s['moat_score']<.78:m.append('stronger evidence of proprietary data loops and workflow switching costs')
        if s['buyer_roi_score']<.85:m.append('quantified buyer ROI case')
        if s['sector']=='climate_insurance':m.append('underwriting, weather-loss, and exposure-model validation')
        if s['acquirer_count']<8:m.append('expanded acquirer universe and buyer mapping')
        return m or ['live market comparables and buyer-specific acquisition rationale']
    def _value_drivers(self,s):
        if s['sector']=='climate_insurance': d=['strategic buyer fit','insurance underwriting ROI','climate exposure data advantage','catastrophe model adjacency','risk-transfer intelligence','recurring platform/data revenue']
        elif s['sector']=='financial_market_intelligence': d=['strategic buyer fit','enterprise subscription potential','signal data advantage','institutional workflow adoption','platform/category formation']
        elif s['sector']=='industrial_supply_chain': d=['strategic buyer fit','enterprise subscription potential','strong value capture','buyer ROI','platform/category formation','industrial resilience urgency']
        else: d=['strategic buyer fit','recurring revenue potential','buyer ROI','data advantage','platform/category formation']
        if s['primary_moat']: d.append(f"primary moat: {s['primary_moat']}")
        return list(dict.fromkeys(d))
    def _methods(self,s):
        m=[{'method':'strategic acquisition premium','use_case':'best when acquirer product roadmap or category gap is directly addressed','priority':'high'},{'method':'ARR / recurring revenue multiple','use_case':'best once subscription revenue is validated','priority':'high' if s['revenue_model'] else 'medium'},{'method':'ROI-based strategic value','use_case':'best when buyer can quantify avoided loss, disruption, risk, or cost','priority':'high'},{'method':'technology and data-asset value','use_case':'best when proprietary datasets, benchmarks, and integrations are proven','priority':'medium'}]
        if s['sector']=='climate_insurance': m.append({'method':'risk-data product value','use_case':'best when climate exposure benchmarks become reusable premium data products','priority':'high'})
        return m
    def _upsides(self,s):
        if s['sector']=='climate_insurance': cases=['underwriting pilots convert to recurring enterprise subscriptions','climate exposure benchmarks become premium data products','risk-transfer and catastrophe modules expand account value','strategic buyer uses acquisition to fill climate-risk intelligence gap']
        elif s['sector']=='financial_market_intelligence': cases=['paid pilots convert to institutional platform subscriptions','signal modules expand across portfolio and risk workflows','proprietary signal benchmarks become premium data products','strategic buyer uses acquisition to fill market-intelligence gap']
        else: cases=['paid pilots convert to recurring enterprise subscriptions','modules expand across buyer workflows','proprietary benchmarks become premium data products','strategic buyer uses acquisition to fill category gap']
        if s['acquirer_count']>=8: cases.append('multiple strategic buyer categories create deal tension')
        return cases
    def _discounts(self,s):
        f=[]
        if s['blocker_level']=='conditional':f.append('conditional deployment blocker')
        if s['moat_score']<.78:f.append('moat still moderate rather than strong')
        if s['commercial_risk_score']>=.30:f.append('enterprise sales and implementation burden')
        if s['risk_score']>=.45:f.append('operational risk review required')
        return f or ['no major deterministic valuation discount surfaced']
    def _path_score(self,s,bonus): return round(self._b(.18+bonus+s['acquisition_score']*.13+s['top_acquirer_score']*.11+s['avg_top_5_acquirer_score']*.06+s['value_capture_score']*.10+s['buyer_roi_score']*.08+s['moat_score']*.08-s['commercial_risk_score']*.035),4)
    def _narrative(self,s,buyers,fit,val): return {'one_liner':f"A {s['sector'].replace('_',' ')} opportunity with {fit.get('level')} strategic fit, {buyers.get('depth')} buyer coverage, and {val.get('valuation_signal',{}).get('strength')} valuation signal.",'acquirer_pitch':self._pitch(s),'deal_story':self._story(s)}
    def _pitch(self,s): return 'Acquire or partner to own a climate-risk intelligence layer for underwriting, exposure management, repricing, and risk-transfer workflows.' if s['sector']=='climate_insurance' else 'Acquire or partner to own a proprietary signal-intelligence layer for institutional research, risk detection, and market workflow expansion.' if s['sector']=='financial_market_intelligence' else 'Acquire or partner to own a predictive intelligence layer with workflow, data, and module expansion potential.'
    def _story(self,s): return 'The deal story should lead with climate exposure urgency, underwriting ROI, weather-loss backtesting, proprietary risk data, and risk-transfer modules.' if s['sector']=='climate_insurance' else 'The deal story should lead with validated buyer pain, measurable ROI, workflow embedding, proprietary data loops, and a clear path from pilots to platform expansion.'
    def _thesis(self,s,ready,fit,val): return f"{s['sector'].replace('_',' ')} is a {ready.get('state')} with {fit.get('level')} strategic fit and {val.get('valuation_signal',{}).get('strength')} valuation signal."
    def _actions(self,s,ready):
        a=[{'action':'build acquirer-specific strategic rationale','purpose':'translate Claire output into buyer-specific deal logic','priority':'high'},{'action':'prepare diligence evidence pack','purpose':'organize ROI proof, technical architecture, data rights, model validation, and risk controls','priority':'high'},{'action':'model pilot-to-enterprise conversion economics','purpose':'support valuation and commercial readiness with concrete revenue milestones','priority':'high'},{'action':'map deal path options','purpose':'compare acquisition, commercial partnership, licensing, and growth-financing paths','priority':'medium'}]
        if s['sector']=='climate_insurance': a.insert(1,{'action':'prepare underwriting and climate-loss validation pack','purpose':'prove model value to insurers, reinsurers, and catastrophe-risk buyers','priority':'high'})
        if s['blocker_level']=='conditional': a.append({'action':'resolve deployment-control blocker before outreach','purpose':'prevent risk-control questions from weakening deal leverage','priority':'critical'})
        if ready.get('state')!='exit_ready': a.append({'action':'close missing proof points','purpose':'move from candidate to exit-ready package','priority':'high'})
        return a
    def _b(self,v): return max(0,min(.96,v))
    def _confidence(self,s,fit,ready): return round(self._b(.22+s['portfolio_score']*.11+fit.get('score',0)*.13+ready.get('score',0)*.11+s['top_acquirer_score']*.09+s['avg_top_5_acquirer_score']*.06+s['value_capture_score']*.09+s['buyer_roi_score']*.08+s['moat_score']*.07-s['risk_score']*.025-s['commercial_risk_score']*.025),4)
    def _dom(self,sector,fallback): return {'climate_insurance':'insurance','defense_autonomy':'technology','healthcare_operations':'healthcare','industrial_supply_chain':'industrial','energy_infrastructure':'energy','financial_market_intelligence':'finance'}.get(sector,fallback or 'general')
    def _get(self,obj,*path):
        cur=obj
        for k in path:
            if not isinstance(cur,dict): return 0.0
            cur=cur.get(k,0.0)
        try:return float(cur or 0.0)
        except Exception:return 0.0
    def _text(self,obj,*path):
        cur=obj
        for k in path:
            if not isinstance(cur,dict): return ''
            cur=cur.get(k,'')
        return str(cur or '')
    def _dedupe(self,items,key):
        d={}
        for item in items:d[item.get(key,'')]=item
        return list(d.values())
