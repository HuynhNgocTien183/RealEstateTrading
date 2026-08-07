<script>
  import { Link } from 'svelte-routing';
  import '../../styles/listingCart.css';

  export let listing;

  function formatPrice(price) {
    if (!price) return 'Thoả thuận';
    const num = Number(price);
    if (num >= 1000) {
      return `${(num / 1000).toFixed(1)} tỷ`;
    }
    return `${num.toFixed(0)} triệu`;
  }

  $: primaryImage = listing.images?.find((img) => img.is_primary)?.image
    || listing.images?.[0]?.image
    || null;
</script>

<Link to={`/listings/${listing.id}`} class="card-link">
  <div class="card">
    <div class="card-image-wrapper">
      {#if primaryImage}
        <img src={primaryImage} alt={listing.title} />
      {:else}
        <div class="card-no-image">Chưa có ảnh</div>
      {/if}
      <span class="card-badge">{listing.property_type}</span>
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
      </div>
    </div>
  </div>
</Link>