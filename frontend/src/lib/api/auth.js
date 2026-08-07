import client from './client';

export async function login(username, password) {
  const res = await client.post('/token/', { username, password });
  return res.data; // { access, refresh }
}

export async function register(userData) {
  const res = await client.post('/users/register/', userData);
  return res.data; // trả JWT ngay sau khi đăng ký
}

export async function getMe() {
  const res = await client.get('/users/me/');
  return res.data;
}

export async function logout(refreshToken) {
  return client.post('/users/logout/', { refresh: refreshToken });
}