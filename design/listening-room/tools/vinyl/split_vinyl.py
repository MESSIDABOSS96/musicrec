"""
Split the record out of room2.png into two registered layers.

    room2.png  ->  vinyl.png  ->  deck-over.png

vinyl.png     the disc alone: one complete uninterrupted record, with the
              things that sit on top of it removed and the surface under them
              reconstructed, and with the lamp glare taken out.
deck-over.png everything static that overlays the disc: the tonearm and
              headshell, the spindle, the case's rear edge where it crosses
              the far rim, and the glare — the glare as a light layer, so the
              disc still shows through it and can later turn underneath.

Why the composite is exact at rest: inside the occluders deck-over carries the
original pixels at full opacity, and everywhere else vinyl + glare is defined
to sum back to the original. The rim needs no special care either — where the
silhouette is partly transparent the baked record shows through underneath at
exactly the same colour, so a soft edge cannot produce a seam or a double edge.

Everything is expressed in the record's own frame (r, th) so that the same
geometry drives the reconstruction, the glare estimate and, later, rotation.
"""
import numpy as np
from PIL import Image
import recordspace as R
from masks import dilate

SX, SY = R.SX, R.SY
SRC = '../../assets/room2.png'   # run from tools/vinyl/
img = R.load(SRC)
H, W = img.shape[:2]
# The record's outline, from fit_ellipse.py: centre, semi-axes and rotation
# in source pixels. Everything downstream is derived from these five numbers.
el = np.array([484.64743589743586, 1238.6759478672986, 133.29294871794872, 53.52843601895734, -0.05672320068981571])
cx, cy, A, B, phi = el
r, th, grad = R.geometry(img.shape, el)

yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
sxx, syy = xx / SX, yy / SY          # scene coordinates

# ---------------------------------------------------------------- silhouette
# Sub-pixel coverage of the ellipse: |grad r| converts the radial error into
# pixels, so the rim lands with the same softness the painted edge has.
alpha_disc = np.clip((1.0 - r) / grad + 0.5, 0.0, 1.0)
inside = r <= 1.0

# ----------------------------------------------------------------- occluders
# The two occluders that cross the rim are carried a little way PAST it. If an
# occluder stopped exactly at r = 1 then alpha and colour would step together
# in the same pixel: the deck layer going transparent at the same place the
# disc's soft edge hands over to the plate. Downscaling averages across that
# step and the two layers no longer reconstruct the original — this was worth
# up to 30 levels along the far rim. Carried past the rim, the deck layer is
# simply opaque original pixels there, which is what the plate holds anyway.
OUT = 1.07

# 1. the case's rear edge, measured as a straight boundary across the far rim
case = (r <= OUT) & (syy < 0.345 * sxx + 460.0)

# 2. the tonearm tube: a band about the measured highlight line
tube_line = -0.275 * sxx + 645.5
tube = (r <= OUT) & (syy - tube_line > -2.0) & (syy - tube_line < 4.5) & (sxx > 250.0)

# 3. the headshell body
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


head = poly(sxx, syy, [(238.6, 571.2), (259.8, 569.8), (256.0, 586.6),
                       (239.0, 588.4)]) & inside

# 4. the spindle
spindle = inside & (sxx > 214.2) & (sxx < 226.4) & (syy > 558.0) & (syy < 568.8)

occ = case | tube | head | spindle
occ = dilate(occ, 1) & (r <= OUT)          # 1px margin so no rim of them is left behind

if __name__ == '__main__':
    x0, x1 = int(cx - A - 16), int(cx + A + 16)
    y0, y1 = int(cy - B - 16), int(cy + B + 16)
    vis = np.clip(img[y0:y1, x0:x1].copy(), 0, 255)
    for m, c in ((case, (90, 160, 255)), (tube, (60, 255, 120)),
                 (head, (255, 220, 60)), (spindle, (255, 60, 200))):
        sel = m[y0:y1, x0:x1]
        vis[sel] = vis[sel] * 0.4 + np.array(c, np.float32) * 0.6
    edge = ((alpha_disc > 0.05) & (alpha_disc < 0.95))[y0:y1, x0:x1]
    vis[edge] = np.array([255, 40, 40], np.float32)
    Image.fromarray(vis.astype(np.uint8)).resize(((x1 - x0) * 3, (y1 - y0) * 3),
                                                 Image.NEAREST).save('/tmp/dbg-occ.png')
    print('occluder coverage inside the disc:')
    tot = inside.sum()
    for n, m in (('case edge', case), ('tonearm tube', tube),
                 ('headshell', head), ('spindle', spindle),
                 ('union+1px', occ & inside)):
        print(f'  {n:14s} {m.sum():6d} px  ({100*m.sum()/tot:4.1f}% of the disc)')
    print('wrote dbg-occ.png  (red = antialiased silhouette edge)')


