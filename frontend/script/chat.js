console.log("chat.js loaded");

let chatInitialized = false;
let messageInput, sendBtn, chatMessages;
let isSending = false;

// ================= PAGE DEBUG =================
window.addEventListener("pageshow", () => {
  console.log("Page restored - not resetting chat");
});

window.addEventListener("beforeunload", () => {
  console.log("⚠ Page is reloading");
});

// ================= INIT =================
window.addEventListener("DOMContentLoaded", () => {
  messageInput = document.getElementById("messageInput");
  sendBtn = document.getElementById("sendBtn");
  chatMessages = document.getElementById("chatMessages");

  restoreChatState();

  console.log("SendBtn:", sendBtn);

  if (!sendBtn || !messageInput || !chatMessages) {
    console.error("Chat elements missing");
    return;
  }

  // SAFE CLICK HANDLER
  setupEmojiPicker();
  sendBtn.onclick = function (e) {
    e.preventDefault();
    e.stopPropagation();
    console.log("Send button clicked");
    sendMessage();
  };

  // SAFE ENTER HANDLER
  messageInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter") {
      e.preventDefault();
      e.stopPropagation();
      console.log("Enter pressed");
      sendMessage();
    }
  });

  handleMeditation();
});

// ================= CHAT SEND =================
async function sendMessage() {
  console.log("sendMessage started");

  if (isSending) {
    console.log("Already sending");
    return;
  }

  const message = messageInput.value.trim();
  console.log("Message value:", message);

  if (!message) {
    console.log("Message empty");
    return;
  }

  isSending = true;

  appendMessage("user", message);
  messageInput.value = "";

  try {
    showTyping();

    console.log("Calling /chat API...");

    const data = await apiRequest("/chat", "POST", {
      message: message,
    });

    console.log("API response:", data);

    removeTyping();

    if (data && data.reply) {
      appendMessage("bot", data.reply);

      if (data.emotion?.label) {
        appendMessage("bot", `<small>Emotion: ${data.emotion.label}</small>`);
      }
    } else {
      appendMessage("bot", "⚠ Invalid response from server");
    }
  } catch (err) {
    removeTyping();
    console.error("Chat Error:", err);
    appendMessage("bot", "⚠ Backend error");
  } finally {
    isSending = false;
  }
}

// ================= APPEND MESSAGE =================
function appendMessage(sender, text) {
  if (!chatMessages) return;

  const msg = document.createElement("div");
  msg.className = `message ${sender}`;

  const content = document.createElement("div");
  content.className = "message-content";
  content.textContent = text;

  msg.appendChild(content);
  chatMessages.appendChild(msg);

  // 🔥 FIX: delay scroll + save together
  requestAnimationFrame(() => {
  chatMessages.scrollTop = chatMessages.scrollHeight;

  setTimeout(() => {
    saveChatState();   // 🔥 delayed save prevents jump
  }, 0);
});
}

function saveChatState() {
  localStorage.setItem("chat_backup", chatMessages.innerHTML);
}

function restoreChatState() {
  const saved = localStorage.getItem("chat_backup");

  if (saved) {
    chatMessages.innerHTML = saved;

    // 🔥 FORCE SCROLL AFTER RESTORE
    setTimeout(() => {
      chatMessages.scrollTop = chatMessages.scrollHeight;
    }, 0);
  }
}

// ================= TYPING =================
function showTyping() {
  removeTyping();

  const div = document.createElement("div");
  div.id = "typing";
  div.className = "message bot";
  div.innerHTML = `<div class="message-content">Typing...</div>`;

  chatMessages.appendChild(div);

  requestAnimationFrame(() => {
    chatMessages.scrollTop = chatMessages.scrollHeight;
  });
}

function removeTyping() {
  const t = document.getElementById("typing");
  if (t) t.remove();
}

// ================= MEDITATION =================
function handleMeditation() {
  if (chatInitialized) return;

  const params = new URLSearchParams(window.location.search);
  const exercise = params.get("exercise");

  if (!exercise) return;

  chatInitialized = true;

  window.history.replaceState({}, document.title, "chat.html");

  const text = `Let's begin ${exercise} exercise together. Relax and follow me.`;

  setTimeout(() => {
    appendMessage("user", `I'd like to try ${exercise}`);
    appendMessage("bot", text);
    startMeditationVoice(text);
  }, 100);
}

// ================= VOICE =================
const voiceModal = document.getElementById("voiceModal");
const closeVoice = document.getElementById("closeVoice");
const endSession = document.getElementById("endSession");

function startMeditationVoice(text) {
  if (!voiceModal) return;

  voiceModal.classList.add("active");

  const subtitle = voiceModal.querySelector(".voice-subtitle");
  if (subtitle) subtitle.textContent = "Speaking...";

  speechSynthesis.cancel();

  const utterance = new SpeechSynthesisUtterance(text);
  utterance.rate = 0.95;

  utterance.onend = () => {
    voiceModal.classList.remove("active");
  };

  speechSynthesis.speak(utterance);
}

function stopVoice() {
  speechSynthesis.cancel();

  if (voiceModal) {
    voiceModal.classList.remove("active");
  }
}

closeVoice?.addEventListener("click", stopVoice);
endSession?.addEventListener("click", stopVoice);

// unlock audio once user interacts
window.addEventListener("click", () => {
  speechSynthesis.resume();
});

function setupEmojiPicker() {
  const button = document.getElementById("emojiBtn");

  const picker = new EmojiButton({
    position: "top-start", // 👈 THIS FIXES YOUR ISSUE
  });

  let isOpen = false;

  picker.on("emoji", (emoji) => {
    messageInput.value += emoji;
    messageInput.focus();

    picker.hidePicker(); // 👈 closes picker after selection
    isOpen = false;
  });

  button.addEventListener("click", () => {
    if (isOpen) {
      picker.hidePicker();
      isOpen = false;
    } else {
      picker.showPicker(button);
      isOpen = true;
    }
  });
}

function scrollToBottom() {
  chatMessages.scrollTop = chatMessages.scrollHeight;
}
