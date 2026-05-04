"""
DMSh Promo Video v2 — modern dark style
1920x1080 · 30 fps · 15 s · MP4
Scenes: terminal boot → split-screen → metrics → features grid → CTA
"""
import math, random
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from moviepy import VideoClip

# ─────────────────────────────────────────────
# CONSTANTS
W, H   = 1920, 1080
FPS    = 30
DUR    = 15
FRAMES = FPS * DUR          # 450

# ─────────────────────────────────────────────
# PALETTE
BG0      = ( 6,  3, 18)     # deepest dark
BG1      = (14,  8, 40)     # dark navy
PUR      = (82, 41,221)     # brand purple
PUR_D    = (40, 20,110)
PUR_L    = (149,127,225)
GRN      = (  0,230,100)    # terminal green
CYN      = (  0,200,240)    # cyan
GLD      = (255,200, 50)    # gold
PNK      = (255, 80,180)    # pink
WHT      = (255,255,255)
TERM_BG  = ( 12, 12, 22)
BRWS_BG  = (245,245,250)
BRWS_BAR = (228,228,235)
DOT_R    = (255, 95, 86)
DOT_Y    = (255,189, 46)
DOT_G    = ( 39,201, 63)
SUBTEXT  = (170,150,220)

# ─────────────────────────────────────────────
# FONTS  (all Cyrillic-capable)
_FC = {}
def F(size, variant="sb"):
    key = (size, variant)
    if key not in _FC:
        paths = {
            "sb": "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
            "sr": "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
            "mb": "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf",
            "mr": "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
        }
        _FC[key] = ImageFont.truetype(paths[variant], size)
    return _FC[key]

# ─────────────────────────────────────────────
# MATH / EASING

def clamp(v, lo=0.0, hi=1.0):
    return max(lo, min(hi, v))

def remap(v, a, b, c=0.0, d=1.0):
    t = clamp((v-a)/(b-a) if b != a else 0.0)
    return c + (d-c)*t

def lerp(a, b, t):
    if isinstance(a, tuple):
        return tuple(int(a[i]+(b[i]-a[i])*t) for i in range(len(a)))
    return a + (b-a)*t

def eout3(t):
    t = clamp(t); return 1-(1-t)**3

def eout5(t):
    t = clamp(t); return 1-(1-t)**5

def ein_out(t):
    t = clamp(t); return t*t*(3-2*t)

def spring(t, stiff=220, damp=18):
    """Underdamped spring 0→1 with overshoot."""
    t = clamp(t)
    if t <= 0: return 0.0
    if t >= 1: return 1.0
    w0   = math.sqrt(stiff)
    zeta = damp / (2*math.sqrt(stiff))
    wd   = w0*math.sqrt(max(0,1-zeta*zeta))
    rt   = t * 1.1
    return 1 - math.exp(-zeta*w0*rt)*(math.cos(wd*rt) + (zeta*w0/max(wd,1e-6))*math.sin(wd*rt))

def prog(f, f0, f1, ease=eout3):
    return ease(remap(f, f0, f1))

# ─────────────────────────────────────────────
# BACKGROUNDS

def bg_dark(t_anim=0.0):
    """Animated dark gradient, left→right purple tint."""
    c1 = lerp(BG0, BG1, 0.5+0.5*math.sin(t_anim*math.pi))
    c2 = lerp(BG1, PUR_D, 0.3+0.2*math.sin(t_anim*math.pi*1.3+1))
    xs  = np.linspace(0,1,W,dtype=np.float32)
    row = np.stack([(c1[i]+(c2[i]-c1[i])*xs).astype(np.uint8) for i in range(3)],1)
    arr = np.tile(row[np.newaxis],(H,1,1))
    # slight vertical darkening at bottom
    ys  = np.linspace(1,0.7,H,dtype=np.float32)[:,np.newaxis,np.newaxis]
    return (arr*ys).clip(0,255).astype(np.uint8)

