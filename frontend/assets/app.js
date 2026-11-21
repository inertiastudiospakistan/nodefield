/* Nodefield frontend — shared behaviour. No secrets here. Demo API base: */
var API_BASE = "http://localhost:8787";

function $(s, r){ return (r||document).querySelector(s); }
function $all(s, r){ return Array.prototype.slice.call((r||document).querySelectorAll(s)); }

document.addEventListener("DOMContentLoaded", function(){
  var y = $("#year"); if (y) y.textContent = new Date().getFullYear();
  // Highlight current nav link.
  var page = (location.pathname.split("/").pop() || "index.html").split("?")[0];
  $all(".site-nav a").forEach(function(a){
    if (a.getAttribute("href") === page) a.classList.add("active");
  });
  // Mobile nav toggle.
  var t = $(".nav-toggle"), nav = $("#siteNav");
  if (t && nav) t.addEventListener("click", function(){
    var open = nav.classList.toggle("open");
    t.setAttribute("aria-expanded", open ? "true" : "false");
  });
  if ($("#registerProvider") || $("#registerDeveloper")) initRegister();
  if ($("#playgroundForm")) initPlayground();
  if ($("#statusBody")) initStatus();
  if ($("#dashboardStats")) initDashboard();
});

function showMsg(el, ok, text){
  if (!el) return;
  el.className = "form-msg " + (ok ? "ok" : "err");
  el.textContent = text;
  el.style.display = "block";
}

/* ---- Register / waitlist ---- */
function formData(form){
  var out = {}, fd = new FormData(form);
  fd.forEach(function(v, k){
    if (k === "preferred_models" || k === "api_features") {
      if (!out[k]) out[k] = [];
      out[k].push(v);
    } else if (k === "beta_interest") {
      out[k] = true;
    } else if (v !== "") {
      out[k] = v;
    }
  });
  // Unchecked checkbox absent from FormData.
  if (form.id === "registerProvider" && !("beta_interest" in out)) out.beta_interest = false;
  ["gpu_vram_gb","system_ram_gb","expected_tokens"].forEach(function(k){
    if (out[k] !== undefined && out[k] !== "") out[k] = Number(out[k]);
  });
  return out;
}

function saveLocal(kind, payload){
  try {
    var key = "nodefield-waitlist";
    var list = JSON.parse(localStorage.getItem(key) || "[]");
    list.push({ kind: kind, submitted_at: new Date().toISOString(), data: payload });
    localStorage.setItem(key, JSON.stringify(list));
    return list.length;
  } catch(e){ return 0; }
}

function initRegister(){
  // Tabs, honouring ?type=provider|developer
  var params = new URLSearchParams(location.search);
  function show(kind){
    $all(".tab-btn").forEach(function(b){ b.classList.toggle("active", b.dataset.tab === kind); });
    $all(".tab-panel").forEach(function(p){ p.classList.toggle("active", p.id === "panel-" + kind); });
  }
  $all(".tab-btn").forEach(function(b){ b.addEventListener("click", function(){ show(b.dataset.tab); }); });
  show(params.get("type") === "developer" ? "developer" : "provider");

  [["registerProvider","provider","#providerMsg"],["registerDeveloper","developer","#developerMsg"]].forEach(function(cfg){
    var form = $(cfg[0] ? "#" + cfg[0] : "");
    if (!form) return;
    form.addEventListener("submit", function(ev){
      ev.preventDefault();
      var payload = formData(form); payload.kind = cfg[1];
      var msg = $(cfg[2]);
      showMsg(msg, true, "Sending…");
      fetch(API_BASE + "/api/waitlist", {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      }).then(function(r){ return r.json().then(function(j){ return { ok: r.ok, j: j }; }); })
      .then(function(res){
        if (res.ok) { showMsg(msg, true, "Thank you — your registration was received by the Nodefield demo backend."); form.reset(); }
        else { var n = saveLocal(cfg[1], payload); showMsg(msg, false, "Backend returned an error (" + (res.j && res.j.detail ? res.j.detail : "unknown") + "). Your entry was saved locally (" + n + " saved in this browser) and will sync when the backend runs."); }
      }).catch(function(){
        var n = saveLocal(cfg[1], payload);
        showMsg(msg, false, "Backend not reachable at " + API_BASE + ". Your entry was saved locally in this browser (" + n + " saved under key nodefield-waitlist) — it has NOT reached a server yet. It will sync when the backend is running.");
      });
    });
  });
}

/* ---- Chat playground (models.html) ---- */
function initPlayground(){
  var form = $("#playgroundForm"), log = $("#chatLog"), btn = $("#playgroundSend");
  form.addEventListener("submit", function(ev){
    ev.preventDefault();
    var model = $("#playModel").value, text = $("#playInput").value.trim();
    if (!text) { log.textContent = "Type a message first."; return; }
    log.textContent = "Sending to " + model + " via " + API_BASE + "/v1/chat/completions …";
    btn.disabled = true;
    fetch(API_BASE + "/v1/chat/completions", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ model: model, messages: [{ role: "user", content: text }], stream: false })
    }).then(function(r){ return r.json().then(function(j){ return { ok: r.ok, status: r.status, j: j }; }); })
    .then(function(res){
      btn.disabled = false;
      if (!res.ok) { log.textContent = "Error " + res.status + ": " + JSON.stringify(res.j, null, 2); return; }
      var reply = res.j && res.j.choices && res.j.choices[0] && res.j.choices[0].message
        ? res.j.choices[0].message.content : JSON.stringify(res.j, null, 2);
      log.textContent = reply;
    }).catch(function(err){
      btn.disabled = false;
      log.textContent = "Could not reach the backend at " + API_BASE + " (" + err.message + "). Start the demo backend first, or check docs.html for the local setup. Nothing was sent.";
    });
  });
}

