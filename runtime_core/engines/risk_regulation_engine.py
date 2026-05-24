"""Risk Regulation Engine v5.19 — sector-gated cleanup."""
from typing import Any, Dict, List, Optional
import re
class RiskRegulationEngine:
    def analyze(self,text:str,domain:str='general',keywords:Optional[List[str]]=None,market_gap:Optional[Dict[str,Any]]=None,trend_trajectory:Optional[Dict[str,Any]]=None,market_formation:Optional[Dict[str,Any]]=None,moat:Optional[Dict[str,Any]]=None,connector_sources:Optional[Dict[str,Any]]=None)->Dict[str,Any]:
        s=self._signals(text or '',keywords or [],domain,market_gap or {},trend_trajectory or {},market_formation or {},moat or {},connector_sources or {})
        rp=self._risk_profile(s); reg=self._regulation_profile(s); block=self._blockers(s,rp,reg)
        return {'status':'success','domain':s['domain'],'sector':s['sector'],'risk_profile':rp,'regulation_profile':reg,'compliance_requirements':self._requirements(s),'operational_risks':self._operational(s),'data_security_privacy':self._security(s),'deployment_constraints':self._constraints(s),'blocker_assessment':block,'mitigation_actions':self._mitigations(s,reg,block),'validation_requirements':self._validations(s),'risk_regulation_thesis':self._thesis(s,rp,reg,block),'evidence_signals':s,'confidence':self._confidence(s)}
    def _signals(self,text,keywords,domain,mg,tr,mf,moat,ext):
        c=f"{text.lower()} {' '.join(keywords).lower()}"; sector=mg.get('sector','general')
        def n(pats): return sum(1 for p in pats if re.search(p,c))
        ins=sector=='climate_insurance' or n([r'insurance',r'reinsurance',r'underwriting',r'catastrophe',r'climate exposure',r'weather losses'])>=1
        ind=sector=='industrial_supply_chain' or n([r'supply chain',r'manufacturing',r'industrial',r'supplier',r'erp',r'procurement'])>=2
        ene=sector=='energy_infrastructure' or n([r'energy',r'grid',r'utility',r'utilities',r'transmission',r'power grid',r'power systems?'])>=2
        hc=sector=='healthcare_operations' or n([r'healthcare',r'hospital',r'patient',r'clinical'])>=1
        defense=sector=='defense_autonomy' or n([r'defense',r'military',r'battlefield',r'mission',r'drone',r'secure command'])>=1
        fin=sector=='financial_market_intelligence' or n([r'financial',r'credit',r'liquidity',r'capital markets?',r'portfolio'])>=2
        autonomy=n([r'autonomous',r'autonomy',r'human override',r'drone coordination'])
        data=n([r'data',r'dataset',r'historical',r'benchmark',r'model',r'forecast',r'signals?'])
        priv=n([r'privacy',r'personal data',r'patient',r'sensitive data'])
        comp=n([r'compliance',r'regulatory',r'regulation',r'audit',r'governance',r'controls'])
        w=max([0.15,0.66 if ins else 0,0.88 if defense else 0,0.82 if hc else 0,0.70 if fin else 0,0.68 if ene else 0,0.46 if ind else 0])
        return {'domain':self._dom(sector,domain),'sector':sector,'explicit_insurance':ins,'explicit_industrial':ind,'explicit_energy':ene,'explicit_healthcare':hc,'explicit_defense':defense,'explicit_finance':fin,'autonomy_term_count':autonomy,'data_term_count':data,'privacy_term_count':priv,'compliance_term_count':comp,'sector_regulatory_weight':w,'market_volatility':float(ext.get('market',{}).get('volatility',0) or 0),'financial_risk':float(ext.get('financial',{}).get('risk',0) or 0),'financial_health':float(ext.get('financial',{}).get('health',0) or 0),'strategic_pressure_score':self._get(mg,'strategic_pressure','score'),'market_gap_confidence':float(mg.get('confidence',0) or 0),'buyer_pull_score':self._get(mf,'buyer_pull','score'),'timing_pressure':self._get(tr,'timing_pressure','score'),'moat_score':self._get(moat,'moat_type','moat_score'),'copy_risk_score':self._get(moat,'copy_risk','score'),'buyer_segment_count':len(mg.get('buyer_segments',[])),'ecosystem_requirement_count':len(mf.get('ecosystem_requirements',[]))}
    def _risk_profile(self,s):
        score=min(0.94,0.16+s['sector_regulatory_weight']*0.22+s['privacy_term_count']*0.035+s['compliance_term_count']*0.02+s['autonomy_term_count']*0.025+s['market_volatility']*0.08+s['financial_risk']*0.07+(0.08 if s['explicit_defense'] else 0)+(0.06 if s['explicit_healthcare'] else 0)+(0.05 if s['explicit_insurance'] else 0))
        return {'level':'high' if score>=0.70 else 'moderate' if score>=0.48 else 'low','score':round(score,4),'risk_drivers':self._drivers(s)}
    def _regulation_profile(self,s):
        score=min(0.96,0.14+s['sector_regulatory_weight']*0.35+s['compliance_term_count']*0.03+s['privacy_term_count']*0.03+(0.12 if s['explicit_defense'] else 0)+(0.10 if s['explicit_healthcare'] else 0)+(0.08 if s['explicit_finance'] else 0)+(0.08 if s['explicit_insurance'] else 0)+(0.07 if s['explicit_energy'] else 0))
        return {'exposure':'high' if score>=0.72 else 'moderate' if score>=0.48 else 'low','score':round(score,4),'regulatory_categories':self._cats(s)}
    def _requirements(self,s):
        r=[{'requirement':'audit logging and traceability','why':'Recommendations should be explainable, reviewable, and reproducible.','priority':'high'},{'requirement':'data governance and access controls','why':'The system uses strategic, operational, or market data.','priority':'high'},{'requirement':'model monitoring and performance validation','why':'Predictions and recommendations must be checked against real outcomes.','priority':'high'}]
        if s['explicit_insurance']: r += [{'requirement':'insurance model governance review','why':'Underwriting, exposure, repricing, and risk-transfer recommendations need documented validation.','priority':'high'},{'requirement':'catastrophe and climate-exposure model validation','why':'Climate and catastrophe outputs can affect underwriting, pricing, and market-withdrawal decisions.','priority':'high'}]
        if s['explicit_finance']: r.append({'requirement':'financial model governance','why':'Credit, liquidity, portfolio, and market-risk signals need documented validation.','priority':'high'})
        if s['explicit_healthcare']: r.append({'requirement':'clinical safety and health-data compliance review','why':'Healthcare workflows can affect patients, clinicians, capacity, or care delivery.','priority':'high'})
        if s['explicit_defense']: r.append({'requirement':'secure deployment, export-control, and mission-use review','why':'Defense, mission, autonomy, surveillance, or battlefield contexts require stricter controls.','priority':'high'})
        if s['explicit_energy']: r.append({'requirement':'critical infrastructure and utility-operations review','why':'Grid, utility, and power systems can carry reliability and infrastructure obligations.','priority':'high'})
        if s['explicit_industrial']: r.append({'requirement':'industrial operations change-control review','why':'Manufacturing, procurement, ERP, supplier, and planning integrations can affect production decisions.','priority':'medium'})
        if s['privacy_term_count'] or s['explicit_healthcare']: r.append({'requirement':'privacy impact assessment','why':'The opportunity may process sensitive, personal, patient, or customer data.','priority':'high'})
        if s['autonomy_term_count'] or s['explicit_defense']: r.append({'requirement':'human oversight and override policy','why':'Autonomous or mission-critical recommendations require reviewable human control.','priority':'high'})
        return self._dedupe(r,'requirement')
    def _operational(self,s):
        risks=[]
        if s['explicit_insurance']: risks += [{'risk':'mispriced climate exposure or underwriting recommendation','severity':'medium','mitigation':'validate with historical loss data, stress scenarios, and underwriting review'},{'risk':'over-reliance on model outputs for repricing or market withdrawal decisions','severity':'medium','mitigation':'require human review and model confidence thresholds'}]
        if s['explicit_industrial']: risks.append({'risk':'bad forecast or recommendation disrupts production planning','severity':'medium','mitigation':'run shadow-mode validation before operational automation'})
        if s['explicit_energy']: risks.append({'risk':'utility or grid operations dependency','severity':'high','mitigation':'validate in simulation and limited-scope pilots'})
        if s['explicit_healthcare']: risks.append({'risk':'recommendations affect clinical or patient-flow decisions','severity':'high','mitigation':'require clinical validation and workflow signoff'})
        if s['explicit_defense']: risks.append({'risk':'mission or surveillance deployment misuse','severity':'high','mitigation':'enforce mission-use constraints and human authorization'})
        return risks or [{'risk':'operational assumptions require validation','severity':'low','mitigation':'validate with pilot users and historical backtesting'}]
    def _security(self,s):
        score=min(0.95,0.18+s['data_term_count']*0.02+s['privacy_term_count']*0.075+(0.08 if s['explicit_healthcare'] else 0)+(0.06 if s['explicit_defense'] else 0)+(0.05 if s['explicit_finance'] or s['explicit_insurance'] else 0))
        controls=['role-based access control','audit logging','data lineage tracking','source-level permissions','encryption in transit and at rest']
        if s['explicit_insurance']: controls+=['model versioning','exposure-data provenance','underwriting decision audit trail']
        if s['explicit_healthcare']: controls+=['privacy impact assessment','minimum necessary data policy','retention and deletion policy']
        if s['explicit_defense']: controls+=['restricted access environments','mission-use authorization logs','secure deployment boundary']
        if s['explicit_industrial']: controls+=['ERP integration access scoping','operational data quality monitoring']
        return {'data_sensitivity':{'level':'high' if score>=0.70 else 'moderate' if score>=0.45 else 'standard','score':round(score,4)},'recommended_controls':sorted(set(controls))}
    def _constraints(self,s):
        c=[{'constraint':'do not automate high-impact decisions until validated','applies_to':'all high-confidence but unvalidated recommendations','priority':'high'},{'constraint':'require explainability for scoring and recommendations','applies_to':'buyer, compliance, and internal review workflows','priority':'high'}]
        if s['explicit_insurance']: c.append({'constraint':'deploy first as underwriting and portfolio-risk decision support','applies_to':'insurance pricing, risk-transfer, and market-withdrawal workflows','priority':'high'})
        if s['explicit_industrial']: c.append({'constraint':'deploy first in advisory / shadow mode','applies_to':'manufacturing, procurement, ERP, and planning-system integrations','priority':'high'})
        if s['explicit_energy']: c.append({'constraint':'validate in simulation before live critical infrastructure use','applies_to':'grid, utility, transmission, power, and infrastructure workflows','priority':'high'})
        if s['explicit_healthcare']: c.append({'constraint':'avoid direct clinical decision automation without clinical validation','applies_to':'patient, clinician, capacity, or care-delivery workflows','priority':'high'})
        if s['explicit_finance']: c.append({'constraint':'separate research signals from regulated financial advice','applies_to':'credit, capital, portfolio, liquidity, and investment workflows','priority':'high'})
        if s['explicit_defense']: c.append({'constraint':'restrict mission-critical or surveillance use without authorization and controls','applies_to':'defense, autonomy, drone, battlefield, or border contexts','priority':'high'})
        return c
    def _blockers(self,s,rp,reg):
        b=[]
        if s['explicit_defense']: b.append('defense/security deployment constraints require review')
        if s['explicit_healthcare'] and s['privacy_term_count']: b.append('health or patient data compliance must be resolved before deployment')
        if s['autonomy_term_count'] and (s['explicit_defense'] or rp['level']=='high'): b.append('AI autonomy in high-impact workflow requires human override policy')
        level='conditional' if b else 'manageable' if rp['level']=='moderate' or reg['exposure']=='moderate' else 'low'
        return {'blocker_level':level,'blockers':b,'go_forward_condition':'Proceed only after documented mitigation plan resolves identified blockers.' if level=='conditional' else 'Proceed with compliance review, shadow-mode validation, and human-review gates.' if level=='manageable' else 'Proceed with standard auditability, data governance, and validation controls.'}
    def _mitigations(self,s,reg,block):
        a=[{'action':'document model assumptions and decision logic','purpose':'support auditability, validation, and buyer trust','priority':'high'},{'action':'launch in advisory mode before automation','purpose':'reduce operational risk while gathering validation evidence','priority':'high'},{'action':'create confidence thresholds and human-review gates','purpose':'prevent unsupported recommendations from driving high-impact decisions','priority':'high'},{'action':'establish data lineage and source-quality scoring','purpose':'make forecasts and recommendations traceable back to source inputs','priority':'high'}]
        if reg['exposure'] in {'moderate','high'}: a.append({'action':'perform sector-specific compliance review','purpose':'confirm regulatory obligations before buyer deployment','priority':'high'})
        if s['explicit_insurance']: a.append({'action':'validate underwriting and exposure models against historical loss data','purpose':'prove climate-risk and repricing recommendations before commercial use','priority':'high'})
        if s['explicit_defense']: a.append({'action':'define allowed-use and restricted-use policy','purpose':'prevent misuse in surveillance, mission, or security-sensitive settings','priority':'high'})
        if block['blocker_level']=='conditional': a.append({'action':'resolve blockers before go-to-market packaging','purpose':'avoid unresolved compliance or deployment constraints','priority':'critical'})
        return self._dedupe(a,'action')
    def _validations(self,s):
        v=[{'validation':'historical backtesting','purpose':'test forecast and recommendation quality against past events','priority':'high'},{'validation':'shadow-mode pilot','purpose':'compare system recommendations with real operator decisions without automating outcomes','priority':'high'},{'validation':'false-positive / false-negative analysis','purpose':'understand failure modes before operational deployment','priority':'high'},{'validation':'user acceptance and workflow-fit testing','purpose':'confirm the system improves decisions in the buyer workflow','priority':'medium'}]
        if s['explicit_insurance']: v.append({'validation':'climate exposure and catastrophe-loss backtesting','purpose':'validate underwriting, repricing, and risk-transfer outputs against historical losses and scenarios','priority':'high'})
        if s['explicit_industrial']: v.append({'validation':'ERP and planning-system integration test','purpose':'validate source quality, permissions, latency, and operational safety','priority':'high'})
        if s['explicit_healthcare']: v.append({'validation':'clinical workflow review','purpose':'confirm no patient-impacting deployment occurs without proper clinical validation','priority':'high'})
        if s['explicit_finance']: v.append({'validation':'financial model governance review','purpose':'validate risk, credit, liquidity, or capital assumptions','priority':'high'})
        if s['explicit_defense']: v.append({'validation':'secure mission-use review','purpose':'define allowed deployment conditions and oversight requirements','priority':'high'})
        return self._dedupe(v,'validation')
    def _drivers(self,s):
        d=[]
        if s['sector_regulatory_weight']>=0.65:d.append('regulated or high-impact sector')
        if s['explicit_insurance']:d.append('insurance underwriting / climate exposure model risk')
        if s['explicit_industrial']:d.append('industrial operations / ERP integration exposure')
        if s['explicit_energy']:d.append('critical infrastructure / utility operations exposure')
        if s['explicit_healthcare']:d.append('healthcare workflow / patient data exposure')
        if s['explicit_defense']:d.append('defense / mission-use exposure')
        if s['autonomy_term_count']:d.append('autonomous decisioning requires human oversight')
        return d or ['no major deterministic risk driver surfaced']
    def _cats(self,s):
        c=['AI governance / model risk','data governance']
        if s['explicit_insurance']: c+=['insurance model governance','underwriting / exposure model validation','climate risk / catastrophe modeling']
        if s['explicit_finance']: c+=['financial model governance']
        if s['explicit_healthcare']: c+=['healthcare / clinical workflow']
        if s['explicit_defense']: c+=['defense / mission use','export-control / secure deployment']
        if s['explicit_energy']: c+=['critical infrastructure / utility operations']
        if s['explicit_industrial']: c+=['industrial operations','ERP / operational-system integration']
        if s['autonomy_term_count'] or s['explicit_defense']: c+=['human oversight for AI recommendations']
        return sorted(set(c))
    def _thesis(self,s,rp,reg,block): return f"{s.get('sector','target sector').replace('_',' ')} shows {rp.get('level')} risk and {reg.get('exposure')} regulatory exposure. Blocker level is {block.get('blocker_level')}."
    def _confidence(self,s): return round(min(0.96,0.26+s['market_gap_confidence']*0.14+s['buyer_pull_score']*0.10+s['moat_score']*0.10+s['sector_regulatory_weight']*0.16+min(0.10,s['compliance_term_count']*0.025)+min(0.08,s['data_term_count']*0.012)),4)
    def _dom(self,sector,fallback): return {'climate_insurance':'insurance','defense_autonomy':'technology','healthcare_operations':'healthcare','industrial_supply_chain':'industrial','energy_infrastructure':'energy','financial_market_intelligence':'finance'}.get(sector,fallback or 'general')
    def _get(self,obj,*path):
        cur=obj
        for k in path:
            if not isinstance(cur,dict): return 0.0
            cur=cur.get(k,0.0)
        try:return float(cur or 0.0)
        except Exception:return 0.0
    def _dedupe(self,items,key):
        d={}
        for item in items:d[item.get(key,'')]=item
        return list(d.values())
