<script>
  import { predictPrice } from '../api/predictions.js';
  import '../../styles/predictionForm.css';

  export let listing = null;

  let area = listing?.area ?? '';
  let frontage = listing?.frontage ?? '';
  let accessRoad = listing?.access_road ?? '';
  let floors = listing?.floors || '';
  let bedrooms = listing?.bedrooms || '';
  let bathrooms = listing?.bathrooms || '';
  let legalStatus = listing?.legal_status ?? 'Have certificate';
  let furnitureState = listing?.furniture_state ?? 'Full';
  let city = listing?.city ?? 'Hồ Chí Minh';
  let district = listing?.district ?? '';

  let result = null;
  let error = '';
  let loading = false;

  const districtOptions = [
      'Quận 1',
      'Quận 2',
      'Quận 3',
      'Quận 4',
      'Quận 5',
      'Quận 6',
      'Quận 7',
      'Quận 8',
      'Quận 9',
      'Quận 10',
      'Quận 11',
      'Quận 12',
      'Bình Thạnh',
      'Phú Nhuận',
      'Tân Bình',
      'Tân Phú',
      'Gò Vấp',
      'Bình Tân',
      'Thủ Đức',
      'Nhà Bè',
      'Hóc Môn',
      'Củ Chi',
      'Bình Chánh',
      'Cần Giờ',
  ];

  function toOptionalNumber(value) {
    if (value === '' || value === null || value === undefined) return undefined;
    const num = Number(value);
    if (!Number.isFinite(num) || num === 0) return undefined;
    return num;
  }

  function formatPrice(price) {
    const num = Number(price);
    if (num >= 1_000_000_000) return `${(num / 1_000_000_000).toFixed(2)} tỷ VNĐ`;
    if (num >= 1_000_000) return `${(num / 1_000_000).toFixed(0)} triệu VNĐ`;
    return `${num.toLocaleString('vi-VN')} VNĐ`;
  }

  async function handlePredict() {
    error = '';
    result = null;
    loading = true;
    try {
      const data = await predictPrice({
        area: Number(area),
        frontage: toOptionalNumber(frontage),
        access_road: toOptionalNumber(accessRoad),
        floors: toOptionalNumber(floors),
        bedrooms: toOptionalNumber(bedrooms),
        bathrooms: toOptionalNumber(bathrooms),
        legal_status: legalStatus,
        furniture_state: furnitureState,
        city,
        district,
        address: listing?.address ?? '',
        property_type: listing?.property_type ?? 'house',
        listing_id: listing?.id ?? undefined,
      });
      result = data;
    } catch (err) {
      error = err.response?.data?.detail || 'Không thể dự đoán giá lúc này. Vui lòng thử lại.';
      console.error(err);
    } finally {
      loading = false;
    }
  }
</script>

<div class="prediction-form-card">
  <h3>🤖 Dự đoán giá nhà bằng AI</h3>

  <form on:submit|preventDefault={handlePredict}>
    <div class="prediction-form-row">
      <label>
        Diện tích (m²)
        <input type="number" bind:value={area} min="1" step="0.1" required />
      </label>
      <label>
        Số tầng
        <input type="number" bind:value={floors} min="1" placeholder="Để trống nếu không rõ" />
      </label>
    </div>

    <div class="prediction-form-row">
      <label>
        Mặt tiền (m)
        <input type="number" bind:value={frontage} min="0" step="0.1" />
      </label>
      <label>
        Đường vào (m)
        <input type="number" bind:value={accessRoad} min="0" step="0.1" />
      </label>
    </div>

    <div class="prediction-form-row">
      <label>
        Phòng ngủ
        <input type="number" bind:value={bedrooms} min="1" placeholder="Để trống nếu không rõ" />
      </label>
      <label>
        Phòng tắm
        <input type="number" bind:value={bathrooms} min="1" placeholder="Để trống nếu không rõ" />
      </label>
    </div>

    <label>
      Tình trạng pháp lý
      <select bind:value={legalStatus}>
        <option value="Have certificate">Đã có sổ</option>
        <option value="Sale contract">Hợp đồng mua bán</option>
        <option value="Pending">Đang chờ sổ</option>
      </select>
    </label>

    <label>
      Nội thất
      <select bind:value={furnitureState}>
        <option value="Full">Đầy đủ nội thất</option>
        <option value="Basic">Nội thất cơ bản</option>
        <option value="None">Không nội thất</option>
      </select>
    </label>

    <div class="prediction-form-row">
      <label>
        Thành phố
        <input type="text" value={city} disabled />
      </label>
      <label>
        Quận/Huyện
        <select bind:value={district} required>
          <option value="">-- Chọn Quận/Huyện --</option>
          {#each districtOptions as d}
            <option value={d}>{d}</option>
          {/each}
        </select>
      </label>
    </div>

    <button type="submit" disabled={loading}>
      {loading ? 'Đang tính toán...' : 'Dự đoán giá ngay'}
    </button>
  </form>

  {#if error}
    <p class="prediction-form-error">{error}</p>
  {/if}

  {#if result}
    <div class="prediction-form-result">
      <span class="result-label">Giá dự đoán</span>
      <span class="result-label">(Có thể chênh lệch nhiều so với giá thực tế)</span>
      <span class="result-price">{formatPrice(result.predicted_price)}</span>
      <span class="result-model">Model: {result.model_version}</span>
    </div>
  {/if}
</div>
