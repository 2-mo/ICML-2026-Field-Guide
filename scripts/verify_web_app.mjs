#!/usr/bin/env node
import { spawn } from "node:child_process";
import { access, mkdir, stat } from "node:fs/promises";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome";
const APP_URL = "http://localhost:8000/";
const shots = [
  ["mobile", "390,844", "/tmp/icml-guide-mobile.png"],
  ["desktop", "1440,1100", "/tmp/icml-guide-desktop.png"],
];

async function exists(path) {
  try {
    await access(path);
    return true;
  } catch {
    return false;
  }
}

function run(cmd, args) {
  return new Promise((resolveRun, reject) => {
    const child = spawn(cmd, args, { cwd: ROOT, stdio: "pipe" });
    let stderr = "";
    child.stderr.on("data", (chunk) => {
      stderr += chunk;
    });
    child.on("close", (code) => {
      if (code === 0) resolveRun(stderr);
      else reject(new Error(`${cmd} exited ${code}\n${stderr}`));
    });
  });
}

async function main() {
  if (!(await exists(CHROME))) {
    console.log("Chrome not found; skipped screenshot verification.");
    return;
  }
  for (const [, , path] of shots) {
    await mkdir(dirname(path), { recursive: true });
  }
  for (const [label, size, path] of shots) {
    await run(CHROME, [
      "--headless=new",
      "--disable-gpu",
      "--hide-scrollbars",
      `--window-size=${size}`,
      `--screenshot=${path}`,
      APP_URL,
    ]);
    const info = await stat(path);
    if (info.size < 20_000) throw new Error(`${label} screenshot looks too small: ${info.size} bytes`);
    console.log(`${label}: ${path} ${info.size} bytes`);
  }
}

main().catch((error) => {
  console.error(error.message);
  process.exit(1);
});
