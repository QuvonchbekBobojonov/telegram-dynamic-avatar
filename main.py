import os
import requests
import random
from telethon import TelegramClient, functions, events, types
from PIL import Image, ImageDraw, ImageFont
import datetime
import asyncio
from dotenv import load_dotenv
import glob
import google.generativeai as genai

# .env faylini yuklaymiz
load_dotenv()

api_id = os.getenv('API_ID')
api_hash = os.getenv('API_HASH')
tg_password = os.getenv('TG_PASSWORD')
ai_key = os.getenv('GEMINI_API_KEY')

# Gemini AI ni sozlash
if ai_key:
    genai.configure(api_key=ai_key)
    # gemini-1.5-flash tavsiya etiladi (gemini-3 mavjud emas)
    model = genai.GenerativeModel('gemini-1.5-flash')
else:
    model = None
    print("OGOHLANTIRISH: GEMINI_API_KEY .env faylida topilmadi. AI javob berish funksiyasi ishlamaydi.")

# Ma'lumotlarni keshlab turish uchun global o'zgaruvchi
DATA_CACHE = {
    'BTC': (None, [], "BTC / USD", 0),
    'USD': (None, [], "USD / UZS", 0),
    'GOLD': (None, [], "GOLD / USD", 0),
    'ETH': (None, [], "ETH / USD", 0)
}

def get_btc_data():
    try:
        url = "https://api.coingecko.com/api/v3/coins/bitcoin/market_chart?vs_currency=usd&days=1"
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        data = response.json()
        prices_history = [p[1] for p in data['prices']]
        current_price = prices_history[-1]
        start_price = prices_history[0]
        change_pct = ((current_price - start_price) / start_price) * 100
        res = (current_price, prices_history, "BTC / USD", change_pct)
        DATA_CACHE['BTC'] = res
        return res
    except Exception as e:
        print(f"BTC API xatolik: {e}")
        return DATA_CACHE['BTC']

def get_usd_uzs_data():
    try:
        url = "https://cbu.uz/uz/arkhiv-kursov-valyut/json/USD/all/"
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        data = response.json()
        current_price = float(data[0]['Rate'])
        change_pct = random.uniform(-0.02, 0.05) 
        history = [current_price * (1 + random.uniform(-0.001, 0.001)) for _ in range(50)]
        history.append(current_price)
        res = (current_price, history, "USD / UZS", change_pct)
        DATA_CACHE['USD'] = res
        return res
    except Exception as e:
        print(f"USD API xatolik: {e}")
        return DATA_CACHE['USD']

def get_gold_data():
    try:
        url = "https://api.coingecko.com/api/v3/coins/pax-gold/market_chart?vs_currency=usd&days=1"
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        data = response.json()
        prices_history = [p[1] for p in data['prices']]
        current_price = prices_history[-1]
        start_price = prices_history[0]
        change_pct = ((current_price - start_price) / start_price) * 100
        res = (current_price, prices_history, "GOLD / USD", change_pct)
        DATA_CACHE['GOLD'] = res
        return res
    except Exception as e:
        print(f"GOLD API xatolik: {e}")
        return DATA_CACHE['GOLD']

def get_eth_data():
    try:
        url = "https://api.coingecko.com/api/v3/coins/ethereum/market_chart?vs_currency=usd&days=1"
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        data = response.json()
        prices_history = [p[1] for p in data['prices']]
        current_price = prices_history[-1]
        start_price = prices_history[0]
        change_pct = ((current_price - start_price) / start_price) * 100
        res = (current_price, prices_history, "ETH / USD", change_pct)
        DATA_CACHE['ETH'] = res
        return res
    except Exception as e:
        print(f"ETH API xatolik: {e}")
        return DATA_CACHE['ETH']

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

