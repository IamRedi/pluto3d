(function(){
const DEFAULT_BILLING_RUNTIME = {
  provider: "stripe",
  ready: false,
  activationReady: false,
  loading: true,
  priceLabel: "$19 / month target",
  premiumPlanName: "Pluto3D Premium",
  detail: "Billing scaffold is loading.",
  storeMode: "local",
  storeDetail: "Local billing scaffold",
  customerPortalAvailable: false,
  subscription: null,
  activationProgress: {
    completed: 0,
    total: 0,
    percent: 0,
    label: "Scaffold only",
    detail: "Billing scaffold is loading."
  },
  activationBlockers: [],
  activationNextSteps: [],
  activationHandoff: null,
  returnState: null
};

function setBillingRuntime(partial){
  window.PLUTO_BILLING_RUNTIME = {
    ...window.PLUTO_BILLING_RUNTIME,
    ...partial
  };

  if(typeof window.syncAuthPreviewUI === "function"){
    window.syncAuthPreviewUI();
  }
}

function getBillingRuntime(){
  return window.PLUTO_BILLING_RUNTIME || { ...DEFAULT_BILLING_RUNTIME };
}

function readConfigValue(config, dottedKey){
  return dottedKey.split(".").reduce((value, key) => {
    if(value && typeof value === "object"){
      return value[key];
    }

    return undefined;
  }, config);
}

function summarizeConfiguredItems(items){
  const completed = items.filter((item) => item.configured).length;
  const total = items.length;
  const percent = total ? Math.round((completed / total) * 100) : 0;
  return { completed, total, percent };
}

function annotateActivationHandoff(handoff){
  if(!handoff){
    return null;
  }

  const publicConfig = window.PLUTO_APP_CONFIG || {};
  const frontendItems = (handoff.frontendPublicConfig || []).map((item) => ({
    ...item,
    configured: Boolean(readConfigValue(publicConfig, item.key))
  }));
  const frontendSummary = summarizeConfiguredItems(frontendItems);
  const switchPath = (handoff.switchPath || []).map((phase) => {
    if(phase.key === "frontend_public_config"){
      return {
        ...phase,
        status: frontendSummary.completed === frontendSummary.total ? "ready" : "pending"
      };
    }

    return phase;
  });
  const currentPhase = frontendSummary.completed === frontendSummary.total
    ? (handoff.summary?.currentPhase || null)
    : {
        key: "frontend_public_config",
        label: "Awaiting frontend config",
        detail: "Frontend public install values still need to be finalized."
      };

  return {
    ...handoff,
    frontendPublicConfig: frontendItems,
    switchPath,
    summary: {
      ...(handoff.summary || {}),
      frontendConfig: frontendSummary,
      currentPhase
    }
  };
}

function readBillingReturnState(){
  const url = new URL(window.location.href);
  const billingState = (url.searchParams.get("billing") || "").trim().toLowerCase();

  if(!billingState){
    return null;
  }

  const stateMap = {
    success: {
      tone: "success",
      title: "Checkout completed",
      copy: "Stripe returned successfully. The next step is confirming webhook persistence and premium activation."
    },
    cancel: {
      tone: "neutral",
      title: "Checkout canceled",
      copy: "No charge was completed. The account stays on the current plan until checkout succeeds."
    },
    portal: {
      tone: "info",
      title: "Returned from billing portal",
      copy: "You are back from the billing portal. Refreshing billing state helps confirm any subscription changes."
    }
  };

  const returnState = stateMap[billingState] || {
    tone: "info",
    title: "Billing return detected",
    copy: "A billing redirect returned to the app."
  };

  url.searchParams.delete("billing");
  window.history.replaceState({}, "", url.toString());
  return returnState;
}

async function refreshBillingRuntime(){
  if(typeof API_BASE === "undefined"){
    setBillingRuntime({
      loading: false,
      detail: "API base is not ready yet."
    });
    return getBillingRuntime();
  }

  try{
    const response = await fetch(`${API_BASE}/api/billing/config`);
    if(!response.ok){
      throw new Error("Billing config request failed.");
    }

    const data = await response.json();
    const store = data.subscriptionStore || {};
    const storeMode = store.mode || "local";
    const storeDetail = storeMode === "supabase"
      ? (store.schemaReady
        ? "Supabase subscription store is ready."
        : "Supabase store selected, but schema is not fully ready yet.")
      : "Local billing scaffold";

    setBillingRuntime({
      provider: data.provider || "stripe",
      ready: Boolean(data.ready),
      activationReady: Boolean(data.activationReady),
      loading: false,
      priceLabel: data.premiumPlan?.priceLabel || DEFAULT_BILLING_RUNTIME.priceLabel,
      premiumPlanName: data.premiumPlan?.name || DEFAULT_BILLING_RUNTIME.premiumPlanName,
      detail: data.activationReady
        ? "Stripe billing is ready for activation."
        : data.ready
          ? "Stripe keys are configured, but the activation path is not fully ready yet."
          : "Stripe scaffold is ready, but live keys and price IDs still need to be added.",
      storeMode,
      storeDetail,
      customerPortalAvailable: false,
      subscription: null,
      activationProgress: data.activationProgress || DEFAULT_BILLING_RUNTIME.activationProgress,
      activationBlockers: data.activationBlockers || [],
      activationNextSteps: data.activationNextSteps || []
    });
  }catch(error){
    console.warn("Billing runtime sync failed:", error);
    setBillingRuntime({
      loading: false,
      detail: "Billing runtime is unavailable right now.",
      activationProgress: {
        completed: 0,
        total: 0,
        percent: 0,
        label: "Runtime unavailable",
        detail: "Billing activation progress could not be loaded."
      },
      activationBlockers: ["Billing runtime is unavailable"],
      activationNextSteps: ["Restore billing runtime access before proceeding."],
      activationHandoff: null
    });
  }

  return getBillingRuntime();
}

async function refreshBillingActivationHandoff(){
  if(typeof API_BASE === "undefined"){
    return getBillingRuntime();
  }

  try{
    const response = await fetch(`${API_BASE}/api/billing/activation-handoff`);
    if(!response.ok){
      throw new Error("Billing activation handoff request failed.");
    }

    const data = await response.json();
    setBillingRuntime({
      activationHandoff: annotateActivationHandoff(data || null)
    });
  }catch(error){
    console.warn("Billing activation handoff sync failed:", error);
  }

  return getBillingRuntime();
}

async function refreshAuthenticatedBillingStatus(){
  const accessToken = getAccessToken();

  if(!accessToken){
    setBillingRuntime({
      customerPortalAvailable: false,
      subscription: null
    });
    return getBillingRuntime();
  }

  try{
    const response = await fetch(`${API_BASE}/api/billing/status`, {
      headers: {
        Authorization: `Bearer ${accessToken}`
      }
    });

    const data = await response.json().catch(() => ({}));
    if(!response.ok){
      throw new Error(data.detail || "Billing status request failed.");
    }

    setBillingRuntime({
      customerPortalAvailable: Boolean(data.customerPortalAvailable),
      subscription: data.subscription || null
    });
  }catch(error){
    console.warn("Authenticated billing status sync failed:", error);
  }

  return getBillingRuntime();
}

function getAccessToken(){
  const liveState = typeof window.getLiveAuthState === "function"
    ? window.getLiveAuthState()
    : null;

  return liveState?.session?.access_token || "";
}

async function postBillingAction(path){
  const accessToken = getAccessToken();

  if(!accessToken){
    throw new Error("Please sign in first.");
  }

  const response = await fetch(`${API_BASE}${path}`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${accessToken}`
    }
  });

  const data = await response.json().catch(() => ({}));

  if(!response.ok){
    throw new Error(data.detail || "Billing action failed.");
  }

  return data;
}

async function startPremiumCheckout(){
  const authState = typeof window.getAuthPreviewState === "function"
    ? window.getAuthPreviewState()
    : { loggedIn:false, mode:"guest" };

  if(!authState.loggedIn){
    window.openPlatformSurface?.("login");
    alert("Sign in first to start premium checkout.");
    return;
  }

  if(authState.mode === "premium"){
    alert("Premium is already active for this account.");
    return;
  }

  try{
    const data = await postBillingAction("/api/billing/checkout-session");
    if(data.checkoutUrl){
      window.location.href = data.checkoutUrl;
      return;
    }

    alert("Checkout session was created without a redirect URL.");
  }catch(error){
    alert(error.message || "Unable to start premium checkout.");
  }
}

async function openBillingPortal(){
  const authState = typeof window.getAuthPreviewState === "function"
    ? window.getAuthPreviewState()
    : { loggedIn:false };

  if(!authState.loggedIn){
    window.openPlatformSurface?.("login");
    alert("Sign in first to manage billing.");
    return;
  }

  try{
    const data = await postBillingAction("/api/billing/portal-session");
    if(data.portalUrl){
      window.location.href = data.portalUrl;
      return;
    }

    alert("Billing portal session was created without a redirect URL.");
  }catch(error){
    alert(error.message || "Unable to open billing portal.");
  }
}

window.PLUTO_BILLING_RUNTIME = { ...DEFAULT_BILLING_RUNTIME };
window.PLUTO_BILLING_RUNTIME.returnState = readBillingReturnState();
window.getBillingRuntime = getBillingRuntime;
window.refreshBillingRuntime = refreshBillingRuntime;
window.refreshAuthenticatedBillingStatus = refreshAuthenticatedBillingStatus;
window.refreshBillingActivationHandoff = refreshBillingActivationHandoff;
window.startPremiumCheckout = startPremiumCheckout;
window.openBillingPortal = openBillingPortal;

if(document.readyState === "loading"){
  document.addEventListener("DOMContentLoaded", () => {
    refreshBillingRuntime();
    refreshBillingActivationHandoff();
    refreshAuthenticatedBillingStatus();
  });
}else{
  refreshBillingRuntime();
  refreshBillingActivationHandoff();
  refreshAuthenticatedBillingStatus();
}
})();
