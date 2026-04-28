// --- Configuration & State ---
const BACKEND_URL = "http://127.0.0.1:8000/ask";

const breathingExplanations = {
    'boxbreathing': "Sit straight and relax your shoulders. We'll practice box breathing together...",
    'breathing': "Find a comfortable position and close your eyes. We'll use the 4-7-8 technique...",
    'anxietybreathing': "Take a moment to settle in. This will help calm your mind...",
    'grounding': "Let's connect with your senses to ground you in the present moment."
};

const breathingTechniques = ['boxbreathing', 'breathing', 'anxietybreathing', 'grounding'];
let currentTechnique = null;
let currentTechniqueFile = null;

// --- DOM Elements ---
const chatToggle = document.getElementById('chatToggle');
const reliefToggle = document.getElementById('reliefToggle');
const chatSection = document.getElementById('chatSection');
const reliefSection = document.getElementById('reliefSection');
const messageInput = document.getElementById('messageInput');
const sendBtn = document.getElementById('sendBtn');
const chatMessages = document.getElementById('chatMessages');
const voiceModal = document.getElementById('voiceModal');
const startSession = document.getElementById('startSession');

// --- Navigation Logic ---
chatToggle.addEventListener('click', () => {
    chatToggle.classList.add('active');
    reliefToggle.classList.remove('active');
    chatSection.classList.remove('hidden');
    reliefSection.classList.add('hidden');
});

reliefToggle.addEventListener('click', () => {
    reliefToggle.classList.add('active');
    chatToggle.classList.remove('active');
    reliefSection.classList.remove('hidden');
    chatSection.classList.add('hidden');
});

// --- Chat Logic (Integrated with FastAPI) ---
async function sendMessage() {
    const text = messageInput.value.trim();
    if (!text) return;

    // 1. Append User Message to UI
    appendMessage('user', text);
    messageInput.value = '';

    try {
        // 2. Call FastAPI Backend
        const response = await fetch(BACKEND_URL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: text })
        });

        const data = await response.json();
        
        // 3. Append Bot Response to UI
        appendMessage('bot', data.response);
    } catch (error) {
        console.error("Error connecting to backend:", error);
        appendMessage('bot', "I'm having trouble connecting to my brain right now. Please try again later.");
    }
}

function appendMessage(role, content) {
    const msgDiv = document.createElement('div');
    msgDiv.className = `message ${role}`;
    
    let innerHTML = `<div class="message-content">${content}</div>`;
    
    if (role === 'bot') {
        innerHTML += `
            <div class="read-aloud">
                <span>🔊</span><span>Read Aloud</span>
            </div>`;
    }
    
    msgDiv.innerHTML = innerHTML;
    chatMessages.appendChild(msgDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;

    // Attach speech listener if it's a bot message
    if (role === 'bot') {
        const btn = msgDiv.querySelector('.read-aloud');
        btn.addEventListener('click', () => startSpeech(content));
    }
}

sendBtn.addEventListener('click', sendMessage);
messageInput.addEventListener('keypress', (e) => { if (e.key === 'Enter') sendMessage(); });

// --- Speech & Exercise Logic ---
function startSpeech(text) {
    if ('speechSynthesis' in window) {
        speechSynthesis.cancel(); // Stop current speech
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.rate = 0.9;
        speechSynthesis.speak(utterance);
        
        // Show modal while speaking
        voiceModal.classList.add('active');
        document.getElementById('voiceSubtitle').textContent = text;
        utterance.onend = () => voiceModal.classList.remove('active');
    }
}

// Relief Card Clicks
document.querySelectorAll('.relief-card').forEach(card => {
    card.addEventListener('click', () => {
        const tech = card.getAttribute('data-technique');
        currentTechnique = tech;
        currentTechniqueFile = card.getAttribute('data-file');
        
        const explanation = breathingExplanations[tech] || `Let's begin the ${tech} exercise.`;
        startSpeech(explanation);
        
        document.getElementById('voiceTitle').textContent = card.querySelector('.card-title').textContent;
    });
});

// Start Exercise (opens the sub-html files)
startSession.addEventListener('click', () => {
    if (currentTechniqueFile) {
        window.open(currentTechniqueFile, '_blank');
        voiceModal.classList.remove('active');
        speechSynthesis.cancel();
    }
});

// End Session
document.getElementById('endSession').addEventListener('click', () => {
    voiceModal.classList.remove('active');
    speechSynthesis.cancel();
});
document.getElementById('closeVoice').addEventListener('click', () => voiceModal.classList.remove('active'));