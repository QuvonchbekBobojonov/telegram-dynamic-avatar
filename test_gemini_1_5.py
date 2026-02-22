import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

ai_key = os.getenv('GEMINI_API_KEY')
model_name = 'gemini-1.5-flash'

def test_model():
    print(f"Testing model: {model_name}...")
    if not ai_key:
        print("Xatto: GEMINI_API_KEY topilmadi!")
        return

    try:
        genai.configure(api_key=ai_key)
        model = genai.GenerativeModel(model_name)
        
        prompt = "Salom, yaxshisizlarmi?"
        response = model.generate_content(prompt)
        
        if response and response.text:
            print("\n--- AI JAVOBI ---")
            print(response.text)
            print("-----------------\n")
        else:
            print("Xato: Model bo'sh javob qaytardi.")
            
    except Exception as e:
        print(f"Xatolik: {e}")

if __name__ == "__main__":
    test_model()
