"""Shared record-space geometry for the vinyl split."""
import numpy as np
from PIL import Image

SX, SY = 853 / 390.0, 1844 / 844.0


def load(path='../../assets/room2.png'):
    return np.asarray(Image.open(path).convert('RGB')).astype(np.float32)


def geometry(shape, ellipse):
    """
    Map every pixel into the record's own frame.

    r is the distance from the spindle as a fraction of the record radius, so
    r == 1 is the rim. th is the angle around the disc. Rotating the record is
    a shift in th, which is why everything below is expressed in these terms.
    """
    cx, cy, A, B, phi = ellipse
    H, W = shape[:2]
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    dx, dy = xx - cx, yy - cy
    c, s = np.cos(-phi), np.sin(-phi)
    u = dx * c - dy * s
    v = dx * s + dy * c
    U, V = u / A, v / B
    r = np.hypot(U, V)
    th = np.arctan2(V, U)
    # |grad r| in image pixels, for sub-pixel antialiasing of the rim
    with np.errstate(invalid='ignore', divide='ignore'):
        gu, gv = U / np.maximum(r, 1e-9), V / np.maximum(r, 1e-9)
        gx = (gu / A) * c + (gv / B) * s
        gy = -(gu / A) * s + (gv / B) * c
        grad = np.hypot(gx, gy)
    return r, th, np.maximum(grad, 1e-9)


def radial_baseline(img, r, mask, nbins=260, rmax=1.06):
    """
    The record as if it were perfectly rotationally symmetric: for each radius,
    the median colour around the disc. Grooves and the label are concentric so
    they survive this; the tonearm and the lamp reflections do not, because
    they occupy only part of the circle at any radius.
    """
    edges = np.linspace(0, rmax, nbins + 1)
    idx = np.clip(np.digitize(r, edges) - 1, 0, nbins - 1)
    base = np.zeros((nbins, 3), np.float32)
    have = np.zeros(nbins, bool)
    for b in range(nbins):
        m = mask & (idx == b)
        if m.sum() >= 8:
            base[b] = np.median(img[m], axis=0)
            have[b] = True
    # Interpolate across radii that had no clean samples. The innermost bins
    # are entirely under the spindle, so they have none at all — carrying the
    # previous bin forward would leave them at zero and punch a black hole
    # through the middle of the label.
    src = np.nonzero(have)[0]
    for ch in range(3):
        base[:, ch] = np.interp(np.arange(nbins), src, base[src, ch])
    # light smoothing along radius so bin noise does not print as rings
    k = 3
    pad = np.pad(base, ((k // 2, k // 2), (0, 0)), mode='edge')
    sm = sum(pad[i:i + nbins] for i in range(k)) / k
    return sm[idx]
