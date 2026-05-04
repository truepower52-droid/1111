"""
DMSh Promo Video v3 — light white/blue/purple theme
1920×1080 · 30 fps · 15 s · MP4

Changes from v2:
- White background, deep blue + purple palette
- No $ signs in terminals (use > prompt)
- All blocks centered
- Improved typography (Regular weight for body, wider line-height)
- Logo integrated (generated from brand elements)
- Shadow text instead of glow (readable on light bg)
"""
import math, random
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from moviepy import VideoClip

# ─────────────────────────────────────────────
W, H   = 1920, 1080
FPS    = 30
DUR    = 15
FRAMES = FPS * DUR          # 450

# ─────────────────────────────────────────────
# PALETTE  — light theme

BG_WHITE  = (255, 255, 255)
BG_SOFT   = (248, 246, 255)   # off-white w/ purple tint
BG_PALE   = (237, 233, 255)   # pale purple panels

DEEP_BLUE = ( 27,  20, 100)   # #1B1464  headings / strong text
NAVY      = ( 40,  32, 140)   # #2820 8C  secondary dark

PURPLE    = (107,  82, 221)   # #6B52DD  primary brand purple
PURPLE_D  = ( 64,  48, 160)   # #4030A0  deeper purple
PURPLE_L  = (176, 160, 232)   # #B0A0E8  soft purple
PURPLE_XL = (220, 212, 250)   # #DCD4FA  very light purple

TEXT_BODY = ( 70,  60, 130)   # body text on white
TEXT_SOFT = (140, 128, 190)   # secondary text

# Terminal stays dark (contrast on white page)
TERM_BG   = ( 12,  10,  35)
T_GRN     = ( 80, 220, 120)   # terminal green
T_CYN     = ( 70, 195, 240)   # terminal cyan
T_GLD     = (240, 190,  60)   # terminal gold
T_PNK     = (240, 100, 200)   # terminal pink
T_LAV     = (170, 150, 255)   # terminal lavender

DOT_R     = (255,  95,  86)
DOT_Y     = (255, 189,  46)
DOT_G     = ( 39, 201,  63)
WHITE     = (255, 255, 255)

# Browser chrome colours
BRWS_TOP  = (240, 238, 250)
BRWS_URL  = (220, 216, 244)

# ─────────────────────────────────────────────
# FONTS

_FC = {}
def F(size, v="sb"):
    if (size, v) not in _FC:
        paths = {
            "sb": "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "sr": "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "mb": "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf",
            "mr": "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
        }
        _FC[(size,v)] = ImageFont.truetype(paths[v], size)
    return _FC[(size,v)]

# ─────────────────────────────────────────────
# EASING / MATH

def clamp(v, lo=0.0, hi=1.0): return max(lo, min(hi, v))
def remap(v, a, b, c=0.0, d=1.0):
    t = clamp((v-a)/(b-a) if b!=a else 0.0)
    return c+(d-c)*t
def lerp_c(a, b, t):
    return tuple(int(a[i]+(b[i]-a[i])*clamp(t)) for i in range(len(a)))
def eout3(t): t=clamp(t); return 1-(1-t)**3
def eout5(t): t=clamp(t); return 1-(1-t)**5
def ein_out(t): t=clamp(t); return t*t*(3-2*t)
def spring(t, stiff=200, damp=18):
    t=clamp(t)
    if t<=0: return 0.0
    if t>=1: return 1.0
    w0=math.sqrt(stiff); z=damp/(2*math.sqrt(stiff))
    wd=w0*math.sqrt(max(0,1-z*z)); rt=t*1.1
    return 1-math.exp(-z*w0*rt)*(math.cos(wd*rt)+(z*w0/max(wd,1e-9))*math.sin(wd*rt))
def prog(f, f0, f1, ease=eout3): return ease(remap(f,f0,f1))

# ─────────────────────────────────────────────
# BACKGROUNDS

