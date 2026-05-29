(function () {
  const dropzone = document.getElementById('dropzone');
  const fileInput = document.getElementById('file-input');
  const fileInfo = document.getElementById('file-info');
  const fileInfoText = document.getElementById('file-info-text');
  const changeFileBtn = document.getElementById('change-file');
  const convertBtn = document.getElementById('convert-btn');
  const resetBtn = document.getElementById('reset-btn');
  const warningPanel = document.getElementById('warning-panel');
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
    resetBtn.hidden = false;
    hideStatus();
    hideWarnings();
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
    resetBtn.hidden = true;
    hideStatus();
    hideWarnings();
    downloadBtn.hidden = true;
  }

  // Reset advanced options back to their defaults.
  function resetAdvanced() {
    sheetNameInput.value = 'QC Report';
    fpsSelect.value = '24';
    lpStartInput.value = '01:00:00:00';
    keepMarkersInput.checked = false;
    lpStartError.hidden = true;
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

  function showWarnings(list) {
    if (!list || !list.length) { hideWarnings(); return; }
    const items = list.map(w => `<li>${escapeHtml(w)}</li>`).join('');
    warningPanel.innerHTML =
      `<p class="warning-title">Warning</p><ul>${items}</ul>`;
    warningPanel.classList.add('visible');
  }

  function hideWarnings() {
    warningPanel.classList.remove('visible');
    warningPanel.innerHTML = '';
  }

  function escapeHtml(s) {
    return String(s)
      .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;').replace(/'/g, '&#39;');
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
  resetBtn.addEventListener('click', () => {
    clearFile();
    resetAdvanced();
  });
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
      let workbook;
      try {
        workbook = XLSX.read(buffer, { type: 'array' });
      } catch (_) {
        throw new Error("Couldn't read this file. Make sure it's a valid Excel workbook.");
      }

      const opts = {
        sheetName: sheetNameInput.value.trim() || 'QC Report',
        fps: parseInt(fpsSelect.value, 10),
        lpStartTc: lpStartInput.value.trim(),
        dropMarkers: !keepMarkersInput.checked,
      };

      const newWorkbook = QCLongPlay.processWorkbook(workbook, opts);

      // Pull intervals back out for the summary table (same full-range read
      // as processWorkbook, so an understated sheet dimension can't drop rows).
      const sourceSheet = workbook.Sheets[opts.sheetName];
      const sourceRows = QCLongPlay.sheetToRows(sourceSheet);
      const built = QCLongPlay.buildIntervals(sourceRows, { fps: opts.fps, lpStartTc: opts.lpStartTc });

      convertedWorkbook = newWorkbook;
      const stem = selectedFile.name.replace(/\.xlsx$/i, '');
      outputFilename = `${stem}_LongPlay.xlsx`;

      showWarnings(built.warnings);
      showStatus('success', `Done. ${built.intervals.length} reel(s) detected.`);
      const summary = '<p class="intervals-summary">Reel breakdown:</p>';
      statusDetails.innerHTML = summary + renderIntervals(built.intervals, opts.fps);
      downloadBtn.hidden = false;
    } catch (err) {
      hideWarnings();
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
