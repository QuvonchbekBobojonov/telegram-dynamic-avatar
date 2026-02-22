import os
import google.generativeai as genai
from dotenv import load_dotenv
import asyncio

load_dotenv()
ai_key = os.getenv('GEMINI_API_KEY')

async def list_available_models():
    if not ai_key:
        print("Xatto: GEMINI_API_KEY topilmadi!")
        return

    try:
        genai.configure(api_key=ai_key)
        print("Sizning API kalitingiz mosh keluvchi modellar ro'yxati:\n")
        
        # Use a simple list to avoid any async issues if list_models isn't async
        models = genai.list_models()
        for m in models:
            if 'generateContent' in m.supported_generation_methods:
                print(f" - {m.name} ({m.display_name})")
                
    except Exception as e:
        print(f"Xatolik yuz berdi: {e}")

if __name__ == "__main__":
    asyncio.run(list_available_models())
