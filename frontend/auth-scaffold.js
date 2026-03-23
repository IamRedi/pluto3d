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
