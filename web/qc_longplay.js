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
