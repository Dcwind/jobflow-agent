// Jobflow Chrome Extension — Popup

const BACKEND_URL = "http://localhost:8000";

const $ = (id) => document.getElementById(id);

// UI state management
function showState(state) {
  for (const s of ["loading", "signed-out", "signed-in"]) {
    $(s).classList.toggle("hidden", s !== state);
  }
}

function showStatus(message, type) {
  const el = $("status");
  el.textContent = message;
  el.className = `status ${type}`;
  if (type === "success") {
    setTimeout(() => el.classList.add("hidden"), 3000);
  }
}

// Check auth state on popup open
async function init() {
  const { token, email, name } = await chrome.storage.session.get([
    "token",
    "email",
    "name",
  ]);

  if (!token) {
    showState("signed-out");
    return;
  }

  // Verify token is still valid
  try {
    const res = await fetch(`${BACKEND_URL}/api/jobs?per_page=1`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    if (res.status === 401) {
      await chrome.storage.session.clear();
      showState("signed-out");
      return;
    }
  } catch {
    // Network error — show signed-in state anyway, will fail on save
  }

  $("user-name").textContent = name || "Signed in";
  $("user-email").textContent = email || "";
  showState("signed-in");
}

// Sign in
function handleSignIn(provider) {
  return async () => {
    $("btn-google").disabled = true;
    $("btn-github").disabled = true;

    const result = await chrome.runtime.sendMessage({
      action: "signIn",
      provider,
    });

    if (result.success) {
      $("user-name").textContent = result.name || "Signed in";
      $("user-email").textContent = result.email || "";
      showState("signed-in");
    } else {
      $("btn-google").disabled = false;
      $("btn-github").disabled = false;
    }
  };
}

// Sign out
async function handleSignOut() {
  await chrome.runtime.sendMessage({ action: "signOut" });
  showState("signed-out");
}

// Save current tab
async function handleSave() {
  const btn = $("btn-save");
  btn.disabled = true;
  btn.textContent = "Saving...";

  try {
    const [tab] = await chrome.tabs.query({
      active: true,
      currentWindow: true,
    });
    if (!tab?.url) {
      showStatus("No URL found", "error");
      return;
    }

    const { token } = await chrome.storage.session.get("token");
    const res = await fetch(`${BACKEND_URL}/api/jobs`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({ urls: [tab.url] }),
    });

    if (res.status === 401) {
      await chrome.storage.session.clear();
      showState("signed-out");
      return;
    }

    const data = await res.json();

    if (!res.ok) {
      showStatus(data.detail || "Failed to save", "error");
      return;
    }

    if (data.succeeded > 0) {
      const job = data.results[0];
      showStatus(`Saved: ${job.title || "Job"} at ${job.company || "Unknown"}`, "success");
    } else if (data.failed > 0) {
      const reason = data.results[0]?.error || "Could not extract job";
      showStatus(reason, "error");
    }
  } catch (err) {
    showStatus("Network error", "error");
  } finally {
    btn.disabled = false;
    btn.textContent = "Save to Jobflow";
  }
}

// Event listeners
$("btn-google").addEventListener("click", handleSignIn("google"));
$("btn-github").addEventListener("click", handleSignIn("github"));
$("btn-signout").addEventListener("click", handleSignOut);
$("btn-save").addEventListener("click", handleSave);

init();
