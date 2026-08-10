<script>
  import { onMount } from 'svelte';
  import { getMe, updateMe } from '../lib/api/auth';
  import { authStore } from '../lib/stores/auth';
  import '../styles/profile.css';

  let loading = true;
  let error = '';
  let saving = false;
  let saveMessage = '';

  let username = '';
  let email = '';
  let phone = '';
  let role = '';

  const roleLabels = {
    buyer: 'Người mua',
    seller: 'Người bán',
    admin: 'Quản trị viên',
  };

  async function loadProfile() {
    loading = true;
    error = '';
    try {
      const user = await getMe();
      username = user.username;
      email = user.email || '';
      phone = user.phone || '';
      role = user.role;
    } catch (err) {
      error = 'Không tải được thông tin hồ sơ.';
      console.error(err);
    } finally {
      loading = false;
    }
  }

  async function handleSave() {
    saving = true;
    saveMessage = '';
    try {
      const updated = await updateMe({ email, phone });
      authStore.setUser(updated);
      saveMessage = 'Đã cập nhật thông tin thành công!';
    } catch (err) {
      saveMessage = 'Cập nhật thất bại. Vui lòng thử lại.';
      console.error(err);
    } finally {
      saving = false;
    }
  }

  onMount(() => {
    loadProfile();
  });
</script>

<div class="profile-page">
  <h1>Hồ sơ cá nhân</h1>

  {#if loading}
    <div class="profile-state">Đang tải...</div>
  {:else if error}
    <div class="profile-state error">{error}</div>
  {:else}
    <div class="profile-card">
      <div class="profile-avatar-placeholder">
        {username?.charAt(0)?.toUpperCase() || '?'}
      </div>

      <form on:submit|preventDefault={handleSave}>
        <div class="profile-field">
          <label for="username">Tên đăng nhập</label>
          <input id="username" type="text" value={username} disabled />
        </div>

        <div class="profile-field">
          <label for="role">Vai trò</label>
          <input id="role" type="text" value={roleLabels[role] || role} disabled />
        </div>

        <div class="profile-field">
          <label for="email">Email</label>
          <input id="email" type="email" bind:value={email} />
        </div>

        <div class="profile-field">
          <label for="phone">Số điện thoại</label>
          <input id="phone" type="tel" bind:value={phone} />
        </div>

        {#if saveMessage}
          <p class="profile-save-message">{saveMessage}</p>
        {/if}

        <button type="submit" disabled={saving}>
          {saving ? 'Đang lưu...' : 'Lưu thay đổi'}
        </button>
      </form>
    </div>
  {/if}
</div>