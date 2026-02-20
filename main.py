import os
import requests
import random
from telethon import TelegramClient, functions
from PIL import Image, ImageDraw, ImageFont
import datetime
import asyncio
from dotenv import load_dotenv
import glob

# .env faylini yuklaymiz
load_dotenv()

api_id = os.getenv('API_ID')
api_hash = os.getenv('API_HASH')
tg_password = os.getenv('TG_PASSWORD')

def get_btc_data():
    try:
        url = "https://api.coingecko.com/api/v3/coins/bitcoin/market_chart?vs_currency=usd&days=1"
        response = requests.get(url, timeout=10)
        data = response.json()
        prices_history = [p[1] for p in data['prices']]
        current_price = prices_history[-1]
        start_price = prices_history[0]
        change_pct = ((current_price - start_price) / start_price) * 100
        return current_price, prices_history, "BTC", change_pct
    except Exception:
        return None, [], "BTC", 0

def get_usd_uzs_data():
    try:
        url = "https://cbu.uz/uz/arkhiv-kursov-valyut/json/USD/all/"
        response = requests.get(url, timeout=10)
        data = response.json()
        current_price = float(data[0]['Rate'])
        change_pct = random.uniform(-0.05, 0.05) 
        history = [current_price * (1 + random.uniform(-0.001, 0.001)) for _ in range(50)]
        history.append(current_price)
        return current_price, history, "USD/UZS", change_pct
    except Exception:
        return None, [], "USD/UZS", 0

def get_gold_data():
    try:
        url = "https://api.coingecko.com/api/v3/coins/pax-gold/market_chart?vs_currency=usd&days=1"
        response = requests.get(url, timeout=10)
        data = response.json()
        prices_history = [p[1] for p in data['prices']]
        current_price = prices_history[-1]
        start_price = prices_history[0]
        change_pct = ((current_price - start_price) / start_price) * 100
        return current_price, prices_history, "GOLD", change_pct
    except Exception:
        return None, [], "GOLD", 0

def get_font(size):
    local_font = "fonts/font.ttf"
    if os.path.exists(local_font):
        return ImageFont.truetype(local_font, size)
    return ImageFont.load_default()

def draw_trading_chart(d, history, color, area):
    mx, my_top, width, height = area
    my_bottom = my_top + height
    min_p, max_p = min(history), max(history)
    p_range = max_p - min_p if max_p != min_p else 1
    
    # Grid
    for i in range(5):
        gy = my_bottom - (i / 4) * height
        d.line([(mx, gy), (mx + width, gy)], fill=(30, 41, 59), width=1)
    
    # Moving Average
    if len(history) > 7:
        ma_points = []
        for i in range(7, len(history)):
            ma_val = sum(history[i-7:i]) / 7
            x = mx + (i / (len(history) - 1)) * width
            y = my_bottom - ((ma_val - min_p) / p_range) * height
            ma_points.append((x, y))
        if len(ma_points) > 1:
            d.line(ma_points, fill=(245, 158, 11), width=2)
    
    # Main Line
    points = [(mx + (i / (len(history) - 1)) * width, my_bottom - ((p - min_p) / p_range) * height) for i, p in enumerate(history)]
    d.line(points, fill=color, width=4)
    fill_points = [(mx, my_bottom)] + points + [(mx + width, my_bottom)]
    d.polygon(fill_points, fill=(color[0]//5, color[1]//5, color[2]//5))

async def create_avatar(session_name):
    choice = random.choice(['BTC', 'USD', 'GOLD'])
    if choice == 'BTC':
        price, history, label, change = get_btc_data()
        color = (16, 185, 129)
        prefix = "$"
    elif choice == 'USD':
        price, history, label, change = get_usd_uzs_data()
        color = (59, 130, 246)
        prefix = ""
    else:
        price, history, label, change = get_gold_data()
        color = (234, 179, 8)
        prefix = "$"

    img = Image.new('RGB', (500, 500), color=(11, 15, 25))
    d = ImageDraw.Draw(img)

    if price and history:
        # 1. Label va 24s o'zgarish (Markazga yaqinroq surildi - doira ichiga tushishi uchun)
        d.text((80, 70), label, fill=(148, 163, 184), font=get_font(30))
        
        change_text = f"{'+' if change >= 0 else ''}{change:.2f}%"
        change_color = (16, 185, 129) if change >= 0 else (239, 68, 68)
        # O'ng tarafdan chekkaroqqa surildi
        d.text((420, 70), change_text, fill=change_color, font=get_font(28), anchor="ra")

        # 2. Asosiy Narx (Markazroqqa surildi)
        price_str = f"{prefix}{price:,.0f}" if choice != 'GOLD' else f"{prefix}{price:,.2f}"
        d.text((80, 110), price_str, fill=(255, 255, 255), font=get_font(75))

        # 3. Trading Chart (Doira kesib tashlamasligi uchun kichraytirildi va markazga olindi)
        # Area: (x, y, width, height) -> (80, 210, 340, 200)
        draw_trading_chart(d, history, color, (80, 210, 340, 200))
        
        # Border (Doira profil uchun ramka shart emas, lekin bezak sifatida qolishi mumkin)
        # d.rectangle([10, 10, 490, 490], outline=(30, 41, 59), width=2)
    else:
        d.text((150, 220), "Loading...", fill=(255, 255, 255), font=get_font(40))

    filename = f"avatar_{session_name}.png"
    img.save(filename)
    return filename

async def session_worker(session_path):
    session_name = os.path.basename(session_path).replace('.session', '')
    print(f"[{session_name}] Ish boshlanmoqda...")
    
    client = TelegramClient(session_name, api_id, api_hash)
    try:
        await client.start(password=tg_password)
        me = await client.get_me()
        print(f"[{session_name}] Muvaffaqiyatli kirdi: {me.first_name}")

        while True:
            try:
                # Har bir seans uchun alohida rasm yaratamiz
                avatar_file = await create_avatar(session_name)
                
                # Yangilash
                file = await client.upload_file(avatar_file)
                await client(functions.photos.UploadProfilePhotoRequest(file=file))
                
                # Eski rasmlarni o'chirish
                photos = await client.get_profile_photos('me', limit=10)
                if len(photos) > 1:
                    await client(functions.photos.DeletePhotosRequest(id=photos[1:]))
                
                print(f"[{session_name} - {datetime.datetime.now().strftime('%H:%M:%S')}] Avatar yangilandi!")
            except Exception as e:
                print(f"[{session_name}] Xato: {e}")
            
            await asyncio.sleep(900) # 15 daqiqa
    except Exception as e:
        print(f"[{session_name}] Login qilishda jiddiy xato: {e}")
    finally:
        await client.disconnect()

async def main():
    # Barcha .session fayllarni qidiramiz
    sessions = glob.glob("*.session")
    if not sessions:
        print("Hech qanday .session fayli topilmadi!")
        return

    print(f"Topilgan seanslar: {', '.join(sessions)}")
    
    # Barcha seanslarni bir vaqtda ishga tushiramiz
    await asyncio.gather(*(session_worker(s) for s in sessions))

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Dastur to'xtatildi.")