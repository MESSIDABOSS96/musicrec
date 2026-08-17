"""
Paint the baked-in placeholder UI text out of room2.png.

Method, per text block:
  1. Take a box that contains the glyphs plus their bloom, and only wall.
  2. Rebuild the wall inside it by transfinite (Coons) interpolation from the
     four boundary strips just outside the box. That reproduces the wall's
     real gradients — it is not a flat fill — and matches the border exactly.
  3. Add back high-frequency texture harvested from clean wall nearby, so the
     rebuilt area is as grainy as its surroundings instead of plastic-smooth.
  4. Feather the outer few pixels so there is no seam.

Boxes are processed top-to-bottom; a box may read its upper boundary from a
box already rebuilt above it, which is what lets adjacent lines be handled
separately instead of as one large smooth blob.
"""
import numpy as np
from PIL import Image

SRC = 'assets/room2.original.png'   # run from design/listening-room/
OUT = 'assets/room2.png'

SX, SY = 853 / 390.0, 1844 / 844.0          # source px per scene px
rng = np.random.default_rng(7)


def sx(v): return int(round(v * SX))
def sy(v): return int(round(v * SY))


def smooth1d(arr, k):
    """Moving average along axis 0, edge-padded. arr is (N,3)."""
    if k <= 1:
        return arr
    pad = np.pad(arr, ((k // 2, k // 2), (0, 0)), mode='edge')
    out = np.zeros_like(arr)
    for i in range(k):
        out += pad[i:i + arr.shape[0]]
    return out / k


def blur(img, k):
    """Box blur, edge-padded. img is (H,W,3)."""
    pad = np.pad(img, ((k // 2, k // 2), (k // 2, k // 2), (0, 0)), mode='edge')
    out = np.zeros_like(img)
    for dy in range(k):
        for dx in range(k):
            out += pad[dy:dy + img.shape[0], dx:dx + img.shape[1]]
    return out / (k * k)


def coons(a, y0, y1, x0, x1, bw, sm):
    """Transfinite interpolation of the box from the strips just outside it."""
    top    = smooth1d(a[y0 - bw:y0,  x0:x1].mean(0), sm)      # (W,3)
    bottom = smooth1d(a[y1:y1 + bw,  x0:x1].mean(0), sm)      # (W,3)
    left   = smooth1d(a[y0:y1, x0 - bw:x0].mean(1), sm)       # (H,3)
    right  = smooth1d(a[y0:y1, x1:x1 + bw].mean(1), sm)       # (H,3)

    H, W = y1 - y0, x1 - x0
    s = ((np.arange(H) + 1) / (H + 1))[:, None, None]
    t = ((np.arange(W) + 1) / (W + 1))[None, :, None]

    # Corners reconciled between the two edges that meet there.
    TL = (top[0]  + left[0])  / 2
    TR = (top[-1] + right[0]) / 2
    BL = (bottom[0]  + left[-1])  / 2
    BR = (bottom[-1] + right[-1]) / 2

    ruled = ((1 - s) * top[None, :, :] + s * bottom[None, :, :]
             + (1 - t) * left[:, None, :] + t * right[:, None, :])
    bilin = ((1 - s) * (1 - t) * TL + (1 - s) * t * TR
             + s * (1 - t) * BL + s * t * BR)
    return ruled - bilin


def grain_from(a, box, shape, kx=2, ky=3):
    """
    Texture matching a clean donor's grain, synthesised rather than copied.

    Copying a donor patch reproduces whatever shapes it contains — an early
    pass tiled a donor holding a vine leaf and stamped ghost foliage across
    the wall. Matching the donor's full 2D spectrum instead inherits the
    donor rectangle's aspect ratio as directional streaking, which was just as
    wrong (horizontal streaks over a wall that brushes vertical).

    So: shape white noise with a small separable kernel, wider vertically to
    match the wall's brush direction, and scale it to the donor's measured
    per-channel amplitude. Grain strength and direction are right; no shape
    from the donor can survive.

    One noise field drives all three channels. Drawing each channel
    independently produces chroma speckle — coloured static — where the real
    surface varies almost entirely in luminance.
    """
    gy0, gy1, gx0, gx1 = box
    donor = a[gy0:gy1, gx0:gx1]
    resid = donor - blur(donor, 5)
    sd = resid.std(axis=(0, 1))                     # per channel, the target

    H, W = shape
    n = rng.standard_normal((H + 2 * ky, W + 2 * kx)).astype(np.float32)
    for k, ax in ((kx, 1), (ky, 0)):
        if k > 1:
            c = np.cumsum(n, axis=ax)
            c = np.concatenate([np.zeros_like(np.take(c, [0], ax)), c], axis=ax)
            n = (np.take(c, range(k, n.shape[ax] + 1), ax)
                 - np.take(c, range(0, n.shape[ax] + 1 - k), ax)) / k
    n = n[:H, :W]
    n = n / max(n.std(), 1e-8)
    return n[:, :, None] * sd[None, None, :]


def feather(H, W, f):
    """1 in the interior, ramping to 0 at the box edge."""
    fy = np.clip((np.minimum(np.arange(H), H - 1 - np.arange(H)) + 0.5) / f, 0, 1)
    fx = np.clip((np.minimum(np.arange(W), W - 1 - np.arange(W)) + 0.5) / f, 0, 1)
    return (fy[:, None] * fx[None, :])[:, :, None]


def clear(a, name, box_scene, donor_scene, bw=5, sm=15, fth=4, grain=1.0):
    x0, y0, x1, y1 = (sx(box_scene[0]), sy(box_scene[1]),
                      sx(box_scene[2]), sy(box_scene[3]))
    H, W = y1 - y0, x1 - x0
    fill = coons(a, y0, y1, x0, x1, bw, sm)
    if grain:
        g = grain_from(a, (sy(donor_scene[1]), sy(donor_scene[3]),
                           sx(donor_scene[0]), sx(donor_scene[2])), (H, W))
        fill = fill + g * grain
    m = feather(H, W, fth)
    before = a[y0:y1, x0:x1].copy()
    a[y0:y1, x0:x1] = fill * m + before * (1 - m)
    print(f'  {name:9s} scene{tuple(box_scene)}  src {W}x{H}px  '
          f'peak removed {before.mean(2).max():5.1f} -> {a[y0:y1, x0:x1].mean(2).max():5.1f}')


a = np.asarray(Image.open(SRC).convert('RGB')).astype(np.float32)

# Clean wall donors for texture. Both are bands the luminance profile shows
# to be flat and ink-free — the band above the text block is NOT usable, it
# catches the hanging vine.
WALL_DONOR = (110, 494, 240, 503)     # flat wall between the CTA and SCROLL
LID_DONOR  = (268, 512, 310, 522)     # flat lid below the wordmark

# Row bands come from the luminance profile through the text column; x bounds
# are clamped clear of the wall panel edge at x=100-101 and the poster at x>=246.
print('rebuilding wall behind the central text block:')
clear(a, 'welcome',  (140, 377, 205, 388),  WALL_DONOR)

# Left edge held at 105: x=100-101 is a real wall-panel edge (a highlight line
# over a shadow line) that must survive. Right edge held at 243: the poster
# beside the wall starts at x=246.
clear(a, 'name',     (105, 393, 243, 424),  WALL_DONOR, bw=4)

# Both tagline lines in one box — the 4px gap between them is not worth
# keeping, and splitting it left the ascender tips of line 2 in the feather.
clear(a, 'tagline',  (121, 430, 220, 458),  WALL_DONOR)

# The tightest box in the set. The pill's right edge reaches x=229.1 and the
# turntable lid's frame starts at x=232.7, so the box stops at 231 and reads a
# 2px boundary strip out of the 3.6px gap between them. Any wider destroys the
# lid frame. The feather has to come down to 2px to match: at 4px the pill's
# own right border sat inside the ramp and survived as a faint vertical line.
clear(a, 'pill',     (107, 462, 231, 496),  WALL_DONOR, bw=2, fth=2)

clear(a, 'scroll',   (125, 504, 214, 515),  WALL_DONOR)
clear(a, 'chevron',  (157, 519, 180, 531),  WALL_DONOR)

print('rebuilding the turntable lid:')
clear(a, 'lid',      (264, 484, 313, 510),  LID_DONOR, bw=4, sm=11, fth=3)


def audit(label, x0, y0, x1, y1):
    """Report the brightest surviving pixel, to catch ink outside a box."""
    reg = a[sy(y0):sy(y1), sx(x0):sx(x1)].mean(2)
    i = np.unravel_index(reg.argmax(), reg.shape)
    print(f'  {label:8s} brightest {reg.max():5.1f} at scene '
          f'({(sx(x0) + i[1]) / SX:.0f}, {(sy(y0) + i[0]) / SY:.0f})   '
          f'median {np.median(reg):5.1f}')


print('audit — anything well above the median is surviving ink:')
audit('wall', 102, 372, 230, 534)     # stops short of the lid frame at x=232.7
audit('gap', 230, 372, 244, 455)      # wall right of the text, above the lid
audit('lid', 262, 482, 314, 512)

Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).save(OUT, optimize=True)
print('wrote', OUT)
