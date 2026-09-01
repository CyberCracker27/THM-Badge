import os
import datetime
from playwright.sync_api import sync_playwright
from PIL import Image, ImageDraw, ImageFont

USERNAME = os.environ.get('THM_USERNAME', 'CyberCracker27')
USER_PUBLIC_ID = '349854'  # Hardcoded – you can change if needed

def fetch_stats():
    with sync_playwright() as p:
        # 1. Launch a realistic browser context
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            viewport={'width': 1280, 'height': 720}
        )
        page = context.new_page()

        # 2. First visit the homepage – this sets the required session cookies
        print("Visiting homepage to get session...")
        page.goto('https://tryhackme.com', wait_until='networkidle', timeout=30000)

        # 3. Now the browser has cookies – we can fetch the API directly
        print("Fetching API data...")
        api_data = page.evaluate(f"""
            async () => {{
                const response = await fetch('/api/v2/public-profile?userPublicId={USER_PUBLIC_ID}', {{
                    headers: {{ 'Accept': 'application/json' }}
                }});
                if (!response.ok) throw new Error('API fetch failed');
                return await response.json();
            }}
        """)

        browser.close()

        # Extract data
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

        return username, USER_PUBLIC_ID, level, rooms, rank, days_active

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
