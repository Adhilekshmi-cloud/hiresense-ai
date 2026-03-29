/**
 * AI Resume Screener — Frontend Application
 * Connects to FastAPI backend for resume screening, scoring, and model comparison.
 */

const API_BASE = 'http://127.0.0.1:8000';

// ── DOM Elements ───────────────────────────────────────────────────────────

const $ = (sel) => document.querySelector(sel);
const $$ = (sel) => document.querySelectorAll(sel);

const uploadZone = $('#uploadZone');
const fileInput = $('#fileInput');
const fileList = $('#fileList');
const uploadStatus = $('#uploadStatus');
const jobDescription = $('#jobDescription');
const modelSelect = $('#modelSelect');
const btnScreen = $('#btnScreen');
const btnCompare = $('#btnCompare');
const btnDownload = $('#btnDownload');
const resultsSection = $('#resultsSection');
const metricsRow = $('#metricsRow');
const candidateList = $('#candidateList');
const comparisonSection = $('#comparisonSection');
const timingCards = $('#timingCards');
const comparisonTable = $('#comparisonTable');

// ── State ──────────────────────────────────────────────────────────────────

const state = {
  files: [],            // { file, name, status: 'pending'|'uploaded'|'error' }
  results: null,        // screening results
  comparison: null,     // model comparison results
};

// ── Upload Zone Drag & Drop ────────────────────────────────────────────────

uploadZone.addEventListener('dragover', (e) => {
  e.preventDefault();
  uploadZone.classList.add('dragover');
});

uploadZone.addEventListener('dragleave', () => {
  uploadZone.classList.remove('dragover');
});

uploadZone.addEventListener('drop', (e) => {
  e.preventDefault();
  uploadZone.classList.remove('dragover');
  handleFiles(e.dataTransfer.files);
});

fileInput.addEventListener('change', () => {
  handleFiles(fileInput.files);
  fileInput.value = '';
});

function handleFiles(fileListInput) {
  for (const file of fileListInput) {
    const ext = file.name.split('.').pop().toLowerCase();
    if (!['pdf', 'docx', 'txt'].includes(ext)) continue;
    if (state.files.some(f => f.name === file.name)) continue;
    state.files.push({ file, name: file.name, status: 'pending' });
  }
  renderFileList();
  uploadAllFiles();
}

function renderFileList() {
  fileList.innerHTML = state.files.map((f, i) => `
    <div class="file-item" data-index="${i}">
      <span class="file-item__name">
        📄 ${f.name}
      </span>
      <div style="display:flex;align-items:center;gap:0.5rem;">
        <span class="file-item__status file-item__status--${f.status === 'uploaded' ? 'success' : 'pending'}">
          ${f.status === 'uploaded' ? '✓ Uploaded' : f.status === 'error' ? '✗ Error' : '⏳ Pending'}
        </span>
        <button class="file-item__remove" onclick="removeFile(${i})">✕</button>
      </div>
    </div>
  `).join('');
  updateButtons();
}

window.removeFile = function(index) {
  state.files.splice(index, 1);
  renderFileList();
};

async function uploadAllFiles() {
  for (const entry of state.files) {
    if (entry.status !== 'pending') continue;
    try {
      const formData = new FormData();
      formData.append('file', entry.file);
      const res = await fetch(`${API_BASE}/api/upload-resume`, {
        method: 'POST',
        body: formData,
      });
      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || 'Upload failed');
      }
      entry.status = 'uploaded';
    } catch (e) {
      entry.status = 'error';
      showStatus(uploadStatus, `Failed to upload ${entry.name}: ${e.message}`, 'error');
    }
    renderFileList();
  }

  const uploaded = state.files.filter(f => f.status === 'uploaded').length;
  if (uploaded > 0) {
    showStatus(uploadStatus, `${uploaded} resume(s) uploaded and processed`, 'success');
  }
}

// ── Buttons ────────────────────────────────────────────────────────────────

function updateButtons() {
  const hasResumes = state.files.some(f => f.status === 'uploaded');
  const hasJD = jobDescription.value.trim().length >= 10;
  btnScreen.disabled = !(hasResumes && hasJD);
  btnCompare.disabled = !(hasResumes && hasJD);
}

jobDescription.addEventListener('input', updateButtons);

