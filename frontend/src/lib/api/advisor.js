import client from './client';

export async function sendAdvisorMessage(message, sessionId) {
  const res = await client.post(
    '/advisor/chat/',
    { message, session_id: sessionId || null },
    { timeout: 90000 },
  );
  return res.data;
}

export async function getAdvisorSession(sessionId) {
  const res = await client.get('/advisor/chat/', { params: { session_id: sessionId } });
  return res.data;
}

export async function getAdvisorHistory() {
  const res = await client.get('/advisor/history/');
  return res.data;
}
