"""
Make the stereo's EQ display dance.

    room2.png  ->  eq-loop.png     16 frames of the segmented level meter

The display is measured, not assumed: lit segments are found by colour
(the orange bars are the only thing that hot in the window), grouped into
vertical columns, and each bar's base and height are read off the pixels.
The baseline the bars stand on is a fitted line — the receiver's front
leans about 16 degrees in this view and the bars must keep standing on
it, not on a horizontal.

Each frame erases the painted bars (every bar's rows filled straight
across from the screen on either side of it) and redraws every column as
a stack of rounded segments on the same baseline: dim embers at the
bottom, hotter toward the tip, a faint glow bleeding onto the glass.
Heights ride closed sinusoids — different phase and rate per bar, all
periodic in the loop — offset so FRAME 0 REPRODUCES THE PAINTING's
levels exactly. Like the flame, every frame is an opaque patch whose
border pixels are the plate's own: no seam, no plate edit.

Run from tools/scenery/. Needs numpy and Pillow. Prints the slot
geometry (scene px) that styles.css must carry.
"""
import numpy as np
from PIL import Image

SRC = '../../assets/room2.png'
img = np.asarray(Image.open(SRC).convert('RGB')).astype(np.float32)
H, W = img.shape[:2]
SX, SY = W / 390.0, H / 844.0

# patch around the meter, clear of the REC text above and the knob right
PX0, PY0, PX1, PY1 = 430, 1538, 528, 1600
N_FRAMES = 16
SEG_PITCH = 4.5          # centre-to-centre of segments, image px
SEG_LIT = 3.2            # lit height within the pitch
N_SEG = 7                # a full column

patch = img[PY0:PY1, PX0:PX1].copy()
ph, pw = patch.shape[:2]

# ------------------------------------------------------------- measurement
r, g, b = patch[..., 0], patch[..., 1], patch[..., 2]
lit = (r > 130) & (g < 130) & (b < 90) & (r - b > 70)
cols_on = lit.any(0)
bars = []
x = 0
while x < pw:
    if cols_on[x]:
        x1 = x
        while x1 < pw and cols_on[x1]:
            x1 += 1
        ys = np.nonzero(lit[:, x:x1])[0]
        bars.append(dict(x0=x, x1=x1, base=ys.max() + 1.0, top=ys.min()))
        x = x1
    else:
        x += 1
print(f'{len(bars)} bars found')

# the sloped shelf line the columns stand on
cx = np.array([(bb['x0'] + bb['x1']) / 2 for bb in bars])
cb = np.array([bb['base'] for bb in bars])
m, c = np.polyfit(cx, cb, 1)
print(f'baseline slope {m:.3f}  ({np.degrees(np.arctan(m)):.1f} deg)')
levels0 = np.array([
    int(np.clip(np.round((m * (bb['x0'] + bb['x1']) / 2 + c - bb['top']) / SEG_PITCH),
                1, N_SEG))
    for bb in bars])
print('painted levels:', levels0)

# --------------------------------------------------- erase the painted bars
bg = patch.copy()
for bb in bars:
    x0, x1 = bb['x0'] - 1, bb['x1'] + 1
    ys = np.nonzero(lit[:, bb['x0']:bb['x1']])[0]
    y0, y1 = max(ys.min() - 2, 0), min(int(bb['base']) + 3, ph)
    l_, r_ = max(x0 - 1, 0), min(x1 + 1, pw - 1)
    t = (np.arange(x0, x1) - x0 + 1) / (x1 - x0 + 1)
    for row in range(y0, y1):
        bg[row, x0:x1] = (bg[row, l_][None, :] * (1 - t[:, None])
                          + bg[row, r_][None, :] * t[:, None])
k = 3
p = np.pad(bg, ((1, 1), (1, 1), (0, 0)), mode='edge')
bg = sum(p[dy:dy + ph, dx:dx + pw] for dy in range(k) for dx in range(k)) / 9.0

# ------------------------------------------------------------------ redraw
# ember ramp, bottom of a column to its tip
C_LO = np.array((166, 48, 22), np.float32)
C_HI = np.array((232, 96, 34), np.float32)
C_TIP = np.array((248, 140, 60), np.float32)

