<script>
  import { onMount } from 'svelte';
  import Router from 'svelte-spa-router';
  import Navbar from './lib/components/Navbar.svelte';
  import routes from './routes.js';
  import { authStore } from './lib/stores/auth';
  import { getMe } from './lib/api/auth';

  let checkingSession = true;

  onMount(async () => {
    const token = localStorage.getItem('access_token');
    if (token) {
      try {
        const user = await getMe();
        authStore.setUser(user);
      } catch (err) {
        // Token đã hết hạn và refresh cũng thất bại -> coi như chưa đăng nhập
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
      }
    }
    checkingSession = false;
  });
</script>

{#if checkingSession}
  <div class="app-loading">Đang tải...</div>
{:else}
  <Navbar />
  <main>
    <Router {routes} />
  </main>
{/if}

<style>
  main {
    max-width: 1200px;
    margin: 0 auto;
    padding: 1rem;
  }

  .app-loading {
    display: flex;
    align-items: center;
    justify-content: center;
    height: 100vh;
    color: var(--color-text-muted);
  }
</style>