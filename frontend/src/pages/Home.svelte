<script>
  import { onMount } from 'svelte';
  import { getListings } from '../lib/api/listings';
  import ListingCard from '../lib/components/ListingCard.svelte';
  import SearchBar from '../lib/components/SearchBar.svelte';
  import '../styles/home.css';
  import PredictionForm from '../lib/components/PredictionForm.svelte';
  import { homeState } from '../lib/stores/homeState.js';
  import { get } from 'svelte/store';
  
  let listings = [];
  let loading = true;
  let error = '';
  let totalCount = 0;
  let pageSize = 12; 
  let currentPage = get(homeState).currentPage;
  let currentFilters = get(homeState).filters;
  let showPredictionForm = false;



  async function fetchListings(filters = {}, page = 1) {
    loading = true;
    error = '';
    try {
      const params = { ...filters, page };
      const data = await getListings(params);

      if (Array.isArray(data)) {
        listings = data;
        totalCount = data.length;
      } else {
        listings = data.results ?? [];
        totalCount = data.count ?? listings.length;
      }

      homeState.set({ currentPage: page, filters });
    } catch (err) {
      error = 'Không tải được danh sách bất động sản. Vui lòng thử lại.';
      console.error(err);
    } finally {
      loading = false;
    }
  }

  function handleFilter(event) {
    currentFilters = event.detail;
    currentPage = 1;
    fetchListings(currentFilters, currentPage);
  }

  function goToPage(page) {
    currentPage = page;
    fetchListings(currentFilters, currentPage);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }

  $: totalPages = Math.ceil(totalCount / pageSize) || 1;

  onMount(() => {
    fetchListings(currentFilters, currentPage);
  });
</script>

<div class="home">
  <h1>Tìm kiếm Bất động sản</h1>

  <SearchBar initialFilters={currentFilters} on:filter={handleFilter} />
  <div class="home-prediction-toggle-wrapper">
    <button
      class="home-prediction-toggle-btn"
      on:click={() => (showPredictionForm = !showPredictionForm)}
    >
      <span>🤖 Dùng AI dự đoán giá nhà</span>
      <span class="toggle-arrow" class:open={showPredictionForm}>▼</span>
    </button>

    {#if showPredictionForm}
      <div class="home-prediction-form-panel">
        <PredictionForm />
      </div>
    {/if}
  </div>

  {#if loading}
    <div class="home-state-message">Đang tải danh sách...</div>
  {:else if error}
    <div class="home-state-message error">{error}</div>
  {:else if listings.length === 0}
    <div class="home-state-message">Không tìm thấy bất động sản nào phù hợp.</div>
  {:else}
    <div class="home-grid">
      {#each listings as listing (listing.id)}
        <ListingCard {listing} />
      {/each}
    </div>

    {#if totalPages > 1}
      <div class="home-pagination">
        <button disabled={currentPage === 1} on:click={() => goToPage(currentPage - 1)}>
          ← Trước
        </button>
        <span>Trang {currentPage} / {totalPages}</span>
        <button disabled={currentPage === totalPages} on:click={() => goToPage(currentPage + 1)}>
          Sau →
        </button>
      </div>
    {/if}
  {/if}
</div>