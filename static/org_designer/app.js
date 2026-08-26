/* Org designer shell. Server charter is authoritative after Save. */

const bootEl = document.getElementById('org-bootstrap');
const BOOT = JSON.parse(bootEl?.textContent || '{}');

const OWNER = 'owner';
const BASELINE_GATES = [
  'submit', 'send', 'two_factor', 'new_ats_account', 'mygreenhouse_login', 'workday_email',
];

const state = {
  revision: BOOT.revision || '',
  draft: BOOT.draft || emptyDraft(),
  templates: BOOT.templates || [],
  selected: OWNER,
  issues: (BOOT.review && BOOT.review.issues) || [],
  completeness: (BOOT.review && BOOT.review.preview && BOOT.review.preview.completeness) || [],
};

const els = {
  tree: document.getElementById('tree'),
  inspectorTitle: document.getElementById('inspectorTitle'),
  inspectorBody: document.getElementById('inspectorBody'),
  company: document.getElementById('company'),
  project: document.getElementById('project'),
  asOf: document.getElementById('asOf'),
  templateSelect: document.getElementById('templateSelect'),
  loadTemplate: document.getElementById('loadTemplate'),
  addBot: document.getElementById('addBot'),
  saveBtn: document.getElementById('saveBtn'),
  exportBtn: document.getElementById('exportBtn'),
  syncPill: document.getElementById('syncPill'),
  issues: document.getElementById('issues'),
  issueList: document.getElementById('issueList'),
  addDialog: document.getElementById('addDialog'),
  addForm: document.getElementById('addForm'),
  newName: document.getElementById('newName'),
  newRole: document.getElementById('newRole'),
  newParent: document.getElementById('newParent'),
};

function emptyDraft() {
  return {
    schema_version: 1,
    mode: 'plan_only',
    computer_boundary: 'shared_per_user',
    company: '',
    project: '',
    as_of: '',
    owner: { name: '', does: [], does_not: [], gates: BASELINE_GATES.slice() },
    seats: [],
    vacancies: [],
    talks: { owner_talks_only_to: '', assign_by: 'dm', assign_detail: '', team_handoff: '' },
    done_when: [],
  };
}

function esc(value) {
  return String(value ?? '').replace(/[&<>"']/g, (c) => (
    { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]
  ));
}

function uid(prefix) {
  return `${prefix}-${Math.random().toString(36).slice(2, 8)}`;
}

function setSync(name, text) {
  if (!els.syncPill) return;
  els.syncPill.dataset.state = name;
  els.syncPill.querySelector('.sync-text').textContent = text;
}

function childrenOf(parentId) {
  const seats = state.draft.seats.filter((s) => (s.listens_to || OWNER) === parentId);
  const vacancies = (state.draft.vacancies || []).filter((v) => (v.listens_to || OWNER) === parentId);
  return { seats, vacancies };
}

function hasReports(id) {
  const { seats, vacancies } = childrenOf(id);
  return seats.length > 0 || vacancies.length > 0;
}

function parentOf(id) {
  const seat = state.draft.seats.find((s) => s.id === id);
  if (seat) return seat.listens_to || OWNER;
  const vac = (state.draft.vacancies || []).find((v) => v.id === id);
  return vac ? (vac.listens_to || OWNER) : null;
}

function wouldCycle(seatId, newParent) {
  if (!newParent || newParent === OWNER) return false;
  const seen = new Set();
  let cur = newParent;
  while (cur && cur !== OWNER) {
    if (cur === seatId) return true;
    if (seen.has(cur)) return true;
    seen.add(cur);
    cur = parentOf(cur);
  }
  return false;
}

function parentOptions(exceptId) {
  const opts = [{ id: OWNER, label: `${state.draft.owner.name || 'Owner'} (human)` }];
  for (const seat of state.draft.seats) {
    if (exceptId && wouldCycle(exceptId, seat.id)) continue;
    opts.push({ id: seat.id, label: `${seat.bot_name} · ${seat.role}` });
  }
  return opts;
}

function applyMetaFromDraft() {
  els.company.value = state.draft.company || '';
  els.project.value = state.draft.project || '';
  els.asOf.value = state.draft.as_of || '';
}

function pullMeta() {
  state.draft.company = els.company.value.trim();
  state.draft.project = els.project.value.trim();
  state.draft.as_of = els.asOf.value;
}

