# QC Long Play Converter — HTML Calculator Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a static, fully-offline browser version of the QC Long Play Converter in a new `web/` folder, matching the conversion behavior of `qc_longplay_convert.py`.

**Architecture:** Vendored SheetJS for in-browser Excel I/O. A pure-JS conversion module (`qc_longplay.js`) that mirrors the Python module function-for-function and operates on plain 2D arrays. UI wiring in `app.js`, markup in `index.html`, dark studio theme in `style.css`. Tests live in `web/test.html` and run in any browser via plain JS assertions — no test framework. Each test renders ✓/✗ as DOM, and a global `window.__testsPassed` boolean is set after the run for automation.

**Tech Stack:** Vanilla JS (no framework, no build step), vendored SheetJS Community Edition, system fonts only, CSS custom properties for theming.

**Spec:** [docs/superpowers/specs/2026-05-09-html-calculator-design.md](../specs/2026-05-09-html-calculator-design.md)

---

### Task 1: Set up directory structure and stub files

**Files:**
- Create: `web/index.html`
- Create: `web/style.css`
- Create: `web/qc_longplay.js`
- Create: `web/app.js`
- Create: `web/test.html`
- Create: `web/vendor/xlsx.full.min.js` (downloaded)

- [ ] **Step 1: Create the directory layout**

```bash
mkdir -p web/vendor
```

- [ ] **Step 2: Create empty stub source files**

Create `web/qc_longplay.js`:

```js
window.QCLongPlay = {};
```

Create `web/app.js` (empty placeholder):

```js
// Wired up in Task 10
```

Create `web/style.css` (empty — filled in Task 9):

```css
/* Filled in Task 9 */
```

Create `web/index.html` (minimal — filled in Task 8):

```html
<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8"><title>QC Long Play Converter</title></head>
<body><p>Placeholder — filled in Task 8.</p></body></html>
```

Create `web/test.html` (filled in Task 2):

```html
<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8"><title>QC LP tests</title></head>
<body><p>Placeholder — filled in Task 2.</p></body></html>
```

- [ ] **Step 3: Vendor SheetJS**

Download SheetJS Community Edition 0.20.3 to `web/vendor/xlsx.full.min.js`:

```bash
curl -fL -o web/vendor/xlsx.full.min.js https://cdn.sheetjs.com/xlsx-0.20.3/package/dist/xlsx.full.min.js
```

If that URL fails, try a different version (e.g. `xlsx-0.18.5`). The file should be ~900KB–1MB.

- [ ] **Step 4: Verify the download**

```bash
ls -la web/vendor/xlsx.full.min.js
head -c 200 web/vendor/xlsx.full.min.js
```

Expected: file size between 800KB and 1.5MB. The first line should start with `/*!` and reference SheetJS / xlsx. If it shows HTML, the download failed (likely a 404 redirect captured) — try a different version URL.

- [ ] **Step 5: Commit**

```bash
git add web/
git commit -m "Set up web/ directory and vendor SheetJS"
```

---

### Task 2: Test harness in `web/test.html`

**Files:**
- Modify: `web/test.html`

- [ ] **Step 1: Write the test harness with a placeholder passing test**

