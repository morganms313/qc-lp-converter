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

  global.QCLongPlay = {
    _internal: { TC_PATTERN, validateFps },
    tcToSeconds,
    framesToSeconds,
    secondsToTc,
  };
})(window);
