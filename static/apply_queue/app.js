/* Apply queue — application shell.
 *
 * Server state is authoritative in LIVE mode: every action posts to the repo
 * and the page reconciles with what came back. localStorage is only a cache
 * for static-file mode, where there is no server to write to.
 *
 * Interaction follows the apple-design principles:
 *   - feedback on pointer-down, continuous during the gesture
 *   - 1:1 tracking with pointer capture, honouring the grab offset
 *   - springs everywhere, always interruptible and velocity-aware
 *   - flicks project their landing point instead of snapping from the release
 *   - boundaries rubber-band rather than hard-stop
 */

import { Spring, SPRINGS, project, rubberband, VelocityTracker, prefersReducedMotion } from './spring.js';

/* ------------------------------------------------------------------ state */

const bootstrapEl = document.getElementById('queue-bootstrap');
const BOOT = JSON.parse(bootstrapEl?.textContent || '{}');

const state = {
  day: BOOT.day || '',
  dates: BOOT.dates || [],
  live: BOOT.live === true,
  items: BOOT.items || [],
  applied: new Set(),
  passed: new Map(),
  filters: { geo: 'all', company: 'all', gtc: 'all', tier: 'all', pass: 'active' },
  focusIndex: -1,
  lastAction: null,
  connection: 'idle',
};

const STORAGE_APPLIED = () => `apply-queue:applied:${state.day}`;
const STORAGE_PASSED = () => `apply-queue:passed:${state.day}`;

const els = {
  queue: document.getElementById('queue'),
  empty: document.getElementById('empty'),
  lede: document.getElementById('lede'),
  progress: document.getElementById('progress'),
  syncPill: document.getElementById('syncPill'),
  dateSelect: document.getElementById('dateSelect'),
  toastStack: document.getElementById('toastStack'),
  chrome: document.getElementById('chrome'),
  modeNote: document.getElementById('modeNote'),
  openNext: document.getElementById('openNext'),
  exportPasses: document.getElementById('exportPasses'),
};

const rowNodes = new Map(); // key -> { li, inner, spring }

/* ------------------------------------------------------------- utilities */

function normKey(raw) {
  let u = (raw || '').split('?')[0];
  while (u.endsWith('/')) u = u.slice(0, -1);
  return u.toLowerCase();
}

function itemKey(item) {
  return item.key || normKey(item.url);
}

function esc(value) {
  return String(value ?? '').replace(/[&<>"']/g, (c) => (
    { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]
  ));
}

function setSync(stateName, text) {
  state.connection = stateName;
  if (!els.syncPill) return;
  els.syncPill.dataset.state = stateName;
  els.syncPill.querySelector('.sync-text').textContent = text;
}

/* ------------------------------------------------------------------ toast */

function toast({ title, sub, kind = 'info', undo = null, timeout = 8000 }) {
  const node = document.createElement('div');
  node.className = 'toast';
  node.dataset.kind = kind;
  node.innerHTML = `
    <div class="toast-text">
      <div class="toast-title">${esc(title)}</div>
      ${sub ? `<div class="toast-sub">${esc(sub)}</div>` : ''}
    </div>`;

  if (undo) {
    const btn = document.createElement('button');
    btn.type = 'button';
    btn.className = 'toast-undo';
    btn.textContent = 'Undo';
    btn.addEventListener('click', async () => {
      btn.disabled = true;
      await undo();
      dismiss();
    });
    node.appendChild(btn);
  }

  els.toastStack.appendChild(node);

  // Materialise: the surface arrives rather than plain-fading in.
  const reduced = prefersReducedMotion();
  if (reduced) {
    node.style.opacity = '0';
    requestAnimationFrame(() => {
      node.style.transition = 'opacity 160ms ease';
      node.style.opacity = '1';
    });
  } else {
    const enter = new Spring({
      from: 0, to: 1, ...SPRINGS.ui,
      onUpdate: (v) => {
        node.style.opacity = String(Math.min(1, Math.max(0, v)));
        node.style.transform = `translateY(${(1 - v) * 16}px) scale(${0.97 + v * 0.03})`;
      },
    });
    enter.start();
  }

  let timer = timeout ? setTimeout(dismiss, timeout) : 0;
  node.addEventListener('pointerenter', () => { if (timer) clearTimeout(timer); });
  node.addEventListener('pointerleave', () => { if (timeout) timer = setTimeout(dismiss, 2500); });

  function dismiss() {
    if (timer) clearTimeout(timer);
    if (!node.isConnected) return;
    if (prefersReducedMotion()) {
      node.style.transition = 'opacity 140ms ease';
      node.style.opacity = '0';
      setTimeout(() => node.remove(), 150);
      return;
    }
    // Spatial consistency: it leaves the way it arrived.
    const exit = new Spring({
      from: 1, to: 0, damping: 1, response: 0.25,
      onUpdate: (v) => {
        node.style.opacity = String(Math.max(0, v));
        node.style.transform = `translateY(${(1 - v) * 16}px) scale(${0.97 + v * 0.03})`;
      },
      onRest: () => node.remove(),
    });
    exit.start();
  }

  return dismiss;
}

