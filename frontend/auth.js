// auth.js
const API_BASE = "http://127.0.0.1:5000";

function signup() {
  const username = document.getElementById("signup-username").value;
  const password = document.getElementById("signup-password").value;

  fetch(`${API_BASE}/signup`, {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({username, password})
  })
    .then(res => res.json())
    .then(data => {
      if (data.message) {
        document.getElementById("signup-message").innerText = "✅ Registered! Redirecting to login...";
        setTimeout(() => {
          window.location.href = "login.html";
        }, 1500);
      } else {
        document.getElementById("signup-message").innerText = data.error || "Error occurred.";
      }
    });
}

function login() {
  const username = document.getElementById("login-username").value;
  const password = document.getElementById("login-password").value;

  fetch(`${API_BASE}/login`, {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({username, password})
  })
    .then(res => res.json())
    .then(data => {
      if (data.user_id) {
        localStorage.setItem("user_id", data.user_id);
        document.getElementById("login-message").innerText = "✅ Logged in! Redirecting...";
        setTimeout(() => {
          window.location.href = "index.html"; // back to your main UI
        }, 1500);
      } else {
        document.getElementById("login-message").innerText = data.error || "Login failed.";
      }
    });
}
