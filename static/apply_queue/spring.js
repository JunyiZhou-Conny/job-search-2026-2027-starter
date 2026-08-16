/* Minimal spring engine for the apply queue.
 *
 * Written instead of pulling in a 140 KB animation bundle: the apple-design
 * guidance we follow is specified directly in terms of *damping ratio* and
 * *response*, which is exactly what this implements. Everything here is
 * interruptible and velocity-aware, which is the whole point:
 *
 *   - animation always starts from the current (presentation) value
 *   - retargeting mid-flight carries the live velocity through, so a reversal
 *     has no "brick wall" discontinuity
 *   - release velocity from a gesture is handed straight to the spring
 *
 * Apple's two designer-facing parameters:
 *   damping  1.0 = critically damped (no overshoot); < 1.0 overshoots
 *   response      = seconds to approach the target (NOT a fixed duration)
 */

/** Analytic spring solver for one scalar value. */
export class Spring {
  /**
   * @param {object} opts
   * @param {number} [opts.from]     initial value
   * @param {number} [opts.to]       target value
   * @param {number} [opts.velocity] initial velocity, units/second
   * @param {number} [opts.damping]  damping ratio (1 = critical)
   * @param {number} [opts.response] response in seconds
   * @param {(value:number, velocity:number)=>void} [opts.onUpdate]
   * @param {()=>void} [opts.onRest]
   */
  constructor(opts = {}) {
    this.value = opts.from ?? 0;
    this.target = opts.to ?? this.value;
    this.velocity = opts.velocity ?? 0;
    this.damping = opts.damping ?? 1;
    this.response = opts.response ?? 0.35;
    this.onUpdate = opts.onUpdate || (() => {});
    this.onRest = opts.onRest || (() => {});
    this.restDelta = opts.restDelta ?? 0.05;
    this.restVelocity = opts.restVelocity ?? 0.5;
    this._raf = 0;
    this._last = 0;
    this._running = false;
  }

  get running() {
    return this._running;
  }

  /** Natural angular frequency implied by `response`. */
  get omega() {
    return (2 * Math.PI) / Math.max(this.response, 0.0001);
  }

  /**
   * Retarget without losing continuity. Current value and velocity are kept,
   * so an in-flight animation can be reversed at any instant.
   */
  setTarget(target, opts = {}) {
    this.target = target;
    if (opts.velocity !== undefined) this.velocity = opts.velocity;
    if (opts.damping !== undefined) this.damping = opts.damping;
    if (opts.response !== undefined) this.response = opts.response;
    this.start();
  }

  /** Jump to a value with no animation (used for 1:1 drag tracking). */
  set(value, velocity = 0) {
    this.stop();
    this.value = value;
    this.velocity = velocity;
    this.onUpdate(this.value, this.velocity);
  }

  start() {
    if (this._running) return;
    this._running = true;
    this._last = performance.now();
    const tick = (now) => {
      if (!this._running) return;
      // Clamp dt so a backgrounded tab doesn't explode the integration.
      const dt = Math.min((now - this._last) / 1000, 1 / 30);
      this._last = now;
      this._step(dt);
      this.onUpdate(this.value, this.velocity);
      if (this._atRest()) {
        this.value = this.target;
        this.velocity = 0;
        this.onUpdate(this.value, this.velocity);
        this._running = false;
        this.onRest();
        return;
      }
      this._raf = requestAnimationFrame(tick);
    };
    this._raf = requestAnimationFrame(tick);
  }

  stop() {
    this._running = false;
    if (this._raf) cancelAnimationFrame(this._raf);
    this._raf = 0;
  }

  _atRest() {
    return (
      Math.abs(this.target - this.value) < this.restDelta &&
      Math.abs(this.velocity) < this.restVelocity
    );
  }

  /** Semi-implicit Euler — stable at the dt values a display produces. */
  _step(dt) {
    const w = this.omega;
    const z = this.damping;
    const k = w * w;             // stiffness (unit mass)
    const c = 2 * z * w;         // damping coefficient
    const x = this.value - this.target;
    const a = -k * x - c * this.velocity;
    this.velocity += a * dt;
    this.value += this.velocity * dt;
  }
}

/** House defaults, matching the values Apple ships for these interactions. */
export const SPRINGS = {
  /** Everything non-physical: menus, settles, snap-backs. No overshoot. */
  ui: { damping: 1.0, response: 0.35 },
  /** Reposition after a momentum gesture. */
  move: { damping: 1.0, response: 0.4 },
  /** Only when the gesture itself carried momentum (a flick). */
  flick: { damping: 0.8, response: 0.3 },
};

/**
 * Where a flick would come to rest, using the exponential-decay projection
 * from Apple's Designing Fluid Interfaces sample code (not v^2/2a).
 *
 * @param {number} velocity px/second at release
 * @param {number} [decelerationRate] 0.998 ≈ scroll feel, 0.99 snappier
 */
export function project(velocity, decelerationRate = 0.998) {
  return ((velocity / 1000) * decelerationRate) / (1 - decelerationRate);
}

/**
 * Progressive resistance past a boundary — real things slow before they stop.
 *
 * @param {number} overshoot how far past the bound the pointer is
 * @param {number} dimension the size the resistance is scaled against
 * @param {number} [constant] 0.55 matches UIKit's feel
 */
export function rubberband(overshoot, dimension, constant = 0.55) {
  if (dimension <= 0) return 0;
  return (overshoot * dimension * constant) / (dimension + constant * Math.abs(overshoot));
}

/** Tracks recent pointer samples so release velocity is real, not a guess. */
export class VelocityTracker {
  constructor(windowMs = 100) {
    this.windowMs = windowMs;
    this.samples = [];
  }

  reset() {
    this.samples = [];
  }

  add(value, time = performance.now()) {
    this.samples.push({ value, time });
    const cutoff = time - this.windowMs;
    while (this.samples.length > 2 && this.samples[0].time < cutoff) {
      this.samples.shift();
    }
  }

  /** px per second across the retained window. */
  get velocity() {
    if (this.samples.length < 2) return 0;
    const first = this.samples[0];
    const last = this.samples[this.samples.length - 1];
    const dt = (last.time - first.time) / 1000;
    if (dt <= 0) return 0;
    return (last.value - first.value) / dt;
  }
}

/** True when the user asked the OS for less motion. */
export function prefersReducedMotion() {
  return (
    typeof window !== 'undefined' &&
    window.matchMedia &&
    window.matchMedia('(prefers-reduced-motion: reduce)').matches
  );
}
