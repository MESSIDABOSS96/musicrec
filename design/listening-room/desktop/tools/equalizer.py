"""
Make the desktop stereo's EQ display dance.

    roomd.png  ->  eq-loop.png     16 frames of the segmented level meter

Direct port of the mobile tools/scenery/equalizer.py: measure the painted
display (lit segments by colour, columns, the sloped shelf line their
bases stand on), erase it, redraw every column per frame as a stack of
ember-to-hot segments riding closed sinusoids, frame 1 reproducing the
painting's own levels. See that file and the README for the reasoning.

Run from desktop/tools/. Needs numpy and Pillow.
"""
import numpy as np
from PIL import Image

SRC = '../assets/roomd.png'
img = np.asarray(Image.open(SRC).convert('RGB')).astype(np.float32)
H, W = img.shape[:2]

PX0, PY0, PX1, PY1 = 1040, 848, 1136, 904
N_FRAMES = 16
SEG_PITCH = 3.4
SEG_LIT = 2.4
N_SEG = 9

patch = img[PY0:PY1, PX0:PX1].copy()
ph, pw = patch.shape[:2]

r, g, b = patch[..., 0], patch[..., 1], patch[..., 2]
lit = (r > 120) & (g < 120) & (b < 95) & (r - b > 60)
cols_on = lit.any(0)
bars = []
x = 0
while x < pw:
    if cols_on[x]:
        x1 = x
        while x1 < pw and cols_on[x1]:
            x1 += 1
        ys = np.nonzero(lit[:, x:x1])[0]
        if (x1 - x) >= 2 and len(ys) >= 4:
            bars.append(dict(x0=x, x1=x1, base=ys.max() + 1.0, top=ys.min()))
        x = x1
    else:
        x += 1
print(f'{len(bars)} bars found')

cx = np.array([(bb['x0'] + bb['x1']) / 2 for bb in bars])
cb = np.array([bb['base'] for bb in bars])
m, c = np.polyfit(cx, cb, 1)
print(f'baseline slope {m:.3f}  ({np.degrees(np.arctan(m)):.1f} deg)')
levels0 = np.array([
    int(np.clip(np.round((m * (bb['x0'] + bb['x1']) / 2 + c - bb['top']) / SEG_PITCH),
                1, N_SEG))
    for bb in bars])
print('painted levels:', levels0)

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

C_LO = np.array((166, 48, 22), np.float32)
C_HI = np.array((232, 96, 34), np.float32)
C_TIP = np.array((248, 140, 60), np.float32)

yy, xx = np.mgrid[0:ph, 0:pw].astype(np.float32)
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
        gg = np.exp(-(((xx - bx) / 4.0) ** 2
                      + ((yy - (base - lv[i] * SEG_PITCH / 2)) / (lv[i] * 2.0)) ** 2))
        glow = np.maximum(glow, gg * 0.16)
    out = out * (1 - glow[:, :, None]) + C_HI[None, None, :] * glow[:, :, None]
    a = paint[:, :, 3:4]
    out = out * (1 - a) + paint[:, :, :3] * a
    frames.append(np.clip(out, 0, 255))

sheet = np.concatenate(frames, axis=1)
Image.fromarray(np.round(sheet).astype(np.uint8)).save(
    '../assets/eq-loop.png', optimize=True)

print('  .art-slot--eq-meter {')
print(f'    --x: {PX0}px; --y: {PY0}px; --w: {pw}px; --h: {ph}px;')
print(f'  }}  /* sheet: {N_FRAMES} frames, frame step {pw}px, total {N_FRAMES * pw}px */')

row = Image.new('RGB', (pw * (N_FRAMES + 1), ph))
row.paste(Image.fromarray(patch.astype(np.uint8)), (0, 0))
for k in range(N_FRAMES):
    row.paste(Image.fromarray(frames[k].astype(np.uint8)), (pw * (k + 1), 0))
row.resize((pw * (N_FRAMES + 1) * 3, ph * 3), Image.NEAREST).save('dbg-eq.png')
print('wrote dbg-eq.png')