# ============================================================== decomposition
def blur3(a, k):
    p = np.pad(a, ((k // 2, k // 2), (k // 2, k // 2), (0, 0)), mode='edge')
    o = np.zeros_like(a)
    for dy in range(k):
        for dx in range(k):
            o += p[dy:dy + a.shape[0], dx:dx + a.shape[1]]
    return o / (k * k)


def build():
    clean = inside & ~occ
    base = R.radial_baseline(img, r, clean)

    # --- glare -------------------------------------------------------------
    # Broad, bright departures from the rotationally-symmetric record. Fine
    # angular texture is left in the disc (it should turn with it); only the
    # smooth bright component is lifted out, and never from the label ring,
    # where the painted label sits slightly off the fitted centre and would
    # otherwise read as glare.
    resid = np.clip(img - base, 0, None)
    resid[occ] = 0
    broad = np.clip(blur3(resid, 7) - 6.0, 0, None)

    win = np.clip((r - 0.46) / 0.05, 0, 1) * np.clip((0.998 - r) / 0.02, 0, 1)
    S = broad * win[:, :, None]
    S[occ] = 0
    S[~inside] = 0

    vinyl = np.clip(img - S, 0, 255)
    S = img - vinyl                      # exact by construction after clipping

    # --- reconstruct the disc under the occluders --------------------------
    # A record is rotationally symmetric, so the honest fill for a hidden
    # patch is the same radius at a different angle — grooves and label edges
    # line up by construction, which no generic inpainting would manage.
    tgt = occ & inside
    ty, tx = np.nonzero(tgt)
    rr, tt = r[tgt], th[tgt]
    got = np.zeros(len(ty), bool)
    out = np.zeros((len(ty), 3), np.float32)
    cph, sph = np.cos(phi), np.sin(phi)
    for dd in (35, -35, 70, -70, 105, -105, 140, -140, 175, -175, 210, -210):
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
        x0f = np.clip(np.floor(xs).astype(int), 0, W - 2)
        y0f = np.clip(np.floor(ys).astype(int), 0, H - 2)
        fx = (xs - x0f)[:, None]
        fy = (ys - y0f)[:, None]
        samp = (vinyl[y0f, x0f] * (1 - fx) * (1 - fy) + vinyl[y0f, x0f + 1] * fx * (1 - fy)
                + vinyl[y0f + 1, x0f] * (1 - fx) * fy + vinyl[y0f + 1, x0f + 1] * fx * fy)
        idx = np.nonzero(need)[0][ok]
        out[idx] = samp[ok]
        got[idx] = True
    out[~got] = base[ty, tx][~got]       # fallback: the symmetric record
    vinyl[ty, tx] = out
    print(f'  reconstructed {tgt.sum()} px under the occluders '
          f'({100*(~got).mean():.1f}% fell back to the symmetric record)')

    # --- encode the glare as a light layer ---------------------------------
    # Solve  a*(C - V) = S  for the most transparent exact solution, so the
    # disc still shows through the highlight and can turn under it later.
    Vv = vinyl
    with np.errstate(divide='ignore', invalid='ignore'):
        a_need = np.max(np.where(S > 0, S / np.maximum(255.0 - Vv, 1e-6), 0), axis=2)
    a = np.clip(a_need, 0, 1)
    hasS = (S.max(2) > 0) & ~occ & inside
    a = np.where(hasS, np.maximum(a, 1.0 / 255.0), 0.0)
    C = np.where(a[:, :, None] > 0, Vv + S / np.maximum(a[:, :, None], 1e-6), 0.0)
    C = np.clip(C, 0, 255)

    # --- assemble the two RGBA layers --------------------------------------
    vin = np.zeros((H, W, 4), np.float32)
    vin[:, :, :3] = vinyl
    vin[:, :, 3] = alpha_disc * 255.0

    deck = np.zeros((H, W, 4), np.float32)
    deck[:, :, :3] = np.where(occ[:, :, None], img, C)
    deck[:, :, 3] = np.where(occ, 255.0, a * 255.0)

    # The page draws this artwork at 390x844, so the browser downscales every
    # layer before compositing. Colour from fully transparent pixels still
    # enters that filter, so leaving them black would drag a dark fringe into
    # every soft edge. Bleed the colour that sits underneath into the margin
    # instead — where a layer's RGB matches what is beneath it, the blend
    # returns that colour whatever the alpha resolves to, and the fringe
    # cannot form. Zero only far enough out that the filter never reaches it,
    # which is what keeps the files small.
    for lay in (vin, deck):
        clear = lay[:, :, 3] == 0
        near = dilate(~clear, 8)
        lay[clear & near, :3] = img[clear & near]
        lay[clear & ~near, :3] = 0

    vin8 = np.round(vin).astype(np.uint8)
    deck8 = np.round(deck).astype(np.uint8)
    Image.fromarray(vin8).save('../../assets/vinyl.png', optimize=True)
    Image.fromarray(deck8).save('../../assets/deck-over.png', optimize=True)

    # --- predict the composite ---------------------------------------------
    av = vin8[:, :, 3:4].astype(np.float32) / 255.0
    ad = deck8[:, :, 3:4].astype(np.float32) / 255.0
    comp = img * (1 - av) + vin8[:, :, :3].astype(np.float32) * av
    comp = comp * (1 - ad) + deck8[:, :, :3].astype(np.float32) * ad
    err = np.abs(np.round(comp) - img).max(2)
    box = inside | dilate(inside, 3)
    print(f'  predicted composite error inside the disc: max {err[box].max():.0f}, '
          f'mean {err[box].mean():.3f}, >1 on {int((err[box]>1).sum())} px')
    return vinyl, S, occ


if __name__ == '__main__':
    build()
