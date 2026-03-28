window.PLUTO_AUTH_STACK = {
  provider: "supabase",
  billing: "stripe",
  enabled: false
};

const AUTH_PREVIEW_STORAGE_KEY = "plutoAuthPreviewState";
const AUTH_USAGE_STORAGE_KEY = "plutoUsagePreviewState";
const IS_LOCAL_TEST_MODE = ["127.0.0.1", "localhost"].includes(window.location.hostname);

const AUTH_PREVIEW_DEFAULT = {
  mode: "guest",
  loggedIn: false,
  name: "Guest",
  email: "",
  planLabel: "Guest"
};

const USAGE_RULES = {
  guest: {
    aiImage: { limit: 2, period: "day" },
    svgGeneration: { limit: 1, period: "day" },
    toyGeneration: { limit: 3, period: "day" },
    free3dGeneration: { limit: 1, period: "day" },
    reliefStlGeneration: { limit: 0, period: "week" },
    real3dGeneration: { limit: 0, period: "month" }
  },
  free: {
    aiImage: { limit: 10, period: "week" },
    svgGeneration: { limit: null, period: null },
    toyGeneration: { limit: 10, period: "week" },
    free3dGeneration: { limit: 3, period: "week" },
    reliefStlGeneration: { limit: 5, period: "week" },
    real3dGeneration: { limit: 0, period: "month" }
  },
  premium: {
    aiImage: { limit: 50, period: "month" },
    svgGeneration: { limit: null, period: null },
    toyGeneration: { limit: null, period: null },
    free3dGeneration: { limit: null, period: null },
    reliefStlGeneration: { limit: null, period: null },
    real3dGeneration: { limit: 10, period: "month" }
  }
};

const DOWNLOAD_POLICY_RULES = {
  test3dModelDownload: {
    guest: "hidden",
    free: "credit",
    premium: "allow"
  }
};

const SPONSOR_PREVIEW_COPY = {
  aiImage: {
    kicker: "Sponsored Generation",
    title: "Free AI image slot in progress",
    copy: "Future free users can see a sponsor card or upgrade message here while generation runs in the background."
  },
  svgGeneration: {
    kicker: "Vector Sponsor Slot",
    title: "Preparing SVG output",
    copy: "This is where a clean sponsor panel, partner note, or upgrade reminder can appear for free users."
  },
  toyGeneration: {
    kicker: "Toy Studio Sponsor",
    title: "Loading toy generation",
    copy: "A short branded wait state here can help cover cost while keeping the experience premium-looking."
  },
  free3dGeneration: {
    kicker: "3D Preview Sponsor",
    title: "Creating print-ready preview",
    copy: "3D test generation can later show a partner card, countdown, or premium upsell while processing."
  }
};

function buildAuthPreviewState(mode){
  if(mode === "premium"){
    return {
      mode: "premium",
      loggedIn: true,
      name: "Pluto Premium",
      email: "premium@pluto3d.app",
      planLabel: "Premium"
    };
  }

  if(mode === "free"){
    return {
      mode: "free",
      loggedIn: true,
      name: "Pluto Creator",
      email: "creator@pluto3d.app",
      planLabel: "Free Account"
    };
  }

  return { ...AUTH_PREVIEW_DEFAULT };
}

function getAuthPreviewState(){
  const liveState = window.PLUTO_LIVE_AUTH_STATE;
  if(liveState?.enabled && !liveState.loading){
    return {
      mode: liveState.mode || "guest",
      loggedIn: Boolean(liveState.loggedIn),
      name: liveState.name || "Guest",
      email: liveState.email || "",
      planLabel: liveState.planLabel || "Guest"
    };
  }

  try{
    const raw = localStorage.getItem(AUTH_PREVIEW_STORAGE_KEY);
    if(!raw){
      return { ...AUTH_PREVIEW_DEFAULT };
    }

    return {
      ...AUTH_PREVIEW_DEFAULT,
      ...JSON.parse(raw)
    };
  }catch(error){
    console.warn("Failed to read auth preview state:", error);
    return { ...AUTH_PREVIEW_DEFAULT };
  }
}

