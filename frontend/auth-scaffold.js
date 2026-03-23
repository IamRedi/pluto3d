window.PLUTO_AUTH_STACK = {
  provider: "supabase",
  billing: "stripe",
  enabled: false
};

const AUTH_PREVIEW_STORAGE_KEY = "plutoAuthPreviewState";

const AUTH_PREVIEW_DEFAULT = {
  mode: "guest",
  loggedIn: false,
  name: "Guest",
  email: "",
  planLabel: "Guest Beta"
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
window.getAuthPreviewState = getAuthPreviewState;
window.setAuthPreviewState = setAuthPreviewState;
window.signInPreview = signInPreview;
window.signOutPreview = signOutPreview;