def bg_white_grad(accent=0.0):
    """White → very-pale-purple gradient, top→bottom."""
    arr = np.ones((H,W,3),dtype=np.float32)*255
    ys  = np.linspace(0,1,H)[:,np.newaxis,np.newaxis]
    tint= np.array(BG_PALE,dtype=np.float32)
    arr = arr*(1-ys*0.35*accent) + tint*(ys*0.35*accent)
    return arr.clip(0,255).astype(np.uint8)

def bg_soft_grid(img, alpha=0.06):
    d = ImageDraw.Draw(img,"RGBA")
    a = int(255*alpha)
    for x in range(0,W,96):  d.line([(x,0),(x,H)],fill=(*PURPLE_L,a))
    for y in range(0,H,96):  d.line([(0,y),(W,y)],fill=(*PURPLE_L,a))

# ─────────────────────────────────────────────
# PARTICLES

class Particles:
    def __init__(self, n=55, seed=13):
        rng=random.Random(seed)
        self.ps=[{
            'x0':rng.random()*W,'y0':rng.random()*H,
            'vx':(rng.random()-.5)*.5,'vy':-(rng.random()*1.0+.2),
            'r':rng.random()*3+1,
            'a':rng.random()*.25+.08,
            'c':rng.choice([PURPLE_L,PURPLE,PURPLE_XL]),
        } for _ in range(n)]
    def draw(self, img, frame, alpha=1.0):
        d=ImageDraw.Draw(img,"RGBA")
        for p in self.ps:
            x=(p['x0']+p['vx']*frame)%W
            y=(p['y0']+p['vy']*frame)%H
            a=int(p['a']*alpha*255)
            d.ellipse([x-p['r'],y-p['r'],x+p['r'],y+p['r']],fill=(*p['c'],a))

_PARTS=Particles()

# ─────────────────────────────────────────────
# LOGO  (programmatic — медицинский крест + "БВ")

