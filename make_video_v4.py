"""
DMSh Promo Video v4
Fixes applied over v3:
1. No text shadows anywhere — plain crisp text
2. Scanlines removed from terminal
3. New horizontal logo "БУДУЩИЙ ВРАЧ"
4. Metrics scene vertically centred
5. Features scene vertically centred
6. Logo removed from CTA scene (only URL)
"""
import math, random
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from moviepy import VideoClip

W, H   = 1920, 1080
FPS    = 30
DUR    = 15
FRAMES = FPS * DUR

# ── Palette ──────────────────────────────────
BG_WHITE  = (255, 255, 255)
BG_PALE   = (237, 233, 255)

DEEP_BLUE = ( 27,  20, 100)
NAVY      = ( 40,  32, 140)
PURPLE    = (107,  82, 221)
PURPLE_D  = ( 64,  48, 160)
PURPLE_L  = (176, 160, 232)
PURPLE_XL = (220, 212, 250)

TEXT_BODY = ( 70,  60, 130)
TEXT_SOFT = (140, 128, 190)

TERM_BG   = ( 12,  10,  35)
T_GRN     = ( 80, 220, 120)
T_CYN     = ( 70, 195, 240)
T_GLD     = (240, 190,  60)
T_PNK     = (240, 100, 200)
T_LAV     = (170, 150, 255)

DOT_R = (255, 95, 86); DOT_Y = (255,189,46); DOT_G = (39,201,63)
WHITE = (255,255,255)
BRWS_TOP = (240,238,250); BRWS_URL = (220,216,244)

# ── Fonts ─────────────────────────────────────
_FC = {}
def F(size, v="sb"):
    if (size,v) not in _FC:
        _FC[(size,v)] = ImageFont.truetype({
            "sb":"/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "sr":"/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "mb":"/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf",
            "mr":"/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
        }[v], size)
    return _FC[(size,v)]

# ── Math ──────────────────────────────────────
def clamp(v,lo=0.0,hi=1.0): return max(lo,min(hi,v))
def remap(v,a,b,c=0.0,d=1.0):
    t=clamp((v-a)/(b-a) if b!=a else 0.0); return c+(d-c)*t
def lerp_c(a,b,t): return tuple(int(a[i]+(b[i]-a[i])*clamp(t)) for i in range(len(a)))
def eout3(t): t=clamp(t); return 1-(1-t)**3
def ein_out(t): t=clamp(t); return t*t*(3-2*t)
def spring(t,stiff=200,damp=18):
    t=clamp(t)
    if t<=0: return 0.0
    if t>=1: return 1.0
    w0=math.sqrt(stiff); z=damp/(2*math.sqrt(stiff))
    wd=w0*math.sqrt(max(0,1-z*z)); rt=t*1.1
    return 1-math.exp(-z*w0*rt)*(math.cos(wd*rt)+(z*w0/max(wd,1e-9))*math.sin(wd*rt))

# ── Background ───────────────────────────────
def bg_white_grad(accent=0.0):
    arr=np.ones((H,W,3),dtype=np.float32)*255
    ys=np.linspace(0,1,H)[:,np.newaxis,np.newaxis]
    tint=np.array(BG_PALE,dtype=np.float32)
    arr=arr*(1-ys*0.32*accent)+tint*(ys*0.32*accent)
    return arr.clip(0,255).astype(np.uint8)

def bg_soft_grid(img, alpha=0.045):
    d=ImageDraw.Draw(img,"RGBA"); a=int(255*alpha)
    for x in range(0,W,96): d.line([(x,0),(x,H)],fill=(*PURPLE_L,a))
    for y in range(0,H,96): d.line([(0,y),(W,y)],fill=(*PURPLE_L,a))

# ── Particles ────────────────────────────────
class Particles:
    def __init__(self,n=55,seed=13):
        rng=random.Random(seed)
        self.ps=[{'x0':rng.random()*W,'y0':rng.random()*H,
                  'vx':(rng.random()-.5)*.5,'vy':-(rng.random()*1.0+.2),
                  'r':rng.random()*3+1,'a':rng.random()*.2+.06,
                  'c':rng.choice([PURPLE_L,PURPLE,PURPLE_XL])} for _ in range(n)]
    def draw(self,img,frame,alpha=1.0):
        d=ImageDraw.Draw(img,"RGBA")
        for p in self.ps:
            x=(p['x0']+p['vx']*frame)%W; y=(p['y0']+p['vy']*frame)%H
            a=int(p['a']*alpha*255)
            d.ellipse([x-p['r'],y-p['r'],x+p['r'],y+p['r']],fill=(*p['c'],a))