/* ------------------------------------------------------------- filtering */

const FILTER_DEFS = [
  ['geoFilters', 'geo', [
    ['all', 'All locations'],
    ['boston_ma', 'Boston / MA'],
    ['bay_area', 'Bay Area / SF'],
    ['other', 'Other US'],
  ]],
  ['classFilters', 'company', [
    ['all', 'All companies'],
    ['big_tech', 'Big tech'],
    ['biotech', 'Biotech / health'],
    ['startup', 'Startup / scaleup'],
    ['other', 'Other'],
  ]],
  ['gtcFilters', 'gtc', [
    ['all', 'GTC: any'],
    ['yes', 'GTC sponsor'],
    ['no', 'Not GTC'],
  ]],
  ['tierFilters', 'tier', [
    ['all', 'All tiers'],
    ['A', 'Today'],
    ['B', 'Backlog'],
    ['C', 'Verify level'],
    ['D', 'Older'],
  ]],
  ['passFilters', 'pass', [
    ['active', 'Active'],
    ['passed', 'Passed'],
    ['all', 'Active + passed'],
  ]],
];

function buildFilters() {
  FILTER_DEFS.forEach(([id, key, options]) => {
    const host = document.getElementById(id);
    if (!host) return;
    host.textContent = '';
    options.forEach(([value, label]) => {
      const btn = document.createElement('button');
      btn.type = 'button';
      btn.className = 'chip';
      btn.textContent = label;
      btn.dataset.value = value;
      btn.setAttribute('aria-pressed', String(state.filters[key] === value));
      btn.addEventListener('click', () => {
        state.filters[key] = value;
        [...host.querySelectorAll('.chip')].forEach((chip) => {
          chip.setAttribute('aria-pressed', String(chip.dataset.value === value));
        });
        applyFilters();
      });
      host.appendChild(btn);
    });
  });
}

function isVisible(item) {
  const key = itemKey(item);
  const passed = state.passed.has(key);
  const f = state.filters;
  if (f.geo !== 'all' && item.geo !== f.geo) return false;
  if (f.company !== 'all' && item.company_class !== f.company) return false;
  if (f.gtc !== 'all' && (item.gtc_sponsor || 'no') !== f.gtc) return false;
  if (f.tier !== 'all' && item.tier !== f.tier) return false;
  if (f.pass === 'active' && passed) return false;
  if (f.pass === 'passed' && !passed) return false;
  return true;
}

function applyFilters() {
  let shown = 0;
  state.items.forEach((item) => {
    const node = rowNodes.get(itemKey(item));
    if (!node) return;
    const visible = isVisible(item);
    node.li.hidden = !visible;
    if (visible) shown += 1;
  });
  els.empty.hidden = shown > 0;
  paint();
}

/* --------------------------------------------------------------- rendering */

