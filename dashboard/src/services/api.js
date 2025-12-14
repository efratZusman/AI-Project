const BASE_URL = "http://127.0.0.1:8000";

async function handleResponse(response) {
  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.detail || "Server error");
  }
  return data;
}

export async function analyzeBeforeSend(draft) {
  const res = await fetch(`${BASE_URL}/analyze-before-send`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ draft }),
  });
  return handleResponse(res);
}

export async function analyzeFollowUp(email_body, days_passed = 3) {
  const res = await fetch(`${BASE_URL}/analyze-follow-up`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email_body, days_passed }),
  });
  return handleResponse(res);
}

export async function healthCheck() {
  const res = await fetch(`${BASE_URL}/health`);
  return handleResponse(res);
}
