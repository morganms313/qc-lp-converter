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

  global.QCLongPlay = {
    _internal: { TC_PATTERN, validateFps },
    tcToSeconds,
    framesToSeconds,
    secondsToTc,
    buildIntervals,
    convertTc,
    processRows,
  };
})(window);
