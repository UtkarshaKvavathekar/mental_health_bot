// Backend configuration - UPDATE THIS TO MATCH YOUR BACKEND URL
const BACKEND_URL = "http://127.0.0.1:8000/ask";

// Breathing explanations
const breathingExplanations = {
    'boxbreathing': "Sit straight and relax your shoulders. We'll practice box breathing together - breathe in for 4, hold for 4, breathe out for 4, and hold for 4. Let's begin.",
    'breathing': "Find a comfortable position and close your eyes if you wish. We'll use the 4-7-8 technique - inhale for 4, hold for 7, exhale for 8. Ready? Let's start.",
    'anxietybreathing': "Take a moment to settle in. This anxiety release breathing will help calm your mind - inhale for 4, hold for 4, exhale slowly for 6, then hold for 2. Let's begin together.",
    'grounding': "Take a moment to settle in. This anxiety release grounding technique will help calm your mind"
};

// Techniques that open a new window
const breathingTechniques = ['boxbreathing', 'breathing', 'anxietybreathing', 'grounding'];

let currentTechnique = null;
let currentTechniqueFile = null;

// Toggle between Chat and Quick Relief
const chatToggle = document.getElementById('chatToggle');
const reliefToggle = document.getElementById('reliefToggle');
const chatSection = document.getElementById('chatSection');
const reliefSection = document.getElementById('reliefSection');

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

// Chat functionality with Backend Integration
const messageInput = document.getElementById('messageInput');
const sendBtn = document.getElementById('sendBtn');
const chatMessages = document.getElementById('chatMessages');

// Helper function to escape HTML and prevent XSS
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

async function sendMessage() {
    const message = messageInput.value.trim();
    if (!message) return;

    // Add user message to chat
    const userMsg = document.createElement('div');
    userMsg.className = 'message user';
    userMsg.innerHTML = `<div class="message-content">${escapeHtml(message)}</div>`;
    chatMessages.appendChild(userMsg);
    messageInput.value = '';
    chatMessages.scrollTop = chatMessages.scrollHeight;

    // Disable send button while processing
    sendBtn.disabled = true;

    // Add loading indicator
    const loadingMsg = document.createElement('div');
    loadingMsg.className = 'message bot';
    loadingMsg.id = 'loading-message';
    loadingMsg.innerHTML = `
        <div>
            <div class="message-content loading">Thinking...</div>
        </div>
    `;
    chatMessages.appendChild(loadingMsg);
    chatMessages.scrollTop = chatMessages.scrollHeight;

    try {
        // Send message to backend
        const response = await fetch(BACKEND_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message: message })
        });

        // Remove loading indicator
        const loadingElement = document.getElementById('loading-message');
        if (loadingElement) {
            loadingElement.remove();
        }

        if (!response.ok) {
            throw new Error(`Server error: ${response.status}`);
        }

        const data = await response.json();

        // Add bot response
        const botMsg = document.createElement('div');
        botMsg.className = 'message bot';
        botMsg.innerHTML = `
            <div>
                <div class="message-content">${escapeHtml(data.response)}</div>
                <div class="read-aloud">
                    <span>🔊</span>
                    <span>Read Aloud</span>
                </div>
            </div>
        `;
        chatMessages.appendChild(botMsg);
        chatMessages.scrollTop = chatMessages.scrollHeight;

        // Add read aloud functionality to new message
        const readAloudBtn = botMsg.querySelector('.read-aloud');
        readAloudBtn.addEventListener('click', () => startReadAloud(readAloudBtn));

    } catch (error) {
        console.error('Error:', error);

        // Remove loading indicator if present
        const loadingElement = document.getElementById('loading-message');
        if (loadingElement) {
            loadingElement.remove();
        }

        // Show error message
        const errorMsg = document.createElement('div');
        errorMsg.className = 'message bot';
        errorMsg.innerHTML = `
            <div>
                <div class="message-content">
                    I apologize, but I'm having trouble connecting right now. Please make sure your backend is running at ${BACKEND_URL}
                    <div class="error">Error: ${error.message}</div>
                </div>
            </div>
        `;
        chatMessages.appendChild(errorMsg);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    } finally {
        // Re-enable send button
        sendBtn.disabled = false;
    }
}

// Event listeners for sending messages
sendBtn.addEventListener('click', sendMessage);
messageInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') sendMessage();
});

