<script>
  import { createEventDispatcher } from 'svelte';
  import '../../styles/searchBar.css';

  const dispatch = createEventDispatcher();

  let search = '';
  let propertyType = '';
  let district = '';
  let minPrice = '';
  let maxPrice = '';

  const districtOptions = [
    'Quận 1', 'Quận 3', 'Quận 4', 'Quận 5', 'Quận 6', 'Quận 7',
    'Quận 8', 'Quận 10', 'Quận 11', 'Quận 12',
    'Bình Thạnh', 'Phú Nhuận', 'Tân Bình', 'Tân Phú',
    'Gò Vấp', 'Bình Tân', 'Thành phố Thủ Đức',
    'Bình Chánh', 'Hóc Môn', 'Củ Chi', 'Nhà Bè', 'Cần Giờ',
  ];

  function handleSearch() {
    dispatch('filter', {
      search: search || undefined,
      property_type: propertyType || undefined,
      district: district || undefined,
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

  <select bind:value={district}>
    <option value="">Quận/Huyện</option>
    {#each districtOptions as d}
      <option value={d}>{d}</option>
    {/each}
  </select>

  <input class="filter-price-input" type="number" placeholder="Giá từ (VNĐ)" bind:value={minPrice} />
  <input class="filter-price-input" type="number" placeholder="Giá đến (VNĐ)" bind:value={maxPrice} />

  <button class="filter-search-btn" on:click={handleSearch}>Tìm kiếm</button>
</div>