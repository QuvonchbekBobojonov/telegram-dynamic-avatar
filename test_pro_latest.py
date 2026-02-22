import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

ai_key = os.getenv('GEMINI_API_KEY')
model_name = 'gemini-pro-latest'

def test_model():
    print(f"Testing model: {model_name}...")
    try:
        genai.configure(api_key=ai_key)
        model = genai.GenerativeModel(model_name)
        response = model.generate_content("Salom")
        print(response.text)
    except Exception as e:
        print(f"Xatolik: {e}")

if __name__ == "__main__":
    test_model()
