const $ = (selector, root = document) => root.querySelector(selector);
const $$ = (selector, root = document) => Array.from(root.querySelectorAll(selector));

const GROUP_LABELS = {
  airport: "Airport",
  side_event_zone: "Evening zone",
  venue_access: "Venue access",
};

const CLASSIC_GROUPS = ["palace_bukchon", "namsan_myeongdong", "hanriver_yeouido", "ddp_city_walk", "jamsil_skyline"];

function escapeHtml(value = "") {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
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
  const response = await fetch("./data/travel.json");
  if (!response.ok) throw new Error("Failed to load travel.json");
  return response.json();
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

function renderAirport(data) {
  setHtml("#airportRouteSteps", (data.airport_route_steps || []).map(directionsCard).join(""));
}

function renderSeoulHighlights(data) {
  const groups = CLASSIC_GROUPS.map((id) => groupById(data, id)).filter(Boolean);
  setHtml("#seoulHighlights", groups.map(travelGroupCard).join(""));
  bindSpotCopy($("#seoulHighlights"));
}

loadTravel()
  .then((data) => {
    updateBottomNavIndicator();
    const frame = $("#travelMapFrame");
    if (frame && data.map_html && !frame.src.includes("?focus=")) frame.src = data.map_html;
    renderAirport(data);
    renderSeoulHighlights(data);
  })
  .catch((error) => {
    document.body.insertAdjacentHTML("afterbegin", `<div class="panel"><strong>${escapeHtml(error.message)}</strong></div>`);
  });

window.addEventListener("resize", () => requestAnimationFrame(updateBottomNavIndicator), { passive: true });
window.addEventListener("orientationchange", () => setTimeout(updateBottomNavIndicator, 220), { passive: true });
requestAnimationFrame(updateBottomNavIndicator);
