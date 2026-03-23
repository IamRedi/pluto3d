// Resolve the backend target from the current environment.
// Local frontend talks to the local FastAPI server, production uses Railway.
window.PLUTO_API_BASE = ["127.0.0.1", "localhost"].includes(window.location.hostname)
  ? "http://127.0.0.1:8000"
  : "https://pluto3d-production.up.railway.app";
