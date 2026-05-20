// ========================================
// GLOBAL APP INITIALIZATION
// ========================================

document.addEventListener("DOMContentLoaded", () => {

  initializeTheme();

  initializeTopbar();

});

// ========================================
// THEME SYSTEM
// ========================================

function initializeTheme() {

  const savedTheme =
    localStorage.getItem("theme") || "light";

  document.body.setAttribute(
    "data-theme",
    savedTheme
  );

  updateThemeIcon(savedTheme);

}

function toggleTheme() {

  const currentTheme =
    document.body.getAttribute("data-theme");

  const newTheme =
    currentTheme === "dark"
      ? "light"
      : "dark";

  document.body.setAttribute(
    "data-theme",
    newTheme
  );

  localStorage.setItem(
    "theme",
    newTheme
  );

  updateThemeIcon(newTheme);
}

function updateThemeIcon(theme) {

  const themeBtn =
    document.getElementById("themeToggle");

  if (!themeBtn) return;

  themeBtn.innerHTML =
  theme === "dark"
    ? "☀"
    : "☾";
}

// ========================================
// TOPBAR USER INFO
// ========================================

function initializeTopbar() {

  const user =
    JSON.parse(localStorage.getItem("user")) || {};

  const userNameEl =
    document.getElementById("topbarUserName");

  const avatarEl =
    document.getElementById("topbarAvatar");

  const name =
    user.name || "Sayali Patil";

  if (userNameEl) {

    userNameEl.textContent = name;
  }

  if (avatarEl) {

    avatarEl.textContent =
      name.charAt(0).toUpperCase();
  }
}

// ========================================
// LOGOUT
// ========================================

function logout() {

  localStorage.removeItem("token");
  localStorage.removeItem("user");
  localStorage.removeItem("activeChatId");

  window.location.href =  "/frontend/auth.html";
}