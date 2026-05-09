const ClaireIntelligenceFeed = (() => {
  const KEY = "claire_intelligence_feed_v17_55";

  const defaultState = () => ({
    version: "v17.55",
    insights: [],
    signals: [],
    narratives: [],
    notes: [],
    lastUpdatedAt: null,
  });

  function load() {
    try {
      const raw = localStorage.getItem(KEY);
      if (!raw) return defaultState();
      const parsed = JSON.parse(raw);
      return { ...defaultState(), ...parsed, version: "v17.55" };
    } catch (_) {
      return defaultState();
    }
  }

  function save(state) {
    const next = { ...state, version: "v17.55", lastUpdatedAt: new Date().toISOString() };
    localStorage.setItem(KEY, JSON.stringify(next, null, 2));
    return next;
  }

  function addInsight(input) {
    const state = load();
    const insight = {
      id: "insight_" + Date.now(),
      title: input.title || "Untitled insight",
      signal: input.signal || "",
      whyItMatters: input.whyItMatters || "",
      evidenceStatus: input.evidenceStatus || "Needs evidence",
      thesisStage: input.thesisStage || "Signal",
      confidence: input.confidence || "Unrated",
      createdAt: new Date().toISOString(),
    };
    const next = {
      ...state,
      insights: [insight, ...(state.insights || [])].slice(0, 100),
      signals: [insight, ...(state.signals || [])].slice(0, 100),
      narratives: [{
        id: "story_" + Date.now(),
        title: "Insight added",
        body: `${insight.title} moved into the signal stream as ${insight.thesisStage}.`,
        createdAt: new Date().toISOString(),
      }, ...(state.narratives || [])].slice(0, 100),
    };
    return save(next);
  }

  function addNote(text) {
    const state = load();
    const note = {
      id: "note_" + Date.now(),
      text: text || "Operator note",
      createdAt: new Date().toISOString(),
    };
    const next = {
      ...state,
      notes: [note, ...(state.notes || [])].slice(0, 100),
      narratives: [{
        id: "story_" + Date.now(),
        title: "Operator note added",
        body: note.text,
        createdAt: note.createdAt,
      }, ...(state.narratives || [])].slice(0, 100),
    };
    return save(next);
  }

  function seedDemoIfEmpty() {
    const state = load();
    if ((state.insights || []).length > 0) return state;
    return save({
      ...state,
      insights: [{
        id: "insight_seed_1",
        title: "No live insight stream yet",
        signal: "Claire is ready to collect signals once backend campaign output is wired.",
        whyItMatters: "The dashboard should show evolving intelligence, not only static pages.",
        evidenceStatus: "Awaiting live evidence",
        thesisStage: "System preparation",
        confidence: "Not rated",
        createdAt: new Date().toISOString(),
      }],
      narratives: [{
        id: "story_seed_1",
        title: "Narrative feed initialized",
        body: "The intelligence feed is ready. Add insights manually now; live campaign events should be wired next.",
        createdAt: new Date().toISOString(),
      }],
    });
  }

  function clear() {
    const next = defaultState();
    save(next);
    return next;
  }

  return { load, save, addInsight, addNote, seedDemoIfEmpty, clear };
})();
