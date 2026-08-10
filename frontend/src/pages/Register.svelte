<script>
  import { push } from 'svelte-spa-router';
  import { register as apiRegister } from '../lib/api/auth';
  import { getMe } from '../lib/api/auth';
  import { authStore } from '../lib/stores/auth';
  import '../styles/register.css';

  let username = '';
  let email = '';
  let phone = '';
  let password = '';
  let confirmPassword = '';
  let role = 'buyer'; // mặc định là Người mua

  let error = '';
  let loading = false;

  async function handleSubmit() {
    error = '';

    if (password !== confirmPassword) {
      error = 'Mật khẩu xác nhận không khớp.';
      return;
    }

    if (password.length < 6) {
      error = 'Mật khẩu phải có ít nhất 6 ký tự.';
      return;
    }

    loading = true;
    try {
      const data = await apiRegister({
        username,
        email,
        phone,
        password,
        password2: confirmPassword,
        role,
      });

      // Backend trả JWT ngay sau khi đăng ký thành công
      localStorage.setItem('access_token', data.access);
      localStorage.setItem('refresh_token', data.refresh);

      const user = await getMe();
      authStore.login(user, data.access, data.refresh);

      push('/');
    } catch (err) {
      const resErrors = err.response?.data;
      if (resErrors && typeof resErrors === 'object') {
        // Django REST Framework thường trả lỗi dạng { field: ["thông báo lỗi"] }
        const firstKey = Object.keys(resErrors)[0];
        const firstMsg = Array.isArray(resErrors[firstKey])
          ? resErrors[firstKey][0]
          : resErrors[firstKey];
        error = firstMsg || 'Đăng ký thất bại. Vui lòng thử lại.';
      } else {
        error = 'Đăng ký thất bại. Vui lòng thử lại.';
      }
    } finally {
      loading = false;
    }
  }
</script>

<div class="register-container">
  <h2>Tạo tài khoản mới</h2>

  <form on:submit|preventDefault={handleSubmit}>
    <div class="register-field">
      <label for="username">Tên đăng nhập</label>
      <input id="username" type="text" bind:value={username} required minlength="3" />
    </div>

    <div class="register-field">
      <label for="email">Email</label>
      <input id="email" type="email" bind:value={email} required />
    </div>

    <div class="register-field">
      <label for="phone">Số điện thoại</label>
      <input id="phone" type="tel" bind:value={phone} placeholder="Không bắt buộc" />
    </div>

    <div class="register-field">
      <label for="password">Mật khẩu</label>
      <input id="password" type="password" bind:value={password} required minlength="6" />
    </div>

    <div class="register-field">
      <label for="confirmPassword">Xác nhận mật khẩu</label>
      <input
        id="confirmPassword"
        type="password"
        bind:value={confirmPassword}
        required
        minlength="6"
      />
    </div>

    <div class="register-field">
      <span class="register-role-label">Bạn muốn đăng ký với vai trò</span>

      <div class="register-role-options">
        <label class="register-role-card" class:active={role === 'buyer'}>
          <input type="radio" bind:group={role} value="buyer" />
          <div class="register-role-icon">🏠</div>
          <div class="register-role-text">
            <strong>Người mua</strong>
            <span>Tìm kiếm và mua bất động sản</span>
          </div>
        </label>

        <label class="register-role-card" class:active={role === 'seller'}>
          <input type="radio" bind:group={role} value="seller" />
          <div class="register-role-icon">🏷️</div>
          <div class="register-role-text">
            <strong>Người bán</strong>
            <span>Đăng tin và bán bất động sản</span>
          </div>
        </label>
      </div>
    </div>

    {#if error}
      <p class="register-error">{error}</p>
    {/if}

    <button type="submit" disabled={loading}>
      {loading ? 'Đang tạo tài khoản...' : 'Đăng ký'}
    </button>

    <p class="register-login-hint">
      Đã có tài khoản? <a href="#/login">Đăng nhập ngay</a>
    </p>
  </form>
</div>