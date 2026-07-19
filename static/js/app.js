document.addEventListener('DOMContentLoaded', () => {
    const chatForm = document.getElementById('chat-form');
    const userInput = document.getElementById('user-input');
    const chatHistory = document.getElementById('chat-history');
    const themeToggle = document.getElementById('theme-toggle');
    const newChatBtn = document.getElementById('new-chat-btn');

    // Configure marked to sanitize HTML
    // We are using marked.js included in the HTML to parse AI's markdown
    marked.setOptions({
        breaks: true,
        gfm: true
    });

    // State
    let messages = [];

    // Load initial messages from local storage or set default
    const loadMessages = () => {
        const stored = localStorage.getItem('chatHistory');
        if (stored) {
            try {
                messages = JSON.parse(stored);
                // Clear default welcome message
                chatHistory.innerHTML = '';
                // Render all messages
                // First filter out system message if present
                const displayMessages = messages.filter(m => m.role !== 'system');
                if (displayMessages.length === 0) {
                    showWelcomeMessage();
                } else {
                    displayMessages.forEach(msg => {
                        addMessageToUI(msg.role === 'user' ? 'user' : 'bot', msg.content, false);
                    });
                }
            } catch (e) {
                initDefaultChat();
            }
        } else {
            initDefaultChat();
        }
        
        // Ensure system prompt is always present in state
        if (!messages.find(m => m.role === 'system')) {
            messages.unshift({ role: 'system', content: 'You are a helpful, smart, and concise AI assistant.' });
        }
    };

    const initDefaultChat = () => {
        messages = [{ role: 'system', content: 'You are a helpful, smart, and concise AI assistant.' }];
        chatHistory.innerHTML = '';
        showWelcomeMessage();
    };

    const showWelcomeMessage = () => {
        chatHistory.innerHTML = `
            <div class="message bot-message slide-in">
                <div class="avatar"><i class="fa-solid fa-robot"></i></div>
                <div class="message-content">
                    <p>Hello! I am Nova, your advanced AI assistant. How can I help you today?</p>
                </div>
            </div>
        `;
    };

    const saveMessages = () => {
        localStorage.setItem('chatHistory', JSON.stringify(messages));
    };

    // Initialize
    loadMessages();

    // Theme logic
    const applyTheme = (isLight) => {
        const darkIcon = document.querySelector('.dark-icon');
        const lightIcon = document.querySelector('.light-icon');
        if (isLight) {
            document.body.classList.add('light-mode');
            darkIcon.style.display = 'none';
            lightIcon.style.display = 'inline-block';
        } else {
            document.body.classList.remove('light-mode');
            darkIcon.style.display = 'inline-block';
            lightIcon.style.display = 'none';
        }
    };

    const storedTheme = localStorage.getItem('theme');
    if (storedTheme === 'light') {
        applyTheme(true);
    }

    themeToggle.addEventListener('click', () => {
        const isLightMode = !document.body.classList.contains('light-mode');
        applyTheme(isLightMode);
        localStorage.setItem('theme', isLightMode ? 'light' : 'dark');
    });

    // New Chat
    newChatBtn.addEventListener('click', () => {
        initDefaultChat();
        saveMessages();
    });

    // Form submission
    chatForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const text = userInput.value.trim();
        if (!text) return;

        // Clear input
        userInput.value = '';

        // Add user message to UI and state
        addMessageToUI('user', text, true);
        messages.push({ role: 'user', content: text });
        saveMessages();

        // Add typing indicator
        const typingId = addTypingIndicator();

        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ messages })
            });

            const data = await response.json();
            
            // Remove typing indicator
            removeTypingIndicator(typingId);

            if (response.ok) {
                let langNote = "";
                if (data.lang && data.lang !== 'en') {
                    langNote = `\n\n<div style="font-size: 0.7em; opacity: 0.7; margin-top: 5px; font-style: italic;">Translated from ${data.lang} via LibreTranslate</div>`;
                }
                addMessageToUI('bot', data.message + langNote, true);
                messages.push({ role: 'assistant', content: data.message });
                saveMessages();
            } else {
                addMessageToUI('bot', 'Sorry, I encountered an error: ' + (data.error || 'Unknown error'), true);
            }
        } catch (error) {
            removeTypingIndicator(typingId);
            addMessageToUI('bot', 'Network error. Please try again.', true);
        }
    });

    function addMessageToUI(role, text, animate = true) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${role}-message ${animate ? 'slide-in' : ''}`;
        
        const avatarHTML = role === 'user' 
            ? '<i class="fa-solid fa-user"></i>' 
            : '<i class="fa-solid fa-robot"></i>';

        // Parse markdown if bot, else escape HTML for user
        let formattedText = '';
        if (role === 'bot') {
            formattedText = marked.parse(text);
        } else {
            // Simple escape for user input
            formattedText = '<p>' + text.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;").replace(/'/g, "&#039;") + '</p>';
        }

        messageDiv.innerHTML = `
            <div class="avatar">${avatarHTML}</div>
            <div class="message-content">
                ${formattedText}
            </div>
        `;
        
        chatHistory.appendChild(messageDiv);
        scrollToBottom();
    }

    function addTypingIndicator() {
        const id = 'typing-' + Date.now();
        const messageDiv = document.createElement('div');
        messageDiv.className = `message bot-message slide-in`;
        messageDiv.id = id;
        
        messageDiv.innerHTML = `
            <div class="avatar"><i class="fa-solid fa-robot"></i></div>
            <div class="message-content" style="padding: 10px 15px;">
                <div class="typing-indicator">
                    <div class="dot"></div>
                    <div class="dot"></div>
                    <div class="dot"></div>
                </div>
            </div>
        `;
        
        chatHistory.appendChild(messageDiv);
        scrollToBottom();
        return id;
    }

    function removeTypingIndicator(id) {
        const el = document.getElementById(id);
        if (el) {
            el.remove();
        }
    }

    function scrollToBottom() {
        chatHistory.scrollTop = chatHistory.scrollHeight;
    }
});