function rowMarkup(item, index) {
  const pills = [];
  if (item.gtc_sponsor === 'yes') {
    pills.push(`<span class="pill pill-gtc" title="${esc(item.gtc_match || '')}">GTC sponsor</span>`);
  }
  if (item.geo_label) pills.push(`<span class="pill pill-geo-${esc(item.geo)}">${esc(item.geo_label)}</span>`);
  if (item.class_label) pills.push(`<span class="pill pill-class-${esc(item.company_class)}">${esc(item.class_label)}</span>`);
  if (item.tier_label) pills.push(`<span class="pill">${esc(item.tier)} · ${esc(item.tier_label)}</span>`);
  if (item.job_id) pills.push(`<span class="pill">${esc(item.job_id)}</span>`);

  const meta = [
    item.location || 'location unknown',
    item.lane ? `${esc(item.lane)} lane` : '',
    item.cluster || '',
    item.grad ? `resume ${esc(item.grad)}` : '',
  ].filter(Boolean).join(' · ');

  return `
    <div class="row-affordance" aria-hidden="true">
      <span class="aff-applied">Applied</span>
      <span class="aff-pass">Pass</span>
    </div>
    <div class="row-inner">
      <div class="row-main">
        <div class="row-index">${String(index + 1).padStart(2, '0')}</div>
        <h2 class="row-title">
          <span class="row-company">${esc(item.company)}</span>
          <span class="row-role">— ${esc(item.role)}</span>
        </h2>
        <p class="row-meta">${meta}</p>
        ${item.reason ? `<p class="row-why">${esc(item.reason)}</p>` : ''}
        <div class="pills">${pills.join('')}</div>
      </div>
      <div class="row-actions">
        <a class="action action-open" href="${esc(item.url)}" target="_blank" rel="noopener">Open</a>
        <button type="button" class="action action-applied" data-act="applied">Applied</button>
        <button type="button" class="action action-pass" data-act="pass">Pass</button>
      </div>
    </div>`;
}

function render() {
  els.queue.textContent = '';
  rowNodes.clear();

  state.items.forEach((item, index) => {
    const key = itemKey(item);
    const li = document.createElement('li');
    li.className = 'row';
    li.dataset.key = key;
    li.innerHTML = rowMarkup(item, index);
    els.queue.appendChild(li);

    const inner = li.querySelector('.row-inner');
    const spring = new Spring({
      from: 0, to: 0, ...SPRINGS.ui,
      onUpdate: (v) => { inner.style.transform = `translateX(${v}px)`; },
    });

    rowNodes.set(key, { li, inner, spring, item });

    li.querySelector('[data-act="applied"]').addEventListener('click', () => markApplied(item));
    li.querySelector('[data-act="pass"]').addEventListener('click', () => markPass(item));
    attachSwipe(li, inner, spring, item);
  });

  buildDateSelect();
  applyFilters();
}

function paint() {
  state.items.forEach((item) => {
    const node = rowNodes.get(itemKey(item));
    if (!node) return;
    const key = itemKey(item);
    node.li.classList.toggle('is-applied', state.applied.has(key));
    node.li.classList.toggle('is-passed', state.passed.has(key));
  });

  const visible = state.items.filter(isVisible);
  const done = visible.filter((i) => state.applied.has(itemKey(i))).length;
  const totalApplied = state.items.filter((i) => state.applied.has(itemKey(i))).length;
  const totalPassed = state.items.filter((i) => state.passed.has(itemKey(i))).length;

  els.progress.textContent = `${done} / ${visible.length} in view · ${totalApplied} applied · ${totalPassed} passed`;

  const remaining = visible.length - done;
  els.lede.textContent = remaining > 0
    ? `${remaining} role${remaining === 1 ? '' : 's'} waiting on you for ${state.day}.`
    : `Nothing left in this view for ${state.day}.`;
}

function buildDateSelect() {
  if (!els.dateSelect) return;
  const dates = state.dates.length ? state.dates : [state.day];
  els.dateSelect.textContent = '';
  dates.forEach((d) => {
    const opt = document.createElement('option');
    opt.value = d;
    opt.textContent = d;
    opt.selected = d === state.day;
    els.dateSelect.appendChild(opt);
  });
  els.dateSelect.disabled = !state.live || dates.length < 2;
  els.dateSelect.onchange = () => loadQueue(els.dateSelect.value);
}

/* ----------------------------------------------------------------- swipe */

const COMMIT_DISTANCE = 96;   // px of travel that commits an action
const DRAG_THRESHOLD = 8;     // px of hysteresis before we own the gesture

