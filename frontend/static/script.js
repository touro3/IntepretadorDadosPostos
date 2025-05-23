document.addEventListener("DOMContentLoaded", function () {
  document.getElementById('sendButton').addEventListener('click', async () => {
    const input = document.getElementById('userInput');
    const message = input.value.trim();

    if (message !== '') {
      const messagesContainer = document.getElementById('chatMessages');

      // Exibe mensagem do usuário
      const userMessage = document.createElement('div');
      userMessage.className = 'message user-message';
      userMessage.textContent = message;
      messagesContainer.appendChild(userMessage);

      input.value = '';
      input.focus();
      messagesContainer.scrollTop = messagesContainer.scrollHeight;

      try {
        const response = await fetch('/chat', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ message })
        });

        const data = await response.json();

        // Exibe resposta do bot
        const botMessage = document.createElement('div');
        botMessage.className = 'message bot-message';
        botMessage.textContent = data.reply;
        messagesContainer.appendChild(botMessage);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;

      } catch (error) {
        const errorMsg = document.createElement('div');
        errorMsg.className = 'message bot-message';
        errorMsg.textContent = 'Erro ao conectar com o servidor.';
        messagesContainer.appendChild(errorMsg);
      }
    }
  });
});
