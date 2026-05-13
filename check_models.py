import os
import django
from decouple import config
from langchain_google_genai import ChatGoogleGenerativeAI
import google.generativeai as genai

# Load API Key
api_key = config('GEMINI_API_KRY', default=None) or config('GEMINI_API_KEY', default=None)

if not api_key:
    print("❌ API Key not found.")
else:
    genai.configure(api_key=api_key)
    print("Listing available models:")
    try:
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                print(f" - {m.name}")
    except Exception as e:
        print(f"❌ Error: {e}")
