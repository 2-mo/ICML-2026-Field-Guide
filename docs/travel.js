const $ = (selector, root = document) => root.querySelector(selector);
const $$ = (selector, root = document) => Array.from(root.querySelectorAll(selector));

const GROUP_LABELS = {
  airport: "Airport",
  side_event_zone: "Evening zone",
  venue_access: "Venue access",
};

const CLASSIC_GROUPS = ["palace_bukchon", "namsan_myeongdong", "hanriver_yeouido", "ddp_city_walk", "jamsil_skyline"];
const SHORT_STOP_NAMES = {
  "Starfield Library": "星空图书馆",
  "Bongeunsa Temple": "奉恩寺",
  "Banpo Hangang Park": "盘浦汉江",
  "National Museum of Korea": "中央博物馆",
  "Itaewon / Hannam-dong": "梨泰院",
  "N Seoul Tower": "南山塔",
  Myeongdong: "明洞",
  "Namsan Cable Car": "南山缆车",
  "Gyeongbokgung Palace": "景福宫",
  "Bukchon Hanok Village": "北村",
  Insadong: "仁寺洞",
  "Seoul Forest": "首尔林",
  "Seongsu-dong": "圣水洞",
  "Lotte World Tower / Seoul Sky": "乐天塔",
  Hongdae: "弘大",
  "Yeonnam-dong / Gyeongui Line Forest Park": "延南洞",
  "Mangwon Market": "望远市场",
  "Changdeokgung Palace": "昌德宫",
  "Dongdaemun Design Plaza": "DDP",
  "Gwangjang Market": "广藏市场",
  "The Hyundai Seoul": "现代百货",
  "Yeouido Hangang Park": "汝矣岛汉江",
  "63 Building": "63大厦",
};
const DATA_VERSION = "20260707-foodfull1";
const FOOD_LEVELS = ["全部", "常规", "入门", "进阶", "挑战"];
const CARRY_FILTERS = ["全部", "适合带回国", "需要规划", "慎买"];
const FOOD_DETAIL_ALIASES = {
  血肠汤饭: "血肠汤饭 / 米肠",
  韩式猪蹄: "韩式酱卤猪蹄",
  部队锅: "部队锅本地吃法",
  炸鸡: "韩式炸鸡",
  拌饭: "石锅 / 全州拌饭",
  雪冰: "雪冰 / 韩式刨冰",
};
const GENERATED_FOOD_IMAGE_CREDIT = "AI generated thumbnail";
const foodState = { difficulty: "全部" };
const shopState = { category: "全部", carry: "全部", query: "" };
let foodGuideData = null;
let souvenirGuideData = null;