function getUsagePreviewState(){
  try{
    const raw = localStorage.getItem(AUTH_USAGE_STORAGE_KEY);
    if(!raw){
      return {
        counters: {},
        credits: {}
      };
    }

    const parsed = JSON.parse(raw);
    if(parsed && typeof parsed === "object" && !Array.isArray(parsed)){
      if(parsed.counters || parsed.credits){
        return {
          counters: parsed.counters || {},
          credits: parsed.credits || {}
        };
      }

      const migratedCounters = Object.entries(parsed).reduce((accumulator, [key, value]) => {
        if(typeof value !== "number"){
          return accumulator;
        }

        const rule = getUsageRule(key, { ignoreLocalTestMode: true });
        accumulator[key] = {
          count: Number(value) || 0,
          windowKey: getUsageWindowKey(rule?.period)
        };
        return accumulator;
      }, {});

      return {
        counters: migratedCounters,
        credits: {}
      };
    }

    return {
      counters: {},
      credits: {}
    };
  }catch(error){
    console.warn("Failed to read usage preview state:", error);
    return {
      counters: {},
      credits: {}
    };
  }
}

function saveUsagePreviewState(state){
  localStorage.setItem(AUTH_USAGE_STORAGE_KEY, JSON.stringify(state));
  window.PLUTO_USAGE_PREVIEW = state;
}

function getCurrentUsageBucket(){
  const authState = getAuthPreviewState();
  return authState.mode || "guest";
}

function getBackendUsageSummary(){
  return (!IS_LOCAL_TEST_MODE && window.PLUTO_ACCOUNT_USAGE) ? window.PLUTO_ACCOUNT_USAGE : null;
}

function getUsageRule(featureKey, options = {}){
  const backendUsage = (!options.ignoreLocalTestMode && getBackendUsageSummary()) || null;
  if(backendUsage?.rules?.[featureKey]){
    return {
      limit: backendUsage.rules[featureKey].limit ?? null,
      period: backendUsage.rules[featureKey].period ?? null
    };
  }

  if(IS_LOCAL_TEST_MODE && !options.ignoreLocalTestMode){
    return {
      limit: null,
      period: null
    };
  }

  const mode = getCurrentUsageBucket();
  return USAGE_RULES[mode]?.[featureKey] ?? {
    limit: null,
    period: null
  };
}

function getUsageWindowKey(period){
  if(!period){
    return "unlimited";
  }

  const now = new Date();
  const year = now.getFullYear();
  const month = String(now.getMonth() + 1).padStart(2, "0");
  const day = String(now.getDate()).padStart(2, "0");

  if(period === "day"){
    return `${year}-${month}-${day}`;
  }

  if(period === "month"){
    return `${year}-${month}`;
  }

  if(period === "week"){
    const start = new Date(now);
    const weekday = start.getDay();
    const delta = weekday === 0 ? -6 : 1 - weekday;
    start.setHours(0, 0, 0, 0);
    start.setDate(start.getDate() + delta);

    const weekYear = start.getFullYear();
    const weekMonth = String(start.getMonth() + 1).padStart(2, "0");
    const weekDay = String(start.getDate()).padStart(2, "0");
    return `${weekYear}-${weekMonth}-${weekDay}`;
  }

  return "unlimited";
}

function getUsageEntryState(collectionKey, featureKey, options = {}){
  const state = getUsagePreviewState();
  const collection = state[collectionKey] || {};
  const existingEntry = collection[featureKey];
  const rule = getUsageRule(featureKey, { ignoreLocalTestMode: options.ignoreLocalTestMode === true });
  const nextWindowKey = getUsageWindowKey(rule?.period);
  const normalizedEntry = existingEntry && typeof existingEntry === "object"
    ? {
        count: Number(existingEntry.count) || 0,
        windowKey: existingEntry.windowKey || nextWindowKey
      }
    : {
        count: typeof existingEntry === "number" ? Number(existingEntry) || 0 : 0,
        windowKey: nextWindowKey
      };

  if(rule?.period && normalizedEntry.windowKey !== nextWindowKey){
    normalizedEntry.count = 0;
    normalizedEntry.windowKey = nextWindowKey;
    collection[featureKey] = normalizedEntry;
    state[collectionKey] = collection;
    saveUsagePreviewState(state);
  }

  return {
    state,
    collection,
    entry: normalizedEntry
  };
}

function getUsageLimit(featureKey){
  return getUsageRule(featureKey).limit;
}

function getUsagePeriod(featureKey){
  return getUsageRule(featureKey).period;
}

