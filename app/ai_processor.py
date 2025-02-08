from openai import OpenAI
from config import OPENAI_API_KEY  # API-ключ для ChatGPT

class AIProcessor:
    """Обрабатывает запрос к OpenAI API"""
    def __init__(self):
        self.client = OpenAI(api_key=OPENAI_API_KEY)

    def analyze_image_with_text(self, image_base64, text_prompt):
        """Анализирует изображение вместе с текстом, используя OpenAI"""
        completion = self.client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": text_prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_base64}",
                            }
                        },
                    ],
                }
            ],
        )
        return completion.choices[0].message.content
