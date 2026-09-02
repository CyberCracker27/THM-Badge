import json
import os
import io
import math
import requests
from PIL import Image, ImageDraw, ImageFont

# ─── 1. Vector Icon Drawing Functions ───
def draw_trophy(draw, x, y, color=(140, 155, 175)):
    # Cup body
    draw.polygon([(x + 2, y + 2), (x + 10, y + 2), (x + 8, y + 9), (x + 4, y + 9)], fill=color)
    # Stem & base
    draw.line([(x + 6, y + 9), (x + 6, y + 12)], fill=color, width=2)
    draw.line([(x + 3, y + 12), (x + 9, y + 12)], fill=color, width=2)
    # Handles
    draw.arc([(x, y + 2), (x + 5, y + 7)], 90, 270, fill=color, width=1)
    draw.arc([(x + 7, y + 2), (x + 12, y + 7)], 270, 90, fill=color, width=1)

def draw_fire(draw, x, y, color=(140, 215, 45)):
    draw.ellipse([(x + 1, y + 2), (x + 9, y + 11)], fill=color)
    draw.polygon([(x + 2, y + 5), (x + 5, y), (x + 8, y + 5)], fill=color)
    draw.ellipse([(x + 3, y + 5), (x + 7, y + 9)], fill=(13, 17, 23))

def draw_rosette(draw, x, y, color=(185, 60, 235)):
    draw.ellipse([(x + 1, y), (x + 9, y + 8)], fill=color)
    draw.ellipse([(x + 3, y + 2), (x + 7, y + 6)], fill=(13, 17, 23))
    draw.polygon([(x + 3, y + 7), (x + 1, y + 12), (x + 4, y + 10)], fill=color)
    draw.polygon([(x + 7, y + 7), (x + 9, y + 12), (x + 6, y + 10)], fill=color)

def draw_door(draw, x, y, color=(70, 130, 245)):
    draw.rounded_rectangle([(x + 1, y), (x + 9, y + 11)], radius=2, fill=color)
    draw.rectangle([(x, y + 10), (x + 10, y + 12)], fill=color)
    draw.point((x + 3, y + 6), fill=(13, 17, 23))

def draw_thm_logo(draw, x, y):
    # Cloud shapes
    draw.arc([(x, y + 2), (x + 14, y + 14)], 160, 360, fill=(255, 255, 255), width=2)
    draw.arc([(x + 10, y - 2), (x + 24, y + 14)], 190, 360, fill=(255, 255, 255), width=2)
    draw.arc([(x + 18, y + 4), (x + 28, y + 14)], 260, 60, fill=(255, 255, 255), width=2)
    draw.line([(x + 2, y + 14), (x + 26, y + 14)], fill=(255, 255, 255), width=2)

    # Binary bits below cloud
    dots = [(2, 17), (5, 17), (8, 17), (3, 20), (6, 20), (2, 23), (7, 23), (9, 23)]
    for dx, dy in dots:
        draw.rectangle([(x + dx, y + dy), (x + dx + 1, y + dy + 1)], fill=(220, 230, 240))

