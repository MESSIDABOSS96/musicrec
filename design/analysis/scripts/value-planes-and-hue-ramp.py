import numpy as np
from PIL import Image

def lum(a): return (0.2126*a[...,0]+0.7152*a[...,1]+0.0722*a[...,2])/255.0
def hexof(rgb): return '#%02X%02X%02X' % tuple(int(round(c)) for c in rgb)

def hsv(a):
    m=a.astype(np.float32)/255.0; mx=m.max(-1); mn=m.min(-1); d=mx-mn
    h=np.zeros_like(mx); r,g,b=m[...,0],m[...,1],m[...,2]; k=d>1e-6
    i=(mx==r)&k; h[i]=((g-b)[i]/d[i])%6
    i=(mx==g)&k; h[i]=((b-r)[i]/d[i])+2
    i=(mx==b)&k; h[i]=((r-g)[i]/d[i])+4
    return h*60, np.where(mx>0,d/np.maximum(mx,1e-6),0), mx

def autocrop_white(im, thresh=250):
    a=np.asarray(im.convert('RGB')).astype(np.int16)
    nonwhite = (a.min(-1) < thresh)
    ys,xs = np.where(nonwhite)
    return im.crop((xs.min(), ys.min(), xs.max()+1, ys.max()+1))

def region_stats(a, L, S, name, y0,y1,x0,x1):
    H,W = L.shape
    sub = a[int(y0*H):int(y1*H), int(x0*W):int(x1*W)]
    sl  = L[int(y0*H):int(y1*H), int(x0*W):int(x1*W)]
    ss  = S[int(y0*H):int(y1*H), int(x0*W):int(x1*W)]
    p = np.percentile(sl,[2,25,50,75,98])
    print(f'  {name:<26} L med {p[2]:.3f}  range p2-p98 [{p[0]:.2f},{p[4]:.2f}] span {p[4]-p[0]:.2f}  '
          f'IQR {p[3]-p[1]:.2f}  sat {ss.mean():.2f}  avg {hexof(sub.reshape(-1,3).mean(0))}')

def go(path, name, regions, crop=False):
    im = Image.open(path).convert('RGB')
    if crop: im = autocrop_white(im)
    a = np.asarray(im).astype(np.float32); H,W,_ = a.shape
    L = lum(a); Hh,S,V = hsv(a)
    print('='*74); print(f'{name}  cropped size {W}x{H}'); print('='*74)

    bands=[(0,.08),(.08,.18),(.18,.30),(.30,.45),(.45,.62),(.62,.80),(.80,1.01)]
    print('[VALUE BANDS]')
    for lo,hi in bands:
        m=(L>=lo)&(L<hi); pct=100*m.mean()
        if m.sum()>200:
            print(f'   L {lo:.2f}-{hi:.2f}  {pct:5.1f}%  {hexof(a[m].mean(0))}  sat {S[m].mean():.2f}  hue-spread {S[m].std():.2f}')
    print(f'   median L {np.median(L):.3f}   share below 0.15: {100*(L<0.15).mean():.1f}%   share above 0.55: {100*(L>0.55).mean():.1f}%')

    print('\n[DEPTH-PLANE VALUE SEPARATION]')
    for (n,y0,y1,x0,x1) in regions:
        region_stats(a,L,S,n,y0,y1,x0,x1)

    print('\n[HUE RAMP BY VALUE DECILE]')
    order=np.argsort(L.ravel()); flat=a.reshape(-1,3); Lf=L.ravel(); Sf=S.ravel(); Hf=Hh.ravel(); n=len(order)
    for d in range(10):
        sl=order[int(n*d/10):int(n*(d+1)/10)]
        w=Sf[sl]+1e-6; ang=np.deg2rad(Hf[sl])
        mh=np.rad2deg(np.arctan2((np.sin(ang)*w).sum(),(np.cos(ang)*w).sum()))%360
        print(f'   D{d}  L {Lf[sl].mean():.3f}  hue {mh:6.1f}  sat {Sf[sl].mean():.2f}  {hexof(flat[sl].mean(0))}')

    print('\n[LOCAL CONTRAST] top 8 highest-contrast 32px cells (where the eye is pulled)')
    cs=32; hs,ws=H//cs, W//cs
    var=np.zeros((hs,ws))
    for i in range(hs):
        for j in range(ws):
            c=L[i*cs:(i+1)*cs, j*cs:(j+1)*cs]
            var[i,j]=c.max()-c.min()
    idx=np.dstack(np.unravel_index(np.argsort(-var.ravel())[:8],var.shape))[0]
    for i,j in idx:
        print(f'   x={j/ws:.2f} y={i/hs:.2f}  contrast {var[i,j]:.2f}  Lmax {L[i*cs:(i+1)*cs,j*cs:(j+1)*cs].max():.2f}')

    print('\n[SATURATION vs VALUE] (does sat peak in midtones?)')
    for lo,hi in [(0,.1),(.1,.2),(.2,.3),(.3,.4),(.4,.5),(.5,.6),(.6,.7),(.7,.85),(.85,1.01)]:
        m=(L>=lo)&(L<hi)
        if m.sum()>200: print(f'   L {lo:.2f}-{hi:.2f}: sat {S[m].mean():.3f}  n={100*m.mean():5.1f}%')

    print('\n[HUE HISTOGRAM] saturated pixels only (sat>0.35), 12 bins of 30deg')
    m=S>0.35
    hist,_=np.histogram(Hh[m],bins=12,range=(0,360))
    tot=hist.sum()
    for i,c in enumerate(hist):
        bar='#'*int(60*c/max(hist.max(),1))
        print(f'   {i*30:3d}-{(i+1)*30:3d}deg {100*c/tot:5.1f}% {bar}')

A_regions = [
 ('frame:left interior',   0.05,0.95, 0.00,0.09),
 ('frame:right interior',  0.05,0.95, 0.91,1.00),
 ('frame:top lintel',      0.00,0.10, 0.00,1.00),
 ('foreground:table',      0.78,1.00, 0.00,1.00),
 ('aperture:sky upper',    0.13,0.30, 0.30,0.80),
 ('aperture:sun zone',     0.33,0.45, 0.42,0.68),
 ('aperture:left buildings',0.13,0.60, 0.10,0.35),
 ('aperture:street floor', 0.55,0.75, 0.35,0.75),
 ('aperture:right tree',   0.28,0.70, 0.72,0.92),
]
B_regions = [
 ('frame:left jamb',       0.00,1.00, 0.00,0.05),
 ('frame:right jamb',      0.00,1.00, 0.95,1.00),
 ('foreground:table+cups', 0.76,1.00, 0.00,1.00),
 ('midground:buses',       0.47,0.72, 0.03,0.45),
 ('sky upper',             0.02,0.28, 0.10,0.85),
 ('sky at horizon',        0.38,0.48, 0.35,0.85),
 ('sun zone',              0.38,0.47, 0.46,0.66),
 ('sea',                   0.47,0.60, 0.35,0.80),
 ('tree canopy',           0.00,0.30, 0.55,1.00),
 ('street/people',         0.53,0.72, 0.45,0.75),
]

go('/Users/anirudhchatterjee/dev/musicrec/design/inspiration/lofi-window-city-sunset.png','IMAGE A - window/city',A_regions,crop=True)
go('/Users/anirudhchatterjee/dev/musicrec/design/inspiration/lofi-beach-sunset-street.png','IMAGE B - cafe/beach',B_regions,crop=False)
