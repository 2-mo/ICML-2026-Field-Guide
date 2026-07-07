const souvenirs = window.SEOUL_SOUVENIRS || [];
const routePlans = window.SEOUL_ROUTE_PLANS || [];

const state = {
  category: "全部",
  price: "全部",
  carry: "全部",
  query: "",
};

const els = {
  statCount: document.querySelector("#stat-count"),
  statCategoryCount: document.querySelector("#stat-category-count"),
  statAreaCount: document.querySelector("#stat-area-count"),
  search: document.querySelector("#search-input"),
  categoryFilters: document.querySelector("#category-filters"),
  priceFilters: document.querySelector("#price-filters"),
  carryFilters: document.querySelector("#carry-filters"),
  routeGrid: document.querySelector("#route-grid"),
  cardGrid: document.querySelector("#card-grid"),
  resultCount: document.querySelector("#result-count"),
  modal: document.querySelector("#detail-modal"),
  modalContent: document.querySelector("#modal-content"),
};

const filters = {
  categories: ["全部", ...Array.from(new Set(souvenirs.map((item) => item.category_group)))],
  prices: [
    "全部",
    ...["小预算", "中等预算", "高预算", "待确认"].filter((bucket) =>
      souvenirs.some((item) => priceBucket(item) === bucket)
    ),
  ],
  carry: [
    "全部",
    ...["适合带回国", "需要规划", "慎买"].filter((bucket) =>
      souvenirs.some((item) => carryBucket(item) === bucket)
    ),
  ],
};

function normalize(text) {
  return String(text || "").toLowerCase();
}

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function makeSearchText(item) {
  return normalize(
    [
      item.product_name_cn,
      item.product_name_en,
      item.product_name_ko,
      item.brand_or_store,
      item.shop_name,
      item.area,
      item.category,
      item.nearest_station,
      item.address_en,
      item.address_ko,
      ...(item.best_for || []),
      ...(item.tags || []),
    ].join(" ")
  );
}

function priceBucket(item) {
  return item.price_bucket || "待确认";
}

function carryBucket(item) {
  if (item.carry_score >= 4 && item.is_suitable_to_bring_home === "yes") return "适合带回国";
  if (item.is_suitable_to_bring_home === "conditional" || item.carry_score === 3) return "需要规划";
  return "慎买";
}

function itemMatches(item) {
  const query = normalize(state.query.trim());
  return (
    (state.category === "全部" || item.category_group === state.category) &&
    (state.price === "全部" || priceBucket(item) === state.price) &&
    (state.carry === "全部" || carryBucket(item) === state.carry) &&
    (!query || makeSearchText(item).includes(query))
  );
}

function chip(label, group, activeValue) {
  const button = document.createElement("button");
  button.type = "button";
  button.className = `chip${label === activeValue ? " is-active" : ""}`;
  button.textContent = label;
  button.dataset.group = group;
  button.dataset.value = label;
  button.setAttribute("aria-pressed", label === activeValue ? "true" : "false");
  return button;
}

function renderFilters() {
  els.categoryFilters.replaceChildren(...filters.categories.map((label) => chip(label, "category", state.category)));
  els.priceFilters.replaceChildren(...filters.prices.map((label) => chip(label, "price", state.price)));
  els.carryFilters.replaceChildren(...filters.carry.map((label) => chip(label, "carry", state.carry)));
}

function renderThumb(item, large = false) {
  if (item.image_url) {
    const badge = item.image_type === "real" ? "真实照片" : "AI生成示意图 / Not a real photo";
    return `
      <div class="thumb${large ? " modal-thumb" : ""}">
        <img src="${escapeHtml(item.image_url)}" alt="${escapeHtml(item.image_alt || item.product_name_cn)}" loading="lazy" />
        <span class="image-badge">${escapeHtml(badge)}</span>
      </div>
    `;
  }

  const badge =
    item.image_type === "ai_generated"
      ? "AI生成示意图 / Not a real photo"
      : "示意占位 / Not a real photo";
  return `
    <div class="thumb${large ? " modal-thumb" : ""}" style="--visual-color: ${escapeHtml(item.visual_color || "#cfe3dc")}">
      <div class="visual-placeholder" aria-hidden="true">
        <div class="visual-object"></div>
        <span class="visual-label">${escapeHtml(item.visual_label || item.category_group)}</span>
      </div>
      <span class="image-badge placeholder">${escapeHtml(badge)}</span>
    </div>
  `;
}

