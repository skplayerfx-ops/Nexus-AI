import os
import google.generativeai as genai

class GeminiEngine:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')

    def generate(self, prompt: str, system_prompt: str = "") -> str:
        try:
            full_prompt = f"{system_prompt}\n\nUser: {prompt}" if system_prompt else prompt
            response = self.model.generate_content(full_prompt)
            return response.text
        except Exception as e:
            return f"Gemini Error: {str(e)}"