async def create_avatar(session_name, choice=None):
    if not choice:
        choice = random.choice(['BTC', 'USD', 'GOLD', 'ETH'])
        
    if choice == 'BTC':
        price, history, label, change = get_btc_data()
        color = (16, 185, 129)
        prefix = "$"
    elif choice == 'USD':
        price, history, label, change = get_usd_uzs_data()
        color = (59, 130, 246)
        prefix = ""
    elif choice == 'ETH':
        price, history, label, change = get_eth_data()
        color = (155, 89, 182) # Purple for ETH
        prefix = "$"
    else:
        price, history, label, change = get_gold_data()
        color = (234, 179, 8)
        prefix = "$"

    img = Image.new('RGB', (500, 500), color=(11, 15, 25))
    d = ImageDraw.Draw(img)

    if price and history:
        d.text((80, 70), label, fill=(148, 163, 184), font=get_font(30))
        change_text = f"{'+' if change >= 0 else ''}{change:.2f}%"
        change_color = (16, 185, 129) if change >= 0 else (239, 68, 68)
        d.text((420, 70), change_text, fill=change_color, font=get_font(28), anchor="ra")
        
        price_str = f"{prefix}{price:,.0f}" if choice != 'GOLD' else f"{prefix}{price:,.2f}"
        d.text((80, 110), price_str, fill=(255, 255, 255), font=get_font(75))
        
        draw_trading_chart(d, history, color, (80, 210, 340, 200))
        
        d.line([(80, 440), (420, 440)], fill=(30, 45, 80), width=1)
        d.text((250, 455), "TERMINAL DATA", fill=(50, 80, 140), font=get_font(18), anchor="ma")
    else:
        d.text((150, 220), "Loading...", fill=(255, 255, 255), font=get_font(40))

    filename = f"avatar_{session_name}.png"
    img.save(filename)
    return filename

async def create_news_card(session_name, headline, category):
    width, height = 1000, 600
    color = (255, 50, 50) if "kiber" in category.lower() else (0, 150, 255)
    
    img = Image.new('RGB', (width, height), (10, 15, 30))
    d = ImageDraw.Draw(img)
    
    for i in range(height):
        alpha = int(40 * (i / height))
        d.line([(0, i), (width, i)], fill=(color[0], color[1], color[2], alpha))

    d.rectangle([20, 20, 980, 580], outline=(color[0], color[1], color[2], 100), width=3)
    d.rectangle([40, 40, 300, 90], fill=color)
    d.text((55, 48), "BREAKING NEWS", fill=(255, 255, 255), font=get_font(30))
    d.text((320, 50), category.upper(), fill=(150, 150, 150), font=get_font(25))

    words = headline.split()
    lines = []
    current_line = ""
    for word in words:
        test_line = current_line + " " + word if current_line else word
        if len(test_line) < 35:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word
    lines.append(current_line)

    y_offset = 180
    for line in lines[:4]:
        d.text((50, y_offset), line, fill=(255, 255, 255), font=get_font(55))
        y_offset += 75

    d.line([(50, 540), (950, 540)], fill=(color[0], color[1], color[2], 150), width=2)
    d.text((50, 550), "TECH MONITOR // WORLDWIDE FEED", fill=(100, 100, 100), font=get_font(20))

    filename = f"news_{session_name}.png"
    img.save(filename)
    return filename

