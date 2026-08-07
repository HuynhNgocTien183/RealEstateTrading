<script>
  import { navigate } from 'svelte-routing';
  import { login as apiLogin, getMe } from '../lib/api/auth.js';
  import { authStore } from '../lib/stores/auth.js';
  import '../styles/login.css';

  let username = '';
  let password = '';
  let error = '';
  let loading = false;

  async function handleSubmit() {
    error = '';
    loading = true;
    try {
      const { access, refresh } = await apiLogin(username, password);
      localStorage.setItem('access_token', access);
      localStorage.setItem('refresh_token', refresh);

      const user = await getMe();
      authStore.login(user, access, refresh);

      navigate('/');
    } catch (err) {
      error = err.response?.data?.detail || 'Đăng nhập thất bại. Kiểm tra lại tài khoản/mật khẩu.';
    } finally {
      loading = false;
    }
  }
</script>

<div class="login-container">
  <h2>Đăng nhập</h2>
  <form on:submit|preventDefault={handleSubmit}>
    <input type="text" placeholder="Tên đăng nhập" bind:value={username} required />
    <input type="password" placeholder="Mật khẩu" bind:value={password} required />
    {#if error}
      <p class="login-error">{error}</p>
    {/if}
    <button type="submit" disabled={loading}>
      {loading ? 'Đang đăng nhập...' : 'Đăng nhập'}
    </button>
  </form>
</div>