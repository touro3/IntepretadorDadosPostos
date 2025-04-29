document.getElementById('sendButton').addEventListener('click', () => {
    const input = document.getElementById('userInput');
    if (input.value.trim() !== '') {
      alert('Você digitou: ' + input.value);
      input.value = '';
    }
  });
  