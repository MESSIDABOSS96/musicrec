"""
Separate the desktop record into its three layers, ready to spin.

    roomd.png  ->  vinyl-rotating.png   the surface that turns
               ->  vinyl-light.png      the disc's sheen and shading, static
               ->  deck-over.png        tonearm, headshell, spindle - static

One script does what the mobile pipeline splits across split_vinyl.py and
symmetrize.py, because the light-layer solve makes the intermediate
"whole disc" layer unnecessary as a shipped asset: the rotating layer is
ring-symmetric BY CONSTRUCTION (median of each ring), so the disc under
the occluders only needs reconstructing well enough to feed the ring
statistics and the light solve.

The perceptual rules are the mobile ones (see ../../README.md):
  - the plate keeps its baked record, the silhouette never moves;
  - the rotating layer is rotationally symmetric plus two deliberate
    marks, and fades out before the rim, so the painted rim, the disc's
    front-edge thickness, and every glint stay still;
  - light does not orbit: everything view-dependent lands in
    vinyl-light.png, solved per pixel so the rest composite reproduces
    the painting exactly outside the marks.

Geometry from fit_ellipse.py: the rim's ellipse, fitted to the disc's
TOP surface (the visible front-edge thickness below it belongs to the
plate). The painted label sits a few px off the fitted centre, so the
label wobbles slightly as it turns; the illustration, not the maths, is
inconsistent — same as mobile.

Run from desktop/tools/. Needs numpy and Pillow. Prints the CSS
constants for styles.css.
"""
import numpy as np
from PIL import Image

SRC = '../assets/roomd.png'
img = np.asarray(Image.open(SRC).convert('RGB')).astype(np.float32)
H, W = img.shape[:2]        # scene px == image px on desktop

ELLIPSE = [1110.1875, 675.75, 92.6875, 26.14, 0.059778]
cx, cy, A, B, phi = ELLIPSE

# ------------------------------------------------------------------ helpers
def dilate(m, k):
    o = m.copy()
    for _ in range(k):
        p = np.pad(o, 1, constant_values=False)
        o = (p[1:-1, 1:-1] | p[:-2, 1:-1] | p[2:, 1:-1] | p[1:-1, :-2] | p[1:-1, 2:])
    return o


yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
c, s = np.cos(-phi), np.sin(-phi)
dx, dy = xx - cx, yy - cy
U = (dx * c - dy * s) / A
V = (dx * s + dy * c) / B
r = np.hypot(U, V)
th = np.arctan2(V, U)
with np.errstate(invalid='ignore', divide='ignore'):
    gu, gv = U / np.maximum(r, 1e-9), V / np.maximum(r, 1e-9)
    gx = (gu / A) * c + (gv / B) * s
    gy = -(gu / A) * s + (gv / B) * c
    grad = np.maximum(np.hypot(gx, gy), 1e-9)

alpha_disc = np.clip((1.0 - r) / grad + 0.5, 0.0, 1.0)
inside = r <= 1.0

# ---------------------------------------------------------------- occluders
OUT = 1.07


def poly(px, py, pts):
    m = np.zeros(px.shape, bool)
    n = len(pts)
    for i in range(n):
        x0, y0 = pts[i]
        x1, y1 = pts[(i + 1) % n]
        cond = ((y0 > py) != (y1 > py))
        with np.errstate(divide='ignore', invalid='ignore'):
            xint = (x1 - x0) * (py - y0) / (y1 - y0 + 1e-12) + x0
        m ^= cond & (px < xint)
    return m


head = poly(xx, yy, [(1146, 673), (1180, 670), (1183, 698), (1150, 702)]) & (r <= OUT)
tube_line = 681.0 - 0.145 * (xx - 1175.0)
tube = (r <= OUT) & (np.abs(yy - tube_line) < 5.5) & (xx > 1158)
spindle = inside & (xx > 1109) & (xx < 1123) & (yy > 659) & (yy < 677)
occ = dilate(head | tube | spindle, 1) & (r <= OUT)

# --------------------------------------- reconstruct the disc under them
vinyl_full = img.copy()
clean = inside & ~occ
tgt = occ & inside
ty, tx = np.nonzero(tgt)
rr, tt = r[tgt], th[tgt]
got = np.zeros(len(ty), bool)
out = np.zeros((len(ty), 3), np.float32)
cph, sph = np.cos(phi), np.sin(phi)
for dd in (35, -35, 70, -70, 105, -105, 140, -140, 175, -175):
    need = ~got
    if not need.any():
        break
    t2 = tt[need] + np.deg2rad(dd)
    u, v = rr[need] * np.cos(t2) * A, rr[need] * np.sin(t2) * B
    xs = cx + u * cph - v * sph
    ys = cy + u * sph + v * cph
    xi = np.clip(np.round(xs).astype(int), 0, W - 1)
    yi = np.clip(np.round(ys).astype(int), 0, H - 1)
    ok = clean[yi, xi]
    idx = np.nonzero(need)[0][ok]
    out[idx] = img[yi[ok], xi[ok]]
    got[idx] = True
