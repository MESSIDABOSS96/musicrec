import numpy as np
from PIL import Image

def lum(a): return (0.2126*a[...,0]+0.7152*a[...,1]+0.0722*a[...,2])/255.0
def hexof(rgb): return '#%02X%02X%02X' % tuple(int(round(c)) for c in rgb)
def autocrop_white(im, thresh=250):
    a=np.asarray(im.convert('RGB')).astype(np.int16); nw=(a.min(-1)<thresh)
    ys,xs=np.where(nw); return im.crop((xs.min(),ys.min(),xs.max()+1,ys.max()+1))

def go(path,name,crop):
    im=Image.open(path).convert('RGB')
    if crop: im=autocrop_white(im)
    a=np.asarray(im).astype(np.float32); H,W,_=a.shape; L=lum(a)
    print('='*74); print(name); print('='*74)

    # --- find emissive cores: bright, isolated, small ---
    print('[EMISSIVE SOURCES] local maxima of L, min separation 6% of frame')
    ds=8
    Ls=np.array(Image.fromarray(np.uint8(L*255)).resize((W//ds,H//ds),Image.BOX)).astype(np.float32)/255
    cand=[]
    hs,ws=Ls.shape
    sep=int(0.06*max(hs,ws))
    tmp=Ls.copy()
    for _ in range(8):
        i,j=np.unravel_index(np.argmax(tmp),tmp.shape)
        if tmp[i,j]<0.55: break
        cand.append((i,j,tmp[i,j]))
        y0,y1=max(0,i-sep),min(hs,i+sep); x0,x1=max(0,j-sep),min(ws,j+sep)
        tmp[y0:y1,x0:x1]=0
    for i,j,v in cand:
        cy,cx=int(i*ds+ds/2), int(j*ds+ds/2)
        core=a[max(0,cy-4):cy+4, max(0,cx-4):cx+4].reshape(-1,3).mean(0)
        print(f'   x={j/ws:.2f} y={i/hs:.2f}  L={v:.2f}  core {hexof(core)}   halo:', end=' ')
        yy,xx=np.ogrid[:H,:W]; d2=(yy-cy)**2+(xx-cx)**2
        prev=None
        for r in [0.008,0.02,0.04,0.07,0.11,0.16]:
            rr=r*max(W,H); ring=(d2>(rr*0.75)**2)&(d2<=(rr*1.25)**2)
            if ring.sum()>80:
                c=a[ring].reshape(-1,3).mean(0)
                print(f'r{r:.3f}:L{L[ring].mean():.2f} {hexof(c)}', end='  ')
        print()

    # --- grain / high-frequency noise in flat regions ---
    print('\n[TEXTURE] high-frequency residual (grain) in the flattest 20% of the image')
    k=np.array([[1,1,1],[1,-8,1],[1,1,1]],dtype=np.float32)
    from numpy.lib.stride_tricks import sliding_window_view
    win=sliding_window_view(L,(3,3))
    hp=np.abs((win*k).sum((-1,-2)))
    # flat = low local range
    rng=win.max((-1,-2))-win.min((-1,-2))
    flat=rng<np.percentile(rng,20)
    print(f'   mean |laplacian| overall  {hp.mean():.4f}')
    print(f'   mean |laplacian| in flat  {hp[flat].mean():.4f}   (>0.004 implies visible grain/dither)')
    print(f'   std of L within flat areas {L[:-2,:-2][flat].std():.4f}')

    # --- outline / ink detection ---
    print('\n[OUTLINE TEST] is there a dark line separating shapes?')
    dark=L<0.10
    win2=sliding_window_view(L,(9,9))
    localmax=win2.max((-1,-2))
    dk=dark[:-8,:-8]
    contour=dk&(localmax>0.30)
    print(f'   dark(L<0.10) pixels: {100*dark.mean():.1f}% of frame')
    print(f'   of those, share within 4px of something L>0.30: {100*contour.sum()/max(dk.sum(),1):.1f}%')
    print('   (>35% => real ink outlines; <20% => shapes separated by value mass, not line)')

    # --- horizon / focal band ---
    print('\n[ROW LUMINANCE PROFILE] mean L per 4% of height (finds the bright band)')
    for f in np.arange(0,1.0,0.04):
        row=L[int(f*H):int((f+0.04)*H)]
        bar='#'*int(row.mean()*70)
        print(f'   y {f:.2f} {row.mean():.3f} {bar}')

    # --- column profile ---
    print('\n[COLUMN LUMINANCE PROFILE] mean L per 5% of width')
    for f in np.arange(0,1.0,0.05):
        col=L[:,int(f*W):int((f+0.05)*W)]
        bar='#'*int(col.mean()*70)
        print(f'   x {f:.2f} {col.mean():.3f} {bar}')

go('/Users/anirudhchatterjee/dev/musicrec/design/inspiration/lofi-window-city-sunset.png','IMAGE A - window/city',True)
go('/Users/anirudhchatterjee/dev/musicrec/design/inspiration/lofi-beach-sunset-street.png','IMAGE B - cafe/beach',False)