function attachSwipe(li, inner, spring, item) {
  const tracker = new VelocityTracker();
  let pointerId = null;
  let startX = 0;
  let startY = 0;
  let grabOffset = 0;
  let owning = false;

  inner.addEventListener('pointerdown', (event) => {
    if (event.button !== 0) return;
    if (event.target.closest('a, button')) return; // let real controls win
    pointerId = event.pointerId;
    startX = event.clientX;
    startY = event.clientY;
    grabOffset = spring.value;
    owning = false;
    tracker.reset();
    tracker.add(event.clientX, event.timeStamp);
  });

  inner.addEventListener('pointermove', (event) => {
    if (pointerId !== event.pointerId) return;
    const dx = event.clientX - startX;
    const dy = event.clientY - startY;

    if (!owning) {
      // Decide intent once, then stay committed to it.
      if (Math.abs(dx) < DRAG_THRESHOLD) return;
      if (Math.abs(dy) > Math.abs(dx)) { pointerId = null; return; } // vertical scroll wins
      owning = true;
      inner.setPointerCapture(event.pointerId);
      li.classList.add('is-dragging');
      spring.stop();
    }

    tracker.add(event.clientX, event.timeStamp);

    // 1:1 with the finger, but resist past the commit point.
    let next = grabOffset + dx;
    const width = li.clientWidth || 600;
    const over = Math.abs(next) - COMMIT_DISTANCE;
    if (over > 0) {
      const sign = Math.sign(next);
      next = sign * (COMMIT_DISTANCE + rubberband(over, width));
    }
    spring.set(next);
    paintAffordance(li, next);
  });

  const finish = (event) => {
    if (pointerId !== event.pointerId) return;
    pointerId = null;
    if (!owning) return;
    owning = false;
    li.classList.remove('is-dragging');

    const velocity = tracker.velocity;
    const current = spring.value;
    // Where the flick is going, not where the finger left off.
    const projected = current + project(velocity);
    const flicked = Math.abs(velocity) > 250;

    if (projected >= COMMIT_DISTANCE) {
      commitSwipe(li, inner, spring, item, 'applied', velocity);
    } else if (projected <= -COMMIT_DISTANCE) {
      commitSwipe(li, inner, spring, item, 'pass', velocity);
    } else {
      // Snap home, carrying the release velocity so there is no seam.
      spring.setTarget(0, { velocity, ...(flicked ? SPRINGS.flick : SPRINGS.ui) });
      paintAffordance(li, 0);
    }
  };

  inner.addEventListener('pointerup', finish);
  inner.addEventListener('pointercancel', finish);
}

function paintAffordance(li, offset) {
  const aff = li.querySelector('.row-affordance');
  if (!aff) return;
  const progress = Math.min(1, Math.abs(offset) / COMMIT_DISTANCE);
  aff.style.opacity = String(progress);
  aff.querySelector('.aff-applied').style.opacity = offset > 0 ? '1' : '0.15';
  aff.querySelector('.aff-pass').style.opacity = offset < 0 ? '1' : '0.15';
}

function commitSwipe(li, inner, spring, item, action, velocity) {
  const width = li.clientWidth || 600;
  const target = action === 'applied' ? width : -width;
  // Hint in the direction of travel, then run the action.
  spring.setTarget(target, { velocity, ...SPRINGS.flick });
  const settle = () => {
    spring.setTarget(0, SPRINGS.ui);
    paintAffordance(li, 0);
  };
  if (action === 'applied') markApplied(item).finally(settle);
  else markPass(item, '').finally(settle);
}

/* ---------------------------------------------------------------- actions */

function payloadFor(item) {
  return {
    url: item.url,
    company: item.company,
    role: item.role,
    job_id: item.job_id || '',
    cluster: item.cluster || '',
    lane: item.lane || '',
    location: item.location || '',
    decided_at: new Date().toISOString(),
  };
}

async function post(path, body) {
  const res = await fetch(path, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    const detail = await res.text().catch(() => '');
    throw new Error(detail || `${path} failed`);
  }
  return res.json();
}

async function markApplied(item) {
  const key = itemKey(item);
  if (state.applied.has(key)) return;

  // Optimistic: the row reacts now, the ledger catches up.
  state.applied.add(key);
  paint();

  if (!state.live) {
    persistLocal();
    toast({ title: 'Marked applied locally', sub: 'Static mode — export decisions to sync.', kind: 'info' });
    return;
  }

  setSync('saving', 'Saving…');
  try {
    const data = await post('/api/applied', payloadFor(item));
    if (data.created && data.created.length) item.job_id = data.created[0];
    setSync('synced', 'Saved');
    state.lastAction = { type: 'applied', item };
    toast({
      title: `Applied · ${item.company}`,
      sub: 'Written to data/applications.csv',
      undo: () => undoAction({ type: 'applied', item }),
    });
  } catch (err) {
    state.applied.delete(key);
    paint();
    setSync('error', 'Write failed');
    toast({ title: 'Could not save "applied"', sub: String(err.message || err), kind: 'error', timeout: 0 });
  }
}

