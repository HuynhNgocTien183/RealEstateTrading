<script>
  import { onMount } from 'svelte';
  import { getListingDetail } from '../lib/api/listings.js';
  import { addFavorite } from '../lib/api/interactions.js';
  import { authStore } from '../lib/stores/auth.js';
  import PredictionForm from '../lib/components/PredictionForm.svelte';
  import '../styles/listingDetail.css';

  export let params = {};

  let listing = null;
  let loading = true;
  let error = '';
  let activeImageIndex = 0;
  let favoriteMessage = '';

  let showContactBox = false;
  let contactMessage = '';
  let sendingMessage = false;
  let sendMessageResult = '';

  function formatPrice(price) {
    if (!price) return 'Thoả thuận';
    const num = Number(price);
    if (num >= 1_000_000_000) return `${(num / 1_000_000_000).toFixed(2)} tỷ`;
    if (num >= 1_000_000) return `${(num / 1_000_000).toFixed(0)} triệu`;
    return num.toLocaleString('vi-VN');
  }

  function formatDate(dateStr) {
    if (!dateStr) return '—';
    const d = new Date(dateStr);
    return d.toLocaleDateString('vi-VN', { day: '2-digit', month: '2-digit', year: 'numeric' });
  }

  const propertyTypeLabels = {
    house: 'Nhà phố',
    apartment: 'Chung cư',
    land: 'Đất nền',
    villa: 'Biệt thự',
  };

  const legalStatusLabels = {
    'Have certificate': 'Đã có sổ',
    'Sale contract': 'Hợp đồng mua bán',
    'Pending': 'Đang chờ sổ',
  };

  const furnitureStateLabels = {
    'Full': 'Đầy đủ nội thất',
    'Basic': 'Nội thất cơ bản',
    'None': 'Không nội thất',
  };

  const statusLabels = {
    available: 'Đang bán',
    sold: 'Đã bán',
    hidden: 'Đã ẩn',
  };

  async function fetchDetail() {
    loading = true;
    error = '';
    try {
      listing = await getListingDetail(params.id);
      activeImageIndex = 0;
    } catch (err) {
      error = 'Không tải được thông tin bất động sản.';
      console.error(err);
    } finally {
      loading = false;
    }
  }

  async function handleAddFavorite() {
    if (!$authStore.isAuthenticated) {
      favoriteMessage = 'Vui lòng đăng nhập để lưu tin yêu thích.';
      return;
    }
    try {
      await addFavorite(listing.id);
      favoriteMessage = 'Đã lưu vào danh sách yêu thích!';
    } catch (err) {
      favoriteMessage = 'Không thể lưu tin này (có thể đã lưu trước đó).';
    }
  }

  function toggleContactBox() {
    if (!$authStore.isAuthenticated) {
      sendMessageResult = 'Vui lòng đăng nhập để liên hệ người bán.';
      showContactBox = true;
      return;
    }
    showContactBox = !showContactBox;
    sendMessageResult = '';
  }

  async function handleSendMessage() {
    if (!contactMessage.trim()) return;
    sendingMessage = true;
    sendMessageResult = '';
    try {
      await sendMessage({
        receiver: listing.seller,
        listing: listing.id,
        content: contactMessage,
      });
      sendMessageResult = 'Đã gửi tin nhắn cho người bán!';
      contactMessage = '';
    } catch (err) {
      sendMessageResult = 'Gửi tin nhắn thất bại. Vui lòng thử lại.';
      console.error(err);
    } finally {
      sendingMessage = false;
    }
  }

  function scrollToLocation() {
    const el = document.getElementById('listing-location-section');
    if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }

  $: if (params.id) {
    fetchDetail();
  }
</script>

