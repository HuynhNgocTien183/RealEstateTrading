<script>
  import { onMount } from "svelte";
  import { getMe, updateMe } from "../lib/api/auth";
  import { authStore } from "../lib/stores/auth";
  import "../styles/profile.css";

  let loading = true;
  let error = "";
  let saving = false;
  let saveMessage = "";

  let username = "";
  let firstName = "";
  let lastName = "";
  let fullName = "";
  let email = "";
  let phone = "";
  let role = "";
  let avatarUrl = "";

  const roleLabels = {
    buyer: "Người mua",
    seller: "Người bán",
    admin: "Quản trị viên",
  };

  async function loadProfile() {
    loading = true;
    error = '';
    try {
      const user = await getMe();
      username = user.username;
      firstName = user.first_name || '';
      lastName = user.last_name || '';
      fullName = user.full_name;
      email = user.email || '';
      phone = user.phone || '';
      role = user.role;
      avatarUrl = user.avatar || '';
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
      const updated = await updateMe({ email, phone, first_name: firstName, last_name: lastName });
      authStore.setUser(updated);
      avatarUrl = updated.avatar || avatarUrl;
      fullName = updated.full_name;
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
      {#if avatarUrl}
        <img
          class="profile-avatar-image"
          src={avatarUrl}
          alt="Avatar của {username}"
        />
      {:else}
        <div class="profile-avatar-placeholder">
          {username?.charAt(0)?.toUpperCase() || "?"}
        </div>
      {/if}

      <p class="profile-fullname-display">{fullName}</p>

      <form on:submit|preventDefault={handleSave}>
        <div class="profile-field">
          <label for="username">Tên đăng nhập</label>
          <input id="username" type="text" value={username} disabled />
        </div>

        <div class="profile-field">
          <label for="role">Vai trò</label>
          <input
            id="role"
            type="text"
            value={roleLabels[role] || role}
            disabled
          />
        </div>

        <div class="profile-field-row">
          <div class="profile-field">
            <label for="firstName">Họ</label>
            <input
              id="firstName"
              type="text"
              bind:value={firstName}
              placeholder="VD: Nguyễn Văn"
            />
          </div>
          <div class="profile-field">
            <label for="lastName">Tên</label>
            <input
              id="lastName"
              type="text"
              bind:value={lastName}
              placeholder="VD: A"
            />
          </div>
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
          {saving ? "Đang lưu..." : "Lưu thay đổi"}
        </button>
      </form>
    </div>
  {/if}
</div>