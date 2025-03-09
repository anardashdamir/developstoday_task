// DOM elements
const chatMessages = document.getElementById('chat-messages');
const userInput = document.getElementById('user-input');
const sendButton = document.getElementById('send-button');

// Chat state
const chatState = {
    messages: [],
    userId: `user_${Date.now()}`, // Generate a simple user ID
    isWaitingForResponse: false
};

// Event listeners
sendButton.addEventListener('click', sendMessage);
userInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});

// Initialize the chat with a welcome message
window.addEventListener('DOMContentLoaded', () => {
    addAssistantMessage("Hello! I'm your Cocktail Advisor. You can ask me about cocktails, their ingredients, or get recommendations. What would you like to know today?");
});

async function sendMessage() {
    const message = userInput.value.trim();
    if (!message || chatState.isWaitingForResponse) return;
    
    // Add user message to the UI
    addUserMessage(message);
    
    // Clear input
    userInput.value = '';
    
    // Show typing indicator
    showTypingIndicator();
    
    // Set waiting state
    chatState.isWaitingForResponse = true;
    
    try {
        // Send the message to the backend
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                messages: [
                    { role: 'system', content: 'You are a Cocktail Advisor, an expert in cocktails and mixed drinks.' },
                    ...chatState.messages,
                    { role: 'user', content: message }
                ],
                user_id: chatState.userId
            })
        });
        
        // Hide typing indicator
        hideTypingIndicator();
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        // Add assistant message to the UI
        addAssistantMessage(data.message.content);
        
    } catch (error) {
        console.error('Error sending message:', error);
        addAssistantMessage("Sorry, I encountered an error processing your request. Please try again.");
        hideTypingIndicator();
    } finally {
        // Reset waiting state
        chatState.isWaitingForResponse = false;
    }
}

function addUserMessage(content) {
    const message = { role: 'user', content };
    chatState.messages.push(message);
    
    const messageElement = document.createElement('div');
    messageElement.className = 'message user';
    messageElement.textContent = content;
    
    const timestamp = document.createElement('div');
    timestamp.className = 'timestamp';
    timestamp.textContent = getFormattedTime();
    messageElement.appendChild(timestamp);
    
    chatMessages.appendChild(messageElement);
    
    // Scroll to the bottom
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function addAssistantMessage(content) {
    const message = { role: 'assistant', content };
    chatState.messages.push(message);
    
    const messageElement = document.createElement('div');
    messageElement.className = 'message assistant';
    
    // Process markdown-like formatting
    let formattedContent = content
        // Bold text
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        // Italic text
        .replace(/\*(.*?)\*/g, '<em>$1</em>')
        // Preserve line breaks
        .replace(/\n/g, '<br>');
    
    // Set innerHTML instead of textContent to preserve formatting
    messageElement.innerHTML = formattedContent;
    
    const timestamp = document.createElement('div');
    timestamp.className = 'timestamp';
    timestamp.textContent = getFormattedTime();
    messageElement.appendChild(timestamp);
    
    chatMessages.appendChild(messageElement);
    
    // Scroll to the bottom
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function showTypingIndicator() {
    const typingElement = document.createElement('div');
    typingElement.className = 'message assistant typing-indicator-container';
    typingElement.id = 'typing-indicator';
    
    const typingIndicator = document.createElement('div');
    typingIndicator.className = 'typing-indicator';
    typingIndicator.innerHTML = '<span></span><span></span><span></span>';
    
    typingElement.appendChild(typingIndicator);
    chatMessages.appendChild(typingElement);
    
    // Scroll to the bottom
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function hideTypingIndicator() {
    const typingElement = document.getElementById('typing-indicator');
    if (typingElement) {
        typingElement.remove();
    }
}

function getFormattedTime() {
    const now = new Date();
    return now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}