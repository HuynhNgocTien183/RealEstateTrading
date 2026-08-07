<script>
  import { createEventDispatcher } from 'svelte';
  import '../../styles/searchBar.css';

  const dispatch = createEventDispatcher();

  let search = '';
  let propertyType = '';
  let city = '';
  let minPrice = '';
  let maxPrice = '';

  function handleSearch() {
    dispatch('filter', {
      search: search || undefined,
      property_type: propertyType || undefined,
      city: city || undefined,
      price_min: minPrice || undefined,
      price_max: maxPrice || undefined,
    });
  }
</script>

<div class="filter-bar">
  <input
    class="filter-search-input"
    type="text"
    placeholder="Tìm theo tên, khu vực..."
    bind:value={search}
    on:keydown={(e) => e.key === 'Enter' && handleSearch()}
  />

  <select bind:value={propertyType}>
    <option value="">Loại hình</option>
    <option value="house">Nhà phố</option>
    <option value="apartment">Chung cư</option>
    <option value="land">Đất nền</option>
    <option value="villa">Biệt thự</option>
  </select>

  <input type="text" placeholder="Thành phố" bind:value={city} />

  <input class="filter-price-input" type="number" placeholder="Giá từ" bind:value={minPrice} />
  <input class="filter-price-input" type="number" placeholder="Giá đến" bind:value={maxPrice} />

  <button class="filter-search-btn" on:click={handleSearch}>Tìm kiếm</button>
</div>