/* ---- Status page ---- */
function setStatus(id, text, cls){
  var el = document.getElementById(id); if (!el) return;
  el.textContent = text; if (cls) el.className = "badge " + cls;
}
function initStatus(){
  fetch(API_BASE + "/api/health").then(function(r){ return r.json(); })
    .then(function(j){
      setStatus("healthBadge", "Backend reachable — " + (j.status || "ok"), "badge-teal");
      $("#healthDetail").textContent = "Health response: " + JSON.stringify(j);
    }).catch(function(){
      setStatus("healthBadge", "Backend not running", "badge-amber");
      $("#healthDetail").textContent = "Could not reach " + API_BASE + "/api/health. The backend is not running on this machine — start it to see live values.";
    });
  fetch(API_BASE + "/api/stats").then(function(r){ return r.json(); })
    .then(function(j){
      setStatus("statsBadge", "Live stats loaded", "badge-teal");
      $("#statProviders").textContent = j.providers_registered != null ? j.providers_registered : "—";
      $("#statDevelopers").textContent = j.developers_registered != null ? j.developers_registered : "—";
      $("#statWorkers").textContent = j.active_workers != null ? j.active_workers : "—";
      $("#statRequests").textContent = j.api_requests != null ? j.api_requests : "—";
      $("#statsDetail").textContent = "Live response: " + JSON.stringify(j);
    }).catch(function(){
      setStatus("statsBadge", "Showing honest defaults — backend not running", "badge-amber");
      $("#statsDetail").textContent = "Backend not reachable. Values below are the honest pre-launch defaults (0 live workers, demo mode), not measured traffic.";
    });
}

/* ---- Dashboard ---- */
function initDashboard(){
  function loadStats(){
    fetch(API_BASE + "/api/stats").then(function(r){ return r.json(); })
      .then(function(j){
        $("#dProviders").textContent = j.providers_registered != null ? j.providers_registered : "0";
        $("#dDevelopers").textContent = j.developers_registered != null ? j.developers_registered : "0";
        $("#dWorkers").textContent = j.active_workers != null ? j.active_workers : "0";
        $("#dRequests").textContent = j.api_requests != null ? j.api_requests : "0";
        $("#dashStatsNote").textContent = "Live from " + API_BASE + "/api/stats.";
      }).catch(function(){
        $("#dashStatsNote").textContent = "Backend not running — showing pre-launch defaults (0). Start the backend on port 8787 to load live demo values.";
      });
  }
  function loadKeys(){
    var list = $("#keyList");
    fetch(API_BASE + "/api/keys").then(function(r){ return r.json(); })
      .then(function(j){
        var keys = j.keys || j || [];
        if (!keys.length) { list.innerHTML = "<p class='muted'>No API keys yet (demo).</p>"; return; }
        list.innerHTML = "<ul>" + keys.map(function(k){
          var p = (k && k.prefix) || k.key_prefix || k.id || JSON.stringify(k);
          var label = (k && k.label) || "";
          return "<li><code class='inline'>" + p + "</code>" + (label ? " — " + label : "") + " <span class='badge badge-grey'>prefix only — full key never shown again</span></li>";
        }).join("") + "</ul>";
      }).catch(function(){
        list.innerHTML = "<p class='muted'>Backend not running — API key list unavailable. Keys are stored server-side; this page never shows a full secret after creation.</p>";
      });
  }
  loadStats(); loadKeys();
  var form = $("#createKeyForm");
  if (form) form.addEventListener("submit", function(ev){
    ev.preventDefault();
    var email = $("#keyEmail").value.trim(), label = $("#keyLabel").value.trim();
    var msg = $("#keyMsg"), out = $("#newKeyBox");
    fetch(API_BASE + "/api/keys", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email: email, label: label })
    }).then(function(r){ return r.json().then(function(j){ return { ok: r.ok, status: r.status, j: j }; }); })
    .then(function(res){
      if (!res.ok) { showMsg(msg, false, "Could not create key (" + res.status + "): " + JSON.stringify(res.j)); return; }
      var key = res.j.key || res.j.api_key || res.j.secret || "";
      out.style.display = "block";
      out.innerHTML = "<strong>Your new demo API key — shown ONCE. Copy it now; it will not be shown again:</strong><br><br>" + key;
      showMsg(msg, true, "Demo key created. Store it safely — the dashboard only ever lists key prefixes afterwards.");
      loadKeys();
    }).catch(function(err){
      showMsg(msg, false, "Backend not reachable at " + API_BASE + " (" + err.message + "). No key was created.");
    });
  });
}
