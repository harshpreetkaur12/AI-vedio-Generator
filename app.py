import io
import re
import tempfile
from pathlib import Path

import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ImageOps
from moviepy import (
    ImageClip, CompositeVideoClip, concatenate_videoclips,
    AudioFileClip, CompositeAudioClip, VideoFileClip, afx, vfx
)

try:
    from gtts import gTTS
except Exception:
    gTTS = None


# ------------------------------------------------------------
# LUMIÈRE PROPERTY FILM STUDIO
# Cinematic 9:16 real-estate films from user-supplied photos and walkthrough clips.
# Photo motion is a 2.5D-style pan/zoom effect, not true 3D.
# ------------------------------------------------------------
st.set_page_config(
    page_title="Lumière | Property Film Studio",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="collapsed",
)

BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "output"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

W, H = 720, 1280
FPS = 24
SCENE_SECONDS = 4.8
TRANSITION_SECONDS = 0.75
GOLD = (207, 170, 111, 255)
CREAM = (250, 247, 240, 255)
MUTED = (224, 222, 216, 255)


st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@400;500;600;700;800&display=swap');
:root { --navy:#102d50; --blue:#1d527c; --sky:#dce9f8; --ice:#f4f8fd; --ink:#132a43; --muted:#6d8198; --gold:#e5b64f; }
.stApp { background:linear-gradient(135deg,#d9e7f7 0%,#eef4fb 48%,#d4e3f4 100%); color:var(--ink); }
[data-testid="stHeader"] { background:rgba(218,232,248,.84); }
[data-testid="stSidebar"] { background:#eaf2fb; }
.block-container { max-width:1440px; padding-top:1.4rem; padding-bottom:3rem; }
h1,h2,h3 { font-family:'Manrope',sans-serif !important; color:var(--ink) !important; letter-spacing:-.035em; font-weight:800 !important; }
p, label, input, textarea, button, small { font-family:'DM Sans',sans-serif; }
.eyebrow { color:#b3d5f8; font-size:.73rem; letter-spacing:.18em; text-transform:uppercase; font-weight:700; }
.hero { position:relative; overflow:hidden; border:1px solid rgba(255,255,255,.24); border-radius:30px; padding:2.25rem 2.4rem; background:linear-gradient(118deg,#102d50 0%,#16466f 56%,#28789a 100%); box-shadow:0 24px 55px rgba(27,62,99,.22); margin-bottom:1.35rem; color:#fff; }
.hero:after { content:''; position:absolute; width:340px; height:340px; right:-100px; top:-150px; border-radius:50%; background:rgba(255,255,255,.08); border:1px solid rgba(255,255,255,.1); }
.hero h1 { color:#fff !important; font-size:clamp(2.1rem,4vw,3.7rem); line-height:1.05; margin:.7rem 0 .75rem; position:relative; z-index:1; }
.hero p { color:#d7e6f6; max-width:760px; font-size:1rem; line-height:1.7; position:relative; z-index:1; }
.pill { display:inline-block; border:1px solid rgba(255,255,255,.28); border-radius:99px; padding:.38rem .75rem; color:#eff7ff; font-size:.72rem; letter-spacing:.05em; margin-right:.4rem; background:rgba(255,255,255,.08); position:relative; z-index:1; }
div[data-testid="stForm"] { border:1px solid rgba(255,255,255,.85); border-radius:24px; padding:1.3rem 1.3rem .9rem; background:rgba(255,255,255,.76); box-shadow:0 15px 40px rgba(47,81,119,.11); backdrop-filter:blur(18px); }
div[data-testid="stTextInput"] input, div[data-testid="stTextArea"] textarea, div[data-testid="stSelectbox"] div[data-baseweb="select"] { background:#f8fbff; color:#17324f; border:1px solid #d4e1f0; border-radius:13px; }
div[data-testid="stTextInput"] input:focus, div[data-testid="stTextArea"] textarea:focus { border-color:#4b8fc1; box-shadow:0 0 0 2px rgba(75,143,193,.13); }
div[data-testid="stFileUploader"] section { background:rgba(242,248,255,.92); border:1px dashed #9ab9d8; border-radius:16px; }
div[data-testid="stFileUploader"] small, [data-testid="stCaptionContainer"] { color:#617a94; }
div.stButton > button, div.stFormSubmitButton > button, div.stDownloadButton > button { border-radius:13px; min-height:2.85rem; font-weight:700; border:1px solid #1c5079; transition:all .2s ease; }
div.stFormSubmitButton > button, div.stDownloadButton > button { background:linear-gradient(105deg,#153d65,#2476a1); color:white; box-shadow:0 8px 18px rgba(25,76,119,.18); }
div.stButton > button:hover, div.stFormSubmitButton > button:hover, div.stDownloadButton > button:hover { border-color:#e6b94f; color:white; background:linear-gradient(105deg,#1a4b77,#2b88b3); transform:translateY(-1px); }
[data-testid="stMetric"] { background:rgba(255,255,255,.78); border:1px solid rgba(255,255,255,.9); padding:1rem; border-radius:17px; box-shadow:0 8px 22px rgba(47,81,119,.08); }
[data-testid="stMetricLabel"] { color:#617a94; }
[data-testid="stMetricValue"] { color:#153b61; }
[data-testid="stExpander"] { background:rgba(255,255,255,.65); border:1px solid #d6e4f3; border-radius:16px; }
[data-testid="stAlert"] { border-radius:13px; }
hr { border-color:#cfdeed; }
footer { visibility:hidden; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
  <div class="eyebrow">✦ Property film studio · made for first impressions</div>
  <h1>Every home has a story.<br>Make yours feel cinematic.</h1>
  <p>Mix real walkthrough footage with AI-generated clips you create in a free/low-cost video tool, then export polished vertical and landscape property films.</p>
  <span class="pill">HOME TOUR</span><span class="pill">VOICE + MUSIC</span><span class="pill">MP4 STUDIO</span>
</div>
""", unsafe_allow_html=True)

with st.container():
    st.markdown("### Create your property film")
    st.caption("Mix real walkthrough clips with AI-generated image-to-video clips (upload them like any other video). Photos receive a local pan/zoom effect; no paid API is called by this app.")

def clean_filename(value):
    return re.sub(r"[^a-zA-Z0-9_-]+", "_", value.strip()).strip("_")[:60] or "property_film"

def get_font(size, bold=False, serif=False):
    if serif:
        candidates = [
            "C:/Windows/Fonts/georgiab.ttf" if bold else "C:/Windows/Fonts/georgia.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
        ]
    else:
        candidates = [
            "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
            "C:/Windows/Fonts/segoeuib.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        ]
    for candidate in candidates:
        if Path(candidate).exists():
            try:
                return ImageFont.truetype(candidate, size)
            except OSError:
                pass
    return ImageFont.load_default()

def wrap_text(draw, text, font, max_width):
    lines, current = [], ""
    for word in str(text).split():
        candidate = f"{current} {word}".strip()
        if draw.textbbox((0, 0), candidate, font=font)[2] <= max_width:
            current = candidate
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines or [""]

def cover_image(image_bytes):
    with Image.open(io.BytesIO(image_bytes)) as im:
        im = ImageOps.exif_transpose(im).convert("RGB")
    return ImageOps.fit(im, (W, H), method=Image.Resampling.LANCZOS, centering=(0.5, 0.5))

def add_bottom_gradient(image):
    rgba = image.convert("RGBA")
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    pixels = overlay.load()
    for y in range(H):
        # Subtle lower-third gradient, preserving the property photo.
        t = max(0, (y - 250) / (H - 250))
        alpha = int(10 + 190 * (t ** 1.8))
        for x in range(W):
            pixels[x, y] = (7, 12, 9, alpha)
    return Image.alpha_composite(rgba, overlay)

def draw_tracking(draw, xy, text, font, fill, tracking=2):
    x, y = xy
    for char in text:
        draw.text((x, y), char, font=font, fill=fill)
        x += draw.textbbox((0, 0), char, font=font)[2] + tracking

def make_scene(photo_bytes, title, subtitle, idx, total, name, location, price, kind):
    image = add_bottom_gradient(cover_image(photo_bytes))
    draw = ImageDraw.Draw(image)
    # Thin inset frame and small editorial header.
    draw.rounded_rectangle((25, 25, W - 25, H - 25), radius=15, outline=(255,255,255,95), width=1)
    draw_tracking(draw, (42, 48), "L U M I È R E   /   PROPERTY FILMS", get_font(12, True), GOLD, 1)
    counter = f"{idx:02d}/{total:02d}"
    cf = get_font(12, True)
    draw.text((W - 42 - draw.textbbox((0,0), counter, font=cf)[2], 48), counter, font=cf, fill=CREAM)

    if kind == "opening":
        draw_tracking(draw, (42, 835), "A PLACE TO CALL HOME", get_font(13, True), GOLD, 2)
        title_font, sub_font, title_y = get_font(38, serif=True), get_font(18), 870
    elif kind == "closing":
        draw_tracking(draw, (42, 835), "YOUR NEXT CHAPTER STARTS HERE", get_font(12, True), GOLD, 1)
        title_font, sub_font, title_y = get_font(34, serif=True), get_font(18), 870
    else:
        draw_tracking(draw, (42, 835), "STEP INSIDE", get_font(12, True), GOLD, 2)
        title_font, sub_font, title_y = get_font(32, serif=True), get_font(17), 870

    title_lines = wrap_text(draw, title, title_font, W - 85)[:3]
    y = title_y
    for line in title_lines:
        draw.text((60, y), line, font=title_font, fill=CREAM, stroke_width=0)
        y += 44
    y += 4
    for line in wrap_text(draw, subtitle, sub_font, W - 85)[:3]:
        draw.text((63, y), line, font=sub_font, fill=(232, 232, 224, 255))
        y += 25

    # Restrained footer with price/location; no invented claims.
    draw.rounded_rectangle((42, 1175, 100, 1179), radius=2, fill=GOLD)
    footer = "  ·  ".join(x for x in [location.strip(), price.strip()] if x)
    draw.text((42, 1192), footer[:62], font=get_font(12, True), fill=CREAM)
    return image.convert("RGB")

def build_scene_plan(name, location, price, property_type, features, contact, count):
    feature_list = [item.strip() for item in features.split(",") if item.strip()]
    plan = [(name, f"{property_type}  ·  {location}", "opening")]
    middle_count = max(0, count - 2)
    for i in range(middle_count):
        if feature_list:
            title = feature_list[i % len(feature_list)]
            subtitle = f"A closer look at {name}"
        else:
            title = ["Space to unwind", "Thoughtfully presented", "Details that feel like home"][i % 3]
            subtitle = f"{property_type} in {location}"
        plan.append((title, subtitle, "photo"))
    plan.append(("Arrange your private viewing", contact, "closing"))
    return plan

def make_motion_clip(frame_path, duration, index):
    # 1.08x overscan creates a smooth Ken Burns camera move without edge gaps.
    scale = 1.09
    enlarged = ImageClip(str(frame_path)).resized(height=int(H * scale)).with_duration(duration)
    max_x, max_y = max(0, enlarged.w - W), max(0, enlarged.h - H)
    mode = index % 4
    def position(t):
        p = min(1.0, max(0.0, t / max(duration, .001)))
        if mode == 0:
            return (-max_x * (.15 + .7*p), -max_y * (.45 - .25*p))
        if mode == 1:
            return (-max_x * (.85 - .7*p), -max_y * (.35 + .25*p))
        if mode == 2:
            return (-max_x * (.5 - .25*p), -max_y * (.8 - .5*p))
        return (-max_x * (.25 + .5*p), -max_y * (.2 + .5*p))
    return CompositeVideoClip([enlarged.with_position(position)], size=(W,H)).with_duration(duration)

def make_video_overlay(title, subtitle, idx, total, name, location, price, kind):
    """Transparent lower-third/title graphics for live walkthrough footage."""
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    draw_tracking(draw, (42, 48), "L U M I È R E   /   PROPERTY FILMS", get_font(12, True), GOLD, 1)
    counter = f"{idx:02d}/{total:02d}"
    cf = get_font(12, True)
    draw.text((W - 42 - draw.textbbox((0, 0), counter, font=cf)[2], 48), counter, font=cf, fill=CREAM)
    # Lower-third translucent panel, leaving most of the room visible.
    panel = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    pd = ImageDraw.Draw(panel)
    pd.rounded_rectangle((24, 825, W - 24, 1228), radius=24, fill=(6, 16, 24, 150), outline=(255,255,255,45), width=1)
    overlay = Image.alpha_composite(overlay, panel)
    draw = ImageDraw.Draw(overlay)
    if kind == "opening":
        label = "A PLACE TO CALL HOME"
    elif kind == "closing":
        label = "YOUR NEXT CHAPTER STARTS HERE"
    else:
        label = "STEP INSIDE"
    draw_tracking(draw, (46, 858), label, get_font(12, True), GOLD, 1)
    title_font = get_font(32, serif=True)
    sub_font = get_font(16)
    y = 892
    for line in wrap_text(draw, title, title_font, W - 95)[:3]:
        draw.text((46, y), line, font=title_font, fill=CREAM)
        y += 40
    y += 4
    for line in wrap_text(draw, subtitle, sub_font, W - 95)[:2]:
        draw.text((48, y), line, font=sub_font, fill=(232, 238, 244, 255))
        y += 23
    footer = "  ·  ".join(x for x in [location.strip(), price.strip()] if x)
    draw.text((46, 1187), footer[:62], font=get_font(11, True), fill=CREAM)
    return overlay

def fit_video_clip(clip, duration):
    """Fit a real walkthrough clip into the vertical canvas without stretching."""
    clip = clip.without_audio()
    # Scale to cover the portrait canvas, then crop the center.
    scale = max(W / clip.w, H / clip.h)
    clip = clip.resized(scale)
    x1 = max(0, (clip.w - W) / 2)
    y1 = max(0, (clip.h - H) / 2)
    clip = clip.cropped(x1=x1, y1=y1, x2=x1 + W, y2=y1 + H)
    clip = clip.subclipped(0, min(duration, clip.duration))
    return clip.with_duration(min(duration, clip.duration))

def landscape_scene(photo_bytes, title, subtitle, idx, total, name, location, price, kind, width=1280, height=720):
    """Landscape editorial frame with readable lower-third typography."""
    with Image.open(io.BytesIO(photo_bytes)) as im:
        im = ImageOps.exif_transpose(im).convert("RGB")
    image = ImageOps.fit(im, (width, height), method=Image.Resampling.LANCZOS, centering=(0.5, 0.5)).convert("RGBA")
    # Restrained bottom gradient for contrast without obscuring the room.
    grad = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    px = grad.load()
    for y in range(height):
        t = max(0, (y - height * .43) / (height * .57))
        alpha = int(8 + 175 * (t ** 1.7))
        for x in range(width):
            px[x, y] = (7, 12, 18, alpha)
    image = Image.alpha_composite(image, grad)
    draw = ImageDraw.Draw(image)
    margin = int(width * .035)
    draw.rounded_rectangle((margin, margin, width-margin, height-margin), radius=12, outline=(255,255,255,90), width=1)
    scale = width / 1280
    small = get_font(max(10, int(15*scale)), True)
    title_font = get_font(max(24, int(43*scale)), serif=True)
    sub_font = get_font(max(13, int(20*scale)))
    draw_tracking(draw, (margin+18, margin+15), "L U M I È R E  /  PROPERTY FILMS", small, GOLD, max(1, int(scale)))
    counter = f"{idx:02d}/{total:02d}"
    draw.text((width-margin-70, margin+15), counter, font=small, fill=CREAM)
    label = "A PLACE TO CALL HOME" if kind == "opening" else ("YOUR NEXT CHAPTER STARTS HERE" if kind == "closing" else "STEP INSIDE")
    base_y = int(height * .64)
    draw_tracking(draw, (margin+22, base_y), label, small, GOLD, max(1, int(scale)))
    y = base_y + int(30*scale)
    for line in wrap_text(draw, title, title_font, int(width*.68))[:2]:
        draw.text((margin+20, y), line, font=title_font, fill=CREAM)
        y += int(49*scale)
    y += 2
    for line in wrap_text(draw, subtitle, sub_font, int(width*.68))[:2]:
        draw.text((margin+22, y), line, font=sub_font, fill=(232,238,244,255))
        y += int(26*scale)
    footer = "  ·  ".join(x for x in [location.strip(), price.strip()] if x)
    draw.text((margin+22, height-margin-28), footer[:100], font=small, fill=CREAM)
    return image.convert("RGB")

def motion_clip_for_size(frame_path, duration, index, width, height):
    scale = 1.08
    enlarged = ImageClip(str(frame_path)).resized(height=int(height * scale)).with_duration(duration)
    # Ensure overscan covers both dimensions for landscape and portrait.
    if enlarged.w < width:
        enlarged = enlarged.resized(width=int(width * scale))
    max_x, max_y = max(0, enlarged.w-width), max(0, enlarged.h-height)
    mode = index % 4
    def position(t):
        progress = min(1.0, max(0.0, t/max(duration, .001)))
        if mode == 0: return (-max_x*.15 - max_x*.7*progress, -max_y*.5)
        if mode == 1: return (-max_x*.85 + max_x*.7*progress, -max_y*.35)
        if mode == 2: return (-max_x*.5 + max_x*.25*progress, -max_y*.8 + max_y*.5*progress)
        return (-max_x*.25 - max_x*.5*progress, -max_y*.2 - max_y*.5*progress)
    return CompositeVideoClip([enlarged.with_position(position)], size=(width,height)).with_duration(duration)

def landscape_video_fit(clip, duration, width=1280, height=720):
    clip = clip.without_audio()
    scale = max(width/clip.w, height/clip.h)
    clip = clip.resized(scale)
    x1, y1 = max(0, (clip.w-width)/2), max(0, (clip.h-height)/2)
    clip = clip.cropped(x1=x1, y1=y1, x2=x1+width, y2=y1+height)
    return clip.subclipped(0, min(duration, clip.duration)).with_duration(min(duration, clip.duration))

def landscape_overlay(title, subtitle, idx, total, location, price, kind, width=1280, height=720):
    overlay = Image.new("RGBA", (width, height), (0,0,0,0))
    draw = ImageDraw.Draw(overlay)
    margin = int(width*.035); scale = width/1280
    small = get_font(max(10,int(15*scale)), True)
    title_font = get_font(max(24,int(43*scale)), serif=True)
    sub_font = get_font(max(13,int(20*scale)))
    draw_tracking(draw,(margin+18,margin+15),"L U M I È R E  /  PROPERTY FILMS",small,GOLD,max(1,int(scale)))
    draw.text((width-margin-70,margin+15),f"{idx:02d}/{total:02d}",font=small,fill=CREAM)
    panel=Image.new("RGBA",(width,height),(0,0,0,0)); pd=ImageDraw.Draw(panel)
    pd.rounded_rectangle((margin,height*.60,width-margin,height-margin),radius=18,fill=(6,16,24,145),outline=(255,255,255,40),width=1)
    overlay=Image.alpha_composite(overlay,panel); draw=ImageDraw.Draw(overlay)
    label="A PLACE TO CALL HOME" if kind=="opening" else ("YOUR NEXT CHAPTER STARTS HERE" if kind=="closing" else "STEP INSIDE")
    y=int(height*.64); draw_tracking(draw,(margin+22,y),label,small,GOLD,max(1,int(scale))); y+=int(30*scale)
    for line in wrap_text(draw,title,title_font,int(width*.68))[:2]:
        draw.text((margin+20,y),line,font=title_font,fill=CREAM); y+=int(49*scale)
    for line in wrap_text(draw,subtitle,sub_font,int(width*.68))[:2]:
        draw.text((margin+22,y),line,font=sub_font,fill=(232,238,244,255)); y+=int(26*scale)
    footer="  ·  ".join(x for x in [location.strip(),price.strip()] if x)
    draw.text((margin+22,height-margin-28),footer[:100],font=small,fill=CREAM)
    return overlay

def render_video(media, plan, name, location, price, narration_text, voice_language, music_upload, add_voice, music_volume, format_key="portrait"):
    width, height = (720, 1280) if format_key == "portrait" else (1280, 720)
    suffix = "vertical_9x16" if format_key == "portrait" else "landscape_16x9"
    output = OUTPUT_DIR / f"{clean_filename(name)}_{suffix}.mp4"
    clips, source_clips = [], []
    temp_dir_obj = tempfile.TemporaryDirectory()
    temp_dir = Path(temp_dir_obj.name)
    final = None
    voice_clip = music_clip = None
    try:
        for i, (asset, scene) in enumerate(zip(media, plan)):
            title, subtitle, kind = scene
            ext = Path(asset.name).suffix.lower()
            if ext in {".mp4", ".mov", ".m4v", ".avi", ".webm"}:
                source_path = temp_dir / f"source_{i:02d}{ext}"
                source_path.write_bytes(asset.getvalue())
                raw_clip = VideoFileClip(str(source_path)); source_clips.append(raw_clip)
                clip = fit_video_clip(raw_clip, SCENE_SECONDS) if format_key == "portrait" else landscape_video_fit(raw_clip, SCENE_SECONDS, width, height)
                overlay = (make_video_overlay(title, subtitle, i+1, len(media), name, location, price, kind)
                           if format_key == "portrait" else landscape_overlay(title, subtitle, i+1, len(media), location, price, kind, width, height))
                overlay_path = temp_dir / f"overlay_{i:02d}.png"; overlay.save(overlay_path, "PNG")
                overlay_clip = ImageClip(str(overlay_path)).with_duration(clip.duration)
                clip = CompositeVideoClip([clip, overlay_clip], size=(width,height)).with_duration(clip.duration)
            else:
                frame = (make_scene(asset.getvalue(), title, subtitle, i+1, len(media), name, location, price, kind)
                         if format_key == "portrait" else landscape_scene(asset.getvalue(), title, subtitle, i+1, len(media), name, location, price, kind, width, height))
                frame_path = temp_dir / f"scene_{i:02d}.jpg"; frame.save(frame_path,"JPEG",quality=94,optimize=True)
                clip = make_motion_clip(frame_path, SCENE_SECONDS, i) if format_key == "portrait" else motion_clip_for_size(frame_path, SCENE_SECONDS, i, width, height)
            if i > 0: clip = clip.with_effects([vfx.CrossFadeIn(TRANSITION_SECONDS)])
            clips.append(clip)
        final = concatenate_videoclips(clips, method="compose", padding=-TRANSITION_SECONDS)
        audio_layers=[]
        if add_voice and gTTS is not None and narration_text.strip():
            voice_path=temp_dir/"voiceover.mp3"; gTTS(text=narration_text,lang=voice_language,slow=False).save(str(voice_path))
            voice_clip=AudioFileClip(str(voice_path))
            if voice_clip.duration>final.duration: voice_clip=voice_clip.subclipped(0,final.duration)
            audio_layers.append(voice_clip.with_start(0).with_volume_scaled(1.0))
        if music_upload is not None:
            music_path=temp_dir/("background_music"+Path(music_upload.name).suffix); music_path.write_bytes(music_upload.getvalue())
            music_clip=AudioFileClip(str(music_path))
            if music_clip.duration<final.duration: music_clip=music_clip.with_effects([afx.AudioLoop(duration=final.duration)])
            else: music_clip=music_clip.subclipped(0,final.duration)
            music_clip=music_clip.with_volume_scaled(music_volume)
            try: music_clip=music_clip.with_effects([afx.AudioFadeOut(2.0)])
            except Exception: pass
            audio_layers.append(music_clip)
        if audio_layers: final=final.with_audio(CompositeAudioClip(audio_layers).with_duration(final.duration))
        final.write_videofile(str(output),fps=FPS,codec="libx264",audio_codec="aac",preset="medium",bitrate="9000k",threads=4,logger="bar")
        return output
    finally:
        if final is not None:
            try: final.close()
            except Exception: pass
        for clip in clips + source_clips:
            try: clip.close()
            except Exception: pass
        for clip in (voice_clip,music_clip):
            if clip is not None:
                try: clip.close()
                except Exception: pass
        temp_dir_obj.cleanup()



with st.form("film_form", clear_on_submit=False):
    st.markdown('<div class="eyebrow">01 / Property details</div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        property_name = st.text_input("Property / listing name *", placeholder="The Willow Residence")
        location = st.text_input("Location *", placeholder="Sector  Chandigarh")
        price = st.text_input("Asking price", placeholder="₹1.25 crore")
        property_type = st.selectbox("Property type", ["Luxury Villa", "Apartment", "2-BHK Apartment", "3-BHK Apartment", "Independent House", "Penthouse", "Commercial Property", "Plot", "Other"])
    with c2:
        contact = st.text_input("Contact / closing call to action *", placeholder="Contact us to schedule a private viewing")
        features = st.text_area("Verified features (comma-separated)", placeholder="Sunlit living room, modular kitchen, private balcony", height=115)
        photo_order = st.caption("Tip: upload photos in the order you want viewers to experience the home.")
    st.markdown('<div class="eyebrow">02 / Visuals & sound</div>', unsafe_allow_html=True)
    photos = st.file_uploader("Photos + real footage + AI-generated clips · upload 4–8 files *", type=["jpg","jpeg","png","mp4","mov","m4v","webm","avi"], accept_multiple_files=True)
    output_formats = st.multiselect("Export formats", ["Vertical 9:16", "Landscape 16:9"], default=["Vertical 9:16", "Landscape 16:9"])
    st.caption("For AI motion: generate a short image-to-video clip in your preferred tool, download the MP4, then upload it here beside your real footage. This keeps API costs at $0 inside this app.")
    a1, a2 = st.columns(2)
    with a1:
        add_voice = st.checkbox("Generate AI voice narration (requires internet)", value=True)
        voice_language = st.selectbox("Narration language", ["English", "Hindi", "French", "Spanish"], index=0)
    with a2:
        music_upload = st.file_uploader("Optional background music (MP3 / WAV / M4A)", type=["mp3","wav","m4a"])
        music_volume = st.slider("Music level", min_value=0.05, max_value=0.35, value=0.12, step=0.01)
    submitted = st.form_submit_button("✦  Create cinematic property film", type="primary", use_container_width=True)

if submitted:
    errors = []
    if not property_name.strip(): errors.append("Enter a property or listing name.")
    if not location.strip(): errors.append("Enter the property location.")
    if not contact.strip(): errors.append("Add a contact detail or call to action.")
    if not photos or not 4 <= len(photos) <= 8: errors.append("Upload between 4 and 8 property photos and/or video clips.")
    if not output_formats: errors.append("Choose at least one export format.")
    if add_voice and gTTS is None: errors.append("Voice narration needs gTTS. Install it with: pip install gTTS")
    if errors:
        for err in errors: st.error(err)
    else:
        try:
            for asset in photos:
                asset.seek(0)
                ext = Path(asset.name).suffix.lower()
                if ext in {".jpg", ".jpeg", ".png"}:
                    with Image.open(asset) as im: im.verify()
                elif ext not in {".mp4", ".mov", ".m4v", ".webm", ".avi"}:
                    raise ValueError(f"Unsupported file type: {asset.name}")
                asset.seek(0)
            st.session_state["film_inputs"] = {
                "name": property_name.strip(), "location": location.strip(),
                "price": price.strip(), "type": property_type, "features": features,
                "contact": contact.strip(), "voice": add_voice,
                "language": {"English":"en", "Hindi":"hi", "French":"fr", "Spanish":"es"}[voice_language],
                "music": music_upload, "volume": music_volume, "photos": photos,
                "formats": output_formats
            }
        except Exception as exc:
            st.error(f"One of the uploaded files could not be read: {exc}")

if "film_inputs" in st.session_state:
    data = st.session_state["film_inputs"]
    st.divider()
    st.markdown("### Your film setup")
    m1, m2, m3 = st.columns(3)
    m1.metric("Visual assets", len(data["photos"]))
    m2.metric("Approx. duration", f"{max(1, len(data['photos'])) * SCENE_SECONDS - (len(data['photos'])-1)*TRANSITION_SECONDS:.0f} sec")
    m3.metric("Formats", ", ".join("9:16" if f == "Vertical 9:16" else "16:9" for f in data["formats"]))
    with st.expander("Review the narration script", expanded=True):
        feature_list = [x.strip() for x in data["features"].split(",") if x.strip()]
        script_parts = [
            f"Welcome to {data['name']}, a {data['type'].lower()} located in {data['location']}."
        ]
        if feature_list:
            script_parts.append("As we step inside, explore " + ", ".join(feature_list) + ".")
        if data["price"]:
            script_parts.append(f"The asking price is {data['price']}.")
        script_parts.append(data["contact"] + ".")
        narration_text = " ".join(script_parts)
        st.write(narration_text)
    if st.button("Render selected format(s)", type="primary", use_container_width=True):
        try:
            plan = build_scene_plan(data["name"], data["location"], data["price"], data["type"], data["features"], data["contact"], len(data["photos"]))
            outputs = []
            for label, key in [("Vertical 9:16", "portrait"), ("Landscape 16:9", "landscape")]:
                if label not in data["formats"]: continue
                with st.spinner(f"Rendering {label} film… this may take a few minutes."):
                    outputs.append(render_video(data["photos"], plan, data["name"], data["location"], data["price"], narration_text, data["language"], data["music"], data["voice"], data["volume"], key))
            st.session_state["film_outputs"] = [str(x) for x in outputs]
            st.success(f"Finished {len(outputs)} export(s).")
        except Exception as exc:
            st.error("The film could not be rendered. Check the error details below.")
            st.exception(exc)

if st.session_state.get("film_outputs"):
    existing_outputs = [Path(x) for x in st.session_state["film_outputs"] if Path(x).is_file()]
    if existing_outputs:
        st.divider(); st.markdown("### Film previews & downloads")
        for result_path in existing_outputs:
            st.markdown(f"**{result_path.stem.replace('_', ' ').title()}**")
            st.video(result_path.read_bytes())
            st.download_button(f"Download {result_path.name}", data=result_path.read_bytes(), file_name=result_path.name, mime="video/mp4", key=f"download_{result_path.name}", use_container_width=True)
        st.caption("Real and AI-generated uploaded clips retain their camera motion; still photos receive a local pan/zoom effect. The app does not generate AI video or call a paid API itself.")

with st.expander("Troubleshooting & quality notes"):
    st.markdown("""
- **Voice narration:** uses gTTS and needs an internet connection when rendering.
- **Background music:** upload music you own or are licensed to use. Keep the level low so narration remains clear.
- **FFmpeg:** MoviePy relies on FFmpeg for MP4 export. If rendering fails on Windows, install FFmpeg and add its `bin` folder to PATH.
- **AI-generated motion on a budget:** create short image-to-video clips in a free/low-cost AI video tool, download the MP4, and upload it with your real footage. This app does not call a paid generation API, so it cannot charge you for generation.
- **True 3D:** photo pan/zoom is not reconstructed room geometry. AI-generated clips can distort architectural details; inspect them before using them in a listing.
- **Aspect ratios:** vertical output is 720×1280; landscape output is 1280×720. Source footage is center-cropped to fill the selected frame, so check framing for wide or tall source clips.
- **Photo order matters:** place the exterior first, then the main living area, kitchen, bedrooms, detail shots and a final attractive view.
""")
