console.log("NEW CHAT.JS LOADED");

const API = "http://127.0.0.1:8000";

let activeChatId = null;
let isSending = false;

let chatMessages;
let chatHistory;
let messageInput;
let chatSidebar;

/* ================= INIT ================= */

document.addEventListener("DOMContentLoaded", async () => {
  chatMessages = document.getElementById("chatMessages");
  chatHistory = document.getElementById("chatHistory");
  messageInput = document.getElementById("messageInput");
  chatSidebar = document.getElementById("chatSidebar");

  document.getElementById("sendBtn").addEventListener("click", (e) => {
    e.preventDefault();
    sendMessage();
  });

  document.getElementById("newChatBtn").addEventListener("click", (e) => {
    e.preventDefault();
    newChat();
  });

  messageInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  });

  document.getElementById("menuBtn").addEventListener("click", (e) => {
    e.preventDefault();
    chatSidebar.classList.toggle("open");
  });

  renderWelcome();
  await loadChats();
});

/* ================= NEW CHAT ================= */

function newChat() {
  activeChatId = null;
  chatMessages.innerHTML = "";
  renderWelcome();
  highlightActive();
  messageInput.focus();
}

/* ================= WELCOME ================= */

function renderWelcome() {
  appendMessage("bot", "Hello 🌿 I'm Serene. Tell me how you're feeling today.");
}

/* ================= SEND ================= */

async function sendMessage() {
  if (isSending) return;

  const message = messageInput.value.trim();
  if (!message) return;

  const user = JSON.parse(localStorage.getItem("user"));
  const user_id = user?.id;

  if (!user_id) {
    appendMessage("bot", "⚠ Please login again");
    return;
  }

  isSending = true;

  appendMessage("user", message);
  messageInput.value = "";

  showTyping();

  try {
    const res = await fetch(`${API}/chat`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        message,
        user_id: Number(user_id),
        chat_id: activeChatId,
      }),
    });

    if (!res.ok) {
      throw new Error("Backend request failed");
    }

    const data = await res.json();

    removeTyping();

    appendMessage("bot", data.reply);

    const wasNewChat = !activeChatId;

    if (wasNewChat) {
      activeChatId = String(data.chat_id);
    }

    await loadChats();
    highlightActive();
  } catch (error) {
    removeTyping();
    appendMessage("bot", "Backend error.");
    console.error(error);
  }

  isSending = false;
}

/* ================= LOAD SIDEBAR ================= */

async function loadChats() {
  const user = JSON.parse(localStorage.getItem("user"));
  const user_id = user?.id || 1;

  try {
    const res = await fetch(`${API}/chats/${user_id}`);
    const chats = await res.json();

    chatHistory.innerHTML = "";

    chats.forEach((chat) => {
      const item = document.createElement("div");
      item.className = "chat-item";
      item.dataset.id = String(chat.chat_id);

      item.innerHTML = `
        <div class="chat-title">${chat.title}</div>
        <div class="chat-actions">
          <span class="chat-action rename">✏️</span>
          <span class="chat-action delete">🗑</span>
        </div>
      `;

      item.addEventListener("click", async () => {
        await openChat(chat.chat_id);
      });

      const renameBtn = item.querySelector(".rename");
      const deleteBtn = item.querySelector(".delete");

      renameBtn.addEventListener("click", async (e) => {
        e.preventDefault();
        e.stopPropagation();

        const title = prompt("Rename chat", chat.title);
        if (!title || !title.trim()) return;

        await fetch(`${API}/chat/${chat.chat_id}/rename`, {
          method: "PUT",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            title: title.trim(),
          }),
        });

        await loadChats();
      });

      deleteBtn.addEventListener("click", async (e) => {
        e.preventDefault();
        e.stopPropagation();

        const confirmDelete = confirm("Delete this chat?");
        if (!confirmDelete) return;

        await fetch(`${API}/chat/${chat.chat_id}`, {
          method: "DELETE",
        });

        if (activeChatId === String(chat.chat_id)) {
          newChat();
        }

        await loadChats();
      });

      chatHistory.appendChild(item);
    });

    highlightActive();
  } catch (error) {
    console.error("Failed to load chats", error);
  }
}

/* ================= OPEN CHAT ================= */

async function openChat(chatId) {
  try {
    const res = await fetch(`${API}/chat/${chatId}`);
    const data = await res.json();

    activeChatId = String(chatId);

    chatMessages.innerHTML = "";

    data.messages.forEach((m) => {
      appendMessage("user", m.message);
      appendMessage("bot", m.response);
    });

    highlightActive();
    chatSidebar.classList.remove("open");
  } catch (error) {
    console.error("Failed to open chat", error);
  }
}

/* ================= HIGHLIGHT ================= */

function highlightActive() {
  document.querySelectorAll(".chat-item").forEach((item) => {
    item.classList.toggle(
      "active",
      String(item.dataset.id) === String(activeChatId)
    );
  });
}

/* ================= MESSAGE ================= */

function appendMessage(type, text) {
  const row = document.createElement("div");
  row.className = `message-row ${type}`;

  const bubble = document.createElement("div");
  bubble.className = "message-bubble";
  bubble.textContent = text;

  row.appendChild(bubble);
  chatMessages.appendChild(row);

  chatMessages.scrollTop = chatMessages.scrollHeight;
}

/* ================= TYPING ================= */

function showTyping() {
  removeTyping();

  const row = document.createElement("div");
  row.id = "typing";
  row.className = "message-row bot";

  row.innerHTML = `
    <div class="message-bubble">Typing...</div>
  `;

  chatMessages.appendChild(row);
  chatMessages.scrollTop = chatMessages.scrollHeight;
}

function removeTyping() {
  document.getElementById("typing")?.remove();
}