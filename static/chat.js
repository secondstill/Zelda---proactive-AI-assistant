// Gemini-style chat rendering
const chatMessages = document.getElementById('chat-messages');
function appendMessage(sender, text) {
    const msgDiv = document.createElement('div');
    msgDiv.className = 'chat-msg' + (sender === 'You' ? ' user' : '');
    const avatar = document.createElement('div');
    avatar.className = 'chat-avatar';
    avatar.textContent = sender === 'You' ? '🧑' : '🧚';
    const bubble = document.createElement('div');
    bubble.className = 'chat-bubble';
    // Zelda's answers: split into paragraphs if sender is Zelda
    if (sender !== 'You') {
        const paras = text.split(/\n\n|\r\n\r\n|\r\r/);
        paras.forEach(p => {
            const para = document.createElement('p');
            para.style.margin = '0 0 0.7em 0';
            para.textContent = p.trim();
            bubble.appendChild(para);
        });
    } else {
        bubble.textContent = text;
    }
    msgDiv.appendChild(avatar);
    msgDiv.appendChild(bubble);
    chatMessages.appendChild(msgDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}
window.appendMessage = appendMessage;

const chatForm = document.getElementById('chat-form');
const chatInput = document.getElementById('chat-input');
if (chatForm && chatInput && chatMessages) {
    chatForm.addEventListener('submit', function(e) {
        e.preventDefault();
        const msg = chatInput.value.trim();
        if (!msg) return;
        appendMessage('You', msg);
        chatInput.value = '';
        fetch('/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: msg })
        })
        .then(res => res.json())
        .then(data => appendMessage('Zelda', data.reply))
        .catch(() => appendMessage('Zelda', 'Sorry, something went wrong.'));
    });
}
