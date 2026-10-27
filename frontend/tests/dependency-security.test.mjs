// Regression tests for security fixes that live in third-party dependencies.
import assert from "node:assert/strict";
import { existsSync, readFileSync, realpathSync } from "node:fs";
import path from "node:path";
import { test } from "node:test";

export function isAtLeast(version, floor) {
  const parse = (v) => v.split("-")[0].split(".").map(Number);
  const [a, b] = [parse(version), parse(floor)];
  for (let i = 0; i < 3; i++) {
    if (a[i] !== b[i]) return a[i] > b[i];
  }
  return true;
}

// Some packages (sharp >= 0.35) don't export ./package.json, so walk up the
// node_modules chain like Node does instead of using require.resolve.
function packageDir(name, startDir) {
  for (let dir = startDir; ; dir = path.dirname(dir)) {
    const candidate = path.join(dir, "node_modules", name);
    if (existsSync(path.join(candidate, "package.json")))
      return realpathSync(candidate);
    if (dir === path.dirname(dir)) throw new Error(`${name} is not installed`);
  }
}

function installedVersion(name, fromPackage) {
  const startDir = fromPackage
    ? packageDir(fromPackage, process.cwd())
    : process.cwd();
  const dir = packageDir(name, startDir);
  return JSON.parse(readFileSync(path.join(dir, "package.json"), "utf8"))
    .version;
}

test("isAtLeast compares semver triples", () => {
  assert.equal(isAtLeast("15.5.28", "15.5.28"), true);
  assert.equal(isAtLeast("15.5.6", "15.5.28"), false);
  assert.equal(isAtLeast("16.0.0", "15.5.28"), true);
  assert.equal(isAtLeast("0.34.5", "0.35.5"), false);
});

test("next includes the October 2026 RCE fixes", () => {
  assert.ok(
    isAtLeast(installedVersion("next"), "15.5.28"),
    installedVersion("next"),
  );
});

test("sharp bundled with next includes the October 2026 libvips fixes", () => {
  const version = installedVersion("sharp", "next");
  assert.ok(isAtLeast(version, "0.35.5"), version);
});
