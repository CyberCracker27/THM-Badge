import os
import datetime
import re
from playwright.sync_api import sync_playwright
from PIL import Image, ImageDraw, ImageFont

USERNAME = os.environ.get('THM_USERNAME', 'CyberCracker27')
PROFILE_URL = f'https://tryhackme.com/p/{USERNAME}'

def fetch_stats():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        # Debug: log all requests/responses (optional, remove if too verbose)
        # page.on('response', lambda r: print(f"RESP: {r.url}"))

        # Navigate and wait for the page to be fully loaded (including API calls)
        page.goto(PROFILE_URL, wait_until='networkidle')

        # Try to catch the API response first
        api_response = None
        # Wait for a response that includes the public-profile API
        try:
            with page.expect_response(
                lambda r: '/api/v2/public-profile' in r.url,
                timeout=15000
            ) as response_info:
                # Keep the page alive; the response should be captured while it loads
                # We already loaded the page, but we can trigger a reload if needed
                # Actually, we've already loaded, so the response may have already happened.
                # To be safe, we can wait a bit and then check.
                pass
            api_response = response_info.value
        except Exception as e:
            print(f"API interception timed out: {e}")

        # If we got the API, use it
        if api_response:
            data = api_response.json()
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

        # Fallback: scrape from DOM (using stable selectors)
        print("API not captured – falling back to DOM scraping.")
        # Wait for the stats container (commonly a div with class "profile-stats")
        page.wait_for_selector('.profile-stats', timeout=10000)
        
        # Extract username from the page title or a header
        username_element = page.locator('.profile-header .username')
        if username_element.count():
            username = username_element.inner_text().strip()
        else:
            username = USERNAME

        # Extract userPublicId – often in a data attribute or from the page source
        # We can try to get it from the API URL that we might have missed, but we can also parse from the HTML
        # For now, we'll use a placeholder
        user_id = page.locator('meta[name="user-id"]').get_attribute('content') or 'N/A'

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

        # Days active – from "Joined" date
        joined_text = page.locator('.profile-stat .joined .stat-value').inner_text().strip()
        # Expect "Joined 2022-01-15"
        match = re.search(r'(\d{4}-\d{2}-\d{2})', joined_text)
        if match:
            created_date = datetime.datetime.strptime(match.group(1), '%Y-%m-%d')
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
    username, user_id, level, rooms, rank, days = fetch_stats()
    draw_badge(username, user_id, level, rooms, rank, days)
