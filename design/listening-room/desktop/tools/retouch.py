"""
Paint the placeholder product UI out of the desktop plate.

    roomd.original.png  ->  roomd.png

As delivered, the artwork has the identity block painted into the wall:
WELCOME TO, a [PRODUCT NAME] wordmark with its glow halo, [SHORT
TAGLINE], and the [PRIMARY ACTION] pill. The live DOM draws all of that,
so the wall behind it is rebuilt here.

Each box is filled by blending a horizontal and a vertical linear
interpolation from the wall just outside it (the wall is smooth, so this
is enough), then re-grained with noise matched to the local wall texture
so the patch does not read as airbrushed. Boxes are generous: the
wordmark's glow reaches well past its glyphs.

Run from desktop/tools/. Needs numpy and Pillow.
"""
import numpy as np
from PIL import Image

SRC = '../assets/roomd.original.png'
OUT = '../assets/roomd.png'

img = np.asarray(Image.open(SRC).convert('RGB')).astype(np.float32)
H, W = img.shape[:2]
rng = np.random.default_rng(11)

# x0, y0, x1, y1 — generous, glow included
BOXES = [
    (630, 374, 790, 410),    # WELCOME TO
    (545, 405, 905, 470),    # [PRODUCT NAME] + halo
    (640, 470, 815, 508),    # [SHORT TAGLINE]
    (600, 515, 862, 585),    # [PRIMARY ACTION] pill + its bloom
]


def blur(a, k, n=1):
    for _ in range(n):
        p = np.pad(a, ((k // 2, k // 2), (k // 2, k // 2), (0, 0)), mode='edge')
        acc = np.zeros_like(a)
        for dy in range(k):
            for dx in range(k):
                acc += p[dy:dy + a.shape[0], dx:dx + a.shape[1]]
        a = acc / (k * k)
    return a


for x0, y0, x1, y1 in BOXES:
    w, h = x1 - x0, y1 - y0
    # margins: a few columns/rows just outside the box, averaged and blurred
    L = blur(img[y0:y1, x0 - 6:x0 - 1], 3).mean(1)      # (h,3)
    R = blur(img[y0:y1, x1 + 1:x1 + 6], 3).mean(1)
    T = blur(img[y0 - 6:y0 - 1, x0:x1], 3).mean(0)      # (w,3)
    B = blur(img[y1 + 1:y1 + 6, x0:x1], 3).mean(0)

    tx = (np.arange(w) + 0.5) / w
    ty = (np.arange(h) + 0.5) / h
    horiz = L[:, None, :] * (1 - tx)[None, :, None] + R[:, None, :] * tx[None, :, None]
    vert = T[None, :, :] * (1 - ty)[:, None, None] + B[None, :, :] * ty[:, None, None]
    # weight toward whichever edge pair is closer
    wx = np.minimum(tx, 1 - tx)[None, :]
    wy = np.minimum(ty, 1 - ty)[:, None]
    a = (wy / np.maximum(wx + wy, 1e-6))[:, :, None]     # near top/bottom -> vert
    fill = horiz * a + vert * (1 - a)

    # matched grain: local wall noise amplitude from the margin strips
    ref = img[y0:y1, x0 - 6:x0 - 1]
    amp = float(np.std(ref - blur(ref, 3)))
    fill += rng.normal(0, amp, fill.shape)
    fill = blur(fill, 3, n=1) * 0.5 + fill * 0.5

    # feather the seam
    fx = np.clip(np.minimum(np.arange(w), w - 1 - np.arange(w)) / 4.0, 0, 1)[None, :]
    fy = np.clip(np.minimum(np.arange(h), h - 1 - np.arange(h)) / 4.0, 0, 1)[:, None]
    f = (fx * fy)[:, :, None]
    img[y0:y1, x0:x1] = img[y0:y1, x0:x1] * (1 - f) + fill * f

Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)).save(OUT, optimize=True)
print('wrote', OUT)
