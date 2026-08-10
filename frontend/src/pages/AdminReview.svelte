<script>
  import { onMount } from 'svelte';
  import {
    getPendingListings,
    getRejectedListings,
    approveListing,
    rejectListing,
  } from '../lib/api/listings.js';
  import { authStore } from '../lib/stores/auth.js';
  import '../styles/adminReview.css';

  let activeTab = 'pending'; // 'pending' | 'rejected'

  let pendingListings = [];
  let rejectedListings = [];
  let loading = true;
  let error = '';
  let actionLoadingId = null;

  let showRejectModal = false;
  let rejectingListing = null;
  let rejectReason = '';
  let rejectError = '';

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
      day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit',
    });
  }

  async function fetchData() {
    loading = true;
    error = '';
    try {
      const [pendingData, rejectedData] = await Promise.all([
        getPendingListings(),
        getRejectedListings(),
      ]);
      pendingListings = Array.isArray(pendingData) ? pendingData : pendingData.results ?? [];
      rejectedListings = Array.isArray(rejectedData) ? rejectedData : rejectedData.results ?? [];
    } catch (err) {
      error = 'Không tải được danh sách tin.';
      console.error(err);
    } finally {
      loading = false;
    }
  }

  async function handleApprove(listing, fromTab) {
    actionLoadingId = listing.id;
    try {
      await approveListing(listing.id);
      if (fromTab === 'pending') {
        pendingListings = pendingListings.filter((l) => l.id !== listing.id);
      } else {
        rejectedListings = rejectedListings.filter((l) => l.id !== listing.id);
      }
    } catch (err) {
      alert('Duyệt tin thất bại. Vui lòng thử lại.');
      console.error(err);
    } finally {
      actionLoadingId = null;
    }
  }

  function openRejectModal(listing) {
    rejectingListing = listing;
    rejectReason = '';
    rejectError = '';
    showRejectModal = true;
  }

  function closeRejectModal() {
    showRejectModal = false;
    rejectingListing = null;
    rejectReason = '';
    rejectError = '';
  }

  async function confirmReject() {
    if (!rejectReason.trim()) {
      rejectError = 'Vui lòng nhập lý do từ chối.';
      return;
    }
    actionLoadingId = rejectingListing.id;
    try {
      await rejectListing(rejectingListing.id, rejectReason.trim());
      pendingListings = pendingListings.filter((l) => l.id !== rejectingListing.id);
      rejectedListings = [
        { ...rejectingListing, approval_status: 'rejected', rejection_reason: rejectReason.trim() },
        ...rejectedListings,
      ];
      closeRejectModal();
    } catch (err) {
      rejectError = 'Từ chối tin thất bại. Vui lòng thử lại.';
      console.error(err);
    } finally {
      actionLoadingId = null;
    }
  }

  onMount(() => {
    fetchData();
  });

  $: currentList = activeTab === 'pending' ? pendingListings : rejectedListings;
</script>

