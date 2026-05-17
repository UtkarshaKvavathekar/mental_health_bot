const API_BASE_URL = "http://127.0.0.1:8000";

// ================================
// AUTH HELPERS
// ================================
function getToken() {
  return localStorage.getItem("token");
}

function logout() {
  localStorage.removeItem("token");
  localStorage.removeItem("user");
  localStorage.removeItem("user_id");

  window.location.href = "login.html";
}

// ================================
// API REQUEST
// ================================
async function fetchProfile() {
  const token = getToken();

  if (!token) {
    checkAuth();
    return;
  }

  try {
    const response = await fetch(`${API_BASE_URL}/api/profile/me`, {
      method: "GET",
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      },
    });

    if (response.status === 401) {
      logout();
      return;
    }

    if (!response.ok) {
      throw new Error("Failed to fetch profile");
    }

    const data = await response.json();

    renderProfile(data);

  } catch (error) {
    console.error("PROFILE FETCH ERROR:", error);

    document.getElementById("profileLoading").innerHTML =
      "Failed to load profile.";

    alert("Unable to load profile data.");
  }
}

// ================================
// RENDER PROFILE
// ================================
function renderProfile(data) {

  document.getElementById("profileLoading").style.display = "none";

  // ==================================
  // HEADER
  // ==================================
  document.getElementById("userName").innerText =
    data.user.name || "User";

  document.getElementById("userEmail").innerText =
    data.user.email || "No email";

  document.getElementById("memberSince").innerText =
    `Member Since: ${formatDate(data.user.created_at)}`;

  document.getElementById("userId").innerText =
    `User ID: #${data.user.id}`;

  document.getElementById("avatar").innerText =
    data.user.name?.charAt(0).toUpperCase() || "U";

  // ==================================
  // STAT BOXES
  // ==================================
  const statBoxes = document.querySelectorAll(".stat-box p");

  statBoxes[0].innerText = data.stats.messages_sent;

  statBoxes[1].innerText = data.stats.meditation_sessions;

  statBoxes[2].innerText =
    `${data.stats.total_meditation_minutes} mins`;

  statBoxes[3].innerText =
    `${data.stats.current_streak} days`;

  statBoxes[4].innerText =
    data.stats.mood_entries_logged;

  statBoxes[5].innerText =
    `${data.stats.days_using_app} days`;

  // ==================================
  // MOOD CHART
  // ==================================
  renderMoodChart(data.mood_trends);

  // ==================================
  // MEDITATION SESSIONS
  // ==================================
  renderMeditationSessions(data.recent_meditations);

  loadSettings(data);

  renderMeditationSessions(data.recent_meditations);

loadSettings(data);
}

// ================================
// MOOD CHART
// ================================
function renderMoodChart(moodData) {

  const chart = document.getElementById("moodChart");

  chart.innerHTML = "";

  if (!moodData || moodData.length === 0) {
    chart.innerHTML = `
      <p style="padding:20px;">
        No mood data available
      </p>
    `;
    return;
  }

  moodData.forEach((item) => {

    const safeValue = Math.max(5, item.value);

    const barItem = document.createElement("div");
    barItem.className = "bar-item";

    barItem.innerHTML = `
      <div 
        class="bar" 
        style="height:${safeValue}%;"
        title="${item.value}"
      ></div>

      <div class="bar-label">
        ${item.day}
      </div>
    `;

    chart.appendChild(barItem);
  });
}

// ================================
// MEDITATION LIST
// ================================
function renderMeditationSessions(sessions) {

  const container = document.getElementById("meditationList");

  container.innerHTML = "";

  if (!sessions || sessions.length === 0) {
    container.innerHTML = `
      <p>No recent sessions found.</p>
    `;
    return;
  }

  sessions.forEach((session) => {

    const div = document.createElement("div");

    div.className = "meditation-session";

    div.innerHTML = `
      <p><strong>Exercise:</strong> ${session.exercise}</p>
      <p><strong>Duration:</strong> ${session.duration} mins</p>
      <p><strong>Date:</strong> ${session.date}</p>
    `;

    container.appendChild(div);
  });
}

// ================================
// DATE FORMATTER
// ================================
function formatDate(dateString) {

  if (!dateString) return "N/A";

  const date = new Date(dateString);

  return date.toLocaleDateString("en-IN", {
    year: "numeric",
    month: "long",
    day: "numeric",
  });
}

