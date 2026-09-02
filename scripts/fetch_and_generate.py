import os
import json
import sys
from playwright.sync_api import sync_playwright
from PIL import Image, ImageDraw, ImageFont
from utils import parse_joined_date, days_since

# Load config
with open('config.json') as f:
    config = json.load(f)
USERNAME = config.get('username')
USER_PUBLIC_ID = config.get('userPublicId')  # optional

def get_stats():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            viewport={'width': 1280, 'height': 720}
        )
        page = context.new_page()

        # 1. Visit homepage to set session cookies
        page.goto('https://tryhackme.com', wait_until='networkidle', timeout=30000)

        # 2. Navigate to profile
        profile_url = f'https://tryhackme.com/p/{USERNAME}'
        print(f'Navigating to {profile_url}')
        page.goto(profile_url, wait_until='networkidle', timeout=30000)
        page.wait_for_timeout(3000)  # extra for lazy loading

        # 3. Try to get userPublicId from page source (if not provided)
        if not USER_PUBLIC_ID:
            html = page.content()
            import re
            match = re.search(r'"userPublicId"\s*:\s*(\d+)', html)
            if match:
                user_id = match.group(1)
            else:
                # fallback: look for a meta tag
                user_id = page.locator('meta[name="user-id"]').get_attribute('content')
            if not user_id:
                raise Exception('Could not find userPublicId')
        else:
            user_id = USER_PUBLIC_ID

        print(f'Using userPublicId: {user_id}')

        # 4. Extract stats from DOM (stable selectors)
        # Username
        username = page.locator('.profile-header .username').inner_text().strip()

        # Level
        level_text = page.locator('.level-badge .level').inner_text().strip()
        level = int(level_text) if level_text.isdigit() else 0

        # Rooms completed
        rooms_text = page.locator('.profile-stat .rooms-completed .stat-value').inner_text().strip()
        rooms = int(rooms_text) if rooms_text.isdigit() else 0

        # Rank
        rank_text = page.locator('.profile-stat .rank .stat-value').inner_text().strip()
        rank = rank_text.replace('#', '').strip()
        if not rank.isdigit():
            rank = 'N/A'

        # Streak
        streak_text = page.locator('.profile-stat .streak .stat-value').inner_text().strip()
        streak = int(streak_text) if streak_text.isdigit() else 0

        # Joined date
        joined_text = page.locator('.profile-stat .joined .stat-value').inner_text().strip()
        joined_date = parse_joined_date(joined_text)
        days_active = days_since(joined_date) if joined_date else 0

        browser.close()
        return {
            'username': username,
            'user_id': user_id,
            'level': level,
            'rooms': rooms,
            'rank': rank,
            'streak': streak,
            'days_active': days_active
        }

def draw_badge(stats):
    username = stats['username']
    user_id = stats['user_id']
    level = stats['level']
    rooms = stats['rooms']
    rank = stats['rank']
    streak = stats['streak']
    days = stats['days_active']

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
    draw.text((20,50), f"ID: {user_id}  🟢 {days}d", fill=text, font=font_small)
    draw.text((20,80), f"🔒 Level {level}  🔑 {rooms} rooms", fill=text, font=font_small)
    draw.text((20,110), f"🏆 Rank #{rank}  🔥 {streak} days streak", fill=gold, font=font_small)
    draw.text((width-150, height-30), "tryhackme.com", fill=(139,148,158), font=font_small)

    os.makedirs('docs', exist_ok=True)
    img.save('docs/tryhackme_badge.png')
    print('✅ Badge image saved to docs/tryhackme_badge.png')

if __name__ == '__main__':
    try:
        stats = get_stats()
        print('Fetched stats:', stats)
        draw_badge(stats)
    except Exception as e:
        print('❌ Error:', e)
        sys.exit(1)
