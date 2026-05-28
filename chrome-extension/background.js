// Jobflow Chrome Extension — Background Service Worker

const CONFIG = {
  webappUrl: "http://localhost:3000",
  backendUrl: "http://localhost:8000",
};

chrome.runtime.onMessage.addListener((msg, _sender, sendResponse) => {
  if (msg.action === "signIn") {
    handleSignIn(msg.provider).then(sendResponse);
    return true; // async response
  }
  if (msg.action === "signOut") {
    handleSignOut().then(sendResponse);
    return true;
  }
});

async function handleSignIn(provider) {
  const redirectUri = chrome.identity.getRedirectURL("callback");
  const authUrl =
    `${CONFIG.webappUrl}/signin/extension` +
    `?provider=${provider}` +
    `&redirect_uri=${encodeURIComponent(redirectUri)}`;

  try {
    const responseUrl = await chrome.identity.launchWebAuthFlow({
      url: authUrl,
      interactive: true,
    });
    const url = new URL(responseUrl);
    const token = url.searchParams.get("token");
    const email = url.searchParams.get("email");
    const name = url.searchParams.get("name");

    if (token) {
      await chrome.storage.session.set({ token, email, name });
      return { success: true, email, name };
    }
    return { success: false, error: "No token received" };
  } catch (err) {
    return { success: false, error: err.message };
  }
}

async function handleSignOut() {
  await chrome.storage.session.clear();
  return { success: true };
}
