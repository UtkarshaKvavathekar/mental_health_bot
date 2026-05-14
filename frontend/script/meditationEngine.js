window.MeditationEngine = (function () {
  let isRunning = false;
  let isPaused = false;
  let sessionStartTime = null;

  function startStars() {
    const canvas = document.getElementById("starsCanvas");
    if (!canvas) return;
    const ctx = canvas.getContext("2d");

    let w = (canvas.width = canvas.offsetWidth);
    let h = (canvas.height = canvas.offsetHeight);

    const stars = Array.from({ length: 120 }, () => ({
      x: Math.random() * w,
      y: Math.random() * h,
      r: Math.random() * 1.5 + 0.5,
      v: Math.random() * 0.3 + 0.1,
    }));

    function draw() {
      ctx.clearRect(0, 0, w, h);
      ctx.fillStyle = "#fff";

      for (let s of stars) {
        s.y += s.v;
        if (s.y > h) s.y = 0;

        ctx.beginPath();
        ctx.arc(s.x, s.y, s.r, 0, Math.PI * 2);
        ctx.fill();
      }
      requestAnimationFrame(draw);
    }

    draw();
  }

  function setupReframe() {
    const btn = document.getElementById("reframeBtn");
    const input = document.getElementById("reframeInput");
    const output = document.getElementById("reframeOutput");

    if (!btn) return;

    btn.onclick = () => {
      const text = input.value.trim();
      if (!text) return;

      const response =
        "Try seeing it this way: This is temporary, and you can learn from it.";
      output.innerText = response;
      speak(response);
    };
  }

  async function controlledWait(seconds) {
    for (let i = seconds; i > 0; i--) {
      if (!isRunning) return false;

      while (isPaused) {
        await wait(200);
      }

      await wait(1000);
    }
    return true;
  }

  function wait(ms) {
    return new Promise((res) => setTimeout(res, ms));
  }

  function speak(text) {
    return new Promise((resolve) => {
      const cleanText = text.replace(/[^\p{L}\p{N}\p{P}\p{Z}]/gu, "");

      speechSynthesis.cancel();

      const u = new SpeechSynthesisUtterance(cleanText);
      u.rate = 0.95;

      u.onend = () => {
        resolve(); // 🔥 wait until speaking finishes
      };

      speechSynthesis.speak(u);
    });
  }
  function showMessage(text) {
    const title = document.getElementById("title");
    const subtitle = document.getElementById("subtitle");

    if (title) title.innerText = "Meditation";
    if (subtitle) subtitle.innerText = text;
  }

  // ================= INTRO STEP (IMPORTANT) =================
  async function intro(type) {
    // 🔥 show intro UI
    document.getElementById("introBox").style.display = "flex";

    // 🔥 hide everything else
    document.getElementById("circle").style.display = "none";
    document.getElementById("groundingBox").style.display = "none";
    document.getElementById("bodyScanBox").style.display = "none";
    document.getElementById("affirmationBox").style.display = "none";
    document.getElementById("sleepBox").style.display = "none";
    document.getElementById("reframeBox").style.display = "none";

    const msg = `Great choice! Let's begin ${type} exercise together. Relax and follow me.`;

    showMessage(msg);

    await speak(msg); // 🔥 wait until speech ends

    // 🔥 hide intro
    document.getElementById("introBox").style.display = "none";

    // 🔥 NOW show correct UI
    startExercise(type);
  }

  // ================= EXERCISES =================

  //let isRunning = false;

  function sleep(ms) {
    return new Promise((resolve) => setTimeout(resolve, ms));
  }

  async function breathing() {
    isRunning = true;

    const circle = document.getElementById("circle");
    const subtitle = document.getElementById("subtitle");

    circle.classList.remove("expand");
    circle.classList.remove("shrink");
    void circle.offsetWidth;

    await wait(300);

    const steps = [
      { text: "Inhale", time: 4, action: "expand" },
      { text: "Hold", time: 7, action: "hold" },
      { text: "Exhale", time: 8, action: "shrink" },
    ];

    while (isRunning) {
      for (let step of steps) {
        if (!isRunning) return;

        subtitle.innerText = step.text;

        speechSynthesis.cancel();
        speechSynthesis.speak(new SpeechSynthesisUtterance(step.text));

        if (step.action === "expand") {
          circle.classList.add("expand");
          circle.classList.remove("shrink");
        } else if (step.action === "shrink") {
          circle.classList.add("shrink");
          circle.classList.remove("expand");
        }

        for (let i = step.time; i > 0; i--) {
          if (!isRunning) return;

          while (isPaused) {
            await wait(200);
          }

          subtitle.innerText = `${step.text} (${i})`;
          await wait(1000);
        }
      }
    }

    subtitle.innerText = "Session stopped 🌿";
  }

  async function grounding() {
    isRunning = true;

    const steps = [
      "👀 5 things you see",
      "✋ 4 things you touch",
      "👂 3 things you hear",
      "👃 2 things you smell",
      "😋 1 thing you taste",
    ];

    for (let s of steps) {
      if (!isRunning) return false;

      document.getElementById("groundingStep").innerText = s;
      speak(s);

      if (!(await controlledWait(3))) return false;
    }

    return true;
  }

  async function bodyscan() {
    isRunning = true;

    const parts = [
      { id: "head", text: "Relax your forehead and unclench your jaw" },
      { id: "shoulders", text: "Drop your shoulders and release tension" },
      { id: "chest", text: "Take a deep breath into your chest" },
      { id: "arms", text: "Let your arms feel heavy and relaxed" },
      { id: "stomach", text: "Soften your stomach and breathe gently" },
      { id: "legs", text: "Relax your legs and feel grounded" },
    ];

    for (let p of parts) {
      if (!isRunning) return false;

      // highlight part
      document
        .querySelectorAll(".part")
        .forEach((el) => el.classList.remove("active"));
      const current = document.getElementById(p.id);
      current.classList.add("active");

      // add pulse animation
      current.classList.add("pulse");

      showMessage(p.text);
      speak(p.text);

      if (!(await controlledWait(3))) return false;

      current.classList.remove("pulse");
    }

    return true;
  }

  async function affirmations() {
    isRunning = true;

    const affirmText = document.getElementById("affirmText");

    const list = [
      "I am safe 🌿",
      "I am calm 🧘",
      "I am strong 💪",
      "I am enough ❤️",
    ];

    for (let text of list) {
      if (!isRunning) return false;

      affirmText.innerText = text;

      // animation
      affirmText.classList.remove("fade");
      void affirmText.offsetWidth; // restart animation
      affirmText.classList.add("fade");

      speak(text);

      if (!(await controlledWait(3))) return false;
    }

    return true;
  }

  async function sleep() {
    isRunning = true;

    const el = document.getElementById("sleepText");
    startStars();

    const steps = [
      "Close your eyes",
      "Take a slow deep breath",
      "Imagine a peaceful place",
      "Let your body feel heavy",
      "Drift into calmness",
    ];

    for (let s of steps) {
      if (!isRunning) return false;

      el.innerText = s;
      speak(s);

      if (!(await controlledWait(4))) return false;
    }

    return true;
  }

  async function reframe() {
    isRunning = true;

    const steps = [
      "Think about what is bothering you",
      "Ask yourself: Is this permanent?",
      "What is one positive angle?",
      "What can you learn from this?",
      "You are stronger than this situation",
    ];

    for (let s of steps) {
      if (!isRunning) return false;

      showMessage(s);
      speak(s);

      if (!(await controlledWait(4))) return false;
    }

    return true;
  }

  // ================= ROUTER =================

  function toggleUI(type) {
    const circle = document.getElementById("circle");
    const groundingBox = document.getElementById("groundingBox");
    const bodyScanBox = document.getElementById("bodyScanBox");
    const affirmBox = document.getElementById("affirmationBox");
    const sleepBox = document.getElementById("sleepBox");
    const reframeBox = document.getElementById("reframeBox");

    // hide all first
    [
      circle,
      groundingBox,
      bodyScanBox,
      affirmBox,
      sleepBox,
      reframeBox,
    ].forEach((el) => el && (el.style.display = "none"));

    if (type === "sleep") sleepBox.style.display = "block";
    else if (type === "reframe") reframeBox.style.display = "block";
    else if (type === "grounding") groundingBox.style.display = "block";
    else if (type === "bodyscan") bodyScanBox.style.display = "block";
    else if (type === "affirmations") affirmBox.style.display = "block";
    else circle.style.display = "block";
  }

  async function startExercise(type) {
    sessionStartTime = Date.now();
    toggleUI(type);
    
    switch (type) {
      case "breathing":
        await breathing();
        break;
      case "grounding":
        await grounding();
        break;
      case "bodyscan":
        await bodyscan();
        break;
      case "affirmations":
        await affirmations();
        break;
      case "sleep":
        await sleep();
        break;

      case "reframe":
        await reframe();
        break;
    }

    showMessage("Session completed 🌿");
    speak("Session completed");
    const auth = checkAuth();

const userId = auth.userId;

const sessionEndTime = Date.now();

const durationSeconds =
  Math.floor(
    (sessionEndTime - sessionStartTime) / 1000
  );

const durationMinutes =
  Math.max(
    1,
    Math.round(durationSeconds / 60)
  );

await fetch(
  "http://127.0.0.1:8000/meditation/save",
  {

    method: "POST",

    headers: {
      "Content-Type": "application/json"
    },

    body: JSON.stringify({

      user_id: userId,

      exercise: type,

      duration: durationMinutes
    })
  }
);
  }

  return {
    intro,
    pause: () => {
      isPaused = true;
      speechSynthesis.pause();
    },
    resume: () => {
      isPaused = false;
      speechSynthesis.resume();
    },
    stop: () => {
      isRunning = false;
      isPaused = false;
      speechSynthesis.cancel();
    },
  };
})();

document.addEventListener("DOMContentLoaded", () => {
  document.getElementById("pauseBtn").onclick = () => {
    window.MeditationEngine.pause();
  };

  document.getElementById("resumeBtn").onclick = () => {
    window.MeditationEngine.resume();
  };

  document.getElementById("stopBtn").onclick = () => {
    window.MeditationEngine.stop();
    document.getElementById("subtitle").innerText = "Stopped";
  };
});
