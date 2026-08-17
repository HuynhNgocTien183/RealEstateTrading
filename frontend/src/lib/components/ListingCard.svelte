<script>
  import '../../styles/listingCard.css';

  export let listing;

  function formatPrice(price) {
    if (!price) return 'Thoả thuận';
    const num = Number(price);
    return `${num.toFixed(0)} VND`;
  }

  $: primaryImage = listing.images?.find((img) => img.is_primary)?.image
    || listing.images?.[0]?.image
    || null;
</script>

<a href={`#/listings/${listing.id}`} class="card-link">
  <div class="card">
    <div class="card-image-wrapper">
      {#if primaryImage}
        <img src={primaryImage} alt={listing.title} />
      {:else}
        <div class="card-no-image">Chưa có ảnh</div>
      {/if}
    </div>

    <div class="card-body">
      <h3>{listing.title}</h3>
      <p class="card-price">{formatPrice(listing.price)}</p>
      <p class="card-location">{listing.district}, {listing.city}</p>

      <div class="card-meta">
        <span>{listing.area} m²</span>
        <span>•</span>
        <span>{listing.bedrooms} PN</span>
        <span>•</span>
        <span>{listing.bathrooms} WC</span>
        {#if listing.favorites_count > 0}
          <span>•</span>
          <span class="card-favorites-count">❤ {listing.favorites_count}</span>
        {/if}
      </div>
    </div>
  </div>
</a>