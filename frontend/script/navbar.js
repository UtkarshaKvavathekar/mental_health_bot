document.addEventListener("DOMContentLoaded", () => {
  const token = localStorage.getItem("token");
const isLoggedIn = !!token;

  const navbarHTML = `
    <div class="navbar">
        <div class="nav-container">

            <div class="logo">S</div>
            
            <div class="nav-links">

                <a href="dashboard.html">Dashboard</a>
                <a href="chat.html">Chat</a>
                <a href="meditation.html">Meditation</a>
                <a href="history.html">History</a>
                <a href="profile.html">Profile</a>

                ${
                  isLoggedIn
                    ? `<a href="#" onclick="logout()">Logout</a>`
                    : `<a href="auth.html">Login</a>`
                }

            </div>

        </div>
    </div>
    `;

  // ✅ prevent duplicate navbar
  if (!document.querySelector(".navbar")) {
    document.body.insertAdjacentHTML("afterbegin", navbarHTML);
  }

  // ACTIVE LINK HIGHLIGHT
 const currentPage = window.location.pathname.split("/").pop() || "index.html";

  document.querySelectorAll(".nav-links a").forEach((link) => {
    const linkPage = link.getAttribute("href");

    if (linkPage === "#" || linkPage === "auth.html") return;

    if (linkPage === currentPage) {
      link.classList.add("active");
    }
  });
});

// GLOBAL LOGOUT
function logout() {
  localStorage.removeItem("token");
  localStorage.removeItem("user");

  window.location.href = "auth.html";
}