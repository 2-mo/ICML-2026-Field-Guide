const state = {
  manifest: null,
  guidePlans: {},
  schedule: null,
  events: null,
  companyEvents: null,
  focus: null,
  essentials: null,
  papers: null,
  starPapers: {},
  search: null,
  selectedDate: "",
  scheduleType: "all",
  eventMode: "side",
  essentialCategory: "within_5_min",
  activeView: "today",
};

const FLOOR_MAP_URL = "https://media.icml.cc/Conferences/ICML2026/coex_map.svg";
let paperDataPromise = null;
let focusDataPromise = null;
let companyEventsPromise = null;
const starPaperDataPromises = {};

const STAR_AUTHORS = [
  { name: "Kaiming He", label: "何恺明", tier: "legend", weight: 120, aliases: ["Kaiming He", "He Kaiming", "何恺明", "何凯明"] },
  { name: "Huazhe Xu", label: "许华哲", tier: "legend", weight: 120, aliases: ["Huazhe Xu", "Xu Huazhe", "许华哲"] },
  { name: "Michael I. Jordan", label: "Michael I. Jordan", tier: "legend", weight: 119, aliases: ["Michael Jordan", "Michael I. Jordan"] },
  { name: "Yann LeCun", label: "杨立昆", tier: "legend", weight: 118, aliases: ["Yann LeCun", "杨立昆"] },
  { name: "Yoshua Bengio", label: "约书亚·本吉奥", tier: "legend", weight: 118, aliases: ["Yoshua Bengio", "约书亚·本吉奥", "约书亚·本希奥"] },
  { name: "Li Fei-Fei", label: "李飞飞", tier: "legend", weight: 116, aliases: ["Li Fei-Fei", "Fei-Fei Li", "李飞飞", "李飛飛"] },
  { name: "Sanjeev Arora", label: "Sanjeev Arora", tier: "legend", weight: 115, aliases: ["Sanjeev Arora"] },
  { name: "Zico Kolter", label: "Zico Kolter", tier: "legend", weight: 115, aliases: ["Zico Kolter", "J. Zico Kolter"] },
  { name: "Sepp Hochreiter", label: "Sepp Hochreiter", tier: "legend", weight: 114, aliases: ["Sepp Hochreiter"] },
  { name: "Dawn Song", label: "宋晓冬", tier: "deep", weight: 96, aliases: ["Dawn Song", "宋晓冬", "宋曉冬"] },
  { name: "Sergey Levine", label: "Sergey Levine", tier: "deep", weight: 94, aliases: ["Sergey Levine"] },
  { name: "Chelsea Finn", label: "Chelsea Finn", tier: "deep", weight: 93, aliases: ["Chelsea Finn"] },
  { name: "Sham Kakade", label: "Sham Kakade", tier: "deep", weight: 93, aliases: ["Sham Kakade"] },
  { name: "Pieter Abbeel", label: "Pieter Abbeel", tier: "deep", weight: 92, aliases: ["Pieter Abbeel"] },
  { name: "Jitendra Malik", label: "Jitendra Malik", tier: "deep", weight: 91, aliases: ["Jitendra Malik"] },
  { name: "Percy Liang", label: "Percy Liang", tier: "deep", weight: 90, aliases: ["Percy Liang"] },
  { name: "Mihaela van der Schaar", label: "Mihaela van der Schaar", tier: "deep", weight: 90, aliases: ["Mihaela van der Schaar"] },
  { name: "Bo Li", label: "Bo Li", tier: "deep", weight: 89, aliases: ["Bo Li"] },
  { name: "Yejin Choi", label: "Yejin Choi", tier: "deep", weight: 89, aliases: ["Yejin Choi"] },
  { name: "Graham Neubig", label: "Graham Neubig", tier: "deep", weight: 88, aliases: ["Graham Neubig"] },
  { name: "Huazheng Wang", label: "Huazheng Wang", tier: "deep", weight: 88, aliases: ["Huazheng Wang"] },
  { name: "Zhiyuan Liu", label: "刘知远", tier: "deep", weight: 88, aliases: ["Zhiyuan Liu", "刘知远"] },
  { name: "Jun Zhu", label: "朱军", tier: "deep", weight: 88, aliases: ["Jun Zhu", "朱军"] },
  { name: "Jie Tang", label: "唐杰", tier: "deep", weight: 87, aliases: ["Jie Tang", "唐杰"] },
  { name: "Luke Zettlemoyer", label: "Luke Zettlemoyer", tier: "deep", weight: 87, aliases: ["Luke Zettlemoyer"] },
  { name: "Christopher Manning", label: "Christopher Manning", tier: "deep", weight: 87, aliases: ["Christopher Manning"] },
  { name: "Stefano Ermon", label: "Stefano Ermon", tier: "deep", weight: 86, aliases: ["Stefano Ermon"] },
  { name: "Jure Leskovec", label: "Jure Leskovec", tier: "deep", weight: 86, aliases: ["Jure Leskovec"] },
  { name: "Max Welling", label: "Max Welling", tier: "deep", weight: 86, aliases: ["Max Welling"] },
  { name: "Ion Stoica", label: "Ion Stoica", tier: "notable", weight: 76, aliases: ["Ion Stoica"] },
  { name: "Matei Zaharia", label: "Matei Zaharia", tier: "notable", weight: 76, aliases: ["Matei Zaharia"] },
  { name: "Alec Radford", label: "Alec Radford", tier: "notable", weight: 75, aliases: ["Alec Radford"] },
  { name: "Trevor Darrell", label: "Trevor Darrell", tier: "notable", weight: 74, aliases: ["Trevor Darrell"] },
  { name: "Antonio Torralba", label: "Antonio Torralba", tier: "notable", weight: 74, aliases: ["Antonio Torralba"] },
  { name: "Rob Fergus", label: "Rob Fergus", tier: "notable", weight: 73, aliases: ["Rob Fergus"] },
  { name: "Dieter Fox", label: "Dieter Fox", tier: "notable", weight: 72, aliases: ["Dieter Fox"] },
  { name: "Russ Tedrake", label: "Russ Tedrake", tier: "notable", weight: 72, aliases: ["Russ Tedrake"] },
  { name: "Saining Xie", label: "Saining Xie", tier: "notable", weight: 71, aliases: ["Saining Xie"] },
  { name: "Zhuang Liu", label: "刘壮", tier: "notable", weight: 70, aliases: ["Zhuang Liu", "Liu Zhuang", "刘壮"] },
  { name: "Jim Fan", label: "Jim Fan", tier: "notable", weight: 70, aliases: ["Jim Fan"] },
  { name: "Jacob Steinhardt", label: "Jacob Steinhardt", tier: "notable", weight: 70, aliases: ["Jacob Steinhardt"] },
  { name: "David Sontag", label: "David Sontag", tier: "notable", weight: 70, aliases: ["David Sontag"] },
  { name: "Anca Dragan", label: "Anca Dragan", tier: "notable", weight: 69, aliases: ["Anca Dragan"] },
  { name: "Dorsa Sadigh", label: "Dorsa Sadigh", tier: "notable", weight: 69, aliases: ["Dorsa Sadigh"] },
  { name: "Ken Goldberg", label: "Ken Goldberg", tier: "notable", weight: 69, aliases: ["Ken Goldberg"] },
  { name: "Yuke Zhu", label: "Yuke Zhu", tier: "notable", weight: 69, aliases: ["Yuke Zhu"] },
  { name: "Moritz Hardt", label: "Moritz Hardt", tier: "notable", weight: 68, aliases: ["Moritz Hardt"] },
  { name: "Tatsunori Hashimoto", label: "Tatsunori Hashimoto", tier: "notable", weight: 68, aliases: ["Tatsunori Hashimoto"] },
  { name: "Ludwig Schmidt", label: "Ludwig Schmidt", tier: "notable", weight: 68, aliases: ["Ludwig Schmidt"] },
  { name: "Marzyeh Ghassemi", label: "Marzyeh Ghassemi", tier: "notable", weight: 68, aliases: ["Marzyeh Ghassemi"] },
  { name: "Aditi Raghunathan", label: "Aditi Raghunathan", tier: "notable", weight: 68, aliases: ["Aditi Raghunathan"] },
  { name: "Joseph E Gonzalez", label: "Joseph E Gonzalez", tier: "notable", weight: 68, aliases: ["Joseph E Gonzalez", "Joseph E. Gonzalez"] },
];

const $ = (selector, root = document) => root.querySelector(selector);
const $$ = (selector, root = document) => Array.from(root.querySelectorAll(selector));

async function loadJson(name) {
  const response = await fetch(`./data/${name}.json`);
  if (!response.ok) throw new Error(`Failed to load ${name}.json`);
  return response.json();
}

async function ensureGuidePlans(date) {
  if (state.guidePlans[date]) return state.guidePlans[date];
  state.guidePlans[date] = await loadJson(`guide_plans/${date}`);
  return state.guidePlans[date];
}