Replace `web/test.html` with:

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>QC Long Play Converter — Tests</title>
<style>
  body { font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
         background: #0E1014; color: #E6E8EC; padding: 24px; }
  h1 { font-size: 18px; margin: 0 0 16px; }
  .summary { padding: 8px 12px; border-radius: 6px; margin-bottom: 16px;
             display: inline-block; font-weight: 600; }
  .summary.pass { background: rgba(93, 190, 138, 0.15); color: #5DBE8A; }
  .summary.fail { background: rgba(232, 99, 90, 0.15); color: #E8635A; }
  .case { padding: 4px 0; }
  .case.pass::before { content: "✓ "; color: #5DBE8A; }
  .case.fail::before { content: "✗ "; color: #E8635A; }
  .case.fail { color: #E8635A; }
  .detail { color: #8A91A0; padding-left: 18px; font-size: 13px; }
</style>
</head>
<body>
<h1>QC Long Play Converter — Tests</h1>
<div id="summary" class="summary"></div>
<div id="cases"></div>

<script src="vendor/xlsx.full.min.js"></script>
<script src="qc_longplay.js"></script>
<script>
(function () {
  const cases = document.getElementById('cases');
  const summary = document.getElementById('summary');
  let passed = 0;
  let failed = 0;

  function record(label, ok, detail) {
    const div = document.createElement('div');
    div.className = 'case ' + (ok ? 'pass' : 'fail');
    div.textContent = label;
    cases.appendChild(div);
    if (!ok && detail) {
      const d = document.createElement('div');
      d.className = 'detail';
      d.textContent = detail;
      cases.appendChild(d);
    }
    if (ok) passed++; else failed++;
  }

  window.assert = function (label, condition, detail) {
    record(label, !!condition, detail);
  };
  window.assertEq = function (label, actual, expected) {
    const ok = JSON.stringify(actual) === JSON.stringify(expected);
    record(label, ok, ok ? null : `expected ${JSON.stringify(expected)}, got ${JSON.stringify(actual)}`);
  };
  window.assertThrows = function (label, fn, messageContains) {
    try {
      fn();
      record(label, false, 'expected to throw, but did not');
    } catch (e) {
      if (messageContains && !String(e.message).includes(messageContains)) {
        record(label, false, `threw '${e.message}', expected to contain '${messageContains}'`);
      } else {
        record(label, true);
      }
    }
  };

  window.runTests = function (tests) {
    tests();
    const total = passed + failed;
    summary.textContent = `${passed} / ${total} passed${failed ? ` — ${failed} failed` : ''}`;
    summary.className = 'summary ' + (failed ? 'fail' : 'pass');
    window.__testsPassed = failed === 0;
    window.__testCounts = { passed, failed, total };
  };
})();
</script>

<script>
runTests(function () {
  assert('test harness works', true);
});
</script>
</body>
</html>
```

- [ ] **Step 2: Verify in a browser**

Open `web/test.html` in a browser (or via a local static server: `cd web && python -m http.server 8765` then visit `http://localhost:8765/test.html`).

Expected: green "1 / 1 passed" banner with one ✓ line "test harness works".

- [ ] **Step 3: Commit**

```bash
git add web/test.html
git commit -m "Add test harness scaffold"
```

---

### Task 3: Timecode arithmetic — `tcToSeconds` and `framesToSeconds`

**Files:**
- Modify: `web/qc_longplay.js`
- Modify: `web/test.html`

- [ ] **Step 1: Write the failing tests**

In `web/test.html`, replace the placeholder `runTests(...)` block at the bottom with:

```html
<script>
runTests(function () {
  const { tcToSeconds, framesToSeconds } = QCLongPlay;

  // tcToSeconds
  assertEq('tcToSeconds 00:00:00:00 @24', tcToSeconds('00:00:00:00', 24), 0);
  assertEq('tcToSeconds 01:00:00:00 @24', tcToSeconds('01:00:00:00', 24), 3600);
  assertEq('tcToSeconds 00:00:00:12 @24', tcToSeconds('00:00:00:12', 24), 0.5);
  assertEq('tcToSeconds 00:00:01:00 @25', tcToSeconds('00:00:01:00', 25), 1);
  assertEq('tcToSeconds 01:23:45:06 @24',
    tcToSeconds('01:23:45:06', 24),
    1*3600 + 23*60 + 45 + 6/24);
  assertEq('tcToSeconds whitespace tolerated', tcToSeconds('  00:00:01:00  ', 24), 1);
  assertEq('tcToSeconds invalid format → null', tcToSeconds('1:2:3:4', 24), null);
  assertEq('tcToSeconds non-string → null', tcToSeconds(null, 24), null);
  assertEq('tcToSeconds non-string number → null', tcToSeconds(42, 24), null);

  // framesToSeconds
  assertEq('framesToSeconds 24 @24', framesToSeconds(24, 24), 1);
  assertEq('framesToSeconds 0 @24', framesToSeconds(0, 24), 0);
  assertEq('framesToSeconds 1 @24', framesToSeconds(1, 24), 1/24);
  assertEq('framesToSeconds 5 @25', framesToSeconds(5, 25), 0.2);
});
</script>
```

- [ ] **Step 2: Run tests — verify they fail**

Reload `web/test.html`. Expected: red "0 / 13 passed — 13 failed" banner. Each line shows ✗ with detail like "expected 0, got undefined" (because `tcToSeconds` and `framesToSeconds` aren't defined yet).

- [ ] **Step 3: Implement `tcToSeconds` and `framesToSeconds`**

Replace `web/qc_longplay.js` with:

```js
(function (global) {
  const TC_PATTERN = /^(\d{2}):(\d{2}):(\d{2}):(\d{2})$/;

  function validateFps(fps) {
    if (typeof fps !== 'number' || !Number.isFinite(fps) || fps <= 0) {
      throw new Error(`FPS must be a positive number, got ${fps}`);
    }
  }

  function tcToSeconds(tc, fps) {
    if (typeof tc !== 'string') return null;
    const m = TC_PATTERN.exec(tc.trim());
    if (!m) return null;
    const h = parseInt(m[1], 10);
    const mi = parseInt(m[2], 10);
    const s = parseInt(m[3], 10);
    const f = parseInt(m[4], 10);
    return h * 3600 + mi * 60 + s + f / fps;
  }

  function framesToSeconds(frames, fps) {
    return frames / fps;
  }

  global.QCLongPlay = {
    _internal: { TC_PATTERN, validateFps },
    tcToSeconds,
    framesToSeconds,
  };
})(window);
```

- [ ] **Step 4: Run tests — verify they pass**

Reload `web/test.html`. Expected: green "13 / 13 passed" banner.

- [ ] **Step 5: Commit**

```bash
git add web/qc_longplay.js web/test.html
git commit -m "Add tcToSeconds and framesToSeconds with tests"
```

---

### Task 4: `secondsToTc` with floating-point guard

**Files:**
- Modify: `web/qc_longplay.js`
- Modify: `web/test.html`

- [ ] **Step 1: Add failing tests**

In `web/test.html`, append to the inside of `runTests(function () { ... })` (just before the closing `});`):

```js
  // secondsToTc
  const { secondsToTc } = QCLongPlay;
  assertEq('secondsToTc 0 @24', secondsToTc(0, 24), '00:00:00:00');
  assertEq('secondsToTc 3600 @24', secondsToTc(3600, 24), '01:00:00:00');
  assertEq('secondsToTc 0.5 @24', secondsToTc(0.5, 24), '00:00:00:12');
  assertEq('secondsToTc 1 @25', secondsToTc(1, 25), '00:00:01:00');
  assertEq('secondsToTc 5025.25 @24',
    secondsToTc(5025.25, 24),
    '01:23:45:06');
  // Floating-point guard: a value that rounds to fps frames must roll over to the next second.
  assertEq('secondsToTc fp guard: 0.99999999 @24', secondsToTc(0.99999999, 24), '00:00:01:00');
  assertEq('secondsToTc round-trip 01:23:45:06 @24',
    secondsToTc(QCLongPlay.tcToSeconds('01:23:45:06', 24), 24),
    '01:23:45:06');
  assertEq('secondsToTc round-trip 23:59:59:23 @24',
    secondsToTc(QCLongPlay.tcToSeconds('23:59:59:23', 24), 24),
    '23:59:59:23');
```

- [ ] **Step 2: Run tests — verify the new ones fail**

Reload `web/test.html`. Expected: 8 new ✗ lines (one per new `secondsToTc` test). The previous 13 still pass.

- [ ] **Step 3: Implement `secondsToTc`**

In `web/qc_longplay.js`, add the function inside the IIFE (after `framesToSeconds`):

```js
  function secondsToTc(seconds, fps) {
    const whole = Math.floor(seconds);
    const frac = seconds - whole;
    let frames = Math.round(frac * fps);
    let total = whole;
    if (frames >= fps) {
      frames = 0;
      total += 1;
    }
    const h = Math.floor(total / 3600);
    const m = Math.floor((total % 3600) / 60);
    const s = total % 60;
    const pad = (n) => String(n).padStart(2, '0');
    return `${pad(h)}:${pad(m)}:${pad(s)}:${pad(frames)}`;
  }
```

And add it to the exports:

```js
  global.QCLongPlay = {
    _internal: { TC_PATTERN, validateFps },
    tcToSeconds,
    framesToSeconds,
    secondsToTc,
  };
```

- [ ] **Step 4: Run tests — verify all pass**

Reload `web/test.html`. Expected: green "21 / 21 passed".

- [ ] **Step 5: Commit**

```bash
git add web/qc_longplay.js web/test.html
git commit -m "Add secondsToTc with floating-point guard"
```

---

### Task 5: `buildIntervals`

**Files:**
- Modify: `web/qc_longplay.js`
- Modify: `web/test.html`

- [ ] **Step 1: Add failing tests**

Append inside `runTests(function () { ... })` in `web/test.html`:

```js
  // buildIntervals
  const { buildIntervals } = QCLongPlay;

  // Helper: build a 2D array fixture matching the expected layout.
  // Columns: 0=note(blank), 1=src tc, 2=dst tc, 3=descriptor.
  function makeRows(reels, opts = {}) {
    const rows = [[null, null, null, 'Header']];
    for (const r of reels) {
      rows.push([null, r.start, null, `Program Start - Reel ${r.n}`]);
      if (r.notes) rows.push(...r.notes.map(tc => [null, tc, null, 'note']));
      rows.push([null, r.end, null, `Program End - Reel ${r.n}`]);
    }
    return rows;
  }

  // Single reel
  const single = makeRows([{ n: 1, start: '01:00:00:00', end: '01:10:00:00' }]);
  const r1 = buildIntervals(single, { fps: 24, lpStartTc: '01:00:00:00' });
  assertEq('single reel: 1 interval', r1.intervals.length, 1);
  assertEq('single reel: reel num', r1.intervals[0].reel, 1);
  assertEq('single reel: lpStart', r1.intervals[0].lpStart, 3600);
  assertEq('single reel: duration', r1.intervals[0].duration, 600);
  assertEq('single reel: firstStart row 1', r1.firstStart, 1);
  assertEq('single reel: lastEnd row 2', r1.lastEnd, 2);

  // Multi reel — LP cursor advances, durations preserved
  const multi = makeRows([
    { n: 1, start: '01:00:00:00', end: '01:10:00:00' },
    { n: 2, start: '02:00:00:00', end: '02:05:00:00' },
    { n: 3, start: '03:00:00:00', end: '03:07:30:00' },
  ]);
  const r3 = buildIntervals(multi, { fps: 24, lpStartTc: '01:00:00:00' });
  assertEq('multi: 3 intervals', r3.intervals.length, 3);
  assertEq('multi: reel 1 lpStart', r3.intervals[0].lpStart, 3600);
  assertEq('multi: reel 2 lpStart = 3600 + 600', r3.intervals[1].lpStart, 4200);
  assertEq('multi: reel 3 lpStart = 4200 + 300', r3.intervals[2].lpStart, 4500);

  // Reel boundaries detected even with notes between
  const withNotes = makeRows([
    { n: 1, start: '01:00:00:00', end: '01:10:00:00',
      notes: ['01:01:00:00', '01:05:30:00'] },
  ]);
  const rNotes = buildIntervals(withNotes, { fps: 24, lpStartTc: '01:00:00:00' });
  assertEq('with notes: still 1 reel', rNotes.intervals.length, 1);

  // Error: no reel boundaries
  assertThrows('no reels throws',
    () => buildIntervals([[null, null, null, 'unrelated']], { fps: 24, lpStartTc: '01:00:00:00' }),
    'No reel boundaries found');

  // Error: invalid FPS
  assertThrows('invalid FPS throws',
    () => buildIntervals(single, { fps: 0, lpStartTc: '01:00:00:00' }),
    'FPS must be a positive number');

  // Reels detected out of order should be sorted
  const reordered = [
    [null, null, null, 'Header'],
    [null, '02:00:00:00', null, 'Program Start - Reel 2'],
    [null, '02:05:00:00', null, 'Program End - Reel 2'],
    [null, '01:00:00:00', null, 'Program Start - Reel 1'],
    [null, '01:10:00:00', null, 'Program End - Reel 1'],
  ];
  const rReorder = buildIntervals(reordered, { fps: 24, lpStartTc: '01:00:00:00' });
  assertEq('out-of-order reels: sorted', rReorder.intervals.map(i => i.reel), [1, 2]);
  assertEq('out-of-order: reel 1 lpStart', rReorder.intervals[0].lpStart, 3600);
  assertEq('out-of-order: reel 2 lpStart = 3600 + 600', rReorder.intervals[1].lpStart, 4200);
```

- [ ] **Step 2: Run tests — verify the new ones fail**

Reload `web/test.html`. Expected: new ✗ lines because `buildIntervals` is undefined or throws.

- [ ] **Step 3: Implement `buildIntervals`**

In `web/qc_longplay.js`, add inside the IIFE (after `secondsToTc`):

```js
  function buildIntervals(rows, opts) {
    opts = opts || {};
    const fps = opts.fps != null ? opts.fps : 24;
    const lpStartTc = opts.lpStartTc != null ? opts.lpStartTc : '01:00:00:00';
    const descCol = opts.descCol != null ? opts.descCol : 3;
    const tcCol = opts.tcCol != null ? opts.tcCol : 1;

    validateFps(fps);

    const reelBounds = {};
    let current = null;

    for (let i = 0; i < rows.length; i++) {
      const row = rows[i] || [];
      const desc = String(row[descCol] != null ? row[descCol] : '');
      const tc = row[tcCol];
      if (desc.indexOf('Program Start - Reel') !== -1) {
        const m = /Reel\s*(\d+)/.exec(desc);
        if (m && typeof tc === 'string') {
          const r = parseInt(m[1], 10);
          reelBounds[r] = { startTc: tc, endTc: null, startRow: i, endRow: null };
          current = r;
        }
      } else if (desc.indexOf('Program End - Reel') !== -1 && current !== null) {
        if (typeof tc === 'string') {
          reelBounds[current].endTc = tc;
          reelBounds[current].endRow = i;
        }
        current = null;
      }
    }

    if (Object.keys(reelBounds).length === 0) {
      throw new Error(
        "No reel boundaries found. Expected rows with " +
        "'Program Start - Reel X' / 'Program End - Reel X' in column 4 (0-based index 3)."
      );
    }

    let lpCursor = tcToSeconds(lpStartTc, fps);
    if (lpCursor === null) {
      throw new Error(`Invalid LP start TC: ${lpStartTc}`);
    }

    const intervals = [];
    const sortedReels = Object.keys(reelBounds).map(Number).sort((a, b) => a - b);
    for (const r of sortedReels) {
      const rs = tcToSeconds(reelBounds[r].startTc, fps);
      const re = tcToSeconds(reelBounds[r].endTc, fps);
      if (rs === null || re === null) {
        throw new Error(`Invalid timecode for Reel ${r} boundaries.`);
      }
      const dur = re - rs;
      intervals.push({ reel: r, reelStart: rs, reelEnd: re, lpStart: lpCursor, duration: dur });
      lpCursor += dur;
    }

    const allBounds = Object.values(reelBounds);
    const firstStart = Math.min.apply(null, allBounds.map(b => b.startRow));
    const lastEnd = Math.max.apply(null, allBounds.map(b => b.endRow));

    return { intervals, firstStart, lastEnd };
  }
```

Add to the exports:

```js
  global.QCLongPlay = {
    _internal: { TC_PATTERN, validateFps },
    tcToSeconds,
    framesToSeconds,
    secondsToTc,
    buildIntervals,
  };
```

- [ ] **Step 4: Run tests — verify all pass**

Reload `web/test.html`. Expected: green banner, all tests pass.

- [ ] **Step 5: Commit**

```bash
git add web/qc_longplay.js web/test.html
git commit -m "Add buildIntervals"
```

---

### Task 6: `convertTc`

**Files:**
- Modify: `web/qc_longplay.js`
- Modify: `web/test.html`

- [ ] **Step 1: Add failing tests**

Append inside `runTests(function () { ... })` in `web/test.html`:

```js
  // convertTc
  const { convertTc } = QCLongPlay;
  const cMulti = buildIntervals(makeRows([
    { n: 1, start: '01:00:00:00', end: '01:10:00:00' },
    { n: 2, start: '02:00:00:00', end: '02:05:00:00' },
    { n: 3, start: '03:00:00:00', end: '03:07:30:00' },
  ]), { fps: 24, lpStartTc: '01:00:00:00' });

  // Reel 1: no correction, +0f
  assertEq('reel 1 start → lp start',
    convertTc('01:00:00:00', cMulti.intervals, 24), '01:00:00:00');
  assertEq('reel 1 mid (+5min) → lp 01:05:00:00',
    convertTc('01:05:00:00', cMulti.intervals, 24), '01:05:00:00');
  assertEq('reel 1 end (closed interval, kept) → lp 01:10:00:00',
    convertTc('01:10:00:00', cMulti.intervals, 24), '01:10:00:00');

  // Reel 2: +1f correction
  // 02:00:00:00 in source maps to 01:10:00:00 + 1f in LP
  assertEq('reel 2 start → lp 01:10:00:00 + 1f',
    convertTc('02:00:00:00', cMulti.intervals, 24), '01:10:00:01');
  // 02:05:00:00 = end of reel 2 → lp end = 01:15:00:00 + 1f
  assertEq('reel 2 end → lp 01:15:00:01',
    convertTc('02:05:00:00', cMulti.intervals, 24), '01:15:00:01');

  // Reel 3: +2f correction
  // 03:00:00:00 → lp 01:15:00:00 + 2f
  assertEq('reel 3 start → lp 01:15:00:02',
    convertTc('03:00:00:00', cMulti.intervals, 24), '01:15:00:02');

  // Out of range → null
  assertEq('out of range tc → null',
    convertTc('00:30:00:00', cMulti.intervals, 24), null);
  assertEq('between reels (no overlap) → null',
    convertTc('01:30:00:00', cMulti.intervals, 24), null);

  // Invalid TC string → returned unchanged (matches Python's convert_tc_corrected)
  assertEq('invalid tc → returned unchanged',
    convertTc('not-a-tc', cMulti.intervals, 24), 'not-a-tc');
```

- [ ] **Step 2: Run tests — verify the new ones fail**

Reload. Expected: new ✗ lines for `convertTc` cases.

- [ ] **Step 3: Implement `convertTc`**

Add inside the IIFE in `web/qc_longplay.js` (after `buildIntervals`):

```js
  function convertTc(tcStr, intervals, fps) {
    const td = tcToSeconds(tcStr, fps);
    if (td === null) return tcStr;
    for (const iv of intervals) {
      if (iv.reelStart <= td && td <= iv.reelEnd) {
        const offset = td - iv.reelStart;
        const correctionFrames = Math.max(0, iv.reel - 1);
        return secondsToTc(iv.lpStart + offset + framesToSeconds(correctionFrames, fps), fps);
      }
    }
    return null;
  }
```

Add to the exports object alongside the others:

```js
    convertTc,
```

- [ ] **Step 4: Run tests — verify all pass**

Reload. Expected: all green.

- [ ] **Step 5: Commit**

```bash
git add web/qc_longplay.js web/test.html
git commit -m "Add convertTc with frame correction"
```

---

### Task 7: `processRows`

**Files:**
- Modify: `web/qc_longplay.js`
- Modify: `web/test.html`

- [ ] **Step 1: Add failing tests**

Append inside `runTests(function () { ... })` in `web/test.html`:

```js
  // processRows
  const { processRows } = QCLongPlay;

  // Build a fixture with two reels and content in between markers.
  // Layout columns: 0=blank, 1=src tc, 2=dst tc, 3=descriptor
  const procFixture = [
    [null, null, null, 'Header'],
    [null, '01:00:00:00', '01:00:00:00', 'Program Start - Reel 1'],
    [null, '01:01:00:00', '01:01:30:00', 'note A in reel 1'],
    [null, '01:09:00:00', '01:09:30:00', 'note B in reel 1'],
    [null, '01:10:00:00', '01:10:00:00', 'Program End - Reel 1'],
    [null, '02:00:00:00', '02:00:00:00', 'Program Start - Reel 2'],
    [null, '02:02:30:00', '02:03:00:00', 'note C in reel 2'],
    [null, '02:05:00:00', '02:05:00:00', 'Program End - Reel 2'],
  ];

  // Default opts: dropMarkers = true
  const dropped = processRows(procFixture, { fps: 24, lpStartTc: '01:00:00:00' });
  // Expected output rows: notes A, B (from reel 1), note C (from reel 2),
  // and the final Program End - Reel 2 (always kept, with forced LP TC).
  // Reel 1 starts at LP 01:00:00:00, +0f correction.
  // Reel 2 starts at LP 01:10:00:00, +1f correction.
  // Final Program End forced to: lastReelLpStart + lastReelDuration + correction + 1f
  //   = 01:10:00:00 + 5min + 1f + 1f = 01:15:00:02
  assertEq('drop markers: 4 rows', dropped.length, 4);
  assertEq('drop markers: row 0 desc', dropped[0][3], 'note A in reel 1');
  assertEq('drop markers: row 0 col 1 converted',
    dropped[0][1], '01:01:00:00');
  assertEq('drop markers: row 0 col 2 converted',
    dropped[0][2], '01:01:30:00');
  // note C: source 02:02:30:00 → reel 2 + offset 2:30 + 1f = 01:12:30:01
  assertEq('drop markers: note C col 1', dropped[2][1], '01:12:30:01');
  // final program end forced
  assertEq('drop markers: final desc', dropped[3][3], 'Program End - Reel 2');
  assertEq('drop markers: final col 1 forced', dropped[3][1], '01:15:00:02');
  assertEq('drop markers: final col 2 forced', dropped[3][2], '01:15:00:02');

  // dropMarkers = false: keep inter-reel markers too
  const kept = processRows(procFixture, { fps: 24, lpStartTc: '01:00:00:00', dropMarkers: false });
  assertEq('keep markers: 7 rows', kept.length, 7);
  // Program Start - Reel 1 → converted: 01:00:00:00 stays
  assertEq('keep markers: reel 1 start preserved', kept[0][3], 'Program Start - Reel 1');
  assertEq('keep markers: reel 1 start tc', kept[0][1], '01:00:00:00');
  // Program Start - Reel 2 → 02:00:00:00 → 01:10:00:01
  // (interval lookup returns LP 01:10:00:00 + 1f)
  const reel2StartIdx = kept.findIndex(r => r[3] === 'Program Start - Reel 2');
  assert('keep markers: reel 2 start present', reel2StartIdx !== -1);
  assertEq('keep markers: reel 2 start tc converted',
    kept[reel2StartIdx][1], '01:10:00:01');

  // Empty rows within range with no descriptor are dropped
  const sparseFixture = [
    [null, null, null, 'Header'],
    [null, '01:00:00:00', null, 'Program Start - Reel 1'],
    [null, null, null, null],  // blank — should be dropped
    [null, '01:05:00:00', null, 'note inside reel'],
    [null, '01:10:00:00', null, 'Program End - Reel 1'],
  ];
  const sparse = processRows(sparseFixture, { fps: 24, lpStartTc: '01:00:00:00' });
  assertEq('sparse: blank row dropped, 2 rows', sparse.length, 2);
  assertEq('sparse: note kept', sparse[0][3], 'note inside reel');
  assertEq('sparse: program end kept (final)', sparse[1][3], 'Program End - Reel 1');

  // Single-reel case
  const singleFixture = [
    [null, '01:00:00:00', null, 'Program Start - Reel 1'],
    [null, '01:00:30:00', null, 'note'],
    [null, '01:01:00:00', null, 'Program End - Reel 1'],
  ];
  const singleResult = processRows(singleFixture, { fps: 24, lpStartTc: '01:00:00:00' });
  // Reel 1, +0f correction, duration 1 minute. Final TC = 01:01:00:00 + 1f
  assertEq('single: 2 rows', singleResult.length, 2);
  assertEq('single: final program end forced', singleResult[1][1], '01:01:00:01');

  // Error propagation
  assertThrows('processRows: no reels throws',
    () => processRows([[null, null, null, 'unrelated']], { fps: 24, lpStartTc: '01:00:00:00' }),
    'No reel boundaries found');
```

- [ ] **Step 2: Run tests — verify the new ones fail**

Reload. Expected: new ✗ lines.

- [ ] **Step 3: Implement `processRows`**

Add inside the IIFE in `web/qc_longplay.js` (after `convertTc`):

```js
  function processRows(rows, opts) {
    opts = opts || {};
    const fps = opts.fps != null ? opts.fps : 24;
    const lpStartTc = opts.lpStartTc != null ? opts.lpStartTc : '01:00:00:00';
    const dropMarkers = opts.dropMarkers !== false; // default true

    validateFps(fps);

    const built = buildIntervals(rows, { fps, lpStartTc });
    const intervals = built.intervals;
    const firstStart = built.firstStart;
    const lastEnd = built.lastEnd;

    const lastInterval = intervals[intervals.length - 1];
    const lastReelCorrection = framesToSeconds(Math.max(0, lastInterval.reel - 1), fps);
    const programEndLpTc = secondsToTc(
      lastInterval.lpStart + lastInterval.duration + lastReelCorrection + framesToSeconds(1, fps),
      fps
    );

    const tcCols = [1, 2];
    const out = [];

    for (let idx = firstStart; idx <= lastEnd; idx++) {
      const src = rows[idx] || [];
      const row = src.slice();

      let changed = false;
      for (const c of tcCols) {
        const v = row[c];
        if (typeof v === 'string' && TC_PATTERN.test(v)) {
          const newTc = convertTc(v, intervals, fps);
          row[c] = newTc;
          if (newTc !== null) changed = true;
        }
      }

      const desc = String(row[3] != null ? row[3] : '');
      const isMarker = desc.indexOf('Program Start - Reel') !== -1 ||
                       desc.indexOf('Program End - Reel') !== -1;
      const isFinalProgramEnd = desc.indexOf('Program End') !== -1 && idx === lastEnd;

      if (isFinalProgramEnd) {
        for (const c of tcCols) row[c] = programEndLpTc;
        out.push(row);
        continue;
      }

      if (dropMarkers && isMarker) continue;

      // hasContent: changed OR any of cols 3-6 is non-null/non-undefined
      let hasContent = changed;
      if (!hasContent) {
        for (const c of [3, 4, 5, 6]) {
          if (row[c] != null) { hasContent = true; break; }
        }
      }
      if (hasContent) out.push(row);
    }

    return out;
  }
```

Add to exports:

```js
    processRows,
```

- [ ] **Step 4: Run tests — verify all pass**

Reload. Expected: all green.

- [ ] **Step 5: Commit**

```bash
git add web/qc_longplay.js web/test.html
git commit -m "Add processRows with marker handling and final TC forcing"
```

---

### Task 8: `processWorkbook` wrapper (uses SheetJS)

**Files:**
- Modify: `web/qc_longplay.js`
- Modify: `web/test.html`

- [ ] **Step 1: Add failing tests**

Append inside `runTests(function () { ... })` in `web/test.html`:

```js
  // processWorkbook
  const { processWorkbook } = QCLongPlay;

  function makeWorkbook(rows, sheetName) {
    const ws = XLSX.utils.aoa_to_sheet(rows);
    const wb = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(wb, ws, sheetName);
    return wb;
  }

  const wbRows = [
    [null, null, null, 'Header'],
    [null, '01:00:00:00', null, 'Program Start - Reel 1'],
    [null, '01:05:00:00', null, 'note'],
    [null, '01:10:00:00', null, 'Program End - Reel 1'],
  ];
  const wb = makeWorkbook(wbRows, 'QC Report');

  const newWb = processWorkbook(wb, { sheetName: 'QC Report', fps: 24, lpStartTc: '01:00:00:00' });
  assertEq('processWorkbook: output sheet name',
    newWb.SheetNames[0], 'QC Report LongPlay');

  const outSheet = newWb.Sheets['QC Report LongPlay'];
  const outRows = XLSX.utils.sheet_to_json(outSheet, { header: 1, raw: false, defval: null });
  assertEq('processWorkbook: 2 output rows', outRows.length, 2);
  assertEq('processWorkbook: row 0 desc', outRows[0][3], 'note');
  assertEq('processWorkbook: row 0 tc converted', outRows[0][1], '01:05:00:00');
  assertEq('processWorkbook: final program end desc', outRows[1][3], 'Program End - Reel 1');
  assertEq('processWorkbook: final program end forced tc', outRows[1][1], '01:10:00:01');

  // Error: sheet not found
  assertThrows('processWorkbook: missing sheet throws',
    () => processWorkbook(wb, { sheetName: 'Nope', fps: 24, lpStartTc: '01:00:00:00' }),
    "Sheet 'Nope' not found");

  // Default options
  const defaultsResult = processWorkbook(wb);
  assertEq('processWorkbook: defaults to QC Report sheet',
    defaultsResult.SheetNames[0], 'QC Report LongPlay');
```

- [ ] **Step 2: Run tests — verify the new ones fail**

Reload. Expected: new ✗ lines.

- [ ] **Step 3: Implement `processWorkbook`**

Add inside the IIFE in `web/qc_longplay.js` (after `processRows`):

```js
  function processWorkbook(workbook, opts) {
    opts = opts || {};
    const sheetName = opts.sheetName != null ? opts.sheetName : 'QC Report';
    const fps = opts.fps != null ? opts.fps : 24;
    const lpStartTc = opts.lpStartTc != null ? opts.lpStartTc : '01:00:00:00';
    const dropMarkers = opts.dropMarkers !== false;

    if (typeof XLSX === 'undefined') {
      throw new Error('SheetJS (XLSX) is not loaded. Make sure vendor/xlsx.full.min.js is included.');
    }
    if (workbook.SheetNames.indexOf(sheetName) === -1) {
      throw new Error(
        `Sheet '${sheetName}' not found. Available sheets: ${workbook.SheetNames.join(', ')}`
      );
    }

    const sheet = workbook.Sheets[sheetName];
    const rows = XLSX.utils.sheet_to_json(sheet, { header: 1, raw: false, defval: null });
    const converted = processRows(rows, { fps, lpStartTc, dropMarkers });

    const newSheet = XLSX.utils.aoa_to_sheet(converted);
    const newWorkbook = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(newWorkbook, newSheet, `${sheetName} LongPlay`);
    return newWorkbook;
  }
```

Add to exports:

```js
    processWorkbook,
```

- [ ] **Step 4: Run tests — verify all pass**

Reload. Expected: all green.

- [ ] **Step 5: Commit**

```bash
git add web/qc_longplay.js web/test.html
git commit -m "Add processWorkbook wrapper for SheetJS"
```

---

### Task 9: HTML markup (`index.html`)

**Files:**
- Modify: `web/index.html`

- [ ] **Step 1: Replace the placeholder with the full markup**

Replace `web/index.html` with:

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>QC Long Play Converter</title>
<link rel="stylesheet" href="style.css">
</head>
<body>
<main>
  <header>
    <h1>QC Long Play Converter</h1>
    <p>Convert reel-based QC timecodes to a continuous long play timeline.</p>
  </header>

  <div id="dropzone" class="dropzone">
    <div class="dropzone-text">Drop a .xlsx file here</div>
    <div class="dropzone-hint">or click to browse</div>
    <input type="file" id="file-input" accept=".xlsx" hidden>
  </div>

  <div id="file-info" class="card file-info" hidden>
    <span id="file-info-text"></span>
    <button type="button" class="change-link" id="change-file">Change file</button>
  </div>

  <button type="button" class="btn btn-primary" id="convert-btn" disabled>Convert</button>

  <div id="status-panel" class="status-panel card">
    <p id="status-message" class="status-message"></p>
    <div id="status-details"></div>
  </div>

  <button type="button" class="btn btn-primary" id="download-btn" hidden>Download converted file</button>

  <details>
    <summary>Advanced settings</summary>
    <div class="advanced-body">
      <div class="field">
        <label for="sheet-name">Sheet name</label>
        <input type="text" id="sheet-name" value="QC Report">
      </div>
      <div class="field-row">
        <div class="field">
          <label for="fps">FPS</label>
          <select id="fps">
            <option value="24" selected>24</option>
            <option value="25">25</option>
            <option value="30">30</option>
          </select>
        </div>
        <div class="field">
          <label for="lp-start">LP start TC</label>
          <input type="text" id="lp-start" value="01:00:00:00" placeholder="HH:MM:SS:FF">
          <div id="lp-start-error" class="field-error" hidden></div>
        </div>
      </div>
      <div class="checkbox-field">
        <input type="checkbox" id="keep-markers">
        <label for="keep-markers">Keep "Program Start/End" markers in output</label>
      </div>
    </div>
  </details>
</main>

<script src="vendor/xlsx.full.min.js"></script>
<script src="qc_longplay.js"></script>
<script src="app.js"></script>
</body>
</html>
```

- [ ] **Step 2: Verify it loads (without styling yet)**

Open `web/index.html` in a browser. Expected: unstyled markup with all elements visible. Click "Drop a .xlsx file here" — the file picker should open. The "Convert" button should appear disabled.

- [ ] **Step 3: Commit**

```bash
git add web/index.html
git commit -m "Add HTML markup for converter UI"
```

---

### Task 10: Dark studio theme (`style.css`)

**Files:**
- Modify: `web/style.css`

- [ ] **Step 1: Replace the placeholder with the full stylesheet**

Replace `web/style.css` with:

```css
:root {
  --bg: #0E1014;
  --surface: #181B22;
  --border: #272B35;
  --text: #E6E8EC;
  --muted: #8A91A0;
  --accent: #E5A93A;
  --accent-hover: #F4BC4E;
  --success: #5DBE8A;
  --error: #E8635A;
  --font-ui: -apple-system, BlinkMacSystemFont, "Segoe UI", Inter, Roboto, sans-serif;
  --font-mono: ui-monospace, SFMono-Regular, "JetBrains Mono", Menlo, Consolas, monospace;
}

*, *::before, *::after { box-sizing: border-box; }
html, body { margin: 0; padding: 0; }
body {
  background: var(--bg);
  color: var(--text);
  font-family: var(--font-ui);
  font-size: 15px;
  line-height: 1.5;
  min-height: 100vh;
  display: flex;
  justify-content: center;
}

main {
  width: 100%;
  max-width: 640px;
  padding: 48px 24px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

header { margin-bottom: 8px; }
header h1 {
  font-size: 28px;
  font-weight: 600;
  margin: 0 0 6px;
  letter-spacing: -0.01em;
}
header p {
  margin: 0;
  color: var(--muted);
  font-size: 14px;
}

.card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 20px 24px;
}

.dropzone {
  background: var(--surface);
  border: 2px dashed #3A4050;
  border-radius: 12px;
  padding: 40px 24px;
  text-align: center;
  cursor: pointer;
  transition: border-color 0.15s ease, background-color 0.15s ease;
}
.dropzone:hover { border-color: var(--muted); }
.dropzone.dragover {
  border-color: var(--accent);
  background: rgba(229, 169, 58, 0.08);
}
.dropzone-text {
  font-size: 16px;
  color: var(--text);
  margin-bottom: 4px;
}
.dropzone-hint {
  font-size: 13px;
  color: var(--muted);
}

.file-info {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-family: var(--font-mono);
  font-size: 14px;
}
.file-info .change-link {
  color: var(--accent);
  background: none;
  border: 0;
  font: inherit;
  cursor: pointer;
  padding: 0;
}
.file-info .change-link:hover {
  color: var(--accent-hover);
  text-decoration: underline;
}

.btn {
  font-family: inherit;
  font-size: 15px;
  font-weight: 600;
  padding: 12px 20px;
  border-radius: 8px;
  border: 1px solid transparent;
  cursor: pointer;
  transition: background 0.15s ease, border-color 0.15s ease, color 0.15s ease;
}
.btn-primary {
  background: var(--accent);
  color: #1A1300;
  border-color: var(--accent);
}
.btn-primary:hover:not(:disabled) {
  background: var(--accent-hover);
  border-color: var(--accent-hover);
}
.btn-primary:disabled {
  background: var(--border);
  border-color: var(--border);
  color: var(--muted);
  cursor: not-allowed;
}

.status-panel { display: none; }
.status-panel.visible { display: block; }
.status-panel.success { border-color: rgba(93, 190, 138, 0.4); }
.status-panel.error { border-color: rgba(232, 99, 90, 0.5); }

.status-message { margin: 0 0 12px; font-size: 14px; font-weight: 500; }
.status-message.success { color: var(--success); }
.status-message.error { color: var(--error); }

.intervals-summary {
  color: var(--muted);
  font-size: 13px;
  margin: 0 0 8px;
}

.interval-table {
  width: 100%;
  border-collapse: collapse;
  font-family: var(--font-mono);
  font-size: 13px;
}
.interval-table th,
.interval-table td {
  padding: 6px 8px;
  text-align: left;
  border-bottom: 1px solid var(--border);
}
.interval-table tr:last-child td { border-bottom: 0; }
.interval-table th {
  font-weight: 600;
  color: var(--muted);
  font-family: var(--font-ui);
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

details {
  border-top: 1px solid var(--border);
  padding-top: 8px;
  margin-top: 8px;
}
details summary {
  cursor: pointer;
  color: var(--muted);
  font-size: 14px;
  padding: 8px 0;
  user-select: none;
  list-style: none;
}
details summary::-webkit-details-marker { display: none; }
details summary::before {
  content: "▸ ";
  display: inline-block;
  transition: transform 0.15s ease;
  margin-right: 4px;
}
details[open] summary::before { transform: rotate(90deg); }
details summary:hover { color: var(--text); }
details[open] summary { color: var(--text); margin-bottom: 12px; }

.advanced-body {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 20px 24px;
}

.field { display: flex; flex-direction: column; gap: 6px; margin-bottom: 16px; }
.field:last-child { margin-bottom: 0; }
.field label {
  font-size: 13px;
  color: var(--muted);
}
.field input[type="text"],
.field select {
  background: var(--bg);
  border: 1px solid var(--border);
  border-radius: 6px;
  padding: 8px 10px;
  color: var(--text);
  font-family: var(--font-mono);
  font-size: 14px;
  width: 100%;
}
.field input[type="text"]:focus,
.field select:focus {
  outline: none;
  border-color: var(--accent);
}

.field-row {
  display: flex;
  gap: 12px;
}
.field-row .field { flex: 1; }

.checkbox-field {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 0;
}
.checkbox-field input { accent-color: var(--accent); }
.checkbox-field label {
  color: var(--text);
  font-size: 14px;
  margin: 0;
}

.field-error {
  color: var(--error);
  font-size: 12px;
  margin-top: 4px;
}
```

- [ ] **Step 2: Verify visually**

Reload `web/index.html` in a browser. Expected: dark charcoal background, centered column ~640px wide, title in white, subtitle in muted gray, dashed-border drop zone, disabled amber convert button (greyed out since no file picked yet), collapsible "▸ Advanced settings" line at the bottom.

- [ ] **Step 3: Commit**

```bash
git add web/style.css
git commit -m "Add dark studio theme"
```

---

### Task 11: UI wiring (`app.js`)

**Files:**
- Modify: `web/app.js`

- [ ] **Step 1: Replace the placeholder with the full UI wiring**

Replace `web/app.js` with:

```js
(function () {
  const dropzone = document.getElementById('dropzone');
  const fileInput = document.getElementById('file-input');
  const fileInfo = document.getElementById('file-info');
  const fileInfoText = document.getElementById('file-info-text');
  const changeFileBtn = document.getElementById('change-file');
  const convertBtn = document.getElementById('convert-btn');
  const statusPanel = document.getElementById('status-panel');
  const statusMessage = document.getElementById('status-message');
  const statusDetails = document.getElementById('status-details');
  const downloadBtn = document.getElementById('download-btn');
  const sheetNameInput = document.getElementById('sheet-name');
  const fpsSelect = document.getElementById('fps');
  const lpStartInput = document.getElementById('lp-start');
  const lpStartError = document.getElementById('lp-start-error');
  const keepMarkersInput = document.getElementById('keep-markers');

  let selectedFile = null;
  let convertedWorkbook = null;
  let outputFilename = null;

  function formatBytes(b) {
    if (b < 1024) return `${b} B`;
    if (b < 1024 * 1024) return `${(b / 1024).toFixed(1)} KB`;
    return `${(b / 1024 / 1024).toFixed(2)} MB`;
  }

  function setFile(file) {
    if (!file.name.toLowerCase().endsWith('.xlsx')) {
      showStatus('error', 'Please select an .xlsx file.');
      return;
    }
    selectedFile = file;
    convertedWorkbook = null;
    outputFilename = null;
    fileInfoText.textContent = `${file.name}  ·  ${formatBytes(file.size)}`;
    fileInfo.hidden = false;
    dropzone.hidden = true;
    convertBtn.disabled = false;
    hideStatus();
    downloadBtn.hidden = true;
  }

  function clearFile() {
    selectedFile = null;
    convertedWorkbook = null;
    outputFilename = null;
    fileInput.value = '';
    fileInfo.hidden = true;
    dropzone.hidden = false;
    convertBtn.disabled = true;
    hideStatus();
    downloadBtn.hidden = true;
  }

  function showStatus(kind, message) {
    statusPanel.classList.remove('success', 'error');
    statusPanel.classList.add('visible', kind);
    statusMessage.className = `status-message ${kind}`;
    statusMessage.textContent = message;
    statusDetails.innerHTML = '';
  }

  function hideStatus() {
    statusPanel.classList.remove('visible', 'success', 'error');
    statusMessage.textContent = '';
    statusDetails.innerHTML = '';
  }

  function renderIntervals(intervals, fps) {
    const tcOf = QCLongPlay.secondsToTc;
    const head = '<thead><tr><th>Reel</th><th>Source</th><th>Long Play</th><th>Duration</th></tr></thead>';
    const body = intervals.map(iv => {
      const src = `${tcOf(iv.reelStart, fps)} → ${tcOf(iv.reelEnd, fps)}`;
      const lp = `${tcOf(iv.lpStart, fps)} → ${tcOf(iv.lpStart + iv.duration, fps)}`;
      const dur = tcOf(iv.duration, fps);
      return `<tr><td>${iv.reel}</td><td>${src}</td><td>${lp}</td><td>${dur}</td></tr>`;
    }).join('');
    return `<table class="interval-table">${head}<tbody>${body}</tbody></table>`;
  }

  function validateLpStart() {
    const v = lpStartInput.value.trim();
    if (!/^\d{2}:\d{2}:\d{2}:\d{2}$/.test(v)) {
      lpStartError.textContent = 'Format: HH:MM:SS:FF (e.g., 01:00:00:00)';
      lpStartError.hidden = false;
      return false;
    }
    lpStartError.hidden = true;
    return true;
  }

  // Drag/drop wiring
  ['dragenter', 'dragover'].forEach(e => {
    dropzone.addEventListener(e, ev => {
      ev.preventDefault();
      dropzone.classList.add('dragover');
    });
  });
  ['dragleave', 'drop'].forEach(e => {
    dropzone.addEventListener(e, ev => {
      ev.preventDefault();
      if (e === 'drop' || ev.target === dropzone) {
        dropzone.classList.remove('dragover');
      }
    });
  });
  dropzone.addEventListener('drop', ev => {
    const file = ev.dataTransfer && ev.dataTransfer.files && ev.dataTransfer.files[0];
    if (file) setFile(file);
  });
  dropzone.addEventListener('click', () => fileInput.click());
  fileInput.addEventListener('change', () => {
    if (fileInput.files[0]) setFile(fileInput.files[0]);
  });
  changeFileBtn.addEventListener('click', clearFile);
  lpStartInput.addEventListener('input', () => {
    if (!lpStartError.hidden) validateLpStart();
  });

  // Convert handler
  convertBtn.addEventListener('click', async () => {
    if (!selectedFile) return;
    if (!validateLpStart()) return;

    convertBtn.disabled = true;
    const originalLabel = convertBtn.textContent;
    convertBtn.textContent = 'Converting…';

    try {
      const buffer = await selectedFile.arrayBuffer();
      const workbook = XLSX.read(buffer, { type: 'array' });

      const opts = {
        sheetName: sheetNameInput.value.trim() || 'QC Report',
        fps: parseInt(fpsSelect.value, 10),
        lpStartTc: lpStartInput.value.trim(),
        dropMarkers: !keepMarkersInput.checked,
      };

      const newWorkbook = QCLongPlay.processWorkbook(workbook, opts);

      // Pull intervals back out for the summary table
      const sourceSheet = workbook.Sheets[opts.sheetName];
      const sourceRows = XLSX.utils.sheet_to_json(sourceSheet, { header: 1, raw: false, defval: null });
      const built = QCLongPlay.buildIntervals(sourceRows, { fps: opts.fps, lpStartTc: opts.lpStartTc });

      convertedWorkbook = newWorkbook;
      const stem = selectedFile.name.replace(/\.xlsx$/i, '');
      outputFilename = `${stem}_LongPlay.xlsx`;

      showStatus('success', `Done. ${built.intervals.length} reel(s) detected.`);
      const summary = '<p class="intervals-summary">Reel breakdown:</p>';
      statusDetails.innerHTML = summary + renderIntervals(built.intervals, opts.fps);
      downloadBtn.hidden = false;
    } catch (err) {
      showStatus('error', err && err.message ? err.message : String(err));
      convertedWorkbook = null;
      outputFilename = null;
      downloadBtn.hidden = true;
    } finally {
      convertBtn.disabled = false;
      convertBtn.textContent = originalLabel;
    }
  });

  // Download handler
  downloadBtn.addEventListener('click', () => {
    if (!convertedWorkbook || !outputFilename) return;
    XLSX.writeFile(convertedWorkbook, outputFilename);
  });

  // Initial state
  clearFile();
})();
```

- [ ] **Step 2: Verify the form interactions**

Reload `web/index.html` in a browser. Verify:

1. The drop zone is visible, the convert button is disabled.
2. Clicking the drop zone opens a file picker (cancel it without selecting).
3. Open Advanced settings — fields appear, no overflow or layout glitches.
4. Type an invalid LP start TC (e.g., `not-a-tc`) — when you click Convert (with no file), nothing happens because the button is still disabled. This step just tests layout, not full conversion (that's Task 12).

- [ ] **Step 3: Commit**

```bash
git add web/app.js
git commit -m "Wire up UI behavior: drag-drop, convert, download"
```

---

### Task 12: End-to-end verification against a known QC report

**Files:**
- None modified — this task is verification only.

This task confirms the JS port matches the Python implementation exactly. It requires a real `.xlsx` file with QC reel boundaries — use any existing file the project has been tested against.

- [ ] **Step 1: Generate a Python baseline**

Use any existing `.xlsx` QC report (in this repo, `convert_longplay.command` and `qc_longplay_convert.py` are the canonical interfaces). From the project root:

```bash
python qc_longplay_convert.py "/path/to/your_QC_Report.xlsx" --fps 24 --lp-start "01:00:00:00"
```

This produces `your_QC_Report_LongPlay.xlsx` (the Python baseline).

- [ ] **Step 2: Open the HTML calculator**

Start a static server inside `web/` and open `index.html`:

```bash
cd web && python -m http.server 8765
```

Open `http://localhost:8765/` in a browser.

- [ ] **Step 3: Run the same conversion in the browser**

Drag `/path/to/your_QC_Report.xlsx` into the drop zone. Confirm:
- File info shows the filename and size.
- Convert button enables.
- Click Convert. Status panel turns green, shows the reel count and the interval breakdown table with timecodes formatted in monospace.
- Download button appears. Click it — browser downloads `your_QC_Report_LongPlay.xlsx`.

- [ ] **Step 4: Compare outputs cell-for-cell**

Use a quick Python diff to verify:

```bash
python <<'EOF'
import sys
import pandas as pd
py_path = "/path/to/your_QC_Report_LongPlay.xlsx"          # Python baseline
js_path = "/path/to/Downloads/your_QC_Report_LongPlay.xlsx" # Browser output

py = pd.read_excel(py_path, header=None, sheet_name=0).fillna('')
js = pd.read_excel(js_path, header=None, sheet_name=0).fillna('')

if py.shape != js.shape:
    print(f"FAIL: shape differs — Python {py.shape}, JS {js.shape}")
    sys.exit(1)

mismatches = []
for r in range(py.shape[0]):
    for c in range(py.shape[1]):
        a, b = py.iat[r, c], js.iat[r, c]
        if str(a) != str(b):
            mismatches.append((r, c, a, b))

if mismatches:
    print(f"FAIL: {len(mismatches)} cell mismatches")
    for r, c, a, b in mismatches[:10]:
        print(f"  ({r},{c}): py={a!r}  js={b!r}")
    sys.exit(1)

print(f"PASS: {py.shape[0]} rows x {py.shape[1]} cols match cell-for-cell")
EOF
```

Expected: `PASS: ...`. If mismatches appear, the JS port has diverged from the Python; investigate which function differs (likely `convertTc`, `processRows`, or boundary detection) and fix.

- [ ] **Step 5: Try the error paths**

In the browser, try each:
- Drop a non-`.xlsx` file (e.g., a `.txt`). Expected: red status panel: "Please select an .xlsx file."
- Set Advanced → Sheet name to `Nope`, click Convert. Expected: red status panel: "Sheet 'Nope' not found. Available sheets: ..."
- Set LP start TC to `bad`, click Convert. Expected: inline error under the field: "Format: HH:MM:SS:FF ..." Conversion is blocked.

- [ ] **Step 6: Commit any fixes**

If Step 4 or Step 5 surfaces bugs, fix them in the relevant module and add a regression test in `web/test.html`. Then:

```bash
git add web/
git commit -m "Fix <bug> uncovered by smoke test"
```

If no fixes are needed, no commit for this task.

---

## Self-Review

**Spec coverage:**

- Vendored SheetJS: Task 1 ✓
- Module split (qc_longplay.js / app.js / style.css / index.html): Tasks 1, 9, 10, 11 ✓
- JS API parity (tcToSeconds, secondsToTc, framesToSeconds, buildIntervals, convertTc, processRows, processWorkbook): Tasks 3–8 ✓
- Closed-interval matching: Task 6 (test "reel 1 end (closed interval, kept)") ✓
- Per-reel frame correction: Task 6 (tests for reel 2 +1f, reel 3 +2f) ✓
- Final Program End forced TC: Task 7 (test "drop markers: final col 1 forced") ✓
- Drop-markers default true / opt-out: Task 7 ✓
- "No reel boundaries" error message matches Python wording: Task 5 ✓
- Sheet-not-found error: Task 8 ✓
- Floating-point guard in secondsToTc: Task 4 ✓
- UI: drop zone, file info, convert button, status panel, download button, advanced settings: Tasks 9, 11 ✓
- Studio dark aesthetic: Task 10 ✓
- LP start TC validation in form: Task 11 ✓
- System-font-only typography: Task 10 ✓
- File type guard at upload: Task 11 ✓
- Output filename `<stem>_LongPlay.xlsx`: Task 11 ✓
- Output sheet name `<original> LongPlay`: Task 8 ✓
- End-to-end parity check vs Python: Task 12 ✓

**Placeholder scan:** No "TBD" / "implement later" / vague test references. Each step contains the actual code or the actual command.

**Type consistency:** Interval object uses `{ reel, reelStart, reelEnd, lpStart, duration }` consistently in Tasks 5, 6, 7, 11. `QCLongPlay` namespace is consistent across all files. `processWorkbook` opts shape consistent in Tasks 8 and 11.

**Scope check:** One implementation plan, one feature, one PR-sized change. Reasonable.
