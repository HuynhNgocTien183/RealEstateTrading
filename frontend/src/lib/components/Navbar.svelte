<script>
  import { authStore } from '../stores/auth';
  import { logout as apiLogout } from '../api/auth';
  import '../../styles/navbar.css';

  async function handleLogout() {
    const refreshToken = localStorage.getItem('refresh_token');
    try {
      if (refreshToken) await apiLogout(refreshToken);
    } catch (err) {
      console.error(err);
    } finally {
      authStore.logout();
      window.location.href = '#/';
    }
  }
</script>

<nav class="navbar">
  <a href="#/" class="navbar-logo">RealEstateTrading</a>

  <div class="navbar-links">
    {#if $authStore.isAuthenticated}
      {#if $authStore.user?.role === 'admin'}
        <a href="#/admin/review">Duyệt tin</a>
      {/if}
      {#if $authStore.user?.role === 'seller'}
        <a href="#/create-listing">Đăng tin</a>
        <a href="#/my-listings">Tin của tôi</a>
      {/if}
      {#if $authStore.user?.role === 'buyer'}
        <a href="#/saved-listings">Tin đã thích</a>
      {/if}
      <a href="#/profile">Hồ sơ</a>
      
      <span class="navbar-username">Xin chào, {$authStore.user?.username}</span>
      <button class="navbar-logout-btn" on:click={handleLogout}>Đăng xuất</button>
    {:else}
      <a href="#/login">Đăng nhập</a>
      <a href="#/register">Đăng ký</a>
    {/if}
  </div>
</nav>
