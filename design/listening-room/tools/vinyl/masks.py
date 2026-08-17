"""Find what sits ON the record: the tonearm, the headshell, the spindle."""
import numpy as np
from PIL import Image
import recordspace as R

SX, SY = R.SX, R.SY


def components(mask):
    """4-connected components, largest first. Returns list of boolean masks."""
    H, W = mask.shape
    lab = np.zeros((H, W), np.int32)
    cur = 0
    out = []
    ys, xs = np.nonzero(mask)
    for sy0, sx0 in zip(ys, xs):
        if lab[sy0, sx0]:
            continue
        cur += 1
        stack = [(sy0, sx0)]
        lab[sy0, sx0] = cur
        pix = []
        while stack:
            y, x = stack.pop()
            pix.append((y, x))
            for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                ny, nx = y + dy, x + dx
                if 0 <= ny < H and 0 <= nx < W and mask[ny, nx] and not lab[ny, nx]:
                    lab[ny, nx] = cur
                    stack.append((ny, nx))
        m = np.zeros((H, W), bool)
        a = np.array(pix)
        m[a[:, 0], a[:, 1]] = True
        out.append(m)
    out.sort(key=lambda m: -m.sum())
    return out


def dilate(m, k):
    o = m.copy()
    for _ in range(k):
        p = np.pad(o, 1, constant_values=False)
        o = (p[1:-1, 1:-1] | p[:-2, 1:-1] | p[2:, 1:-1] | p[1:-1, :-2] | p[1:-1, 2:])
    return o


def erode(m, k):
    return ~dilate(~m, k)


if __name__ == '__main__':
    img = R.load()
    el = np.load('ellipse.npy')
    cx, cy, A, B, phi = el
    r, th, grad = R.geometry(img.shape, el)
    inside = r <= 1.0
    base = R.radial_baseline(img, r, inside)
    dev = (img - base).max(2)

    T = 55
    cand = (dev > T) & (r < 0.98)
    comps = components(cand)
    print(f'components of (deviation > {T}) inside the disc:')
    for i, m in enumerate(comps[:10]):
        ys, xs = np.nonzero(m)
        print(f'  #{i}  {m.sum():5d}px   scene x {xs.min()/SX:6.1f}-{xs.max()/SX:6.1f}'
              f'   y {ys.min()/SY:6.1f}-{ys.max()/SY:6.1f}'
              f'   r {r[m].min():.2f}-{r[m].max():.2f}   peak dev {dev[m].max():5.1f}')

    x0, x1 = int(cx - A - 14), int(cx + A + 14)
    y0, y1 = int(cy - B - 14), int(cy + B + 14)
    vis = np.clip(img[y0:y1, x0:x1].copy(), 0, 255)
    palette = [(255, 60, 60), (60, 255, 120), (90, 160, 255), (255, 220, 60),
               (255, 120, 255), (120, 255, 255), (255, 160, 60)]
    for i, m in enumerate(comps[:7]):
        c = np.array(palette[i], np.float32)
        sel = m[y0:y1, x0:x1]
        vis[sel] = vis[sel] * 0.35 + c * 0.65
    Image.fromarray(vis.astype(np.uint8)).resize(((x1 - x0) * 3, (y1 - y0) * 3),
                                                 Image.NEAREST).save('dbg-comps.png')
    print('wrote dbg-comps.png  (colours follow the order printed above)')
