import requests
import datetime
import os
from PIL import Image, ImageDraw, ImageFont

# 1. Fetch live data
username = os.environ.get('THM_USERNAME', 'CyberCracker27')
api_url = f'https://tryhackme.com/api/v2/public-profile?username={username}'
response = requests.get(api_url)
data = response.json()

# 2. Extract values
user_id = data.get('userPublicId', 'N/A')
level = data.get('level', 0)
rooms_completed = data.get('roomsCompleted', 0)
rank = data.get('rank', 'N/A') # Optional, you can display it if you want

# Calculate account age in days
created_date = datetime.datetime.fromisoformat(data['created'].replace('Z', '+00:00'))
days_active = (datetime.datetime.now(datetime.timezone.utc) - created_date).days

# 3. Create the Badge Image (matching your screenshot style)
width, height = 500, 180
bg_color = (22, 27, 34)  # Dark GitHub-style background
border_color = (48, 54, 61)
text_color = (201, 209, 217)
accent_color = (88, 166, 255)

img = Image.new('RGB', (width, height), color=bg_color)
draw = ImageDraw.Draw(img)

# Try to use a nice font, fallback to default
try:
    font_large = ImageFont.truetype("DejaVuSansMono.ttf", 24)
    font_small = ImageFont.truetype("DejaVuSansMono.ttf", 18)
except:
    font_large = ImageFont.load_default()
    font_small = ImageFont.load_default()

# Draw border
draw.rectangle([(0, 0), (width-1, height-1)], outline=border_color, width=3)

# Row 1: Username + Hex ID (e.g., CyberCracker27 [0x349854])
draw.text((20, 15), f"{username} [0x{user_id}]", fill=accent_color, font=font_large)

# Row 2: UserPublicId (plain)
draw.text((20, 50), f"ID: {user_id}", fill=text_color, font=font_small)

# Row 3: Days Active
draw.text((20, 80), f"{days_active} days active", fill=text_color, font=font_small)

# Row 4: Level (Left) & Rooms Completed (Right)
draw.text((20, 110), f"Level: {level}", fill=text_color, font=font_small)
draw.text((200, 110), f"Rooms: {rooms_completed}", fill=text_color, font=font_small)

# Row 5: Rank (Center)
rank_text = f"Rank: #{rank}" if rank != 'N/A' else "Rank: N/A"
draw.text((20, 140), rank_text, fill=(255, 215, 0), font=font_small)

# Bottom: tryhackme.com
draw.text((width - 150, height - 30), "tryhackme.com", fill=(139, 148, 158), font=font_small)

# 4. Save the image to the 'docs' folder (for GitHub Pages)
os.makedirs('docs', exist_ok=True)
img.save('docs/tryhackme_badge.png')
print("Badge generated successfully!")
