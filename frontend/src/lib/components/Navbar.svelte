<script>
  import { Link } from 'svelte-routing';
  import { authStore } from '../stores/auth.js';
  import { logout as apiLogout } from '../api/auth.js';
  import '../../styles/navbar.css';

  async function handleLogout() {
    const refreshToken = localStorage.getItem('refresh_token');
    try {
      if (refreshToken) await apiLogout(refreshToken);
    } catch (err) {
      console.error(err);
    } finally {
      authStore.logout();
      window.location.href = '/';
    }
  }
</script>

<nav class="navbar">
  <Link to="/" class="navbar-logo">RealEstateTrading</Link>

  <div class="navbar-links">
    {#if $authStore.isAuthenticated}
      <Link to="/create-listing">Đăng tin</Link>
      <Link to="/my-listings">Tin của tôi</Link>
      <span class="navbar-username">Xin chào, {$authStore.user?.username}</span>
      <button class="navbar-logout-btn" on:click={handleLogout}>Đăng xuất</button>
    {:else}
      <Link to="/login">Đăng nhập</Link>
      <Link to="/register">Đăng ký</Link>
    {/if}
  </div>
</nav>