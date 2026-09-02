import json
import datetime
import os
from PIL import Image, ImageDraw, ImageFont

def draw_badge(data):
    # 🔥 FIX: Access the nested "data" object
    profile = data.get('data', {})  # <-- this is the fix

    username = profile.get('username', 'User')
    user_id = profile.get('_id', '')[:6]
    level = profile.get('level', 0)
    rooms = profile.get('completedRoomsNumber', 0)
    rank = profile.get('rank', 'N/A')
    streak = profile.get('streak', 0)

    created = profile.get('dateSignUp')
    if created:
        created_date = datetime.datetime.fromisoformat(created.replace('Z', '+00:00'))
        days_active = (datetime.datetime.now(datetime.timezone.utc) - created_date).days
    else:
        days_active = 0

    # ─── Drawing code (unchanged) ───
    width, height = 500, 180
    bg = (22, 27, 34)
    border = (48, 54, 61)
    text = (201, 209, 217)
    accent = (88, 166, 255)
    gold = (255, 215, 0)

    img = Image.new('RGB', (width, height), color=bg)
    draw = ImageDraw.Draw(img)

    try:
        font_large = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", 24)
        font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", 18)
    except:
        font_large = font_small = ImageFont.load_default()

    draw.rectangle([(0,0), (width-1,height-1)], outline=border, width=3)
    draw.text((20,15), f"{username} [0x{user_id}]", fill=accent, font=font_large)
    draw.text((20,50), f"ID: {user_id}  🟢 {days_active}d", fill=text, font=font_small)
    draw.text((20,80), f"🔒 Level {level}  🔑 {rooms} rooms", fill=text, font=font_small)
    draw.text((20,110), f"🏆 Rank #{rank}  🔥 {streak} days streak", fill=gold, font=font_small)
    draw.text((width-150, height-30), "tryhackme.com", fill=(139,148,158), font=font_small)

    os.makedirs('docs', exist_ok=True)
    img.save('docs/tryhackme_badge.png')
    print('✅ Badge image saved to docs/tryhackme_badge.png')

if __name__ == '__main__':
    try:
        with open('data.json', 'r') as f:
            data = json.load(f)
        draw_badge(data)
    except Exception as e:
        print(f'❌ Error: {e}')
        raise
