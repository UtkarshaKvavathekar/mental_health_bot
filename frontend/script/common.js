// ======================================
// APPLY DARK MODE GLOBALLY
// ======================================

function applyDarkMode() {

  const isDarkMode =
    localStorage.getItem("darkMode") === "true";

  if (isDarkMode) {
    document.body.classList.add("dark-mode");
  } else {
    document.body.classList.remove("dark-mode");
  }
}

// APPLY AFTER PAGE LOAD
document.addEventListener("DOMContentLoaded", () => {
  applyDarkMode();
});

// ======================================
// LOGOUT
// ======================================

function logout() {

  localStorage.removeItem("token");
  localStorage.removeItem("user");
  localStorage.removeItem("activeChatId");

  window.location.href = "auth.html";
}