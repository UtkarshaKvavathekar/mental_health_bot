console.log("chat.js loaded");

let chatInitialized = false;
let messageInput, sendBtn, chatMessages;
let isSending = false;

let chats = [];
let activeChatId = null;

const API_BASE = "http://127.0.0.1:8000";
const auth = checkAuth();
const userId = auth.userId;
const CHAT_STORAGE_KEY =
  `serene_chats_${userId}`;

const ACTIVE_CHAT_KEY =
  `serene_active_chat_${userId}`;

async function apiRequest(path, method = "GET", body = null) {
  const options = {
    method,
    headers: {
      "Content-Type": "application/json",
    },
  };

  if (body !== null) {
    options.body = JSON.stringify(body);
  }

  const response = await fetch(`${API_BASE}${path}`, options);

  if (!response.ok) {
    const text = await response.text();
    throw new Error(`API ${response.status}: ${text}`);
  }

  return await response.json();
}

// ================= PAGE DEBUG =================
window.addEventListener("pageshow", () => {
  console.log("Page restored - not resetting chat");
});

// ================= INIT =================
window.addEventListener("DOMContentLoaded", async () => {
  messageInput = document.getElementById("messageInput");
  sendBtn = document.getElementById("sendBtn");

  chatMessages = document.getElementById("chatMessages");
  initializeSidebar();

  await restoreChatState();

  console.log("SendBtn:", sendBtn);
  console.log("messageInput:", messageInput);
  console.log("chatMessages:", chatMessages);

  if (!sendBtn || !messageInput || !chatMessages) {
    console.error("Chat elements missing");
    return;
  }

  // SAFE CLICK HANDLER
  setupEmojiPicker();
  sendBtn.addEventListener("click", (e) => {
    e.preventDefault();
    e.stopPropagation();

    console.log("Send button clicked");

    sendMessage();
  });

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

  const active = chats.find((c) => c.id === activeChatId);
  if (active && active.title === "New Chat") {
    active.title = message.slice(0, 24);
    renderSidebar();
  }

  messageInput.value = "";

  try {
    showTyping();

    console.log("Calling /chat API...");

    const data = await apiRequest("/chat", "POST", {
      message: message,
      chat_id:

  activeChatId &&
  chats.some(c => c.id === activeChatId)

    ? activeChatId

    : null,
      user_id: userId,
    });

    if (data.chat_id) {

  // 🚀 update active chat

  activeChatId = data.chat_id;

  // remove temporary draft chats

  chats = chats.filter(
    (c) => c.id !== null
  );

  // check if chat already exists

  const existing = chats.find(
    (c) => c.id === data.chat_id
  );

  // create only if missing

  if (!existing) {

    chats.unshift({

      id: data.chat_id,

      title: message.slice(0, 24),
    });
  }

  // 🚀 VERY IMPORTANT
  // preserve current active chat

  renderSidebar();

  saveChatState();
}

    console.log("API response:", data);

    removeTyping();

    if (data && data.reply) {
      appendMessage("bot", data.reply);
    } else {
      appendMessage("bot", "⚠ Invalid response from server");
    }
  } catch (err) {
    removeTyping();
    console.error("Chat Error:", err);
    appendMessage("bot", `⚠ Error: ${err.message}`);
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
      // only save if chat already exists
      if (activeChatId !== null) {
        saveChatState();
      }
    }, 0);
  });
}

function saveChatState() {
  const active = chats.find((c) => c.id === activeChatId);
  if (!active) return;

  active.messages = chatMessages.innerHTML;

  localStorage.setItem(CHAT_STORAGE_KEY, JSON.stringify(chats));
  localStorage.setItem(ACTIVE_CHAT_KEY, activeChatId);
}

