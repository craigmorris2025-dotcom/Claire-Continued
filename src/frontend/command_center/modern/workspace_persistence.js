const ClaireWorkspace = (() => {
  const KEY = "claire_workspace_v17_54";

  const defaultState = () => ({
    version: "v17.54",
    discoveries: [],
    drafts: [],
    campaigns: [],
    activity: [],
    timeline: [],
    lastOpenedAt: null,
  });

  function load() {
    try {
      const raw = localStorage.getItem(KEY);
      if (!raw) return defaultState();
      const parsed = JSON.parse(raw);
      return { ...defaultState(), ...parsed, version: "v17.54" };
    } catch (_) {
      return defaultState();
    }
  }

  function save(state) {
    const next = { ...state, version: "v17.54", lastOpenedAt: new Date().toISOString() };
    localStorage.setItem(KEY, JSON.stringify(next, null, 2));
    return next;
  }

  function addActivity(state, type, title, detail) {
    const event = {
      id: "act_" + Date.now(),
      type,
      title,
      detail,
      createdAt: new Date().toISOString(),
    };
    const next = {
      ...state,
      activity: [event, ...(state.activity || [])].slice(0, 50),
      timeline: [event, ...(state.timeline || [])].slice(0, 100),
    };
    return save(next);
  }

  function saveDiscovery(input) {
    const state = load();
    const discovery = {
      id: "disc_" + Date.now(),
      title: input.title || "Untitled discovery",
      domain: input.domain || "General",
      horizon: input.horizon || "Now",
      question: input.question || "",
      status: "draft",
      createdAt: new Date().toISOString(),
    };
    const next = {
      ...state,
      discoveries: [discovery, ...(state.discoveries || [])],
      drafts: [discovery, ...(state.drafts || [])],
    };
    save(next);
    return addActivity(next, "discovery_saved", "Discovery draft saved", discovery.title);
  }

  function saveCampaignDraft(input) {
    const state = load();
    const campaign = {
      id: "camp_" + Date.now(),
      title: input.title || "Untitled campaign",
      cadence: input.cadence || "Manual",
      objective: input.objective || "",
      status: "draft",
      createdAt: new Date().toISOString(),
    };
    const next = {
      ...state,
      campaigns: [campaign, ...(state.campaigns || [])],
      drafts: [campaign, ...(state.drafts || [])],
    };
    save(next);
    return addActivity(next, "campaign_draft_saved", "Campaign draft saved", campaign.title);
  }

  function clearWorkspace() {
    const next = defaultState();
    save(next);
    return next;
  }

  return { load, save, addActivity, saveDiscovery, saveCampaignDraft, clearWorkspace };
})();
