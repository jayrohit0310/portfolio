// Chatbot Widget Interactivity

document.addEventListener('DOMContentLoaded', () => {
    const chatToggle = document.getElementById('chat-toggle');
    const chatContainer = document.getElementById('chat-container');
    const chatClose = document.getElementById('chat-close');
    const chatInput = document.getElementById('chat-input');
    const chatSend = document.getElementById('chat-send');
    const chatMessages = document.getElementById('chat-messages');
    const suggestionChips = document.querySelectorAll('.suggestion-chip');

    // 1. Toggle Chat Widget
    if (chatToggle && chatContainer) {
        chatToggle.addEventListener('click', () => {
            chatContainer.classList.toggle('hidden');
            chatContainer.classList.toggle('scale-95');
            chatContainer.classList.toggle('opacity-0');
            
            // Scroll to bottom on open
            scrollToBottom();
            
            // Focus on input
            if (!chatContainer.classList.contains('hidden')) {
                chatInput.focus();
            }
        });
    }

    if (chatClose && chatContainer) {
        chatClose.addEventListener('click', () => {
            chatContainer.classList.add('hidden', 'scale-95', 'opacity-0');
        });
    }

    // 2. Format Response Text (Simple Markdown Parser)
    function formatMessageText(text) {
        let formatted = text;
        // Bold tags **text**
        formatted = formatted.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        // Bullets • item
        formatted = formatted.replace(/•\s?(.*?)(?=\n|$)/g, '<li>$1</li>');
        // If there are list items, wrap them in a list tag
        if (formatted.includes('<li>')) {
            // Very simple list tag wrapping (wrap successive list items if they are adjacent)
            // Just replacing list elements is fine for custom display
        }
        // Linebreaks
        formatted = formatted.replace(/\n/g, '<br>');
        return formatted;
    }

    // 3. Append Message to UI
    function appendMessage(sender, text, isNew = true) {
        const msgDiv = document.createElement('div');
        msgDiv.className = `flex ${sender === 'user' ? 'justify-end' : 'justify-start'} mb-3`;

        const innerDiv = document.createElement('div');
        innerDiv.className = `max-w-[85%] px-4 py-2.5 rounded-2xl text-sm ${
            sender === 'user' 
                ? 'bg-indigo-600 text-white rounded-tr-none' 
                : 'bg-slate-100 dark:bg-slate-800 text-slate-800 dark:text-slate-200 rounded-tl-none border border-slate-200/50 dark:border-slate-700/50'
        }`;

        msgDiv.appendChild(innerDiv);
        chatMessages.appendChild(msgDiv);
        scrollToBottom();

        if (sender === 'bot' && isNew) {
            // Typing effect for bot message
            innerDiv.innerHTML = '';
            const formattedHTML = formatMessageText(text);
            
            // Render HTML incrementally by tokens or simple speed up
            let currentHTML = '';
            let i = 0;
            // Temporary container to parse HTML nodes
            const tempDiv = document.createElement('div');
            tempDiv.innerHTML = formattedHTML;
            
            // Simple text typewriter, if it contains tags we render directly or type quickly
            if (formattedHTML.includes('<')) {
                // If contains HTML, render immediately to avoid breaking elements
                innerDiv.innerHTML = formattedHTML;
                scrollToBottom();
            } else {
                // Typewriter effect
                const interval = setInterval(() => {
                    if (i < text.length) {
                        innerDiv.textContent += text.charAt(i);
                        i++;
                        scrollToBottom();
                    } else {
                        clearInterval(interval);
                        // Final format check to replace any special characters
                        innerDiv.innerHTML = formatMessageText(text);
                        scrollToBottom();
                    }
                }, 15);
            }
        } else {
            innerDiv.innerHTML = formatMessageText(text);
        }
    }

    // 4. Show/Hide Typing Indicator
    let typingIndicator = null;
    function showTypingIndicator() {
        if (typingIndicator) return;
        
        typingIndicator = document.createElement('div');
        typingIndicator.className = 'flex justify-start mb-3 id-typing-indicator';
        typingIndicator.innerHTML = `
            <div class="bg-slate-100 dark:bg-slate-800 text-slate-500 px-4 py-2.5 rounded-2xl rounded-tl-none border border-slate-200/50 dark:border-slate-700/50 text-xs flex items-center space-x-1">
                <span class="w-1.5 h-1.5 bg-slate-400 dark:bg-slate-500 rounded-full animate-bounce" style="animation-delay: 0.1s"></span>
                <span class="w-1.5 h-1.5 bg-slate-400 dark:bg-slate-500 rounded-full animate-bounce" style="animation-delay: 0.2s"></span>
                <span class="w-1.5 h-1.5 bg-slate-400 dark:bg-slate-500 rounded-full animate-bounce" style="animation-delay: 0.3s"></span>
            </div>
        `;
        chatMessages.appendChild(typingIndicator);
        scrollToBottom();
    }

    function removeTypingIndicator() {
        if (typingIndicator) {
            typingIndicator.remove();
            typingIndicator = null;
        }
    }

    function scrollToBottom() {
        if (chatMessages) {
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }
    }

    // 5. Send Message Handler
    function handleSendMessage(messageText) {
        if (!messageText || messageText.trim() === '') return;
        
        // Append user message
        appendMessage('user', messageText);
        chatInput.value = '';

        // Show thinking status
        showTypingIndicator();

        // AJAX to Flask API
        fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ message: messageText })
        })
        .then(response => response.json())
        .then(data => {
            removeTypingIndicator();
            if (data.success) {
                appendMessage('bot', data.reply);
            } else {
                appendMessage('bot', "Oops! I encountered an error while processing your request. Please try again.");
            }
        })
        .catch(err => {
            removeTypingIndicator();
            appendMessage('bot', "Connection error. Make sure the server is running.");
            console.error(err);
        });
    }

    // Trigger on Send Click
    if (chatSend) {
        chatSend.addEventListener('click', () => {
            handleSendMessage(chatInput.value);
        });
    }

    // Trigger on Enter Key
    if (chatInput) {
        chatInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                handleSendMessage(chatInput.value);
            }
        });
    }

    // 6. Handle Click on Recommendation Chips
    suggestionChips.forEach(chip => {
        chip.addEventListener('click', () => {
            const question = chip.getAttribute('data-question');
            handleSendMessage(question);
        });
    });
});