function getUsageCount(featureKey){
  const backendUsage = getBackendUsageSummary();
  if(backendUsage?.rules?.[featureKey]){
    return Number(backendUsage.rules[featureKey].used || 0);
  }

  const { entry } = getUsageEntryState("counters", featureKey);
  return entry.count || 0;
}

function getUsageCreditCount(featureKey){
  const backendUsage = getBackendUsageSummary();
  if(backendUsage?.credits && Object.prototype.hasOwnProperty.call(backendUsage.credits, featureKey)){
    return Number(backendUsage.credits[featureKey] || 0);
  }

  const { entry } = getUsageEntryState("credits", featureKey);
  return entry.count || 0;
}

function getUsageSnapshot(){
  return {
    aiImage: getUsageCount("aiImage"),
    svgGeneration: getUsageCount("svgGeneration"),
    toyGeneration: getUsageCount("toyGeneration"),
    free3dGeneration: getUsageCount("free3dGeneration"),
    reliefStlGeneration: getUsageCount("reliefStlGeneration"),
    real3dGeneration: getUsageCount("real3dGeneration")
  };
}

function canUseFeature(featureKey){
  const rule = getUsageRule(featureKey);
  const limit = rule.limit;
  if(limit === null){
    return true;
  }

  if(limit <= 0){
    return false;
  }

  return getUsageCount(featureKey) < limit;
}

function incrementUsage(featureKey){
  const { state, collection, entry } = getUsageEntryState("counters", featureKey);
  collection[featureKey] = {
    count: (entry.count || 0) + 1,
    windowKey: entry.windowKey
  };
  state.counters = collection;
  saveUsagePreviewState(state);

  if(typeof syncAuthPreviewUI === "function"){
    syncAuthPreviewUI();
  }
}

function grantUsageCredit(featureKey, amount = 1){
  const { state, collection, entry } = getUsageEntryState("credits", featureKey);
  collection[featureKey] = {
    count: Math.max(0, (entry.count || 0) + amount),
    windowKey: entry.windowKey
  };
  state.credits = collection;
  saveUsagePreviewState(state);
}

function consumeUsageCredit(featureKey, amount = 1){
  if(IS_LOCAL_TEST_MODE){
    return {
      allowed: true,
      remaining: null
    };
  }

  const { state, collection, entry } = getUsageEntryState("credits", featureKey);
  const available = entry.count || 0;
  if(available < amount){
    return {
      allowed: false,
      remaining: available
    };
  }

  collection[featureKey] = {
    count: Math.max(0, available - amount),
    windowKey: entry.windowKey
  };
  state.credits = collection;
  saveUsagePreviewState(state);

  if(typeof syncAuthPreviewUI === "function"){
    syncAuthPreviewUI();
  }

  return {
    allowed: true,
    remaining: collection[featureKey].count
  };
}

function getViewerDownloadAccess(policyKey){
  if(!policyKey || IS_LOCAL_TEST_MODE){
    return {
      visible: true,
      allowed: true,
      reason: ""
    };
  }

  const mode = getCurrentUsageBucket();
  const policy = DOWNLOAD_POLICY_RULES[policyKey]?.[mode] || "allow";

  if(policy === "hidden"){
    return {
      visible: false,
      allowed: false,
      reason: "Sign in to download this test model."
    };
  }

  if(policy === "credit"){
    const credits = getUsageCreditCount("test3dDownloadCredit");
    return {
      visible: true,
      allowed: credits > 0,
      reason: credits > 0 ? "" : "Your test-model download credit has already been used."
    };
  }

  return {
    visible: true,
    allowed: true,
    reason: ""
  };
}

function grantViewerDownloadAccess(policyKey, amount = 1){
  if(IS_LOCAL_TEST_MODE || !policyKey || getBackendUsageSummary()){
    return;
  }

  const mode = getCurrentUsageBucket();
  if(policyKey === "test3dModelDownload" && mode === "free"){
    grantUsageCredit("test3dDownloadCredit", amount);
  }
}