<div class="admin-review">
  {#if !$authStore.isAuthenticated}
    <div class="admin-review-state error">Vui lòng đăng nhập để truy cập trang này.</div>
  {:else if $authStore.user?.role !== 'admin'}
    <div class="admin-review-state error">Bạn không có quyền truy cập trang này.</div>
  {:else}
    <h1>Duyệt tin đăng</h1>

    <div class="admin-review-tabs">
      <button
        class="tab-btn"
        class:active={activeTab === 'pending'}
        on:click={() => (activeTab = 'pending')}
      >
        Đang chờ duyệt ({pendingListings.length})
      </button>
      <button
        class="tab-btn"
        class:active={activeTab === 'rejected'}
        on:click={() => (activeTab = 'rejected')}
      >
        Đã từ chối ({rejectedListings.length})
      </button>
    </div>

    {#if loading}
      <div class="admin-review-state">Đang tải danh sách...</div>
    {:else if error}
      <div class="admin-review-state error">{error}</div>
    {:else if currentList.length === 0}
      <div class="admin-review-state">
        {activeTab === 'pending' ? '🎉 Không có tin nào đang chờ duyệt.' : 'Không có tin nào bị từ chối.'}
      </div>
    {:else}
      <div class="admin-review-list">
        {#each currentList as listing (listing.id)}
          <div class="admin-review-card">
            <div class="admin-review-image">
              {#if listing.images && listing.images.length > 0}
                <img src={listing.images[0].image} alt={listing.title} />
              {:else}
                <div class="admin-review-no-image">Chưa có ảnh</div>
              {/if}
            </div>

            <div class="admin-review-info">
              <div class="admin-review-info-header">
                <h3>{listing.title}</h3>
                <span class="admin-review-price">{formatPrice(listing.price)}</span>
              </div>

              <p class="admin-review-meta">
                👤 {listing.seller_username} &nbsp;•&nbsp;
                📍 {listing.district}, {listing.city} &nbsp;•&nbsp;
                🕒 {formatDate(listing.created_at)}
              </p>

              <p class="admin-review-specs">
                {listing.area} m² • {listing.bedrooms} PN • {listing.bathrooms} WC •
                {listing.property_type}
              </p>

              {#if activeTab === 'rejected' && listing.rejection_reason}
                <p class="admin-review-rejection-reason">
                  ❌ Lý do từ chối: {listing.rejection_reason}
                </p>
              {/if}

              {#if listing.description}
                <p class="admin-review-description">{listing.description}</p>
              {/if}

              <div class="admin-review-actions">
                <a
                  class="btn-view-detail"
                  href={`#/listings/${listing.id}`}
                  target="_blank"
                  rel="noopener"
                >
                  Xem chi tiết ↗
                </a>

                {#if activeTab === 'pending'}
                  <button
                    class="btn-approve"
                    disabled={actionLoadingId === listing.id}
                    on:click={() => handleApprove(listing, 'pending')}
                  >
                    {actionLoadingId === listing.id ? 'Đang xử lý...' : '✓ Duyệt'}
                  </button>
                  <button
                    class="btn-reject"
                    disabled={actionLoadingId === listing.id}
                    on:click={() => openRejectModal(listing)}
                  >
                    ✕ Từ chối
                  </button>
                {:else}
                  <button
                    class="btn-approve"
                    disabled={actionLoadingId === listing.id}
                    on:click={() => handleApprove(listing, 'rejected')}
                  >
                    {actionLoadingId === listing.id ? 'Đang xử lý...' : '↺ Duyệt lại'}
                  </button>
                {/if}
              </div>
            </div>
          </div>
        {/each}
      </div>
    {/if}
  {/if}
</div>

{#if showRejectModal}
  <div
    class="modal-overlay"
    role="button"
    tabindex="0"
    on:click={closeRejectModal}
    on:keydown={(e) => e.key === 'Escape' && closeRejectModal()}
  >
    <div
      class="modal-box"
      role="dialog"
      aria-modal="true"
      tabindex="0"
      on:click|stopPropagation
      on:keydown={(e) => e.key === 'Escape' && closeRejectModal()}
    >
      <h3>Từ chối tin: {rejectingListing?.title}</h3>
      <textarea
        bind:value={rejectReason}
        placeholder="Nhập lý do từ chối (VD: ảnh không rõ ràng, thiếu thông tin pháp lý...)"
        rows="4"
      ></textarea>
      {#if rejectError}
        <p class="modal-error">{rejectError}</p>
      {/if}
      <div class="modal-actions">
        <button class="btn-modal-cancel" on:click={closeRejectModal}>Huỷ</button>
        <button
          class="btn-modal-confirm"
          on:click={confirmReject}
          disabled={actionLoadingId === rejectingListing?.id}
        >
          {actionLoadingId === rejectingListing?.id ? 'Đang gửi...' : 'Xác nhận từ chối'}
        </button>
      </div>
    </div>
  </div>
{/if}