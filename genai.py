import google.generativeai as genai
import os
from config import GENAI_API_KEY

genai.configure(api_key=GENAI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

response = model.generate_content("한국말로 해줘. 음식추천점 ")
print(response.text)