// ================================
// LOGOUT BUTTONS
// ================================
document.addEventListener("DOMContentLoaded", () => {

  const logoutBtn = document.querySelector(".logout");

  if (logoutBtn) {
    logoutBtn.addEventListener("click", logout);
  }

    // =========================
  // EDIT PROFILE BUTTON
  // =========================

  const editBtn =
  document.getElementById("editProfileBtn");

const bottomEditBtn =
  document.getElementById("editProfileBtnBottom");

  const modal =
    document.getElementById("editProfileModal");

  const closeModalBtn =
    document.getElementById("closeModalBtn");

  const saveProfileBtn =
    document.getElementById("saveProfileBtn");

  // =========================
// OPEN MODAL FUNCTION
// =========================

function openEditModal() {

  document.getElementById("editName").value =
    document.getElementById("userName").innerText;

  document.getElementById("editEmail").value =
    document.getElementById("userEmail").innerText;

  modal.style.display = "flex";
}

// TOP BUTTON
editBtn?.addEventListener(
  "click",
  openEditModal
);

// BOTTOM BUTTON
bottomEditBtn?.addEventListener(
  "click",
  openEditModal
);

  // CLOSE MODAL
  closeModalBtn.addEventListener("click", () => {

    modal.style.display = "none";
  });

  // SAVE PROFILE
  saveProfileBtn.addEventListener("click", async () => {

    const name =
      document.getElementById("editName").value;

    const email =
      document.getElementById("editEmail").value;

    try {

      const response = await fetch(
        `${API_BASE_URL}/api/profile/update`,
        {
          method: "PUT",

          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${getToken()}`
          },

          body: JSON.stringify({
            name,
            email
          })
        }
      );

      const data = await response.json();

      if (!response.ok) {

        alert(data.detail || "Update failed");
        return;
      }

      alert("Profile updated successfully");

      modal.style.display = "none";

      fetchProfile();

    } catch (error) {

      console.error(error);

      alert("Something went wrong");
    }
  });

  

document
  .getElementById("saveSettingsBtn")
  ?.addEventListener("click", saveSettings);

document
  .getElementById("changePasswordBtn")
  ?.addEventListener("click", changePassword);

document
  .getElementById("exportDataBtn")
  ?.addEventListener("click", exportData);

document
  .getElementById("deleteAccountBtn")
  ?.addEventListener("click", deleteAccount);


  // DARK MODE TOGGLE LIVE
document
  .getElementById("darkMode")
  ?.addEventListener("change", function () {

    if (this.checked) {

      document.body.classList.add("dark-mode");

      localStorage.setItem(
        "darkMode",
        "true"
      );

    } else {

      document.body.classList.remove("dark-mode");

      localStorage.setItem(
        "darkMode",
        "false"
      );
    }

});

  fetchProfile();
});


// ======================================
// SAVE SETTINGS
// ======================================

async function saveSettings() {

  try {

    const response = await fetch(
      `${API_BASE_URL}/api/profile/settings`,
      {

        method: "PUT",

        headers: {
          "Content-Type": "application/json",

          Authorization: `Bearer ${getToken()}`
        },

        body: JSON.stringify({

          dark_mode:
            document.getElementById("darkMode").checked,

          notifications:
            document.getElementById("notifications").checked,

          email_reminders:
            document.getElementById("emailReminders").checked,

          privacy_mode:
            document.getElementById("privacyMode").checked,

          language:
            document.getElementById("language").value
        })
      }
    );

    if (!response.ok) {
      throw new Error("Failed to save settings");
    }

    // SAVE DARK MODE
localStorage.setItem(
  "darkMode",
  document.getElementById("darkMode").checked
);

// // APPLY IMMEDIATELY
// applyDarkMode();

alert("Settings saved successfully");

  } catch (error) {

    console.error(error);

    alert("Failed to save settings");
  }
}


// ======================================
// CHANGE PASSWORD
// ======================================

async function changePassword() {

  const oldPassword = prompt(
    "Enter old password"
  );

  if (!oldPassword) return;

  const newPassword = prompt(
    "Enter new password"
  );

  if (!newPassword) return;

  try {

    const response = await fetch(
      `${API_BASE_URL}/api/profile/change-password`,
      {

        method: "PUT",

        headers: {
          "Content-Type": "application/json",

          Authorization: `Bearer ${getToken()}`
        },

        body: JSON.stringify({
          old_password: oldPassword,
          new_password: newPassword
        })
      }
    );

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.detail);
    }

    alert("Password changed successfully");

  } catch (error) {

    alert(error.message);
  }
}


// ======================================
// EXPORT DATA
// ======================================

async function exportData() {

  try {

    const response = await fetch(
      `${API_BASE_URL}/api/profile/export`,
      {

        headers: {
          Authorization: `Bearer ${getToken()}`
        }
      }
    );

    const data = await response.json();

    const blob = new Blob(
      [JSON.stringify(data, null, 2)],
      {
        type: "application/json"
      }
    );

    const url = URL.createObjectURL(blob);

    const a = document.createElement("a");

    a.href = url;

    a.download = "serene-data.json";

    a.click();

    URL.revokeObjectURL(url);

  } catch (error) {

    console.error(error);

    alert("Failed to export data");
  }
}


// ======================================
// DELETE ACCOUNT
// ======================================

async function deleteAccount() {

  const confirmDelete = confirm(
    "Are you sure you want to delete your account?"
  );

  if (!confirmDelete) return;

  try {

    const response = await fetch(
      `${API_BASE_URL}/api/profile/delete`,
      {

        method: "DELETE",

        headers: {
          Authorization: `Bearer ${getToken()}`
        }
      }
    );

    if (!response.ok) {
      throw new Error("Delete failed");
    }

    alert("Account deleted");

    logout();

  } catch (error) {

    console.error(error);

    alert("Failed to delete account");
  }
}


// ======================================
// LOAD SETTINGS
// ======================================


function loadSettings(data) {

  // ===============================
  // LOAD SETTINGS
  // ===============================

  document.getElementById("notifications").checked =
    data.user.notifications || false;

  document.getElementById("emailReminders").checked =
    data.user.email_reminders || false;

  document.getElementById("privacyMode").checked =
    data.user.privacy_mode || false;

  document.getElementById("language").value =
    data.user.language || "English";

  // ===============================
  // DARK MODE
  // ===============================

  // Get latest value from localStorage
  const savedDarkMode =
    localStorage.getItem("darkMode") === "true";

  // Set toggle
  document.getElementById("darkMode").checked =
    savedDarkMode;

  // Apply class
  if (savedDarkMode) {

    document.body.classList.add("dark-mode");

  } else {

    document.body.classList.remove("dark-mode");
  }
}