function renderTemplates() {
  const current = els.templateSelect.value;
  els.templateSelect.innerHTML = '<option value="">Empty company</option>' +
    state.templates.map((t) => `<option value="${esc(t.id)}">${esc(t.name)}</option>`).join('');
  els.templateSelect.value = current;
}

function renderTree() {
  els.tree.innerHTML = '';
  els.tree.appendChild(ownerRow());
  els.tree.appendChild(branch(OWNER));
}

function ownerRow() {
  const li = document.createElement('li');
  li.innerHTML = `<div class="node" data-kind="owner" data-id="${OWNER}">
    <span class="handle" aria-hidden="true"></span>
    <span><span class="node-name">${esc(state.draft.owner.name || 'Owner')}</span>
    <span class="node-role">Human · gates only</span></span>
    <span class="pill">owner</span>
  </div>`;
  const node = li.querySelector('.node');
  if (state.selected === OWNER) node.classList.add('is-selected');
  node.addEventListener('click', () => select(OWNER));
  bindDrop(node, OWNER);
  return li;
}

function branch(parentId, seen = new Set()) {
  const ol = document.createElement('ol');
  ol.className = 'tree';
  if (seen.has(parentId)) return ol;
  seen.add(parentId);
  const { seats, vacancies } = childrenOf(parentId);
  for (const seat of seats) {
    ol.appendChild(seatRow(seat));
    const kids = branch(seat.id, seen);
    if (kids.children.length) ol.appendChild(kids);
  }
  for (const vac of vacancies) {
    ol.appendChild(vacancyRow(vac));
    const kids = branch(vac.id, seen);
    if (kids.children.length) ol.appendChild(kids);
  }
  return ol;
}

function seatRow(seat) {
  const li = document.createElement('li');
  const wave = seat.staffing?.kind || 'pilot';
  li.innerHTML = `<div class="node" data-kind="seat" data-id="${esc(seat.id)}" draggable="false">
    <button class="handle" type="button" aria-label="Drag to reparent">::</button>
    <span><span class="node-name">${esc(seat.bot_name)}</span>
    <span class="node-role">${esc(seat.role)}${seat.team ? ` · ${esc(seat.team)}` : ''}</span></span>
    <span class="pill pill-${esc(wave)}">${esc(wave)}</span>
  </div>`;
  const node = li.querySelector('.node');
  if (state.selected === seat.id) node.classList.add('is-selected');
  node.addEventListener('click', (event) => {
    if (event.target.closest('.handle')) return;
    select(seat.id);
  });
  bindDrag(node, seat.id);
  bindDrop(node, seat.id);
  return li;
}

function vacancyRow(vac) {
  const li = document.createElement('li');
  li.innerHTML = `<div class="node vacancy" data-kind="vacancy" data-id="${esc(vac.id)}">
    <span class="handle" aria-hidden="true"></span>
    <span><span class="node-name">Unnamed · ${esc(vac.role)}</span>
    <span class="node-role">Name this seat before save</span></span>
    <span class="pill">vacant</span>
  </div>`;
  const node = li.querySelector('.node');
  if (state.selected === vac.id) node.classList.add('is-selected');
  node.addEventListener('click', () => select(vac.id));
  return li;
}

function bindDrag(node, seatId) {
  const handle = node.querySelector('.handle');
  handle.addEventListener('pointerdown', (event) => {
    event.preventDefault();
    node.classList.add('is-dragging');
    const move = (ev) => {
      const over = document.elementFromPoint(ev.clientX, ev.clientY)?.closest('.node');
      document.querySelectorAll('.node.is-drop').forEach((el) => el.classList.remove('is-drop'));
      if (over && over.dataset.id && !wouldCycle(seatId, over.dataset.id)) over.classList.add('is-drop');
    };
    const up = (ev) => {
      node.classList.remove('is-dragging');
      document.querySelectorAll('.node.is-drop').forEach((el) => el.classList.remove('is-drop'));
      const over = document.elementFromPoint(ev.clientX, ev.clientY)?.closest('.node');
      const target = over?.dataset.id;
      if (target && !wouldCycle(seatId, target) && over.dataset.kind !== 'vacancy') {
        const seat = state.draft.seats.find((s) => s.id === seatId);
        if (seat) seat.listens_to = target;
        select(seatId);
        render();
      }
      window.removeEventListener('pointermove', move);
      window.removeEventListener('pointerup', up);
    };
    window.addEventListener('pointermove', move);
    window.addEventListener('pointerup', up);
  });
}

