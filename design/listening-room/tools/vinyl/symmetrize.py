"""
Split the disc's LIGHT from its SURFACE, so the surface can turn.

    vinyl.png  ->  vinyl-rotating.png  ->  vinyl-light.png

Rotating vinyl.png as-is fails perceptually even though the geometry is
exact: the disc carries view-dependent paint — the sheen across its
surface, the glints along the rim — and rotating the disc makes that
light orbit it. Light belongs to the room, not to the record, so the eye
reads the whole disc as a separate object pasted on top of the scene.

The split:

vinyl-rotating.png  the surface that turns. Every pixel replaced by the
                    median of its ring in record space, so the layer is
                    rotationally symmetric and can spin with no artifact
                    at all. Grooves and label edges are concentric, so
                    they survive untouched. Its alpha fades out just
                    inside the rim: the painted rim, its glints, and the
                    disc's front-edge thickness stay in the plate and
                    never move. On top of the symmetric surface, two
                    deliberately asymmetric marks — a warm smudge on the
                    label and a dust fleck out on the grooves — because a
                    perfectly symmetric disc spins invisibly.
vinyl-light.png     everything the surface lost: the signed residual
                    between the real disc and its symmetric version,
                    encoded as a static normal-composite layer. The sheen
                    and shading live here and never rotate. The marks
                    pass underneath it, dimming where the light is strong,
                    which is what a real reflection does to detail.

Exactness at rest: the layer chain
    plate -> vinyl-rotating -> vinyl-light -> deck-over
reproduces what the chain plate -> vinyl -> deck-over produced, to
rounding, everywhere outside the two marks. The solve below picks, per
pixel, the most transparent (colour, alpha) whose normal composite over
the symmetric surface lands exactly on the old composite.

Run from tools/vinyl/. Needs numpy and Pillow.
"""
import numpy as np
from PIL import Image

from masks import dilate
import recordspace as R
from split_vinyl import alpha_disc, img, inside, r, th

SRC = '../../assets/vinyl.png'

vin = np.asarray(Image.open(SRC).convert('RGBA')).astype(np.float32)
V, aD = vin[:, :, :3], vin[:, :, 3] / 255.0
H, W = V.shape[:2]

# ------------------------------------------------------------------ surface
# The symmetric record. vinyl.png is the right input: occluded patches are
# already reconstructed and the broad glare already lifted out, so its rings
# are clean all the way round.
base = R.radial_baseline(V, r, inside)

# Alpha: the disc silhouette, faded out before the rim so the painted rim
# stays static in the plate. Fully open inside r=0.94, gone by r=0.985.
fade = np.clip((0.985 - r) / 0.045, 0.0, 1.0)
aR = alpha_disc * fade

# ------------------------------------------------------------------- marks
# Small, warm, and asymmetric — without them a symmetric disc spins
# invisibly. Drawn in record space so they ride the same geometry as the
# rotation. Peak strengths chosen to read in motion, not in a still.


def blob(r0, th0, sr, sth, gain):
    dth = np.mod(th - th0 + np.pi, 2 * np.pi) - np.pi
    g = np.exp(-0.5 * (((r - r0) / sr) ** 2 + (dth / sth) ** 2))
    return g[:, :, None] * np.array(gain, np.float32)


mark = (blob(0.26, 0.9, 0.11, 0.55, (30, 18, 8))       # smudge on the label
        + blob(0.72, -1.8, 0.018, 0.06, (26, 20, 12)))  # fleck on the grooves
surface = np.clip(base + mark, 0, 255)

# -------------------------------------------------------------------- light
# Static layer solved so that at rest the new chain reproduces the old one.
# T is what plate -> vinyl used to compose to; B0 is what plate -> rotating
# composes to now (marks excluded — they must survive, not be cancelled).
O = img
T = O * (1 - aD[:, :, None]) + V * aD[:, :, None]
B0 = O * (1 - aR[:, :, None]) + base * aR[:, :, None]
d = T - B0

# Most transparent exact solution of  C*a + B0*(1-a) = T  with C in range:
# lightening pixels are bounded by C <= 255, darkening ones by C >= 0.
with np.errstate(divide='ignore', invalid='ignore'):
    need = np.where(d > 0, d / np.maximum(255.0 - B0, 1e-6),
                    -d / np.maximum(B0, 1e-6))
aL = np.clip(need.max(axis=2), 0.0, 1.0)
active = (np.abs(d).max(axis=2) > 0.5) & (r <= 1.06)
aL = np.where(active, np.maximum(aL, 1.0 / 255.0), 0.0)
C = np.where(aL[:, :, None] > 0, B0 + d / np.maximum(aL[:, :, None], 1e-6), 0.0)
C = np.clip(C, 0, 255)

# ---------------------------------------------------------------- assemble
rot = np.zeros((H, W, 4), np.float32)
rot[:, :, :3] = surface
rot[:, :, 3] = aR * 255.0

lig = np.zeros((H, W, 4), np.float32)
lig[:, :, :3] = C
lig[:, :, 3] = aL * 255.0

# Same margin bleed as split_vinyl.py: the browser downscales before
# compositing, and colour from fully transparent pixels enters that filter.
for lay in (rot, lig):
    clear = lay[:, :, 3] == 0
    near = dilate(~clear, 8)
    lay[clear & near, :3] = img[clear & near]
    lay[clear & ~near, :3] = 0

rot8 = np.round(rot).astype(np.uint8)
lig8 = np.round(lig).astype(np.uint8)


def build():
    Image.fromarray(rot8).save('../../assets/vinyl-rotating.png', optimize=True)
    Image.fromarray(lig8).save('../../assets/vinyl-light.png', optimize=True)

    # Predict the rest composite of the new chain against the old one.
    ar = rot8[:, :, 3:4].astype(np.float32) / 255.0
    al = lig8[:, :, 3:4].astype(np.float32) / 255.0
    comp = O * (1 - ar) + rot8[:, :, :3].astype(np.float32) * ar
    comp = comp * (1 - al) + lig8[:, :, :3].astype(np.float32) * al
    err = np.abs(np.round(comp) - np.round(T)).max(2)
    marked = mark.max(2) > 1.0
    box = inside | dilate(inside, 3)
    quiet = box & ~marked
    print(f'  rest composite vs old chain, marks excluded: '
          f'max {err[quiet].max():.0f}, mean {err[quiet].mean():.3f}')
    print(f'  mark region: {int(marked.sum())} px, '
          f'peak departure {err[box & marked].max():.0f} levels')


if __name__ == '__main__':
    build()