yy, xx = np.mgrid[0:ph, 0:pw].astype(np.float32)

# per-bar motion character, deterministic
rng = np.random.default_rng(7)
ph1 = rng.uniform(0, 2 * np.pi, len(bars))
ph2 = rng.uniform(0, 2 * np.pi, len(bars))
a1 = rng.uniform(0.9, 1.7, len(bars))
a2 = rng.uniform(0.5, 1.1, len(bars))


def levels(k):
    p = 2 * np.pi * k / N_FRAMES
    drift = (a1 * np.sin(p + ph1) + a2 * np.sin(2 * p + ph2)
             + 0.5 * np.sin(3 * p + 0.8))
    at0 = (a1 * np.sin(ph1) + a2 * np.sin(ph2) + 0.5 * np.sin(0.8))
    return np.clip(np.round(levels0 + drift - at0), 1, N_SEG).astype(int)


frames = []
for k in range(N_FRAMES):
    lv = levels(k)
    flick = 1.0 + 0.04 * np.sin(2 * np.pi * k / N_FRAMES * 2 + 1.3)
    out = bg.copy()
    glow = np.zeros((ph, pw), np.float32)
    paint = np.zeros((ph, pw, 4), np.float32)
    for i, bb in enumerate(bars):
        bx = (bb['x0'] + bb['x1']) / 2
        base = m * bx + c
        for s in range(lv[i]):
            yc = base - (s + 0.5) * SEG_PITCH
            cov = (np.clip((SEG_LIT / 2 + 0.5) - np.abs(yy - yc), 0, 1)
                   * np.clip(np.minimum(xx - (bb['x0'] - 0.5),
                                        (bb['x1'] - 0.5) - xx) + 0.5, 0, 1))
            t = s / (N_SEG - 1)
            col = C_LO * (1 - t) + C_HI * t
            if s == lv[i] - 1 and lv[i] >= 3:
                col = C_TIP
            a = np.clip(cov, 0, 1)[:, :, None]
            paint[:, :, :3] = (paint[:, :, :3] * (1 - a)
                               + col[None, None, :] * flick * a)
            paint[:, :, 3:4] = np.maximum(paint[:, :, 3:4], a)
        gg = np.exp(-(((xx - bx) / 4.5) ** 2
                      + ((yy - (base - lv[i] * SEG_PITCH / 2)) / (lv[i] * 2.6)) ** 2))
        glow = np.maximum(glow, gg * 0.16)
    out = out * (1 - glow[:, :, None]) + C_HI[None, None, :] * glow[:, :, None]
    a = paint[:, :, 3:4]
    out = out * (1 - a) + paint[:, :, :3] * a
    frames.append(np.clip(out, 0, 255))

sheet = np.concatenate(frames, axis=1)
Image.fromarray(np.round(sheet).astype(np.uint8)).save(
    '../../assets/eq-loop.png', optimize=True)

print('  .art-slot--eq-meter {')
print(f'    --x: {PX0 / SX:.2f}px; --y: {PY0 / SY:.2f}px; '
      f'--w: {(PX1 - PX0) / SX:.2f}px; --h: {(PY1 - PY0) / SY:.2f}px;')
print(f'  }}  /* sheet: {N_FRAMES} frames, frame step {(PX1 - PX0) / SX:.2f}px, '
      f'total {N_FRAMES * (PX1 - PX0) / SX:.2f}px */')

# frame 0 vs painting: same levels, redrawn segments — report the departure
err = np.abs(np.round(frames[0]) - patch).max()
print(f'frame 0 vs painted meter: max departure {err:.0f} levels '
      f'(a redraw, not a copy — eyeball dbg-eq.png)')
row = Image.new('RGB', (pw * (N_FRAMES + 1), ph))
row.paste(Image.fromarray(patch.astype(np.uint8)), (0, 0))
for k in range(N_FRAMES):
    row.paste(Image.fromarray(frames[k].astype(np.uint8)), (pw * (k + 1), 0))
row.resize((pw * (N_FRAMES + 1) * 3, ph * 3), Image.NEAREST).save('dbg-eq.png')
print('wrote dbg-eq.png  (painting first, then the 16 frames)')
