(function(){
const DEFAULT_RUNTIME = {
  provider: "supabase",
  configured: false,
  sdkReady: false,
  configLoaded: false,
  clientReady: false,
  statusLabel: "Setup Needed",
  detail: "Create Supabase first, then add Supabase values to frontend/app-config.js.",
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
  backendPlan: "guest",
  planSource: "guest",
  planReason: "",
  subscription: null,
  activity: null,
  session: null,
  user: null
};

let supabaseClient = null;
const GUEST_USAGE_KEY_STORAGE = "plutoGuestUsageKey";
let activityHeartbeatTimer = null;
let activityHeartbeatSession = null;
const ACTIVITY_HEARTBEAT_MS = 60000;
const ACTIVITY_HEARTBEAT_SECONDS = 60;
const GUEST_ACTIVITY_KEY_STORAGE = "plutoGuestActivityKey";

function getGuestActivityKey(){
  try{
    const existing = localStorage.getItem(GUEST_ACTIVITY_KEY_STORAGE);
    if(existing){
      return existing;
    }
    const nextValue = `guest-${crypto.randomUUID()}`;
    localStorage.setItem(GUEST_ACTIVITY_KEY_STORAGE, nextValue);
    return nextValue;
  }catch(error){
    return `guest-fallback-${Date.now()}`;
  }
}

function getApiBaseUrl(){
  return window.PLUTO_API_BASE || (typeof API_BASE !== "undefined" ? API_BASE : "");
}

function getGuestUsageKey(){
  try{
    const existing = localStorage.getItem(GUEST_USAGE_KEY_STORAGE);
    if(existing){
      return existing;
    }

    const nextValue = `guest-${crypto.randomUUID()}`;
    localStorage.setItem(GUEST_USAGE_KEY_STORAGE, nextValue);
    return nextValue;
  }catch(error){
    return "guest-browser";
  }
}

function getPlutoApiHeaders(additionalHeaders = {}){
  const liveState = getLiveAuthState();
  const headers = {
    ...additionalHeaders,
    "X-Pluto-Guest-Key": getGuestUsageKey()
  };

  if(liveState?.session?.access_token){
    headers.Authorization = `Bearer ${liveState.session.access_token}`;
  }

  return headers;
}

async function fetchBackendAccountState(session){
  const apiBase = getApiBaseUrl();
  if(!session?.access_token || !apiBase){
    return null;
  }

  try{
    const response = await fetch(`${apiBase}/api/account/me`, {
      headers: {
        Authorization: `Bearer ${session.access_token}`
      }
    });

    if(!response.ok){
      return null;
    }

    const data = await response.json();
    window.PLUTO_ACCOUNT_USAGE = data?.usage || null;
    return data;
  }catch(error){
    console.warn("Backend account sync failed:", error);
    return null;
  }
}

async function postActivityPing(session){
  const apiBase = getApiBaseUrl();
  if(!apiBase){
    return;
  }

  const isAuthenticated = Boolean(session?.access_token);
  const url = isAuthenticated
    ? `${apiBase}/api/account/activity/ping`
    : `${apiBase}/api/account/guest/ping`;

  const headers = {
    "Content-Type": "application/json"
  };

  if(isAuthenticated){
    headers.Authorization = `Bearer ${session.access_token}`;
  }else{
    headers["X-Pluto-Guest-Key"] = getGuestActivityKey();
  }

  try{
    await fetch(url, {
      method: "POST",
      headers,
      body: JSON.stringify({
        activeSeconds: ACTIVITY_HEARTBEAT_SECONDS
      })
    });
  }catch(error){
    console.warn("Activity heartbeat failed:", error);
  }
}

function stopActivityHeartbeat(){
  if(activityHeartbeatTimer){
    clearInterval(activityHeartbeatTimer);
    activityHeartbeatTimer = null;
  }
  activityHeartbeatSession = null;
}

function startActivityHeartbeat(session){
  stopActivityHeartbeat();
  activityHeartbeatSession = session;
  activityHeartbeatTimer = setInterval(() => {
    if(document.visibilityState !== "visible"){
      return;
    }
    postActivityPing(activityHeartbeatSession);
  }, ACTIVITY_HEARTBEAT_MS);
}

function getBackendUsageState(){
  return window.PLUTO_ACCOUNT_USAGE || null;
}

function setBackendUsageState(usage){
  window.PLUTO_ACCOUNT_USAGE = usage || null;

  if(typeof window.syncAuthPreviewUI === "function"){
    window.syncAuthPreviewUI();
  }
}

async function refreshAccountUsageState(){
  const apiBase = getApiBaseUrl();
  if(!apiBase){
    return getBackendUsageState();
  }

  try{
    const response = await fetch(`${apiBase}/api/account/usage`, {
      headers: getPlutoApiHeaders()
    });

    if(!response.ok){
      throw new Error("Usage request failed.");
    }

    const data = await response.json();
    setBackendUsageState(data || null);
  }catch(error){
    console.warn("Backend usage sync failed:", error);
  }

  return getBackendUsageState();
}

async function consumeBackendFeatureUsage(featureKey, options = {}){
  const apiBase = getApiBaseUrl();
  if(!apiBase){
    throw new Error("API base is not ready.");
  }

  const response = await fetch(`${apiBase}/api/account/usage/consume`, {
    method: "POST",
    headers: getPlutoApiHeaders({
      "Content-Type": "application/json"
    }),
    body: JSON.stringify({
      featureKey,
      amount: options.amount || 1,
      grantCredits: options.grantCredits || {}
    })
  });

  const data = await response.json().catch(() => ({}));

  if(!response.ok){
    throw new Error(data.detail || "Usage consume failed.");
  }

  setBackendUsageState(data.usage || null);
  return data;
}

async function consumeBackendUsageCredit(creditKey, options = {}){
  const apiBase = getApiBaseUrl();
  if(!apiBase){
    throw new Error("API base is not ready.");
  }

  const response = await fetch(`${apiBase}/api/account/usage/consume-credit`, {
    method: "POST",
    headers: getPlutoApiHeaders({
      "Content-Type": "application/json"
    }),
    body: JSON.stringify({
      creditKey,
      amount: options.amount || 1
    })
  });

  const data = await response.json().catch(() => ({}));

  if(!response.ok){
    throw new Error(data.detail || "Usage credit consume failed.");
  }

  setBackendUsageState(data.usage || null);
  return data;
}

function getConfig(){
  return window.PLUTO_AUTH_CONFIG || window.PLUTO_APP_CONFIG?.auth || null;
}

function getPublicKey(config){
  return config?.supabasePublishableKey || config?.supabaseAnonKey || "";
}

function normalizeConfiguredSiteUrl(value){
  if(typeof value !== "string"){
    return "";
  }

  const trimmed = value.trim();

  if(!trimmed){
    return "";
  }

  try{
    const normalized = new URL(trimmed);
    normalized.hash = "";
    normalized.search = "";
    return normalized.toString().replace(/\/$/, "");
  }catch(error){
    return "";
  }
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

  if(typeof window.refreshAuthenticatedBillingStatus === "function"){
    window.refreshAuthenticatedBillingStatus();
  }

  if(typeof window.syncAuthPreviewUI === "function"){
    window.syncAuthPreviewUI();
  }
}

function getLiveAuthState(){
  return window.PLUTO_LIVE_AUTH_STATE || { ...DEFAULT_LIVE_STATE };
}

function buildLiveStateFromSession(session){
  if(!session?.user){
    return { ...DEFAULT_LIVE_STATE, enabled: true, loading: false };
  }

  const displayName =
    session.user.user_metadata?.full_name ||
    session.user.user_metadata?.name ||
    "Pluto Creator";

  return {
    enabled: true,
    loading: false,
    mode: "free",
    loggedIn: true,
    name: displayName,
    email: session.user.email || "",
    planLabel: "Free Account",
    backendPlan: "free",
    planSource: "session_default",
    planReason: "Session exists before backend plan resolution returns.",
    subscription: null,
    session,
    user: session.user
  };
}

function mergeBackendAccountState(liveState, backendState){
  if(!backendState){
    return liveState;
  }

  if(!backendState.authenticated){
    return {
      ...liveState,
      mode: "guest",
      loggedIn: false,
      name: "Guest",
      email: "",
      planLabel: "Guest",
      backendPlan: backendState.plan || "guest",
      planSource: "guest",
      planReason: "Backend returned an unauthenticated account state.",
      subscription: null,
      activity: null,
      session: null,
      user: null
    };
  }

  const user = backendState.user || {};
  const backendPlan = backendState.plan === "premium" ? "premium" : "free";

  return {
    ...liveState,
    mode: backendPlan,
    planLabel: backendPlan === "premium" ? "Premium" : "Free Account",
    name: user.name || liveState.name,
    email: user.email || liveState.email,
    backendPlan,
    planSource: backendState.planSource || liveState.planSource || "unknown",
    planReason: backendState.planReason || liveState.planReason || "",
    subscription: backendState.subscription || null,
    activity: backendState.activity || null
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
  if(window.PLUTO_APP_CONFIG?.auth?.supabaseUrl && getPublicKey(window.PLUTO_APP_CONFIG?.auth)){
    refreshAuthRuntimeStatus();
    ensureSupabaseSdk();
    return;
  }

  if(window.PLUTO_AUTH_CONFIG?.supabaseUrl && getPublicKey(window.PLUTO_AUTH_CONFIG)){
    refreshAuthRuntimeStatus();
    ensureSupabaseSdk();
    return;
  }

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
  await refreshAccountUsageState();
  startActivityHeartbeat(firstSession);

  supabaseClient.auth.onAuthStateChange(async (_event, session) => {
    const nextState = buildLiveStateFromSession(session);
    const backendState = await fetchBackendAccountState(session);
    setLiveAuthState(mergeBackendAccountState(nextState, backendState));
    await refreshAccountUsageState();
    if(session?.access_token){
      startActivityHeartbeat(session);
    }else{
      stopActivityHeartbeat();
    }
  });

  refreshAuthRuntimeStatus();
}

function getRedirectUrl(){
  const configuredSiteUrl = normalizeConfiguredSiteUrl(window.PLUTO_APP_CONFIG?.siteUrl);
  const currentPath = window.location.pathname || "/";

  if(configuredSiteUrl){
    return currentPath === "/" ? configuredSiteUrl : `${configuredSiteUrl}${currentPath}`;
  }

  return `${window.location.origin}${currentPath}`;
}

function authNotReadyMessage(){
  const runtime = getAuthRuntimeStatus();
  return runtime.configured
    ? "Supabase config is ready, but the auth client is not fully loaded yet. Refresh the page once."
    : "Supabase is not configured yet. Add values to frontend/app-config.js first.";
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
    return;
  }

  if(typeof closePlatformSurface === "function"){
    closePlatformSurface();
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
    return;
  }

  if(typeof closePlatformSurface === "function"){
    closePlatformSurface();
  }
}

window.PLUTO_AUTH_RUNTIME = { ...DEFAULT_RUNTIME };
window.PLUTO_LIVE_AUTH_STATE = { ...DEFAULT_LIVE_STATE };
window.refreshAuthRuntimeStatus = refreshAuthRuntimeStatus;
window.getAuthRuntimeStatus = getAuthRuntimeStatus;
window.getLiveAuthState = getLiveAuthState;
window.getPlutoGuestUsageKey = getGuestUsageKey;
window.getPlutoApiHeaders = getPlutoApiHeaders;
window.getBackendUsageState = getBackendUsageState;
window.refreshAccountUsageState = refreshAccountUsageState;
window.consumeBackendFeatureUsage = consumeBackendFeatureUsage;
window.consumeBackendUsageCredit = consumeBackendUsageCredit;
window.signInWithGoogleReal = signInWithGoogleReal;
window.signInWithEmailReal = signInWithEmailReal;
window.signUpWithEmailReal = signUpWithEmailReal;
window.signOutReal = signOutReal;

if(document.readyState === "loading"){
  document.addEventListener("DOMContentLoaded", () => {
    ensureAuthConfigScript();
    refreshAuthRuntimeStatus();
    ensureSupabaseSdk();
    refreshAccountUsageState();
  });
}else{
  ensureAuthConfigScript();
  refreshAuthRuntimeStatus();
  ensureSupabaseSdk();
  refreshAccountUsageState();
}
})();
