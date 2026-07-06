#!/usr/bin/env node
import { mkdir, stat } from "node:fs/promises";
import { dirname, resolve } from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";
import { spawn } from "node:child_process";

const HERE = dirname(fileURLToPath(import.meta.url));
const CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome";
const HTML = resolve(HERE, "render.html");
const OUT_DIR = resolve(HERE, "../final");
const cards = [
  ["cover", "01-coex-map-arrival.png"],
  ["density", "02-poster-topic-density.png"],
  ["star", "03-star-author-posters.png"],
  ["papers", "04-video-mllm-paper-route-a.png"],
  ["papers2", "05-video-mllm-paper-route-b.png"],
  ["events", "06-evening-events-jul6-jul9.png"],
  ["seoul", "07-seoul-attractions.png"],
];

function runChrome(url, outPath) {
  return new Promise((resolveRun, reject) => {
    const child = spawn(CHROME, [
      "--headless=new",
      "--disable-gpu",
      "--hide-scrollbars",
      "--no-first-run",
      "--no-default-browser-check",
      "--window-size=1080,1440",
      `--screenshot=${outPath}`,
      url,
    ]);
    let stderr = "";
    child.stderr.on("data", (chunk) => {
      stderr += chunk;
    });
    child.on("close", (code) => {
      if (code === 0) resolveRun();
      else reject(new Error(`Chrome exited ${code}\n${stderr}`));
    });
  });
}

async function main() {
  await mkdir(OUT_DIR, { recursive: true });
  const base = pathToFileURL(HTML).href;
  for (const [key, name] of cards) {
    const outPath = resolve(OUT_DIR, name);
    await runChrome(`${base}?card=${key}`, outPath);
    const info = await stat(outPath);
    if (info.size < 160_000) {
      throw new Error(`${name} looks too small: ${info.size} bytes`);
    }
    console.log(`${name}: ${info.size} bytes`);
  }
}

main().catch((error) => {
  console.error(error.message);
  process.exit(1);
});
