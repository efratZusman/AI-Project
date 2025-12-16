const BASE_URL = "http://127.0.0.1:8000";

async function handleResponse(res) {
  const data = await res.json();
  if (!res.ok) throw new Error(data.detail || "Server error");
  return data;
}

export async function analyzeBeforeSend(subject, body, isReply, threadContext) {
  const payload = {
    subject,
    body,
    language: "auto",
    is_reply: isReply,
    thread_context: threadContext,
  };

  const res = await fetch(`${BASE_URL}/analyze-before-send`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  return handleResponse(res);
}
export async function analyzeFollowUp(body, daysPassed = 3) {
  const payload = {
    email_body: body,
    days_passed: daysPassed,
  };

  const res = await fetch(`${BASE_URL}/analyze-follow-up`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  return handleResponse(res);
}

