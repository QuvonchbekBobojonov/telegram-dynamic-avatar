import os
import requests
import random
from telethon import TelegramClient, functions
from PIL import Image, ImageDraw, ImageFont
import datetime
import asyncio
from dotenv import load_dotenv

# .env faylini yuklaymiz
load_dotenv()

api_id = os.getenv('API_ID')
api_hash = os.getenv('API_HASH')
tg_password = os.getenv('TG_PASSWORD')

client = TelegramClient('tg', api_id, api_hash)

def get_btc_data():
    try:
        # Oxirgi 24 soatlik narxlar tarixini olamiz
        url = "https://api.coingecko.com/api/v3/coins/bitcoin/market_chart?vs_currency=usd&days=1"
        response = requests.get(url, timeout=10)
        data = response.json()
        prices_history = [p[1] for p in data['prices']]
        current_price = prices_history[-1]
        return current_price, prices_history
    except Exception as e:
        print(f"Ma'lumot olishda xato: {e}")
        return None, []

def get_font(size):
    font_paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "C:\\Windows\\Fonts\\arialbd.ttf",
        "C:\\Windows\\Fonts\\arial.ttf",
        "fonts/DejaVuSans-Bold.ttf",
        "arial.ttf"
    ]
    for path in font_paths:
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()

async def create_avatar():
    current_price, history = get_btc_data()
    
    # Orqa fon (minimalist to'q ko'k)
    img = Image.new('RGB', (500, 500), color=(11, 15, 25))
    d = ImageDraw.Draw(img)

    if current_price and history:
        # 1. Narxni chiqarish
        font_price = get_font(70)
        price_text = f"${current_price:,.0f}"
        d.text((50, 50), "BTC", fill=(255, 255, 255), font=get_font(40))
        d.text((50, 110), price_text, fill=(34, 197, 94), font=font_price) # Yashil rang

        # 2. Grafik chizish
        # Grafik maydoni: x(50, 450), y(250, 450)
        margin_x = 50
        margin_y_top = 250
        margin_y_bottom = 450
        width = 400
        height = 200

        min_p = min(history)
        max_p = max(history)
        p_range = max_p - min_p if max_p != min_p else 1

        points = []
        for i, p in enumerate(history):
            x = margin_x + (i / (len(history) - 1)) * width
            y = margin_y_bottom - ((p - min_p) / p_range) * height
            points.append((x, y))

        # Grafik chizig'ini chizish
        d.line(points, fill=(34, 197, 94), width=4)
        
        # Grafik ostini rang bilan to'ldirish (gradient effekti o'rniga oddiy rang)
        fill_points = [(margin_x, margin_y_bottom)] + points + [(margin_x + width, margin_y_bottom)]
        d.polygon(fill_points, fill=(22, 101, 52, 100)) # To'q yashil shaffofroq (emulyatsiya)

        # 3. Vaqt (pastda kichikroq)
        now_str = datetime.datetime.now().strftime("%H:%M")
        d.text((380, 50), now_str, fill=(100, 116, 139), font=get_font(30))
    else:
        d.text((100, 200), "Yuklanmoqda...", fill=(255, 255, 255), font=get_font(40))

    img.save('avatar.png')

async def update_profile():
    try:
        await client.start(password=tg_password)
    except Exception as e:
        print(f"Login qilishda xato: {e}")
        return

    while True:
        try:
            await create_avatar()
            file = await client.upload_file('avatar.png')
            await client(functions.photos.UploadProfilePhotoRequest(file=file))
            
            photos = await client.get_profile_photos('me', limit=10)
            if len(photos) > 1:
                await client(functions.photos.DeletePhotosRequest(id=photos[1:]))
            
            print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] BTC Chart yangilandi!")
        except Exception as e:
            print(f"Xato: {e}")

        # Grafik har 15 daqiqada yangilanadi
        await asyncio.sleep(900)

if __name__ == '__main__':
    try:
        asyncio.run(update_profile())
    except KeyboardInterrupt:
        print("To'xtatildi.")