_PARTS=Particles()

# ── Logo — horizontal "БУДУЩИЙ ВРАЧ" ─────────
def make_logo_h(height=110):
    """Horizontal logo: [icon] [БУДУЩИЙ ВРАЧ]"""
    # Measure text first
    probe=Image.new("RGBA",(1,1)); dp=ImageDraw.Draw(probe)
    ts = int(height*0.58)
    text="БУДУЩИЙ ВРАЧ"
    b=dp.textbbox((0,0),text,font=F(ts,"sb"))
    text_w=b[2]-b[0]; text_h=b[3]-b[1]

    icon_w = int(height*0.88)
    gap    = int(height*0.18)
    total_w= icon_w + gap + text_w + 4
    img=Image.new("RGBA",(total_w,height),(0,0,0,0))
    d=ImageDraw.Draw(img,"RGBA")

    # ── Icon: arc behind + cross ──
    icx=icon_w//2; icy=height//2

    # lighter arc (circle) slightly offset → creates crescent feel
    ar=int(height*0.40)
    d.ellipse([icx-ar,icy-ar,icx+ar,icy+ar],fill=(*PURPLE_L,230))
    # second smaller lighter circle offset right+down
    ar2=int(height*0.32)
    ox,oy=int(height*0.14),int(height*0.10)
    d.ellipse([icx+ox-ar2,icy+oy-ar2,icx+ox+ar2,icy+oy+ar2],fill=(*PURPLE_XL,180))

    # cross
    aw=int(height*0.20); al=int(height*0.70)
    d.rectangle([icx-aw//2,icy-al//2,icx+aw//2,icy+al//2],fill=(*PURPLE,255))
    d.rectangle([icx-al//2,icy-aw//2,icx+al//2,icy+aw//2],fill=(*PURPLE,255))

    # ── Text ──
    tx=icon_w+gap; ty=(height-text_h)//2 - 2
    d.text((tx,ty),text,font=F(ts,"sb"),fill=(*DEEP_BLUE,255))
    return img

_LOGO_H_CACHE={}
def get_logo_h(height):
    if height not in _LOGO_H_CACHE:
        _LOGO_H_CACHE[height]=make_logo_h(height)
    return _LOGO_H_CACHE[height]

def paste_logo_h(img, cx, cy, height, alpha=1.0):
    """Paste horizontal logo centred at (cx,cy)."""
    logo=get_logo_h(height).copy()
    if alpha<1.0:
        arr=np.array(logo,dtype=np.float32); arr[:,:,3]*=alpha
        logo=Image.fromarray(arr.clip(0,255).astype(np.uint8),"RGBA")
    lw=logo.width
    img.paste(logo,(cx-lw//2,cy-height//2),logo)

# ── Text helpers (NO shadow) ─────────────────
def tw(d,t,sz,v="sb"):
    b=d.textbbox((0,0),t,font=F(sz,v)); return b[2]-b[0]
def th(d,t,sz,v="sb"):
    b=d.textbbox((0,0),t,font=F(sz,v)); return b[3]-b[1]

def text_c(d,text,cy,sz,col=DEEP_BLUE,v="sb",alpha=255):
    w_=tw(d,text,sz,v); h_=th(d,text,sz,v)
    d.text(((W-w_)//2,cy-h_//2),text,font=F(sz,v),fill=(*col,alpha))

def text_xy(d,text,x,y,sz,col=DEEP_BLUE,v="sb",alpha=255):
    d.text((x,y),text,font=F(sz,v),fill=(*col,alpha))

def typewriter(text,t):
    return text[:max(0,int(len(text)*clamp(t)))]

# ── Terminal (NO scanlines) ───────────────────
def draw_terminal(img,x,y,w,h,title,lines,frame=0):
    d=ImageDraw.Draw(img,"RGBA"); r=14
    # shadow
    for s in range(20,0,-4):
        d.rounded_rectangle([x+s,y+s,x+w+s,y+h+s],radius=r+2,
                             fill=(0,0,0,int(90*(1-s/20)*0.18)))
    # title bar
    d.rounded_rectangle([x,y,x+w,y+40],radius=r,fill=(32,30,55,255))
    d.rectangle([x,y+22,x+w,y+40],fill=(32,30,55,255))
    # body — solid dark, NO scanlines
    d.rectangle([x,y+40,x+w,y+h],fill=(*TERM_BG,255))
    d.rounded_rectangle([x,y+h-r*2,x+w,y+h],radius=r,fill=(*TERM_BG,255))
    d.rounded_rectangle([x,y,x+w,y+h],radius=r,outline=(*PURPLE_L,45),width=1)
    # dots
    for i,dc in enumerate([DOT_R,DOT_Y,DOT_G]):
        cx_=x+16+i*22
        d.ellipse([cx_-7,y+13,cx_+7,y+27],fill=(*dc,255))
    # title
    tw_=tw(d,title,15,"mr")
    d.text((x+w//2-tw_//2,y+12),title,font=F(15,"mr"),fill=(160,155,210,255))
    # text lines — generous line-height for readability
    lh=34; py=y+58
    for ln in lines:
        if py>y+h-20: break
        shown=typewriter(ln["text"],ln["t"])
        if ln["t"]<1.0 and (frame//10)%2==0: shown+="█"
        d.text((x+22,py),shown,font=F(21,"mr"),fill=(*ln["color"],240))
        py+=lh

# ── Browser window ────────────────────────────
def draw_browser(img,x,y,w,h,url,content_fn):
    d=ImageDraw.Draw(img,"RGBA"); r=14
    for s in range(20,0,-4):
        d.rounded_rectangle([x+s,y+s,x+w+s,y+h+s],radius=r+2,
                             fill=(60,50,160,int(80*(1-s/20)*0.15)))
    d.rounded_rectangle([x,y,x+w,y+50],radius=r,fill=(*BRWS_TOP,255))
    d.rectangle([x,y+28,x+w,y+50],fill=(*BRWS_TOP,255))
    d.rectangle([x,y+50,x+w,y+h],fill=(*BG_WHITE,255))
    d.rounded_rectangle([x,y+h-r*2,x+w,y+h],radius=r,fill=(*BG_WHITE,255))
    d.rounded_rectangle([x,y,x+w,y+h],radius=r,outline=(*PURPLE_L,110),width=1)
    for i,dc in enumerate([DOT_R,DOT_Y,DOT_G]):
        cx_=x+16+i*22
        d.ellipse([cx_-7,y+18,cx_+7,y+32],fill=(*dc,255))
    ux,uy=x+100,y+10; uw_=int(w*0.52)
    d.rounded_rectangle([ux,uy,ux+uw_,uy+28],radius=14,fill=(*BRWS_URL,255))
    d.text((ux+12,uy+6),"[https]  "+url,font=F(14,"sr"),fill=(*TEXT_BODY,200))
    d.rectangle([x,y+50,x+w,y+54],fill=(*PURPLE,210))
    content_fn(img,x,y+54,w,h-54)

# ── Light card ────────────────────────────────
def light_card(img,x,y,w,h,accent=PURPLE,alpha_t=1.0,radius=18):
    d=ImageDraw.Draw(img,"RGBA")
    d.rounded_rectangle([x,y,x+w,y+h],radius=radius,fill=(*BG_WHITE,int(245*alpha_t)))
    d.rounded_rectangle([x,y,x+w,y+h],radius=radius,outline=(*accent,int(150*alpha_t)),width=2)
    d.rounded_rectangle([x,y+14,x+5,y+h-14],radius=3,fill=(*accent,int(255*alpha_t)))

# ── Transition ────────────────────────────────
def fade_blend(a,b,t):
    t=ein_out(clamp(t)); return (a*(1-t)+b*t).astype(np.uint8)

# ── Terminal line builder ─────────────────────
def build_lines(spec,f_start,f_end,frame):
    ct=remap(frame,f_start,f_end)
    visible=max(1,int(ct*len(spec))); out=[]
    for i,ln in enumerate(spec[:visible]):
        if i<visible-1:
            out.append({"text":ln[0],"color":ln[1],"t":1.0})
        else:
            ls=i/len(spec); le=(i+1)/len(spec)
            out.append({"text":ln[0],"color":ln[1],"t":clamp(remap(ct,ls,le)*2.2)})
    return out

# ═══════════════════════════════════════════════
# SCENE 1  f=0..75   LOGO HERO
# ═══════════════════════════════════════════════
def scene1(f):
    t=remap(f,0,75)
    arr=bg_white_grad(accent=min(1.0,t*1.5))
    img=Image.fromarray(arr).convert("RGBA")
    bg_soft_grid(img,0.04)
    _PARTS.draw(img,f,alpha=clamp(t*2)*0.16)
    d=ImageDraw.Draw(img,"RGBA")

    # Logo springs in — horizontal, centred
    ls=spring(remap(f,2,38))
    logo_h=int(130*ls)
    if logo_h>8:
        paste_logo_h(img,W//2,H//2-40,logo_h,alpha=clamp(ls))

    # Title
    ta=int(255*clamp(remap(f,32,54)))
    ty_off=int((1-eout3(remap(f,32,54)))*38)
    if ta:
        text_c(d,"Дистанционная медицинская школа",
               H//2+108+ty_off,44,DEEP_BLUE,"sb",ta)

    # Subtitle
    sa=int(255*clamp(remap(f,42,62)))
    if sa:
        text_c(d,"Цифровая платформа «Будущий врач»",
               H//2+168,26,TEXT_BODY,"sr",sa)

    # Badge
    ba=int(255*clamp(remap(f,52,70)))
    if ba:
        badge="При поддержке Минздрава России"
        bw=tw(d,badge,19,"sr")+44
        bx=(W-bw)//2; by=H//2+208
        d.rounded_rectangle([bx,by,bx+bw,by+40],radius=20,
                             fill=(*PURPLE_XL,int(210*ba/255)))
        d.rounded_rectangle([bx,by,bx+bw,by+40],radius=20,
                             outline=(*PURPLE_L,int(140*ba/255)),width=1)
        text_c(d,badge,by+20,19,PURPLE,"sr",ba)

    return np.array(img.convert("RGB"))

# ═══════════════════════════════════════════════
# SCENE 2  f=75..195   SPLIT
# ═══════════════════════════════════════════════
STATS_SPEC=[
    ("# Статистика платформы",               T_LAV),
    ("",                                     WHITE),
    ("> users    = 20_000  # пользователей", T_GRN),
    ("> partners =    100  # партнёров",     T_CYN),
    ("> content  =    370  # единиц",        T_GLD),
    ("> specs    =     30  # специальностей",T_PNK),
    ("",                                     WHITE),
    ("> platform.status = 'ACTIVE'",         T_GRN),
]

def scene2(f):
    arr=bg_white_grad(accent=0.6)
    img=Image.fromarray(arr).convert("RGBA")
    bg_soft_grid(img,0.04)
    _PARTS.draw(img,f,0.13)
    d=ImageDraw.Draw(img,"RGBA")

    div_a=int(50*clamp(remap(f,80,100)))
    if div_a: d.line([(W//2,80),(W//2,H-80)],fill=(*PURPLE_L,div_a),width=1)

    # ── LEFT browser ──
    BW,BH=860,560
    bs=spring(remap(f,75,122))
    bx=int(40+(bs-1)*(BW+60)); by=H//2-BH//2

    def bcontent(img_,cx,cy,cw,ch):
        d2=ImageDraw.Draw(img_,"RGBA"); pad=44
        # mini logo
        la=int(255*clamp(remap(f,118,136)))
        if la: paste_logo_h(img_,cx+cw//2,cy+46,68,alpha=la/255)
        # heading
        ta=int(255*clamp(remap(f,122,144)))
        if ta:
            text_xy(d2,"Дистанционная медицинская школа",
                    cx+pad,cy+98,24,DEEP_BLUE,"sb",ta)
        sa=int(255*clamp(remap(f,132,152)))
        if sa:
            text_xy(d2,"Платформа «Будущий врач»",
                    cx+pad,cy+136,18,TEXT_BODY,"sr",sa)
        ba=int(255*clamp(remap(f,142,160)))
        if ba:
            badge="Минздрав России"
            bw2=tw(d2,badge,15,"sr")+26
            d2.rounded_rectangle([cx+pad,cy+164,cx+pad+bw2,cy+190],
                                  radius=11,fill=(*PURPLE_XL,int(220*ba/255)))
            text_xy(d2,badge,cx+pad+13,cy+169,15,PURPLE,"sr",ba)
        feats=["Олимпиадный тренажёр","Медицинский Атлас",
               "Первая помощь + сертификат","Подготовка к ЕГЭ"]
        for i,feat in enumerate(feats):
            fa=int(255*clamp(remap(f,150+i*10,172+i*10)))
            if fa:
                fy=cy+212+i*52
                d2.ellipse([cx+pad,fy+10,cx+pad+10,fy+20],fill=(*PURPLE,fa))
                text_xy(d2,feat,cx+pad+20,fy,21,TEXT_BODY,"sr",fa)

    if bs>0.02: draw_browser(img,bx,by,BW,BH,"futuredoc.minzdrav.gov.ru",bcontent)

    # ── RIGHT terminal ──
    TW2,TH2=820,400
    tx2=W//2+30+(W//2-30-TW2)//2
    ts2=spring(remap(f,82,130))
    tx2_a=int(tx2+(1-ts2)*(TW2+100)); ty2=H//2-TH2//2
    if ts2>0.02:
        lines2=build_lines(STATS_SPEC,122,192,f)
        tmp2=Image.new("RGBA",(TW2,TH2),(0,0,0,0))
        draw_terminal(tmp2,0,0,TW2,TH2,"stats.py — python3",lines2,frame=f)
        img.paste(tmp2,(tx2_a,ty2),tmp2)

    return np.array(img.convert("RGB"))

# ═══════════════════════════════════════════════
# SCENE 3  f=195..285   METRICS — vertically centred
# ═══════════════════════════════════════════════
METRICS=[
    (20000,"+","пользователей", PURPLE),
    (  100,"+","партнёров",     DEEP_BLUE),
    (  370,"+","единиц контента",PURPLE_D),
    (   30,"+","специальностей",NAVY),
]

def count_str(target,t):
    v=int(eout3(clamp(t))*target)
    return f"{v:,}".replace(","," ")

def scene3(f):
    arr=bg_white_grad(accent=0.8)
    img=Image.fromarray(arr).convert("RGBA")
    bg_soft_grid(img,0.05)
    _PARTS.draw(img,f,0.13)
    d=ImageDraw.Draw(img,"RGBA")

    # ── Vertical layout ──
    TITLE_H = 58     # heading font ~46 + margin
    UL_H    = 18     # underline + gap
    CW,CH   = 368,270
    GAP     = 36
    TAG_H   = 50
    BLOCK_H = TITLE_H + UL_H + CH + TAG_H
    top     = (H - BLOCK_H) // 2   # vertically centred

    title_cy = top + TITLE_H//2
    ul_y     = top + TITLE_H + 4
    sy       = top + TITLE_H + UL_H
    tag_cy   = sy + CH + TAG_H//2 + 8
    total_cards = len(METRICS)*CW+(len(METRICS)-1)*GAP
    sx = (W - total_cards)//2

    # heading
    ha=int(255*clamp(remap(f,196,218)))
    if ha:
        text_c(d,"Платформа «Будущий врач» в цифрах",title_cy,46,DEEP_BLUE,"sb",ha)
        uw=tw(d,"Платформа «Будущий врач» в цифрах",46,"sb")
        d.rectangle([(W-uw)//2,ul_y,(W+uw)//2,ul_y+4],fill=(*PURPLE,ha))

    for i,(target,suf,label,col) in enumerate(METRICS):
        ct=spring(remap(f,197+i*14,244+i*14))
        if ct<=0: continue
        cx=sx+i*(CW+GAP)

        # card glow
        for g in range(20,0,-5):
            d.rounded_rectangle([cx-g//2,sy-g//2,cx+CW+g//2,sy+CH+g//2],
                                 radius=22,fill=(*col,int(14*(1-g/20)*ct)))
        light_card(img,cx,sy,CW,CH,col,ct)
        d2=ImageDraw.Draw(img,"RGBA")

        # big number — centred in card, no shadow
        nt=remap(f,207+i*12,262+i*12)
        num=count_str(target,nt)
        if nt>=1.0: num=f"{target:,}".replace(","," ")+suf
        nw=tw(d2,num,72,"sb")
        d2.text((cx+(CW-nw)//2,sy+26),num,font=F(72,"sb"),fill=(*col,int(255*ct)))

        # label centred
        lw=tw(d2,label,22,"sr")
        d2.text((cx+(CW-lw)//2,sy+118),label,font=F(22,"sr"),
                fill=(*TEXT_BODY,int(220*ct)))

        # progress bar
        bt=clamp(remap(f,222+i*10,270+i*10))
        bw_f=CW-48; bar_y=sy+CH-46
        d2.rounded_rectangle([cx+24,bar_y,cx+24+bw_f,bar_y+8],
                              radius=4,fill=(*PURPLE_XL,200))
        if bt>0:
            d2.rounded_rectangle([cx+24,bar_y,cx+24+int(bw_f*bt),bar_y+8],
                                  radius=4,fill=(*col,int(255*ct)))

    tg_a=int(255*clamp(remap(f,266,282)))
    if tg_a:
        text_c(d,"От 5 класса до поступления в медицинский вуз",
               tag_cy,26,TEXT_SOFT,"sr",tg_a)

    return np.array(img.convert("RGB"))

# ═══════════════════════════════════════════════
# SCENE 4  f=285..375   FEATURES — vertically centred
# ═══════════════════════════════════════════════
FEATURES=[
    (PURPLE,   "[1]","Олимпиадный тренажёр", "Задачи прошлых лет с разборами"),
    (DEEP_BLUE,"[2]","Первая помощь",         "Видеокурс + сертификат"),
    (PURPLE_D, "[3]","Медицинский Атлас",     "Интерактивные изображения"),
    (NAVY,     "[4]","Подготовка к ЕГЭ",      "Биология, химия, анатомия"),
    (PURPLE,   "[5]","Профориентация",        "Энциклопедия специальностей"),
    (DEEP_BLUE,"[6]","Сертификаты",           "Доп. баллы при поступлении"),
]
DIRS=[(-1,0),(0,-1),(1,0),(-1,0),(0,1),(1,0)]

def scene4(f):
    arr=bg_white_grad(accent=0.7)
    img=Image.fromarray(arr).convert("RGBA")
    bg_soft_grid(img,0.04)
    _PARTS.draw(img,f,0.12)
    d=ImageDraw.Draw(img,"RGBA")

    # ── Vertical layout ──
    COLS=3; CW,CH=500,178; HG=36; VG=28
    TITLE_H = 62
    UL_H    = 16
    ROWS_H  = 2*CH + VG
    BLOCK_H = TITLE_H + UL_H + ROWS_H
    top     = (H - BLOCK_H) // 2
    title_cy= top + TITLE_H//2
    ul_y    = top + TITLE_H + 2
    fy      = top + TITLE_H + UL_H
    total_w = COLS*CW+(COLS-1)*HG
    fx      = (W - total_w)//2

    ha=int(255*clamp(remap(f,286,305)))
    if ha:
        text_c(d,"Что входит в ДМШ?",title_cy,50,DEEP_BLUE,"sb",ha)
        uw=tw(d,"Что входит в ДМШ?",50,"sb")
        d.rectangle([(W-uw)//2,ul_y,(W+uw)//2,ul_y+4],fill=(*PURPLE,ha))

    for i,(col,badge,title_,sub) in enumerate(FEATURES):
        c=i%COLS; r=i//COLS
        df=285+c*12+r*22
        ct=spring(remap(f,df,df+55))
        if ct<=0: continue
        dx,dy=DIRS[i]
        bx=fx+c*(CW+HG); by=fy+r*(CH+VG)
        off=int((1-ct)*130)
        cx_=bx+dx*off; cy_=by+dy*off
        ai=int(255*clamp(ct))

        for g in range(16,0,-4):
            d.rounded_rectangle([cx_+g//2,cy_+g//2,cx_+CW+g//2,cy_+CH+g//2],
                                 radius=18,fill=(*col,int(12*(1-g/16)*ct)))
        light_card(img,cx_,cy_,CW,CH,col,ct)
        d2=ImageDraw.Draw(img,"RGBA")

        bw2=tw(d2,badge,18,"mb")+18
        d2.rounded_rectangle([cx_+16,cy_+16,cx_+16+bw2,cy_+40],
                              radius=8,fill=(*col,int(200*ct)))
        d2.text((cx_+25,cy_+19),badge,font=F(18,"mb"),fill=(*WHITE,ai))
        # title — plain, no shadow
        d2.text((cx_+16,cy_+52),title_,font=F(26,"sb"),fill=(*col,ai))
        d2.text((cx_+16,cy_+90),sub,font=F(19,"sr"),fill=(*TEXT_BODY,int(205*ct)))

    return np.array(img.convert("RGB"))

# ═══════════════════════════════════════════════
# SCENE 5  f=375..450   CTA  (no logo)
# ═══════════════════════════════════════════════
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
    _PARTS.draw(img,f,0.18)
    d=ImageDraw.Draw(img,"RGBA")

    # ── LEFT: CTA ──
    la=int(255*clamp(remap(f,376,392)))
    if la:
        lw_=tw(d,"СЛЕДУЮЩИЙ ШАГ",18,"mb")
        d.text((72,192),"СЛЕДУЮЩИЙ ШАГ",font=F(18,"mb"),fill=(*PURPLE,la))
        d.line([(72,218),(72+lw_+60,218)],fill=(*PURPLE_L,la),width=2)

    for i,(word,wy) in enumerate(zip(CTA_WORDS,[258,374,490])):
        ws=spring(remap(f,380+i*12,422+i*12))
        wa=int(255*clamp(remap(f,380+i*12,414+i*12)))
        if wa<=0: continue
        ay=int(wy+(1-ws)*80)
        d.text((72,ay),word,font=F(96,"sb"),fill=(*DEEP_BLUE,wa))

    ul_t=clamp(remap(f,416,434))
    if ul_t:
        uw2=tw(d,CTA_WORDS[-1],96,"sb")
        d.rectangle([72,596,72+int(uw2*ul_t),605],fill=(*PURPLE,255))

    sub_a=int(255*clamp(remap(f,424,440)))
    if sub_a:
        d.text((72,622),"Старт с сентября 2026",
               font=F(28,"sr"),fill=(*TEXT_BODY,sub_a))

    # ── RIGHT: terminal ──
    TW3,TH3=760,420
    tx3=W//2+30+(W//2-30-TW3)//2; ty3=H//2-TH3//2
    ts3=spring(remap(f,378,428))
    tx3_a=int(tx3+(1-ts3)*(TW3+100))
    if ts3>0.02:
        lines3=build_lines(CTA_TERM,418,448,f)
        tmp3=Image.new("RGBA",(TW3,TH3),(0,0,0,0))
        draw_terminal(tmp3,0,0,TW3,TH3,"connect.sh — bash",lines3,frame=f)
        img.paste(tmp3,(tx3_a,ty3),tmp3)

    # URL only — centred, no logo
    url_a=int(255*clamp(remap(f,432,448)))
    if url_a:
        url="futuredoc.minzdrav.gov.ru"
        uw3=tw(d,url,32,"mb"); pill_w=uw3+48
        d.rounded_rectangle([(W-pill_w)//2,H-92,(W+pill_w)//2,H-50],
                             radius=22,fill=(*PURPLE_XL,int(230*url_a/255)))
        text_c(d,url,H-71,32,DEEP_BLUE,"mb",url_a)

    return np.array(img.convert("RGB"))

# ── Scene routing ─────────────────────────────
CUTS=[(75,92,scene1,scene2),(195,212,scene2,scene3),
      (285,302,scene3,scene4),(375,392,scene4,scene5)]

def make_frame(f):
    f=int(clamp(f,0,FRAMES-1))
    for f0,f1,sa,sb in CUTS:
        if f0<=f<f1:
            t=(f-f0)/(f1-f0)
            return fade_blend(sa(f),sb(f),t)
    if f<75:  return scene1(f)
    if f<195: return scene2(f)
    if f<285: return scene3(f)
    if f<375: return scene4(f)
    return scene5(f)

# ── Render ────────────────────────────────────
if __name__=="__main__":
    print("Rendering ДМШ promo v4  (1920×1080 · 30fps · 15s) …")
    clip=VideoClip(lambda t: make_frame(int(t*FPS)), duration=DUR)
    out="/home/user/1111/ДМШ_промо_v4.mp4"
    clip.write_videofile(out,fps=FPS,codec="libx264",
                         preset="fast",ffmpeg_params=["-crf","16"],logger="bar")
    print(f"\nDone → {out}")
