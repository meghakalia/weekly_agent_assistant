from dotenv import load_dotenv
import os
import google.generativeai as genai

# Load variables from .env
load_dotenv()

# Read the key
api_key = os.getenv("GEMINI_API_KEY")

# Configure the client
genai.configure(api_key=api_key)

# Create a model and send a prompt
model = genai.GenerativeModel("gemini-2.5-flash")

try:
    response = model.generate_content("Hello Gemini via dotenv!")
    print("Model response:\n", response.text)
except Exception as e:
    print("Error:", e)
