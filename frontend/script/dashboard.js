// 🔐 Check login
const auth = checkAuth();
const user = auth.user;
const token = auth.token;
const userId = auth.userId;
const loadingEl = document.getElementById("dashboardLoading");

// 🚀 Load Dashboard
async function loadDashboard() {
  loadingEl.style.display = "block";

  try {
    const data = await apiRequest(`/dashboard/${userId}`);
    updateUI(data);
  } catch (err) {
    console.log(err);

  document.getElementById("dashboardLoading").innerHTML =
    "Failed to load dashboard.";

    // fallback UI
    updateUI({
      name: "User",
      meditationMinutes: 0,
      chatMessages: 0,
      streak: 0,
      moodHistory: [],
      todayFocus: "Stay positive today 🌿",
      focusTip: "Take small breaks",
      insight: "You are doing great!",
    });
  }
  finally {
    loadingEl.style.display = "none";
  }
}

// 🎯 Update UI
function updateUI(data) {
  document.getElementById("welcome").innerText =
    "Welcome " + (data.name || "User");

  const streakEl = document.getElementById("streakText");

  if (streakEl) {
    streakEl.innerText =
      "🔥 You're on a " +
      (data.streak ?? 0) +
      "-day check-in streak. Keep going!";
  }

  // 📊 Stats
  const stats = document.querySelectorAll(".stat-box p");
  if (stats.length >= 3) {
    stats[0].innerText = data.meditationMinutes ?? "-";
    stats[1].innerText = data.chatMessages ?? "-";
    stats[2].innerText = (data.streak ?? 0) + " Days";
  }

  // 📈 Chart
  renderChart(data.moodHistory || []);

  // 🎯 Focus
  document.getElementById("todayFocus").innerText =
    data.todayFocus || "No focus available";

  document.getElementById("focusTip").innerText =
    data.focusTip || "Stay mindful today";

  // 💡 Insight
  document.getElementById("insight").innerHTML =
    "💡 <strong>Pro Tip:</strong> " +
    (data.insight || "Take care of yourself");
}

// 📊 Mood Chart
function renderChart(moodData) {
  const container = document.getElementById("chartBars");
  if (!container) return;

  container.innerHTML = "";

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

// 😊 Save Mood (with small UX improvement)
document.querySelectorAll(".mood-btn").forEach((btn) => {
  btn.addEventListener("click", async () => {
    const mood = btn.innerText;

    // UX improvement: prevent spam clicks
    btn.disabled = true;

    try {
      await fetch("http://localhost:8000/mood", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: "Bearer " + token,
        },
        body: JSON.stringify({
          user_id: userId,
          mood: mood,
        }),
      });
    } catch (err) {
      console.log("Backend not ready");
    }

    // re-enable button
    setTimeout(() => {
      btn.disabled = false;
    }, 1000);
  });
});

// 🔒 Prevent back navigation
window.history.pushState(null, "", window.location.href);
window.onpopstate = function () {
  window.history.pushState(null, "", window.location.href);
};

// 🚀 INIT
loadDashboard();