<script>
  import { onMount } from 'svelte';
  import { getMyListings, deleteListing } from '../lib/api/listings.js';
  import { authStore } from '../lib/stores/auth.js';
  import '../styles/myListings.css';

  let listings = [];
  let loading = true;
  let error = '';
  let deletingId = null;

  const statusLabels = {
    available: 'Đang bán',
    sold: 'Đã bán',
    hidden: 'Đã ẩn',
  };

  const approvalLabels = {
    pending: 'Chờ duyệt',
    approved: 'Đã duyệt',
    rejected: 'Bị từ chối',
  };

  function formatPrice(price) {
    if (!price) return 'Thoả thuận';
    const num = Number(price);
    if (num >= 1_000_000_000) return `${(num / 1_000_000_000).toFixed(2)} tỷ`;
    if (num >= 1_000_000) return `${(num / 1_000_000).toFixed(0)} triệu`;
    return num.toLocaleString('vi-VN');
  }

  function formatDate(dateStr) {
    if (!dateStr) return '—';
    return new Date(dateStr).toLocaleDateString('vi-VN', {
      day: '2-digit', month: '2-digit', year: 'numeric',
    });
  }

  async function fetchMyListings() {
    loading = true;
    error = '';
    try {
      const data = await getMyListings();
      listings = Array.isArray(data) ? data : data.results ?? [];
    } catch (err) {
      error = 'Không tải được danh sách tin của bạn.';
      console.error(err);
    } finally {
      loading = false;
    }
  }

  async function handleDelete(listing) {
    if (!confirm(`Bạn chắc chắn muốn xoá tin "${listing.title}"?`)) return;
    deletingId = listing.id;
    try {
      await deleteListing(listing.id);
      listings = listings.filter((l) => l.id !== listing.id);
    } catch (err) {
      alert('Xoá tin thất bại. Vui lòng thử lại.');
      console.error(err);
    } finally {
      deletingId = null;
    }
  }

  onMount(() => {
    fetchMyListings();
  });
</script>

<div class="my-listing-page">
  {#if !$authStore.isAuthenticated}
    <div class="my-listing-state error">Vui lòng đăng nhập để xem tin của bạn.</div>
  {:else}
    <div class="my-listing-header">
      <h1>Tin của tôi ({listings.length})</h1>
      <a href="#/create-listing" class="btn-create-new">+ Đăng tin mới</a>
    </div>

    {#if loading}
      <div class="my-listing-state">Đang tải danh sách...</div>
    {:else if error}
      <div class="my-listing-state error">{error}</div>
    {:else if listings.length === 0}
      <div class="my-listing-state">
        Bạn chưa đăng tin nào. <a href="#/create-listing">Đăng tin ngay</a>
      </div>
    {:else}
      <div class="my-listing-list">
        {#each listings as listing (listing.id)}
          <div class="my-listing-card">
            <div class="my-listing-image">
              {#if listing.images && listing.images.length > 0}
                <img src={listing.images[0].image} alt={listing.title} />
              {:else}
                <div class="my-listing-no-image">Chưa có ảnh</div>
              {/if}
            </div>

            <div class="my-listing-info">
              <div class="my-listing-info-header">
                <h3>{listing.title}</h3>
                <span class="my-listing-price">{formatPrice(listing.price)}</span>
              </div>

              <div class="my-listing-badges">
                <span class="badge approval-{listing.approval_status}">
                  {approvalLabels[listing.approval_status] || listing.approval_status}
                </span>
                <span class="badge status-{listing.status}">
                  {statusLabels[listing.status] || listing.status}
                </span>
              </div>

              <p class="my-listing-meta">
                📍 {listing.district}, {listing.city} &nbsp;•&nbsp;
                🕒 Đăng ngày {formatDate(listing.created_at)} &nbsp;•&nbsp;
                👁 {listing.views_count ?? 0} lượt xem
              </p>

              {#if listing.approval_status === 'rejected' && listing.rejection_reason}
                <p class="my-listing-rejection-reason">
                  ❌ Lý do từ chối: {listing.rejection_reason}
                </p>
              {/if}

              <div class="my-listing-actions">
                <a class="btn-action-link" href={`#/listings/${listing.id}`} target="_blank" rel="noopener">
                  Xem chi tiết ↗
                </a>
                <a class="btn-action-link" href={`#/edit-listing/${listing.id}`}>
                  ✎ Sửa
                </a>
                <button
                  class="btn-delete"
                  disabled={deletingId === listing.id}
                  on:click={() => handleDelete(listing)}
                >
                  {deletingId === listing.id ? 'Đang xoá...' : '🗑 Xoá'}
                </button>
              </div>
            </div>
          </div>
        {/each}
      </div>
    {/if}
  {/if}
</div>