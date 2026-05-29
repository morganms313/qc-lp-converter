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

    // Find the last parseable timecode in the TC column (scanning bottom-up),
    // used to infer a missing end boundary for the final reel.
    function lastTcInfo() {
      for (let i = rows.length - 1; i >= 0; i--) {
        const row = rows[i] || [];
        const v = row[tcCol];
        if (typeof v === 'string' && tcToSeconds(v, fps) !== null) {
          return { tc: v, row: i };
        }
      }
      return null;
    }

    const expectedBoundaryMsg = (r) =>
      `Expected a row with 'Program End - Reel ${r}' in column 4 ` +
      `and a timecode (HH:MM:SS:FF) in column 2.`;

    const warnings = [];
    const intervals = [];
    const sortedReels = Object.keys(reelBounds).map(Number).sort((a, b) => a - b);
    const lastReel = sortedReels[sortedReels.length - 1];

    for (const r of sortedReels) {
      const rs = tcToSeconds(reelBounds[r].startTc, fps);
      if (rs === null) {
        throw new Error(
          `Reel ${r} has no valid 'Program Start - Reel ${r}' timecode ` +
          `(HH:MM:SS:FF in column 2).`
        );
      }

      let re = tcToSeconds(reelBounds[r].endTc, fps);
      if (re === null) {
        // Missing or unparseable Program End marker.
        if (r === lastReel) {
          // Last reel: fall back to the last timecode in the sheet, with a warning.
          const info = lastTcInfo();
          const inferred = info ? tcToSeconds(info.tc, fps) : null;
          if (info === null || inferred === null || inferred <= rs) {
            throw new Error(
              `Reel ${r} is missing its 'Program End - Reel ${r}' marker and no ` +
              `usable timecode was found after its start to infer the end. ` +
              expectedBoundaryMsg(r)
            );
          }
          re = inferred;
          reelBounds[r].endRow = info.row; // so the slice extends to the inferred end
          warnings.push(
            `Reel ${r} had no valid 'Program End - Reel ${r}' marker — used the ` +
            `last timecode in the sheet (${info.tc}) as its end. Verify this is correct.`
          );
        } else {
          // Middle reel: cannot safely infer. Fail with a clear, actionable message.
          throw new Error(
            `Reel ${r} is missing its 'Program End - Reel ${r}' marker. ` +
            expectedBoundaryMsg(r)
          );
        }
      }

      const dur = re - rs;
      intervals.push({ reel: r, reelStart: rs, reelEnd: re, lpStart: lpCursor, duration: dur });
      lpCursor += dur;
    }

    const allBounds = Object.values(reelBounds);
    const startRows = allBounds.map(b => b.startRow).filter(x => x != null);
    const endRows = allBounds.map(b => b.endRow).filter(x => x != null);
    const firstStart = Math.min.apply(null, startRows);
    const lastEnd = endRows.length
      ? Math.max.apply(null, endRows)
      : Math.max.apply(null, startRows);

    return { intervals, firstStart, lastEnd, warnings };
  }

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

  // Compute the true used range of a worksheet from its actual cell addresses,
  // taking the union with the declared '!ref'. Some exports (e.g. these QC
  // reports) declare a too-small <dimension>, e.g. "A1:M87" while real data
  // runs to row 359; reading by the declared range would silently drop every
  // row below it (and with it all the reel markers).
  function fullSheetRange(sheet) {
    const ADDR = /^([A-Z]+)(\d+)$/;
    let endR = 0, endC = 0;
    if (sheet['!ref']) {
      const dr = XLSX.utils.decode_range(sheet['!ref']);
      endR = dr.e.r;
      endC = dr.e.c;
    }
    for (const k in sheet) {
      if (k[0] === '!') continue;
      const m = ADDR.exec(k);
      if (!m) continue;
      const r = parseInt(m[2], 10) - 1;
      const c = XLSX.utils.decode_col(m[1]);
      if (r > endR) endR = r;
      if (c > endC) endC = c;
    }
    return XLSX.utils.encode_range({ s: { r: 0, c: 0 }, e: { r: endR, c: endC } });
  }

  // Read a worksheet to a row-major array of arrays, reading the full used
  // range (not just the possibly-understated declared dimension).
  function sheetToRows(sheet) {
    if (typeof XLSX === 'undefined') {
      throw new Error('SheetJS (XLSX) is not loaded. Make sure vendor/xlsx.full.min.js is included.');
    }
    return XLSX.utils.sheet_to_json(sheet, {
      header: 1, raw: false, defval: null, range: fullSheetRange(sheet),
    });
  }

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
    const rows = sheetToRows(sheet);
    const converted = processRows(rows, { fps, lpStartTc, dropMarkers });

    const newSheet = XLSX.utils.aoa_to_sheet(converted);
    const newWorkbook = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(newWorkbook, newSheet, `${sheetName} LongPlay`);
    return newWorkbook;
  }

  global.QCLongPlay = {
    _internal: { TC_PATTERN, validateFps },
    tcToSeconds,
    framesToSeconds,
    secondsToTc,
    buildIntervals,
    convertTc,
    processRows,
    processWorkbook,
    fullSheetRange,
    sheetToRows,
  };
})(window);
