window.PLUTO_AUTH_STACK = {
  provider: "supabase",
  billing: "stripe",
  enabled: false
};

const AUTH_PREVIEW_STORAGE_KEY = "plutoAuthPreviewState";
const AUTH_USAGE_STORAGE_KEY = "plutoUsagePreviewState";

const AUTH_PREVIEW_DEFAULT = {
  mode: "guest",
  loggedIn: false,
  name: "Guest",
  email: "",
  planLabel: "Guest Beta"
};

const USAGE_LIMITS = {
  guest: {
    aiImage: 2,
    svgGeneration: 3,
    toyGeneration: 3,
    free3dGeneration: 1
  },
  free: {
    aiImage: 8,
    svgGeneration: 12,
    toyGeneration: 10,
    free3dGeneration: 4
  },
  premium: {
    aiImage: null,
    svgGeneration: null,
    toyGeneration: null,
    free3dGeneration: null
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
      planLabel: "Premium Preview"
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
      return {};
    }

    return JSON.parse(raw);
  }catch(error){
    console.warn("Failed to read usage preview state:", error);
    return {};
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

function getUsageLimit(featureKey){
  const mode = getCurrentUsageBucket();
  return USAGE_LIMITS[mode]?.[featureKey] ?? null;
}

function getUsageCount(featureKey){
  const state = getUsagePreviewState();
  return state[featureKey] || 0;
}

function getUsageSnapshot(){
  return {
    aiImage: getUsageCount("aiImage"),
    svgGeneration: getUsageCount("svgGeneration"),
    toyGeneration: getUsageCount("toyGeneration"),
    free3dGeneration: getUsageCount("free3dGeneration")
  };
}

function canUseFeature(featureKey){
  const limit = getUsageLimit(featureKey);
  if(limit === null){
    return true;
  }

  return getUsageCount(featureKey) < limit;
}

function incrementUsage(featureKey){
  const state = getUsagePreviewState();
  state[featureKey] = (state[featureKey] || 0) + 1;
  saveUsagePreviewState(state);

  if(typeof syncAuthPreviewUI === "function"){
    syncAuthPreviewUI();
  }
}

function resetUsagePreview(){
  saveUsagePreviewState({});

  if(typeof syncAuthPreviewUI === "function"){
    syncAuthPreviewUI();
  }
}

function shouldShowSponsorPreview(){
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
window.getUsageCount = getUsageCount;
window.getUsageSnapshot = getUsageSnapshot;
window.canUseFeature = canUseFeature;
window.incrementUsage = incrementUsage;
window.resetUsagePreview = resetUsagePreview;
window.shouldShowSponsorPreview = shouldShowSponsorPreview;
window.showSponsorPreview = showSponsorPreview;