def bg_grid(img, alpha=0.07):
    d = ImageDraw.Draw(img,"RGBA")
    ga = int(255*alpha)
    for x in range(0,W,96):
        d.line([(x,0),(x,H)], fill=(*PUR,ga))
    for y in range(0,H,96):
        d.line([(0,y),(W,y)], fill=(*PUR,ga))

# ─────────────────────────────────────────────
# PARTICLES  (position computed from frame — stateless)

class Particles:
    def __init__(self, n=70, seed=7):
        rng = random.Random(seed)
        self.ps = [{
            'x0': rng.random()*W, 'y0': rng.random()*H,
            'vx': (rng.random()-.5)*.6,
            'vy': -(rng.random()*1.2+.2),
            'r' : rng.random()*2+.5,
            'a' : rng.random()*.5+.2,
            'c' : rng.choice([PUR_L,GRN,CYN,WHT]),
        } for _ in range(n)]

    def draw(self, img, frame, alpha=1.0):
        d = ImageDraw.Draw(img,"RGBA")
        for p in self.ps:
            x = (p['x0']+p['vx']*frame)%W
            y = (p['y0']+p['vy']*frame)%H
            r = p['r']
            a = int(p['a']*alpha*255)
            d.ellipse([x-r,y-r,x+r,y+r], fill=(*p['c'],a))

_PARTS = Particles()

# ─────────────────────────────────────────────
# TEXT HELPERS

def tw(d, text, sz, v="sb"):
    b = d.textbbox((0,0),text,font=F(sz,v)); return b[2]-b[0]
def th(d, text, sz, v="sb"):
    b = d.textbbox((0,0),text,font=F(sz,v)); return b[3]-b[1]