// ── Screen Resumes ─────────────────────────────────────────────────────────

btnScreen.addEventListener('click', async () => {
  const jd = jobDescription.value.trim();
  if (jd.length < 10) return;

  btnScreen.disabled = true;
  btnScreen.innerHTML = '<span class="spinner"></span> Analyzing...';
  resultsSection.classList.add('hidden');
  comparisonSection.classList.add('hidden');

  try {
    const res = await fetch(`${API_BASE}/api/screen`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        job_description: jd,
        model_name: modelSelect.value,
        top_n: 50,
      }),
    });

    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Screening failed');
    }

    state.results = await res.json();
    renderResults();
  } catch (e) {
    showStatus(uploadStatus, `Screening error: ${e.message}`, 'error');
  } finally {
    btnScreen.disabled = false;
    btnScreen.innerHTML = '🔍 Screen Resumes';
    updateButtons();
  }
});

// ── Render Results ─────────────────────────────────────────────────────────

function renderResults() {
  const { candidates, model_used, total_resumes } = state.results;
  resultsSection.classList.remove('hidden');

  // Metrics
  const topScore = candidates.length > 0 ? candidates[0].final_score : 0;
  const avgScore = candidates.length > 0
    ? (candidates.reduce((s, c) => s + c.final_score, 0) / candidates.length)
    : 0;
  const strongCount = candidates.filter(c => c.verdict === 'STRONG MATCH').length;

  metricsRow.innerHTML = `
    ${metricCard(total_resumes, 'Total Resumes')}
    ${metricCard(topScore.toFixed(1) + '%', 'Top Score')}
    ${metricCard(avgScore.toFixed(1) + '%', 'Avg Score')}
    ${metricCard(strongCount, 'Strong Matches')}
  `;

  // Candidate cards
  candidateList.innerHTML = candidates.map((c, i) => candidateCard(c, i)).join('');

  // Scroll to results
  resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

function metricCard(value, label) {
  return `
    <div class="metric">
      <div class="metric__value">${value}</div>
      <div class="metric__label">${label}</div>
    </div>
  `;
}

function candidateCard(c, index) {
  const verdictClass = {
    'STRONG MATCH': 'strong',
    'GOOD MATCH': 'good',
    'PARTIAL MATCH': 'partial',
    'WEAK MATCH': 'weak',
  }[c.verdict] || 'partial';

  const matchedTags = c.matched_skills.map(s =>
    `<span class="skill-tag skill-tag--match">${s}</span>`
  ).join('');

  const missingTags = c.missing_skills.map(s =>
    `<span class="skill-tag skill-tag--missing">${s}</span>`
  ).join('');

  const strengthItems = c.strengths.map(s => `<li>${s}</li>`).join('');
  const weaknessItems = c.weaknesses.map(w => `<li>${w}</li>`).join('');

  const sb = c.score_breakdown;

  return `
    <div class="candidate" id="candidate-${index}" style="animation-delay: ${index * 0.08}s">
      <div class="candidate__header" onclick="toggleCandidate(${index})">
        <div class="candidate__left">
          <div class="candidate__rank">${c.rank}</div>
          <div class="candidate__name">${c.filename}</div>
        </div>
        <div class="candidate__right">
          <span class="candidate__verdict verdict--${verdictClass}">${c.verdict}</span>
          <span class="candidate__score">${c.final_score.toFixed(1)}%</span>
          <button class="candidate__toggle">▼</button>
        </div>
      </div>
      <div class="candidate__details">
        <div class="candidate__body">
          <p class="candidate__summary">${c.summary}</p>

          <div class="score-grid">
            ${scoreBar('Skills', sb.skills, 'skills')}
            ${scoreBar('Semantic', sb.semantic, 'semantic')}
            ${scoreBar('Experience', sb.experience, 'experience')}
            ${scoreBar('Education', sb.education, 'education')}
          </div>

          <div class="skills-section">
            <div>
              <div class="skills-group__title">✅ Matched Skills</div>
              <div class="skills-group__tags">
                ${matchedTags || '<span style="color:var(--text-muted);font-size:0.8rem;">No matching skills</span>'}
              </div>
            </div>
            <div>
              <div class="skills-group__title">❌ Missing Skills</div>
              <div class="skills-group__tags">
                ${missingTags || '<span style="color:var(--text-muted);font-size:0.8rem;">No missing skills</span>'}
              </div>
            </div>
          </div>

          <div class="insights">
            <div class="insight-group insight-group--strengths">
              <div class="insight-group__title">💪 Strengths</div>
              <ul>${strengthItems || '<li>No specific strengths identified</li>'}</ul>
            </div>
            <div class="insight-group insight-group--weaknesses">
              <div class="insight-group__title">⚠️ Weaknesses</div>
              <ul>${weaknessItems || '<li>No specific weaknesses identified</li>'}</ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  `;
}

function scoreBar(label, value, type) {
  return `
    <div class="score-item">
      <div class="score-item__label">${label}</div>
      <div class="score-item__bar">
        <div class="score-item__fill score-item__fill--${type}" style="width: ${value}%"></div>
      </div>
      <div class="score-item__value">${value.toFixed(1)}%</div>
    </div>
  `;
}

window.toggleCandidate = function(index) {
  const el = document.getElementById(`candidate-${index}`);
  el.classList.toggle('expanded');
};

// ── CSV Download ───────────────────────────────────────────────────────────

btnDownload.addEventListener('click', () => {
  if (!state.results) return;

  const rows = [
    ['Rank', 'Filename', 'Final Score (%)', 'Verdict', 'Skills (%)', 'Semantic (%)', 'Experience (%)', 'Education (%)', 'Matched Skills', 'Missing Skills'],
    ...state.results.candidates.map(c => [
      c.rank,
      c.filename,
      c.final_score.toFixed(2),
      c.verdict,
      c.score_breakdown.skills.toFixed(2),
      c.score_breakdown.semantic.toFixed(2),
      c.score_breakdown.experience.toFixed(2),
      c.score_breakdown.education.toFixed(2),
      `"${c.matched_skills.join(', ')}"`,
      `"${c.missing_skills.join(', ')}"`,
    ]),
  ];

  const csv = rows.map(r => r.join(',')).join('\n');
  const blob = new Blob([csv], { type: 'text/csv' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = 'screening_results.csv';
  a.click();
  URL.revokeObjectURL(url);
});

// ── Model Comparison ───────────────────────────────────────────────────────

btnCompare.addEventListener('click', async () => {
  const jd = jobDescription.value.trim();
  if (jd.length < 10) return;

  btnCompare.disabled = true;
  btnCompare.innerHTML = '<span class="spinner"></span> Comparing...';
  comparisonSection.classList.add('hidden');

  try {
    const res = await fetch(`${API_BASE}/api/compare-models`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ job_description: jd }),
    });

    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Comparison failed');
    }

    state.comparison = await res.json();
    renderComparison();
  } catch (e) {
    showStatus(uploadStatus, `Comparison error: ${e.message}`, 'error');
  } finally {
    btnCompare.disabled = false;
    btnCompare.innerHTML = '📊 Compare Models';
    updateButtons();
  }
});

