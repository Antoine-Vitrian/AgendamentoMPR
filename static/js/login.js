document.addEventListener("DOMContentLoaded", () => {
    const loginBtn = document.getElementById("loginBtn");
    const username = document.getElementById("username");
    const password = document.getElementById("password");

    // Validação simples
    loginBtn.addEventListener("click", () => {
        const userVal = username.value.trim();
        const passVal = password.value.trim();

        // Exemplo de credenciais fixas (substitua por lógica real)
        if (userVal === "UsuarioMpr123" && passVal === "mprAdmin123") {
        // Redireciona para rota Flask
        window.location.href = "/formulario"; 
        // "/dashboard" deve ser uma rota configurada no Flask
        } else {
        alert("Usuário ou senha incorretos!");
        }
    });
    });