def txtc(d, text, cy, sz, col=WHT, v="sb", alpha=255):
    w_ = tw(d,text,sz,v)
    d.text(((W-w_)//2, cy-th(d,text,sz,v)//2), text,
           font=F(sz,v), fill=(*col,alpha))

def glow(d, text, x, y, sz, col, v="sb", strength=3, base_a=255):
    """Render text with a soft glow halo."""
    for r in range(strength,0,-1):
        a = int(base_a * 0.18 * (1-r/strength))
        for dx,dy in [(-r,0),(r,0),(0,-r),(0,r),(-r,-r),(r,-r),(-r,r),(r,r)]:
            d.text((x+dx,y+dy), text, font=F(sz,v), fill=(*col,a))
    d.text((x,y), text, font=F(sz,v), fill=(*col,base_a))

def typewriter(text, t):
    """Return first int(len*t) characters."""
    return text[:max(0,int(len(text)*clamp(t)))]

# ─────────────────────────────────────────────
# TERMINAL WINDOW

def draw_terminal(img, x, y, w, h, title, lines, frame=0):
    """
    lines: list of dict(text, color, t)
           t=1.0 → fully shown; t<1 → typewriter active
    """
    d  = ImageDraw.Draw(img,"RGBA")
    r  = 14

    # drop shadow
    for s in range(24,0,-3):
        a = int(180*(1-s/24)*0.25)
        d.rounded_rectangle([x+s,y+s,x+w+s,y+h+s],radius=r+2,fill=(0,0,0,a))

    # title bar
    d.rounded_rectangle([x,y,x+w,y+40], radius=r, fill=(32,32,46,255))
    d.rectangle([x,y+20,x+w,y+40], fill=(32,32,46,255))

    # body
    d.rectangle([x,y+40,x+w,y+h], fill=(*TERM_BG,252))
    d.rounded_rectangle([x,y+h-r*2,x+w,y+h], radius=r, fill=(*TERM_BG,252))

    # border glow
    d.rounded_rectangle([x,y,x+w,y+h], radius=r,
                         outline=(*PUR_L,60), width=1)

    # traffic dots
    for i,(dc) in enumerate([DOT_R,DOT_Y,DOT_G]):
        cx = x+16+i*22; cy = y+20
        d.ellipse([cx-7,cy-7,cx+7,cy+7], fill=(*dc,255))

    # title text
    tw_ = tw(d,title,15,"mr")
    d.text((x+w//2-tw_//2, y+12), title, font=F(15,"mr"),
           fill=(160,160,190,255))

    # scanlines (subtle CRT feel)
    for sy in range(y+42, y+h, 4):
        d.line([(x+1,sy),(x+w-1,sy)], fill=(0,0,0,12))

    # text lines
    lh, py = 30, y+54
    for ln in lines:
        if py > y+h-16: break
        shown = typewriter(ln["text"], ln["t"])
        # cursor blink on active line
        if ln["t"] < 1.0:
            if (frame//10)%2 == 0:
                shown += "█"        # block cursor
        d.text((x+18,py), shown, font=F(20,"mr"),
               fill=(*ln["color"],240))
        py += lh

# ─────────────────────────────────────────────
# BROWSER WINDOW

def draw_browser(img, x, y, w, h, url, content_fn, frame=0):
    d = ImageDraw.Draw(img,"RGBA")
    r = 14

    # shadow
    for s in range(24,0,-3):
        a = int(160*(1-s/24)*0.22)
        d.rounded_rectangle([x+s,y+s,x+w+s,y+h+s],radius=r+2,fill=(0,0,0,a))

    # chrome bar
    d.rounded_rectangle([x,y,x+w,y+52], radius=r, fill=(*BRWS_BAR,255))
    d.rectangle([x,y+28,x+w,y+52], fill=(*BRWS_BAR,255))

    # content
    d.rectangle([x,y+52,x+w,y+h], fill=(*BRWS_BG,255))
    d.rounded_rectangle([x,y+h-r*2,x+w,y+h], radius=r, fill=(*BRWS_BG,255))

    # dots
    for i,dc in enumerate([DOT_R,DOT_Y,DOT_G]):
        cx = x+16+i*22; cy = y+26
        d.ellipse([cx-7,cy-7,cx+7,cy+7], fill=(*dc,255))

    # URL bar
    ux, uy = x+100, y+10
    uw_ = int(w*0.52)
    d.rounded_rectangle([ux,uy,ux+uw_,uy+30], radius=15,
                         fill=(210,210,218,255))
    # lock icon
    d.text((ux+10,uy+5), "[S]",
           font=F(14,"mr"), fill=(80,80,100,255))
    url_disp = url if tw(d,url,15,"sr") < uw_-50 else url
    d.text((ux+34,uy+7), url_disp, font=F(15,"sr"), fill=(60,60,80,255))

    # top border accent
    d.rectangle([x,y+52,x+w,y+55], fill=(*PUR,200))

    # content callback
    content_fn(img, x, y+55, w, h-55)

# ─────────────────────────────────────────────
# GLASSMORPHISM CARD

def glass_card(img, x, y, w, h, accent, alpha_t=1.0, radius=18):
    # blur background
    bx,by,bw,bh = max(0,x),max(0,y),w,h
    region = img.crop((bx,by,bx+bw,by+bh))
    blurred = region.filter(ImageFilter.GaussianBlur(10)).convert("RGBA")
    tint = Image.new("RGBA",(bw,bh), (*PUR_D, int(160*alpha_t)))
    blurred = Image.alpha_composite(blurred, tint)
    img.paste(blurred,(bx,by))
    d = ImageDraw.Draw(img,"RGBA")
    # border
    d.rounded_rectangle([x,y,x+w,y+h], radius=radius,
                         outline=(*accent,int(180*alpha_t)), width=2)
    # left accent stripe
    d.rounded_rectangle([x,y+16,x+4,y+h-16], radius=2,
                         fill=(*accent,int(255*alpha_t)))

# ─────────────────────────────────────────────
# GLITCH TRANSITION

def glitch_blend(a_arr, b_arr, t, seed=0):
    """Cross-fade with RGB-channel glitch."""
    rng = random.Random(seed)
    out = (a_arr*(1-t)+b_arr*t).astype(np.uint8)
    if 0.15 < t < 0.85:
        shift = int((1-abs(t-0.5)*2)*18)
        if shift > 0:
            out[:,:,0] = np.roll(out[:,:,0], rng.randint(-shift,shift), axis=1)
            out[:,:,2] = np.roll(out[:,:,2], rng.randint(-shift,shift), axis=1)
            for _ in range(4):
                row = rng.randint(0,H-1)
                out[row,:,:] = np.roll(out[row,:,:], rng.randint(-30,30),axis=0)
    return out

# ─────────────────────────────────────────────
# ─────────────────────────────────────────────
# SCENE 1  (f=0..75)  TERMINAL BOOT
# ─────────────────────────────────────────────

BOOT_LINES = [
    {"text": "$ init dmsh-platform --env production",   "color": GRN},
    {"text": "  [OK] content   : 370 units loaded",     "color": GRN},
    {"text": "  [OK] users     : 20 000 registered",    "color": GRN},
    {"text": "  [OK] partners  : 100 connected",        "color": GRN},
    {"text": "  [OK] specs     : 30 specialisations",   "color": CYN},
    {"text": "$ connect futuredoc.minzdrav.gov.ru",     "color": CYN},
    {"text": "  Establishing secure connection...",     "color": (160,160,200)},
    {"text": "  Connected. Welcome to DMSH.",           "color": GLD},
]

def scene_boot(f):
    t   = remap(f, 0, 75)
    arr = bg_dark(t*0.4)
    img = Image.fromarray(arr,"RGB").convert("RGBA")
    bg_grid(img, 0.05)
    _PARTS.draw(img, f, alpha=clamp(t*2)*0.35)

    # Terminal window springs open from center
    WIN_W, WIN_H = 860, 320
    open_s = spring(remap(f, 2, 30))
    sw = max(4, int(WIN_W*open_s))
    sh = max(4, int(WIN_H*open_s))
    wx = W//2 - sw//2
    wy = H//2 - sh//2 - 60

    if open_s > 0.05:
        # compute which lines are visible
        content_t = remap(f, 28, 72)
        lines_out = []
        for i, ln in enumerate(BOOT_LINES):
            line_start = i/len(BOOT_LINES)
            line_end   = (i+1)/len(BOOT_LINES)
            lt = remap(content_t, line_start, line_end) * 2.5
            if content_t < line_start: break
            lines_out.append({
                "text" : ln["text"],
                "color": ln["color"],
                "t"    : clamp(lt),
            })
        # draw onto tmp surface for scale
        tmp = Image.new("RGBA",(WIN_W,WIN_H),(0,0,0,0))
        draw_terminal(tmp,0,0,WIN_W,WIN_H,"dmsh — bash",lines_out,frame=f)
        scaled = tmp.resize((sw,sh), Image.LANCZOS)
        img.paste(scaled,(wx,wy),scaled)

    # subtitle below terminal
    sub_a = int(255*clamp(remap(f,35,65)))
    if sub_a:
        d = ImageDraw.Draw(img,"RGBA")
        txt = "Цифровая платформа «Будущий врач»"
        txtc(d, txt, wy+sh+52, 34, SUBTEXT, "sr", sub_a)

    return np.array(img.convert("RGB"))

# ─────────────────────────────────────────────
# SCENE 2  (f=75..195)  SPLIT SCREEN
# ─────────────────────────────────────────────

STATS_LINES = [
    {"text": "# stats.py — platform metrics",           "color": (120,100,200)},
    {"text": "",                                         "color": WHT},
    {"text": "users    = 20_000   # +38% YoY",          "color": GRN},
    {"text": "partners =    100   # медвузы + школы",   "color": CYN},
    {"text": "content  =    370   # единиц",            "color": GLD},
    {"text": "specs    =     30   # специальностей",    "color": PNK},
    {"text": "",                                         "color": WHT},
    {"text": "platform.status = 'ACTIVE'",              "color": GRN},
]

def scene_split(f):
    t   = remap(f, 75, 195)
    arr = bg_dark(t*0.5+0.4)
    img = Image.fromarray(arr,"RGB").convert("RGBA")
    bg_grid(img, 0.06)
    _PARTS.draw(img, f, 0.28)

    d = ImageDraw.Draw(img,"RGBA")

    # divider line
    div_a = int(80*clamp(remap(f,78,95)))
    if div_a:
        d.line([(W//2,60),(W//2,H-60)], fill=(*PUR_L,div_a), width=1)

    # ── LEFT  browser slides in from left ──
    BW, BH = 860, 580
    bs = spring(remap(f, 75, 118))
    bx = int(30 + (bs-1)*(BW+60))
    by = H//2 - BH//2

    def browser_content(img_, cx, cy, cw, ch):
        d2 = ImageDraw.Draw(img_,"RGBA")
        pad = 44
        ct  = remap(f, 110, 185)

        # Headline
        ta = int(255*clamp(remap(f,112,138)))
        if ta:
            d2.text((cx+pad, cy+26),
                    "Дистанционная медицинская школа",
                    font=F(30,"sb"), fill=(20,15,55,ta))

        # Sub
        sa = int(255*clamp(remap(f,125,148)))
        if sa:
            d2.text((cx+pad, cy+74),
                    "Платформа «Будущий врач»",
                    font=F(21,"sr"), fill=(70,60,120,sa))

        # Badge
        ba = int(255*clamp(remap(f,135,155)))
        if ba:
            badge = "Минздрав России"
            bw2 = tw(d2,badge,16,"sr")+28
            d2.rounded_rectangle([cx+pad,cy+112,cx+pad+bw2,cy+140],
                                  radius=12,fill=(*PUR,ba//4))
            d2.text((cx+pad+14,cy+117),badge,font=F(16,"sr"),fill=(*PUR,ba))

        # Feature list
        feats = [
            "Олимпиадный тренажёр",
            "Медицинский Атлас",
            "Первая помощь + сертификат",
            "Подготовка к ЕГЭ",
        ]
        for i,feat in enumerate(feats):
            fa = int(255*clamp(remap(f, 145+i*10, 168+i*10)))
            if fa:
                fx,fy = cx+pad, cy+166+i*52
                # dot
                d2.ellipse([fx,fy+8,fx+10,fy+18],fill=(*GRN,fa))
                d2.text((fx+20,fy),feat,font=F(22,"sr"),fill=(25,20,60,fa))

    if bs > 0.02:
        draw_browser(img, bx, by, BW, BH,
                     "futuredoc.minzdrav.gov.ru", browser_content, frame=f)

    # ── RIGHT  terminal slides in from right ──
    TW2, TH2 = 820, 380
    ts2 = spring(remap(f, 82, 130))
    tx2 = int(W//2+30 + (1-ts2)*(TW2+80))
    ty2 = H//2 - TH2//2

    if ts2 > 0.02:
        content_t2 = remap(f, 125, 192)
        lines2 = []
        for i,ln in enumerate(STATS_LINES):
            ls = i/len(STATS_LINES)
            le = (i+1)/len(STATS_LINES)
            lt = remap(content_t2, ls, le)*2.5
            if content_t2 < ls: break
            lines2.append({"text":ln["text"],"color":ln["color"],"t":clamp(lt)})

        tmp2 = Image.new("RGBA",(TW2,TH2),(0,0,0,0))
        draw_terminal(tmp2,0,0,TW2,TH2,"stats.py — python3",lines2,frame=f)
        img.paste(tmp2,(tx2,ty2),tmp2)

    return np.array(img.convert("RGB"))

# ─────────────────────────────────────────────
# SCENE 3  (f=195..285)  METRICS
# ─────────────────────────────────────────────

METRICS = [
    (20000, "+", "пользователей",  GRN),
    (100,   "+", "партнёров",                          CYN),
    (370,   "+", "единиц контента", GLD),
    (30,    "+", "специальностей",  PNK),
]

def count_str(target, t):
    v = int(eout3(clamp(t))*target)
    s = f"{v:,}".replace(","," ")   # narrow no-break space
    return s

def scene_metrics(f):
    t   = remap(f, 195, 285)
    arr = bg_dark(t*0.3+0.9)
    img = Image.fromarray(arr,"RGB").convert("RGBA")
    bg_grid(img, 0.07)
    _PARTS.draw(img, f, 0.4)

    d = ImageDraw.Draw(img,"RGBA")

    # Header
    ha = int(255*clamp(remap(f,196,218)))
    if ha:
        glow(d,"Платформа «Будущий врач» — в цифрах",
              (W - tw(d,"Платформа «Будущий врач» — в цифрах",44,"sb"))//2,
              88, 44, WHT, "sb", strength=4, base_a=ha)
        # underline
        uw = tw(d,"Платформа «Будущий врач» — в цифрах",44,"sb")
        d.rectangle([(W-uw)//2,144,(W+uw)//2,148],fill=(*PUR,ha))

    # 4 metric cards
    CW,CH = 380,270
    gap   = 36
    total = len(METRICS)*CW+(len(METRICS)-1)*gap
    sx    = (W-total)//2
    sy    = 200

    for i,(target,suf,label,col) in enumerate(METRICS):
        delay = i*0.12
        ct    = spring(remap(f, 195+i*14, 240+i*14))
        if ct <= 0: continue
        cx = sx+i*(CW+gap)

        # glow halo behind card
        for g in range(30,0,-5):
            a = int(25*(1-g/30)*ct)
            d.rounded_rectangle([cx-g//2,sy-g//2,cx+CW+g//2,sy+CH+g//2],
                                  radius=22, fill=(*col,a))

        # glass card
        glass_card(img,cx,sy,CW,CH,col,alpha_t=ct)
        d2 = ImageDraw.Draw(img,"RGBA")

        # big number with glow
        nt = remap(f, 205+i*12, 260+i*12)
        num = count_str(target, nt)
        if nt >= 1.0:
            num = f"{target:,}".replace(","," ") + suf
        glow(d2, num, cx+(CW-tw(d2,num,76,"sb"))//2, sy+28,
             76, col, "sb", strength=5, base_a=int(255*ct))

        # label
        lw = tw(d2,label,24,"sr")
        d2.text((cx+(CW-lw)//2, sy+126), label,
                font=F(24,"sr"), fill=(*WHT,int(220*ct)))

        # progress bar
        bt = clamp(remap(f, 220+i*10, 268+i*10))
        bw_full = CW-48
        bar_y = sy+CH-48
        d2.rounded_rectangle([cx+24,bar_y,cx+24+bw_full,bar_y+8],
                              radius=4, fill=(*TERM_BG,200))
        if bt > 0:
            d2.rounded_rectangle([cx+24,bar_y,cx+24+int(bw_full*bt),bar_y+8],
                                  radius=4, fill=(*col,int(255*ct)))

    # tagline bottom
    tg_a = int(255*clamp(remap(f,264,282)))
    if tg_a:
        d = ImageDraw.Draw(img,"RGBA")
        txtc(d,"От 5 класса — до поступления в медицинский вуз",
              sy+CH+68, 28, SUBTEXT, "sr", tg_a)

    return np.array(img.convert("RGB"))

# ─────────────────────────────────────────────
# SCENE 4  (f=285..375)  FEATURE CARDS
# ─────────────────────────────────────────────

FEATURES = [
    (GRN,  "[1]", "Олимпиадный тренажёр",   "Задачи прошлых лет с разборами"),
    (CYN,  "[2]", "Первая помощь",             "Видеокурс + сертификат"),
    (GLD,  "[3]", "Медицинский Атлас",        "Интерактивные изображения"),
    (PNK,  "[4]", "Подготовка к ЕГЭ",          "Биология, химия, анатомия"),
    (PUR_L,"[5]", "Профориентация",        "Энциклопедия специальностей"),
    (WHT,  "[6]", "Сертификаты",                "Доп. баллы при поступлении"),
]
# entrance direction per card: (dx,dy) normalised
DIRS = [(-1,0),(0,-1),(1,0),(-1,0),(0,1),(1,0)]

def scene_features(f):
    t   = remap(f, 285, 375)
    arr = bg_dark(1.2+t*0.2)
    img = Image.fromarray(arr,"RGB").convert("RGBA")
    bg_grid(img, 0.06)
    _PARTS.draw(img, f, 0.32)

    d = ImageDraw.Draw(img,"RGBA")

    # header
    ha = int(255*clamp(remap(f,286,305)))
    if ha:
        glow(d,"Что входит в ДМШ?",
             (W-tw(d,"Что входит в ДМШ?",52,"sb"))//2,
             56,52,WHT,"sb",strength=4,base_a=ha)

    COLS, CW, CH = 3, 510, 178
    hg, vg = 38, 28
    total_w = COLS*CW+(COLS-1)*hg
    fx_base = (W-total_w)//2
    fy_base = 162

    for i,(col,badge,title_,sub) in enumerate(FEATURES):
        c  = i%COLS; r = i//COLS
        delay_f = 285 + c*12 + r*22
        ct = spring(remap(f, delay_f, delay_f+55))
        if ct <= 0: continue

        dx,dy = DIRS[i]
        base_x = fx_base + c*(CW+hg)
        base_y = fy_base + r*(CH+vg)
        off = int((1-ct)*140)
        cx_ = base_x + dx*off
        cy_ = base_y + dy*off
        a_i = int(255*clamp(ct))

        glass_card(img, cx_, cy_, CW, CH, col, alpha_t=ct)
        d2 = ImageDraw.Draw(img,"RGBA")

        # badge
        glow(d2,badge,cx_+16,cy_+18,28,col,"mb",strength=3,base_a=a_i)
        # title
        d2.text((cx_+90,cy_+18),title_,font=F(30,"sb"),fill=(*WHT,a_i))
        # sub
        d2.text((cx_+90,cy_+62),sub,font=F(21,"sr"),fill=(*col,int(200*ct)))
        # bottom separator
        d2.rectangle([cx_+18,cy_+CH-36,cx_+CW-18,cy_+CH-34],
                      fill=(*col,int(80*ct)))

    return np.array(img.convert("RGB"))

# ─────────────────────────────────────────────
# SCENE 5  (f=375..450)  CTA
# ─────────────────────────────────────────────

CTA_TERM = [
    {"text": "$ connect --school your_school.edu",      "color": GRN},
    {"text": "> Шаг 1: Оставьте заявку",                    "color": CYN},
    {"text": "  Ответим в течение 24 часов",              "color": (150,150,190)},
    {"text": "> Шаг 2: Подберём условия",                 "color": CYN},
    {"text": "  Оптимальный вариант для вас",          "color": (150,150,190)},
    {"text": "> Шаг 3: Получите доступ",                  "color": CYN},
    {"text": "  Старт с сентября 2026",              "color": (150,150,190)},
    {"text": "",                                          "color": WHT},
    {"text": "[OK] Connected. Welcome!",                  "color": GLD},
]

CTA_WORDS = [
    "Подключите",
    "вашу",
    "школу",
]

def scene_cta(f):
    t   = remap(f, 375, 450)
    arr = bg_dark(1.4+t*0.3)
    img = Image.fromarray(arr,"RGB").convert("RGBA")
    bg_grid(img, 0.08)
    _PARTS.draw(img, f, 0.45)

    d = ImageDraw.Draw(img,"RGBA")

    # left column — big CTA words spring in
    label_a = int(255*clamp(remap(f,376,392)))
    if label_a:
        d.text((80,196),"СЛЕДУЮЩИЙ ШАГ",
               font=F(20,"mr"),fill=(*GRN,label_a))
        d.line([(80,224),(360,224)],fill=(*GRN,label_a),width=2)

    word_y = [256, 370, 484]
    for i,(word,wy) in enumerate(zip(CTA_WORDS,word_y)):
        ws = spring(remap(f, 380+i*12, 420+i*12))
        wa = int(255*clamp(remap(f, 380+i*12, 412+i*12)))
        if wa <= 0: continue
        actual_y = int(wy + (1-ws)*90)
        glow(d,word,80,actual_y,100,WHT,"sb",strength=5,base_a=wa)

    # green underline under last word
    ul_t = clamp(remap(f, 415, 435))
    if ul_t:
        uw2 = tw(d,CTA_WORDS[-1],100,"sb")
        d.rectangle([80,word_y[-1]+106,80+int(uw2*ul_t),word_y[-1]+114],
                     fill=(*GRN,255))

    # "Start September 2026"
    sub_a2 = int(255*clamp(remap(f,422,440)))
    if sub_a2:
        d.text((80,614),"Старт с сентября 2026",
               font=F(30,"sr"),fill=(*PUR_L,sub_a2))

    # right — terminal slides in
    TW3,TH3 = 780,400
    ts3 = spring(remap(f,378,428))
    tx3 = int(W-TW3-60+(1-ts3)*(TW3+80))
    ty3 = H//2 - TH3//2

    if ts3 > 0.02:
        ct3   = remap(f, 420, 448)
        lines3 = []
        for i,ln in enumerate(CTA_TERM):
            ls = i/len(CTA_TERM); le=(i+1)/len(CTA_TERM)
            lt = remap(ct3,ls,le)*2.5
            if ct3 < ls: break
            lines3.append({"text":ln["text"],"color":ln["color"],"t":clamp(lt)})

        tmp3 = Image.new("RGBA",(TW3,TH3),(0,0,0,0))
        draw_terminal(tmp3,0,0,TW3,TH3,"connect.sh — bash",lines3,frame=f)
        img.paste(tmp3,(tx3,ty3),tmp3)

    # glowing URL at bottom
    url_a = int(255*clamp(remap(f,430,448)))
    if url_a:
        url = "futuredoc.minzdrav.gov.ru"
        ux  = (W-tw(d,url,34,"mb"))//2
        glow(d,url,ux,H-74,34,GRN,"mb",strength=6,base_a=url_a)

    return np.array(img.convert("RGB"))

# ─────────────────────────────────────────────
# TRANSITIONS  (short cross-dissolve + glitch)
# ─────────────────────────────────────────────

CUTS = [
    (75,  90,  scene_boot,     scene_split),
    (195, 210, scene_split,    scene_metrics),
    (285, 300, scene_metrics,  scene_features),
    (375, 390, scene_features, scene_cta),
]

def make_frame(f):
    f = clamp(f, 0, FRAMES-1)
    f = int(f)
    for (f0,f1,sa,sb) in CUTS:
        if f0 <= f < f1:
            t  = (f-f0)/(f1-f0)
            return glitch_blend(sa(f), sb(f), t, seed=f0)
    if f < 75:   return scene_boot(f)
    if f < 195:  return scene_split(f)
    if f < 285:  return scene_metrics(f)
    if f < 375:  return scene_features(f)
    return scene_cta(f)

# ─────────────────────────────────────────────
# RENDER
# ─────────────────────────────────────────────
if __name__ == "__main__":
    print("Rendering ДМШ promo v2  (1920x1080 · 30fps · 15s)…")

    def frame_fn(t):
        return make_frame(int(t*FPS))

    clip = VideoClip(frame_fn, duration=DUR)
    out  = "/home/user/1111/ДМШ_промо_v2.mp4"
    clip.write_videofile(out, fps=FPS, codec="libx264",
                         preset="fast", ffmpeg_params=["-crf","16"],
                         logger="bar")
    print(f"\nDone  →  {out}")
