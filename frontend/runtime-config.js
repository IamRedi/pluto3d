// Public deployment config can override backend routing per install.
const publicConfig = window.PLUTO_APP_CONFIG || {};
const explicitApiBase = (publicConfig.apiBase || "").trim().replace(/\/$/, "");
const isLocalHost = ["127.0.0.1", "localhost"].includes(window.location.hostname);
const localApiBase = "http://127.0.0.1:8000";
const productionApiBase = "https://pluto3d-production.up.railway.app";

window.PLUTO_API_BASE = isLocalHost
  ? localApiBase
  : (explicitApiBase || productionApiBase);
