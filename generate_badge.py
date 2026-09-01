import os
import datetime
from playwright.sync_api import sync_playwright
from PIL import Image, ImageDraw, ImageFont

USERNAME = os.environ.get('THM_USERNAME', 'CyberCracker27')
PROFILE_URL = f'https://tryhackme.com/p/{USERNAME}'

def fetch_stats():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # Intercept the API call that returns the live stats
        with page.expect_response(
            lambda r: '/api/v2/public-profile?userPublicId=' in r.url
        ) as response_info:
            page.goto(PROFILE_URL, wait_until='networkidle')

        response = response_info.value
        data = response.json()

        # Extract all required fields
        username = data.get('username', USERNAME)
        user_id = data.get('userPublicId', 'N/A')
        level = data.get('level', 0)
        rooms = data.get('roomsCompleted', 0)
        rank = data.get('rank', 'N/A')
        created = data.get('created')

        if created:
            created_date = datetime.datetime.fromisoformat(created.replace('Z', '+00:00'))
            days_active = (datetime.datetime.now(datetime.timezone.utc) - created_date).days
        else:
            days_active = 0

        browser.close()
        return username, user_id, level, rooms, rank, days_active

def draw_badge(username, user_id, level, rooms, rank, days_active):
    width, height = 500, 180
    bg_color = (22, 27, 34)      # dark background
    border_color = (48, 54, 61)
    text_color = (201, 209, 217)
    accent_color = (88, 166, 255)   # blue

    img = Image.new('RGB', (width, height), color=bg_color)
    draw = ImageDraw.Draw(img)

    try:
        font_large = ImageFont.truetype("DejaVuSansMono.ttf", 24)
        font_small = ImageFont.truetype("DejaVuSansMono.ttf", 18)
    except:
        font_large = ImageFont.load_default()
        font_small = ImageFont.load_default()

    # Border
    draw.rectangle([(0, 0), (width-1, height-1)], outline=border_color, width=3)

    # Row 1: Username + [0xID]
    draw.text((20, 15), f"{username} [0x{user_id}]", fill=accent_color, font=font_large)

    # Row 2: ID (plain)
    draw.text((20, 50), f"ID: {user_id}", fill=text_color, font=font_small)

    # Row 3: Days active
    draw.text((20, 80), f"{days_active} days active", fill=text_color, font=font_small)

    # Row 4: Level & Rooms
    draw.text((20, 110), f"Level: {level}", fill=text_color, font=font_small)
    draw.text((200, 110), f"Rooms: {rooms}", fill=text_color, font=font_small)

    # Row 5: Rank
    rank_text = f"Rank: #{rank}" if rank != 'N/A' else "Rank: N/A"
    draw.text((20, 140), rank_text, fill=(255, 215, 0), font=font_small)  # gold

    # Bottom: tryhackme.com
    draw.text((width - 150, height - 30), "tryhackme.com", fill=(139, 148, 158), font=font_small)

    os.makedirs('docs', exist_ok=True)
    img.save('docs/tryhackme_badge.png')
    print("✅ Badge generated successfully!")

if __name__ == "__main__":
    username, user_id, level, rooms, rank, days = fetch_stats()
    draw_badge(username, user_id, level, rooms, rank, days)
