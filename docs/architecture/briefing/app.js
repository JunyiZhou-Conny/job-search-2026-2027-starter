import { Spring, SPRINGS, project, rubberband, VelocityTracker, prefersReducedMotion } from "./spring.js";
import { SCENES, CHAPTERS, BANDS, TRUTH } from "./model.js";

const stage = document.getElementById("stage");
const sceneRoot = document.getElementById("scene");
const truthEl = document.getElementById("truth");
const chaptersEl = document.getElementById("chapters");
const dotsEl = document.getElementById("dots");
const prevBtn = document.getElementById("prev");
const nextBtn = document.getElementById("next");
const hintEl = document.getElementById("hint");
const sheetEl = document.getElementById("sheet");
const scrimEl = document.getElementById("scrim");

const state = { index: 0, x: 0 };

const xSpring = new Spring({
  from: 0,
  to: 0,
  ...SPRINGS.ui,
  onUpdate(value) {
    sceneRoot.style.transform = `translateX(${value}px)`;
    sceneRoot.style.opacity = String(1 - Math.min(Math.abs(value) / 240, 0.35));
  },
});

function renderChapters() {
  const current = SCENES[state.index];
  chaptersEl.innerHTML = CHAPTERS.map((ch) => {
    const currentAttr = ch.id === current.chapter ? ' aria-current="true"' : "";
    return `<button type="button" data-chapter="${ch.id}"${currentAttr}>${ch.title}</button>`;
  }).join("");
}

function renderDots() {
  dotsEl.innerHTML = SCENES.map((scene, i) => {
    const currentAttr = i === state.index ? ' aria-current="true"' : "";
    return `<button type="button" data-index="${i}" aria-label="${scene.title}"${currentAttr}></button>`;
  }).join("");
}

function renderBlock(block) {
  if (block.kind === "line" || block.kind === "flow") {
    return `<div class="${block.kind}">${block.items.map((item, i) => {
      const chev = i < block.items.length - 1 ? '<span class="chev">→</span>' : "";
      return `<span class="chip">${item}</span>${chev}`;
    }).join("")}</div>`;
  }
  if (block.kind === "cards") {
    return `<div class="grid">${block.items.map((item) => (
      `<article class="card"><h3>${item.t}</h3><p>${item.d}</p></article>`
    )).join("")}</div>`;
  }
  if (block.kind === "tools") {
    return `<div class="grid">${block.items.map((item) => (
      `<article class="tool"><h3>${item.name}</h3><p>${item.role}</p></article>`
    )).join("")}</div>`;
  }
  if (block.kind === "clock") {
    return `<div class="clock">${block.items.map((item) => (
      `<article class="clock-row"><div class="et">${item.et}</div><div><strong>${item.name}</strong><p>${item.does}</p></div></article>`
    )).join("")}</div>`;
  }
  if (block.kind === "states") {
    return `<div class="states">${block.items.map((item) => (
      `<article class="state"><strong>${item.name}</strong><span>${item.meaning}</span></article>`
    )).join("")}</div>`;
  }
  if (block.kind === "list") {
    return `<ul class="plain-list">${block.items.map((item) => `<li>${item}</li>`).join("")}</ul>`;
  }
  if (block.kind === "bands") {
    return `<div class="bands">${BANDS.map((band) => (
      `<button type="button" class="band" data-band="${band.id}">
        <h3>${band.id} ${band.title}</h3>
        <p>${band.meaning}</p>
        <ol>${band.nodes.map((node) => `<li class="kind-${node.kind}">${node.name}</li>`).join("")}</ol>
      </button>`
    )).join("")}</div>`;
  }
  return "";
}

function renderScene() {
  const scene = SCENES[state.index];
  truthEl.dataset.truth = scene.truth;
  truthEl.textContent = scene.truth;
  truthEl.title = TRUTH[scene.truth];
  const note = scene.note ? `<p class="note">${scene.note}</p>` : "";
  sceneRoot.innerHTML = `
    <p class="kicker">${scene.kicker}</p>
    <h1>${scene.title}</h1>
    <p class="lede">${scene.lede}</p>
    ${scene.blocks.map(renderBlock).join("")}
    ${note}
  `;
  renderChapters();
  renderDots();
  prevBtn.disabled = state.index === 0;
  nextBtn.disabled = state.index === SCENES.length - 1;
  hintEl.textContent = `${state.index + 1} / ${SCENES.length}`;
  closeSheet();
}

