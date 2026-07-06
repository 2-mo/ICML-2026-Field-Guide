const $ = (selector, root = document) => root.querySelector(selector);
const $$ = (selector, root = document) => Array.from(root.querySelectorAll(selector));

const state = {
  data: { events: [], last_update: "" },
  query: "",
  date: "all",
  status: "all",
  type: "all",
  view: "timeline",
  expanded: new Set(),
};

const VIEW_LABELS = {
  timeline: "Timeline",
  calendar: "Calendar",
  map: "Map",
  companies: "Companies",
};

const STATUS_CLASS = {
  Official: "official",
  Public: "public",
  Invite: "invite",
  Registration: "registration",
};

const DAY_LABEL = {
  "2026-07-06": "July 6",
  "2026-07-07": "July 7",
  "2026-07-08": "July 8",
  "2026-07-09": "July 9",
};

async function loadJson(name) {
  const response = await fetch(`./data/${name}.json`);
  if (!response.ok) throw new Error(`Failed to load ${name}.json`);
  return response.json();
}

function escapeHtml(value = "") {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

function unique(values) {
  return [...new Set(values.filter(Boolean))];
}

function eventSearchText(event) {
  return [
    event.title,
    event.organizer,
    event.type,
    event.status,
    event.admission,
    event.venue,
    event.area,
    event.source,
    ...(event.companies || []),
    ...(event.highlights || []),
    ...(event.audience || []),
  ]
    .filter(Boolean)
    .join(" ")
    .toLowerCase();
}

function filteredEvents() {
  const query = state.query.trim().toLowerCase();
  return state.data.events
    .filter((event) => state.date === "all" || event.date === state.date)
    .filter((event) => state.status === "all" || event.status === state.status)
    .filter((event) => state.type === "all" || event.type === state.type)
    .filter((event) => !query || eventSearchText(event).includes(query))
    .sort((a, b) => `${a.date} ${a.sort_time}`.localeCompare(`${b.date} ${b.sort_time}`));
}

function groupBy(items, keyFn) {
  return items.reduce((groups, item) => {
    const key = keyFn(item);
    if (!groups.has(key)) groups.set(key, []);
    groups.get(key).push(item);
    return groups;
  }, new Map());
}

function shortDate(date) {
  return DAY_LABEL[date] || date;
}

function statusTag(event) {
  const statusClass = STATUS_CLASS[event.status] || "default";
  return `<span class="company-status-tag ${statusClass}">${escapeHtml(event.status)}</span>`;
}

function typeTag(event) {
  return `<span class="company-type-tag">${escapeHtml(event.type)}</span>`;
}

function linkButtons(event) {
  if (!event.links?.length) return `<span class="company-link-disabled">No public link</span>`;
  return event.links
    .map((link) => `<a href="${escapeHtml(link.url)}" target="_blank" rel="noreferrer">${escapeHtml(link.label)} ↗</a>`)
    .join("");
}

function companyLogo(name = "", color = "#76b900") {
  const normalized = name.replace(/[^a-zA-Z0-9\u4e00-\u9fa5]/g, "").trim();
  const initials = normalized.slice(0, 2).toUpperCase() || "AI";
  return `<span class="company-logo" style="--event-color: ${escapeHtml(color)}">${escapeHtml(initials)}</span>`;
}

function eventCard(event) {
  const expanded = state.expanded.has(event.id);
  const highlights = (event.highlights || []).map((item) => `<span>${escapeHtml(item)}</span>`).join("");
  const audience = (event.audience || []).map((item) => `<span>${escapeHtml(item)}</span>`).join("");
  const detailsId = `details-${event.id}`;
  return `
    <article class="company-event-card ${expanded ? "is-expanded" : ""}" style="--event-color: ${escapeHtml(event.color || "#76b900")}">
      <button class="company-event-main" type="button" data-expand="${escapeHtml(event.id)}" aria-expanded="${expanded}" aria-controls="${detailsId}">
        <span class="event-color-bar"></span>
        <span class="event-time">${escapeHtml(event.time)}</span>
        <span class="event-copy">
          <span class="event-title-row">
            <b>${escapeHtml(event.title)}</b>
            <span class="event-tags">${statusTag(event)}${typeTag(event)}</span>
          </span>
          <span>${escapeHtml(event.organizer)}</span>
        </span>
      </button>
      <div class="company-event-detail" id="${detailsId}">
        <div class="company-event-meta">
          <span>${escapeHtml(shortDate(event.date))} · ${escapeHtml(event.day || "")}</span>
          <span>${escapeHtml(event.venue || "Venue TBD")}</span>
          <span>${escapeHtml(event.admission || event.status)}</span>
        </div>
        ${highlights ? `<div class="company-highlight-row">${highlights}</div>` : ""}
        ${audience ? `<div class="company-audience-row"><b>Audience</b>${audience}</div>` : ""}
        <p>${escapeHtml(event.source || "")}</p>
        <div class="company-event-actions">${linkButtons(event)}</div>
      </div>
    </article>
  `;
}

function filterButton(value, label, active, attr) {
  return `<button class="company-filter ${active ? "is-active" : ""}" type="button" data-${attr}="${escapeHtml(value)}">${escapeHtml(label)}</button>`;
}

function renderFilters() {
  const events = state.data.events;
  const dates = unique(events.map((event) => event.date)).sort();
  const statuses = unique(events.map((event) => event.status));
  const types = unique(events.map((event) => event.type)).sort();

  $("#companyViewTabs").innerHTML = Object.entries(VIEW_LABELS)
    .map(([value, label]) => filterButton(value, label, state.view === value, "view"))
    .join("");
  $("#companyDateFilters").innerHTML =
    filterButton("all", "All days", state.date === "all", "date") +
    dates.map((date) => filterButton(date, `${shortDate(date)} · ${events.filter((event) => event.date === date).length}`, state.date === date, "date")).join("");
  $("#companyStatusFilters").innerHTML =
    filterButton("all", "All status", state.status === "all", "status") +
    statuses.map((status) => filterButton(status, status, state.status === status, "status")).join("");
  $("#companyTypeFilters").innerHTML =
    filterButton("all", "All types", state.type === "all", "type") +
    types.map((type) => filterButton(type, type, state.type === type, "type")).join("");

  $$("#companyViewTabs [data-view]").forEach((button) => {
    button.addEventListener("click", () => {
      state.view = button.dataset.view;
      render();
    });
  });
  $$("#companyDateFilters [data-date]").forEach((button) => {
    button.addEventListener("click", () => {
      state.date = button.dataset.date;
      render();
    });
  });
  $$("#companyStatusFilters [data-status]").forEach((button) => {
    button.addEventListener("click", () => {
      state.status = button.dataset.status;
      render();
    });
  });
  $$("#companyTypeFilters [data-type]").forEach((button) => {
    button.addEventListener("click", () => {
      state.type = button.dataset.type;
      render();
    });
  });
}

function renderStats(events) {
  const organizerCount = unique(events.flatMap((event) => event.companies || [event.organizer])).length;
  const publicCount = events.filter((event) => event.status === "Public" || event.status === "Registration").length;
  const linkCount = events.filter((event) => event.links?.length).length;
  $("#companyStats").innerHTML = [
    ["Events", `${events.length}+`],
    ["Days", unique(events.map((event) => event.date)).length],
    ["Organizers", `${organizerCount}+`],
    ["Links", linkCount],
    ["Open / Reg", publicCount],
  ]
    .map(
      ([label, value]) => `
        <article>
          <b>${escapeHtml(value)}</b>
          <span>${escapeHtml(label)}</span>
        </article>
      `,
    )
    .join("");
}

function renderTimeline(events) {
  if (!events.length) {
    $("#companyTimeline").innerHTML = $("#emptyTemplate").innerHTML;
    return;
  }
  const groups = groupBy(events, (event) => event.date);
  $("#companyTimeline").innerHTML = [...groups.entries()]
    .map(
      ([date, items]) => `
        <section class="company-day-block">
          <header>
            <span>${escapeHtml(shortDate(date))}</span>
            <b>${escapeHtml(items[0]?.day || "")}</b>
          </header>
          <div>${items.map(eventCard).join("")}</div>
        </section>
      `,
    )
    .join("");
  attachCardEvents();
}

function renderCalendar(events) {
  const allDates = unique(state.data.events.map((event) => event.date)).sort();
  const groups = groupBy(events, (event) => event.date);
  $("#companyCalendar").innerHTML = allDates
    .map((date) => {
      const items = groups.get(date) || [];
      const max = Math.max(1, ...allDates.map((itemDate) => (groups.get(itemDate) || []).length));
      const height = 22 + (items.length / max) * 70;
      return `
        <article class="calendar-day-card ${items.length ? "" : "is-muted"}">
          <div>
            <span>${escapeHtml(shortDate(date))}</span>
            <b>${escapeHtml(items[0]?.day || state.data.events.find((event) => event.date === date)?.day || "")}</b>
          </div>
          <i style="height: ${height}px"></i>
          <strong>${items.length}</strong>
          <ul>
            ${items.slice(0, 4).map((event) => `<li>${escapeHtml(event.time)} · ${escapeHtml(event.title)}</li>`).join("")}
          </ul>
        </article>
      `;
    })
    .join("");
}

function mapPosition(area = "") {
  const key = area.toLowerCase();
  if (key.includes("coex")) return [54, 48];
  if (key.includes("yeouido")) return [20, 62];
  if (key.includes("jamsil")) return [79, 55];
  if (key.includes("gangnam")) return [61, 65];
  return [50, 38];
}

function renderMap(events) {
  const groups = groupBy(events, (event) => event.area || "Seoul");
  const pins = [...groups.entries()]
    .map(([area, items]) => {
      const [left, top] = mapPosition(area);
      return `
        <button class="company-map-pin" type="button" style="left: ${left}%; top: ${top}%;" data-area="${escapeHtml(area)}">
          <span>${items.length}</span>
          <b>${escapeHtml(area)}</b>
        </button>
      `;
    })
    .join("");
  const lists = [...groups.entries()]
    .map(
      ([area, items]) => `
        <article>
          <h3>${escapeHtml(area)}</h3>
          ${items.map((event) => `<p><b>${escapeHtml(event.time)}</b> ${escapeHtml(event.title)} · ${escapeHtml(event.organizer)}</p>`).join("")}
        </article>
      `,
    )
    .join("");
  $("#companyMap").innerHTML = `
    <div class="company-map-stage" aria-label="Approximate Seoul event clusters">
      <span class="map-river"></span>
      <span class="map-coex">COEX</span>
      <span class="map-yeouido">Yeouido</span>
      <span class="map-jamsil">Jamsil</span>
      <span class="map-gangnam">Gangnam</span>
      ${pins}
    </div>
    <div class="company-map-list">${lists}</div>
  `;
}

function renderCompanyCards(events) {
  const groups = groupBy(events, (event) => event.organizer);
  $("#companyCards").innerHTML = [...groups.entries()]
    .map(([organizer, items]) => {
      const color = items[0]?.color || "#76b900";
      const types = unique(items.map((event) => event.type)).slice(0, 3);
      return `
        <article class="company-org-card" style="--event-color: ${escapeHtml(color)}">
          <header>
            ${companyLogo(organizer, color)}
            <div>
              <h3>${escapeHtml(organizer)}</h3>
              <p>${items.length} event${items.length > 1 ? "s" : ""} · ${types.map(escapeHtml).join(" / ")}</p>
            </div>
          </header>
          <div>
            ${items.map((event) => `<span>${escapeHtml(shortDate(event.date))} · ${escapeHtml(event.time)} · ${escapeHtml(event.title)}</span>`).join("")}
          </div>
        </article>
      `;
    })
    .join("");
}

function attachCardEvents() {
  $$("[data-expand]").forEach((button) => {
    button.addEventListener("click", () => {
      const id = button.dataset.expand;
      if (state.expanded.has(id)) state.expanded.delete(id);
      else state.expanded.add(id);
      renderTimeline(filteredEvents());
    });
  });
}

function render() {
  const events = filteredEvents();
  $("#companyUpdate").textContent = `Last Update: ${state.data.last_update || "unknown"} · Seoul time`;
  $("#companyCount").textContent = `${events.length} shown`;
  renderStats(state.data.events);
  renderFilters();
  $$(".company-view").forEach((view) => view.classList.toggle("is-active", view.dataset.view === state.view));
  renderTimeline(events);
  renderCalendar(events);
  renderMap(events);
  renderCompanyCards(events);
}

function bindSearch() {
  $("#companySearch").addEventListener("input", (event) => {
    state.query = event.target.value;
    render();
  });
}

loadJson("company_events")
  .then((data) => {
    state.data = {
      ...data,
      events: (data.events || []).sort((a, b) => `${a.date} ${a.sort_time}`.localeCompare(`${b.date} ${b.sort_time}`)),
    };
    bindSearch();
    render();
  })
  .catch((error) => {
    console.error(error);
    $("#companyTimeline").innerHTML = $("#emptyTemplate").innerHTML;
  });
