<script>
  import { onMount } from 'svelte';
  import { getPredictionHistory } from '../lib/api/predictions.js';
  import { authStore } from '../lib/stores/auth.js';
  import '../styles/predictionHistory.css';
    import { ArrowLeft } from '@lucide/svelte';

  let logs = [];
  let loading = true;
  let error = '';

  const legalStatusLabels = {
    'Have certificate': 'Đã có sổ',
    'Sale contract': 'Hợp đồng mua bán',
    'Pending': 'Đang chờ sổ',
  };

  const furnitureStateLabels = {
    'Full': 'Đầy đủ nội thất',
    'Basic': 'Nội thất cơ bản',
    'None': 'Không nội thất',
  };

  const housePositionLabels = {
    Alley: 'Hẻm',
    Frontage: 'Mặt tiền',
    Unknown: 'Không rõ',
  };

  function formatPrice(price) {
    const num = Number(price);
    if (num >= 1_000_000_000) return `${(num / 1_000_000_000).toFixed(2)} tỷ`;
    if (num >= 1_000_000) return `${(num / 1_000_000).toFixed(0)} triệu`;
    return num.toLocaleString('vi-VN');
  }

  function formatDate(dateStr) {
    return new Date(dateStr).toLocaleString('vi-VN', {
      day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit',
    });
  }

  async function fetchHistory() {
    loading = true;
    error = '';
    try {
      const data = await getPredictionHistory();
      logs = Array.isArray(data) ? data : data.results ?? [];
    } catch (err) {
      error = 'Không tải được lịch sử dự đoán.';
      console.error(err);
    } finally {
      loading = false;
    }
  }

  onMount(() => {
    fetchHistory();
  });
</script>

<div class="prediction-history-page">
  <button class="btn-back" on:click={() => history.back()}><ArrowLeft size={16} /></button>

  <h1>Lịch sử dự đoán giá</h1>

  {#if !$authStore.isAuthenticated}
    <div class="ph-state error">Vui lòng đăng nhập để xem lịch sử dự đoán.</div>
  {:else if loading}
    <div class="ph-state">Đang tải...</div>
  {:else if error}
    <div class="ph-state error">{error}</div>
  {:else if logs.length === 0}
    <div class="ph-state">Bạn chưa thực hiện lần dự đoán giá nào.</div>
  {:else}
    <div class="ph-list">
      {#each logs as log (log.id)}
        <div class="ph-card">
          <div class="ph-card-header">
            <span class="ph-price">{formatPrice(log.predicted_price)}</span>
            <span class="ph-date">{formatDate(log.created_at)}</span>
          </div>

          <div class="ph-inputs-grid">
            {#if log.input_data?.area}
              <div class="ph-input-item">
                <span class="ph-input-label">Diện tích</span>
                <span class="ph-input-value">{log.input_data.area} m²</span>
              </div>
            {/if}
            {#if log.input_data?.floors}
              <div class="ph-input-item">
                <span class="ph-input-label">Số tầng</span>
                <span class="ph-input-value">{log.input_data.floors}</span>
              </div>
            {/if}
            {#if log.input_data?.bedrooms != null}
              <div class="ph-input-item">
                <span class="ph-input-label">Phòng ngủ</span>
                <span class="ph-input-value">{log.input_data.bedrooms}</span>
              </div>
            {/if}
            {#if log.input_data?.bathrooms != null}
              <div class="ph-input-item">
                <span class="ph-input-label">Phòng tắm</span>
                <span class="ph-input-value">{log.input_data.bathrooms}</span>
              </div>
            {/if}
            {#if log.input_data?.frontage}
              <div class="ph-input-item">
                <span class="ph-input-label">Mặt tiền</span>
                <span class="ph-input-value">{log.input_data.frontage} m</span>
              </div>
            {/if}
            {#if log.input_data?.access_road}
              <div class="ph-input-item">
                <span class="ph-input-label">Đường vào</span>
                <span class="ph-input-value">{log.input_data.access_road} m</span>
              </div>
            {/if}
            {#if log.input_data?.house_position}
              <div class="ph-input-item">
                <span class="ph-input-label">Vị trí nhà</span>
                <span class="ph-input-value">
                  {housePositionLabels[log.input_data.house_position] || log.input_data.house_position}
                </span>
              </div>
            {/if}
            {#if log.input_data?.street}
              <div class="ph-input-item">
                <span class="ph-input-label">Đường</span>
                <span class="ph-input-value">{log.input_data.street}</span>
              </div>
            {/if}
            {#if log.input_data?.ward}
              <div class="ph-input-item">
                <span class="ph-input-label">Phường/Xã</span>
                <span class="ph-input-value">{log.input_data.ward}</span>
              </div>
            {/if}
            {#if log.input_data?.legal_status}
              <div class="ph-input-item">
                <span class="ph-input-label">Pháp lý</span>
                <span class="ph-input-value">
                  {legalStatusLabels[log.input_data.legal_status] || log.input_data.legal_status}
                </span>
              </div>
            {/if}
            {#if log.input_data?.furniture_state}
              <div class="ph-input-item">
                <span class="ph-input-label">Nội thất</span>
                <span class="ph-input-value">
                  {furnitureStateLabels[log.input_data.furniture_state] || log.input_data.furniture_state}
                </span>
              </div>
            {/if}
            {#if log.input_data?.district}
              <div class="ph-input-item">
                <span class="ph-input-label">Khu vực</span>
                <span class="ph-input-value">{log.input_data.district}, {log.input_data.city}</span>
              </div>
            {/if}
          </div>

          <span class="ph-model-tag">Model: {log.model_version}</span>
        </div>
      {/each}
    </div>
  {/if}
</div>