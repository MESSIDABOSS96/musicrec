/* =========================================================================
   SCROLL — the camera

   The whole page is ONE SHOT: a slow push from the full room into the
   record shelf under the turntable. The scrollbar is the playhead — this
   file reads how far through the scroll track the user is (0..1) and poses
   every scroll-driven element for exactly that moment. Nothing here runs on
   a clock; scroll back up and the shot plays in reverse, frame-perfect.

   Two ideas carry everything:

   1. THE CAMERA is a single transform applied identically to the art and
      lighting layers (the world). With transform-origin 0 0, a world point
      P lands on screen at  scale * P + translate  — so to look at TARGET
      at zoom k, solve for the translate that puts k * TARGET wherever we
      want it on screen. No other geometry is needed.

   2. THE PLAYHEAD IS SMOOTHED. Raw scroll position lands in steps (wheel
      clicks, trackpad flicks). The displayed playhead chases the real one
      with an exponential ease-out each frame, which is what makes the
      camera feel like it has mass. Under prefers-reduced-motion the chase
      is disabled and the camera never moves at all — the copy still
      surfaces, by opacity alone.

   The idle loops (vinyl spin, sway, flame, EQ, lamp flicker) stay on their
   own clocks in styles.css. The room keeps living while the camera moves —
   that is deliberate, and it is most of why the end frame feels alive: the
   receiver's meter is still dancing when the shot settles on the shelf.
   ========================================================================= */

(() => {
'use strict';

/* ---------------------------------------------------------------------------
   THE SHOT
   Scene coordinates, authored 390x844. TARGET is the record shelf — the
   spine rows plus the receiver's display, measured from the artwork (the
   left spine row centres near x 151; nudged right to 178 so the REC/EQ
   display stays in frame at full zoom). ZOOM 3.2 frames the shelf opening;
   the source art is 2.19x the scene size, so the end frame is ~1.5x past
   pixel-true — soft, but the shelf-dark layer is already rising by then.

   The camera dwells before DOLLY_IN and after DOLLY_OUT so the room gets a
   beat to breathe at both ends of the move.
--------------------------------------------------------------------------- */
const SCENE = { w: 390, h: 844 };
const SHOT = {
  TARGET: { x: 178, y: 705 },   /* what we push toward                    */
  CENTER: { x: 195, y: 422 },   /* where it ends up: mid-frame            */
  ZOOM: 3.2,                    /* how close we get                       */
  DOLLY_IN: 0.08,               /* playhead where the camera starts moving */
  DOLLY_OUT: 0.92,              /* ...and where it settles                 */
};

/* The copy and light cues, as [fade-in start, in end, out start, out end]
   spans on the playhead. Chosen so each line has the frame to itself. */
const CUES = {
  identity: { out: [0.04, 0.14] },              /* the title block departs */
  cue:      { out: [0.005, 0.05] },             /* the scroll invitation   */
  line1:    { span: [0.24, 0.32, 0.44, 0.52] },
  line2:    { span: [0.54, 0.62, 0.72, 0.80] },
  dark:     { in: [0.80, 0.95] },               /* the shelf's dark rises  */
  finale:   { in: [0.88, 0.97] },               /* name + action return    */
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
/* 0 before a, 1 after b, smoothstep between. */
const rise = (p, a, b) => {
  const t = clamp01((p - a) / (b - a));
  return t * t * (3 - 2 * t);
};
/* Up over [a,b], down over [c,d]. */
const pulse = (p, [a, b, c, d]) => rise(p, a, b) * (1 - rise(p, c, d));

/* Opacity + visibility together: an element at opacity 0 must also stop
   catching focus and clicks (there are two CTAs on this page; only the
   visible one may be tabbable). */
function show(node, v) {
  node.style.opacity = v.toFixed(4);
  node.style.visibility = v > 0.001 ? 'visible' : 'hidden';
}

/* Pose everything for playhead p. */
function pose(p) {
  if (!reduceMotion) {
    /* Ease the leg of the move, then zoom exponentially along it — equal
       playhead steps then multiply the scale by equal factors, which is
       what a constant-speed dolly looks like. Linear scale would crawl at
       the start and lunge at the end. */
    const leg = rise(p, SHOT.DOLLY_IN, SHOT.DOLLY_OUT);
    const k = Math.exp(Math.log(SHOT.ZOOM) * leg);

    /* Where TARGET should sit on screen right now: it starts at its own
       resting spot (so leg 0 is the identity transform) and drifts to
       mid-frame as the zoom takes. */
    const sx = SHOT.TARGET.x + (SHOT.CENTER.x - SHOT.TARGET.x) * leg;
    const sy = SHOT.TARGET.y + (SHOT.CENTER.y - SHOT.TARGET.y) * leg;
    let tx = sx - k * SHOT.TARGET.x;
    let ty = sy - k * SHOT.TARGET.y;

    /* Keep the view inside the painting: the scene box shows world rect
       [-t/k, (scene - t)/k], which stays within [0, scene] exactly when
       t is in [scene * (1 - k), 0]. Without this, the leg where the
       target drifts to mid-frame can outrun the zoom and peek past the
       artwork's bottom edge (it was masked by rug-dark meeting void-dark,
       but it was there). */
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

let travel = 1;                 /* scrollable px — track minus one viewport */
function measure() {
  travel = Math.max(1, track.offsetHeight - window.innerHeight);
}

let playhead = null;            /* what's on screen */
let last = performance.now();

function frame(now) {
  const dt = Math.min((now - last) / 1000, 0.1);
  last = now;

  const goal = clamp01(window.scrollY / travel);

  if (playhead === null) {
    playhead = goal;            /* first frame: no chase, land exactly */
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