<div class="listing-detail">
  {#if loading}
    <div class="listing-detail-state">Đang tải thông tin...</div>
  {:else if error}
    <div class="listing-detail-state error">{error}</div>
  {:else if listing}
    <div class="listing-detail-grid">
      <!-- Cột trái -->
      <div class="listing-detail-main">
        <div class="listing-detail-gallery">
          {#if listing.images && listing.images.length > 0}
            <img
              class="listing-detail-main-image"
              src={listing.images[activeImageIndex]?.image}
              alt={listing.title}
            />
            {#if listing.images.length > 1}
              <div class="listing-detail-thumbnails">
                {#each listing.images as img, i}
                  <button
                    type="button"
                    class="listing-detail-thumb-btn"
                    on:click={() => (activeImageIndex = i)}
                  >
                    <img
                      class="listing-detail-thumb"
                      class:active={i === activeImageIndex}
                      src={img.image}
                      alt="Ảnh {i + 1}"
                    />
                  </button>
                {/each}
              </div>
            {/if}
          {:else}
            <div class="listing-detail-no-image">Chưa có ảnh</div>
          {/if}
        </div>

        <div class="listing-detail-title-row">
          <h1>{listing.title}</h1>
          {#if listing.status}
            <span class="status-badge status-{listing.status}">
              {statusLabels[listing.status] || listing.status}
            </span>
          {/if}
        </div>

        <p class="listing-detail-location">
          📍 {listing.address}, {listing.district}, {listing.city}
        </p>

        <div class="listing-detail-action-buttons">
          <button class="btn-action btn-contact" on:click={toggleContactBox}>
            💬 Liên hệ
          </button>
          <button class="btn-action btn-location" on:click={scrollToLocation}>
            📍 Vị trí
          </button>
          <button class="btn-action btn-favorite-inline" on:click={handleAddFavorite}>
            ♡ Yêu thích
          </button>
        </div>

        {#if favoriteMessage}
          <p class="favorite-message">{favoriteMessage}</p>
        {/if}

        <div class="listing-detail-price-row">
          <span class="listing-detail-price">{formatPrice(listing.price)}</span>
        </div>

        <div class="listing-detail-specs">
          <div class="spec-item">
            <span class="spec-label">Diện tích</span>
            <span class="spec-value">{listing.area} m²</span>
          </div>

          {#if listing.floors}
            <div class="spec-item">
              <span class="spec-label">Số tầng</span>
              <span class="spec-value">{listing.floors}</span>
            </div>
          {/if}

          <div class="spec-item">
            <span class="spec-label">Phòng ngủ</span>
            <span class="spec-value">{listing.bedrooms}</span>
          </div>

          <div class="spec-item">
            <span class="spec-label">Phòng tắm</span>
            <span class="spec-value">{listing.bathrooms}</span>
          </div>

          <div class="spec-item">
            <span class="spec-label">Loại hình</span>
            <span class="spec-value">
              {propertyTypeLabels[listing.property_type] || listing.property_type}
            </span>
          </div>

          {#if listing.frontage}
            <div class="spec-item">
              <span class="spec-label">Mặt tiền</span>
              <span class="spec-value">{listing.frontage} m</span>
            </div>
          {/if}

          {#if listing.access_road}
            <div class="spec-item">
              <span class="spec-label">Đường vào</span>
              <span class="spec-value">{listing.access_road} m</span>
            </div>
          {/if}

          {#if listing.legal_status}
            <div class="spec-item">
              <span class="spec-label">Pháp lý</span>
              <span class="spec-value">
                {legalStatusLabels[listing.legal_status] || listing.legal_status}
              </span>
            </div>
          {/if}

          {#if listing.furniture_state}
            <div class="spec-item">
              <span class="spec-label">Nội thất</span>
              <span class="spec-value">
                {furnitureStateLabels[listing.furniture_state] || listing.furniture_state}
              </span>
            </div>
          {/if}

          {#if listing.house_direction}
            <div class="spec-item">
              <span class="spec-label">Hướng nhà</span>
              <span class="spec-value">{listing.house_direction}</span>
            </div>
          {/if}

          {#if listing.balcony_direction}
            <div class="spec-item">
              <span class="spec-label">Hướng ban công</span>
              <span class="spec-value">{listing.balcony_direction}</span>
            </div>
          {/if}
        </div>

        {#if listing.description}
          <div class="listing-detail-description">
            <h3>Mô tả chi tiết</h3>
            <p>{listing.description}</p>
          </div>
        {/if}

        <div class="listing-detail-meta-info">
          <div class="meta-item">
            <span>Ngày đăng</span>
            <strong>{formatDate(listing.created_at)}</strong>
          </div>
          <div class="meta-item">
            <span>Cập nhật</span>
            <strong>{formatDate(listing.updated_at)}</strong>
          </div>
          <div class="meta-item">
            <span>Lượt xem</span>
            <strong>{listing.views_count ?? 0}</strong>
          </div>
        </div>

        <div id="listing-location-section" class="listing-detail-location-section">
          <h3>Vị trí bất động sản</h3>
          {#if listing.latitude && listing.longitude}
            <iframe
              title="Bản đồ vị trí"
              class="listing-detail-map-embed"
              src={`https://www.google.com/maps?q=${listing.latitude},${listing.longitude}&output=embed`}
              loading="lazy"
            ></iframe>
          {:else}
            <p class="no-map-hint">Chưa có toạ độ chính xác cho tin đăng này.</p>
          {/if}

          {#if listing.maps_link}
            <a class="listing-detail-map-link" href={listing.maps_link} target="_blank" rel="noopener">
              🗺️ Mở trong Google Maps
            </a>
          {/if}
        </div>
      </div>

      <!-- Cột phải -->
      <div class="listing-detail-sidebar">
        <div class="listing-detail-contact-card">
          <h3>Người đăng tin</h3>
          <p class="contact-username">{listing.seller_username || 'Ẩn danh'}</p>
          <button class="btn-favorite">
            💬 Liên hệ người bán
          </button>
        </div>

        <PredictionForm {listing} />
      </div>
    </div>
  {/if}
</div>