async function restoreChatState() {
  const storedUserId = localStorage.getItem("chat_user_id");

  if (storedUserId && storedUserId != userId) {
    activeChatId = null;

    localStorage.removeItem(CHAT_STORAGE_KEY);

    localStorage.removeItem(ACTIVE_CHAT_KEY);
  }
  try {
    const data = await apiRequest(`/api/get_chats/${userId}`, "GET");

    chats = data || [];
    const savedActiveChat = localStorage.getItem(
  ACTIVE_CHAT_KEY
);

if (savedActiveChat) {

  activeChatId = Number(savedActiveChat);
}
    chats = chats.filter(chat => chat.id);
    localStorage.setItem("chat_user_id", userId);

    if (!chats.length) {

  chats = [
    {
      id: null,
      title: "New Chat",
    },
  ];

  activeChatId = null;

} else {

  // 🚀 IMPORTANT:
  // reset to newest valid user chat

 const currentChatStillExists = chats.some(

  chat => chat.id === activeChatId
);

if (!currentChatStillExists) {

  activeChatId = chats[0]?.id || null;
}
}

    renderSidebar();

    if (activeChatId) {
      await loadChat(activeChatId);
    } else {
      chatMessages.innerHTML = `
        <div class="message bot">
          <div class="message-content">
            Hello 🌿 I'm Serene. Tell me how you're feeling today.
          </div>
        </div>
      `;
    }
  } catch (err) {
    console.error(err);
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

function initializeSidebar() {
  document
    .getElementById("newChatBtn")
    ?.addEventListener("click", createNewChat);

  document
    .getElementById("mobileSidebarToggle")
    ?.addEventListener("click", openSidebar);

  document
    .getElementById("sidebarClose")
    ?.addEventListener("click", closeSidebar);

  document
    .getElementById("sidebarOverlay")
    ?.addEventListener("click", closeSidebar);
}

function renderSidebar() {
  const container = document.getElementById("chatHistory");
  if (!container) return;

  container.innerHTML = "";

  chats.forEach((chat) => {
    const item = document.createElement("div");

    const isActive =
      (activeChatId === null && chat.id === null) || chat.id === activeChatId;

    item.className = `chat-item ${isActive ? "active" : ""}`;

    item.innerHTML = `
      <div class="chat-title">${chat.title}</div>
      <div class="chat-actions">
        <button class="chat-action-btn rename-btn">✎</button>
        <button class="chat-action-btn delete-btn">🗑</button>
      </div>
    `;

    item.addEventListener("click", () => loadChat(chat.id));

    item.querySelector(".rename-btn").addEventListener("click", (e) => {
      e.stopPropagation();
      renameChat(chat.id);
    });

    item.querySelector(".delete-btn").addEventListener("click", (e) => {
      e.stopPropagation();
      deleteChat(chat.id);
    });

    container.appendChild(item);
  });
}

function createNewChat() {
  activeChatId = null;
  const existingDraft = chats.find((chat) => chat.id === null);

  if (existingDraft) {
    activeChatId = null;
  } else {
    chats.unshift({
      id: null,
      title: "New Chat",
    });

    activeChatId = null;
  }

  chatMessages.innerHTML = `
    <div class="message bot">
      <div class="message-content">
        Hello 🌿 I'm Serene. Tell me how you're feeling today.
      </div>
    </div>
  `;

  renderSidebar();
  closeSidebar();
}

async function renameChat(id) {
  const title = prompt("Rename chat");
  if (!title) return;

  await apiRequest("/api/rename_chat", "POST", {
    chat_id: id,
    title,
  });

  await restoreChatState();
}

async function deleteChat(id) {
  await apiRequest("/api/delete_chat", "POST", {
    chat_id: id,
  });

  await restoreChatState();
}

async function loadChat(id) {
  if (!id) return;

  activeChatId = id;
  localStorage.setItem(
  ACTIVE_CHAT_KEY,
  id
);

  const data = await apiRequest(`/api/get_messages/${id}/${userId}`, "GET");

  chatMessages.innerHTML = "";

  data.messages.forEach((msg) => {
    const div = document.createElement("div");
    div.className = `message ${msg.sender}`;

    div.innerHTML = `
      <div class="message-content">${msg.text}</div>
    `;

    chatMessages.appendChild(div);
  });

  renderSidebar();
  scrollToBottom();
  closeSidebar();
}

function saveAllChats() {
  localStorage.setItem(CHAT_STORAGE_KEY, JSON.stringify(chats));
  localStorage.setItem(ACTIVE_CHAT_KEY, activeChatId);
}

function openSidebar() {
  document.getElementById("chatSidebar")?.classList.add("open");
  document.getElementById("sidebarOverlay")?.classList.add("active");
}

function closeSidebar() {
  document.getElementById("chatSidebar")?.classList.remove("open");
  document.getElementById("sidebarOverlay")?.classList.remove("active");
}
