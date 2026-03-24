(function(){
const DEFAULT_RUNTIME = {
  provider: "supabase",
  configured: false,
  sdkReady: false,
  configLoaded: false,
  statusLabel: "Setup Needed",
  detail: "Create Supabase first, then add frontend/auth-config.js.",
  source: "preview"
};

function getConfig(){
  return window.PLUTO_AUTH_CONFIG || null;
}

function hasConfig(){
  const config = getConfig();
  return Boolean(config?.supabaseUrl && config?.supabaseAnonKey);
}

function buildRuntimeState(){
  const configReady = hasConfig();
  const sdkReady = Boolean(window.supabase?.createClient);

  if(configReady && sdkReady){
    return {
      provider: "supabase",
      configured: true,
      sdkReady: true,
      configLoaded: true,
      statusLabel: "Client Ready",
      detail: "Supabase config and client library are both ready for live auth wiring.",
      source: "runtime"
    };
  }

  if(configReady){
    return {
      provider: "supabase",
      configured: true,
      sdkReady: false,
      configLoaded: true,
      statusLabel: "Config Ready",
      detail: "Supabase keys are present. The next step is wiring the live auth client.",
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
    refreshAuthRuntimeStatus();
    return;
  }

  const script = document.createElement("script");
  script.src = "auth-config.js";
  script.dataset.authConfig = "true";
  script.async = true;
  script.onload = () => refreshAuthRuntimeStatus();
  script.onerror = () => refreshAuthRuntimeStatus();
  document.head.appendChild(script);
}

function authNotReadyMessage(){
  const runtime = getAuthRuntimeStatus();
  return runtime.configured
    ? "Supabase config is ready. Live auth wiring is the next build step."
    : "Supabase is not configured yet. Follow SUPABASE_SETUP_CHECKLIST.md first.";
}

function signInWithGoogleReal(){
  alert(authNotReadyMessage());
}

function signInWithEmailReal(){
  alert(authNotReadyMessage());
}

function signUpWithEmailReal(){
  alert(authNotReadyMessage());
}

function signOutReal(){
  alert(authNotReadyMessage());
}

window.PLUTO_AUTH_RUNTIME = { ...DEFAULT_RUNTIME };
window.refreshAuthRuntimeStatus = refreshAuthRuntimeStatus;
window.getAuthRuntimeStatus = getAuthRuntimeStatus;
window.signInWithGoogleReal = signInWithGoogleReal;
window.signInWithEmailReal = signInWithEmailReal;
window.signUpWithEmailReal = signUpWithEmailReal;
window.signOutReal = signOutReal;

if(document.readyState === "loading"){
  document.addEventListener("DOMContentLoaded", () => {
    ensureAuthConfigScript();
    refreshAuthRuntimeStatus();
  });
}else{
  ensureAuthConfigScript();
  refreshAuthRuntimeStatus();
}
})();