vinyl_full[ty, tx] = out
print(f'reconstructed {tgt.sum()} px under occluders '
      f'({100 * (~got).mean():.1f}% unfilled -> ring median)')

# -------------------------------------------------- ring-symmetric surface
nbins = 300
edges = np.linspace(0, 1.06, nbins + 1)
idx = np.clip(np.digitize(r, edges) - 1, 0, nbins - 1)
base = np.zeros((H, W, 3), np.float32)
ring = np.zeros((nbins, 3), np.float32)
have = np.zeros(nbins, bool)
sel_all = r <= 1.06
for bin_ in range(nbins):
    m = sel_all & (idx == bin_) & ~occ
    if m.sum() >= 8:
        ring[bin_] = np.median(img[m].reshape(-1, 3), axis=0)
        have[bin_] = True
src = np.nonzero(have)[0]
for ch in range(3):
    ring[:, ch] = np.interp(np.arange(nbins), src, ring[src, ch])
k = 3
pad = np.pad(ring, ((1, 1), (0, 0)), mode='edge')
ring = (pad[:-2] + pad[1:-1] + pad[2:]) / 3
base = ring[idx]
# pixels the rotational fill could not reach fall back to the ring median
vinyl_full[ty[~got], tx[~got]] = base[ty[~got], tx[~got]]

# marks: a warm smudge on the label, a dust fleck on the grooves
def blob(r0, th0, sr, sth, gain):
    dth = np.mod(th - th0 + np.pi, 2 * np.pi) - np.pi
    g = np.exp(-0.5 * (((r - r0) / sr) ** 2 + (dth / sth) ** 2))
    return g[:, :, None] * np.array(gain, np.float32)


mark = (blob(0.24, 1.1, 0.10, 0.5, (34, 16, 8))
        + blob(0.70, -2.1, 0.02, 0.05, (30, 22, 12)))
surface = np.clip(base + mark, 0, 255)

fade = np.clip((0.985 - r) / 0.045, 0.0, 1.0)
aR = alpha_disc * fade

# ------------------------------------------------------------- light layer
T = img * (1 - alpha_disc[:, :, None]) + vinyl_full * alpha_disc[:, :, None]
B0 = img * (1 - aR[:, :, None]) + base * aR[:, :, None]
d = T - B0
with np.errstate(divide='ignore', invalid='ignore'):
    need = np.where(d > 0, d / np.maximum(255.0 - B0, 1e-6),
                    -d / np.maximum(B0, 1e-6))
aL = np.clip(need.max(axis=2), 0.0, 1.0)
active = (np.abs(d).max(axis=2) > 0.5) & (r <= 1.06)
aL = np.where(active, np.maximum(aL, 1.0 / 255.0), 0.0)
C = np.where(aL[:, :, None] > 0, B0 + d / np.maximum(aL[:, :, None], 1e-6), 0.0)
C = np.clip(C, 0, 255)

# ------------------------------------------------------------------ deck
occ_deck = dilate(occ, 1) & (r <= OUT)

# ---------------------------------------------------------------- assemble
rot = np.zeros((H, W, 4), np.float32)
rot[:, :, :3] = surface
rot[:, :, 3] = aR * 255.0

lig = np.zeros((H, W, 4), np.float32)
lig[:, :, :3] = C
lig[:, :, 3] = aL * 255.0

deck = np.zeros((H, W, 4), np.float32)
deck[:, :, :3] = np.where(occ_deck[:, :, None], img, 0)
deck[:, :, 3] = np.where(occ_deck, 255.0, 0.0)

for lay in (rot, lig, deck):
    clear = lay[:, :, 3] == 0
    near = dilate(~clear, 8)
    lay[clear & near, :3] = img[clear & near]
    lay[clear & ~near, :3] = 0

Image.fromarray(np.round(rot).astype(np.uint8)).save('../assets/vinyl-rotating.png', optimize=True)
Image.fromarray(np.round(lig).astype(np.uint8)).save('../assets/vinyl-light.png', optimize=True)
Image.fromarray(np.round(deck).astype(np.uint8)).save('../assets/deck-over.png', optimize=True)

# ------------------------------------------------------------------ verify
ar = rot[:, :, 3:4] / 255.0
al = lig[:, :, 3:4] / 255.0
ad = deck[:, :, 3:4] / 255.0
comp = img * (1 - ar) + rot[:, :, :3] * ar
comp = comp * (1 - al) + lig[:, :, :3] * al
comp = comp * (1 - ad) + deck[:, :, :3] * ad
err = np.abs(np.round(comp) - img).max(2)
marked = mark.max(2) > 1.0
box = inside | dilate(inside, 3)
quiet = box & ~marked & ~occ_deck
print(f'rest composite vs painting (marks + occluders aside): '
      f'max {err[quiet].max():.0f}, mean {err[quiet].mean():.3f}')

print('\nCSS constants:')
print(f'  --disc-spindle-x: {cx:.3f}px;')
print(f'  --disc-spindle-y: {cy:.3f}px;')
print(f'  --disc-tilt: {np.degrees(phi):.4f}deg;')
print(f'  --disc-squash: {B / A:.6f};')
