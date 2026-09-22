import urllib.parse

class ImageEngine:
    @staticmethod
    def generate_url(prompt: str, width: int = 1024, height: int = 1024) -> str:
        encoded_prompt = urllib.parse.quote(prompt.strip())
        return f"https://image.pollinations.ai/prompt/{encoded_prompt}?width={width}&height={height}&seed=42&nologo=true&model=flux"
