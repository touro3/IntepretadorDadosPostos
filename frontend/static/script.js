document.addEventListener("DOMContentLoaded", function () {
  const sendButton = document.getElementById('sendButton');
  const input = document.getElementById('userInput');
  const messagesContainer = document.getElementById('chatMessages');

  async function sendMessage() {
    const message = input.value.trim();
    if (!message) return;

    // Adiciona mensagem do usuário (sem avatar)
    addMessage(message, 'user-message', false);
    input.value = '';
    
    try {
      // Mostra mensagem de "Digitando..." com avatar do robô
      const typingMsg = addMessage(
        '<div class="typing-indicator"><span></span><span></span><span></span></div>', 
        'bot-message', 
        true
      );
      
      // Simula delay de resposta
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Remove o "Digitando..." antes de mostrar a resposta real
      messagesContainer.removeChild(typingMsg);

      // Envia para o servidor
      const response = await fetch('/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message })
      });

      const data = await response.json();
      
      // Adiciona resposta do bot COM avatar animado
      addMessage(
        `<img src="/static/robo_animado.gif" class="bot-avatar">
         <div class="bot-text">${data.reply}</div>`, 
        'bot-message', 
        true
      );
      
    } catch (error) {
      addMessage(
        `<img src="/static/robo_animado.gif" class="bot-avatar">
         <div class="bot-text">Erro ao conectar com o servidor</div>`, 
        'bot-message', 
        true
      );
      console.error('Erro no chat:', error);
    }
  }

  function addMessage(content, className, isHTML = false) {
    const message = document.createElement("div");
    message.className = `message ${className}`;
    
    if (isHTML) {
      message.innerHTML = content;
    } else {
      message.textContent = content;
    }
    
    messagesContainer.appendChild(message);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
    return message;
  }

  // Event listeners
  sendButton.addEventListener('click', sendMessage);
  
  input.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
      sendMessage();
    }
  });
});