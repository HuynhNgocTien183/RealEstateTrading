<script>
  import { onMount } from 'svelte';
  import { getFavorites, removeFavorite } from '../lib/api/interactions';
  import ListingCard from '../lib/components/ListingCard.svelte';
  import '../styles/savedListing.css';

  let favorites = [];
  let loading = true;
  let error = '';

  async function loadFavorites() {
    loading = true;
    error = '';
    try {
      const data = await getFavorites();
      favorites = Array.isArray(data) ? data : data.results ?? [];
    } catch (err) {
      error = 'Không tải được danh sách tin đã thích.';
      console.error(err);
    } finally {
      loading = false;
    }
  }

  async function handleRemove(favoriteId) {
    try {
      await removeFavorite(favoriteId);
      favorites = favorites.filter((f) => f.id !== favoriteId);
    } catch (err) {
      console.error(err);
    }
  }

  onMount(() => {
    loadFavorites();
  });
</script>

<div class="saved-listings-page">
  <h1>Tin đã thích</h1>

  {#if loading}
    <div class="saved-listings-state">Đang tải...</div>
  {:else if error}
    <div class="saved-listings-state error">{error}</div>
  {:else if favorites.length === 0}
    <div class="saved-listings-state">Bạn chưa lưu tin nào.</div>
  {:else}
    <div class="saved-listings-grid">
      {#each favorites as fav (fav.id)}
        <div class="saved-listing-item">
          <ListingCard listing={fav.listing_detail} />
          <button class="btn-remove-favorite" on:click={() => handleRemove(fav.id)}>
            ✕ Bỏ thích
          </button>
        </div>
      {/each}
    </div>
  {/if}
</div>