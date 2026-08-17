<script>
  import { onMount } from 'svelte';
  import { push } from 'svelte-spa-router';
  import { createListing, updateListing, getListingDetail } from '../lib/api/listings.js';
  import { authStore } from '../lib/stores/auth.js';
  import '../styles/createListing.css';

  export let params = {};
  $: isEditMode = !!params.id;

  let title = '';
  let description = '';
  let price = '';
  let area = '';
  let bedrooms = 0;
  let bathrooms = 0;
  let floors = '';
  let propertyType = 'house';
  let address = '';
  let city = 'Hồ Chí Minh'; // Cố định, không cho sửa
  let district = '';
  let googleMapsUrl = '';

  let imageFiles = [];
  let imagePreviews = [];
  let existingImages = [];

  let error = '';
  let loading = false;
  let loadingExisting = false;

  const districtOptions = [
    'Quận 1', 'Quận 3', 'Quận 4', 'Quận 5', 'Quận 6', 'Quận 7',
    'Quận 8', 'Quận 10', 'Quận 11', 'Quận 12',
    'Bình Thạnh', 'Phú Nhuận', 'Tân Bình', 'Tân Phú',
    'Gò Vấp', 'Bình Tân', 'Thành phố Thủ Đức',
    'Bình Chánh', 'Hóc Môn', 'Củ Chi', 'Nhà Bè', 'Cần Giờ',
  ];

  async function loadExistingListing(id) {
    loadingExisting = true;
    error = '';
    try {
      const listing = await getListingDetail(id);
      title = listing.title;
      description = listing.description || '';
      price = listing.price;
      area = listing.area;
      bedrooms = listing.bedrooms;
      bathrooms = listing.bathrooms;
      floors = listing.floors || '';
      propertyType = listing.property_type;
      address = listing.address;
      district = listing.district;
      googleMapsUrl = listing.google_maps_url || '';
      existingImages = listing.images || [];
    } catch (err) {
      error = 'Không tải được thông tin tin đăng để sửa.';
      console.error(err);
    } finally {
      loadingExisting = false;
    }
  }

  function handleImageChange(event) {
    const files = Array.from(event.target.files);
    imageFiles = files;
    imagePreviews = files.map((f) => URL.createObjectURL(f));
  }

  function removeImage(index) {
    imageFiles = imageFiles.filter((_, i) => i !== index);
    imagePreviews = imagePreviews.filter((_, i) => i !== index);
  }

  async function handleSubmit() {
    error = '';

    if (!title.trim() || !price || !area || !district) {
      error = 'Vui lòng điền đầy đủ các trường bắt buộc.';
      return;
    }

    loading = true;
    try {
      const payload = {
        title,
        description,
        price,
        area,
        bedrooms,
        bathrooms,
        floors: floors || undefined,
        property_type: propertyType,
        address,
        city,
        district,
        google_maps_url: googleMapsUrl || undefined,
      };

      if (isEditMode) {
        await updateListing(params.id, payload);
        push(`/listings/${params.id}`);
      } else {
        await createListing(payload, imageFiles);
        push('/my-listings');   // ← Đổi sang trang "Tin của tôi"
      }
    } catch (err) {
      const resErrors = err.response?.data;
      if (resErrors && typeof resErrors === 'object') {
        const firstKey = Object.keys(resErrors)[0];
        const firstMsg = Array.isArray(resErrors[firstKey])
          ? resErrors[firstKey][0]
          : resErrors[firstKey];
        error = firstMsg || 'Thao tác thất bại. Vui lòng thử lại.';
      } else {
        error = 'Thao tác thất bại. Vui lòng thử lại.';
      }
      console.error(err);
    } finally {
      loading = false;
    }
  }

  onMount(() => {
    if (isEditMode) {
      loadExistingListing(params.id);
    }
  });
</script>

