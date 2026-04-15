const BASE_URL = "http://127.0.0.1:8000";

async function apiRequest(endpoint, method = "GET", body = null) {
  const token = localStorage.getItem("token");

  const options = {
    method,
    headers: {
      "Content-Type": "application/json",
    },
  };

  if (token) {
    options.headers.Authorization = `Bearer ${token}`;
  }

  if (body) {
    options.body = JSON.stringify(body);
  }

  const res = await fetch(`${BASE_URL}${endpoint}`, options);

  let data;
  try {
    data = await res.json();
  } catch {
    data = null;
  }

  if (!res.ok) {
    console.error("API Error:", data);
    throw new Error(data?.detail || "Request failed");
  }

  return data;
}

// AUTH
async function loginUser(data) {
  return apiRequest("/auth/login", "POST", data);
}

async function signupUser(data) {
  return apiRequest("/auth/signup", "POST", data);
}