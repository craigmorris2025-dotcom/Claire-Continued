# Deal / Exit Modeling

**Status:** success

## Exit Readiness

```json
{
  "missing_proof": [
    "documented mitigation of human-review / deployment-control blocker",
    "stronger evidence of proprietary data loops and workflow switching costs",
    "quantified buyer ROI case"
  ],
  "readiness_drivers": [
    "portfolio score available",
    "acquirer matching available",
    "business model available",
    "risk/regulation profile available",
    "strong top acquirer fit",
    "readiness is conditional on blocker mitigation"
  ],
  "score": 0.5084,
  "state": "exit_candidate_with_conditions"
}
```

## Strategic Fit

```json
{
  "fit_drivers": [
    "large acquirer universe",
    "high top-acquirer match score",
    "deal requires deployment-control proof"
  ],
  "level": "moderate",
  "score": 0.7351,
  "strategic_rationale": "defense autonomy has deep strategic-buyer coverage, top acquirer score of 0.9800, buyer pull of 0.5790, and value capture of 0.5354."
}
```

## Valuation Logic

```json
{
  "discount_factors": [
    "conditional deployment blocker",
    "moat still moderate rather than strong",
    "enterprise sales and implementation burden",
    "operational risk review required"
  ],
  "primary_value_drivers": [
    "strategic buyer fit",
    "recurring revenue potential",
    "buyer ROI",
    "data advantage",
    "platform/category formation",
    "primary moat: integration_depth"
  ],
  "upside_cases": [
    "paid pilots convert to recurring enterprise subscriptions",
    "modules expand across buyer workflows",
    "proprietary benchmarks become premium data products",
    "strategic buyer uses acquisition to fill category gap",
    "multiple strategic buyer categories create deal tension"
  ],
  "valuation_methods": [
    {
      "method": "strategic acquisition premium",
      "priority": "high",
      "use_case": "best when acquirer product roadmap or category gap is directly addressed"
    },
    {
      "method": "ARR / recurring revenue multiple",
      "priority": "high",
      "use_case": "best once subscription revenue is validated"
    },
    {
      "method": "ROI-based strategic value",
      "priority": "high",
      "use_case": "best when buyer can quantify avoided loss, disruption, risk, or cost"
    },
    {
      "method": "technology and data-asset value",
      "priority": "medium",
      "use_case": "best when proprietary datasets, benchmarks, and integrations are proven"
    }
  ],
  "valuation_signal": {
    "score": 0.5694,
    "strength": "early_option_value"
  }
}
```

## Recommended Next Actions

```json
[
  {
    "action": "build acquirer-specific strategic rationale",
    "priority": "high",
    "purpose": "translate Claire output into buyer-specific deal logic"
  },
  {
    "action": "prepare diligence evidence pack",
    "priority": "high",
    "purpose": "organize ROI proof, technical architecture, data rights, model validation, and risk controls"
  },
  {
    "action": "model pilot-to-enterprise conversion economics",
    "priority": "high",
    "purpose": "support valuation and commercial readiness with concrete revenue milestones"
  },
  {
    "action": "map deal path options",
    "priority": "medium",
    "purpose": "compare acquisition, commercial partnership, licensing, and growth-financing paths"
  },
  {
    "action": "resolve deployment-control blocker before outreach",
    "priority": "critical",
    "purpose": "prevent risk-control questions from weakening deal leverage"
  },
  {
    "action": "close missing proof points",
    "priority": "high",
    "purpose": "move from candidate to exit-ready package"
  }
]
```

## Additional Fields

### Domain

```json
"technology"
```

### Sector

```json
"defense_autonomy"
```

### Buyer Universe

