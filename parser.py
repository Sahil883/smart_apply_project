from google import generativeai
from dotenv import load_dotenv
import os
load_dotenv()
generativeai.configure(api_key=os.getenv('GEMINI_API_KEY'))

model=generativeai.GenerativeModel(model_name="gemini-2.0-flash")
response = model.generate_content('Teach me about how an LLM works')

print(response.text)