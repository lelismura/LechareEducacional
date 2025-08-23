// Seleciona o logo e o overlay
const logo = document.getElementById('app-logo');
const overlay = document.getElementById('overlay');

// Ao clicar no logo, abre o cartão
if (logo) {
  logo.addEventListener('click', () => {
    overlay.style.display = 'flex';
    setTimeout(() => overlay.classList.add('show'), 10);
  });
}

// Fecha o cartão
function fecharCard() {
  overlay.classList.remove('show');
  setTimeout(() => overlay.style.display = 'none', 300);
}

// Copiar para área de transferência
function copyToClipboard(text) {
  navigator.clipboard.writeText(text).then(() => {
    alert("Copiado: " + text);
  });
}