function escapeHtml(value = "") {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function tag(label, kind = "") {
  if (!label) return "";
  return `<span class="tag ${escapeHtml(kind)}">${escapeHtml(label)}</span>`;
}

function action(url, label) {
  if (!url) return "";
  return `<a class="action-link" href="${escapeHtml(url)}" target="_blank" rel="noreferrer">${escapeHtml(label)}</a>`;
}

function setHtml(selector, html) {
  const node = $(selector);
  if (!node) return;
  node.innerHTML = html || $("#emptyTemplate").innerHTML;
}

function updateBottomNavIndicator() {
  const nav = $(".bottom-nav");
  if (!nav) return;
  const active = $(".nav-item.is-active", nav);
  if (!active) {
    nav.classList.remove("has-active-indicator");
    return;
  }
  const navRect = nav.getBoundingClientRect();
  const activeRect = active.getBoundingClientRect();
  nav.style.setProperty("--active-x", `${activeRect.left - navRect.left}px`);
  nav.style.setProperty("--active-w", `${activeRect.width}px`);
  nav.classList.add("has-active-indicator");
}

async function loadTravel() {
  const response = await fetch(`./data/travel.json?v=${DATA_VERSION}`);
  if (!response.ok) throw new Error("Failed to load travel.json");
  return response.json();
}

async function loadRouteIdeas() {
  const response = await fetch(`./data/travel_route_ideas.json?v=${DATA_VERSION}`);
  if (!response.ok) return null;
  return response.json();
}

async function loadFoodGuide() {
  const response = await fetch(`./data/seoul_food.json?v=${DATA_VERSION}`);
  if (!response.ok) throw new Error("Failed to load seoul_food.json");
  return response.json();
}

async function loadSouvenirGuide() {
  const response = await fetch(`./data/seoul_souvenirs.json?v=${DATA_VERSION}`);
  if (!response.ok) throw new Error("Failed to load seoul_souvenirs.json");
  return response.json();
}

function normalizeText(value = "") {
  return String(value).toLowerCase().trim();
}

function googleMapsSearchUrl(query) {
  const params = new URLSearchParams({ api: "1", query });
  return `https://www.google.com/maps/search/?${params.toString()}`;
}

function naverMapSearchUrl(query) {
  return `https://map.naver.com/p/search/${encodeURIComponent(query)}`;
}

function copyButton(value, label = "Copy") {
  if (!value) return "";
  return `<button class="action-link travel-copy-button" type="button" data-copy="${escapeHtml(value)}">${escapeHtml(label)}</button>`;
}

function travelFilterButton(label, active, dataName) {
  return `
    <button class="travel-filter-chip ${active ? "is-active" : ""}" type="button" ${dataName}="${escapeHtml(label)}" aria-pressed="${active ? "true" : "false"}">
      ${escapeHtml(label)}
    </button>
  `;
}

function groupById(data, id) {
  return (data.groups || []).find((group) => group.id === id);
}

function routesByGroup(data, group) {
  return (data.routes || []).filter((row) => row.group === group);
}

function essentialsByCategory(data, category) {
  return (data.essentials || []).filter((row) => row.category === category);
}

function spotName(spot) {
  if (!spot?.name_en) return spot?.name_zh || "";
  if (!spot.name_zh || spot.name_zh === spot.name_en) return spot.name_en;
  return `${spot.name_en} / ${spot.name_zh}`;
}

function spotCopyText(spot) {
  return spot.query || [spot.name_en, "Seoul"].filter(Boolean).join(", ") || spot.name_zh || "";
}

function routeCard(row) {
  const label = GROUP_LABELS[row.group] || row.group;
  return `
    <article class="route-card travel-route-card">
      <div class="meta-row">${tag(label)}${tag(row.travelmode)}</div>
      <h4>${escapeHtml(row.name)}</h4>
      <p>${escapeHtml(row.why)}</p>
      <div class="actions">${action(row.google_maps_directions_url, "Route")}</div>
    </article>
  `;
}

const SPOT_NOTE_ZH = {
  "Gyeongbokgung Palace": "朝鲜王朝最大宫殿，可和光化门、北村一起安排。",
  "Gwanghwamun Gate": "景福宫正门和广场地标，适合作为市中心路线起点。",
  "Cheong Wa Dae": "景福宫北侧的前总统府，适合顺路看历史建筑。",
  "Bukchon Hanok Village": "传统韩屋街区，夹在几座王宫之间，适合步行拍照。",
  "MMCA Seoul": "景福宫旁的现代艺术馆，天气不好时也适合。",
  "Arario Museum in Space": "小型美术馆，建筑本身也是看点。",
  Insadong: "画廊、茶馆和伴手礼集中，适合作为市中心散步收尾。",
  "Deoksugung Palace": "市厅附近的宫殿，可和清溪川或明洞顺路。",
  "Changdeokgung Palace": "保存完整的朝鲜王宫，秘苑需要额外规划。",
  "Namsangol Hanok Village": "南山脚下的韩屋村，比北村更省体力。",
  Myeongdong: "主要购物区，适合吃饭、逛街或接南山路线。",
  "Namsan Cable Car": "去首尔塔的经典方式，排队短时更值得。",
  "N Seoul Tower": "首尔经典观景点，适合天气清楚的傍晚。",
  "National Assembly": "汝矣岛路线里的建筑点，有余力再顺路看。",
  "63 Building": "汉江边的天际线地标，可和汝矣岛一起安排。",
  "Centre Pompidou Hanwha Seoul": "蓬皮杜首尔分馆，出发前确认开放信息。",
  "Hangang Park": "低强度汉江夜间散步点，适合会议后放松。",
  "Dongdaemun Design Plaza": "扎哈设计的东大门地标，夜景更强。",
  "Cheonggyecheon Stream": "市中心水边步道，适合 DDP 或明洞之后散步。",
  "Seoullo 7017": "首尔站附近的高架步道，适合顺路走一段。",
  "Lotte World Tower": "555 米高楼和商场，是蚕室路线核心。",
  "Seoul Sky": "乐天世界塔内观景台，天气好时再去。",
  "Seokchon Lake": "蚕室旁平坦湖边步道，适合轻松散步。",
  "Lotte World Adventure": "主题乐园，只有想专门玩一段时间才建议去。",
};

function kindSlug(kind = "") {
  return kind.toLowerCase().replaceAll(" ", "-").replaceAll("/", "-");
}

function kindIcon(kind = "") {
  const text = kind.toLowerCase();
  const icons = {
    palace: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 10h16"/><path d="M6 10V7l6-3 6 3v3"/><path d="M7 10v8"/><path d="M12 10v8"/><path d="M17 10v8"/><path d="M5 18h14"/><path d="M4 21h16"/></svg>',
    hanok: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M3 11l9-6 9 6"/><path d="M5 10h14"/><path d="M6 10v9h12v-9"/><path d="M10 19v-5h4v5"/></svg>',
    museum: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 7l8-4 8 4"/><path d="M5 7h14"/><path d="M7 10v7"/><path d="M12 10v7"/><path d="M17 10v7"/><path d="M5 17h14"/><path d="M4 21h16"/></svg>',
    landmark: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 3l2.2 5.2 5.6.5-4.2 3.6 1.3 5.5L12 14.9 7.1 17.8l1.3-5.5-4.2-3.6 5.6-.5L12 3z"/></svg>',
    shopping: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6 8h12l-1 12H7L6 8z"/><path d="M9 8a3 3 0 0 1 6 0"/></svg>',
    tower: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 3v18"/><path d="M8 21h8"/><path d="M9 7h6"/><path d="M7 12h10"/><path d="M9 7l-3 14"/><path d="M15 7l3 14"/></svg>',
    water: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M3 16c2 0 2-1.5 4-1.5S9 16 11 16s2-1.5 4-1.5S17 16 21 16"/><path d="M3 20c2 0 2-1.5 4-1.5S9 20 11 20s2-1.5 4-1.5S17 20 21 20"/><path d="M7 10l5-6 5 6"/></svg>',
    walk: '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="13" cy="5" r="2"/><path d="M10 22l2-7"/><path d="M15 22l-2-6-3-2 2-5 3 3 3 1"/><path d="M7 13l3-4"/></svg>',
    default: '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="7"/><path d="M12 8v4l3 2"/></svg>',
  };
  if (text.includes("palace") || text.includes("unesco")) return icons.palace;
  if (text.includes("hanok")) return icons.hanok;
  if (text.includes("museum") || text.includes("art")) return icons.museum;
  if (text.includes("architecture") || text.includes("landmark")) return icons.landmark;
  if (text.includes("shopping") || text.includes("craft")) return icons.shopping;
  if (text.includes("skyline") || text.includes("observatory") || text.includes("city view")) return icons.tower;
  if (text.includes("river") || text.includes("lake")) return icons.water;
  if (text.includes("walk")) return icons.walk;
  return icons.default;
}

function routeStepText(text = "") {
  const tokens = [
    ["Incheon Airport", "station-incheon"],
    ["Gimpo Airport", "station-gimpo"],
    ["Bongeunsa Station", "station-bongeunsa"],
    ["Bongeunsa", "station-bongeunsa"],
    ["COEX", "station-coex"],
  ];
  let html = escapeHtml(text);
  tokens.forEach(([name, className]) => {
    html = html.replaceAll(
      escapeHtml(name),
      `<span class="travel-station-token ${className}">${escapeHtml(name)}</span>`,
    );
  });
  return html;
}

function routeStep(step) {
  const line = step.line || step.mode || "";
  const lineClass = line.toLowerCase().replaceAll(" ", "-").replaceAll("/", "-");
  return `
    <li>
      <span class="travel-step-line ${escapeHtml(step.kind || "")} line-${escapeHtml(lineClass)}">${escapeHtml(line)}</span>
      <span>${routeStepText(step.text)}</span>
    </li>
  `;
}

function directionsCard(row) {
  return `
    <article class="travel-directions-card">
      <header>
        <div class="travel-directions-meta">
          <div class="meta-row">${tag(row.badge, row.badge_kind)}${tag(row.duration)}${tag(row.time_estimate)}${tag(row.fare)}</div>
          <div class="actions">
            ${action(row.google_maps_directions_url, "Google Maps")}
          </div>
        </div>
        <h4>${escapeHtml(row.name)}</h4>
        <p>${escapeHtml(row.summary)}</p>
      </header>
      <ol class="travel-steps">${(row.steps || []).map(routeStep).join("")}</ol>
    </article>
  `;
}

function spotCard(spot, compact = false) {
  const zhNote = SPOT_NOTE_ZH[spot.name_en] || spot.note;
  const copyText = spotCopyText(spot);
  return `
    <li class="spot-card ${compact ? "is-compact" : ""}" data-copy-query="${escapeHtml(copyText)}" role="button" tabindex="0" aria-label="Copy ${escapeHtml(copyText)} for Google Maps">
      <span class="spot-icon kind-${escapeHtml(kindSlug(spot.kind))}" aria-hidden="true">${kindIcon(spot.kind)}</span>
      <div>
        <div class="spot-heading">
          <h4>${escapeHtml(spot.name_zh || spot.name_en)}</h4>
          <span>${escapeHtml(spot.name_en || "")}</span>
        </div>
        <p><b>${escapeHtml(zhNote)}</b><span>${escapeHtml(spot.note)}</span></p>
      </div>
    </li>
  `;
}

async function copyText(value) {
  if (navigator.clipboard?.writeText && window.isSecureContext) {
    await navigator.clipboard.writeText(value);
    return;
  }
  const textarea = document.createElement("textarea");
  textarea.value = value;
  textarea.setAttribute("readonly", "");
  textarea.style.position = "fixed";
  textarea.style.left = "-9999px";
  document.body.appendChild(textarea);
  textarea.select();
  document.execCommand("copy");
  textarea.remove();
}

function showCopied(node) {
  window.clearTimeout(node.copyTimer);
  node.classList.add("is-copied");
  node.setAttribute("data-copy-feedback", "Copied");
  node.copyTimer = window.setTimeout(() => {
    node.classList.remove("is-copied");
    node.removeAttribute("data-copy-feedback");
  }, 900);
}

function bindSpotCopy(root = document) {
  root.addEventListener("click", async (event) => {
    const card = event.target.closest?.(".spot-card[data-copy-query]");
    if (!card) return;
    await copyText(card.dataset.copyQuery || "");
    showCopied(card);
  });
  root.addEventListener("keydown", async (event) => {
    if (event.key !== "Enter" && event.key !== " ") return;
    const card = event.target.closest?.(".spot-card[data-copy-query]");
    if (!card) return;
    event.preventDefault();
    await copyText(card.dataset.copyQuery || "");
    showCopied(card);
  });
}

function travelGroupCard(group) {
  return `
    <article class="travel-group">
      <header>
        <div>
          <div class="meta-row">${tag(group.when)}</div>
          <h3>${escapeHtml(group.title_en)}</h3>
          <p>${escapeHtml(group.route_hint)}</p>
        </div>
      </header>
      <ul class="spot-list">
        ${(group.spots || []).map((spot) => spotCard(spot, true)).join("")}
      </ul>
    </article>
  `;
}

function routeIdeaUrl(route, origin) {
  const stops = (route.stops || []).filter((stop) => Number.isFinite(stop.lat) && Number.isFinite(stop.lng));
  if (!stops.length || !origin?.query) return "";
  const destination = stops[stops.length - 1];
  const params = new URLSearchParams({
    api: "1",
    origin: origin.query,
    destination: `${destination.lat},${destination.lng}`,
    travelmode: "transit",
  });
  const waypoints = stops.slice(0, -1).map((stop) => `${stop.lat},${stop.lng}`).join("|");
  if (waypoints) params.set("waypoints", waypoints);
  return `https://www.google.com/maps/dir/?${params.toString()}`;
}

function routeIdeaStop(stop) {
  return `
    <li>
      <b>${escapeHtml(stop.label || stop.name)}</b>
      <span>${escapeHtml(stop.note || stop.name)}</span>
    </li>
  `;
}

function shortStopName(stop) {
  const name = typeof stop === "string" ? stop : stop?.name || "";
  if (typeof stop === "object" && stop?.label) return stop.label;
  if (SHORT_STOP_NAMES[name]) return SHORT_STOP_NAMES[name];
  return String(name)
    .split(" / ")[0]
    .split(" 与 ")[0]
    .split(" · ")[0]
    .replace(/\s+[A-Z][A-Za-z\s]+$/, "")
    .trim();
}

function routePhotoTile(stop, index) {
  const label = shortStopName(stop);
  return `
    <figure class="route-photo-tile ${stop.photo ? "" : "is-empty"}" style="--tile-index: ${index}">
      ${
        stop.photo
          ? `<img src="${escapeHtml(stop.photo)}" alt="${escapeHtml(label)}" loading="lazy" referrerpolicy="no-referrer" onerror="this.parentElement.classList.add('is-empty'); this.remove();">`
          : ""
      }
      <figcaption>${escapeHtml(label)}</figcaption>
    </figure>
  `;
}

function routePhotoCollage(route, stops) {
  const tiles = stops.slice(0, 3);
  if (!tiles.length) {
    return `
      <div class="route-idea-media has-1">
        <figure class="route-photo-tile is-empty">
          <figcaption>${escapeHtml(route.title || "Seoul")}</figcaption>
        </figure>
      </div>
    `;
  }
  return `
    <div class="route-idea-media has-${tiles.length}">
      ${tiles.map(routePhotoTile).join("")}
    </div>
  `;
}

function routeIdeaCard(route, origins) {
  const stops = (route.stops || []).slice(0, 3);
  return `
    <article class="route-idea-card">
      ${routePhotoCollage(route, stops)}
      <div class="route-idea-body">
        <header>
          <div>
            <div class="meta-row">${tag(route.subtitle)}${(route.tags || []).map((label) => tag(label)).join("")}</div>
            <h3>${escapeHtml(route.title)}</h3>
          </div>
        </header>
        <p class="route-idea-summary">${escapeHtml(route.summary)}</p>
        <ol class="route-stop-list">${stops.map(routeIdeaStop).join("")}</ol>
        ${
          route.backup
            ? `<p class="route-idea-backup">${tag(route.backup.label)}<span>${escapeHtml(route.backup.summary)}</span></p>`
            : ""
        }
        <div class="route-origin-actions">
          ${(origins || []).map((origin) => action(routeIdeaUrl(route, origin), origin.label)).join("")}
        </div>
      </div>
    </article>
  `;
}

function renderRouteIdeas(routeData) {
  const root = $("#routeIdeas");
  if (!root) return;
  const routes = routeData?.routes || [];
  if (!routes.length) {
    root.innerHTML = $("#emptyTemplate").innerHTML;
    return;
  }
  root.innerHTML = `
    <div class="route-ideas-note">
      <span>${escapeHtml(routeData.note || "Flexible routes")}</span>
    </div>
    ${routes.map((route) => routeIdeaCard(route, routeData.origins || [])).join("")}
  `;
}

function foodQuery(food) {
  const koreanName = String(food.krName || food.enName || food.cnName || "")
    .split("/")
    .map((item) => item.trim())
    .find(Boolean);
  const area =
    (food.areas || []).find(Boolean) ||
    String(food.area || "")
      .split("/")
      .map((item) => item.trim())
      .find(Boolean) ||
    "Seoul";
  return [koreanName || food.cnName, area, "Seoul"].filter(Boolean).join(" ");
}

function foodDetailForName(guide, name) {
  const targetName = FOOD_DETAIL_ALIASES[name] || name;
  return (guide?.foods || []).find((food) => food.cnName === targetName || food.id === targetName);
}

function foodAreaTags(food) {
  if (food.areas?.length) return food.areas.slice(0, 2);
  return String(food.area || "")
    .split("/")
    .map((item) => item.trim())
    .filter(Boolean)
    .slice(0, 2);
}

function foodOverviewItems(guide) {
  const groups = guide?.overviewGroups || [];
  if (!groups.length) {
    return (guide?.foods || []).map((food) => ({
      ...food,
      key: food.id || food.cnName,
      detail: food,
      group: food.difficulty,
      area: (food.areas || []).join(" / "),
      groupNote: food.reason,
    }));
  }

  return groups.flatMap((group) =>
    (group.items || []).map(([cnName, krName, area, difficulty, itemImage]) => {
      const detail = foodDetailForName(guide, cnName);
      const overviewImage = itemImage || guide?.overviewImages?.[cnName] || "";
      const image = detail?.image || overviewImage;
      return {
        key: `${group.name}::${cnName}`,
        cnName,
        krName: krName || detail?.krName || "",
        difficulty: difficulty || detail?.difficulty || "",
        area,
        areas: detail?.areas || [],
        group: group.name,
        groupNote: group.note || "",
        detail,
        image,
        imageAlt: detail?.imageAlt || cnName,
        imageCredit: detail?.imageCredit || (overviewImage ? GENERATED_FOOD_IMAGE_CREDIT : ""),
        reason: detail?.reason || group.note || "",
      };
    }),
  );
}

function foodCard(food) {
  const query = foodQuery(food);
  const areas = foodAreaTags(food);
  return `
    <article class="travel-food-tile">
      <button class="travel-food-tile-main" type="button" data-food-detail="${escapeHtml(food.key)}">
        <figure class="travel-food-thumb">
          ${
            food.image
              ? `<img src="${escapeHtml(food.image)}" alt="${escapeHtml(food.imageAlt || food.cnName)}" loading="lazy">`
              : `<div class="travel-visual-placeholder" aria-hidden="true">${escapeHtml(food.cnName || "Food")}</div>`
          }
          <figcaption>${escapeHtml(food.difficulty)}</figcaption>
        </figure>
        <div class="travel-food-tile-body">
          <div class="travel-extra-kicker">
            <span>${escapeHtml(food.group || food.krName || "")}</span>
            ${tag(food.difficulty)}
          </div>
          <h3>${escapeHtml(food.cnName)}</h3>
          <p>${escapeHtml(food.krName || food.reason || "")}</p>
          <div class="travel-mini-tags">${areas.map((area) => tag(area)).join("")}</div>
        </div>
      </button>
      <div class="travel-extra-actions">
        ${action(googleMapsSearchUrl(query), "Google")}
        ${copyButton(query)}
      </div>
    </article>
  `;
}

function foodRouteCard(route, index) {
  return `
    <article class="travel-route-mini-card">
      <span>${String(index + 1).padStart(2, "0")}</span>
      <h3>${escapeHtml(route.title)}</h3>
      <p>${escapeHtml(route.subtitle)}</p>
      <div class="travel-mini-tags">${(route.picks || []).map((pick) => tag(pick)).join("")}</div>
    </article>
  `;
}

function renderFoodFilters(guide) {
  const root = $("#foodFilters");
  if (!root) return;
  const available = new Set(foodOverviewItems(guide).map((food) => food.difficulty));
  const levels = FOOD_LEVELS.filter((level) => level === "全部" || available.has(level));
  root.innerHTML = levels.map((level) => travelFilterButton(level, foodState.difficulty === level, "data-food-filter")).join("");
}

function renderFoodGuide(guide) {
  const foods = foodOverviewItems(guide);
  const filtered = foodState.difficulty === "全部" ? foods : foods.filter((food) => food.difficulty === foodState.difficulty);
  renderFoodFilters(guide);
  const foodRoot = $("#foodGuide");
  if (foodRoot) {
    foodRoot.className = "travel-food-grid";
    foodRoot.innerHTML = filtered.map(foodCard).join("") || $("#emptyTemplate").innerHTML;
  }
  setHtml("#foodRoutes", (guide.routes || []).map(foodRouteCard).join(""));
  const count = $("#foodResultCount");
  if (count) count.textContent = `${filtered.length} / ${foods.length} foods`;
}

function carryBucket(item) {
  if (item.carry_score >= 4 && item.is_suitable_to_bring_home === "yes") return "适合带回国";
  if (item.is_suitable_to_bring_home === "conditional" || item.carry_score === 3) return "需要规划";
  return "慎买";
}

function shopSearchText(item) {
  return normalizeText(
    [
      item.product_name_cn,
      item.product_name_en,
      item.product_name_ko,
      item.brand_or_store,
      item.shop_name,
      item.area,
      item.category,
      item.category_group,
      item.nearest_station,
      item.address_en,
      item.address_ko,
      ...(item.best_for || []),
      ...(item.tags || []),
    ].join(" "),
  );
}

function shopMatches(item) {
  const query = normalizeText(shopState.query);
  return (
    (shopState.category === "全部" || item.category_group === shopState.category) &&
    (shopState.carry === "全部" || carryBucket(item) === shopState.carry) &&
    (!query || shopSearchText(item).includes(query))
  );
}

function shopMapQuery(item) {
  return item.map_search_keyword || [item.shop_name, item.address_ko || item.address_en].filter(Boolean).join(" ");
}

function shopVisual(item) {
  if (item.image_url) {
    return `<img src="${escapeHtml(item.image_url)}" alt="${escapeHtml(item.image_alt || item.product_name_cn)}" loading="lazy">`;
  }
  return `
    <div class="travel-shop-placeholder" style="--visual-color: ${escapeHtml(item.visual_color || "#d8e3dd")}">
      <span>${escapeHtml(item.visual_label || item.category_group || "Gift")}</span>
    </div>
  `;
}

function shopCard(item) {
  const query = shopMapQuery(item);
  return `
    <article class="travel-extra-card travel-shop-card">
      <figure class="travel-extra-media travel-shop-media">
        ${shopVisual(item)}
        <figcaption>${escapeHtml(carryBucket(item))}</figcaption>
      </figure>
      <div class="travel-extra-body">
        <div class="travel-extra-kicker">
          <span>${escapeHtml(item.category_group)}</span>
          ${tag(item.area)}
        </div>
        <h3>${escapeHtml(item.product_name_cn)}</h3>
        <p>${escapeHtml(item.why_buy)}</p>
        <div class="travel-shop-facts">
          <span><b>买</b>${escapeHtml(item.shop_name)}</span>
          <span><b>站</b>${escapeHtml(item.nearest_station)}</span>
          <span><b>价</b>${escapeHtml(item.price_bucket || "待确认")}</span>
        </div>
        <div class="travel-extra-actions">
          <button class="action-link" type="button" data-shop-detail="${escapeHtml(item.id)}">Details</button>
          ${action(naverMapSearchUrl(query), "Naver")}
          ${action(googleMapsSearchUrl(query), "Google")}
          ${copyButton(item.address_ko || item.address_en)}
        </div>
      </div>
    </article>
  `;
}

function shopRouteCard(route, index) {
  return `
    <article class="travel-route-mini-card travel-shop-route-card">
      <span>${String(index + 1).padStart(2, "0")}</span>
      <h3>${escapeHtml(route.title)}</h3>
      <p>${escapeHtml(route.summary)}</p>
      <div class="travel-mini-tags">${tag(route.time)}${tag(route.best_for)}</div>
      <div class="travel-extra-actions">
        ${action(naverMapSearchUrl(route.search_keyword || route.stops?.join(" ") || route.title), "Naver")}
        ${copyButton(`${route.title}: ${(route.stops || []).join(" -> ")}`, "Copy route")}
      </div>
    </article>
  `;
}

function renderShopFilters(guide) {
  const categories = ["全部", ...new Set((guide.souvenirs || []).map((item) => item.category_group).filter(Boolean))];
  setHtml(
    "#shopCarryFilters",
    CARRY_FILTERS.map((label) => travelFilterButton(label, shopState.carry === label, "data-shop-carry")).join(""),
  );
  setHtml(
    "#shopCategoryFilters",
    categories.map((label) => travelFilterButton(label, shopState.category === label, "data-shop-category")).join(""),
  );
}

function renderShopGuide(guide) {
  const items = guide.souvenirs || [];
  const filtered = items.filter(shopMatches);
  renderShopFilters(guide);
  setHtml("#shopRoutes", (guide.routePlans || []).map(shopRouteCard).join(""));
  setHtml("#shopGuide", filtered.map(shopCard).join(""));
  const count = $("#shopResultCount");
  if (count) count.textContent = `${filtered.length} / ${items.length} gifts`;
}

function detailLine(label, value) {
  if (!value) return "";
  return `<div class="travel-detail-line"><b>${escapeHtml(label)}</b><span>${escapeHtml(value)}</span></div>`;
}

function sourceLinks(urls = []) {
  return urls
    .map((url, index) => `<a href="${escapeHtml(url)}" target="_blank" rel="noreferrer">Source ${index + 1}</a>`)
    .join("");
}

function openTravelModal(html) {
  const modal = $("#travelDetailModal");
  const content = $("#travelModalContent");
  if (!modal || !content) return;
  content.innerHTML = html;
  if (typeof modal.showModal === "function") modal.showModal();
  else modal.setAttribute("open", "");
}

function openFoodDetail(id) {
  const overview = foodOverviewItems(foodGuideData).find((item) => item.key === id || item.detail?.id === id || item.detail?.cnName === id);
  const food = overview?.detail || (foodGuideData?.foods || []).find((item) => (item.id || item.cnName) === id);
  if (!overview && !food) return;
  if (!food) {
    openTravelModal(`
      <article class="travel-detail-content">
        <figure class="travel-detail-hero">
          ${overview.image ? `<img src="${escapeHtml(overview.image)}" alt="${escapeHtml(overview.imageAlt || overview.cnName)}">` : ""}
        </figure>
        <p class="eyebrow">${escapeHtml(overview.difficulty)} · ${escapeHtml(overview.krName || "")}</p>
        <h2>${escapeHtml(overview.cnName)}</h2>
        <p>${escapeHtml(overview.groupNote)}</p>
        <div class="travel-detail-grid">
          ${detailLine("分类", overview.group)}
          ${detailLine("推荐区域", overview.area)}
          ${detailLine("图片", overview.imageCredit)}
        </div>
        <div class="travel-extra-actions">
          ${action(googleMapsSearchUrl(foodQuery(overview)), "Google Maps")}
          ${copyButton(foodQuery(overview))}
        </div>
      </article>
    `);
    return;
  }
  openTravelModal(`
    <article class="travel-detail-content">
      <figure class="travel-detail-hero">
        ${food.image ? `<img src="${escapeHtml(food.image)}" alt="${escapeHtml(food.imageAlt || food.cnName)}">` : ""}
      </figure>
      <p class="eyebrow">${escapeHtml(food.difficulty)} · ${escapeHtml(food.krName || "")}</p>
      <h2>${escapeHtml(food.cnName)}</h2>
      <p>${escapeHtml(food.reason)}</p>
      <div class="travel-detail-grid">
        ${detailLine("国内差异", food.chinaGap)}
        ${detailLine("口味特点", food.flavor)}
        ${detailLine("推荐区域", (food.areas || []).join(" / "))}
        ${detailLine("适合人群", food.audience)}
        ${detailLine("避雷提醒", food.warning)}
        ${detailLine("价格", food.price)}
      </div>
      <div class="travel-extra-actions">
        ${action(googleMapsSearchUrl(foodQuery(food)), "Google Maps")}
        ${copyButton(foodQuery(food))}
      </div>
    </article>
  `);
}

function openShopDetail(id) {
  const item = (souvenirGuideData?.souvenirs || []).find((candidate) => candidate.id === id);
  if (!item) return;
  const query = shopMapQuery(item);
  openTravelModal(`
    <article class="travel-detail-content">
      <figure class="travel-detail-hero travel-shop-detail-hero">
        ${shopVisual(item)}
      </figure>
      <p class="eyebrow">${escapeHtml(item.category_group)} · ${escapeHtml(item.area)}</p>
      <h2>${escapeHtml(item.product_name_cn)}</h2>
      <p class="travel-detail-subtitle">${escapeHtml(item.product_name_ko)} · ${escapeHtml(item.product_name_en)}</p>
      <p>${escapeHtml(item.why_buy)}</p>
      <div class="travel-detail-grid">
        ${detailLine("适合送给", (item.best_for || []).join(" / "))}
        ${detailLine("预估价格", item.price_range_krw)}
        ${detailLine("购买地点", item.shop_name)}
        ${detailLine("最近地铁", item.nearest_station)}
        ${detailLine("韩文地址", item.address_ko)}
        ${detailLine("英文地址", item.address_en)}
        ${detailLine("营业时间", item.opening_hours)}
        ${detailLine("购买提醒", item.caution_note)}
        ${detailLine("带回国", item.bring_home_note)}
      </div>
      <div class="travel-extra-actions">
        ${action(naverMapSearchUrl(query), "Naver Map")}
        ${action(googleMapsSearchUrl(query), "Google Maps")}
        ${copyButton(item.address_ko || item.address_en, "Copy address")}
        ${copyButton(query, "Copy keyword")}
      </div>
      <div class="travel-source-links">${sourceLinks(item.source_urls)}</div>
    </article>
  `);
}

function closeTravelModal() {
  const modal = $("#travelDetailModal");
  if (!modal) return;
  if (typeof modal.close === "function") modal.close();
  else modal.removeAttribute("open");
}

function updateTravelTabs(activeKey) {
  $$("[data-travel-tab]").forEach((tab) => {
    const isActive = tab.dataset.travelTab === activeKey;
    tab.classList.toggle("is-active", isActive);
    if (isActive) tab.setAttribute("aria-current", "true");
    else tab.removeAttribute("aria-current");
  });
}

function updateTravelTabsCompact() {
  const tabs = $(".travel-mode-tabs");
  if (!tabs) return;
  tabs.classList.toggle("is-compact", window.scrollY > 90);
}

function bindTravelTabObserver() {
  const panels = $$("[data-travel-panel]");
  if (!panels.length || !("IntersectionObserver" in window)) return;
  const observer = new IntersectionObserver(
    (entries) => {
      const visible = entries
        .filter((entry) => entry.isIntersecting)
        .sort((a, b) => b.intersectionRatio - a.intersectionRatio)[0];
      if (visible?.target?.dataset.travelPanel) updateTravelTabs(visible.target.dataset.travelPanel);
    },
    { rootMargin: "-22% 0px -62% 0px", threshold: [0.04, 0.12, 0.2] },
  );
  panels.forEach((panel) => observer.observe(panel));
}

function bindTravelInteractions() {
  document.addEventListener("click", async (event) => {
    const foodFilter = event.target.closest?.("[data-food-filter]");
    if (foodFilter) {
      foodState.difficulty = foodFilter.dataset.foodFilter;
      renderFoodGuide(foodGuideData);
      return;
    }

    const shopCategory = event.target.closest?.("[data-shop-category]");
    if (shopCategory) {
      shopState.category = shopCategory.dataset.shopCategory;
      renderShopGuide(souvenirGuideData);
      return;
    }

    const shopCarry = event.target.closest?.("[data-shop-carry]");
    if (shopCarry) {
      shopState.carry = shopCarry.dataset.shopCarry;
      renderShopGuide(souvenirGuideData);
      return;
    }

    const foodDetail = event.target.closest?.("[data-food-detail]");
    if (foodDetail) {
      openFoodDetail(foodDetail.dataset.foodDetail);
      return;
    }

    const shopDetail = event.target.closest?.("[data-shop-detail]");
    if (shopDetail) {
      openShopDetail(shopDetail.dataset.shopDetail);
      return;
    }

    const copyTarget = event.target.closest?.("[data-copy]");
    if (copyTarget) {
      await copyText(copyTarget.dataset.copy || "");
      showCopied(copyTarget);
      return;
    }

    const closeButton = event.target.closest?.("[data-close-travel-modal]");
    if (closeButton) closeTravelModal();
  });

  $("#travelDetailModal")?.addEventListener("click", (event) => {
    if (event.target === event.currentTarget) closeTravelModal();
  });

  $("#travelShopSearch")?.addEventListener("input", (event) => {
    shopState.query = event.target.value;
    renderShopGuide(souvenirGuideData);
  });

  $$("[data-travel-tab]").forEach((tab) => {
    tab.addEventListener("click", () => updateTravelTabs(tab.dataset.travelTab));
  });
}

function renderAirport(data) {
  setHtml("#airportRouteSteps", (data.airport_route_steps || []).map(directionsCard).join(""));
}

function renderSeoulHighlights(data) {
  const groups = CLASSIC_GROUPS.map((id) => groupById(data, id)).filter(Boolean);
  setHtml("#seoulHighlights", groups.map(travelGroupCard).join(""));
  bindSpotCopy($("#seoulHighlights"));
}

Promise.all([loadTravel(), loadRouteIdeas(), loadFoodGuide(), loadSouvenirGuide()])
  .then(([data, routeIdeas, foodGuide, souvenirGuide]) => {
    foodGuideData = foodGuide;
    souvenirGuideData = souvenirGuide;
    updateBottomNavIndicator();
    const frame = $("#travelMapFrame");
    if (frame && data.map_html && !frame.src.includes("?focus=")) frame.src = data.map_html;
    renderAirport(data);
    renderFoodGuide(foodGuide);
    renderShopGuide(souvenirGuide);
    renderRouteIdeas(routeIdeas);
    renderSeoulHighlights(data);
    bindTravelInteractions();
    bindTravelTabObserver();
  })
  .catch((error) => {
    document.body.insertAdjacentHTML("afterbegin", `<div class="panel"><strong>${escapeHtml(error.message)}</strong></div>`);
  });

window.addEventListener("resize", () => requestAnimationFrame(updateBottomNavIndicator), { passive: true });
window.addEventListener("scroll", () => requestAnimationFrame(updateTravelTabsCompact), { passive: true });
window.addEventListener("orientationchange", () => setTimeout(updateBottomNavIndicator, 220), { passive: true });
requestAnimationFrame(updateBottomNavIndicator);
requestAnimationFrame(updateTravelTabsCompact);
