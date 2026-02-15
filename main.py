import os

from telethon import TelegramClient, functions
from PIL import Image, ImageDraw, ImageFont
import datetime
import asyncio
import time
from dotenv import load_dotenv

# .env faylini yuklaymiz
load_dotenv()

api_id = os.getenv('API_ID')
api_hash = os.getenv('API_HASH')
tg_password = os.getenv('TG_PASSWORD')

client = TelegramClient('tg', api_id, api_hash)

def get_background_name():
    now = datetime.datetime.now()
    month = now.month
    hour = now.hour

    if month in [12, 1, 2]:
        season = "winter"
    elif month in [3, 4, 5]:
        season = "spring"
    elif month in [6, 7, 8]:
        season = "summer"
    else:
        season = "autumn"

    if 6 <= hour < 18:
        day_night = "day"
    else:
        day_night = "night"

    return f"./images/{season}_{day_night}.png"


async def create_avatar():
    bg_file = get_background_name()

    try:
        img = Image.open(bg_file)
        img = img.resize((500, 500))  # O'lchamni to'g'rilash
    except:
        img = Image.new('RGB', (500, 500), color=(33, 150, 243))

    d = ImageDraw.Draw(img)
    now = datetime.datetime.now().strftime("%H:%M")

    try:
        font = ImageFont.truetype("arial.ttf", 150)
    except:
        font = ImageFont.load_default()

    d.text((80, 150), now, fill=(255, 255, 255), font=font)
    img.save('avatar.png')

async def update_profile_photo():
    try:
        await client.start(password=tg_password)
    except Exception as e:
        print(f"Login qilishda xato: {e}")
        return

    me = await client.get_me()
    print(f"Muvaffaqiyatli kirdingiz: {me.first_name} (@{me.username})")

    while True:
        try:
            await create_avatar()

            file = await client.upload_file('avatar.png')
            await client(functions.photos.UploadProfilePhotoRequest(file=file))
            print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Avatar yangilandi!")

            photos = await client.get_profile_photos('me', limit=1)

            if len(photos) > 1:
                old_photos = photos[1:]
                await client(functions.photos.DeletePhotosRequest(id=old_photos))
                print(f"Eski rasmlar ({len(old_photos)} ta) o'chirildi.")

        except Exception as e:
            print(f"Xato yuz berdi: {e}")

        await asyncio.sleep(60)


if __name__ == '__main__':
    try:
        asyncio.run(update_profile_photo())
    except KeyboardInterrupt:
        print("Dastur to'xtatildi.")