function bindDrop(node, _id) {
  node.addEventListener('dragover', (event) => event.preventDefault());
}

function select(id) {
  state.selected = id;
  renderTree();
  renderInspector();
}

function renderInspector() {
  pullMeta();
  if (state.selected === OWNER) {
    els.inspectorTitle.textContent = 'Owner';
    els.inspectorBody.innerHTML = ownerForm();
    bindOwnerForm();
    return;
  }
  const seat = state.draft.seats.find((s) => s.id === state.selected);
  if (seat) {
    els.inspectorTitle.textContent = seat.bot_name;
    els.inspectorBody.innerHTML = seatForm(seat);
    bindSeatForm(seat);
    return;
  }
  const vac = (state.draft.vacancies || []).find((v) => v.id === state.selected);
  if (vac) {
    els.inspectorTitle.textContent = vac.role;
    els.inspectorBody.innerHTML = vacancyForm(vac);
    bindVacancyForm(vac);
    return;
  }
  els.inspectorTitle.textContent = 'Nothing selected';
  els.inspectorBody.innerHTML = '<p class="hint">Select a row in the tree.</p>';
}

function ownerForm() {
  const o = state.draft.owner;
  const t = state.draft.talks;
  return `<div class="stack">
    <label class="field"><span>Name</span><input id="fOwnerName" value="${esc(o.name)}" /></label>
    <label class="field"><span>Does</span><textarea id="fOwnerDoes">${esc((o.does || []).join('\n'))}</textarea></label>
    <label class="field"><span>Does not</span><textarea id="fOwnerDoesNot">${esc((o.does_not || []).join('\n'))}</textarea></label>
    <label class="field"><span>Junyi talks only to</span>
      <select id="fTalksTo">${parentOptions().filter((p) => p.id !== OWNER).map((p) =>
        `<option value="${esc(p.id)}" ${t.owner_talks_only_to === p.id ? 'selected' : ''}>${esc(p.label)}</option>`
      ).join('')}<option value="" ${!t.owner_talks_only_to ? 'selected' : ''}>Not set</option></select>
    </label>
    <label class="field"><span>Chief assigns by</span>
      <select id="fAssign">
        <option value="dm" ${t.assign_by === 'dm' ? 'selected' : ''}>DM</option>
        <option value="group_chat" ${t.assign_by === 'group_chat' ? 'selected' : ''}>Group chat</option>
        <option value="other" ${t.assign_by === 'other' ? 'selected' : ''}>Other</option>
      </select>
    </label>
    <label class="field"><span>Assignment note</span><input id="fAssignDetail" value="${esc(t.assign_detail)}" /></label>
    <label class="field"><span>Handoff between teams</span><textarea id="fHandoff">${esc(t.team_handoff)}</textarea></label>
    <label class="field"><span>Done when (one per line)</span><textarea id="fDone">${esc((state.draft.done_when || []).join('\n'))}</textarea></label>
  </div>`;
}

function bindOwnerForm() {
  const pull = () => {
    state.draft.owner.name = document.getElementById('fOwnerName').value.trim();
    state.draft.owner.does = lines(document.getElementById('fOwnerDoes').value);
    state.draft.owner.does_not = lines(document.getElementById('fOwnerDoesNot').value);
    state.draft.owner.gates = BASELINE_GATES.slice();
    state.draft.talks.owner_talks_only_to = document.getElementById('fTalksTo').value;
    state.draft.talks.assign_by = document.getElementById('fAssign').value;
    state.draft.talks.assign_detail = document.getElementById('fAssignDetail').value.trim();
    state.draft.talks.team_handoff = document.getElementById('fHandoff').value.trim();
    state.draft.done_when = lines(document.getElementById('fDone').value);
    renderTree();
  };
  els.inspectorBody.querySelectorAll('input, textarea, select').forEach((el) => {
    el.addEventListener('input', pull);
    el.addEventListener('change', pull);
  });
}

