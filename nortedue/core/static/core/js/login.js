document.addEventListener("DOMContentLoaded", function () {
    const loginForm = document.getElementById("loginForm");
    const btnSubmit = document.getElementById("btnSubmit");
    const togglePasswordBtn = document.getElementById("togglePassword");
    const passwordInput = document.getElementById("id_password");
    const usernameInput = document.getElementById("id_username");

    // Foco automático no primeiro campo (Usuário) ao carregar a página
    if (usernameInput) {
        usernameInput.focus();
    }

    // Alternar visibilidade da senha (Mostrar / Ocultar)
    if (togglePasswordBtn && passwordInput) {
        togglePasswordBtn.addEventListener("click", function () {
            const isPassword = passwordInput.getAttribute("type") === "password";
            passwordInput.setAttribute("type", isPassword ? "text" : "password");
            
            // Troca o ícone (SVG) de Olho Fechado / Aberto
            this.innerHTML = isPassword 
                ? `<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M2 12s3-7 10-7 10 7 10 7-3 7-10 7-10-7-10-7Z"/><circle cx="12" cy="12" r="3"/></svg>`
                : `<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9.88 9.88a3 3 0 1 0 4.24 4.24"/><path d="M10.73 5.08A10.43 10.43 0 0 1 12 5c7 0 10 7 10 7a13.16 13.16 0 0 1-1.67 2.68"/><path d="M6.61 6.61A13.52 13.52 0 0 0 2 12s3 7 10 7a9.74 9.74 0 0 0 5.39-1.61"/><line x1="2" x2="22" y1="2" y2="22"/></svg>`;
        });
    }

    // Feedback visual ao enviar o formulário
    if (loginForm && btnSubmit) {
        loginForm.addEventListener("submit", function () {
            btnSubmit.disabled = true;
            btnSubmit.innerText = "Entrando...";
        });
    }
});