<div class="create-listing-page">
  {#if !$authStore.isAuthenticated}
    <div class="create-listing-state error">Vui lòng đăng nhập để đăng tin.</div>
  {:else}
    <h1>{isEditMode ? 'Chỉnh sửa tin đăng' : 'Đăng tin bất động sản'}</h1>

    {#if loadingExisting}
      <div class="create-listing-state">Đang tải thông tin tin đăng...</div>
    {:else}
      <form on:submit|preventDefault={handleSubmit}>
        <section class="form-section">
          <h3>Thông tin cơ bản</h3>

          <label>
            Tiêu đề tin đăng *
            <input type="text" bind:value={title} placeholder="VD: Nhà phố mặt tiền Quận 7" required />
          </label>

          <label>
            Mô tả chi tiết
            <textarea bind:value={description} rows="5" placeholder="Mô tả về bất động sản..."></textarea>
          </label>

          <div class="form-row">
            <label>
              Loại hình *
              <select bind:value={propertyType}>
                <option value="house">Nhà phố</option>
                <option value="apartment">Chung cư</option>
                <option value="land">Đất nền</option>
                <option value="villa">Biệt thự</option>
              </select>
            </label>

            <label>
              Giá bán (VNĐ) *
              <input type="number" bind:value={price} min="0" placeholder="VD: 2500000000" required />
            </label>
          </div>
        </section>

        <section class="form-section">
          <h3>Thông số kỹ thuật</h3>

          <div class="form-row">
            <label>
              Diện tích (m²) *
              <input type="number" bind:value={area} min="1" required />
            </label>
            <label>
              Số tầng
              <input type="number" bind:value={floors} min="1" />
            </label>
          </div>

          <div class="form-row">
            <label>
              Phòng ngủ *
              <input type="number" bind:value={bedrooms} min="0" required />
            </label>
            <label>
              Phòng tắm *
              <input type="number" bind:value={bathrooms} min="0" required />
            </label>
          </div>
        </section>

        <section class="form-section">
          <h3>Vị trí</h3>

          <label>
            Địa chỉ cụ thể *
            <input type="text" bind:value={address} placeholder="VD: 123 Đường Nguyễn Văn Linh" required />
          </label>

          <div class="form-row">
            <label>
              Thành phố
              <input type="text" value={city} disabled />
            </label>
            <label>
              Quận/Huyện *
              <select bind:value={district} required>
                <option value="">-- Chọn Quận/Huyện --</option>
                {#each districtOptions as d}
                  <option value={d}>{d}</option>
                {/each}
              </select>
            </label>
          </div>

          <label>
            Link Google Maps (không bắt buộc)
            <input type="url" bind:value={googleMapsUrl} placeholder="https://maps.google.com/..." />
          </label>
        </section>

        <section class="form-section">
          <h3>Hình ảnh</h3>

          {#if isEditMode}
            {#if existingImages.length > 0}
              <div class="image-preview-grid">
                {#each existingImages as img}
                  <div class="image-preview-item">
                    <img src={img.image} alt="Ảnh hiện có" />
                  </div>
                {/each}
              </div>
              <p class="edit-image-hint">Ảnh hiện tại không thể chỉnh sửa trong form này.</p>
            {/if}
          {:else}
            <label class="image-upload-label">
              <input type="file" accept="image/*" multiple on:change={handleImageChange} />
              <span>📷 Chọn ảnh (ảnh đầu tiên sẽ là ảnh đại diện)</span>
            </label>

            {#if imagePreviews.length > 0}
              <div class="image-preview-grid">
                {#each imagePreviews as src, i}
                  <div class="image-preview-item">
                    <img {src} alt="Ảnh {i + 1}" />
                    {#if i === 0}
                      <span class="primary-badge">Đại diện</span>
                    {/if}
                    <button type="button" class="remove-image-btn" on:click={() => removeImage(i)}>
                      ✕
                    </button>
                  </div>
                {/each}
              </div>
            {/if}
          {/if}
        </section>

        {#if error}
          <p class="create-listing-error">{error}</p>
        {/if}

        <button type="submit" class="submit-btn" disabled={loading || loadingExisting}>
          {#if loading}
            {isEditMode ? 'Đang lưu...' : 'Đang đăng tin...'}
          {:else}
            {isEditMode ? 'Lưu thay đổi' : 'Đăng tin ngay'}
          {/if}
        </button>
      </form>
    {/if}
  {/if}
</div>