function seatForm(seat) {
  const staffing = seat.staffing || { kind: 'pilot', order: 1, detail: '' };
  return `<div class="stack">
    <label class="field"><span>Bot name</span><input id="fName" value="${esc(seat.bot_name)}" /></label>
    <label class="field"><span>Role</span><input id="fRole" value="${esc(seat.role)}" /></label>
    <label class="field"><span>Listens to</span>
      <select id="fParent">${parentOptions(seat.id).map((p) =>
        `<option value="${esc(p.id)}" ${(seat.listens_to || OWNER) === p.id ? 'selected' : ''}>${esc(p.label)}</option>`
      ).join('')}</select>
    </label>
    <label class="field"><span>Team label</span><input id="fTeam" value="${esc(seat.team || '')}" /></label>
    <label class="field"><span>Does (one per line)</span><textarea id="fDoes">${esc((seat.does || []).join('\n'))}</textarea></label>
    <label class="field"><span>Does not</span><textarea id="fDoesNot">${esc((seat.does_not || []).join('\n'))}</textarea></label>
    <label class="field"><span>Staffing</span>
      <select id="fWave">
        <option value="pilot" ${staffing.kind === 'pilot' ? 'selected' : ''}>Pilot</option>
        <option value="later" ${staffing.kind === 'later' ? 'selected' : ''}>Later</option>
        <option value="on_call" ${staffing.kind === 'on_call' ? 'selected' : ''}>On call</option>
      </select>
    </label>
    <label class="field"><span>Pilot order</span><input id="fOrder" type="number" min="1" value="${esc(staffing.order || 1)}" /></label>
    <label class="field"><span>Later / on-call note</span><input id="fDetail" value="${esc(staffing.detail || '')}" /></label>
    <button class="btn danger" id="fDelete" type="button">Remove seat</button>
  </div>`;
}

function bindSeatForm(seat) {
  const pull = () => {
    seat.bot_name = document.getElementById('fName').value.trim();
    seat.role = document.getElementById('fRole').value.trim();
    seat.listens_to = document.getElementById('fParent').value;
    seat.team = document.getElementById('fTeam').value.trim();
    seat.does = lines(document.getElementById('fDoes').value);
    seat.does_not = lines(document.getElementById('fDoesNot').value);
    seat.staffing = {
      kind: document.getElementById('fWave').value,
      order: Number(document.getElementById('fOrder').value) || 1,
      detail: document.getElementById('fDetail').value.trim(),
    };
    renderTree();
  };
  els.inspectorBody.querySelectorAll('input, textarea, select').forEach((el) => {
    el.addEventListener('input', pull);
    el.addEventListener('change', pull);
  });
  document.getElementById('fDelete').addEventListener('click', () => {
    if (hasReports(seat.id)) {
      setSync('error', 'Reparent reports first');
      return;
    }
    state.draft.seats = state.draft.seats.filter((s) => s.id !== seat.id);
    if (state.draft.talks.owner_talks_only_to === seat.id) state.draft.talks.owner_talks_only_to = '';
    select(OWNER);
    render();
  });
}

function vacancyForm(vac) {
  return `<div class="stack">
    <p class="hint">${esc(vac.role)} is a paper role. Give it a bot name to seat it.</p>
    <label class="field"><span>Bot name</span><input id="vName" required /></label>
    <label class="field"><span>Does</span><textarea id="vDoes">${esc((vac.suggested_does || []).join('\n'))}</textarea></label>
    <label class="field"><span>Does not</span><textarea id="vDoesNot">${esc((vac.suggested_does_not || []).join('\n'))}</textarea></label>
    <button class="btn btn-primary" id="vSeat" type="button">Seat this bot</button>
    <button class="btn" id="vDrop" type="button">Delete slip</button>
  </div>`;
}

function bindVacancyForm(vac) {
  document.getElementById('vSeat').addEventListener('click', () => {
    const name = document.getElementById('vName').value.trim();
    if (!name || name === '_') {
      setSync('error', 'Name the bot');
      return;
    }
    state.draft.seats.push({
      id: vac.id,
      bot_name: name,
      role: vac.role,
      listens_to: vac.listens_to,
      does: lines(document.getElementById('vDoes').value),
      does_not: lines(document.getElementById('vDoesNot').value),
      staffing: vac.staffing || { kind: 'pilot', order: state.draft.seats.length + 1, detail: '' },
      team: vac.team || '',
    });
    state.draft.vacancies = state.draft.vacancies.filter((v) => v.id !== vac.id);
    select(vac.id);
    render();
  });
  document.getElementById('vDrop').addEventListener('click', () => {
    if (hasReports(vac.id)) {
      setSync('error', 'Reparent reports first');
      return;
    }
    state.draft.vacancies = state.draft.vacancies.filter((v) => v.id !== vac.id);
    select(OWNER);
    render();
  });
}