async function consumeViewerDownloadAccess(policyKey){
  const access = getViewerDownloadAccess(policyKey);
  if(!access.visible || !access.allowed){
    return access;
  }

  if(IS_LOCAL_TEST_MODE || !policyKey){
    return access;
  }

  if(getBackendUsageSummary()){
    if(policyKey === "test3dModelDownload" && typeof window.consumeBackendUsageCredit === "function"){
      try{
        const response = await window.consumeBackendUsageCredit("test3dDownloadCredit", { amount: 1 });
        const remaining = Number(response?.usage?.credits?.test3dDownloadCredit ?? 0);
        return {
          visible: remaining > 0,
          allowed: true,
          reason: "",
          remaining
        };
      }catch(error){
        return {
          visible: false,
          allowed: false,
          reason: error.message || "Your test-model download credit has already been used."
        };
      }
    }

    return access;
  }

  const mode = getCurrentUsageBucket();
  if(policyKey === "test3dModelDownload" && mode === "free"){
    const result = consumeUsageCredit("test3dDownloadCredit", 1);
    return {
      visible: result.allowed ? true : false,
      allowed: result.allowed,
      reason: result.allowed ? "" : "Your test-model download credit has already been used."
    };
  }

  return access;
}

function resetUsagePreview(){
  saveUsagePreviewState({
    counters: {},
    credits: {}
  });

  if(typeof syncAuthPreviewUI === "function"){
    syncAuthPreviewUI();
  }
}

function shouldShowSponsorPreview(){
  if(IS_LOCAL_TEST_MODE){
    return false;
  }

  return getAuthPreviewState().mode !== "premium";
}

function getSponsorPreviewConfig(featureKey){
  return SPONSOR_PREVIEW_COPY[featureKey] || {
    kicker: "Sponsored Wait State",
    title: "Preparing your result",
    copy: "This is a preview of a future sponsor or ad-supported loading state for free users."
  };
}

function showSponsorPreview(featureKey){
  if(!shouldShowSponsorPreview()){
    return Promise.resolve();
  }

  const overlay = document.getElementById("sponsorPreviewOverlay");
  const kicker = document.getElementById("sponsorPreviewKicker");
  const title = document.getElementById("sponsorPreviewTitle");
  const copy = document.getElementById("sponsorPreviewCopy");

  if(!overlay || !kicker || !title || !copy){
    return Promise.resolve();
  }

  const config = getSponsorPreviewConfig(featureKey);
  kicker.textContent = config.kicker;
  title.textContent = config.title;
  copy.textContent = config.copy;
  overlay.classList.remove("hidden");

  return new Promise((resolve) => {
    window.clearTimeout(window.__plutoSponsorTimer);
    window.__plutoSponsorTimer = window.setTimeout(() => {
      overlay.classList.add("hidden");
      resolve();
    }, 1800);
  });
}

function setAuthPreviewState(mode){
  const nextState = buildAuthPreviewState(mode);
  localStorage.setItem(AUTH_PREVIEW_STORAGE_KEY, JSON.stringify(nextState));
  window.PLUTO_AUTH_PREVIEW = nextState;

  if(typeof syncAuthPreviewUI === "function"){
    syncAuthPreviewUI();
  }
}

function signInPreview(mode){
  setAuthPreviewState(mode || "free");
}

function signOutPreview(){
  setAuthPreviewState("guest");
}

window.PLUTO_AUTH_PREVIEW = getAuthPreviewState();
window.PLUTO_USAGE_PREVIEW = getUsagePreviewState();
window.getAuthPreviewState = getAuthPreviewState;
window.setAuthPreviewState = setAuthPreviewState;
window.signInPreview = signInPreview;
window.signOutPreview = signOutPreview;
window.getUsagePreviewState = getUsagePreviewState;
window.getUsageLimit = getUsageLimit;
window.getUsagePeriod = getUsagePeriod;
window.getUsageRule = getUsageRule;
window.getUsageCount = getUsageCount;
window.getUsageSnapshot = getUsageSnapshot;
window.canUseFeature = canUseFeature;
window.incrementUsage = incrementUsage;
window.grantViewerDownloadAccess = grantViewerDownloadAccess;
window.getViewerDownloadAccess = getViewerDownloadAccess;
window.consumeViewerDownloadAccess = consumeViewerDownloadAccess;
window.resetUsagePreview = resetUsagePreview;
window.shouldShowSponsorPreview = shouldShowSponsorPreview;
window.showSponsorPreview = showSponsorPreview;
window.isLocalTestMode = () => IS_LOCAL_TEST_MODE;
