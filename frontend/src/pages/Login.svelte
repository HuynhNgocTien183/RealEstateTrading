<script>
  import { push } from 'svelte-spa-router';
  import { login as apiLogin, getMe } from '../lib/api/auth';
  import { authStore } from '../lib/stores/auth';
  import {Eye, EyeOff} from '@lucide/svelte'; 
  import '../styles/login.css';

  let username = '';
  let password = '';
  let error = '';
  let loading = false;
  let showPassword = false;

  async function handleSubmit() {
    error = '';
    loading = true;
    try {
      const { access, refresh } = await apiLogin(username, password);
      localStorage.setItem('access_token', access);
      localStorage.setItem('refresh_token', refresh);

      const user = await getMe();
      authStore.login(user, access, refresh);

      push('/');
    } catch (err) {
      if (err.response?.status === 401 || err.response?.status === 400) {
        error = 'Sai tên đăng nhập hoặc mật khẩu.';
      } else {
        error = 'Đăng nhập thất bại. Vui lòng thử lại.';
        
    }
    } finally {
      loading = false;
    }
  }
</script>

<div class="login-container">
  <h2>Đăng nhập</h2>
  <form on:submit|preventDefault={handleSubmit}>
    <input type="text" placeholder="Tên đăng nhập" bind:value={username} required />
    <div class="password-input-wrapper">
      <input
        type={showPassword ? 'text' : 'password'}
        placeholder="Mật khẩu"
        bind:value={password}
        required
      />
      <button type="button" class="password-toggle-btn" on:click={() => (showPassword = !showPassword)}>
        {#if showPassword}
          <EyeOff size={18} color="currentColor" background="none" />
        {:else}
          <Eye size={18} color="currentColor" background="none" />
        {/if}
      </button>
    </div>
    {#if error}
      <p class="login-error">{error}</p>
    {/if}
    <button type="submit" class="login-submit-btn" disabled={loading}>
      {loading ? 'Đang đăng nhập...' : 'Đăng nhập'}
    </button>
  </form>
</div>