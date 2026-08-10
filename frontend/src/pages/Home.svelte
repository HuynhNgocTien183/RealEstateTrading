<script>
  import { onMount } from 'svelte';
  import { getListings } from '../lib/api/listings';
  import ListingCard from '../lib/components/ListingCard.svelte';
  import SearchBar from '../lib/components/SearchBar.svelte';
  import '../styles/home.css';
  import PredictionForm from '../lib/components/PredictionForm.svelte';
  
  
  let listings = [];
  let loading = true;
  let error = '';
  let currentPage = 1;
  let totalCount = 0;
  let pageSize = 12;
  let currentFilters = {};

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
    fetchListings();
  });
</script>

<div class="home">
  <h1>Tìm kiếm Bất động sản</h1>

  <SearchBar on:filter={handleFilter} />
  <PredictionForm />

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