function goTo(index, velocity = 0) {
  const next = Math.max(0, Math.min(SCENES.length - 1, index));
  const same = next === state.index;
  state.index = next;
  renderScene();
  const id = SCENES[state.index].id;
  if (location.hash !== `#${id}`) {
    history.replaceState(null, "", `#${id}`);
  }
  if (prefersReducedMotion()) {
    xSpring.set(0);
    return;
  }
  if (same && velocity === 0) {
    xSpring.setTarget(0, SPRINGS.ui);
    return;
  }
  sceneRoot.style.transform = "translateX(0px)";
  xSpring.set(velocity > 0 ? 48 : -48, velocity);
  xSpring.setTarget(0, SPRINGS.ui);
}

function openBand(id) {
  const band = BANDS.find((item) => item.id === id);
  if (!band) return;
  sheetEl.hidden = false;
  scrimEl.hidden = false;
  sheetEl.innerHTML = `
    <p class="kicker">${band.id}</p>
    <h2>${band.title} / ${band.meaning}</h2>
    <div class="states">${band.nodes.map((node) => (
      `<article class="state"><strong>${node.name}</strong><span>${node.meaning}</span></article>`
    )).join("")}</div>
  `;
}

function closeSheet() {
  sheetEl.hidden = true;
  scrimEl.hidden = true;
  sheetEl.innerHTML = "";
}

chaptersEl.addEventListener("click", (event) => {
  const button = event.target.closest("[data-chapter]");
  if (!button) return;
  const index = SCENES.findIndex((scene) => scene.chapter === button.dataset.chapter);
  goTo(index);
});

dotsEl.addEventListener("click", (event) => {
  const button = event.target.closest("[data-index]");
  if (!button) return;
  goTo(Number(button.dataset.index));
});

prevBtn.addEventListener("click", () => goTo(state.index - 1));
nextBtn.addEventListener("click", () => goTo(state.index + 1));
scrimEl.addEventListener("click", closeSheet);

stage.addEventListener("click", (event) => {
  const button = event.target.closest("[data-band]");
  if (!button) return;
  openBand(button.dataset.band);
});

window.addEventListener("keydown", (event) => {
  if (event.key === "ArrowRight" || event.key === " ") {
    event.preventDefault();
    goTo(state.index + 1);
  } else if (event.key === "ArrowLeft") {
    event.preventDefault();
    goTo(state.index - 1);
  } else if (event.key === "Escape") {
    closeSheet();
  }
});

const tracker = new VelocityTracker();
let drag = null;

stage.addEventListener("pointerdown", (event) => {
  if (event.target.closest("button")) return;
  stage.setPointerCapture(event.pointerId);
  tracker.reset();
  tracker.add(event.clientX);
  drag = { startX: event.clientX, lastX: event.clientX };
});

stage.addEventListener("pointermove", (event) => {
  if (!drag) return;
  tracker.add(event.clientX);
  const dx = event.clientX - drag.startX;
  const atStart = state.index === 0 && dx > 0;
  const atEnd = state.index === SCENES.length - 1 && dx < 0;
  const x = atStart || atEnd ? rubberband(dx, stage.clientWidth) : dx;
  xSpring.set(x);
  drag.lastX = event.clientX;
});

stage.addEventListener("pointerup", () => {
  if (!drag) return;
  const velocity = tracker.velocity;
  const projected = xSpring.value + project(velocity);
  const threshold = stage.clientWidth * 0.18;
  if (projected < -threshold) goTo(state.index + 1, velocity);
  else if (projected > threshold) goTo(state.index - 1, velocity);
  else xSpring.setTarget(0, { ...SPRINGS.flick, velocity });
  drag = null;
});

window.addEventListener("hashchange", () => {
  const id = location.hash.replace("#", "");
  const index = SCENES.findIndex((scene) => scene.id === id);
  if (index >= 0 && index !== state.index) goTo(index);
});

const boot = location.hash.replace("#", "");
const bootIndex = SCENES.findIndex((scene) => scene.id === boot);
goTo(bootIndex >= 0 ? bootIndex : 0);
