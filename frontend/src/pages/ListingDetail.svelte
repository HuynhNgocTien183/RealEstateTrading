<script>
  import { onMount } from "svelte";
  import { getListingDetail } from "../lib/api/listings.js";
  import {
    addFavorite,
    removeFavorite,
    getFavorites,
  } from "../lib/api/interactions.js";
  import { authStore } from "../lib/stores/auth.js";
  import PredictionForm from "../lib/components/PredictionForm.svelte";
  import "../styles/listingDetail.css";
  import "../styles/app.css";

  export let params = {};

  let listing = null;
  let loading = true;
  let error = "";
  let activeImageIndex = 0;
  let favoriteMessage = "";
  let isFavorited = false;
  let favoriteId = null;
  let favoriteLoading = false;

  function formatPrice(price) {
    if (!price) return "Thoả thuận";
    const num = Number(price);
    if (num >= 1_000_000_000) return `${(num / 1_000_000_000).toFixed(2)} tỷ`;
    if (num >= 1_000_000) return `${(num / 1_000_000).toFixed(0)} triệu`;
    return num.toLocaleString("vi-VN");
  }

  function formatDate(dateStr) {
    if (!dateStr) return "—";
    const d = new Date(dateStr);
    return d.toLocaleDateString("vi-VN", {
      day: "2-digit",
      month: "2-digit",
      year: "numeric",
    });
  }

  const propertyTypeLabels = {
    house: "Nhà phố",
    apartment: "Chung cư",
    land: "Đất nền",
    villa: "Biệt thự",
  };

  const legalStatusLabels = {
    "Have certificate": "Đã có sổ",
    "Sale contract": "Hợp đồng mua bán",
    Pending: "Đang chờ sổ",
  };

  const furnitureStateLabels = {
    Full: "Đầy đủ nội thất",
    Basic: "Nội thất cơ bản",
    None: "Không nội thất",
  };

  const statusLabels = {
    available: "Đang bán",
    sold: "Đã bán",
    hidden: "Đã ẩn",
  };

  async function fetchDetail() {
    loading = true;
    error = "";
    try {
      listing = await getListingDetail(params.id);
      activeImageIndex = 0;
      await checkFavoriteStatus();
    } catch (err) {
      error = "Không tải được thông tin bất động sản.";
      console.error(err);
    } finally {
      loading = false;
    }
  }

  async function checkFavoriteStatus() {
    if (!$authStore.isAuthenticated) return;
    try {
      const data = await getFavorites();
      const favorites = Array.isArray(data) ? data : (data.results ?? []);
      const found = favorites.find(
        (f) => (f.listing_detail?.id ?? f.listing) === listing.id,
      );
      if (found) {
        isFavorited = true;
        favoriteId = found.id;
      } else {
        isFavorited = false;
        favoriteId = null;
      }
    } catch (err) {
      console.error(err);
    }
  }

  async function handleToggleFavorite() {
    if (!$authStore.isAuthenticated) {
      favoriteMessage = "Vui lòng đăng nhập để lưu tin yêu thích.";
      return;
    }

    favoriteLoading = true;
    favoriteMessage = "";
    try {
      if (isFavorited) {
        await removeFavorite(favoriteId);
        isFavorited = false;
        favoriteId = null;
        listing.favorites_count = Math.max(0, (listing.favorites_count ?? 1) - 1);
        favoriteMessage = "Đã bỏ khỏi danh sách yêu thích.";
      } else {
        const created = await addFavorite(listing.id);
        isFavorited = true;
        favoriteId = created.id;
        listing.favorites_count = (listing.favorites_count ?? 0) + 1;
        favoriteMessage = "Đã lưu vào danh sách yêu thích!";
      }
    } catch (err) {
      favoriteMessage = "Thao tác thất bại. Vui lòng thử lại.";
      console.error(err);
    } finally {
      favoriteLoading = false;
    }
  }

  function scrollToLocation() {
    const el = document.getElementById("listing-location-section");
    if (el) el.scrollIntoView({ behavior: "smooth", block: "start" });
  }

  $: if (params.id) {
    fetchDetail();
  }

  function extractLatLngFromMapsUrl(url) {
    if (!url) return null;

    const pinMatch = url.match(/!3d(-?\d+\.\d+)!4d(-?\d+\.\d+)/);
    if (pinMatch) {
      return { lat: pinMatch[1], lng: pinMatch[2] };
    }

    const viewMatch = url.match(/@(-?\d+\.\d+),(-?\d+\.\d+)/);
    if (viewMatch) {
      return { lat: viewMatch[1], lng: viewMatch[2] };
    }

    return null;
  }

  function getEmbedMapUrl(listing) {
    const extracted = extractLatLngFromMapsUrl(listing.google_maps_url);
    if (extracted) {
      return `https://www.google.com/maps?q=${extracted.lat},${extracted.lng}&output=embed`;
    }

    if (listing.latitude && listing.longitude) {
      return `https://www.google.com/maps?q=${listing.latitude},${listing.longitude}&output=embed`;
    }

    return null;
  }
</script>

<div class="listing-detail">
  <button class="btn-back" on:click={() => history.back()}> ← Quay lại </button>
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
          <button class="btn-action btn-location" on:click={scrollToLocation}>
            📍 Vị trí
          </button>
          <button
            class="btn-action btn-favorite-inline"
            class:favorited={isFavorited}
            disabled={favoriteLoading}
            on:click={handleToggleFavorite}
          >
            {isFavorited ? "❤ Đã thích" : "♡ Yêu thích"}
            <span class="favorite-count-badge">{listing.favorites_count ?? 0}</span>
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
              {propertyTypeLabels[listing.property_type] ||
                listing.property_type}
            </span>
          </div>

          {#if listing.legal_status}
            <div class="spec-item">
              <span class="spec-label">Pháp lý</span>
              <span class="spec-value">
                {legalStatusLabels[listing.legal_status] ||
                  listing.legal_status}
              </span>
            </div>
          {/if}

          {#if listing.furniture_state}
            <div class="spec-item">
              <span class="spec-label">Nội thất</span>
              <span class="spec-value">
                {furnitureStateLabels[listing.furniture_state] ||
                  listing.furniture_state}
              </span>
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

        <div
          id="listing-location-section"
          class="listing-detail-location-section"
        >
          <h3>Vị trí bất động sản</h3>
          {#if getEmbedMapUrl(listing)}
            <iframe
              title="Bản đồ vị trí"
              class="listing-detail-map-embed"
              src={getEmbedMapUrl(listing)}
              loading="lazy"
            ></iframe>
          {:else}
            <p class="no-map-hint">Chưa có vị trí cho tin đăng này.</p>
          {/if}
        </div>
      </div>

      <!-- Cột phải -->
      <div class="listing-detail-sidebar">
        <div class="listing-detail-contact-card">
          <h3>Người đăng tin</h3>
          <p class="contact-username">
            {listing.seller_full_name || listing.seller_username || "Ẩn danh"}
          </p>
          <p class="contact-phone">📞 {listing.seller_phone || "Không có"}</p>
          <p class="contact-email">
            ✉️
            {#if listing.seller_email}
              
              <a  href={`https://mail.google.com/mail/?view=cm&fs=1&to=${listing.seller_email}`}
                target="_blank"
                rel="noopener"
                class="contact-email-link"
              >
                {listing.seller_email}
              </a>
            {:else}
              Không có
            {/if}
          </p>
        </div>

        <PredictionForm {listing} />
      </div>
    </div>
  {/if}
</div>