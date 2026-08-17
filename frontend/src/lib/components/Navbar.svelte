<script>
  import { push } from 'svelte-spa-router';
  import active from 'svelte-spa-router/active';
  import { authStore } from '../stores/auth';
  import { logout as apiLogout } from '../api/auth';
  import '../../styles/navbar.css';

  let scrolled = false;
  let dropdownOpen = false;
  let mobileMenuOpen = false;

  function handleScroll() {
    scrolled = window.scrollY > 8;
  }

  function toggleDropdown() {
    dropdownOpen = !dropdownOpen;
  }

  function closeDropdown() {
    dropdownOpen = false;
  }

  function handleClickOutside(node) {
    const handler = (e) => {
      if (!node.contains(e.target)) closeDropdown();
    };
    document.addEventListener('click', handler, true);
    return { destroy: () => document.removeEventListener('click', handler, true) };
  }

  async function handleLogout() {
    closeDropdown();
    mobileMenuOpen = false;
    const refreshToken = localStorage.getItem('refresh_token');
    try {
      if (refreshToken) await apiLogout(refreshToken);
    } catch (err) {
      console.error(err);
    } finally {
      authStore.logout();
      push('/');
    }
  }

  function goTo(path) {
    mobileMenuOpen = false;
    push(path);
  }
</script>

<svelte:window on:scroll={handleScroll} />

<nav class="navbar" class:scrolled>
  <div class="navbar-inner">
    <a href="#/" class="navbar-logo">
      <span class="navbar-logo-mark">R</span>
      <span class="navbar-logo-text">RealEstateTrading</span>
    </a>

    <button
      class="navbar-burger"
      aria-label="Mở menu"
      on:click={() => (mobileMenuOpen = !mobileMenuOpen)}
    >
      <span class:open={mobileMenuOpen}></span>
      <span class:open={mobileMenuOpen}></span>
      <span class:open={mobileMenuOpen}></span>
    </button>

    <div class="navbar-links" class:mobile-open={mobileMenuOpen}>
      {#if $authStore.isAuthenticated}
        {#if $authStore.user?.role === 'admin'}
          <a href="#/admin/review" use:active class="nav-link" on:click={() => (mobileMenuOpen = false)}>
            Duyệt tin
          </a>
        {/if}
        {#if $authStore.user?.role === 'seller'}
          <a href="#/create-listing" use:active class="nav-link" on:click={() => (mobileMenuOpen = false)}>
            Đăng tin
          </a>
          <a href="#/my-listings" use:active class="nav-link" on:click={() => (mobileMenuOpen = false)}>
            Tin của tôi
          </a>
        {/if}
        <a href="#/saved-listings" use:active class="nav-link" on:click={() => (mobileMenuOpen = false)}>
          Yêu thích
        </a>

        <div class="navbar-mobile-account">
          <a href="#/profile" class="nav-link" on:click={() => (mobileMenuOpen = false)}>Hồ sơ</a>
          <button class="nav-link nav-link-logout" on:click={handleLogout}>Đăng xuất</button>
        </div>

        <div class="navbar-account" use:handleClickOutside>
          <button class="navbar-avatar-btn" on:click={toggleDropdown}>
            {#if $authStore.user?.avatar}
              <img class="navbar-avatar-img" src={$authStore.user.avatar} alt={$authStore.user.username} />
            {:else}
              <span class="navbar-avatar-fallback">
                {$authStore.user?.username?.charAt(0)?.toUpperCase() || '?'}
              </span>
            {/if}
            <span class="navbar-username">{$authStore.user?.full_name || $authStore.user?.username}</span>
            <svg class="navbar-caret" class:open={dropdownOpen} width="10" height="6" viewBox="0 0 10 6" fill="none">
              <path d="M1 1L5 5L9 1" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </button>

          {#if dropdownOpen}
            <div class="navbar-dropdown">
              <button class="dropdown-item" on:click={() => { closeDropdown(); goTo('/profile'); }}>
                👤 Hồ sơ của tôi
              </button>
              <div class="dropdown-divider"></div>
              <button class="dropdown-item dropdown-item-danger" on:click={handleLogout}>
                ↪ Đăng xuất
              </button>
            </div>
          {/if}
        </div>
      {:else}
        <a href="#/login" use:active class="nav-link" on:click={() => (mobileMenuOpen = false)}>Đăng nhập</a>
        <a href="#/register" use:active class="nav-link nav-link-cta" on:click={() => (mobileMenuOpen = false)}>Đăng ký</a>
      {/if}
    </div>
  </div>
</nav>