# ─── 2. Download and Cache Profile Avatar ───
def download_avatar(avatar_url):
    os.makedirs('docs', exist_ok=True)
    avatar_path = os.path.join('docs', 'avatar.jpg')
    
    if not avatar_url:
        return None

    try:
        res = requests.get(avatar_url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
        if res.status_code == 200:
            with open(avatar_path, 'wb') as f:
                f.write(res.content)
            print(f"✅ Avatar saved to {avatar_path}")
            return Image.open(io.BytesIO(res.content)).convert('RGBA')
    except Exception as e:
        print(f"⚠️ Failed to download avatar: {e}")

    if os.path.exists(avatar_path):
        return Image.open(avatar_path).convert('RGBA')
    return None

# ─── 3. Main Badge Drawing ───
def draw_badge():
    with open('data.json', 'r') as f:
        data = json.load(f)

    profile = data.get('data', {})

    username = profile.get('username', 'User')
    raw_id = profile.get('_id', '')
    user_id = raw_id[0] if raw_id else '6'
    badgesNumber = profile.get('badgesNumber', 0)
    rooms = profile.get('completedRoomsNumber', 0)
    rank = profile.get('rank', 'N/A')
    streak = profile.get('streak', 0)
    avatar_url = profile.get('avatar', '')

    # Fetch avatar & save to docs/avatar.jpg
    avatar_img = download_avatar(avatar_url)

    # Exact Canvas Dimensions
    width, height = 480, 110
    radius = 16

    card = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(card)

    # Background card
    draw.rounded_rectangle(
        [(0, 0), (width - 1, height - 1)],
        radius=radius,
        fill=(13, 17, 23, 255),
        outline=(48, 54, 61, 255),
        width=1
    )

    # Wave graphic overlay on the right side
    wave_overlay = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    wave_draw = ImageDraw.Draw(wave_overlay)
    for i in range(16):
        pts = []
        for x in range(240, width):
            y = int(52 + 18 * math.sin((x + i * 16) / 38.0) + (x - 240) * 0.12)
            pts.append((x, y))
        wave_draw.line(pts, fill=(46, 160, 67, 18), width=1)
    card = Image.alpha_composite(card, wave_overlay)
    draw = ImageDraw.Draw(card)

    # Fonts
    font_bold = font_regular = font_small = None
    for p in [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "C:\\Windows\\Fonts\\segoeuib.ttf",
        "C:\\Windows\\Fonts\\segoeui.ttf"
    ]:
        if os.path.exists(p):
            try:
                font_bold = ImageFont.truetype(p, 17)
                font_regular = ImageFont.truetype(p, 13)
                font_small = ImageFont.truetype(p, 10)
                break
            except Exception:
                continue

    if not font_bold:
        font_bold = font_regular = font_small = ImageFont.load_default()

    # Circular Avatar
    avatar_size = 72
    avatar_x, avatar_y = 18, 19

    if not avatar_img:
        avatar_img = Image.new('RGBA', (avatar_size, avatar_size), (35, 40, 50, 255))

    avatar_img = avatar_img.resize((avatar_size, avatar_size), Image.Resampling.LANCZOS)
    mask = Image.new('L', (avatar_size, avatar_size), 0)
    ImageDraw.Draw(mask).ellipse([(0, 0), (avatar_size, avatar_size)], fill=255)
    card.paste(avatar_img, (avatar_x, avatar_y), mask)

    # Green accent ring around avatar
    draw.ellipse(
        [(avatar_x - 3, avatar_y - 3), (avatar_x + avatar_size + 2, avatar_y + avatar_size + 2)],
        outline=(46, 160, 67, 255),
        width=2
    )

    # Header: Username + Lightning Bolt + [0x...]
    text_x = 108
    draw.text((text_x, 18), username, fill=(255, 255, 255), font=font_bold)
    name_w = font_bold.getbbox(username)[2] - font_bold.getbbox(username)[0]

    bolt_x = text_x + name_w + 8
    draw.polygon(
        [(bolt_x + 4, 19), (bolt_x, 26), (bolt_x + 3, 26), (bolt_x + 1, 32), (bolt_x + 7, 24), (bolt_x + 4, 24)],
        fill=(245, 158, 11)
    )
    draw.text((bolt_x + 13, 18), f"[0x{user_id}]", fill=(190, 200, 215), font=font_bold)

    # Inline Statistics Row
    stat_y = 51
    curr_x = text_x

    # Trophy
    draw_trophy(draw, curr_x, stat_y)
    curr_x += 16
    draw.text((curr_x, stat_y - 1), str(rank), fill=(225, 230, 240), font=font_regular)
    curr_x += (font_regular.getbbox(str(rank))[2] - font_regular.getbbox(str(rank))[0]) + 14

    # Flame (Streak)
    draw_fire(draw, curr_x, stat_y - 1)
    curr_x += 14
    streak_str = f"{streak} days"
    draw.text((curr_x, stat_y - 1), streak_str, fill=(225, 230, 240), font=font_regular)
    curr_x += (font_regular.getbbox(streak_str)[2] - font_regular.getbbox(streak_str)[0]) + 14

    # Rosette (badgesNumber)
    draw_rosette(draw, curr_x, stat_y - 1)
    curr_x += 14
    draw.text((curr_x, stat_y - 1), str(badgesNumber), fill=(225, 230, 240), font=font_regular)
    curr_x += (font_regular.getbbox(str(badgesNumber))[2] - font_regular.getbbox(str(badgesNumber))[0]) + 14

    # Door (Rooms)
    draw_door(draw, curr_x, stat_y - 1)
    curr_x += 14
    draw.text((curr_x, stat_y - 1), str(rooms), fill=(225, 230, 240), font=font_regular)

    # Domain text
    draw.text((text_x, 76), "tryhackme.com", fill=(160, 170, 185), font=font_regular)

    # Top-right TryHackMe Logo
    logo_x = width - 85
    draw_thm_logo(draw, logo_x, 15)
    thm_txt_x = logo_x + 32
    draw.text((thm_txt_x, 12), "Try", fill=(255, 255, 255), font=font_small)
    draw.text((thm_txt_x, 22), "Hack", fill=(255, 255, 255), font=font_small)
    draw.text((thm_txt_x, 32), "Me", fill=(255, 255, 255), font=font_small)

    card.save('docs/tryhackme_badge.png', 'PNG')
    print('✅ Badge saved to docs/tryhackme_badge.png')

if __name__ == '__main__':
    draw_badge()
