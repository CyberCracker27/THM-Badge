import os
import datetime
from playwright.sync_api import sync_playwright
from PIL import Image, ImageDraw, ImageFont

# --- Config ---
USERNAME = os.environ.get('THM_USERNAME', 'CyberCracker27')
PROFILE_URL = f'https://tryhackme.com/p/{USERNAME}'

def fetch_stats():
    with sync_playwright() as p:
        # Launch headless browser (Chromium)
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # Go to profile and wait for the stats to load
        page.goto(PROFILE_URL, wait_until='networkidle')
        # The stats are inside a div with class "profile-stats" or similar
        # Inspect the page to find the correct selectors (updated October 2024)
        # Let's use common selectors (adjust if needed)
        
        # Wait for the level element (it appears after JS loads)
        page.wait_for_selector('.level-badge .level', timeout=10000)
        
        # Extract data
        level = page.locator('.level-badge .level').inner_text().strip()
        rooms = page.locator('.profile-stat .rooms-completed .stat-value').inner_text().strip()
        rank = page.locator('.profile-stat .rank .stat-value').inner_text().strip()
        # Account creation date – often in a tooltip or meta
        # We'll get it from the "joined" element
        joined_text = page.locator('.profile-stat .joined .stat-value').inner_text().strip()
        # joined_text is like "Joined 2022-01-15" – parse it
        # Alternatively, you can get the raw timestamp from the page's data attributes
        
        browser.close()
        
        # Convert to numbers
        level = int(level)
        rooms = int(rooms)
        # rank may contain "#" – clean it
        rank = rank.replace('#', '').strip()
        if rank.isdigit():
            rank = int(rank)
        else:
            rank = 'N/A'
        
        # Calculate days active from the joined date
        # Since the joined text is like "Joined 2022-01-15"
        # We'll parse it
        import re
        date_match = re.search(r'(\d{4}-\d{2}-\d{2})', joined_text)
        if date_match:
            created_date = datetime.datetime.strptime(date_match.group(1), '%Y-%m-%d')
            days_active = (datetime.datetime.now() - created_date).days
        else:
            days_active = 0
        
        return level, rooms, rank, days_active

def draw_badge(level, rooms, rank, days_active):
    width, height = 500, 180
    bg_color = (22, 27, 34)
    border_color = (48, 54, 61)
    text_color = (201, 209, 217)
    accent_color = (88, 166, 255)

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

    # Row 1: Username and ID (we'll use the userPublicId from the page? We'll omit or use a placeholder)
    # The screenshot shows "CyberCracker27 [0x349854]" – we don't have the public ID here, but we can still show the username.
    draw.text((20, 15), f"{USERNAME}", fill=accent_color, font=font_large)

    # Row 2: ID (not available – skip or show something)
    draw.text((20, 50), f"ID: {USERNAME}", fill=text_color, font=font_small)

    # Row 3: Days active
    draw.text((20, 80), f"{days_active} days active", fill=text_color, font=font_small)

    # Row 4: Level & Rooms
    draw.text((20, 110), f"Level: {level}", fill=text_color, font=font_small)
    draw.text((200, 110), f"Rooms: {rooms}", fill=text_color, font=font_small)

    # Row 5: Rank
    rank_text = f"Rank: #{rank}" if rank != 'N/A' else "Rank: N/A"
    draw.text((20, 140), rank_text, fill=(255, 215, 0), font=font_small)

    # Bottom: tryhackme.com
    draw.text((width - 150, height - 30), "tryhackme.com", fill=(139, 148, 158), font=font_small)

    os.makedirs('docs', exist_ok=True)
    img.save('docs/tryhackme_badge.png')
    print("Badge generated successfully!")

if __name__ == "__main__":
    level, rooms, rank, days = fetch_stats()
    draw_badge(level, rooms, rank, days)