function renderComparison() {
  const { models, resume_filenames } = state.comparison;
  comparisonSection.classList.remove('hidden');

  // Timing cards
  timingCards.innerHTML = models.map(m => `
    <div class="timing-card">
      <div class="timing-card__value">${m.time_seconds.toFixed(3)}s</div>
      <div class="timing-card__label">${m.model}</div>
    </div>
  `).join('');

  // Score comparison table
  const thead = comparisonTable.querySelector('thead');
  const tbody = comparisonTable.querySelector('tbody');

  thead.innerHTML = `<tr>
    <th>Resume</th>
    ${models.map(m => `<th>${m.model}</th>`).join('')}
  </tr>`;

  tbody.innerHTML = resume_filenames.map((name, i) => `
    <tr>
      <td>${name}</td>
      ${models.map(m => `<td>${(m.scores[i] * 100).toFixed(2)}%</td>`).join('')}
    </tr>
  `).join('');

  comparisonSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

// ── Utility ────────────────────────────────────────────────────────────────

function showStatus(container, message, type) {
  container.innerHTML = `<div class="status status--${type}">${message}</div>`;
  setTimeout(() => {
    const el = container.querySelector('.status');
    if (el) el.style.opacity = '0';
    setTimeout(() => container.innerHTML = '', 300);
  }, 5000);
}
