import os
from google import genai
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("No GEMINI_API_KEY found")
    exit(1)

client = genai.Client(api_key=api_key)

print(f"Client models dir: {dir(client.models)}")
