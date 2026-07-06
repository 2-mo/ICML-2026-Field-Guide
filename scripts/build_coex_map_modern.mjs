#!/usr/bin/env node
import { mkdir, readFile, writeFile } from "node:fs/promises";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const sourcePath = resolve(ROOT, "data/maps/coex_map.svg");
const dataOutputPath = resolve(ROOT, "data/maps/coex_map_modern.html");
const docsOutputPath = resolve(ROOT, "docs/maps/coex_map_modern.html");

const modernDefs = `
    <linearGradient id="modernHallA" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#b7e4de" />
      <stop offset="100%" stop-color="#72c8c0" />
    </linearGradient>
    <linearGradient id="modernHallC" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#d2ecff" />
      <stop offset="100%" stop-color="#86c5f4" />
    </linearGradient>
    <linearGradient id="modernHallB" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#ffe2d5" />
      <stop offset="100%" stop-color="#ffc2ad" />
    </linearGradient>
    <linearGradient id="modernHallD" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#ffe7b8" />
      <stop offset="100%" stop-color="#f7cc76" />
    </linearGradient>
    <linearGradient id="modernRoom" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#d7def8" />
      <stop offset="100%" stop-color="#aab8ef" />
    </linearGradient>
    <linearGradient id="modernBallroom" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#ddd5ff" />
      <stop offset="100%" stop-color="#b9a8f7" />
    </linearGradient>
    <linearGradient id="modernMall" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#2f3337" />
      <stop offset="100%" stop-color="#14171a" />
    </linearGradient>
    <filter id="modernRoomGlow" x="-10%" y="-18%" width="120%" height="136%">
      <feDropShadow dx="0" dy="9" stdDeviation="10" flood-color="#0066cc" flood-opacity="0.18" />
    </filter>`;

function inlineSvg(svg) {
  return svg
    .replace(/^<\?xml[^>]*>\s*/u, "")
    .replace(
      /<svg\b/u,
      '<svg class="venue-svg" preserveAspectRatio="xMidYMid meet"',
    )
    .replace(/\s+width="1920"/u, ' width="100%"')
    .replace(/\s+height="900"/u, ' height="100%"')
    .replace(/(<defs\s+id="defs154">)/u, `$1${modernDefs}`);
}

