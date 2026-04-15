let isLogin = true;

// ===============================
// SWITCH FORM
// ===============================
function switchForm() {
  const title = document.getElementById("formTitle");
  const btn = document.querySelector(".auth-btn");
  const switchText = document.querySelector(".switch");

  const fields = [
    "nameField",
    "phoneField",
    "ageField",
    "genderField",
    "confirmField",
  ];

  isLogin = !isLogin;

  title.innerText = isLogin ? "Login" : "Sign Up";
  btn.innerText = isLogin ? "Login" : "Create Account";

  fields.forEach((id) => {
    document.getElementById(id).style.display = isLogin ? "none" : "block";
  });

  switchText.innerHTML = isLogin
    ? 'Don’t have account? <span onclick="switchForm()">Sign Up</span>'
    : 'Already have account? <span onclick="switchForm()">Login</span>';
}

// ===============================
// MAIN AUTH FUNCTION
// ===============================
async function handleAuth() {
  const email = document.getElementById("email").value.trim();
  const password = document.getElementById("password").value.trim();
  const btn = document.querySelector(".auth-btn");

  try {
    btn.disabled = true;
    btn.innerText = "Loading...";

    // ---------------- LOGIN ----------------
    if (isLogin) {
      if (!email || !password) {
        alert("Please enter email and password");
        return;
      }

      const data = await loginUser({ email, password });

      console.log("Login response:", data);

      localStorage.setItem("token", data.access_token);
      localStorage.setItem(
        "user",
        JSON.stringify({
          id: data.user_id,
          email: data.email,
        })
      );

      window.location.href = "dashboard.html";
    }

    // ---------------- SIGNUP ----------------
    else {
      const newUser = {
        name: document.getElementById("name").value.trim(),
        email,
        phone: document.getElementById("phone").value.trim(),
        age: document.getElementById("age").value,
        gender: document.getElementById("gender").value,
        password,
      };

      if (!newUser.name || !newUser.email || !newUser.password) {
        alert("Please fill required fields");
        return;
      }

      const data = await signupUser(newUser);

      console.log("Signup response:", data);

      alert("Account created successfully! Please login now.");

      switchForm();
    }
  } catch (err) {
    console.error(err);
    alert(err.message || "Something went wrong");
  } finally {
    btn.disabled = false;
    btn.innerText = isLogin ? "Login" : "Create Account";
  }
}

// ===============================
// EVENT LISTENER
// ===============================
document.getElementById("authForm").addEventListener("submit", function (e) {
  e.preventDefault();
  handleAuth();
});