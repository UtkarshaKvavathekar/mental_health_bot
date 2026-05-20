document.addEventListener("DOMContentLoaded", () => {
  const currentPage = window.location.pathname.split("/").pop();

  const appShell = `

  <!-- SIDEBAR -->
  <aside class="sidebar" id="sidebar">

    <div class="sidebar-top">

      <div class="brand">

        <div class="brand-logo">
          S
        </div>

        <div class="brand-text">
          <h2>Serene</h2>
          <p>Mind Wellness</p>
        </div>

      </div>

      <button
        class="sidebar-close-btn"
        id="sidebarCloseBtn">
        ✕
      </button>

      <nav class="sidebar-nav">

        <a href="dashboard.html"
           class="${currentPage === "dashboard.html" ? "active" : ""}">
         <span>
  <i class="fa-solid fa-house"></i>
</span>
          Dashboard
        </a>

        <a href="chat.html"
           class="${currentPage === "chat.html" ? "active" : ""}">
          <span>
  <i class="fa-solid fa-comment-dots"></i>
</span>
          Chat
        </a>

        <a href="meditation.html"
           class="${currentPage === "meditation.html" ? "active" : ""}">
          <span>
  <i class="fa-solid fa-spa"></i>
</span>
          Meditation
        </a>

        <a href="history.html"
           class="${currentPage === "history.html" ? "active" : ""}">
          <span>
  <i class="fa-solid fa-clock-rotate-left"></i>
</span>
          History
        </a>

        <a href="profile.html"
           class="${currentPage === "profile.html" ? "active" : ""}">
          <span>
  <i class="fa-solid fa-user"></i>
</span>
          Profile
        </a>

      </nav>

    </div>

    <div class="sidebar-bottom">

      <button
  onclick="logout()"
  class="logout-btn">

  <i class="fa-solid fa-arrow-right-from-bracket"></i>

  Logout

</button>

    </div>

  </aside>

  <!-- OVERLAY -->
  <div
    class="sidebar-overlay"
    id="sidebarOverlay">
  </div>

  <!-- GLOBAL TOPBAR -->
  <header class="global-topbar">

    <div class="topbar-left">

      <button
  id="sidebarToggle"
  class="sidebar-toggle">

  <i class="fa-solid fa-bars"></i>

</button>

    </div>

    <div class="topbar-right">

      <button
        class="theme-toggle"
        id="themeToggle"
        onclick="toggleTheme()">
        🌙
      </button>

      <div class="topbar-user">

        <div
          class="topbar-avatar"
          id="topbarAvatar">
          U
        </div>

        <div class="topbar-user-info">

          <h4 id="topbarUserName">
            User
          </h4>

          <p>Premium Member</p>

        </div>

      </div>

    </div>

  </header>
  `;

  document.body.insertAdjacentHTML("afterbegin", appShell);

  // =====================================
  // SIDEBAR
  // =====================================

  const sidebar = document.getElementById("sidebar");

  const overlay = document.getElementById("sidebarOverlay");

  const toggleBtn = document.getElementById("sidebarToggle");

  const closeBtn = document.getElementById("sidebarCloseBtn");

  if (toggleBtn) {
    toggleBtn.addEventListener("click", () => {
      sidebar.classList.toggle("show");

      overlay.classList.toggle("show");
    });
  }

  if (closeBtn) {
    closeBtn.addEventListener("click", closeSidebar);
  }

  if (overlay) {
    overlay.addEventListener("click", closeSidebar);
  }

  function closeSidebar() {
    sidebar.classList.remove("show");

    overlay.classList.remove("show");
  }
});
