// function checkAuth() {
//   const token = localStorage.getItem("token");

//   if (!token) {
//     window.location.href = "auth.html";
//   }
// }

function logout() {
  localStorage.removeItem("token");
  localStorage.removeItem("user");
  localStorage.removeItem("activeChatId");

  window.location.href = "auth.html";
}