function escapeHtml(value = "") {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

function normalizeAuthorName(value = "") {
  return String(value)
    .normalize("NFKD")
    .replace(/[\u0300-\u036f]/g, "")
    .replace(/[^\p{L}\p{N}]+/gu, " ")
    .trim()
    .toLowerCase();
}

function authorSet(row = {}) {
  return new Set(
    String(row.authors || "")
      .split(/\s*\|\s*/)
      .map(normalizeAuthorName)
      .filter(Boolean),
  );
}

function starAuthors(row = {}) {
  const names = authorSet(row);
  if (!names.size) return [];
  return STAR_AUTHORS.filter((author) => (author.aliases || [author.name]).some((alias) => names.has(normalizeAuthorName(alias)))).sort((a, b) => b.weight - a.weight);
}

function starAuthorWeight(row = {}) {
  return starAuthors(row).reduce((best, author) => Math.max(best, author.weight), 0);
}

function starAuthorDisplay(author) {
  return author.label && author.label !== author.name ? `${author.label} / ${author.name}` : author.label || author.name;
}

function starAuthorTrail(row = {}) {
  const hits = starAuthors(row).slice(0, 3);
  if (!hits.length) return "";
  return `<span class="star-author-trail">(${hits.map((author) => `<span class="star-author ${author.tier}">${escapeHtml(starAuthorDisplay(author))}</span>`).join("")})</span>`;
}

async function ensurePaperData() {
  if (state.papers) return state.papers;
  if (!paperDataPromise) paperDataPromise = loadJson("papers");
  state.papers = await paperDataPromise;
  return state.papers;
}

async function ensureFocusData() {
  if (state.focus) return state.focus;
  if (!focusDataPromise) focusDataPromise = loadJson("focus");
  state.focus = await focusDataPromise;
  return state.focus;
}

async function ensureCompanyEventsData() {
  if (state.companyEvents) return state.companyEvents;
  if (!companyEventsPromise) companyEventsPromise = loadJson("company_events");
  state.companyEvents = await companyEventsPromise;
  return state.companyEvents;
}

function hasStarPapersForDate(date) {
  return ["2026-07-07", "2026-07-08", "2026-07-09"].includes(date);
}

async function ensureStarPaperData(date) {
  if (!hasStarPapersForDate(date)) return { papers: [] };
  if (state.starPapers[date]) return state.starPapers[date];
  if (!starPaperDataPromises[date]) starPaperDataPromises[date] = loadJson(`star_papers/${date}`);
  state.starPapers[date] = await starPaperDataPromises[date];
  return state.starPapers[date];
}

function compactDate(value = "") {
  if (value === "2026-07-10_11") return "Jul 10-11";
  if (!value) return "";
  const date = new Date(`${value}T00:00:00+09:00`);
  return date.toLocaleDateString("en-US", { month: "short", day: "numeric", timeZone: "Asia/Seoul" });
}

function labelDate(value = "") {
  if (value === "2026-07-10_11") return "Fri-Sat, Jul 10-11";
  if (!value) return "TBD";
  const date = new Date(`${value}T00:00:00+09:00`);
  return date.toLocaleDateString("en-US", { weekday: "short", month: "short", day: "numeric", timeZone: "Asia/Seoul" });
}

function weekdayDate(value = "") {
  if (value === "2026-07-10_11") return "Workshop";
  if (!value) return "";
  const date = new Date(`${value}T00:00:00+09:00`);
  return date.toLocaleDateString("en-US", { weekday: "short", timeZone: "Asia/Seoul" });
}

function nowKstDate() {
  const parts = new Intl.DateTimeFormat("en-US", {
    timeZone: "Asia/Seoul",
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
  }).formatToParts(new Date());
  const year = parts.find((part) => part.type === "year")?.value;
  const month = parts.find((part) => part.type === "month")?.value;
  const day = parts.find((part) => part.type === "day")?.value;
  return `${year}-${month}-${day}`;
}

function nowKstMinutes() {
  const parts = new Intl.DateTimeFormat("en-GB", {
    timeZone: "Asia/Seoul",
    hour: "2-digit",
    minute: "2-digit",
    hour12: false,
  }).formatToParts(new Date());
  const hour = Number(parts.find((part) => part.type === "hour")?.value || 0);
  const minute = Number(parts.find((part) => part.type === "minute")?.value || 0);
  return hour * 60 + minute;
}

function timeToMinutes(value = "") {
  const match = value.match(/(\d{1,2}):(\d{2})/);
  if (!match) return null;
  return Number(match[1]) * 60 + Number(match[2]);
}

function selectDefaultDate(dates) {
  const requestedDate = new URLSearchParams(window.location.search).get("date");
  if ((requestedDate === "2026-07-10" || requestedDate === "2026-07-11") && dates.includes("2026-07-10_11")) return "2026-07-10_11";
  if (requestedDate && dates.includes(requestedDate)) return requestedDate;
  const today = nowKstDate();
  if ((today === "2026-07-10" || today === "2026-07-11") && dates.includes("2026-07-10_11")) return "2026-07-10_11";
  if (dates.includes(today)) return today;
  return dates.find((date) => date > today) || dates[dates.length - 1];
}

function action(url, label) {
  if (!url) return "";
  const href = url === "https://media.icml.cc/Conferences/ICML2026/coex_map.svg" ? "./maps/coex_map_modern.html" : url;
  return `<a class="action-link" href="${escapeHtml(href)}" target="_blank" rel="noreferrer">${escapeHtml(label)}</a>`;
}

function tag(label, kind = "") {
  if (!label) return "";
  return `<span class="tag ${kind}">${escapeHtml(label)}</span>`;
}

function tagStrip(items = [], kind = "") {
  const generic = new Set(["RSVP", "Open", "Check first", "Location after RSVP", "Location not public / after RSVP", "deduped"]);
  return items
    .filter(Boolean)
    .filter((item) => !generic.has(String(item).trim()))
    .slice(0, 3)
    .map((item) => tag(item, kind))
    .join("");
}

function compactTopic(label = "") {
  const text = String(label).trim();
  const lowered = text.toLowerCase();
  if (lowered.includes("reinforcement learning") || lowered === "rl") return "RL";
  if (lowered.includes("theory") || lowered.includes("optimization") || lowered.includes("foundations")) return "Theory / Opt";
  if (lowered.includes("robotics") || lowered.includes("embodied")) return "Robotics";
  if (lowered.includes("efficient") || lowered.includes("systems") || lowered.includes("hardware")) return "Systems";
  if (lowered.includes("foundation") || lowered.includes("llm") || lowered.includes("language")) return "LLM / FM";
  if (lowered.includes("data") || lowered.includes("evaluation") || lowered.includes("benchmark")) return "Data / Eval";
  if (lowered.includes("safety") || lowered.includes("alignment") || lowered.includes("reliability")) return "Safety";
  if (lowered.includes("vision") || lowered.includes("video") || lowered.includes("multimodal")) return "Vision";
  if (lowered.includes("causal") || lowered.includes("probabilistic") || lowered.includes("structured")) return "Causal";
  if (lowered.includes("science") || lowered.includes("biology") || lowered.includes("protein")) return "AI4Science";
  return text.length > 18 ? text.split("/")[0].trim() : text;
}

function prettyVenue(value = "") {
  let text = String(value).trim().replace(/\s+/g, " ");
  if (!text || /Location (after RSVP|not public)/i.test(text)) return "";
  text = text.replace(/\bGRAND BALLROOM\s+(\d{3})\s+(\d{3})\b/gi, "Grand Ballroom $1-$2");
  text = text.replace(/\bASEM\s+BALLROOM\s+(\d{3})\s+(\d{3})\b/gi, "ASEM Ballroom $1-$2");
  text = text
    .replace(/\bGRAND BALLROOM\b/gi, "Grand Ballroom")
    .replace(/\bASEM\s+BALLROOM\b/gi, "ASEM Ballroom")
    .replace(/\bHALL\s+([A-D]\d?)\b/gi, (_, hall) => `Hall ${hall.toUpperCase()}`)
    .replace(/\bROOM\s+E\b/gi, "Room E")
    .replace(/\bAUDITORIUM\b/gi, "Auditorium")
    .replace(/\bFOYER\b/gi, "Foyer")
    .replace(/\bASEM\b/gi, "ASEM")
    .replace(/\bCOEX\b/gi, "COEX");
  return text;
}

function isOfficialDenseCard(candidate, block) {
  return block?.kind === "official_slot" && ["tutorial", "mentorship", "official_social", "expo"].includes(candidate.type);
}

function candidateSignals(candidate, block) {
  const generic = new Set(["RSVP", "Open", "Check first", "Location after RSVP", "Location not public / after RSVP", "deduped"]);
  const facts = (candidate.facts || []).filter(Boolean).filter((item) => !generic.has(String(item).trim()));
  const topics = (candidate.topics || []).filter(Boolean).filter((item) => !generic.has(String(item).trim()));
  if (isOfficialDenseCard(candidate, block)) {
    const duplicateType = candidateTypeLabel(candidate).toLowerCase();
    const selectedTopics = topics
      .filter((item) => {
        const label = String(item).trim().toLowerCase();
        return label !== duplicateType && !label.includes(duplicateType);
      })
      .map(compactTopic)
      .slice(0, 3);
    if (!selectedTopics.length) return "";
    return `<div class="signal-strip">${selectedTopics.map((item) => tag(item)).join("")}</div>`;
  }
  const selected = candidate.type === "oral" ? topics.slice(0, 3).map(compactTopic) : [...facts.slice(0, 2), ...topics.map(compactTopic)].slice(0, 3);
  if (!selected.length) return "";
  return `<div class="signal-strip">${selected.map((item, index) => tag(item, candidate.type === "oral" ? "" : index < facts.length ? "ok" : "")).join("")}</div>`;
}

function interestStars(level = "", reasons = []) {
  if (!level) return "";
  const detail = (reasons || []).filter(Boolean).join(" / ");
  const label = level === "close" ? "Close relevance" : "Broad relevance";
  return `<span class="interest-stars ${level}" aria-label="${label}${detail ? `: ${escapeHtml(detail)}` : ""}">★</span>`;
}

function interestMark(value = 0, score = 0, reasons = []) {
  const numericScore = Number(score || 0);
  if (numericScore >= 35) return interestStars("close", reasons);
  if (numericScore >= 28) return interestStars("broad", reasons);
  return "";
}

function displayCandidateTitle(candidate) {
  return String(candidate.title || "").replace(/^我的相关论文\s*·\s*/u, "");
}

function isPriorityPosterRoute(candidate) {
  if (candidate.type !== "poster_route") return false;
  const title = String(candidate.title || "");
  const facts = candidate.facts || [];
  const topics = candidate.topics || [];
  return title.startsWith("我的相关论文") || facts.some((item) => String(item).includes("pick")) || topics.includes("Personal");
}

function posterHighlightMark(item) {
  const flags = String(item.flags || "").toLowerCase();
  if (!flags.includes("spotlight") && !flags.includes("highlight")) return "";
  return `<span class="poster-highlight" aria-label="highlight poster">🌟</span>`;
}

function hasSpotlightFlag(flags = []) {
  return flags.some((flag) => /spotlight|highlight/i.test(String(flag || "")));
}

function minutesFromTimeRange(value = "") {
  const match = String(value || "").match(/\b\d{1,2}:\d{2}\b/);
  return timeToMinutes(match ? match[0] : value.split("-", 1)[0]);
}

function timelineSortValue(row) {
  const dateTime = String(row.sort_time || "").match(/^(\d{4}-\d{2}-\d{2})\s+(\d{1,2}:\d{2})/);
  if (dateTime) {
    const day = Date.parse(`${dateTime[1]}T00:00:00+09:00`) / 60000;
    return day + (timeToMinutes(dateTime[2]) || 0);
  }
  return timeToMinutes(row.sort_time) ?? minutesFromTimeRange(row.time) ?? 9999;
}

function sortCandidates(candidates = []) {
  return [...candidates].sort((a, b) => {
    const timeDiff = minutesFromTimeRange(a.see || a.time || "") - minutesFromTimeRange(b.see || b.time || "");
    if (Number.isFinite(timeDiff) && timeDiff) return timeDiff;
    const starDiff = Number(b.interest_stars || 0) - Number(a.interest_stars || 0);
    if (starDiff) return starDiff;
    const interestDiff = Number(b.interest_score || 0) - Number(a.interest_score || 0);
    if (interestDiff) return interestDiff;
    return Number(b.score || 0) - Number(a.score || 0);
  });
}

function dedupeByTitle(rows = []) {
  const seen = new Set();
  return rows.filter((row) => {
    const key = String(row.title || row.name || "").trim().toLowerCase();
    if (!key) return true;
    if (seen.has(key)) return false;
    seen.add(key);
    return true;
  });
}

function dedupeExamples(rows = []) {
  const seen = new Set();
  return rows.filter((row) => {
    const key = String(row.title || "").trim().toLowerCase();
    if (!key) return true;
    if (seen.has(key)) return false;
    seen.add(key);
    return true;
  });
}

function compactFocusDate(date = "") {
  return date ? compactDate(date) : "TBD";
}

function focusPaperCard(row) {
  const rawFlags = (row.flags || []).map((item) => String(item || ""));
  const hasOral = rawFlags.some((item) => /oral/i.test(item));
  const hasSpotlight = !hasOral && rawFlags.some((item) => /spotlight|highlight/i.test(item));
  const flags = hasOral ? [{ label: "Oral", kind: "oral" }] : hasSpotlight ? [{ label: "Spotlight", kind: "spotlight" }] : [];
  const metaChips = [
    ["date", row.date ? compactFocusDate(row.date) : "TBD"],
    ["time", row.time || ""],
    ["poster", row.position || ""],
    ["room", row.room || ""],
  ].filter(([, value]) => value);
  const websiteUrl = row.website_url || row.url || "";
  const arxivUrl = row.arxiv_url || "";
  return `
    <article class="focus-paper">
      <a class="focus-paper-title" href="${escapeHtml(websiteUrl)}" target="_blank" rel="noreferrer">
        <b>${interestMark(row.interest_stars, row.interest_score, row.interest_reasons)}${escapeHtml(row.title)}</b>
      </a>
      <div class="focus-paper-row">
        <span class="focus-paper-meta">
          ${metaChips.map(([kind, value]) => `<span class="focus-chip ${kind}">${escapeHtml(value)}</span>`).join("")}
        </span>
        <span class="focus-paper-tags">
          ${flags.map((item) => `<span class="focus-flag ${item.kind}">${escapeHtml(item.label)}</span>`).join("")}
          <a href="${escapeHtml(websiteUrl)}" target="_blank" rel="noreferrer">Website</a>
          ${
            arxivUrl
              ? `<a href="${escapeHtml(arxivUrl)}" target="_blank" rel="noreferrer">arXiv</a>`
              : `<span class="is-disabled" aria-disabled="true">arXiv</span>`
          }
        </span>
      </div>
    </article>
  `;
}

function focusPaperGroups() {
  const groups = state.focus?.focus_groups || [];
  if (groups.length) return groups;
  return [
    {
      id: "auto_focus",
      title: "Video Anomaly Understanding",
      papers: state.focus?.paper_focus || [],
    },
  ];
}

function focusGroupIcon(group = {}) {
  return {
    agents_tool_use: "bot",
    reasoning_models: "brain",
    video_anomaly_understanding: "scan-search",
    multimodal_llms: "layers",
    video_understanding: "video",
    anomaly_detection: "radar",
  }[group.id] || "file-text";
}

function iconSvg(name = "file-text") {
  const paths = {
    bot: '<path d="M12 8V4"/><rect x="5" y="8" width="14" height="11" rx="3"/><path d="M9 13h.01"/><path d="M15 13h.01"/><path d="M8 19v2"/><path d="M16 19v2"/>',
    brain: '<path d="M9 4a3 3 0 0 0-3 3v1a3 3 0 0 0 0 6v1a3 3 0 0 0 5 2.2"/><path d="M15 4a3 3 0 0 1 3 3v1a3 3 0 0 1 0 6v1a3 3 0 0 1-5 2.2"/><path d="M12 5v14"/>',
    "scan-search": '<path d="M8 4H5a1 1 0 0 0-1 1v3"/><path d="M16 4h3a1 1 0 0 1 1 1v3"/><path d="M8 20H5a1 1 0 0 1-1-1v-3"/><path d="M15 15l5 5"/><circle cx="11" cy="11" r="4"/>',
    layers: '<path d="m12 3 8 4-8 4-8-4 8-4z"/><path d="m4 12 8 4 8-4"/><path d="m4 17 8 4 8-4"/>',
    video: '<rect x="4" y="6" width="12" height="12" rx="2"/><path d="m16 10 4-2v8l-4-2z"/>',
    radar: '<circle cx="12" cy="12" r="8"/><path d="M12 12V4"/><path d="m12 12 5 5"/><circle cx="12" cy="12" r="2"/>',
    "file-text": '<path d="M14 3H7a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V8z"/><path d="M14 3v5h5"/><path d="M8 13h8"/><path d="M8 17h6"/>',
  };
  return `<svg viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">${paths[name] || paths["file-text"]}</svg>`;
}

function focusPaperGroup(group, index) {
  const rows = dedupeByTitle(group.papers || []);
  if (!rows.length) return "";
  const isVideoAnomalyGroup = group.id === "video_anomaly_understanding";
  const isOpen = !isVideoAnomalyGroup && index === 0;
  return `
    <details class="focus-group" ${isOpen ? "open" : ""}>
      <summary>
        <span class="focus-group-icon focus-icon-${escapeHtml(group.id || "paper")}" aria-hidden="true">
          ${iconSvg(focusGroupIcon(group))}
        </span>
        <b>${escapeHtml(group.title)}</b>
        <em>${rows.length}</em>
        <span class="focus-toggle-hint" aria-hidden="true"></span>
      </summary>
      <div class="focus-paper-list">${rows.map(focusPaperCard).join("")}</div>
    </details>
  `;
}

function focusGroupHeader(groups) {
  if (state.selectedDate !== "2026-07-06") return "";
  const count = groups.reduce((total, group) => total + dedupeByTitle(group.papers || []).length, 0);
  if (!count) return "";
  return `
    <div class="focus-group-header">
      <b>Paper Watchlist</b>
      <span>${count} papers</span>
    </div>
  `;
}

function companyEventsForDate(date) {
  return (state.companyEvents?.events || [])
    .filter((event) => event.date === date)
    .sort((a, b) => `${a.sort_time || "99:00"} ${a.title}`.localeCompare(`${b.sort_time || "99:00"} ${b.title}`));
}

function companyEventLink(event) {
  const link = (event.links || [])[0];
  if (!link?.url) return `<span class="company-day-action is-disabled">No link</span>`;
  const label = link.label || (event.status === "Official" ? "Official" : "Source");
  return `<a class="company-day-action" href="${escapeHtml(link.url)}" target="_blank" rel="noreferrer">${escapeHtml(label)} ↗</a>`;
}

function companyEventRow(event) {
  const statusClass = String(event.status || "").toLowerCase();
  const meta = [event.organizer, event.venue].filter(Boolean).join(" · ");
  return `
    <article class="company-day-event" style="--event-color: ${escapeHtml(event.color || "#0b6b62")}">
      <div class="company-day-time">${escapeHtml(event.time || "TBD")}</div>
      <div class="company-day-main">
        <b>${escapeHtml(event.title)}</b>
        <span>${escapeHtml(meta)}</span>
        <div class="company-day-tags">
          <em class="company-day-tag company-day-status ${escapeHtml(statusClass)}">${escapeHtml(event.status || "Check")}</em>
          <em class="company-day-tag">${escapeHtml(event.type || "Event")}</em>
        </div>
      </div>
      ${companyEventLink(event)}
    </article>
  `;
}

function companyDayBlock(date) {
  const events = companyEventsForDate(date);
  if (!events.length) return "";
  return `
    <article class="route-block daily-company-block">
      <header class="route-block-head">
        <h4>Company / side events</h4>
        <span>${events.length} events</span>
      </header>
      <div class="company-day-list">
        ${events.map(companyEventRow).join("")}
      </div>
    </article>
  `;
}

function candidateScanLine(block, candidate) {
  if (block.kind === "official_slot") return "";
  const types = ["expo", "orientation", "workshop", "tutorial", "mentorship", "official_social", "onsite_tip"];
  if (!types.includes(candidate.type) || !candidate.see) return "";
  return `<p class="scan-line">${escapeHtml(candidate.see)}</p>`;
}

function renderDailyFocus() {
  if (state.selectedDate !== "2026-07-06") {
    $("#dailyFocus").classList.remove("home-day-focus");
    $("#dailyFocus").innerHTML = "";
    return;
  }
  if (!state.focus) {
    $("#dailyFocus").classList.remove("home-day-focus");
    $("#dailyFocus").innerHTML = "";
    void ensureFocusData().then(() => {
      if (state.activeView === "today" && state.selectedDate === "2026-07-06") renderTodayRoute();
    });
    return;
  }
  const focusGroups = focusPaperGroups();
  const homeMap =
    `
        <section class="home-map-card">
          <header>
            <b>COEX Venue Map</b>
            <a href="${FLOOR_MAP_URL}" target="_blank" rel="noreferrer">Official map</a>
          </header>
          <a class="home-map-preview" href="${FLOOR_MAP_URL}" target="_blank" rel="noreferrer" aria-label="Open official COEX venue map">
            <span class="home-bridge home-bridge-arch"></span>
            <span class="home-hall home-cr4">Conf. Room<br />400-403</span>
            <span class="home-hall home-cr3">Conf. Room<br />300-328</span>
            <span class="home-hall home-cbs">COEX<br />Broadcast<br />Studio</span>
            <span class="home-service-strip"></span>
            <span class="home-hall home-hall-c">Hall C</span>
            <span class="home-hall home-hall-a">Hall A</span>
            <span class="home-hall home-hall-d">Hall D</span>
            <span class="home-hall home-hall-b">Hall B</span>
            <span class="home-hall home-room-e">Room E</span>
            <span class="home-hall home-aud">Auditorium</span>
            <span class="home-hall home-asem">ASEM<br />Ballroom<br />201-211</span>
            <span class="home-hall home-gb">Grand<br />Ballroom<br />101-105</span>
            <span class="home-bag-marker" aria-label="Luggage and coat check on 2F inside the Plaetz" title="Luggage and coat check: 2F · inside the Plaetz">
              <svg class="home-marker-icon" aria-hidden="true" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M10 6V5a2 2 0 0 1 2-2h0a2 2 0 0 1 2 2v1" />
                <rect x="5" y="6" width="14" height="15" rx="2" />
                <path d="M9 10h6" />
                <path d="M9 14h6" />
              </svg>
              <b>BAG</b>
            </span>
            <span class="home-badge-marker" aria-label="Registration Desk and badge pickup on 1F at Hall B Foyer, East Gate" title="Badge pickup: 1F · Hall B Foyer · East Gate">
              <svg class="home-marker-icon" aria-hidden="true" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M13.5 8h-3" />
                <path d="m15 2-1 2h3a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h3" />
                <path d="M16.899 22A5 5 0 0 0 7.1 22" />
                <path d="m9 2 3 6" />
                <circle cx="12" cy="15" r="3" />
              </svg>
              <b>BADGE</b>
            </span>
            <span class="home-ground home-mall">Starfield COEX Mall · B1 connection</span>
            <span class="home-station home-samseong"><i></i><b>Samseong Station<br />Line 2</b></span>
            <span class="home-station home-bongeunsa"><i></i><b>Bongeunsa Station<br />Line 9</b></span>
          </a>
        </section>
      `;
  $("#dailyFocus").classList.add("home-day-focus");
  $("#dailyFocus").innerHTML = `
    ${homeMap}
    <div class="focus-group-list">
      ${focusGroupHeader(focusGroups)}
      ${focusGroups.map(focusPaperGroup).join("")}
    </div>
  `;
}

function exampleList(candidate) {
  const rawExamples = dedupeExamples(candidate.examples || []);
  const examples = candidate.type === "oral" ? rawExamples : rawExamples.slice(0, isPriorityPosterRoute(candidate) ? 6 : 4);
  if (!examples.length) return "";
  if (candidate.type === "poster_route") {
    return `
      <div class="example-list">
        ${examples
          .map(
            (item) => `
              <a href="${escapeHtml(item.url)}" target="_blank" rel="noreferrer">
                <b>${escapeHtml(item.position || "poster")}${posterHighlightMark(item)}</b>
                <span>${interestMark(item.interest_stars, item.interest_score, item.interest_reasons)}${escapeHtml(item.title)}</span>
              </a>
            `,
          )
          .join("")}
      </div>
    `;
  }
  if (candidate.type === "side_event") {
    return `
      <div class="example-list">
        ${examples
          .map((item) => {
            const location = item.location || "";
            const showLocation = location && !/Location (after RSVP|not public)/i.test(location);
            return `
              <div>
                <b>${escapeHtml(item.time)}</b>
                <span>${escapeHtml(item.title)}</span>
                ${showLocation ? `<em>${escapeHtml(location)}</em>` : ""}
              </div>
            `;
          })
          .join("")}
      </div>
    `;
  }
  return `
    <div class="example-list">
      ${examples
        .map(
          (item) => `
            <a href="${escapeHtml(item.url)}" target="_blank" rel="noreferrer">
              <b>${escapeHtml(item.time)}</b>
              <span>${interestMark(item.interest_stars, item.interest_score, item.interest_reasons)}${escapeHtml(item.title)}</span>
            </a>
          `,
        )
        .join("")}
    </div>
  `;
}

function sourceAction(candidate) {
  if (!candidate.url) return "";
  const label = candidate.type === "side_event" ? "RSVP" : candidate.type === "company_event" ? "Source" : "Official";
  const href = candidate.url === "https://media.icml.cc/Conferences/ICML2026/coex_map.svg" ? "./maps/coex_map_modern.html" : candidate.url;
  return `<a class="source-link" href="${escapeHtml(href)}" target="_blank" rel="noreferrer" aria-label="Open source">${escapeHtml(label)} ↗</a>`;
}

function candidateKicker(candidate) {
  if (!candidate.code) return "";
  return `<span class="session-code">${escapeHtml(candidate.code)}</span>`;
}

function candidateTypeLabel(candidate) {
  return {
    oral: "Oral",
    poster_route: "Poster",
    star_paper: "Paper",
    side_event: "Meetup",
    company_event: "Company",
    workshop: "Workshop",
    tutorial: "Tutorial",
    mentorship: "Mentor",
    official_social: "Social",
    expo: "Expo",
    orientation: "Route",
    onsite_tip: "First day",
  }[candidate.type] || "";
}

function candidateHead(candidate, block) {
  const typeLabel = candidateTypeLabel(candidate);
  return `
    <div class="candidate-head">
      <div class="candidate-title-block">
        <div class="candidate-meta-row">
          ${candidateKicker(candidate) || (typeLabel ? `<span class="session-code type-code">${escapeHtml(typeLabel)}</span>` : "")}
          ${interestMark(candidate.interest_stars, candidate.interest_score, candidate.interest_reasons)}
          ${candidateSignals(candidate, block)}
          ${sourceAction(candidate)}
        </div>
        <h5>${escapeHtml(displayCandidateTitle(candidate))}${starAuthorTrail(candidate)}</h5>
      </div>
    </div>
  `;
}

function candidatePlace(candidate) {
  const where = prettyVenue(candidate.where || "");
  if (!where || venueInfo(candidate)) return "";
  return `<div class="candidate-place">${escapeHtml(where)}</div>`;
}

function candidateExtra(candidate) {
  if (candidate.type === "workshop") return "";
  if (candidate.type === "star_paper") return starPaperLine(candidate);
  if (candidate.type === "side_event") return sideEventLine(candidate);
  if (candidate.type === "company_event") return companyEventLine(candidate);
  return exampleList(candidate);
}

function candidateCard(candidate, block, { stackable = false } = {}) {
  return `
    <section class="candidate-card candidate-${escapeHtml(candidate.type || "item")} ${candidate.url ? "has-source" : ""}">
      ${candidateHead(candidate, block)}
      ${candidateScanLine(block, candidate)}
      ${candidateExtra(candidate)}
      ${venueMini(candidate)}
      ${candidatePlace(candidate)}
    </section>
  `;
}

function sideEventCategory(candidate) {
  if (candidate.type === "official_social") return "Evening social";
  const text = [candidate.title, candidate.see, ...(candidate.topics || [])].filter(Boolean).join(" ").toLowerCase();
  if (text.includes("dinner")) return "Dinner";
  if (text.includes("cafe") || text.includes("cowork")) return "Cafe / coworking";
  if (text.includes("social")) return "Evening social";
  if (text.includes("meetup") || text.includes("networking")) return "Meetup / networking";
  if (text.includes("workshop") || text.includes("summit")) return "Workshop / summit";
  return "Other side events";
}

function meetupListCard(candidates, category = "Meetups") {
  const items = candidates
    .map((candidate) => {
      const content = `
        <span>${escapeHtml(candidate.facts?.[0] || candidate.see || "RSVP")}</span>
        <b>${escapeHtml(displayCandidateTitle(candidate))}</b>
      `;
      if (!candidate.url) return `<div class="meetup-row">${content}</div>`;
      return `
        <a class="meetup-row" href="${escapeHtml(candidate.url || "#")}" target="_blank" rel="noreferrer">
          ${content}
        </a>
      `;
    })
    .join("");
  return `
    <section class="candidate-card candidate-side_event meetup-list-card has-source">
      <div class="candidate-head">
        <div class="meetup-card-heading">
          <h5>${escapeHtml(category)}</h5>
          <span class="tag ok">${candidates.length} options</span>
        </div>
      </div>
      <div class="meetup-list">${items}</div>
    </section>
  `;
}

function companyEventLine(candidate) {
  const note = candidate.why || "";
  const see = candidate.see || "";
  return `
    <div class="company-event-line">
      ${see ? `<b>${escapeHtml(see)}</b>` : ""}
      ${note ? `<span>${escapeHtml(note)}</span>` : ""}
    </div>
  `;
}

function starPaperLine(candidate) {
  return `
    <div class="star-paper-line">
      <b>${escapeHtml([candidate.see, candidate.where].filter(Boolean).join(" · "))}</b>
    </div>
  `;
}

function sideEventLine(candidate) {
  const organizer = (candidate.topics || [])[0] || candidate.see || "";
  const source = candidate.source_url && candidate.source_url !== candidate.url ? action(candidate.source_url, "Source") : "";
  if (!organizer && !source) return "";
  return `
    <div class="side-event-line">
      ${organizer ? `<span>${escapeHtml(organizer)}</span>` : ""}
      ${source ? `<em>${source}</em>` : ""}
    </div>
  `;
}

function venueInfo(candidate) {
  const where = candidate.where || "";
  const text = where.toUpperCase();
  if (!where || /LOCATION AFTER RSVP|NOT PUBLIC/i.test(where)) return null;
  if (candidate.type === "side_event" || candidate.type === "company_event") return null;
  if (candidate.type === "onsite_tip" && !/HALL|ROOM|BALLROOM|AUDITORIUM|ASEM|FOYER/.test(text)) return null;
  const exact = prettyVenue(where);
  const make = (label, detail, x, y) => ({ label, detail, exact, x, y });
  if (text.includes("ROOM E")) return make("Room E", "inside Hall C", 35, 36);
  if (text.includes("HALL C")) return make("Hall C", "hall cluster", 31, 29);
  if (text.includes("HALL D")) return make("Hall D", "hall cluster", 60, 29);
  if (text.includes("AUDITORIUM")) return make("Auditorium", "ballroom side", 87, 29);
  if (text.includes("ASEM")) return make("ASEM Ballroom", "ballroom side", 87, 58);
  if (text.includes("HALL A")) return make("Hall A", "poster side", 31, 70);
  if (text.includes("HALL B")) return make("Hall B", "hall cluster", 60, 70);
  if (text.includes("GRAND BALLROOM")) return make("Grand Ballroom", "ballroom side", 87, 79);
  if (text.includes(",") || text.includes("FOYER")) return make("COEX Halls", "A/B/C/D hall cluster", 58, 52);
  return make(where, "Open map for exact room", 54, 50);
}

function venueMiniDetail(info) {
  const detail = info.exact && info.exact !== info.label ? info.exact : info.detail;
  return detail
    .replace(/\s*\((?:\d+(?:st|nd|rd|th)\s+)?floor\)/gi, "")
    .replace(/\b[1-4]F\s*·\s*/gi, "")
    .replace(/\s*·\s*[1-4]F\b/gi, "")
    .trim();
}

function venueMini(candidate) {
  const info = venueInfo(candidate);
  if (!info) return "";
  const detail = venueMiniDetail(info);
  return `
    <div class="venue-mini">
      <div class="venue-mini-map" aria-hidden="true">
        <span class="mini-bridge bridge-arch"></span>
        <span class="mini-hall hall-c">C</span>
        <span class="mini-hall hall-d">D</span>
        <span class="mini-hall hall-a">A</span>
        <span class="mini-hall hall-b">B</span>
        <span class="mini-hall conf-cr4">CR4</span>
        <span class="mini-hall conf-cr3">CR3</span>
        <span class="mini-hall conf-cbs">CBS</span>
        <span class="mini-hall room-e">E</span>
        <span class="mini-hall aud">Au</span>
        <span class="mini-hall gb">GB</span>
        <span class="mini-hall asem">AS</span>
        <span class="mini-station station-samseong"></span>
        <span class="mini-station station-bongeunsa"></span>
        <i style="--mx:${info.x}%; --my:${info.y}%"></i>
      </div>
      <div class="venue-mini-text">
        <strong>${escapeHtml(info.label)}</strong>
        <span>${escapeHtml(detail)}</span>
      </div>
    </div>
  `;
}

function starPaperCandidate(row) {
  return {
    type: "star_paper",
    title: row.title,
    authors: row.authors,
    url: row.poster_url,
    source_url: row.openreview_url,
    code: row.position || "Poster",
    see: [row.time, row.session].filter(Boolean).join(" · "),
    where: row.room || "",
    facts: [row.oral ? "Oral" : row.spotlight ? "Spotlight" : ""].filter(Boolean),
    topics: [],
    score: starAuthorWeight(row),
  };
}

function starAuthorGroupList(block) {
  const groups = [];
  for (const candidate of block.candidates || []) {
    for (const author of starAuthors(candidate)) {
      let group = groups.find((item) => item.author.name === author.name);
      if (!group) {
        group = { author, papers: [] };
        groups.push(group);
      }
      if (!group.papers.some((paper) => paper.title === candidate.title)) group.papers.push(candidate);
    }
  }
  return `
    <div class="star-author-list">
      ${groups
        .sort((a, b) => b.author.weight - a.author.weight || b.papers.length - a.papers.length)
        .slice(0, 7)
        .map(
          (group) => `
            <section class="star-author-group">
              <header>
                <span class="star-author ${group.author.tier}">${escapeHtml(starAuthorDisplay(group.author))}</span>
                <em>${group.papers.length} paper${group.papers.length > 1 ? "s" : ""}</em>
              </header>
              <div class="star-author-papers">
                ${group.papers
                  .slice(0, 2)
                  .map(
                    (paper) => `
                      <a class="star-author-paper" href="${escapeHtml(paper.url || "#")}" target="_blank" rel="noreferrer">
                        <b>${escapeHtml(paper.code || "Poster")}</b>
                        <span>${escapeHtml(paper.title)}</span>
                        <small>${escapeHtml([paper.see, paper.where].filter(Boolean).join(" · "))}</small>
                      </a>
                    `,
                  )
                  .join("")}
              </div>
            </section>
          `,
        )
        .join("")}
    </div>
  `;
}

function starAuthorPaperBlock(date) {
  const selectedDates = date === "2026-07-10_11" ? ["2026-07-10", "2026-07-11"] : [date];
  const rows = selectedDates
    .flatMap((selectedDate) => state.starPapers[selectedDate]?.papers || [])
    .filter((row) => selectedDates.includes(row.date))
    .filter((row) => row.bucket === "现场可逛")
    .sort((a, b) => {
      const starDiff = Number(b.star_weight || starAuthorWeight(b)) - Number(a.star_weight || starAuthorWeight(a));
      if (starDiff) return starDiff;
      const flagDiff = Number(Boolean(b.oral)) - Number(Boolean(a.oral)) || Number(Boolean(b.spotlight)) - Number(Boolean(a.spotlight));
      if (flagDiff) return flagDiff;
      return `${a.time || "99:99"} ${a.position || ""}`.localeCompare(`${b.time || "99:99"} ${b.position || ""}`);
    })
    .slice(0, 18);
  if (!rows.length) return null;
  return {
    kind: "star_paper_slot",
    start: 9998,
    urgency: "Later",
    time: "Star radar",
    title: "Star author papers",
    candidates: rows.map(starPaperCandidate),
  };
}

function recheckTag(value) {
  return value === "yes" ? tag("需确认 / Recheck", "hot") : tag("OK", "ok");
}

function empty() {
  return $("#emptyTemplate").innerHTML;
}

function setHtml(selector, html) {
  $(selector).innerHTML = html || empty();
}

function updateClock() {
  const time = new Intl.DateTimeFormat("en-GB", {
    timeZone: "Asia/Seoul",
    hour: "2-digit",
    minute: "2-digit",
  }).format(new Date());
  $("#kstClock").textContent = time;
}

function motionOkay() {
  return !window.matchMedia("(prefers-reduced-motion: reduce)").matches;
}

function softReveal(root, selector = ".route-block") {
  if (!motionOkay()) return;
  const nodes = selector ? $$(selector, root).slice(0, 12) : [root];
  nodes.forEach((node, index) => {
    node.animate(
      [
        { opacity: 0, transform: "translateY(8px)" },
        { opacity: 1, transform: "translateY(0)" },
      ],
      {
        duration: 220,
        delay: Math.min(index * 28, 180),
        easing: "cubic-bezier(.2,.7,.2,1)",
        fill: "both",
      },
    );
  });
}

function showView(view, { updateHash = true } = {}) {
  state.activeView = view;
  $$(".view").forEach((node) => node.classList.toggle("is-active", node.dataset.view === view));
  $$(".view-tab").forEach((node) => node.classList.toggle("is-active", node.dataset.openView === view || (view === "today" && node.dataset.openView === "today")));
  $$(".nav-item[data-date]").forEach((node) => node.classList.toggle("is-active", node.dataset.date === state.selectedDate));
  $("#dateNav")?.classList.toggle("is-hidden", view !== "today");
  updateBottomNavIndicator();
  const targetHash = view === "today" ? `#${state.selectedDate}` : `#${view}`;
  if (updateHash && window.location.hash !== targetHash) {
    history.replaceState(null, "", targetHash);
  }
  window.scrollTo({ top: 0 });
  requestAnimationFrame(() => window.scrollTo({ top: 0 }));
  softReveal($(`.view[data-view="${view}"]`), null);
}

function updateBottomNavIndicator() {
  const nav = $("#dateNav");
  if (!nav) return;
  const active = $(".nav-item.is-active", nav);
  if (!active || nav.classList.contains("is-hidden")) {
    nav.classList.remove("has-active-indicator");
    return;
  }
  const navRect = nav.getBoundingClientRect();
  const activeRect = active.getBoundingClientRect();
  nav.style.setProperty("--active-x", `${activeRect.left - navRect.left}px`);
  nav.style.setProperty("--active-w", `${activeRect.width}px`);
  nav.classList.add("has-active-indicator");
}

function loadDeferredIframes(root = document) {
  $$("iframe[data-src]", root).forEach((frame) => {
    if (!frame.src) frame.src = frame.dataset.src;
  });
}

async function openView(view, options = {}) {
  showView(view, options);
  if (view === "schedule") await openSchedule();
  if (view === "map") {
    loadDeferredIframes($(`.view[data-view="${view}"]`));
    await renderRouteCards();
    renderNearby();
    renderEssentials();
  }
  if (view === "events") {
    await ensureEvents();
    renderEvents();
  }
}

function renderDateChips() {
  const dates = state.manifest.conference.nav_dates || state.manifest.conference.dates;
  state.selectedDate = state.selectedDate || selectDefaultDate(dates);
  $("#dateNav").innerHTML = dates
    .map(
      (date) => `
        <button class="nav-item ${date === state.selectedDate ? "is-active" : ""}" data-date="${date}" aria-label="${labelDate(date)}">
          <span>${compactDate(date)}</span>
          <b>${weekdayDate(date)}</b>
        </button>
      `,
    )
    .join("") + `
      <a class="nav-item nav-link" href="./travel.html" aria-label="Travel, routes, and map">
        <span>Map</span>
        <b>Travel</b>
      </a>
    `;
  $$("#dateNav .nav-item[data-date]").forEach((button) => {
    button.addEventListener("click", () => {
      state.selectedDate = button.dataset.date;
      renderDateChips();
      renderTodayRoute();
      void ensureGuidePlans(state.selectedDate).then(() => {
        if (state.activeView === "today") renderTodayRoute();
      });
      if (state.schedule) renderSchedule();
      if (state.papers) renderPaperFilters();
      showView("today");
    });
  });
  requestAnimationFrame(updateBottomNavIndicator);
}

function renderTodayRoute() {
  if (!state.companyEvents) {
    void ensureCompanyEventsData().then(() => {
      if (state.activeView === "today") renderTodayRoute();
    });
  }
  if (hasStarPapersForDate(state.selectedDate) && !state.starPapers[state.selectedDate]) {
    void ensureStarPaperData(state.selectedDate).then(() => {
      if (state.activeView === "today") renderTodayRoute();
    });
  }
  const plans = state.guidePlans[state.selectedDate];
  if (!plans) {
    setHtml("#routePickList", '<div class="empty-state"><strong>Loading day plan</strong><span>正在加载当天路线...</span></div>');
    return;
  }
  renderDailyFocus();
  const isHomeDay = state.selectedDate === "2026-07-06";
  const isToday = state.selectedDate === nowKstDate();
  const currentMinutes = isToday ? nowKstMinutes() : -1;
  const enriched = plans.map((row) => {
    const start = timelineSortValue(row);
    let urgency = "Later";
    if (start !== null && isToday) {
      if (start <= currentMinutes && currentMinutes <= start + 105) urgency = "Now";
      else if (start > currentMinutes && start <= currentMinutes + 180) urgency = "Next";
      else if (start < currentMinutes) urgency = "Passed";
    }
    return { ...row, start: start ?? 9999, urgency };
  });
  const usefulHomeCandidate = (block, candidate) => {
    if (!isHomeDay) return true;
    const title = String(candidate.title || "");
    if (block.kind === "onsite_slot") return false;
    if (candidate.type === "orientation") return false;
    if (/^Expo talks \/ demos \/ workshops$/i.test(title)) return false;
    return true;
  };
  const displayRows = enriched
    .filter((row) => row.kind !== "company_slot")
    .map((row) => ({ ...row, candidates: (row.candidates || []).filter((candidate) => usefulHomeCandidate(row, candidate)) }))
    .filter((row) => (row.candidates || []).length);
  const mergeEveningRows = (rows) => {
    const eveningRows = rows.filter((row) => row.kind === "evening_slot");
    if (eveningRows.length <= 1) return rows;
    const sideEvents = eveningRows.flatMap((row) => row.candidates || []).filter((candidate) => candidate.type === "side_event");
    const nonSideEvening = eveningRows.flatMap((row) => row.candidates || []).filter((candidate) => candidate.type !== "side_event");
    const nonEvening = rows.filter((row) => row.kind !== "evening_slot");
    if (!sideEvents.length) return rows;
    return [
      ...nonEvening,
      {
        ...eveningRows[0],
        start: Math.min(...eveningRows.map((row) => row.start)),
        time: "Evening",
        title: "Evening options",
        candidates: [...nonSideEvening, ...sideEvents],
      },
    ];
  };
  const starBlock = starAuthorPaperBlock(state.selectedDate);
  const groupedRows = starBlock ? [...mergeEveningRows(displayRows), starBlock] : mergeEveningRows(displayRows);
  const visible = groupedRows
    .filter((row) => row.urgency !== "Passed")
    .concat(groupedRows.filter((row) => row.urgency === "Passed").slice(-2))
    .sort((a, b) => {
      const kindWeight = { oral_slot: 0, poster_slot: 1, evening_slot: 2 };
      return a.start - b.start || (kindWeight[a.kind] ?? 9) - (kindWeight[b.kind] ?? 9) || a.title.localeCompare(b.title);
    });

  $("#selectedDayHeading").textContent = "";
  $("#selectedDayHeading").parentElement?.classList.add("is-empty");
  const routePickList = $("#routePickList");
  routePickList.classList.toggle("home-day-list", isHomeDay);
  routePickList.classList.toggle("workshop-day-list", state.selectedDate === "2026-07-10_11");
  const isStackedDay = ["2026-07-07", "2026-07-08", "2026-07-09"].includes(state.selectedDate);
  const blockLabel = (kind) => {
    if (kind === "oral_slot") return "Orals";
    if (kind === "poster_slot") return "Posters";
    if (kind === "star_paper_slot") return "Star authors";
    if (kind === "evening_slot") return "Evening options";
    if (kind === "company_slot") return "大厂线索";
    if (kind === "expo_slot") return "Expo / demos";
    if (kind === "official_slot") return "Venue activities";
    if (kind === "workshop_slot") return "Workshop";
    if (kind === "onsite_slot") return "First arrival";
    return "Options";
  };
  const isStackableBlock = (block) => {
    const count = dedupeByTitle(block.candidates || []).length;
    return isStackedDay && count > 1 && ["oral_slot", "poster_slot"].includes(block.kind);
  };
  const candidateListClass = (block) =>
    block.kind === "star_paper_slot" ? "candidate-list star-author-route-list" : `candidate-list${isStackableBlock(block) ? " stacked-cards" : ""}${block.kind === "evening_slot" ? " evening-list" : ""}`;
  const candidateListInner = (block) => {
    if (block.kind === "star_paper_slot") return starAuthorGroupList(block);
    const stackable = isStackableBlock(block);
    const candidates = dedupeByTitle(sortCandidates(block.candidates));
    const isEveningGroupCandidate = (candidate) => ["side_event", "official_social"].includes(candidate.type);
    const sideEvents = block.kind === "evening_slot" ? candidates.filter(isEveningGroupCandidate) : [];
    const otherCandidates = sideEvents.length ? candidates.filter((candidate) => !isEveningGroupCandidate(candidate)) : candidates;
    const sideEventGroups = sideEvents.reduce((groups, candidate) => {
      const category = sideEventCategory(candidate);
      if (!groups.has(category)) groups.set(category, []);
      groups.get(category).push(candidate);
      return groups;
    }, new Map());
    const categoryOrder = ["Dinner", "Cafe / coworking", "Evening social", "Meetup / networking", "Workshop / summit", "Other side events"];
    const cards = [
      ...otherCandidates.map((candidate) => candidateCard(candidate, block, { stackable })),
      ...categoryOrder.flatMap((category) => (sideEventGroups.has(category) ? [meetupListCard(sideEventGroups.get(category), category)] : [])),
    ].join("");
    return cards;
  };
  setHtml(
    "#routePickList",
    visible
      .map(
        (block) => `
          <article class="route-block">
            <header class="route-block-head">
              <h4>${escapeHtml(block.time)} · ${escapeHtml(blockLabel(block.kind))}</h4>
            </header>
            <div class="${candidateListClass(block)}">
              ${candidateListInner(block)}
            </div>
          </article>
        `,
      )
      .join("") + companyDayBlock(state.selectedDate),
  );
  softReveal($("#routePickList"));
}

async function ensureSchedule() {
  if (!state.schedule) state.schedule = await loadJson("schedule");
}

function ensureScheduleDate() {
  const selectedDates = state.selectedDate === "2026-07-10_11" ? ["2026-07-10", "2026-07-11"] : [state.selectedDate];
  if (state.schedule.sessions.some((row) => selectedDates.includes(row.date))) return;
  const firstDate = state.schedule.sessions.find((row) => row.date)?.date;
  if (firstDate) state.selectedDate = firstDate;
}

function renderScheduleFilters() {
  const types = ["all", ...new Set(state.schedule.sessions.map((row) => row.type))];
  $("#scheduleFilters").innerHTML = types
    .map((type) => `<button class="seg ${type === state.scheduleType ? "is-active" : ""}" data-type="${escapeHtml(type)}">${escapeHtml(type === "all" ? "All" : type.replace(" Session", ""))}</button>`)
    .join("");
  $$("#scheduleFilters .seg").forEach((button) => {
    button.addEventListener("click", () => {
      state.scheduleType = button.dataset.type;
      renderSchedule();
    });
  });
}

function renderSchedule() {
  renderScheduleFilters();
  const selectedDates = state.selectedDate === "2026-07-10_11" ? ["2026-07-10", "2026-07-11"] : [state.selectedDate];
  const rows = state.schedule.sessions
    .filter((row) => selectedDates.includes(row.date))
    .filter((row) => state.scheduleType === "all" || row.type === state.scheduleType)
    .sort((a, b) => a.date.localeCompare(b.date) || a.start.localeCompare(b.start));

  setHtml(
    "#scheduleList",
    rows
      .map(
        (row) => `
          <article class="timeline-item">
            <div class="time-cell">${escapeHtml(row.time)}</div>
            <div>
              <div class="meta-row">${tag(row.type)}${tag(row.room)}</div>
              <h4>${escapeHtml(row.title)}</h4>
              <p>${row.item_count ? `${row.item_count} items · showing first ${row.items.length}` : "Session page"}</p>
              ${
                row.items.length
                  ? `<div class="stack compact">${row.items
                      .slice(0, 3)
                      .map((item) => `<p><b>${escapeHtml(item.time)}</b> ${escapeHtml(item.title)}</p>`)
                      .join("")}</div>`
                  : ""
              }
              <div class="actions">${action(row.url, "Open ICML")}</div>
            </div>
          </article>
        `,
      )
      .join(""),
  );
}

async function openSchedule() {
  await ensureSchedule();
  ensureScheduleDate();
  renderDateChips();
  renderSchedule();
}

async function ensurePapers() {
  if (!state.papers) {
    $("#loadPapersButton").textContent = "Loading...";
  }
  await ensurePaperData();
  $("#loadPapersButton").textContent = "Refresh filters";
  renderPaperFilters();
}

function renderPaperFilters() {
  const topics = Object.keys(state.papers.topic_routes);
  const topicSelect = $("#topicFilter");
  if (topicSelect.options.length <= 1) {
    topicSelect.insertAdjacentHTML(
      "beforeend",
      topics.map((topic) => `<option value="${escapeHtml(topic)}">${escapeHtml(topic)}</option>`).join(""),
    );
  }
  const daySelect = $("#paperDayFilter");
  if (daySelect.options.length <= 1) {
    daySelect.insertAdjacentHTML(
      "beforeend",
      state.manifest.conference.dates.map((date) => `<option value="${date}">${labelDate(date)}</option>`).join(""),
    );
  }
  if (!daySelect.value) {
    const paperDates = new Set(state.papers.papers.map((row) => row.date).filter(Boolean));
    daySelect.value = paperDates.has(state.selectedDate) ? state.selectedDate : "";
  }
  renderTopicRoutes();
  renderPaperList();
}

function renderTopicRoutes() {
  const topic = $("#topicFilter").value;
  const selectedDay = $("#paperDayFilter").value || state.selectedDate;
  const entries = topic ? [[topic, state.papers.topic_routes[topic] || []]] : Object.entries(state.papers.topic_routes);
  $("#topicRouteCount").textContent = `${entries.length} topics`;
  setHtml(
    "#topicRoutes",
    entries
      .slice(0, 18)
      .map(([name, routes]) => {
        const topRoutes = routes
          .slice()
          .sort((a, b) => {
            const dayA = a.date === selectedDay ? 0 : 1;
            const dayB = b.date === selectedDay ? 0 : 1;
            return dayA - dayB || a.time.localeCompare(b.time) || b.papers - a.papers;
          })
          .slice(0, 4);
        return `
          <details class="topic-block" ${topic ? "open" : ""}>
            <summary>
              <strong>${escapeHtml(name)}</strong>
              <span class="status-pill">${routes.reduce((sum, row) => sum + row.papers, 0)} papers</span>
            </summary>
            <div class="route-sessions">
              ${topRoutes
                .map(
                  (row) => `
                    <article class="route-card">
                      <div class="meta-row">${tag(row.date)}${tag(row.time)}${tag(row.room)}</div>
                      <h4>${escapeHtml(row.session)}</h4>
                      <p>${row.papers} papers · ${row.spotlight} spotlight · ${row.oral} oral-linked</p>
                      <div class="actions">${action(row.url, "Open session")}</div>
                    </article>
                  `,
                )
                .join("")}
            </div>
          </details>
        `;
      })
      .join(""),
  );
}

function renderPaperList() {
  const topic = $("#topicFilter").value;
  const day = $("#paperDayFilter").value;
  const badge = $("#paperBadgeFilter").value;
  let rows = state.papers.papers;
  if (topic) rows = rows.filter((row) => row.tracks.includes(topic));
  if (day) rows = rows.filter((row) => row.date === day);
  if (badge === "oral") rows = rows.filter((row) => row.oral);
  if (badge === "spotlight") rows = rows.filter((row) => row.spotlight);
  if (badge === "extra") rows = rows.filter((row) => row.bucket !== "现场可逛");
  if (badge === "stars") rows = rows.filter((row) => row.bucket === "现场可逛" && starAuthorWeight(row));

  rows = rows.slice().sort((a, b) => {
    const starDiff = starAuthorWeight(b) - starAuthorWeight(a);
    if (starDiff) return starDiff;
    const flagDiff = Number(Boolean(b.oral)) - Number(Boolean(a.oral)) || Number(Boolean(b.spotlight)) - Number(Boolean(a.spotlight));
    if (flagDiff) return flagDiff;
    return `${a.date || "9999"} ${a.time || "99:99"} ${a.position || ""}`.localeCompare(`${b.date || "9999"} ${b.time || "99:99"} ${b.position || ""}`);
  });

  $("#paperCount").textContent = `${rows.length.toLocaleString()} matches · showing 80`;
  setHtml(
    "#paperList",
    rows
      .slice(0, 80)
      .map(
        (row) => `
          <article class="paper-card">
            <div class="meta-row">
              ${row.oral ? tag("Oral", "oral") : row.spotlight ? tag("Spotlight", "hot") : ""}
              ${row.bucket !== "现场可逛" ? tag("Extra attention") : tag(row.position || "Poster", "ok")}
            </div>
            <h4>${escapeHtml(row.title)}${starAuthorTrail(row)}</h4>
            <p>${escapeHtml(row.authors)}</p>
            <p>${escapeHtml([row.date, row.time, row.session, row.room].filter(Boolean).join(" · "))}</p>
            <p>${escapeHtml(row.tracks)}</p>
            <div class="actions">${action(row.poster_url, "Open ICML")}${action(row.openreview_url, "OpenReview")}</div>
          </article>
        `,
      )
      .join(""),
  );
}

async function ensureEvents() {
  if (!state.events) state.events = await loadJson("events");
}

function renderEvents() {
  $$(".seg[data-event-kind]").forEach((node) => node.classList.toggle("is-active", node.dataset.eventKind === state.eventMode));
  const rows = state.eventMode === "official" ? state.events.opportunities : state.events.side_events.filter((row) => row.date >= "2026-07-06" && row.date <= "2026-07-11");
  renderEventWatch();
  setHtml(
    "#eventList",
    rows
      .map((row) => {
        const isOfficial = state.eventMode === "official";
        const title = row.name || row.title;
        const meta = isOfficial
          ? [row.opportunity_type, row.date_time_kst, row.location]
          : [compactDate(row.date), row.time, row.kind, row.region || row.location || "After RSVP"];
        const sourceUrl = row.source_url && row.source_url !== row.url ? row.source_url : "";
        return `
          <article class="event-card ${isOfficial ? "" : "side-event-card"}">
            <div class="meta-row">${tag(isOfficial ? "Official" : "Side event", isOfficial ? "ok" : "")}${tag(row.priority || row.confidence || "Check", row.priority === "P0" ? "hot" : "")}</div>
            <h4>${escapeHtml(title)}</h4>
            <p>${escapeHtml(meta.filter(Boolean).join(" · "))}</p>
            ${isOfficial ? `<p>${escapeHtml(row.guide_use_zh || row.notes || "")}</p>` : `<p>${escapeHtml([row.organizer, row.platform, row.ticket ? readableTicket(row.ticket) : ""].filter(Boolean).join(" · "))}</p>`}
            <div class="actions">${action(row.url || row.source_url, isOfficial ? "Open ICML" : "RSVP")}${sourceUrl ? action(sourceUrl, "Source") : ""}</div>
          </article>
        `;
      })
      .join(""),
  );
}

function renderEventWatch() {
  const confirmed = (state.events.side_events || [])
    .filter((row) => row.date >= "2026-07-06" && row.date <= "2026-07-11")
    .filter((row) => /manual_verified|detail_page/.test(row.confidence || ""))
    .slice(0, 8);
  const watch = state.events.unconfirmed_watch || [];
  if (state.eventMode !== "side") {
    $("#eventWatchList").innerHTML = "";
    return;
  }
  setHtml(
    "#eventWatchList",
    `
      <div class="watch-section">
        <h3>Confirmed vendor-side events / 已核实厂商活动</h3>
        <div class="watch-grid">
          ${confirmed
            .map(
              (row) => `
                <article>
                  <b>${escapeHtml(row.title)}</b>
                  <span>${escapeHtml([compactDate(row.date), row.time, row.organizer].filter(Boolean).join(" · "))}</span>
                </article>
              `,
            )
            .join("")}
        </div>
      </div>
      <div class="watch-section muted-watch">
        <h3>Unconfirmed company watch / 未确认大厂线索</h3>
        <div class="watch-grid">
          ${watch
            .map(
              (row) => `
                <article>
                  <b>${escapeHtml(row.company)}</b>
                  <span>${escapeHtml(row.status)}</span>
                  <em>${escapeHtml(row.note)}</em>
                </article>
              `,
            )
            .join("")}
        </div>
      </div>
    `,
  );
}

function readableTicket(value = "") {
  if (!value) return "";
  return value.replace("https://schema.org/", "").replace("http://schema.org/", "");
}

async function ensureEssentials() {
  if (!state.essentials) state.essentials = await loadJson("essentials");
}

function renderEssentialFilters() {
  const labels = {
    within_5_min: "5 min / 会场内外",
    arrival_first: "Arrival / 落地",
    evening_or_rain_backup: "Evening / 雨天晚饭",
  };
  $("#essentialFilters").innerHTML = Object.entries(labels)
    .map(([key, label]) => `<button class="seg ${key === state.essentialCategory ? "is-active" : ""}" data-category="${key}">${label}</button>`)
    .join("");
  $$("#essentialFilters .seg").forEach((button) => {
    button.addEventListener("click", () => {
      state.essentialCategory = button.dataset.category;
      renderEssentials();
    });
  });
}

function renderEssentials() {
  renderEssentialFilters();
  const rows = state.essentials.local.filter((row) => row.category === state.essentialCategory);
  setHtml(
    "#essentialList",
    rows
      .map(
        (row) => `
          <article class="info-card">
            <div class="meta-row">${tag(row.guide_use_en)}${recheckTag(row.needs_recheck)}</div>
            <h4>${escapeHtml(row.name_zh)} / ${escapeHtml(row.name_en)}${row.korean_note ? ` (${escapeHtml(row.korean_note)})` : ""}</h4>
            <p>${escapeHtml(row.hours_or_timing)} · ${escapeHtml(row.location_en)}</p>
            <p>${escapeHtml(row.why_zh)}</p>
            <div class="actions">${action(row.source_url, "Source")}</div>
          </article>
        `,
      )
      .join(""),
  );

}

async function renderRouteCards() {
  await ensureEssentials();
  setHtml(
    "#routeCards",
    state.essentials.routes
      .slice(0, 8)
      .map(
        (row) => `
          <article class="route-card">
            <div class="meta-row">${tag(row.group)}${tag(row.travelmode)}</div>
            <h4>${escapeHtml(row.name)}</h4>
            <p>${escapeHtml(row.origin)} → ${escapeHtml(row.destination)}</p>
            <p>${escapeHtml(row.why || row.notes)}</p>
            <div class="actions">${action(row.google_maps_directions_url, "Open Google Maps")}</div>
          </article>
        `,
      )
      .join(""),
  );
}

function renderNearby() {
  const rows = (state.essentials.nearby || []).slice(0, 12);
  setHtml(
    "#nearbyList",
    rows
      .map(
        (row) => `
          <article class="route-card">
            <div class="meta-row">${tag(row.zone)}${tag(row.kind)}</div>
            <h4>${escapeHtml(row.name)}</h4>
            <p>${escapeHtml(row.when_to_go)} · ${escapeHtml(row.from_coex)}</p>
            <p>${escapeHtml(row.notes)}</p>
            <div class="actions">${action(row.google_maps_directions_url, "Route")}${action(row.source, "Source")}</div>
          </article>
        `,
      )
      .join(""),
  );
}

async function ensureSearch() {
  if (!state.search) state.search = await loadJson("search");
}

async function runSearch(query) {
  if (!query.trim()) {
    if (state.activeView === "search") showView("today");
    return;
  }
  await ensureSearch();
  showView("search");
  const terms = query.toLowerCase().split(/\s+/).filter(Boolean);
  const rows = state.search
    .filter((row) => {
      const body = `${row.title} ${row.subtitle} ${row.keywords}`.toLowerCase();
      return terms.every((term) => body.includes(term));
    })
    .slice(0, 80);

  setHtml(
    "#searchResults",
    rows
      .map(
        (row) => `
          <article class="search-card">
            <div class="meta-row">${tag(row.type)}</div>
            <h4>${escapeHtml(row.title)}</h4>
            <p>${escapeHtml(row.subtitle)}</p>
            <div class="actions">${action(row.url, "Open")}</div>
          </article>
        `,
      )
      .join(""),
  );
}

function bindEvents() {
  $$(".nav-item[data-target]").forEach((button) => {
    button.addEventListener("click", async () => {
      await openView(button.dataset.target);
    });
  });

  $$("[data-open-section]").forEach((button) => {
    button.addEventListener("click", () => openView(button.dataset.openSection));
  });

  $$("[data-open-view]").forEach((button) => {
    button.addEventListener("click", () => openView(button.dataset.openView));
  });

  $("#loadPapersButton").addEventListener("click", ensurePapers);
  $("#topicFilter").addEventListener("change", () => {
    renderTopicRoutes();
    renderPaperList();
  });
  $("#paperDayFilter").addEventListener("change", renderPaperList);
  $("#paperBadgeFilter").addEventListener("change", renderPaperList);

  $$(".seg[data-event-kind]").forEach((button) => {
    button.addEventListener("click", () => {
      state.eventMode = button.dataset.eventKind;
      renderEvents();
    });
  });

  window.addEventListener("resize", () => requestAnimationFrame(updateBottomNavIndicator), { passive: true });
  window.addEventListener("orientationchange", () => setTimeout(updateBottomNavIndicator, 220), { passive: true });
}

async function init() {
  updateClock();
  setInterval(updateClock, 30_000);

  const manifest = await loadJson("manifest");
  state.manifest = manifest;
  const initialView = window.location.hash.replace("#", "");
  const navDates = manifest.conference.nav_dates || manifest.conference.dates;
  const initialDate = initialView === "2026-07-10" || initialView === "2026-07-11" ? "2026-07-10_11" : initialView;
  const isDateEntry = navDates.includes(initialDate);
  const isViewEntry = Boolean($(`.view[data-view="${initialView}"]`));
  const shouldRenderToday = isDateEntry || !isViewEntry;
  state.selectedDate = isDateEntry ? initialDate : selectDefaultDate(navDates);

  if (shouldRenderToday) {
    await ensureGuidePlans(state.selectedDate);
  }

  renderDateChips();
  if (shouldRenderToday) renderTodayRoute();
  bindEvents();

  if (navDates.includes(initialDate)) {
    showView("today", { updateHash: false });
  } else if (initialView === "essentials") {
    await openView("map", { updateHash: false });
  } else if ($(`.view[data-view="${initialView}"]`)) {
    await openView(initialView, { updateHash: false });
  }
}

init().catch((error) => {
  console.error(error);
  document.body.insertAdjacentHTML(
    "afterbegin",
    `<div class="panel"><strong>Failed to load guide data.</strong><p>${escapeHtml(error.message)}</p></div>`,
  );
});