function tagList(items, limit = 4) {
  return (items || []).slice(0, limit).map((tag) => `<span class="tag">${escapeHtml(tag)}</span>`).join("");
}

function scorePills(item) {
  return `
    <span class="score-pill">携带 ${item.carry_score}/5</span>
    <span class="score-pill">送礼 ${item.gift_score}/5</span>
    <span class="score-pill">特色 ${item.uniqueness_score}/5</span>
  `;
}

function renderCard(item) {
  const article = document.createElement("article");
  article.className = "gift-card";
  article.innerHTML = `
    ${renderThumb(item)}
    <div class="card-body">
      <div class="card-topline">
        <span class="category">${escapeHtml(item.category_group)}</span>
        <span class="confidence">可信度 ${escapeHtml(item.confidence_level)}</span>
      </div>
      <h3>${escapeHtml(item.product_name_cn)}</h3>
      <p class="ko-name">${escapeHtml(item.product_name_ko)} · ${escapeHtml(item.product_name_en)}</p>
      <p class="why">${escapeHtml(item.why_buy)}</p>
      <div class="facts">
        <div class="fact"><b>购买</b><span>${escapeHtml(item.shop_name)}</span></div>
        <div class="fact"><b>地铁</b><span>${escapeHtml(item.nearest_station)}</span></div>
        <div class="fact"><b>价格</b><span>${escapeHtml(item.price_range_krw)}</span></div>
      </div>
      <div class="tag-row">${tagList([item.area, carryBucket(item), ...(item.tags || [])], 5)}</div>
      <div class="score-row">${scorePills(item)}</div>
      <div class="card-actions">
        <button class="primary-button" type="button" data-detail="${escapeHtml(item.id)}">看详情</button>
        <button class="secondary-button" type="button" data-copy="${escapeHtml(item.address_ko || item.address_en)}">复制地址</button>
      </div>
    </div>
  `;
  return article;
}

function renderCards() {
  const filtered = souvenirs.filter(itemMatches);
  els.resultCount.textContent = `${filtered.length} / ${souvenirs.length} 个条目`;
  if (!filtered.length) {
    els.cardGrid.innerHTML = `<div class="empty-state">没有匹配结果。换个关键词或清掉筛选试试。</div>`;
    return;
  }
  els.cardGrid.replaceChildren(...filtered.map(renderCard));
}

function renderRoutes() {
  els.routeGrid.replaceChildren(
    ...routePlans.map((route) => {
      const card = document.createElement("article");
      card.className = "route-card";
      const routeText = `${route.title}: ${route.stops.join(" -> ")}`;
      const routeQuery = encodeURIComponent(route.search_keyword || route.stops.join(" "));
      card.innerHTML = `
        <h3>${escapeHtml(route.title)}</h3>
        <p>${escapeHtml(route.summary)}</p>
        <ol>${route.stops.map((stop) => `<li>${escapeHtml(stop)}</li>`).join("")}</ol>
        <div class="route-meta">
          <span>${escapeHtml(route.time)}</span>
          <span>${escapeHtml(route.best_for)}</span>
        </div>
        <div class="route-actions">
          <button class="text-button" type="button" data-copy="${escapeHtml(routeText)}">复制路线</button>
          <a class="text-button" href="https://map.naver.com/p/search/${routeQuery}" target="_blank" rel="noreferrer">Naver 搜索</a>
          <a class="text-button" href="https://www.google.com/maps/search/?api=1&query=${routeQuery}" target="_blank" rel="noreferrer">Google 搜索</a>
        </div>
      `;
      return card;
    })
  );
}

async function copyText(text) {
  try {
    await navigator.clipboard.writeText(text);
    return true;
  } catch {
    const textarea = document.createElement("textarea");
    textarea.value = text;
    textarea.style.position = "fixed";
    textarea.style.left = "-9999px";
    document.body.append(textarea);
    textarea.focus();
    textarea.select();
    const ok = document.execCommand("copy");
    textarea.remove();
    return ok;
  }
}

function mapLinks(item) {
  const keyword = encodeURIComponent(item.map_search_keyword || `${item.shop_name} ${item.address_ko || item.address_en}`);
  return `
    <a class="text-button" href="https://map.naver.com/p/search/${keyword}" target="_blank" rel="noreferrer">Naver Map</a>
    <a class="text-button" href="https://map.kakao.com/?q=${keyword}" target="_blank" rel="noreferrer">Kakao Map</a>
    <a class="text-button" href="https://www.google.com/maps/search/?api=1&query=${keyword}" target="_blank" rel="noreferrer">Google Maps</a>
  `;
}

