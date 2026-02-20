import os
import asyncio
from telethon import TelegramClient
from dotenv import load_dotenv

# .env faylini yuklaymiz
load_dotenv()

api_id = os.getenv('API_ID')
api_hash = os.getenv('API_HASH')
tg_password = os.getenv('TG_PASSWORD')

async def add_session():
    print("=== Yangi Telegram Seansini Qo'shish ===")
    session_name = input("Yangi seans uchun nom kiriting (masalan: shaxsiy, ish): ").strip()
    
    if not session_name:
        print("Xato: Seans nomi bo'sh bo'lishi mumkin emas!")
        return

    client = TelegramClient(session_name, api_id, api_hash)
    
    try:
        # 2FA (ikki bosqichli parol) bo'lsa .env dan oladi yoki terminaldan so'raydi
        await client.start(password=lambda: tg_password or input("Ikki bosqichli parolingizni kiriting: "))
        me = await client.get_me()
        print(f"\nMuvaffaqiyatli bog'landi!")
        print(f"Foydalanuvchi: {me.first_name} (@{me.username})")
        print(f"Fayl yaratildi: {session_name}.session")
        print("\nEndi 'python main.py' buyrug'ini bersangiz, ushbu akkaunt ham avtomat yangilanadi.")
    except Exception as e:
        print(f"Xato yuz berdi: {e}")
    finally:
        await client.disconnect()

if __name__ == '__main__':
    asyncio.run(add_session())
