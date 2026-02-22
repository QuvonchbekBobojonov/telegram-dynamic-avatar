import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

ai_key = os.getenv('GEMINI_API_KEY')
model_name = 'gemini-2.0-flash'

def test_model():
    print(f"Testing model: {model_name}...")
    if not ai_key:
        print("Xatto: GEMINI_API_KEY topilmadi!")
        return

    try:
        genai.configure(api_key=ai_key)
        model = genai.GenerativeModel(model_name)
        
        prompt = "Assalomu alaykum, o'zingni tanishtir."
        response = model.generate_content(prompt)
        
        if response and response.text:
            print("\n--- AI JAVOBI ---")
            print(response.text)
            print("-----------------\n")
            print("Muvaffaqiyatli: Model ishlayapti!")
        else:
            print("Xato: Model bo'sh javob qaytardi.")
            
    except Exception as e:
        print(f"Xatolik yuz berdi: {e}")

if __name__ == "__main__":
    test_model()
