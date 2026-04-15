window.MeditationEngine = (function () {

  let isRunning = false;

  function wait(ms) {
    return new Promise(res => setTimeout(res, ms));
  }

  function speak(text) {
    speechSynthesis.cancel();
    const u = new SpeechSynthesisUtterance(text);
    u.rate = 0.95;
    speechSynthesis.speak(u);
  }

  function showMessage(text) {
    const chat = document.getElementById("chatMessages");
    if (!chat) return;

    const div = document.createElement("div");
    div.className = "message bot";
    div.innerHTML = `<div class="message-content">${text}</div>`;
    chat.appendChild(div);
    chat.scrollTop = chat.scrollHeight;
  }

  // ================= INTRO STEP (IMPORTANT) =================
  async function intro(type) {

    const modal = document.getElementById("voiceModal");

    if (modal) {
      modal.classList.add("active");
      const subtitle = modal.querySelector(".voice-subtitle");
      if (subtitle) subtitle.textContent = "Starting...";
    }

    const msg = `Great choice! Let's begin ${type} exercise together. Relax and follow me.`;

    showMessage(msg);
    speak(msg);

    await wait(3000);

    if (modal) modal.classList.remove("active");

    startExercise(type);
  }

  // ================= EXERCISES =================

  async function breathing() {
    isRunning = true;

    for (let i = 0; i < 3; i++) {
      if (!isRunning) break;

      showMessage("Inhale 🌬️");
      speak("Inhale");
      await wait(3000);

      showMessage("Hold ✋");
      speak("Hold");
      await wait(3000);

      showMessage("Exhale 🌿");
      speak("Exhale");
      await wait(3000);
    }
  }

  async function grounding() {
    const steps = [
      "5 things you see",
      "4 things you touch",
      "3 things you hear",
      "2 things you smell",
      "1 thing you feel"
    ];

    for (let s of steps) {
      showMessage(s);
      speak(s);
      await wait(2500);
    }
  }

  async function bodyscan() {
    const parts = ["Head", "Shoulders", "Chest", "Arms", "Stomach", "Legs"];

    for (let p of parts) {
      showMessage("Relax your " + p);
      speak("Relax your " + p);
      await wait(2000);
    }
  }

  async function affirmations() {
    const list = ["I am safe", "I am calm", "I am strong", "I am enough"];

    for (let l of list) {
      showMessage(l);
      speak(l);
      await wait(2000);
    }
  }

  // ================= ROUTER =================
  async function startExercise(type) {

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
    }

    showMessage("Session completed 🌿");
    speak("Session completed");
  }

  return {
    intro
  };

})();