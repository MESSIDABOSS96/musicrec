/* =========================================================================
   SCROLL — the camera (desktop)

   Same engine as ../scroll.js — read that file's header for the two ideas
   that carry everything (the camera as one solved transform; the smoothed
   playhead). This copy holds the desktop shot's own geometry, plus one
   addition the mobile engine gained at the same time: the camera is
   CLAMPED to the artwork, so no leg of the move can ever show the void
   past the painting's edge.
   ========================================================================= */

(() => {
'use strict';

/* ---------------------------------------------------------------------------
   THE SHOT
   Scene coordinates, authored 1536x1024 (scene px == artwork px; the
   scene's own fit-to-viewport scale wraps this and doesn't interact).
   TARGET is the record cabinet right of centre — the two spine bays plus
   the receiver, whose meter keeps dancing in the end frame. ZOOM 3.3
   frames the cabinet opening (roughly x 758-1222 of the artwork).
--------------------------------------------------------------------------- */
const SCENE = { w: 1536, h: 1024 };
const SHOT = {
  TARGET: { x: 990, y: 850 },   /* what we push toward                    */
  CENTER: { x: 768, y: 512 },   /* where it ends up: mid-frame            */
  ZOOM: 3.3,                    /* how close we get                       */
  DOLLY_IN: 0.08,               /* playhead where the camera starts moving */
  DOLLY_OUT: 0.92,              /* ...and where it settles                 */
};

/* The copy and light cues, as spans on the playhead. */
const CUES = {
  identity: { out: [0.04, 0.14] },
  cue:      { out: [0.005, 0.05] },
  line1:    { span: [0.24, 0.32, 0.44, 0.52] },
  line2:    { span: [0.54, 0.62, 0.72, 0.80] },
  dark:     { in: [0.80, 0.95] },
  finale:   { in: [0.88, 0.97] },
};

const CHASE_RATE = 7;  /* 1/s — how eagerly the playhead chases the scroll */

/* --------------------------------------------------------------------------- */

const track = document.querySelector('[data-layer="scroll-track"]');
const world = [
  document.querySelector('[data-layer="art"]'),
  document.querySelector('[data-layer="lighting"]'),
];
const $actor = n => document.querySelector(`[data-actor="${n}"]`);
const el = {
  identity: $actor('identity'),
  cue:      $actor('scroll-cue'),
  line1:    $actor('story-line-1'),
  line2:    $actor('story-line-2'),
  dark:     $actor('shelf-dark'),
  finale:   $actor('finale'),
};

const reduceMotion = matchMedia('(prefers-reduced-motion: reduce)').matches;

const clamp01 = v => (v < 0 ? 0 : v > 1 ? 1 : v);
const rise = (p, a, b) => {
  const t = clamp01((p - a) / (b - a));
  return t * t * (3 - 2 * t);
};
const pulse = (p, [a, b, c, d]) => rise(p, a, b) * (1 - rise(p, c, d));

function show(node, v) {
  node.style.opacity = v.toFixed(4);
  node.style.visibility = v > 0.001 ? 'visible' : 'hidden';
}

function pose(p) {
  if (!reduceMotion) {
    const leg = rise(p, SHOT.DOLLY_IN, SHOT.DOLLY_OUT);
    const k = Math.exp(Math.log(SHOT.ZOOM) * leg);

    const sx = SHOT.TARGET.x + (SHOT.CENTER.x - SHOT.TARGET.x) * leg;
    const sy = SHOT.TARGET.y + (SHOT.CENTER.y - SHOT.TARGET.y) * leg;
    let tx = sx - k * SHOT.TARGET.x;
    let ty = sy - k * SHOT.TARGET.y;

    /* Keep the view inside the painting: the scene box shows world rect
       [-t/k, (scene - t)/k], which stays within [0, scene] exactly when
       t is in [scene * (1 - k), 0]. Without this, the leg where the
       target drifts to mid-frame can outrun the zoom and peek past the
       artwork's edge. */
    tx = Math.min(0, Math.max(SCENE.w * (1 - k), tx));
    ty = Math.min(0, Math.max(SCENE.h * (1 - k), ty));

    const m = `translate3d(${tx.toFixed(2)}px, ${ty.toFixed(2)}px, 0) scale(${k.toFixed(4)})`;
    for (const layer of world) layer.style.transform = m;
  }

  show(el.identity, 1 - rise(p, ...CUES.identity.out));
  show(el.cue,      1 - rise(p, ...CUES.cue.out));
  show(el.line1,    pulse(p, CUES.line1.span));
  show(el.line2,    pulse(p, CUES.line2.span));
  show(el.dark,     rise(p, ...CUES.dark.in));
  show(el.finale,   rise(p, ...CUES.finale.in));
}

/* ---------------------------------------------------------------------------
   THE LOOP
--------------------------------------------------------------------------- */

let travel = 1;
function measure() {
  travel = Math.max(1, track.offsetHeight - window.innerHeight);
}

let playhead = null;
let last = performance.now();

function frame(now) {
  const dt = Math.min((now - last) / 1000, 0.1);
  last = now;

  const goal = clamp01(window.scrollY / travel);

  if (playhead === null) {
    playhead = goal;
    pose(playhead);
  } else {
    const next = reduceMotion
      ? goal
      : playhead + (goal - playhead) * (1 - Math.exp(-CHASE_RATE * dt));
    if (Math.abs(next - playhead) > 1e-5) {
      playhead = Math.abs(goal - next) < 1e-4 ? goal : next;
      pose(playhead);
    }
  }

  requestAnimationFrame(frame);
}

window.addEventListener('resize', measure);
measure();
requestAnimationFrame(frame);

})();
