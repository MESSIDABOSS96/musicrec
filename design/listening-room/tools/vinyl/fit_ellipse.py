"""
Fit the record's outline in room2.png.

The silhouette has to be a true ellipse, not a traced outline: a record spins
about its own axis, so the projected silhouette is invariant under that spin
only if it is exactly the projection of a circle. A traced mask would breathe
at the rim as the disc turns.

Per-ray edge detection fails here. Contrast reverses around the rim — the
deck is brighter than the record on the left, darker on the right — and the
label, the tonearm and the lamp reflections all carry stronger gradients than
the rim itself, so "strongest edge along the ray" locks onto the wrong thing.

Instead, treat it as one closed curve and maximise the MEDIAN of the
gradient projected on the curve normal. The rim supports edge energy all the
way round; a highlight streak only supports a short arc, and the median
ignores it. Five parameters, refined by coordinate descent.
"""
import numpy as np
from PIL import Image

SX, SY = 853 / 390.0, 1844 / 844.0

img = np.asarray(Image.open('../../assets/room2.png').convert('RGB')).astype(np.float32)
lum = img.mean(2)
H, W = lum.shape


def blur(a, k=3):
    p = np.pad(a, k // 2, mode='edge')
    o = np.zeros_like(a)
    for dy in range(k):
        for dx in range(k):
            o += p[dy:dy + a.shape[0], dx:dx + a.shape[1]]
    return o / (k * k)


sm = blur(lum, 3)
Gy, Gx = np.gradient(sm)


def bilinear(L, x, y):
    x0 = np.clip(np.floor(x).astype(int), 0, W - 2)
    y0 = np.clip(np.floor(y).astype(int), 0, H - 2)
    fx, fy = x - x0, y - y0
    return (L[y0, x0] * (1 - fx) * (1 - fy) + L[y0, x0 + 1] * fx * (1 - fy)
            + L[y0 + 1, x0] * (1 - fx) * fy + L[y0 + 1, x0 + 1] * fx * fy)


# Sector around the tonearm's crossing is dropped: the arm's own edges are far
# stronger than the rim and would bias even a robust statistic.
TH = np.linspace(0, 2 * np.pi, 720, endpoint=False)
deg = np.rad2deg(TH)
USE = ~(((deg > 335) | (deg < 30)))


def energy(p):
    cx, cy, A, B, phi = p
    if A <= 10 or B <= 5 or B >= A:
        return -1e9
    th = TH[USE]
    ex, ey = A * np.cos(th), B * np.sin(th)
    c, s = np.cos(phi), np.sin(phi)
    x = cx + ex * c - ey * s
    y = cy + ex * s + ey * c
    # outward normal of the ellipse, rotated into image space
    nx0, ny0 = np.cos(th) / A, np.sin(th) / B
    nx = nx0 * c - ny0 * s
    ny = nx0 * s + ny0 * c
    n = np.hypot(nx, ny)
    nx, ny = nx / n, ny / n
    g = bilinear(Gx, x, y) * nx + bilinear(Gy, x, y) * ny
    return np.median(np.abs(g))


p = np.array([222.5 * SX, 569 * SY, 60 * SX, 26 * SY, np.deg2rad(-3)])
steps = np.array([4.0, 4.0, 6.0, 4.0, np.deg2rad(4)])
best = energy(p)
for _ in range(60):
    improved = False
    for i in range(5):
        for sgn in (+1, -1):
            q = p.copy()
            q[i] += sgn * steps[i]
            e = energy(q)
            if e > best:
                best, p, improved = e, q, True
    if not improved:
        steps *= 0.5
        if steps[0] < 0.02:
            break

cx, cy, A, B, phi = p
phi = (phi + np.pi) % np.pi
if phi > np.pi / 2:
    phi -= np.pi

print('fitted ellipse:')
print(f'  centre    source ({cx:.2f}, {cy:.2f})   scene ({cx/SX:.2f}, {cy/SY:.2f})')
print(f'  semi-axes source A={A:.2f} B={B:.2f}   scene {A/SX:.2f} x {B/SY:.2f}')
print(f'  diameter  scene {2*A/SX:.1f} x {2*B/SY:.1f}')
print(f'  rotation  {np.rad2deg(phi):+.2f} deg')
print(f'  B/A = {B/A:.4f}  -> record plane tilted {np.rad2deg(np.arccos(B/A)):.1f} deg from face-on')
print(f'  edge energy (median |grad.n|) = {best:.3f}')
np.save('ellipse.npy', p)  # feeds the constant in split_vinyl.py
