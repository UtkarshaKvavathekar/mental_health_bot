document.querySelectorAll(".relief-card").forEach(card => {
  card.addEventListener("click", () => {

    const technique = card.getAttribute("data-technique");

    // 🔥 switch UI
    document.getElementById("reliefUI").style.display = "none";
    document.getElementById("meditationUI").style.display = "flex";

    // 🔥 start meditation
    window.MeditationEngine.intro(technique);
  });
});