import { writable } from 'svelte/store';

export const homeState = writable({
  currentPage: 1,
  filters: {},
});