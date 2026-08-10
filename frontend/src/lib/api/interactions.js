import client from './client';

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