```json
{
  "acquirer_categories": [
    "defense primes",
    "defense technology companies",
    "aerospace companies",
    "secure command platforms"
  ],
  "acquirer_count": 8,
  "average_top_5_score": 0.9386,
  "buyer_types": [
    {
      "priority": "medium",
      "strategic_reason": "can acquire the opportunity for product expansion and data advantage",
      "type": "strategic technology buyers"
    }
  ],
  "depth": "deep",
  "top_match_score": 0.98,
  "top_matches": [
    {
      "fit_dimensions": {
        "buyer_segment_fit": 0.035,
        "category_alignment": 0.11,
        "focus_alignment": 0.072,
        "sector_fit": 0.1,
        "strategic_pressure": 0.0188
      },
      "focus": [
        "aerospace",
        "autonomous platforms",
        "surveillance",
        "command systems"
      ],
      "match_score": 0.98,
      "matched_signals": [
        "aerospace",
        
... [truncated]
```

### Deal Paths

```json
[
  {
    "best_for": "strategic platforms seeking product/category expansion",
    "fit": 0.6716,
    "path": "strategic acquisition",
    "priority": "high",
    "trigger": "validated ROI and defensibility"
  },
  {
    "best_for": "strategic buyers needing proof",
    "fit": 0.6316,
    "path": "commercial partnership to acquisition",
    "priority": "medium",
    "trigger": "partner integration and repeated buyer demand"
  },
  {
    "best_for": "platforms wanting embedded intelligence",
    "fit": 0.6016,
    "path": "platform licensing / OEM",
    "priority": "medium",
    "trigger": "stable APIs and modules"
  },
  {
    "best_for": "scaling adoption before strategic exit",
    "fit": 0.5716,
    "path": "growth financing before exit",
    "priority": "medium",
    "trigger": "repeatable sales motion"
  }
]
```

### Diligence Requirements

```json
[
  {
    "priority": "high",
    "requirement": "customer ROI evidence",
    "why": "Buyers need proof that the system reduces cost, risk, loss, or cycle time."
  },
  {
    "priority": "high",
    "requirement": "technical architecture and integration review",
    "why": "Strategic buyers will review scalability, APIs, integration, and maintainability."
  },
  {
    "priority": "high",
    "requirement": "model performance validation",
    "why": "Forecasting and recommendation quality must be proven with backtests and pilots."
  },
  {
    "priority": "high",
    "requirement": "data rights and governance review",
    "why": "Data-loop defensibility depends on clear rights, lineage, permissions, and controls."
  },
  {
    "priority": "high",
    "requirement": "commercial model validation",
    "why": "Pricing must be supported by willingness-to-pay and expansion proof."
  },
  {
   
... [truncated]
```

### Risk Adjustments

```json
[
  {
    "adjustment": "conditional deployment discount",
    "impact": "Strategic buyers may require risk controls and human-review validation before premium valuation.",
    "mitigation": "Package blocker mitigation as diligence evidence.",
    "severity": "medium"
  },
  {
    "adjustment": "moat maturity discount",
    "impact": "Moderate moat may reduce premium unless data loops and workflow dependency are proven.",
    "mitigation": "Validate repeat usage, proprietary benchmarks, and integration depth.",
    "severity": "medium"
  }
]
```

### Negotiation Levers

```json
[
  {
    "lever": "buyer pain and ROI",
    "priority": "high",
    "use": "Anchor valuation to measurable buyer value."
  },
  {
    "lever": "data and workflow moat",
    "priority": "high",
    "use": "Position defensibility around proprietary data and recurring workflow use."
  },
  {
    "lever": "multi-acquirer tension",
    "priority": "high",
    "use": "Create tension across strategic buyer categories."
  },
  {
    "lever": "recurring revenue path",
    "priority": "high",
    "use": "Emphasize subscriptions, module expansion, and account growth."
  }
]
```

### Exit Narrative

```json
{
  "acquirer_pitch": "Acquire or partner to own a predictive intelligence layer with workflow, data, and module expansion potential.",
  "deal_story": "The deal story should lead with validated buyer pain, measurable ROI, workflow embedding, proprietary data loops, and a clear path from pilots to platform expansion.",
  "one_liner": "A defense autonomy opportunity with moderate strategic fit, deep buyer coverage, and early_option_value valuation signal."
}
```

### Deal Exit Thesis

```json
"defense autonomy is a exit_candidate_with_conditions with moderate strategic fit and early_option_value valuation signal."
```

### Confidence

```json
0.6778
```
