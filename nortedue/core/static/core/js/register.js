document.addEventListener("DOMContentLoaded", function () {
    const registerForm = document.getElementById("registerForm");
    const btnSubmit = document.getElementById("btnSubmit");
    const usernameInput = document.getElementById("id_username");

    // Foco automático no primeiro campo ao carregar
    if (usernameInput) {
        usernameInput.focus();
    }

    // Função utilitária para alternar visibilidade de qualquer campo de senha
    function setupPasswordToggle(buttonId, inputId) {
        const toggleBtn = document.getElementById(buttonId);
        const passwordInput = document.getElementById(inputId);

        if (toggleBtn && passwordInput) {
            toggleBtn.addEventListener("click", function () {
                const isPassword = passwordInput.getAttribute("type") === "password";
                passwordInput.setAttribute("type", isPassword ? "text" : "password");
                
                // Alterna o ícone SVG de olho
                this.innerHTML = isPassword 
                    ? `<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M2 12s3-7 10-7 10 7 10 7-3 7-10 7-10-7-10-7Z"/><circle cx="12" cy="12" r="3"/></svg>`
                    : `<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9.88 9.88a3 3 0 1 0 4.24 4.24"/><path d="M10.73 5.08A10.43 10.43 0 0 1 12 5c7 0 10 7 10 7a13.16 13.16 0 0 1-1.67 2.68"/><path d="M6.61 6.61A13.52 13.52 0 0 0 2 12s3 7 10 7a9.74 9.74 0 0 0 5.39-1.61"/><line x1="2" x2="22" y1="2" y2="22"/></svg>`;
            });
        }
    }

    // Configura o olho para o campo de Senha e Confirmação de Senha
    setupPasswordToggle("togglePassword1", "id_password1");
    setupPasswordToggle("togglePassword2", "id_password2");

    // Feedback visual ao enviar o formulário
    if (registerForm && btnSubmit) {
        registerForm.addEventListener("submit", function () {
            btnSubmit.disabled = true;
            btnSubmit.innerText = "Criando conta...";
        });
    }
});