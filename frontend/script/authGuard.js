function checkAuth() {
  const token = localStorage.getItem("token");
  const user = JSON.parse(localStorage.getItem("user"));

  if (!token || !user) {
    window.location.href = "auth.html";
    return null;
  }

  return {
    token,
    user,
    userId: user.id
  };
}