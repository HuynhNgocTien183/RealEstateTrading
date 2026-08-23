<script>
  import { onMount } from 'svelte';
  import { getListings } from '../lib/api/listings.js';
  import ListingCard from '../lib/components/ListingCard.svelte';
  import '../styles/sellerListings.css';
  import { ArrowLeft } from '@lucide/svelte';

  export let params = {};

  let listings = [];
  let loading = true;
  let error = '';
  let sellerName = '';

  async function fetchSellerListings() {
    loading = true;
    error = '';
    try {
      const data = await getListings({ seller: params.id });
      listings = Array.isArray(data) ? data : data.results ?? [];
      if (listings.length > 0) {
        sellerName = listings[0].seller_full_name || listings[0].seller_username;
      }
    } catch (err) {
      error = 'Không tải được danh sách tin của người bán này.';
      console.error(err);
    } finally {
      loading = false;
    }
  }

  $: if (params.id) {
    fetchSellerListings();
  }
</script>

<div class="seller-listings-page">
  <button class="btn-back" on:click={() => history.back()}><ArrowLeft size = {16} /></button>

  {#if loading}
    <div class="seller-listings-state">Đang tải...</div>
  {:else if error}
    <div class="seller-listings-state error">{error}</div>
  {:else}
    <h1>
      {#if sellerName}
        Tất cả tin đăng của <span class="seller-name-highlight">{sellerName}</span>
      {:else}
        Tin đăng của người bán
      {/if}
      <span class="seller-listings-count">({listings.length})</span>
    </h1>

    {#if listings.length === 0}
      <div class="seller-listings-state">Người bán này chưa có tin đăng nào được duyệt.</div>
    {:else}
      <div class="seller-listings-grid">
        {#each listings as listing (listing.id)}
          <ListingCard {listing} />
        {/each}
      </div>
    {/if}
  {/if}
</div>