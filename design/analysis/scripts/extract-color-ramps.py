import numpy as np
from PIL import Image
def lum(a): return (0.2126*a[...,0]+0.7152*a[...,1]+0.0722*a[...,2])/255.0
def hexof(c): return '#%02X%02X%02X'%tuple(int(round(x)) for x in c)
def autocrop(im,t=250):
    a=np.asarray(im.convert('RGB')).astype(np.int16); nw=(a.min(-1)<t)
    ys,xs=np.where(nw); return im.crop((xs.min(),ys.min(),xs.max()+1,ys.max()+1))
def hsv(a):
    m=a/255.0; mx=m.max(-1); mn=m.min(-1); d=mx-mn
    h=np.zeros_like(mx); r,g,b=m[...,0],m[...,1],m[...,2]; k=d>1e-6
    i=(mx==r)&k; h[i]=((g-b)[i]/d[i])%6
    i=(mx==g)&k; h[i]=((b-r)[i]/d[i])+2
    i=(mx==b)&k; h[i]=((r-g)[i]/d[i])+4
    return h*60, np.where(mx>0,d/np.maximum(mx,1e-6),0)

for path,name,crop in [('lofi-window-city-sunset.png','IMAGE A',True),('lofi-beach-sunset-street.png','IMAGE B',False)]:
    im=Image.open('/Users/anirudhchatterjee/dev/musicrec/design/inspiration/'+path).convert('RGB')
    if crop: im=autocrop(im)
    a=np.asarray(im).astype(np.float32); L=lum(a); Hh,S=hsv(a)
    print('='*60); print(name+' — WARM RAMP (dominant wedge only), by value shelf'); print('='*60)
    if name=='IMAGE A': warm=(Hh>=5)&(Hh<=60)
    else: warm=((Hh>=330)|(Hh<=35))
    for lo,hi in [(0.0,.05),(.05,.09),(.09,.14),(.14,.20),(.20,.28),(.28,.38),(.38,.50),(.50,.62),(.62,.78),(.78,1.01)]:
        m=warm&(L>=lo)&(L<hi)
        if m.sum()>400:
            c=a[m].reshape(-1,3).mean(0)
            print(f'  L {lo:.2f}-{hi:.2f}  {hexof(c)}  hue {np.median(Hh[m]):5.1f}  sat {S[m].mean():.2f}  area {100*m.mean():4.1f}%')
    print('  COOL COUNTERPOINT by value shelf')
    if name=='IMAGE A': cool=(Hh>=140)&(Hh<=215)
    else: cool=(Hh>=195)&(Hh<=255)
    for lo,hi in [(0.0,.09),(.09,.16),(.16,.24),(.24,.34),(.34,.50)]:
        m=cool&(L>=lo)&(L<hi)
        if m.sum()>400:
            c=a[m].reshape(-1,3).mean(0)
            print(f'  L {lo:.2f}-{hi:.2f}  {hexof(c)}  hue {np.median(Hh[m]):5.1f}  sat {S[m].mean():.2f}  area {100*m.mean():4.1f}%')
    print(f'  warm total {100*warm.mean():.1f}%   cool total {100*cool.mean():.1f}%')
