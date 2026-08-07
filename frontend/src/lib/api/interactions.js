import client from './client';

export async function getMessages(params = {}) {
  const res = await client.get('/interactions/messages/', { params });
  return res.data;
}

export async function sendMessage(data) {
  const res = await client.post('/interactions/messages/', data);
  return res.data;
}

export async function getConversations() {
  const res = await client.get('/interactions/messages/conversations/');
  return res.data;
}

export async function markAsRead(data) {
  return client.post('/interactions/messages/mark_read/', data);
}

export async function getFavorites() {
  const res = await client.get('/interactions/favorites/');
  return res.data;
}

export async function addFavorite(listingId) {
  const res = await client.post('/interactions/favorites/', { listing: listingId });
  return res.data;
}

export async function removeFavorite(id) {
  return client.delete(`/interactions/favorites/${id}/`);
}