function page(svg) {
  return `<!doctype html>
<html lang="zh-CN">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover" />
    <meta name="theme-color" content="#f5f5f7" />
    <meta
      name="description"
      content="A modern HTML presentation of the official ICML 2026 COEX venue map, preserving the original venue content."
    />
    <title>ICML 2026 COEX Venue Map</title>
    <style>
      :root {
        --paper: #f5f5f7;
        --paper-soft: #ffffff;
        --ink: #1d1d1f;
        --muted: #6e6e73;
        --line: rgba(0, 0, 0, 0.1);
        --line-strong: rgba(0, 0, 0, 0.18);
        --blue: #007aff;
        --teal: #00a6a6;
        --green: #30d158;
        --orange: #ff9f0a;
        --purple: #8e8df6;
        --mall: #1d1d1f;
        --station-green: #00a86b;
        --station-gold: #c78b00;
        --shadow: 0 18px 42px rgba(0, 0, 0, 0.08);
        --radius: 18px;
        color-scheme: light;
      }

      * {
        box-sizing: border-box;
      }

      html {
        min-height: 100%;
      }

      body {
        min-height: 100%;
        margin: 0;
        background:
          radial-gradient(circle at 18% -10%, rgba(0, 122, 255, 0.12), transparent 30%),
          radial-gradient(circle at 90% 0%, rgba(48, 209, 88, 0.1), transparent 26%),
          var(--paper);
        color: var(--ink);
        font-family: -apple-system, BlinkMacSystemFont, "SF Pro Text", "SF Pro Display", "Helvetica Neue", "PingFang SC", "Noto Sans CJK SC", sans-serif;
        letter-spacing: 0;
      }

      a {
        color: inherit;
      }

      button {
        font: inherit;
      }

      .page {
        display: grid;
        grid-template-columns: minmax(0, 1fr);
        gap: 12px;
        min-height: 100svh;
        padding: 18px;
      }

      .page > * {
        min-width: 0;
      }

      .map-shell {
        display: block;
        width: 100%;
        min-width: 0;
      }

      .masthead {
        display: flex;
        align-items: flex-end;
        justify-content: space-between;
        gap: 16px;
      }

      .eyebrow {
        margin: 0 0 4px;
        color: var(--muted);
        font-size: 0.68rem;
        font-weight: 700;
        letter-spacing: 0.08em;
        text-transform: uppercase;
      }

      h1,
      h2,
      h3,
      p {
        margin: 0;
      }

      h1 {
        max-width: 840px;
        font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", "Helvetica Neue", "PingFang SC", sans-serif;
        font-size: clamp(1.8rem, 3.2vw, 3.15rem);
        font-weight: 700;
        line-height: 1;
        letter-spacing: 0;
      }

      .dek {
        max-width: 720px;
        margin-top: 5px;
        color: var(--muted);
        font-size: 0.9rem;
        font-weight: 500;
        line-height: 1.35;
      }

      .toolbar {
        display: flex;
        align-items: center;
        justify-content: flex-end;
        gap: 7px;
        flex: 0 0 auto;
      }

      .icon-button,
      .plain-link {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        min-height: 38px;
        border: 1px solid var(--line-strong);
        border-radius: 999px;
        background: rgba(255, 255, 255, 0.72);
        color: var(--ink);
        font-weight: 700;
        text-decoration: none;
        box-shadow: 0 6px 16px rgba(0, 0, 0, 0.05);
        backdrop-filter: blur(18px);
      }

      .icon-button {
        width: 38px;
        padding: 0;
        cursor: pointer;
      }

      .plain-link {
        padding: 0 11px;
        font-size: 0.78rem;
        white-space: nowrap;
      }

      .icon-button:hover,
      .plain-link:hover,
      .legend-item:hover {
        border-color: rgba(0, 122, 255, 0.45);
        background: rgba(255, 255, 255, 0.92);
      }

      .stage {
        position: relative;
        display: block;
        min-height: 0;
        min-width: 0;
        margin-top: 10px;
        overflow: auto;
        border: 1px solid var(--line);
        border-radius: var(--radius);
        background: rgba(255, 255, 255, 0.78);
        box-shadow: var(--shadow);
        backdrop-filter: blur(22px);
        -webkit-overflow-scrolling: touch;
      }

      .stage::before {
        position: sticky;
        top: 0;
        left: 0;
        display: block;
        width: 100%;
        height: 0;
        border-top: 1px solid rgba(255, 255, 255, 0.86);
        content: "";
        z-index: 2;
      }

      .map-artboard {
        position: relative;
        width: var(--zoom, 100%);
        min-width: 0;
        max-width: 100%;
        aspect-ratio: 1920 / 900;
        margin: 0 auto;
        padding: 8px;
        transition: width 160ms ease;
      }

      .map-artboard.is-zoomed {
        max-width: none;
      }

      .map-artboard svg {
        display: block;
        position: absolute;
        inset: 8px;
        width: calc(100% - 16px) !important;
        height: calc(100% - 16px) !important;
        overflow: visible;
      }

      .map-artboard svg #rect156 {
        fill: transparent !important;
      }

      .map-artboard svg text,
      .map-artboard svg tspan {
        font-family: -apple-system, BlinkMacSystemFont, "SF Pro Text", "Helvetica Neue", "PingFang SC", "Noto Sans CJK SC", sans-serif !important;
        letter-spacing: 0 !important;
        paint-order: stroke fill;
      }

      .map-artboard svg text[fill="#111"],
      .map-artboard svg text[fill="#333"],
      .map-artboard svg text[fill="#d0a000"],
      .map-artboard svg text[fill="#24a020"] {
        fill: #1d1d1f !important;
        stroke: rgba(255, 255, 255, 0.72);
        stroke-linejoin: round;
        stroke-width: 2.2px;
      }

      .map-artboard svg text[fill="#fff"],
      .map-artboard svg text[fill="#ffffff"] {
        fill: #1d1d1f !important;
        stroke: rgba(255, 255, 255, 0.68);
        stroke-linejoin: round;
        stroke-width: 1.8px;
      }

      .map-artboard svg #rect226 {
        fill: url("#modernHallC") !important;
      }

      .map-artboard svg #rect228 {
        fill: url("#modernHallA") !important;
      }

      .map-artboard svg #rect236 {
        fill: url("#modernHallD") !important;
      }

      .map-artboard svg #rect238 {
        fill: url("#modernHallB") !important;
      }

      .map-artboard svg #rect216,
      .map-artboard svg #rect218,
      .map-artboard svg #rect230 {
        fill: url("#modernRoom") !important;
      }

      .map-artboard svg #rect240,
      .map-artboard svg #rect242,
      .map-artboard svg #rect244 {
        fill: url("#modernBallroom") !important;
      }

      .map-artboard svg #rect220,
      .map-artboard svg #rect222,
      .map-artboard svg #rect224,
      .map-artboard svg #rect232,
      .map-artboard svg #rect234 {
        fill: #f1f2f6 !important;
        opacity: 0.96;
      }

      .map-artboard svg #rect216,
      .map-artboard svg #rect218,
      .map-artboard svg #rect220,
      .map-artboard svg #rect222,
      .map-artboard svg #rect224,
      .map-artboard svg #rect226,
      .map-artboard svg #rect228,
      .map-artboard svg #rect230,
      .map-artboard svg #rect232,
      .map-artboard svg #rect234,
      .map-artboard svg #rect236,
      .map-artboard svg #rect238,
      .map-artboard svg #rect240,
      .map-artboard svg #rect242,
      .map-artboard svg #rect244 {
        stroke: rgba(255, 255, 255, 0.88) !important;
        stroke-width: 3px !important;
        transition: opacity 160ms ease, filter 160ms ease, stroke 160ms ease;
      }

      .map-artboard svg #polygon320 {
        fill: url("#modernMall") !important;
        stroke: rgba(0, 0, 0, 0.18) !important;
      }

      .map-artboard svg #polygon324 {
        fill: #edf0f3 !important;
        opacity: 1 !important;
      }

      .map-artboard svg #line326 {
        stroke: #ffcc00 !important;
        stroke-width: 4px !important;
      }

      .map-artboard svg #path149 {
        fill: var(--ink) !important;
      }

      .map-artboard svg #line158,
      .map-artboard svg #line172,
      .map-artboard svg #line186,
      .map-artboard svg #path344 {
        stroke: var(--ink) !important;
      }

      .map-artboard svg #path196,
      .map-artboard svg #line198,
      .map-artboard svg #line200,
      .map-artboard svg #line202,
      .map-artboard svg #line204,
      .map-artboard svg #line206,
      .map-artboard svg #line208,
      .map-artboard svg #path210,
      .map-artboard svg #path212,
      .map-artboard svg #path214 {
        stroke: #9aa0a6 !important;
      }

      .map-artboard svg #line300,
      .map-artboard svg #line304,
      .map-artboard svg #line308,
      .map-artboard svg #line312,
      .map-artboard svg #line316 {
        stroke: #c7c7cc !important;
        stroke-dasharray: 10 8;
      }

      .map-artboard svg #text302,
      .map-artboard svg #text306,
      .map-artboard svg #text310,
      .map-artboard svg #text314,
      .map-artboard svg #text318 {
        fill: var(--ink) !important;
      }

      .map-artboard svg #text332,
      .map-artboard svg #text334,
      .map-artboard svg #text336 {
        fill: var(--station-green) !important;
      }

      .map-artboard svg #text338,
      .map-artboard svg #text340,
      .map-artboard svg #text342 {
        fill: var(--station-gold) !important;
      }

      .map-artboard svg #text322 {
        fill: #ffffff !important;
        stroke: rgba(0, 0, 0, 0.18) !important;
        stroke-width: 1px !important;
      }

      .map-artboard svg .is-dim {
        opacity: 0.36;
      }

      .map-artboard svg .is-highlight {
        filter: url("#modernRoomGlow");
        opacity: 1;
        stroke: #ffffff !important;
        stroke-width: 6px !important;
      }

      .side-panel {
        display: grid;
        grid-template-columns: minmax(0, 1.2fr) minmax(260px, 0.8fr);
        gap: 10px;
        overflow: hidden;
      }

      .info-block {
        border: 1px solid var(--line);
        border-radius: 16px;
        background: rgba(255, 255, 255, 0.72);
        box-shadow: 0 10px 24px rgba(0, 0, 0, 0.045);
        backdrop-filter: blur(22px);
      }

      .info-block header {
        padding: 10px 12px 0;
      }

      .info-block h2 {
        font-size: 0.9rem;
        font-weight: 700;
        line-height: 1.15;
      }

      .legend-list,
      .anchor-list {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
        gap: 7px;
        max-width: 100%;
        overflow: hidden;
        padding: 10px 12px 12px;
        scrollbar-width: none;
      }

      .legend-list::-webkit-scrollbar,
      .anchor-list::-webkit-scrollbar {
        display: none;
      }

      .legend-item {
        display: flex;
        grid-template-columns: 18px minmax(0, 1fr);
        align-items: center;
        gap: 9px;
        min-width: 0;
        min-height: 40px;
        padding: 7px 8px;
        border: 1px solid var(--line);
        border-radius: 13px;
        background: rgba(255, 255, 255, 0.62);
        color: var(--ink);
        text-align: left;
        cursor: pointer;
      }

      .legend-item strong,
      .anchor-item strong {
        display: block;
        font-size: 0.8rem;
        line-height: 1.1;
      }

      .legend-item span:last-child,
      .anchor-item span {
        display: block;
        margin-top: 2px;
        color: var(--muted);
        font-size: 0.68rem;
        font-weight: 600;
        line-height: 1.15;
      }

      .swatch {
        width: 18px;
        height: 18px;
        border: 1px solid rgba(24, 32, 36, 0.16);
        border-radius: 6px;
      }

      .swatch.poster {
        background: linear-gradient(135deg, #b7e4de, #72c8c0);
      }

      .swatch.oral {
        background: linear-gradient(135deg, #ffe0a8, #f3bd59);
      }

      .swatch.rooms {
        background: linear-gradient(135deg, #d7def8, #aab8ef);
      }

      .swatch.ballroom {
        background: linear-gradient(135deg, #ddd5ff, #b9a8f7);
      }

      .swatch.mall {
        background: linear-gradient(135deg, #303a3e, #151c20);
      }

      .anchor-item {
        min-width: 0;
        padding: 9px 10px;
        border-left: 3px solid var(--line-strong);
        border-radius: 10px;
        background: rgba(255, 255, 255, 0.5);
      }

      .anchor-item:nth-child(1) {
        border-left-color: var(--teal);
      }

      .anchor-item:nth-child(2) {
        border-left-color: var(--orange);
      }

      .anchor-item:nth-child(3) {
        border-left-color: var(--blue);
      }

      .anchor-item:nth-child(4) {
        border-left-color: var(--purple);
      }

      .source-note {
        padding: 0 12px 12px;
        color: var(--muted);
        font-size: 0.68rem;
        font-weight: 600;
        line-height: 1.35;
        overflow-wrap: anywhere;
      }

      .source-note .long-source {
        display: inline;
      }

      @media (max-width: 980px) {
        .page {
          padding: 10px;
        }

        .masthead {
          display: grid;
          gap: 9px;
        }

        .toolbar {
          justify-content: flex-start;
          overflow-x: auto;
          padding-bottom: 2px;
        }

        .stage {
          min-height: 0;
          height: auto;
        }

        .map-artboard {
          min-width: 0;
          padding: 6px;
        }

        .side-panel {
          grid-template-columns: 1fr;
        }

        .legend-list,
        .anchor-list {
          grid-template-columns: repeat(2, minmax(0, 1fr));
        }
      }

      @media (max-width: 560px) {
        h1 {
          font-size: 1.72rem;
        }

        .plain-link {
          min-height: 36px;
          padding: 0 9px;
        }

        .stage {
          min-height: 0;
        }

        .map-artboard {
          min-width: 0;
        }
      }

      body.is-embed {
        overflow: hidden;
        background: #ffffff;
      }

      body.is-embed .page {
        display: block;
        min-height: 100svh;
        padding: 0;
      }

      body.is-embed .masthead,
      body.is-embed .side-panel {
        display: none;
      }

      body.is-embed .map-shell {
        display: block;
      }

      body.is-embed .stage {
        width: 100%;
        height: 100svh;
        min-height: 0;
        border: 0;
        border-radius: 0;
        box-shadow: none;
      }

      body.is-embed .map-artboard {
        min-width: 0;
        padding: 6px;
      }
    </style>
  </head>
  <body>
    <main class="page">
      <section class="map-shell" aria-label="Modernized ICML 2026 COEX venue map">
        <header class="masthead">
          <div>
            <p class="eyebrow">ICML 2026 / Seoul COEX</p>
            <h1>COEX Venue Map</h1>
            <p class="dek">官方地图内容保持不变，只重做配色、层次和导览呈现。</p>
          </div>
          <nav class="toolbar" aria-label="Map actions">
            <button class="icon-button" type="button" data-zoom-step="-12" aria-label="Zoom out" title="Zoom out">−</button>
            <button class="icon-button" type="button" data-zoom-reset aria-label="Reset zoom" title="Reset zoom">100</button>
            <button class="icon-button" type="button" data-zoom-step="12" aria-label="Zoom in" title="Zoom in">+</button>
            <a class="plain-link" href="./coex_map.svg" target="_blank" rel="noreferrer">Official SVG</a>
            <a class="plain-link" href="../index.html">Guide</a>
          </nav>
        </header>
        <div class="stage" tabindex="0">
          <div class="map-artboard">
${svg}
          </div>
        </div>
      </section>

      <aside class="side-panel" aria-label="Map legend and venue anchors">
        <section class="info-block">
          <header>
            <p class="eyebrow">Legend</p>
            <h2>Venue layers</h2>
          </header>
          <div class="legend-list">
            <button class="legend-item" type="button" data-highlight="poster">
              <span class="swatch poster" aria-hidden="true"></span>
              <span><strong>Poster halls</strong><span>Hall A / Hall C</span></span>
            </button>
            <button class="legend-item" type="button" data-highlight="oral">
              <span class="swatch oral" aria-hidden="true"></span>
              <span><strong>Oral halls</strong><span>Hall B / Hall D</span></span>
            </button>
            <button class="legend-item" type="button" data-highlight="rooms">
              <span class="swatch rooms" aria-hidden="true"></span>
              <span><strong>Conference rooms</strong><span>Room E / 300 / 400</span></span>
            </button>
            <button class="legend-item" type="button" data-highlight="ballroom">
              <span class="swatch ballroom" aria-hidden="true"></span>
              <span><strong>Ballrooms</strong><span>Auditorium / ASEM / Grand</span></span>
            </button>
            <button class="legend-item" type="button" data-highlight="mall">
              <span class="swatch mall" aria-hidden="true"></span>
              <span><strong>COEX Mall</strong><span>B1 Starfield + east transit axis</span></span>
            </button>
          </div>
        </section>

        <section class="info-block">
          <header>
            <p class="eyebrow">Anchors</p>
            <h2>Fast orientation</h2>
          </header>
          <div class="anchor-list">
            <div class="anchor-item">
              <strong>1F South</strong>
              <span>Hall A poster flow, Samseong / Parnas side.</span>
            </div>
            <div class="anchor-item">
              <strong>1F North</strong>
              <span>Grand Ballroom, Auditorium side, Bongeunsa direction.</span>
            </div>
            <div class="anchor-item">
              <strong>3F South</strong>
              <span>Hall C, Hall D, Room E, main oral room cluster.</span>
            </div>
            <div class="anchor-item">
              <strong>B1 East</strong>
              <span>Starfield COEX Mall and subway transfer line.</span>
            </div>
          </div>
          <p class="source-note">Source: official ICML 2026 COEX SVG, downloaded from media.icml.cc on 2026-07-02. Geometry and labels are preserved.</p>
        </section>
      </aside>
    </main>

    <script>
      const params = new URLSearchParams(window.location.search);
      const isEmbed = params.has("embed");
      document.body.classList.toggle("is-embed", isEmbed);

      const artboard = document.querySelector(".map-artboard");
      let zoom = 100;
      const zoneIds = {
        poster: ["rect226", "rect228"],
        oral: ["rect236", "rect238"],
        rooms: ["rect216", "rect218", "rect230"],
        ballroom: ["rect240", "rect242", "rect244"],
        mall: ["polygon320", "polygon324", "line326"],
      };
      const allZoneIds = Object.values(zoneIds).flat();

      function setZoom(next) {
        zoom = Math.max(100, Math.min(180, next));
        artboard.style.setProperty("--zoom", zoom + "%");
        artboard.classList.toggle("is-zoomed", zoom > 100);
      }

      function clearHighlight() {
        for (const id of allZoneIds) {
          const node = document.getElementById(id);
          node?.classList.remove("is-dim", "is-highlight");
        }
      }

      function highlight(group) {
        clearHighlight();
        if (!group) return;
        for (const id of allZoneIds) {
          document.getElementById(id)?.classList.add("is-dim");
        }
        for (const id of zoneIds[group] || []) {
          const node = document.getElementById(id);
          node?.classList.remove("is-dim");
          node?.classList.add("is-highlight");
        }
      }

      function softenRooms() {
        for (const id of allZoneIds.filter((value) => value.startsWith("rect"))) {
          const node = document.getElementById(id);
          node?.setAttribute("rx", "8");
          node?.setAttribute("ry", "8");
        }
      }

      setZoom(zoom);
      softenRooms();

      document.querySelectorAll("[data-zoom-step]").forEach((button) => {
        button.addEventListener("click", () => setZoom(zoom + Number(button.dataset.zoomStep)));
      });

      document.querySelector("[data-zoom-reset]")?.addEventListener("click", () => setZoom(100));

      document.querySelectorAll("[data-highlight]").forEach((button) => {
        button.addEventListener("mouseenter", () => highlight(button.dataset.highlight));
        button.addEventListener("focus", () => highlight(button.dataset.highlight));
        button.addEventListener("click", () => highlight(button.dataset.highlight));
        button.addEventListener("mouseleave", clearHighlight);
        button.addEventListener("blur", clearHighlight);
      });
    </script>
  </body>
</html>
`;
}

const svg = inlineSvg(await readFile(sourcePath, "utf8"));
const html = page(svg);

await mkdir(dirname(dataOutputPath), { recursive: true });
await mkdir(dirname(docsOutputPath), { recursive: true });
await writeFile(dataOutputPath, html);
await writeFile(docsOutputPath, html);

console.log(`Wrote ${dataOutputPath}`);
console.log(`Wrote ${docsOutputPath}`);
