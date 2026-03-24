(function(){
const DEFAULT_RUNTIME = {
  provider: "supabase",
  configured: false,
  sdkReady: false,
  configLoaded: false,
  clientReady: false,
  statusLabel: "Setup Needed",
  detail: "Create Supabase first, then add frontend/auth-config.js.",
  source: "preview"
};

const DEFAULT_LIVE_STATE = {
  enabled: false,
  loading: true,
  mode: "guest",
  loggedIn: false,
  name: "Guest",
  email: "",
  planLabel: "Guest",
  session: null,
  user: null
};

let supabaseClient = null;

async function fetchBackendAccountState(session){
  if(!session?.access_token || typeof API_BASE === "undefined"){
    return null;
  }

  try{
    const response = await fetch(`${API_BASE}/api/account/me`, {
      headers: {
        Authorization: `Bearer ${session.access_token}`
      }
    });

    if(!response.ok){
      return null;
    }

    return await response.json();
  }catch(error){
    console.warn("Backend account sync failed:", error);
    return null;
  }
}

function getConfig(){
  return window.PLUTO_AUTH_CONFIG || null;
}

function getPublicKey(config){
  return config?.supabasePublishableKey || config?.supabaseAnonKey || "";
}

function hasConfig(){
  const config = getConfig();
  return Boolean(config?.supabaseUrl && getPublicKey(config));
}

function setLiveAuthState(partial){
  window.PLUTO_LIVE_AUTH_STATE = {
    ...window.PLUTO_LIVE_AUTH_STATE,
    ...partial
  };

  if(typeof window.syncAuthPreviewUI === "function"){
    window.syncAuthPreviewUI();
  }
}

function getLiveAuthState(){
  return window.PLUTO_LIVE_AUTH_STATE || { ...DEFAULT_LIVE_STATE };
}

function derivePlan(user){
  const appPlan = user?.app_metadata?.plan;
  const userPlan = user?.user_metadata?.plan;
  const plan = appPlan || userPlan || "free";

  if(plan === "premium"){
    return {
      mode: "premium",
      planLabel: "Premium",
      name: user?.user_metadata?.full_name || user?.user_metadata?.name || "Pluto Premium"
    };
  }

  return {
    mode: "free",
    planLabel: "Free Account",
    name: user?.user_metadata?.full_name || user?.user_metadata?.name || "Pluto Creator"
  };
}

function buildLiveStateFromSession(session){
  if(!session?.user){
    return { ...DEFAULT_LIVE_STATE, enabled: true, loading: false };
  }

  const plan = derivePlan(session.user);

  return {
    enabled: true,
    loading: false,
    mode: plan.mode,
    loggedIn: true,
    name: plan.name,
    email: session.user.email || "",
    planLabel: plan.planLabel,
    session,
    user: session.user
  };
}

function mergeBackendAccountState(liveState, backendState){
  if(!backendState?.authenticated){
    return liveState;
  }

  const user = backendState.user || {};
  const backendPlan = backendState.plan === "premium" ? "premium" : "free";

  return {
    ...liveState,
    mode: backendPlan,
    planLabel: backendPlan === "premium" ? "Premium" : "Free Account",
    name: user.name || liveState.name,
    email: user.email || liveState.email
  };
}

function buildRuntimeState(){
  const configReady = hasConfig();
  const sdkReady = Boolean(window.supabase?.createClient);
  const clientReady = Boolean(supabaseClient);

  if(configReady && sdkReady && clientReady){
    return {
      provider: "supabase",
      configured: true,
      sdkReady: true,
      configLoaded: true,
      clientReady: true,
      statusLabel: "Live Auth Ready",
      detail: "Supabase config and client are active. Login can now use real session state.",
      source: "runtime"
    };
  }

  if(configReady && sdkReady){
    return {
      provider: "supabase",
      configured: true,
      sdkReady: true,
      configLoaded: true,
      clientReady: false,
      statusLabel: "Client Wiring",
      detail: "Supabase config is loaded and the SDK is available. Final client wiring is in progress.",
      source: "runtime"
    };
  }

  if(configReady){
    return {
      provider: "supabase",
      configured: true,
      sdkReady: false,
      configLoaded: true,
      clientReady: false,
      statusLabel: "Config Ready",
      detail: "Supabase keys are present. The auth SDK is still loading.",
      source: "runtime"
    };
  }

  return { ...DEFAULT_RUNTIME };
}

function refreshAuthRuntimeStatus(){
  window.PLUTO_AUTH_RUNTIME = buildRuntimeState();

  if(typeof window.syncAuthPreviewUI === "function"){
    window.syncAuthPreviewUI();
  }

  return window.PLUTO_AUTH_RUNTIME;
}

function getAuthRuntimeStatus(){
  return window.PLUTO_AUTH_RUNTIME || refreshAuthRuntimeStatus();
}

function ensureAuthConfigScript(){
  if(document.querySelector('script[data-auth-config="true"]')){
    return;
  }

  const script = document.createElement("script");
  script.src = "auth-config.js";
  script.dataset.authConfig = "true";
  script.async = true;
  script.onload = () => {
    refreshAuthRuntimeStatus();
    ensureSupabaseSdk();
  };
  script.onerror = () => refreshAuthRuntimeStatus();
  document.head.appendChild(script);
}

function ensureSupabaseSdk(){
  if(window.supabase?.createClient){
    initializeSupabaseClient();
    return;
  }

  if(document.querySelector('script[data-auth-sdk="true"]')){
    return;
  }

  const script = document.createElement("script");
  script.src = "https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2";
  script.dataset.authSdk = "true";
  script.async = true;
  script.onload = () => initializeSupabaseClient();
  script.onerror = () => refreshAuthRuntimeStatus();
  document.head.appendChild(script);
}

async function initializeSupabaseClient(){
  const config = getConfig();
  const publicKey = getPublicKey(config);

  if(!config?.supabaseUrl || !publicKey || !window.supabase?.createClient){
    refreshAuthRuntimeStatus();
    return;
  }

  if(!supabaseClient){
    supabaseClient = window.supabase.createClient(config.supabaseUrl, publicKey);
  }

  setLiveAuthState({ enabled: true, loading: true });
  refreshAuthRuntimeStatus();

  const { data } = await supabaseClient.auth.getSession();
  const firstSession = data?.session || null;
  const firstState = buildLiveStateFromSession(firstSession);
  const firstBackendState = await fetchBackendAccountState(firstSession);
  setLiveAuthState(mergeBackendAccountState(firstState, firstBackendState));

  supabaseClient.auth.onAuthStateChange(async (_event, session) => {
    const nextState = buildLiveStateFromSession(session);
    const backendState = await fetchBackendAccountState(session);
    setLiveAuthState(mergeBackendAccountState(nextState, backendState));
  });

  refreshAuthRuntimeStatus();
}

function getRedirectUrl(){
  return `${window.location.origin}${window.location.pathname}`;
}

function authNotReadyMessage(){
  const runtime = getAuthRuntimeStatus();
  return runtime.configured
    ? "Supabase config is ready, but the auth client is not fully loaded yet. Refresh the page once."
    : "Supabase is not configured yet. Add values to frontend/auth-config.js first.";
}

async function signInWithGoogleReal(){
  if(!supabaseClient){
    alert(authNotReadyMessage());
    return;
  }

  const { error } = await supabaseClient.auth.signInWithOAuth({
    provider: "google",
    options: {
      redirectTo: getRedirectUrl()
    }
  });

  if(error){
    alert(error.message || "Google sign-in failed.");
  }
}

async function signInWithEmailReal(email, password){
  if(!supabaseClient){
    alert(authNotReadyMessage());
    return;
  }

  if(!email || !password){
    alert("Write email and password first.");
    return;
  }

  const { error } = await supabaseClient.auth.signInWithPassword({
    email,
    password
  });

  if(error){
    alert(error.message || "Email sign-in failed.");
  }
}

async function signUpWithEmailReal(email, password){
  if(!supabaseClient){
    alert(authNotReadyMessage());
    return;
  }

  if(!email || !password){
    alert("Write email and password first.");
    return;
  }

  const { error } = await supabaseClient.auth.signUp({
    email,
    password,
    options: {
      emailRedirectTo: getRedirectUrl()
    }
  });

  if(error){
    alert(error.message || "Email sign-up failed.");
    return;
  }

  alert("Signup request sent. If email confirmation is enabled, check your inbox.");
}

async function signOutReal(){
  if(!supabaseClient){
    alert(authNotReadyMessage());
    return;
  }

  const { error } = await supabaseClient.auth.signOut();

  if(error){
    alert(error.message || "Sign out failed.");
  }
}

window.PLUTO_AUTH_RUNTIME = { ...DEFAULT_RUNTIME };
window.PLUTO_LIVE_AUTH_STATE = { ...DEFAULT_LIVE_STATE };
window.refreshAuthRuntimeStatus = refreshAuthRuntimeStatus;
window.getAuthRuntimeStatus = getAuthRuntimeStatus;
window.getLiveAuthState = getLiveAuthState;
window.signInWithGoogleReal = signInWithGoogleReal;
window.signInWithEmailReal = signInWithEmailReal;
window.signUpWithEmailReal = signUpWithEmailReal;
window.signOutReal = signOutReal;

if(document.readyState === "loading"){
  document.addEventListener("DOMContentLoaded", () => {
    ensureAuthConfigScript();
    refreshAuthRuntimeStatus();
    ensureSupabaseSdk();
  });
}else{
  ensureAuthConfigScript();
  refreshAuthRuntimeStatus();
  ensureSupabaseSdk();
}
})();
