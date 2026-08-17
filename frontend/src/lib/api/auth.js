import client from './client';

export async function login(username, password) {
  const res = await client.post('/token/', { username, password });
  return res.data; // { access, refresh }
}

export async function register(userData) {
  const formData = new FormData();
  Object.entries(userData).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== '') {
      formData.append(key, value);
    }
  });

  const res = await client.post('/users/register/', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return res.data;
}


export async function logout(refreshToken) {
  return client.post('/users/logout/', { refresh: refreshToken });
}

export async function getMe() {
  const res = await client.get('/users/me/');
  return res.data;
}

export async function updateMe(data) {
  const res = await client.patch('/users/me/', data);
  return res.data;
}