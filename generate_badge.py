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

        # Step 1: Load the profile page with extra time
        page.goto(PROFILE_URL, wait_until='networkidle', timeout=60000)
        # Wait a bit more for any dynamic content
        page.wait_for_timeout(5000)

        # Step 2: Extract userPublicId from the HTML source
        html = page.content()
        # Look for something like "userPublicId":12345, "userPublicId":"12345" or userPublicId=12345
        match = re.search(r'"userPublicId"\s*:\s*"?(\d+)"?', html)
        if not match:
            match = re.search(r'userPublicId[=:]\s*["\']?(\d+)["\']?', html)
        if match:
            user_id = match.group(1)
            print(f"Extracted userPublicId: {user_id}")
        else:
            # Fallback: try to get it from a meta tag or data attribute
            meta_tag = page.query_selector('meta[name="user-id"]')
            user_id = meta_tag.get_attribute('content') if meta_tag else None
            if not user_id:
                # If still not found, we can't proceed
                browser.close()
                raise Exception("Could not find userPublicId on the page.")
            print(f"Found userPublicId from meta: {user_id}")

        # Step 3: Use the browser's fetch to call the API directly
        api_data = page.evaluate(f"""
            async () => {{
                const response = await fetch('/api/v2/public-profile?userPublicId={user_id}', {{
                    headers: {{ 'Accept': 'application/json' }}
                }});
                if (!response.ok) throw new Error('API fetch failed');
                return await response.json();
            }}
        """)

        # Step 4: Extract data
        username = api_data.get('username', USERNAME)
        level = api_data.get('level', 0)
        rooms = api_data.get('roomsCompleted', 0)
        rank = api_data.get('rank', 'N/A')
        created = api_data.get('created')
        if created:
            created_date = datetime.datetime.fromisoformat(created.replace('Z', '+00:00'))
            days_active = (datetime.datetime.now(datetime.timezone.utc) - created_date).days
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
