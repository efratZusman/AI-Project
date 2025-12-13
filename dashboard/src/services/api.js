// src/services/api.js

const BASE_URL = "http://127.0.0.1:8000";

async function handleResponse(response) {
  if (!response.ok) {
    let message = `HTTP ${response.status}`;
    try {
      const data = await response.json();
      if (data && data.detail) {
        message = data.detail;
      }
    } catch (_) {}
    throw new Error(message);
  }
  return response.json();
}

export async function analyzeEmail({ subject, body }) {
  const res = await fetch(`${BASE_URL}/analyze_email`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ subject, body }),
  });
  return handleResponse(res);
}

export async function getHistory() {
  const res = await fetch(`${BASE_URL}/history`);
  return handleResponse(res);
}

export async function getEmailById(id) {
  const res = await fetch(`${BASE_URL}/email/${id}`);
  return handleResponse(res);
}

export async function deleteEmail(id) {
  const res = await fetch(`${BASE_URL}/email/${id}`, {
    method: "DELETE",
  });
  return handleResponse(res);
}

export async function searchEmails({ q, category, priority }) {
  const params = new URLSearchParams();

  if (q && q.trim()) params.append("q", q.trim());
  if (category && category !== "all") params.append("category", category);
  if (priority && priority !== "all") params.append("priority", priority);

  const res = await fetch(`${BASE_URL}/search?${params.toString()}`);
  return handleResponse(res);
}

export async function healthCheck() {
  const res = await fetch(`${BASE_URL}/health`);
  return handleResponse(res);
}
