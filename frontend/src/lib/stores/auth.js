import { writable } from 'svelte/store';

function createAuthStore() {
  const { subscribe, set, update } = writable({
    user: null,
    isAuthenticated: false,
  });

  return {
    subscribe,
    login: (userData, accessToken, refreshToken) => {
      localStorage.setItem('access_token', accessToken);
      localStorage.setItem('refresh_token', refreshToken);
      set({ user: userData, isAuthenticated: true });
    },
    logout: () => {
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      set({ user: null, isAuthenticated: false });
    },
    setUser: (userData) => {
      update((state) => ({ ...state, user: userData, isAuthenticated: true }));
    },
  };
}

export const authStore = createAuthStore();