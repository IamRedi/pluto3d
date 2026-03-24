// Public deployment config can override backend routing per install.
const publicConfig = window.PLUTO_APP_CONFIG || {};
const explicitApiBase = (publicConfig.apiBase || "").trim().replace(/\/$/, "");
const isLocalHost = ["127.0.0.1", "localhost"].includes(window.location.hostname);

window.PLUTO_API_BASE = explicitApiBase
  || (isLocalHost
    ? "http://127.0.0.1:8000"
    : "https://pluto3d-production.up.railway.app");