function sourceList(item) {
  return (item.source_urls || [])
    .map((url, index) => `<li><a href="${escapeHtml(url)}" target="_blank" rel="noreferrer">来源 ${index + 1}</a></li>`)
    .join("");
}

function openDetail(item) {
  els.modalContent.innerHTML = `
    <div class="modal-content-inner">
      <div class="modal-visual">${renderThumb(item, true)}</div>
      <section class="modal-main">
        <p class="eyebrow">${escapeHtml(item.category_group)} · ${escapeHtml(item.area)}</p>
        <h2>${escapeHtml(item.product_name_cn)}</h2>
        <p class="ko-name">${escapeHtml(item.product_name_ko)} · ${escapeHtml(item.product_name_en)}</p>
        <div class="modal-meta">
          ${tagList([carryBucket(item), item.buying_difficulty, ...(item.best_for || [])], 8)}
        </div>
        <p>${escapeHtml(item.why_buy)}</p>
        <div class="detail-grid">
          <div class="detail-line"><b>适合送给</b><span>${escapeHtml((item.best_for || []).join("、"))}</span></div>
          <div class="detail-line"><b>预估价格</b><span>${escapeHtml(item.price_range_krw)}</span></div>
          <div class="detail-line"><b>购买地点</b><span>${escapeHtml(item.shop_name)}</span></div>
          <div class="detail-line"><b>英文地址</b><span>${escapeHtml(item.address_en)}</span></div>
          <div class="detail-line"><b>韩文地址</b><span>${escapeHtml(item.address_ko)}</span></div>
          <div class="detail-line"><b>最近地铁</b><span>${escapeHtml(item.nearest_station)}</span></div>
          <div class="detail-line"><b>营业时间</b><span>${escapeHtml(item.opening_hours)}</span></div>
          <div class="detail-line"><b>购买提醒</b><span>${escapeHtml(item.caution_note)}</span></div>
          <div class="detail-line"><b>带回国</b><span>${escapeHtml(item.bring_home_note)}</span></div>
          <div class="detail-line"><b>图片</b><span>${escapeHtml(item.image_credit)}</span></div>
        </div>
        <div class="score-row">${scorePills(item)}</div>
        <div class="button-row">
          <button class="text-button" type="button" data-copy="${escapeHtml(item.address_ko || item.address_en)}">复制韩文地址</button>
          <button class="text-button" type="button" data-copy="${escapeHtml(item.map_search_keyword)}">复制地图关键词</button>
          ${mapLinks(item)}
        </div>
        <h3>信息来源</h3>
        <ul class="source-list">${sourceList(item)}</ul>
      </section>
    </div>
  `;
  if (typeof els.modal.showModal === "function") {
    els.modal.showModal();
  } else {
    els.modal.setAttribute("open", "");
  }
}

function bindEvents() {
  els.search.addEventListener("input", (event) => {
    state.query = event.target.value;
    renderCards();
  });

  document.addEventListener("click", async (event) => {
    const chipButton = event.target.closest(".chip");
    if (chipButton) {
      state[chipButton.dataset.group] = chipButton.dataset.value;
      renderFilters();
      renderCards();
      return;
    }

    const detailButton = event.target.closest("[data-detail]");
    if (detailButton) {
      const item = souvenirs.find((candidate) => candidate.id === detailButton.dataset.detail);
      if (item) openDetail(item);
      return;
    }

    const copyButton = event.target.closest("[data-copy]");
    if (copyButton) {
      const originalText = copyButton.textContent;
      const ok = await copyText(copyButton.dataset.copy);
      copyButton.textContent = ok ? "已复制" : "复制失败";
      window.setTimeout(() => {
        copyButton.textContent = originalText;
      }, 1200);
      return;
    }

    if (event.target.closest("[data-close-modal]")) {
      els.modal.close();
    }
  });

  els.modal.addEventListener("click", (event) => {
    if (event.target === els.modal) els.modal.close();
  });
}

function init() {
  els.statCount.textContent = souvenirs.length;
  els.statCategoryCount.textContent = new Set(souvenirs.map((item) => item.category_group)).size;
  els.statAreaCount.textContent = new Set(souvenirs.map((item) => item.area)).size;
  renderFilters();
  renderRoutes();
  renderCards();
  bindEvents();
}

init();