async function markPass(item, presetReason) {
  const key = itemKey(item);
  if (state.passed.has(key)) return;

  const reason = presetReason !== undefined
    ? presetReason
    : (window.prompt('Pass reason (optional)', '') ?? null);
  if (reason === null) return;

  const record = { url: item.url, company: item.company, role: item.role, reason };
  state.passed.set(key, record);
  paint();
  applyFilters();

  if (!state.live) {
    persistLocal();
    toast({ title: 'Passed locally', sub: 'Static mode — export decisions to sync.', kind: 'info' });
    return;
  }

  setSync('saving', 'Saving…');
  try {
    await post('/api/pass', { ...payloadFor(item), decision: 'pass', reason });
    setSync('synced', 'Saved');
    state.lastAction = { type: 'pass', item };
    toast({
      title: `Passed · ${item.company}`,
      sub: 'Archived in data/job_decisions.csv',
      undo: () => undoAction({ type: 'pass', item }),
    });
  } catch (err) {
    state.passed.delete(key);
    paint();
    applyFilters();
    setSync('error', 'Write failed');
    toast({ title: 'Could not save "pass"', sub: String(err.message || err), kind: 'error', timeout: 0 });
  }
}

async function undoAction(action) {
  if (!action || !state.live) return;
  const key = itemKey(action.item);
  setSync('saving', 'Undoing…');
  try {
    await post('/api/undo', { url: action.item.url, action: action.type });
    if (action.type === 'applied') state.applied.delete(key);
    else state.passed.delete(key);
    state.lastAction = null;
    paint();
    applyFilters();
    setSync('synced', 'Undone');
    toast({ title: 'Undone', sub: `${action.item.company} restored to discovered`, timeout: 4000 });
  } catch (err) {
    setSync('error', 'Undo failed');
    toast({ title: 'Undo failed', sub: String(err.message || err), kind: 'error', timeout: 0 });
  }
}

function persistLocal() {
  try {
    localStorage.setItem(STORAGE_APPLIED(), JSON.stringify([...state.applied]));
    localStorage.setItem(STORAGE_PASSED(), JSON.stringify([...state.passed]));
  } catch (err) {
    console.warn('local persist failed', err);
  }
}

function restoreLocal() {
  try {
    const applied = JSON.parse(localStorage.getItem(STORAGE_APPLIED()) || '[]');
    const passed = JSON.parse(localStorage.getItem(STORAGE_PASSED()) || '[]');
    state.applied = new Set(applied);
    state.passed = new Map(passed);
  } catch (err) {
    console.warn('local restore failed', err);
  }
}

/* ------------------------------------------------------------ server sync */

async function loadState() {
  if (!state.live) return;
  try {
    const res = await fetch('/api/state');
    const data = await res.json();
    state.applied = new Set((data.applied || []).map(normKey));
    state.passed = new Map((data.passed || []).map((d) => [normKey(d.url), d]));
    setSync('synced', 'Synced');
  } catch (err) {
    setSync('offline', 'Server offline');
  }
  paint();
  applyFilters();
}

async function loadQueue(day) {
  if (!state.live) return;
  setSync('saving', 'Loading…');
  try {
    const res = await fetch(`/api/queue?date=${encodeURIComponent(day)}`);
    const data = await res.json();
    state.day = data.day;
    state.dates = data.dates || state.dates;
    state.items = data.items || [];
    render();
    await loadState();
  } catch (err) {
    setSync('error', 'Load failed');
    toast({ title: 'Could not load that date', sub: String(err.message || err), kind: 'error' });
  }
}

function connectEvents() {
  if (!state.live || typeof EventSource === 'undefined') return;
  const source = new EventSource('/api/events');
  source.addEventListener('open', () => setSync('synced', 'Live'));
  source.addEventListener('state-changed', () => { loadState(); });
  source.addEventListener('error', () => {
    setSync('offline', 'Reconnecting…');
    // EventSource retries on its own; a slow poll covers the gap.
  });
  setInterval(() => {
    if (state.connection === 'offline') loadState();
  }, 5000);
}

