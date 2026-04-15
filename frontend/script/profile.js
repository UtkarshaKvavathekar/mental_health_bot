// 🔐 Check login
const auth = checkAuth();
const user = auth.user;
const token = auth.token;
const userId = auth.userId;
const loadingEl = document.getElementById("profileLoading");

// ===============================
// 🚀 Load Profile
// ===============================
async function loadProfile() {
  loadingEl.style.display = "block";
  try {
    const data = await apiRequest(`/profile/${user.id}`);

  } catch (err) {
    console.log(err);

  document.getElementById("profileLoading").innerHTML =
    "Failed to load profile. Please try again later.";

    updateUI({
      name: "User",
      email: "N/A",
      memberSince: "N/A",
      id: user.id,
      messagesSent: 0,
      meditationSessions: 0,
      totalMeditationTime: 0,
      streak: 0,
      moodEntries: 0,
      daysUsingApp: 0,
      moodHistory: [],
      recentMeditations: [],
    });
  }
  finally{
    loadingEl.style.display = "none";
  }
}

// ===============================
// 🎯 Update UI
// ===============================
function updateUI(data) {
  // Avatar
  const avatar = document.getElementById("avatar");
  if (avatar)
    avatar.innerText = (data.name || "U").charAt(0);

  // Basic Info
  document.getElementById("userName").innerText =
    data.name || "User";

  document.getElementById("userEmail").innerText =
    "Email: " + (data.email || "N/A");

  document.getElementById("memberSince").innerText =
    "Member Since: " + (data.memberSince || "N/A");

  document.getElementById("userId").innerText =
    "User ID: #" + (data.id || user.id);

  // Stats (safe update)
  const stats = document.querySelectorAll(".stat-box p");

  if (stats.length >= 6) {
    stats[0].innerText = data.messagesSent ?? 0;
    stats[1].innerText = data.meditationSessions ?? 0;
    stats[2].innerText = (data.totalMeditationTime ?? 0) + " min";
    stats[3].innerText = (data.streak ?? 0) + " Days";
    stats[4].innerText = data.moodEntries ?? 0;
    stats[5].innerText = data.daysUsingApp ?? 0;
  }

  // Mood Chart
  renderChart(data.moodHistory || []);

  // Meditation History
  renderMeditation(data.recentMeditations || []);
}

// ===============================
// 📊 Mood Chart
// ===============================
function renderChart(moodData) {
  const container = document.getElementById("moodChart");
  if (!container) return;

  container.innerHTML = "";

  if (!moodData.length) {
    container.innerHTML = "<p>No mood data yet</p>";
    return;
  }

  moodData.forEach((item) => {
    const barItem = document.createElement("div");
    barItem.className = "bar-item";

    const bar = document.createElement("div");
    bar.className = "bar";
    bar.style.height = (item.value || 0) + "%";

    const label = document.createElement("div");
    label.className = "bar-label";
    label.innerText = item.day || "";

    barItem.appendChild(bar);
    barItem.appendChild(label);
    container.appendChild(barItem);
  });
}

// ===============================
// 🧘 Meditation List
// ===============================
function renderMeditation(list) {
  const container = document.getElementById("meditationList");
  if (!container) return;

  if (!list || list.length === 0) {
    container.innerHTML = "<p>No sessions yet 🧘</p>";
    return;
  }

  container.innerHTML = "";

  list.forEach((item) => {
    const div = document.createElement("div");
    div.className = "meditation-session";

    div.innerHTML = `
      <p>🧘 ${item.exercise || "-"}</p>
      <p>${item.time || "-"} • ${item.duration || 0} min</p>
      <p>Mood: ${item.moodBefore || "-"} → ${item.moodAfter || "-"}</p>
    `;

    container.appendChild(div);
  });
}

// ===============================
// 🔒 Prevent Back Navigation
// ===============================
window.history.pushState(null, "", window.location.href);
window.onpopstate = function () {
  window.history.pushState(null, "", window.location.href);
};

// ===============================
// 🚀 INIT
// ===============================
loadProfile();