def make_logo(size=300):
    img=Image.new("RGBA",(size,size),(0,0,0,0))
    d=ImageDraw.Draw(img,"RGBA")

    # icon area: left 42% of total width
    iw=int(size*0.42)
    icx,icy=iw//2, size//2

    # soft halo circle behind
    hr=int(iw*0.68)
    d.ellipse([icx-hr,icy-hr,icx+hr,icy+hr],fill=(*PURPLE_L,220))

    # second lighter circle (overlap, slightly offset right+down)
    hr2=int(iw*0.58)
    d.ellipse([icx+int(iw*.18)-hr2,icy+int(iw*.12)-hr2,
               icx+int(iw*.18)+hr2,icy+int(iw*.12)+hr2],
              fill=(*PURPLE_XL,160))

    # medical cross
    aw=int(iw*0.28)    # arm width
    al=int(iw*0.85)    # arm length
    # vertical
    d.rectangle([icx-aw//2,icy-al//2,icx+aw//2,icy+al//2],fill=(*PURPLE,255))
    # horizontal
    d.rectangle([icx-al//2,icy-aw//2,icx+al//2,icy+aw//2],fill=(*PURPLE,255))

    # "БВ" text
    ts=int(size*0.44)
    d.text((iw+int(size*0.03), size//2-ts//2-int(size*.02)),
           "БВ", font=F(ts,"sb"), fill=(*DEEP_BLUE,255))
    return img

_LOGO_CACHE={}
def get_logo(size):
    if size not in _LOGO_CACHE:
        _LOGO_CACHE[size]=make_logo(size)
    return _LOGO_CACHE[size]

def paste_logo(img, cx, cy, size, alpha=1.0):
    """Paste logo centered at (cx,cy)."""
    logo=get_logo(size).copy()
    if alpha<1.0:
        arr=np.array(logo,dtype=np.float32)
        arr[:,:,3]*=alpha
        logo=Image.fromarray(arr.clip(0,255).astype(np.uint8),"RGBA")
    x,y=cx-size//2, cy-size//2
    img.paste(logo,(x,y),logo)

# ─────────────────────────────────────────────
# TEXT HELPERS

def tw(d,t,sz,v="sb"):
    b=d.textbbox((0,0),t,font=F(sz,v)); return b[2]-b[0]
def th(d,t,sz,v="sb"):
    b=d.textbbox((0,0),t,font=F(sz,v)); return b[3]-b[1]

def text_c(d, text, cy, sz, col=DEEP_BLUE, v="sb", alpha=255):
    """Draw text horizontally centred at vertical position cy."""
    w_=tw(d,text,sz,v); h_=th(d,text,sz,v)
    x=(W-w_)//2; y=cy-h_//2
    d.text((x,y),text,font=F(sz,v),fill=(*col,alpha))

def text_at(d, text, x, y, sz, col=DEEP_BLUE, v="sb", alpha=255):
    d.text((x,y),text,font=F(sz,v),fill=(*col,alpha))

def shadow_text(d, text, x, y, sz, col, v="sb", alpha=255, sh=3):
    """Subtle drop-shadow text — readable on light bg."""
    d.text((x+sh,y+sh),text,font=F(sz,v),fill=(20,15,80,int(40*alpha/255)))
    d.text((x,y),text,font=F(sz,v),fill=(*col,alpha))

def typewriter(text, t):
    return text[:max(0,int(len(text)*clamp(t)))]

# ─────────────────────────────────────────────
# TERMINAL WINDOW  (dark, centred by caller)

def draw_terminal(img, x, y, w, h, title, lines, frame=0):
    """
    lines: list of dict(text, color, t)  — t<1 → typewriter active
    All $ stripped, replaced with >
    """
    d=ImageDraw.Draw(img,"RGBA")
    r=14

    # shadow
    for s in range(22,0,-3):
        a=int(140*(1-s/22)*0.18)
        d.rounded_rectangle([x+s,y+s,x+w+s,y+h+s],radius=r+2,fill=(0,0,0,a))

    # title bar
    d.rounded_rectangle([x,y,x+w,y+40],radius=r,fill=(32,30,55,255))
    d.rectangle([x,y+22,x+w,y+40],fill=(32,30,55,255))

    # body
    d.rectangle([x,y+40,x+w,y+h],fill=(*TERM_BG,252))
    d.rounded_rectangle([x,y+h-r*2,x+w,y+h],radius=r,fill=(*TERM_BG,252))

    # subtle purple border
    d.rounded_rectangle([x,y,x+w,y+h],radius=r,outline=(*PURPLE_L,50),width=1)

    # traffic dots
    for i,dc in enumerate([DOT_R,DOT_Y,DOT_G]):
        cx_=x+16+i*22; cy_=y+20
        d.ellipse([cx_-7,cy_-7,cx_+7,cy_+7],fill=(*dc,255))

    # title
    tw_=tw(d,title,15,"mr")
    d.text((x+w//2-tw_//2,y+12),title,font=F(15,"mr"),fill=(160,155,210,255))

    # scanlines
    for sy in range(y+42,y+h,4):
        d.line([(x+1,sy),(x+w-1,sy)],fill=(0,0,0,10))

    # text lines
    lh=32; py=y+56
    for ln in lines:
        if py>y+h-18: break
        shown=typewriter(ln["text"],ln["t"])
        if ln["t"]<1.0 and (frame//10)%2==0:
            shown+="█"
        d.text((x+20,py),shown,font=F(20,"mr"),fill=(*ln["color"],235))
        py+=lh

# ─────────────────────────────────────────────
# BROWSER WINDOW

def draw_browser(img, x, y, w, h, url, content_fn):
    d=ImageDraw.Draw(img,"RGBA")
    r=14

    # shadow
    for s in range(22,0,-3):
        a=int(120*(1-s/22)*0.15)
        d.rounded_rectangle([x+s,y+s,x+w+s,y+h+s],radius=r+2,fill=(60,50,160,a))

    # chrome
    d.rounded_rectangle([x,y,x+w,y+50],radius=r,fill=(*BRWS_TOP,255))
    d.rectangle([x,y+28,x+w,y+50],fill=(*BRWS_TOP,255))

    # content
    d.rectangle([x,y+50,x+w,y+h],fill=(*BG_WHITE,255))
    d.rounded_rectangle([x,y+h-r*2,x+w,y+h],radius=r,fill=(*BG_WHITE,255))

    # border
    d.rounded_rectangle([x,y,x+w,y+h],radius=r,outline=(*PURPLE_L,120),width=1)

    # dots
    for i,dc in enumerate([DOT_R,DOT_Y,DOT_G]):
        cx_=x+16+i*22; cy_=y+25
        d.ellipse([cx_-7,cy_-7,cx_+7,cy_+7],fill=(*dc,255))

    # URL bar
    ux,uy=x+100,y+9; uw_=int(w*0.54)
    d.rounded_rectangle([ux,uy,ux+uw_,uy+30],radius=14,fill=(*BRWS_URL,255))
    lock="[https]  "+url
    d.text((ux+12,uy+7),lock,font=F(14,"sr"),fill=(*TEXT_BODY,200))

    # purple top-border accent inside content
    d.rectangle([x,y+50,x+w,y+54],fill=(*PURPLE,220))

    content_fn(img,x,y+54,w,h-54)

# ─────────────────────────────────────────────
# CARD   (light glassmorphism on white bg)

def light_card(img, x, y, w, h, accent=PURPLE, alpha_t=1.0, radius=18):
    d=ImageDraw.Draw(img,"RGBA")
    # fill
    d.rounded_rectangle([x,y,x+w,y+h],radius=radius,
                         fill=(*BG_WHITE,int(240*alpha_t)))
    # border
    d.rounded_rectangle([x,y,x+w,y+h],radius=radius,
                         outline=(*accent,int(160*alpha_t)),width=2)
    # left accent stripe
    d.rounded_rectangle([x,y+14,x+5,y+h-14],radius=3,
                         fill=(*accent,int(255*alpha_t)))

# ─────────────────────────────────────────────
# TRANSITION: clean fade + slight scale

def fade_blend(a_arr, b_arr, t):
    t=ein_out(clamp(t))
    return (a_arr*(1-t)+b_arr*t).astype(np.uint8)

# ─────────────────────────────────────────────
# TERMINAL LINE BUILDER  (no $ signs)

def build_lines(spec, t_global, n_lines, f_start, f_end, frame):
    """Animate N lines appearing sequentially."""
    content_t = remap(frame, f_start, f_end)
    visible   = max(1, int(content_t * len(spec)))
    out       = []
    for i, ln in enumerate(spec[:visible]):
        if i < visible-1:
            out.append({"text":ln[0],"color":ln[1],"t":1.0})
        else:
            lstart = i/len(spec); lend=(i+1)/len(spec)
            lt=remap(content_t,lstart,lend)*2.2
            out.append({"text":ln[0],"color":ln[1],"t":clamp(lt)})
    return out

# ─────────────────────────────────────────────
# ─────────────────────────────────────────────
# SCENE 1  f=0..75   LOGO + TITLE
# ─────────────────────────────────────────────

def scene1(f):
    t=remap(f,0,75)
    arr=bg_white_grad(accent=min(1.0,t*1.5))
    img=Image.fromarray(arr).convert("RGBA")
    bg_soft_grid(img,0.04)
    _PARTS.draw(img,f,alpha=clamp(t*2)*0.18)

    d=ImageDraw.Draw(img,"RGBA")

    # ── Logo springs in ──
    logo_s=spring(remap(f,2,38))
    logo_sz=int(320*logo_s)
    if logo_sz>10:
        paste_logo(img,W//2,H//2-60,logo_sz,alpha=clamp(logo_s))

    # ── Title below logo ──
    title="Дистанционная медицинская школа"
    ta=int(255*clamp(remap(f,30,52)))
    ty_off=int((1-eout3(remap(f,30,52)))*40)
    if ta:
        shadow_text(d,title,(W-tw(d,title,46,"sb"))//2,
                    H//2+130+ty_off,46,DEEP_BLUE,"sb",ta)

    # ── Subtitle ──
    sub="Цифровая платформа «Будущий врач»"
    sa=int(255*clamp(remap(f,40,60)))
    if sa:
        text_c(d,sub,H//2+196,28,TEXT_BODY,"sr",sa)

    # ── Badge ──
    ba=int(255*clamp(remap(f,50,68)))
    if ba:
        badge="При поддержке Минздрава России"
        bw=tw(d,badge,20,"sr")+40
        bx=(W-bw)//2; by=H//2+240
        d.rounded_rectangle([bx,by,bx+bw,by+38],radius=19,
                             fill=(*PURPLE_XL,int(200*ba/255)))
        d.rounded_rectangle([bx,by,bx+bw,by+38],radius=19,
                             outline=(*PURPLE_L,int(160*ba/255)),width=1)
        text_c(d,badge,by+19,20,PURPLE,"sr",ba)

    return np.array(img.convert("RGB"))

# ─────────────────────────────────────────────
# SCENE 2  f=75..195   SPLIT: BROWSER LEFT / TERMINAL RIGHT
# ─────────────────────────────────────────────

STATS_SPEC=[
    ("# Статистика платформы",              T_LAV),
    ("",                                    WHITE),
    ("> users    = 20_000  # пользователей",T_GRN),
    ("> partners =    100  # партнёров",    T_CYN),
    ("> content  =    370  # единиц",       T_GLD),
    ("> specs    =     30  # специальностей",T_PNK),
    ("",                                    WHITE),
    ("> platform.status = 'ACTIVE'",        T_GRN),
]

def scene2(f):
    t=remap(f,75,195)
    arr=bg_white_grad(accent=0.6)
    img=Image.fromarray(arr).convert("RGBA")
    bg_soft_grid(img,0.045)
    _PARTS.draw(img,f,0.15)

    d=ImageDraw.Draw(img,"RGBA")

    # Subtle divider
    div_a=int(50*clamp(remap(f,80,100)))
    if div_a:
        d.line([(W//2,80),(W//2,H-80)],fill=(*PURPLE_L,div_a),width=1)

    # ── LEFT: browser ──
    BW,BH=860,560
    bs=spring(remap(f,75,122))
    bx=int(40+(bs-1)*(BW+60))
    by=H//2-BH//2

    def bcontent(img_,cx,cy,cw,ch):
        d2=ImageDraw.Draw(img_,"RGBA")
        pad=44

        # mini logo
        lsa=int(255*clamp(remap(f,118,135)))
        if lsa:
            paste_logo(img_,cx+pad+55,cy+52,110,alpha=lsa/255)

        # heading
        ta=int(255*clamp(remap(f,120,142)))
        if ta:
            shadow_text(d2,"Дистанционная",cx+pad+130,cy+14,
                        24,DEEP_BLUE,"sb",ta)
            shadow_text(d2,"медицинская школа",cx+pad+130,cy+46,
                        24,DEEP_BLUE,"sb",ta)

        sa=int(255*clamp(remap(f,130,150)))
        if sa:
            d2.text((cx+pad+130,cy+84),"Платформа «Будущий врач»",
                    font=F(17,"sr"),fill=(*TEXT_BODY,sa))

        ba=int(255*clamp(remap(f,140,158)))
        if ba:
            badge="Минздрав России"
            bw2=tw(d2,badge,15,"sr")+26
            d2.rounded_rectangle([cx+pad+130,cy+112,
                                   cx+pad+130+bw2,cy+138],
                                  radius=11,fill=(*PURPLE_XL,int(220*ba/255)))
            d2.text((cx+pad+143,cy+117),badge,
                    font=F(15,"sr"),fill=(*PURPLE,ba))

        feats=["Олимпиадный тренажёр",
               "Медицинский Атлас",
               "Первая помощь + сертификат",
               "Подготовка к ЕГЭ"]
        for i,feat in enumerate(feats):
            fa=int(255*clamp(remap(f,148+i*10,170+i*10)))
            if fa:
                fy=cy+160+i*52
                d2.ellipse([cx+pad,fy+10,cx+pad+10,fy+20],
                           fill=(*PURPLE,fa))
                d2.text((cx+pad+20,fy),feat,
                        font=F(21,"sr"),fill=(*TEXT_BODY,fa))

    if bs>0.02:
        draw_browser(img,bx,by,BW,BH,"futuredoc.minzdrav.gov.ru",bcontent)

    # ── RIGHT: terminal, centred in right half ──
    TW2,TH2=820,390
    tx2=W//2+30+(W//2-TW2)//2    # horizontally centred in right half
    ts2=spring(remap(f,82,130))
    tx2_anim=int(tx2+(1-ts2)*(TW2+100))
    ty2=H//2-TH2//2

    if ts2>0.02:
        lines2=build_lines(STATS_SPEC,t,len(STATS_SPEC),122,192,f)
        tmp2=Image.new("RGBA",(TW2,TH2),(0,0,0,0))
        draw_terminal(tmp2,0,0,TW2,TH2,"stats.py — python3",lines2,frame=f)
        img.paste(tmp2,(tx2_anim,ty2),tmp2)

    return np.array(img.convert("RGB"))

# ─────────────────────────────────────────────
# SCENE 3  f=195..285   METRICS
# ─────────────────────────────────────────────

METRICS=[
    (20000,"+","пользователей",  PURPLE),
    (  100,"+","партнёров",      DEEP_BLUE),
    (  370,"+","единиц контента",PURPLE_D),
    (   30,"+","специальностей", NAVY),
]

def count_str(target,t):
    v=int(eout3(clamp(t))*target)
    return f"{v:,}".replace(","," ")

def scene3(f):
    arr=bg_white_grad(accent=0.8)
    img=Image.fromarray(arr).convert("RGBA")
    bg_soft_grid(img,0.05)
    _PARTS.draw(img,f,0.15)

    d=ImageDraw.Draw(img,"RGBA")

    # header, centred
    ha=int(255*clamp(remap(f,196,218)))
    if ha:
        title="Платформа «Будущий врач» в цифрах"
        shadow_text(d,title,(W-tw(d,title,46,"sb"))//2,
                    78,46,DEEP_BLUE,"sb",ha)
        uw=tw(d,title,46,"sb")
        d.rectangle([(W-uw)//2,132,(W+uw)//2,136],fill=(*PURPLE,ha))

    # 4 cards centred
    CW,CH=370,268; gap=34
    total=(len(METRICS)*CW+(len(METRICS)-1)*gap)
    sx=(W-total)//2; sy=182

    for i,(target,suf,label,col) in enumerate(METRICS):
        ct=spring(remap(f,197+i*14,244+i*14))
        if ct<=0: continue
        cx=sx+i*(CW+gap)

        # card shadow
        for g in range(20,0,-4):
            a=int(18*(1-g/20)*ct)
            d.rounded_rectangle([cx+g//2,sy+g//2,cx+CW+g//2,sy+CH+g//2],
                                  radius=20,fill=(*col,a))

        light_card(img,cx,sy,CW,CH,col,ct)
        d2=ImageDraw.Draw(img,"RGBA")

        # big number
        nt=remap(f,207+i*12,262+i*12)
        num=count_str(target,nt)
        if nt>=1.0: num=f"{target:,}".replace(","," ")+suf
        nw=tw(d2,num,72,"sb")
        shadow_text(d2,num,cx+(CW-nw)//2,sy+24,72,col,"sb",int(255*ct),sh=2)

        # label, centred in card
        lw=tw(d2,label,22,"sr")
        d2.text((cx+(CW-lw)//2,sy+116),label,
                font=F(22,"sr"),fill=(*TEXT_BODY,int(220*ct)))

        # progress bar
        bt=clamp(remap(f,222+i*10,270+i*10))
        bw_f=CW-48; bar_y=sy+CH-48
        d2.rounded_rectangle([cx+24,bar_y,cx+24+bw_f,bar_y+8],
                               radius=4,fill=(*PURPLE_XL,200))
        if bt>0:
            d2.rounded_rectangle([cx+24,bar_y,cx+24+int(bw_f*bt),bar_y+8],
                                   radius=4,fill=(*col,int(255*ct)))

    # tagline
    tg_a=int(255*clamp(remap(f,266,282)))
    if tg_a:
        text_c(d,"От 5 класса до поступления в медицинский вуз",
               sy+CH+64,26,TEXT_SOFT,"sr",tg_a)

    return np.array(img.convert("RGB"))

# ─────────────────────────────────────────────
# SCENE 4  f=285..375   FEATURES
# ─────────────────────────────────────────────

FEATURES=[
    (PURPLE,   "[1]","Олимпиадный тренажёр",  "Задачи прошлых лет с разборами"),
    (DEEP_BLUE,"[2]","Первая помощь",          "Видеокурс + сертификат"),
    (PURPLE_D, "[3]","Медицинский Атлас",      "Интерактивные изображения"),
    (NAVY,     "[4]","Подготовка к ЕГЭ",       "Биология, химия, анатомия"),
    (PURPLE,   "[5]","Профориентация",         "Энциклопедия специальностей"),
    (DEEP_BLUE,"[6]","Сертификаты",            "Доп. баллы при поступлении"),
]
DIRS=[(-1,0),(0,-1),(1,0),(-1,0),(0,1),(1,0)]

def scene4(f):
    arr=bg_white_grad(accent=0.7)
    img=Image.fromarray(arr).convert("RGBA")
    bg_soft_grid(img,0.045)
    _PARTS.draw(img,f,0.13)

    d=ImageDraw.Draw(img,"RGBA")

    ha=int(255*clamp(remap(f,286,305)))
    if ha:
        title="Что входит в ДМШ?"
        shadow_text(d,title,(W-tw(d,title,50,"sb"))//2,
                    62,50,DEEP_BLUE,"sb",ha)
        uw=tw(d,title,50,"sb")
        d.rectangle([(W-uw)//2,116,(W+uw)//2,120],fill=(*PURPLE,ha))

    COLS=3; CW,CH=500,178; hg=36; vg=28
    total_w=COLS*CW+(COLS-1)*hg
    fx=(W-total_w)//2; fy=148

    for i,(col,badge,title_,sub) in enumerate(FEATURES):
        c=i%COLS; r=i//COLS
        df=285+c*12+r*22
        ct=spring(remap(f,df,df+55))
        if ct<=0: continue

        dx,dy=DIRS[i]
        bx=fx+c*(CW+hg); by=fy+r*(CH+vg)
        off=int((1-ct)*130)
        cx_=bx+dx*off; cy_=by+dy*off
        ai=int(255*clamp(ct))

        # card shadow
        for g in range(16,0,-4):
            a=int(14*(1-g/16)*ct)
            d.rounded_rectangle([cx_+g//2,cy_+g//2,
                                  cx_+CW+g//2,cy_+CH+g//2],
                                  radius=18,fill=(*col,a))

        light_card(img,cx_,cy_,CW,CH,col,ct)
        d2=ImageDraw.Draw(img,"RGBA")

        # badge tag
        bw2=tw(d2,badge,18,"mb")+18
        d2.rounded_rectangle([cx_+16,cy_+16,cx_+16+bw2,cy_+40],
                               radius=8,fill=(*col,int(200*ct)))
        d2.text((cx_+25,cy_+19),badge,font=F(18,"mb"),fill=(*WHITE,ai))

        # title
        shadow_text(d2,title_,cx_+16,cy_+52,26,col,"sb",ai,sh=1)
        # sub
        d2.text((cx_+16,cy_+90),sub,font=F(19,"sr"),fill=(*TEXT_BODY,int(200*ct)))

    return np.array(img.convert("RGB"))

# ─────────────────────────────────────────────
# SCENE 5  f=375..450   CTA
# ─────────────────────────────────────────────

CTA_TERM=[
    ("# Подключение школы",                  T_LAV),
    ("",                                     WHITE),
    ("> connect --school your_school.edu",   T_GRN),
    ("  Шаг 1: Оставьте заявку",             T_CYN),
    ("  Ответим в течение 24 часов",         (160,150,220)),
    ("  Шаг 2: Подберём условия",            T_CYN),
    ("  Шаг 3: Получите доступ",             T_CYN),
    ("  Старт с сентября 2026",              (160,150,220)),
    ("",                                     WHITE),
    ("[OK] Connected successfully!",         T_GRN),
]

CTA_WORDS=["Подключите","вашу","школу"]

def scene5(f):
    arr=bg_white_grad(accent=0.9)
    img=Image.fromarray(arr).convert("RGBA")
    bg_soft_grid(img,0.05)
    _PARTS.draw(img,f,0.2)

    d=ImageDraw.Draw(img,"RGBA")

    # ── LEFT: CTA words ──
    la=int(255*clamp(remap(f,376,392)))
    if la:
        label="СЛЕДУЮЩИЙ ШАГ"
        lw=tw(d,label,18,"mb")
        lx=72
        d.text((lx,192),label,font=F(18,"mb"),fill=(*PURPLE,la))
        d.line([(lx,218),(lx+lw+60,218)],fill=(*PURPLE_L,la),width=2)

    for i,(word,wy) in enumerate(zip(CTA_WORDS,[258,370,482])):
        ws=spring(remap(f,380+i*12,422+i*12))
        wa=int(255*clamp(remap(f,380+i*12,414+i*12)))
        if wa<=0: continue
        ay=int(wy+(1-ws)*80)
        shadow_text(d,word,72,ay,96,DEEP_BLUE,"sb",wa,sh=3)

    # underline
    ul_t=clamp(remap(f,416,434))
    if ul_t:
        uw2=tw(d,CTA_WORDS[-1],96,"sb")
        d.rectangle([72,588,72+int(uw2*ul_t),596],fill=(*PURPLE,255))

    # tagline
    sub_a=int(255*clamp(remap(f,424,440)))
    if sub_a:
        d.text((72,616),"Старт с сентября 2026",
               font=F(28,"sr"),fill=(*TEXT_BODY,sub_a))

    # ── RIGHT: terminal centred in right half ──
    TW3,TH3=760,420
    tx3=W//2+30+(W//2-30-TW3)//2    # centred in right half
    ty3=H//2-TH3//2
    ts3=spring(remap(f,378,428))
    tx3_anim=int(tx3+(1-ts3)*(TW3+100))

    if ts3>0.02:
        lines3=build_lines(CTA_TERM,None,len(CTA_TERM),418,448,f)
        tmp3=Image.new("RGBA",(TW3,TH3),(0,0,0,0))
        draw_terminal(tmp3,0,0,TW3,TH3,"connect.sh — bash",lines3,frame=f)
        img.paste(tmp3,(tx3_anim,ty3),tmp3)

    # ── Bottom: logo + URL centred ──
    logo_a=clamp(remap(f,432,448))
    if logo_a>0.02:
        paste_logo(img,W//2-160,H-72,120,alpha=logo_a)

        url="futuredoc.minzdrav.gov.ru"
        uw3=tw(d,url,30,"mb")
        url_x=W//2-160+70    # aligned next to logo
        # pill background
        pill_w=uw3+40
        d.rounded_rectangle([url_x-8,H-92,url_x+pill_w,H-52],
                              radius=20,fill=(*PURPLE_XL,int(230*logo_a)))
        d.text((url_x+12,H-88),url,font=F(30,"mb"),fill=(*DEEP_BLUE,int(255*logo_a)))

    return np.array(img.convert("RGB"))

# ─────────────────────────────────────────────
# SCENE CUTS
CUTS=[
    (75, 92, scene1, scene2),
    (195,212, scene2, scene3),
    (285,302, scene3, scene4),
    (375,392, scene4, scene5),
]

def make_frame(f):
    f=int(clamp(f,0,FRAMES-1))
    for f0,f1,sa,sb in CUTS:
        if f0<=f<f1:
            t=(f-f0)/(f1-f0)
            return fade_blend(sa(f),sb(f),t)
    if f<75:   return scene1(f)
    if f<195:  return scene2(f)
    if f<285:  return scene3(f)
    if f<375:  return scene4(f)
    return scene5(f)

# ─────────────────────────────────────────────
# RENDER
if __name__=="__main__":
    print("Rendering ДМШ promo v3  (1920×1080 · 30fps · 15s) …")

    def frame_fn(t):
        return make_frame(int(t*FPS))

    clip=VideoClip(frame_fn,duration=DUR)
    out="/home/user/1111/ДМШ_промо_v3.mp4"
    clip.write_videofile(out,fps=FPS,codec="libx264",
                         preset="fast",ffmpeg_params=["-crf","16"],
                         logger="bar")
    print(f"\nDone  →  {out}")