// Voice mode
const voiceBtn = document.getElementById('voiceBtn');
const voiceBtnText = document.getElementById('voiceBtnText');
const voiceModal = document.getElementById('voiceModal');
const closeVoice = document.getElementById('closeVoice');
const startSession = document.getElementById('startSession');
const endSession = document.getElementById('endSession');
const voiceTitle = document.getElementById('voiceTitle');
const voiceSubtitle = document.getElementById('voiceSubtitle');

let isListening = false;
let silenceTimer = null;

// Speak button - single click to start, auto-stop after 4 seconds of silence
voiceBtn.addEventListener('click', (e) => {
    e.preventDefault();

    if (!isListening) {
        isListening = true;
        voiceBtn.classList.add('speaking');
        voiceBtnText.textContent = 'Listening...';

        silenceTimer = setTimeout(() => {
            if (isListening) {
                isListening = false;
                voiceBtn.classList.remove('speaking');
                voiceBtnText.textContent = 'Speak';
            }
        }, 4000);
    } else {
        isListening = false;
        clearTimeout(silenceTimer);
        voiceBtn.classList.remove('speaking');
        voiceBtnText.textContent = 'Speak';
    }
});

// Start Exercise button handler
startSession.addEventListener('click', () => {
    if (currentTechnique && breathingTechniques.includes(currentTechnique) && currentTechniqueFile) {
        // Open the breathing exercise in a new window
        window.open(currentTechniqueFile, '_blank');
        // Close the modal
        voiceModal.classList.remove('active');
        if ('speechSynthesis' in window) {
            speechSynthesis.cancel();
        }
    }
    // For non-breathing techniques, do nothing (as requested)
});

// End Session button handler
endSession.addEventListener('click', () => {
    voiceModal.classList.remove('active');
    if ('speechSynthesis' in window) {
        speechSynthesis.cancel();
    }
    currentTechnique = null;
    currentTechniqueFile = null;
});

// Read aloud functionality
function startReadAloud(readAloudElement) {
    const messageContent = readAloudElement.previousElementSibling.textContent;
    voiceModal.classList.add('active');
    voiceTitle.textContent = 'Serene Live';
    voiceSubtitle.textContent = messageContent;

    if ('speechSynthesis' in window) {
        const utterance = new SpeechSynthesisUtterance(messageContent);
        utterance.rate = 0.9;
        utterance.pitch = 1;
        utterance.onend = () => {
            setTimeout(() => {
                voiceModal.classList.remove('active');
            }, 500);
        };
        speechSynthesis.speak(utterance);
    } else {
        setTimeout(() => {
            voiceModal.classList.remove('active');
        }, 5000);
    }
}

document.querySelectorAll('.read-aloud').forEach(btn => {
    btn.addEventListener('click', () => startReadAloud(btn));
});

closeVoice.addEventListener('click', () => {
    voiceModal.classList.remove('active');
    if ('speechSynthesis' in window) {
        speechSynthesis.cancel();
    }
    currentTechnique = null;
    currentTechniqueFile = null;
});

// Quick Relief cards
const reliefCards = document.querySelectorAll('.relief-card');

reliefCards.forEach(card => {
    card.addEventListener('click', () => {
        const technique = card.getAttribute('data-technique');
        const techniqueFile = card.getAttribute('data-file');
        const techniqueName = card.querySelector('.card-title').textContent;

        currentTechnique = technique;
        currentTechniqueFile = techniqueFile;

        // Show voice modal with explanation
        voiceModal.classList.add('active');
        voiceTitle.textContent = techniqueName;

        // Remove glow class first
        if (startSession.classList) {
            startSession.classList.remove('glow');
        }

        if (breathingExplanations[technique]) {
            // Breathing techniques: show explanation and enable "Start Exercise"
            voiceSubtitle.textContent = breathingExplanations[technique];

            // Add glow effect to start button
            if (startSession.classList) {
                startSession.classList.add('glow');
            }

            if ('speechSynthesis' in window) {
                const utterance = new SpeechSynthesisUtterance(breathingExplanations[technique]);
                utterance.rate = 0.9;
                utterance.pitch = 1;
                speechSynthesis.speak(utterance);
            }
        } else {
            // Other techniques: show generic message
            voiceSubtitle.textContent = `Let's begin the ${techniqueName} exercise together. Find a comfortable position and let me guide you through this.`;

            if ('speechSynthesis' in window) {
                const utterance = new SpeechSynthesisUtterance(voiceSubtitle.textContent);
                utterance.rate = 0.9;
                utterance.pitch = 1;
                speechSynthesis.speak(utterance);
            }
        }
    });
});