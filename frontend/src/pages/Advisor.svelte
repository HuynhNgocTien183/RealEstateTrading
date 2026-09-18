<script>
  import { onMount, tick } from 'svelte';
  import { push } from 'svelte-spa-router';
  import { ArrowLeft, Send, Sparkles, RotateCcw } from '@lucide/svelte';
  import { sendAdvisorMessage, getAdvisorSession } from '../lib/api/advisor.js';
  import { authStore } from '../lib/stores/auth.js';
  import '../styles/advisor.css';

  const SESSION_KEY = 'advisor_session_id';

  const suggestions = [
    'Tôi có 5 tỷ, gợi ý nhà phố 3 phòng ngủ',
    'Nhà ở Quận 7 tầm giá nào đang bán?',
    'Mua nhà lần đầu ở TP.HCM cần chú ý gì?',
    'Khác nhau giữa AI dự đoán giá và AI tư vấn?',
  ];

  let messages = [];
  let input = '';
  let sessionId = '';
  let loading = false;
  let booting = true;
  let error = '';
  let threadEl;

  function formatPrice(price) {
    const num = Number(price);
    if (!num) return 'Thoả thuận';
    if (num >= 1_000_000_000) return `${(num / 1_000_000_000).toFixed(2)} tỷ`;
    if (num >= 1_000_000) return `${(num / 1_000_000).toFixed(0)} triệu`;
    return num.toLocaleString('vi-VN');
  }

  function persistSession(id) {
    sessionId = id;
    if (id) sessionStorage.setItem(SESSION_KEY, id);
    else sessionStorage.removeItem(SESSION_KEY);
  }

  async function scrollToBottom() {
    await tick();
    if (threadEl) threadEl.scrollTop = threadEl.scrollHeight;
  }

  async function loadSession(id) {
    if (!id) return;
    try {
      const data = await getAdvisorSession(id);
      persistSession(data.id);
      messages = (data.messages || []).map((item) => ({
        role: item.role,
        content: item.content,
        sources: item.sources || [],
      }));
    } catch (err) {
      persistSession('');
      messages = [];
    }
  }

  async function ask(text) {
    const question = (text || input).trim();
    if (!question || loading) return;

    error = '';
    input = '';
    messages = [...messages, { role: 'user', content: question, sources: [] }];
    loading = true;
    await scrollToBottom();

    try {
      const data = await sendAdvisorMessage(question, sessionId);
      persistSession(data.session_id);
      messages = [
        ...messages,
        { role: 'assistant', content: data.answer, sources: data.sources || [] },
      ];
    } catch (err) {
      error = err.response?.data?.detail || 'Không gửi được câu hỏi. Kiểm tra GOOGLE_API_KEY và thử lại.';
      messages = messages.slice(0, -1);
      input = question;
    } finally {
      loading = false;
      await scrollToBottom();
    }
  }

  function handleSubmit(event) {
    event.preventDefault();
    ask(input);
  }

  function resetChat() {
    persistSession('');
    messages = [];
    error = '';
    input = '';
  }

  onMount(async () => {
    const stored = sessionStorage.getItem(SESSION_KEY);
    if (stored) await loadSession(stored);
    booting = false;
    await scrollToBottom();
  });
</script>

<div class="advisor-page">
  <div class="advisor-top">
    <button class="btn-back" on:click={() => history.back()}><ArrowLeft size={16} /></button>
    <div class="advisor-heading">
      <h1><Sparkles size={22} /> Tư vấn nhà đất</h1>
      <p>AI đọc tin đang bán trên sàn rồi gợi ý theo ngân sách và nhu cầu của bạn.</p>
    </div>
    {#if messages.length}
      <button class="advisor-reset" on:click={resetChat}>
        <RotateCcw size={15} /> Chat mới
      </button>
    {/if}
  </div>

  <div class="advisor-shell card">
    <div class="advisor-thread" bind:this={threadEl}>
      {#if booting}
        <div class="advisor-empty">Đang tải cuộc trò chuyện...</div>
      {:else if messages.length === 0}
        <div class="advisor-empty">
          <Sparkles size={36} />
          <h2>Bạn đang tìm nhà thế nào?</h2>
          <p>
            Hỏi bằng tiếng Việt, ví dụ ngân sách, quận, số phòng ngủ.
            {#if !$authStore.isAuthenticated}
              Đăng nhập để lưu lịch sử tư vấn theo tài khoản.
            {/if}
          </p>
          <div class="advisor-suggestions">
            {#each suggestions as item}
              <button type="button" on:click={() => ask(item)}>{item}</button>
            {/each}
          </div>
        </div>
      {:else}
        {#each messages as msg, i (i)}
          <div class="advisor-bubble" class:user={msg.role === 'user'} class:assistant={msg.role === 'assistant'}>
            <div class="advisor-bubble-label">{msg.role === 'user' ? 'Bạn' : 'AI tư vấn'}</div>
            <div class="advisor-bubble-text">{msg.content}</div>
            {#if msg.sources?.length}
              <div class="advisor-sources">
                <span class="advisor-sources-label">Tin liên quan</span>
                {#each msg.sources as listing (listing.id)}
                  <button class="advisor-source-card" on:click={() => push(`/listings/${listing.id}`)}>
                    {#if listing.image}
                      <img src={listing.image} alt={listing.title} />
                    {:else}
                      <div class="advisor-source-fallback">Nhà</div>
                    {/if}
                    <div>
                      <strong>{listing.title}</strong>
                      <span>{formatPrice(listing.price)} · {listing.area} m² · {listing.district}</span>
                    </div>
                  </button>
                {/each}
              </div>
            {/if}
          </div>
        {/each}
        {#if loading}
          <div class="advisor-bubble assistant">
            <div class="advisor-bubble-label">AI tư vấn</div>
            <div class="advisor-typing">Đang tìm tin phù hợp...</div>
          </div>
        {/if}
      {/if}
    </div>

    {#if error}
      <div class="advisor-error">{error}</div>
    {/if}

    <form class="advisor-composer" on:submit={handleSubmit}>
      <textarea
        rows="2"
        placeholder="Ví dụ: Nhà phố 80m², 3 phòng ngủ, dưới 6 tỷ ở Gò Vấp..."
        bind:value={input}
        disabled={loading}
        on:keydown={(event) => {
          if (event.key === 'Enter' && !event.shiftKey) {
            event.preventDefault();
            ask(input);
          }
        }}
      ></textarea>
      <button type="submit" class="btn-primary" disabled={loading || !input.trim()}>
        <Send size={16} /> Gửi
      </button>
    </form>
  </div>
</div>
