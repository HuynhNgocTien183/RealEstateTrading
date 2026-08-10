import client from './client';

export async function predictPrice(data) {
  const res = await client.post('/predictions/predict/', data);
  return res.data;
}

export async function getPredictionHistory() {
  const res = await client.get('/predictions/history/');
  return res.data;
}