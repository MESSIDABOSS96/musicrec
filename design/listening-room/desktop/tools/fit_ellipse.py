"""
Fit the record's rim ellipse on the desktop plate.

A moment fit fails here — everything around the disc is nearly as dark
as the disc, so the mask bleeds into the plinth. Instead: start from a
hand-measured guess and hill-climb the five parameters to maximise the
inside/outside brightness step across the rim, sampled along the ellipse
normal, skipping the arc under the tonearm. dbg-ellipse.png shows the
result in red on a 3x crop; the constant in split_vinyl.py comes from
here.
"""
import numpy as np
from PIL import Image

img = np.asarray(Image.open('../assets/roomd.png').convert('RGB')).astype(np.float32)
lum = img.mean(2)
H, W = lum.shape

# hand-measured from the 3x crop
P0 = np.array([1112.0, 677.0, 93.0, 30.5, np.radians(4.0)])

T = np.linspace(0, 2 * np.pi, 240, endpoint=False)


def rim_pts(p, t):
    cx, cy, A, B, phi = p
    c, s = np.cos(phi), np.sin(phi)
    u, v = A * np.cos(t), B * np.sin(t)
    x = cx + u * c - v * s
    y = cy + u * s + v * c
    # outward normal of the ellipse, in image space
    nu, nv = np.cos(t) / A * B, np.sin(t) / B * A     # gradient direction pre-rotation
    nx = nu * c - nv * s
    ny = nu * s + nv * c
    n = np.hypot(nx, ny)
    return x, y, nx / n, ny / n


def sample(x, y):
    xi = np.clip(x, 0, W - 1.001)
    yi = np.clip(y, 0, H - 1.001)
    x0, y0 = xi.astype(int), yi.astype(int)
    fx, fy = xi - x0, yi - y0
    return (lum[y0, x0] * (1 - fx) * (1 - fy) + lum[y0, x0 + 1] * fx * (1 - fy)
            + lum[y0 + 1, x0] * (1 - fx) * fy + lum[y0 + 1, x0 + 1] * fx * fy)


def score(p):
    x, y, nx, ny = rim_pts(p, T)
    # skip the arc under the tonearm (right side, roughly t in [-0.5, 0.6])
    keep = ~((T < 0.6) | (T > 2 * np.pi - 0.5))
    step = 0.0
    for d in (1.5, 2.5, 3.5):
        step += sample(x + nx * d, y + ny * d) - sample(x - nx * d, y - ny * d)
    return float(step[keep].mean())


p = P0.copy()
steps = np.array([0.5, 0.5, 0.5, 0.3, np.radians(0.4)])
for it in range(200):
    improved = False
    for i in range(5):
        for sgn in (1, -1):
            q = p.copy()
            q[i] += sgn * steps[i]
            if score(q) > score(p):
                p = q
                improved = True
    if not improved:
        steps *= 0.5
        if steps[0] < 0.02:
            break
print(f'fit: cx={p[0]:.3f} cy={p[1]:.3f} A={p[2]:.3f} B={p[3]:.3f} '
      f'phi={np.degrees(p[4]):.3f}deg  score={score(p):.2f} (start {score(P0):.2f})')
print(f'ELLIPSE = [{p[0]:.4f}, {p[1]:.4f}, {p[2]:.4f}, {p[3]:.4f}, {p[4]:.6f}]')

X0, Y0, X1, Y1 = 990, 620, 1240, 740
vis = np.clip(img[Y0:Y1, X0:X1].copy() * 1.5, 0, 255)
t = np.linspace(0, 2 * np.pi, 1440)
x, y, _, _ = rim_pts(p, t)
for xi, yi in zip(np.round(x).astype(int) - X0, np.round(y).astype(int) - Y0):
    if 0 <= yi < vis.shape[0] and 0 <= xi < vis.shape[1]:
        vis[yi, xi] = (255, 40, 40)
Image.fromarray(vis.astype(np.uint8)).resize(((X1 - X0) * 3, (Y1 - Y0) * 3),
                                             Image.NEAREST).save('dbg-ellipse.png')
print('wrote dbg-ellipse.png')