function lines(text) {
  return String(text || '').split('\n').map((s) => s.trim()).filter(Boolean);
}

function renderIssues() {
  const all = [...state.issues, ...state.completeness];
  if (!all.length) {
    els.issues.hidden = true;
    els.issueList.innerHTML = '';
    return;
  }
  els.issues.hidden = false;
  els.issueList.innerHTML = all.map((i) => `<li>${esc(i.message)}</li>`).join('');
}

function render() {
  applyMetaFromDraft();
  renderTemplates();
  renderTree();
  renderInspector();
  renderIssues();
}

async function put(writeBrief) {
  pullMeta();
  setSync('saving', writeBrief ? 'Exporting' : 'Saving');
  const res = await fetch('/api/org', {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      draft: state.draft,
      expected_revision: state.revision,
      write_brief: writeBrief,
    }),
  });
  const data = await res.json();
  if (res.status === 409) {
    setSync('error', 'Reload — charter changed');
    return data;
  }
  if (!res.ok) {
    state.issues = data.issues || [];
    renderIssues();
    setSync('error', data.issues?.[0]?.message || 'Fix the tree');
    return data;
  }
  state.revision = data.revision;
  state.issues = [];
  state.completeness = data.preview?.completeness || [];
  renderIssues();
  setSync('synced', writeBrief ? 'Brief written' : 'Charter saved');
  if (writeBrief && data.preview?.brief) {
    try {
      await navigator.clipboard.writeText(extractPaste(data.preview.brief));
      setSync('synced', 'Brief copied');
    } catch {
      /* clipboard may be blocked; file is still written */
    }
  }
  return data;
}

function extractPaste(markdown) {
  const match = markdown.match(/```text\n([\s\S]*?)\nEND PASTE/);
  return match ? `${match[1]}\nEND PASTE` : markdown;
}

async function loadTemplate() {
  const id = els.templateSelect.value;
  const url = id ? `/api/org?template=${encodeURIComponent(id)}` : '/api/org?fresh=1';
  const res = await fetch(url);
  const data = await res.json();
  state.draft = data.draft;
  state.issues = data.review?.issues || [];
  state.completeness = data.review?.preview?.completeness || [];
  state.selected = OWNER;
  render();
  setSync('idle', id ? 'Roles loaded — name each bot' : 'Empty company');
}

function openAdd() {
  els.newParent.innerHTML = parentOptions().map((p) =>
    `<option value="${esc(p.id)}" ${state.selected === p.id ? 'selected' : ''}>${esc(p.label)}</option>`
  ).join('');
  els.newName.value = '';
  els.newRole.value = '';
  els.addDialog.showModal();
}

document.getElementById('addCancel').addEventListener('click', () => {
  els.addDialog.close();
});

els.addForm.addEventListener('submit', (event) => {
  const submitter = event.submitter;
  if (!submitter || submitter.value !== 'add') return;
  const name = els.newName.value.trim();
  const role = els.newRole.value.trim();
  if (!name || name === '_' || !role) {
    event.preventDefault();
    setSync('error', 'Name and role required');
    return;
  }
  const seat = {
    id: uid('s'),
    bot_name: name,
    role,
    listens_to: els.newParent.value || OWNER,
    does: [],
    does_not: [],
    staffing: { kind: 'pilot', order: state.draft.seats.length + 1, detail: '' },
    team: '',
  };
  state.draft.seats.push(seat);
  if (!state.draft.talks.owner_talks_only_to) state.draft.talks.owner_talks_only_to = seat.id;
  select(seat.id);
  render();
});

els.company.addEventListener('input', pullMeta);
els.project.addEventListener('input', pullMeta);
els.asOf.addEventListener('change', pullMeta);
els.loadTemplate.addEventListener('click', () => loadTemplate());
els.addBot.addEventListener('click', openAdd);
els.saveBtn.addEventListener('click', () => put(false));
els.exportBtn.addEventListener('click', () => put(true));

render();
