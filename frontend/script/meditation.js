document.querySelectorAll(".relief-card").forEach(card => {
  card.addEventListener("click", () => {

    const technique = card.getAttribute("data-technique");

    // go to chat page WITH PARAM
    window.location.href = `chat.html?exercise=${technique}`;
  });
});