async def session_worker(session_path, session_index):
    session_name = os.path.basename(session_path).replace('.session', '')
    print(f"[{session_name}] Ish boshlanmoqda...")
    
    client = TelegramClient(session_name, api_id, api_hash)
    try:
        await client.start(password=tg_password)
        me = await client.get_me()
        print(f"[{session_name}] Muvaffaqiyatli kirdi: {me.first_name}")

        choices = ['BTC', 'USD', 'GOLD', 'ETH']
        
        @client.on(events.NewMessage(incoming=True, func=lambda e: e.is_private))
        async def handle_new_message(event):
            if not model: return
            try:
                sender = await event.get_sender()
                if not sender: return
                is_contact = getattr(sender, 'contact', False)
                if isinstance(sender, types.User) and not is_contact and not sender.bot:
                    # Psixologik tahlil va xulq-atvor bo'yicha ekspert shaxsiyati
                    system_prompt = (
                        "Siz ushbu profil egasining AI Yordamchisiz. Mutaxassisligingiz: Inson fe’l-atvori, psixologik tahlil va xulq-atvor sirlari. "
                        "Har doim foydalanuvchiga quyidagicha salom bering: "
                        "'Assalomu alaykum! Men ushbu profiling sahifasi egasining AI Yordamchisiman. "
                        "Inson fe’l-atvori, psixologik tahlil va xulq-atvor sirlari olamiga xush kelibsiz! Sizga qanday yordam bera olaman?' "
                        "Javoblaringiz aqlli, tahliliy va xushmuomala bo'lsin."
                    )
                    prompt = f"{system_prompt}\n\nFoydalanuvchi yozdi: '{event.text}'. Unga o'zbek tilida javob bering."
                    response = await asyncio.to_thread(model.generate_content, prompt)
                    if response and response.text:
                        await event.reply(response.text)
            except Exception as ae:
                print(f"[{session_name}] AI xatolik: {ae}")

        async def avatar_timer():
            while True:
                try:
                    time_offset = int(datetime.datetime.now().timestamp() / 900)
                    my_choice = choices[(session_index + time_offset) % len(choices)]
                    avatar_file = await create_avatar(session_name, choice=my_choice)
                    file = await client.upload_file(avatar_file)
                    await client(functions.photos.UploadProfilePhotoRequest(file=file))
                    try:
                        photos = await client.get_profile_photos('me')
                        if len(photos) > 1:
                            await client(functions.photos.DeletePhotosRequest(id=photos[1:]))
                    except Exception as pe:
                        print(f"[{session_name}] Rasmlarni ochirishda xato: {pe}")
                    if os.path.exists(avatar_file): os.remove(avatar_file)
                except Exception as e:
                    print(f"[{session_name}] Avatar xatosi: {e}")
                await asyncio.sleep(900)

        channel_id = os.getenv('CHANNEL_USERNAME')
        async def channel_poster():
            if not channel_id: return
            while True:
                try:
                    if model:
                        prompt = """Hozirgi vaqtda (bugun/kecha) dunyodagi eng muhim IT yoki Kiberxavfsizlik yangiligini top. 
                        Javobni FAQAT ushbu formatda (JSON) qaytar:
                        {
                            "headline": "Yangilik sarlavhasi",
                            "body": "Yangilik tafsiloti",
                            "category": "Kiberxavfsizlik" yoki "Texnologiya",
                            "source": "Manba nomi",
                            "tags": "#hashtag"
                        }"""
                        response = await asyncio.to_thread(model.generate_content, prompt)
                        if response and response.text:
                            import json
                            raw_text = response.text.replace("```json", "").replace("```", "").strip()
                            data = json.loads(raw_text)
                            news_img = await create_news_card(f"news_{session_name}", data['headline'], data['category'])
                            caption = f"⚡️ **{data['headline']}**\n\n{data['body']}\n\n� Manba: **{data['source']}**\n\n📌 #{data['category']} {data['tags']}\n\n📢 @{channel_id.replace('@', '')}"
                            await client.send_file(channel_id, news_img, caption=caption)
                            if os.path.exists(news_img): os.remove(news_img)
                            print(f"[{session_name}] Kanalga yangilik joylandi.")
                except Exception as ce:
                    print(f"[{session_name}] Kanalga post xatosi: {ce}")
                await asyncio.sleep(1800)

        asyncio.create_task(avatar_timer())
        asyncio.create_task(channel_poster())
        await client.run_until_disconnected()
    except Exception as e:
        print(f"[{session_name}] Xato: {e}")
    finally:
        await client.disconnect()

async def main():
    sessions = glob.glob("*.session")
    if not sessions: return
    await asyncio.gather(*(session_worker(s, i) for i, s in enumerate(sessions)))

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Dastur to'xtatildi.")