/* -------------------------------------------------------------- keyboard */

function visibleItems() {
  return state.items.filter(isVisible);
}

function focusRow(delta) {
  const list = visibleItems();
  if (!list.length) return;
  state.focusIndex = Math.max(0, Math.min(list.length - 1, state.focusIndex + delta));
  const item = list[state.focusIndex];
  rowNodes.forEach((node) => node.li.classList.remove('is-focused'));
  const node = rowNodes.get(itemKey(item));
  if (node) {
    node.li.classList.add('is-focused');
    node.li.scrollIntoView({ block: 'nearest', behavior: prefersReducedMotion() ? 'auto' : 'smooth' });
  }
}

function focusedItem() {
  const list = visibleItems();
  if (state.focusIndex < 0 || state.focusIndex >= list.length) return null;
  return list[state.focusIndex];
}

function openNext() {
  const next = visibleItems().find((i) => !state.applied.has(itemKey(i)));
  if (!next) {
    toast({ title: 'Nothing left to open', sub: 'Every role in this view is handled.', timeout: 4000 });
    return;
  }
  window.open(next.url, '_blank', 'noopener');
  state.focusIndex = visibleItems().indexOf(next);
  focusRow(0);
}

function bindKeys() {
  document.addEventListener('keydown', (event) => {
    const tag = (event.target.tagName || '').toLowerCase();
    if (tag === 'input' || tag === 'textarea' || tag === 'select') return;
    if (event.metaKey || event.ctrlKey || event.altKey) return;

    switch (event.key.toLowerCase()) {
      case 'j': event.preventDefault(); focusRow(state.focusIndex < 0 ? 0 : 1); break;
      case 'k': event.preventDefault(); focusRow(-1); break;
      case 'o': {
        const item = focusedItem();
        if (item) window.open(item.url, '_blank', 'noopener');
        break;
      }
      case 'a': {
        const item = focusedItem();
        if (item) markApplied(item);
        break;
      }
      case 'p': {
        const item = focusedItem();
        if (item) markPass(item);
        break;
      }
      case 'u': if (state.lastAction) undoAction(state.lastAction); break;
      case '?': toast({
        title: 'Shortcuts',
        sub: 'J/K move · O open · A applied · P pass · U undo',
        timeout: 6000,
      }); break;
      default: break;
    }
  });
}

/* ---------------------------------------------------------- scroll edges */

function bindScrollEdge() {
  const update = () => {
    const strength = Math.min(1, window.scrollY / 40);
    els.chrome.style.setProperty('--edge-strength', String(strength));
  };
  update();
  window.addEventListener('scroll', update, { passive: true });
}

/* -------------------------------------------------------------- exporting */

function bindControls() {
  els.openNext?.addEventListener('click', openNext);

  els.exportPasses?.addEventListener('click', () => {
    const decisions = [...state.passed.values()];
    const applied = state.items
      .filter((i) => state.applied.has(itemKey(i)))
      .map((i) => ({ ...payloadFor(i) }));
    if (!decisions.length && !applied.length) {
      toast({ title: 'Nothing to export yet', timeout: 3500 });
      return;
    }
    const payload = { exported_at: new Date().toISOString(), decisions, applied };
    const blob = new Blob([JSON.stringify(payload, null, 2)], { type: 'application/json' });
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = `queue_decisions_${state.day}.json`;
    a.click();
    URL.revokeObjectURL(a.href);
  });
}

/* ------------------------------------------------------------------ boot */

async function boot() {
  render();
  bindFilters();
  bindControls();
  bindKeys();
  bindScrollEdge();

  if (state.live) {
    els.modeNote.textContent = 'Live mode — Applied and Pass write straight into the repo.';
    setSync('synced', 'Live');
    await loadState();
    connectEvents();
  } else {
    els.modeNote.innerHTML =
      'Static file — decisions stay in this browser. Run <code>python3 scripts/serve_apply_queue.py</code> for live writes.';
    setSync('static', 'Static file');
    restoreLocal();
    paint();
    applyFilters();
  }
}

function bindFilters() {
  buildFilters();
}

boot();
