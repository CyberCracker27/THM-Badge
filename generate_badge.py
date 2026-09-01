import os
import datetime
import re
from playwright.sync_api import sync_playwright
from PIL import Image, ImageDraw, ImageFont

USERNAME = os.environ.get('THM_USERNAME', 'CyberCracker27')
PROFILE_URL = f'https://tryhackme.com/p/{USERNAME}'

def fetch_stats():
    with sync_playwright() as p:
        # Realistic browser context
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            viewport={'width': 1280, 'height': 720}
        )
        page = context.new_page()

        # Visit homepage to establish session
        print("Visiting homepage to get session...")
        page.goto('https://tryhackme.com', wait_until='networkidle', timeout=30000)

        # Now navigate to profile
        print("Navigating to profile...")
        page.goto(PROFILE_URL, wait_until='networkidle', timeout=30000)
        page.wait_for_timeout(3000)  # extra time for any lazy loading

        # Try to get the userPublicId from the page source (for badge)
        html = page.content()
        match = re.search(r'"userPublicId"\s*:\s*(\d+)', html)
        if match:
            user_id = match.group(1)
        else:
            user_id = 'N/A'

        # Scrape stats from the DOM
        # The selectors are based on common patterns on TryHackMe
        # We'll use flexible selectors with fallbacks

        # Username
        username_element = page.locator('.profile-header .username')
        if username_element.count():
            username = username_element.inner_text().strip()
        else:
            username = USERNAME

        # Level – try several possible selectors
        level_text = page.locator('.level-badge .level, .level-display, [data-testid="level"]').first.inner_text().strip()
        level = int(re.search(r'\d+', level_text).group()) if re.search(r'\d+', level_text) else 0

        # Rooms completed
        rooms_text = page.locator('.stat-rooms .stat-value, .rooms-completed, [data-testid="rooms"]').first.inner_text().strip()
        rooms = int(re.search(r'\d+', rooms_text).group()) if re.search(r'\d+', rooms_text) else 0

        # Rank
        rank_text = page.locator('.stat-rank .stat-value, .rank-display, [data-testid="rank"]').first.inner_text().strip()
        rank = re.sub(r'[^0-9]', '', rank_text) if rank_text else 'N/A'
        if not rank:
            rank = 'N/A'

        # Joined date (for days active)
        joined_text = page.locator('.stat-joined .stat-value, .joined-date, [data-testid="joined"]').first.inner_text().strip()
        match_date = re.search(r'(\d{4}-\d{2}-\d{2})', joined_text)
        if match_date:
            created_date = datetime.datetime.strptime(match_date.group(1), '%Y-%m-%d')
            days_active = (datetime.datetime.now() - created_date).days
        else:
            days_active = 0

        browser.close()
        return username, user_id, level, rooms, rank, days_active

def draw_badge(username, user_id, level, rooms, rank, days_active):
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

    draw.rectangle([(0, 0), (width-1, height-1)], outline=border_color, width=3)
    draw.text((20, 15), f"{username} [0x{user_id}]", fill=accent_color, font=font_large)
    draw.text((20, 50), f"ID: {user_id}", fill=text_color, font=font_small)
    draw.text((20, 80), f"{days_active} days active", fill=text_color, font=font_small)
    draw.text((20, 110), f"Level: {level}", fill=text_color, font=font_small)
    draw.text((200, 110), f"Rooms: {rooms}", fill=text_color, font=font_small)
    rank_text = f"Rank: #{rank}" if rank != 'N/A' else "Rank: N/A"
    draw.text((20, 140), rank_text, fill=(255, 215, 0), font=font_small)
    draw.text((width - 150, height - 30), "tryhackme.com", fill=(139, 148, 158), font=font_small)

    os.makedirs('docs', exist_ok=True)
    img.save('docs/tryhackme_badge.png')
    print("✅ Badge generated successfully!")

if __name__ == "__main__":
    try:
        username, user_id, level, rooms, rank, days = fetch_stats()
        draw_badge(username, user_id, level, rooms, rank, days)
    except Exception as e:
        print(f"Error: {e}")
        raise
