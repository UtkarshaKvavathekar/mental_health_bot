// 🔐 Check login
const auth = checkAuth();
const user = auth.user;
const token = auth.token;
const userId = auth.userId;
const loadingEl = document.getElementById("historyLoading");

// ===============================
// 🚀 Load History from Backend
// ===============================
async function loadHistory() {
  loadingEl.style.display = "block";
  try {
    const data = await apiRequest(`/history/${userId}`);
    updateUI(data);

  } catch (err) {
    console.log(err);

  document.getElementById("historyLoading").innerHTML =
    "Failed to load history. Please try again later.";


    updateUI({
      totalSessions: 0,
      totalMinutes: 0,
      streak: 0,
      sessions: [],
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
  // Stats
  document.getElementById("totalSessions").innerText =
    data.totalSessions ?? 0;

  document.getElementById("totalMinutes").innerText =
    data.totalMinutes ?? 0;

  document.getElementById("streakCount").innerText =
    data.streak ?? 0;

  const container = document.getElementById("historyContainer");

  // No sessions
  if (!data.sessions || data.sessions.length === 0) {
    container.innerHTML =
      "<div class='empty'>🌿 Your mindfulness journey begins here. Complete a meditation session to see your progress.</div>"
    return;
  }

  // Table creation
  let table = `
    <table>
      <thead>
        <tr>
          <th>Date</th>
          <th>Exercise</th>
          <th>Duration (min)</th>
        </tr>
      </thead>
      <tbody>
  `;

  data.sessions.forEach((session) => {
    table += `
      <tr>
        <td>${session.date ?? "-"}</td>
        <td>${session.exercise ?? "-"}</td>
        <td>${session.duration ?? 0}</td>
      </tr>
    `;
  });

  table += "</tbody></table>";

  container.innerHTML = table;
}

// ===============================
// 🗑 Clear History (Backend)
// ===============================
async function clearHistory() {
  if (!confirm("Are you sure you want to delete all history?")) return;

  try {
    const res = await fetch(`http://127.0.0.1:8000/history/${userId}`,
      {
        method: "DELETE",
        headers: {
          "Content-Type": "application/json",
          Authorization: "Bearer " + token,
        },
      }
    );

    if (!res.ok) throw new Error("Delete failed");

    location.reload();
  } catch (err) {
    console.log("Backend not ready or delete failed");
  }
}

// ===============================
// 🔙 Go Dashboard
// ===============================
function goDashboard() {
  window.location.href = "dashboard.html";
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
loadHistory();