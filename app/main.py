from flask import Flask, render_template, request
from openai import OpenAI
import base64
from datetime import datetime
from config import OPENAI_API_KEY  # Импортируем API-ключ из config.py
from markupsafe import Markup
import imghdr  # Для определения типа изображения

app = Flask(__name__)

# Инициализация клиента OpenAI
client = OpenAI(api_key=OPENAI_API_KEY)

# Функция для кодирования изображения в Base64
def encode_image_to_base64(image_file):
    return base64.b64encode(image_file.read()).decode("utf-8")

# Функция для анализа изображения и текста
def analyze_image_with_text(image_base64, text_prompt):
    completion = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": text_prompt},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/{image_base64.split(',')[0]};base64,{image_base64}",
                        }
                    },
                ],
            }
        ],
    )
    return completion.choices[0].message.content

# Функция для форматирования текста
def format_result(raw_text):
    paragraphs = raw_text.split("\n\n")  # Разделяем текст на абзацы
    formatted_paragraphs = [f"<p>{paragraph.strip()}</p>" for paragraph in paragraphs]  # Заворачиваем каждый абзац в <p>
    return "\n".join(formatted_paragraphs)  # Возвращаем HTML-код с абзацами

@app.route("/")
def index():
    return render_template("base.html", result=None)

@app.route("/process", methods=["POST"])
def process():
    try:
        # Получаем файл изображения и текстовый запрос из формы
        uploaded_file = request.files.get("image_upload")
        text_prompt = request.form.get("text_prompt", "").strip()

        # Проверка: файл и текст должны быть предоставлены
        if not uploaded_file or not text_prompt:
            return render_template("base.html", result="Загрузите фото и введите запрос.")

        # Проверка длины текстового запроса
        if len(text_prompt.split()) > 300:
            return render_template("base.html", result="Текстовый запрос не должен превышать 300 слов.")

        # Проверка типа файла
        file_type = imghdr.what(uploaded_file)
        if not file_type:
            return render_template("base.html", result="Загрузите корректный файл изображения (jpg, png, bmp, gif и др.)")

        # Создание уникального имени для загруженного файла
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        uploaded_file.filename = f"{timestamp}.{file_type}"

        # Кодирование изображения в Base64
        image_base64 = encode_image_to_base64(uploaded_file)

        # Отправка запроса в OpenAI API
        raw_result = analyze_image_with_text(image_base64, text_prompt)

        # Вывод сырого результата в терминал для проверки
        print(f"Сырой результат: {raw_result}")

        # Форматируем результат
        formatted_result = format_result(raw_result)

        # Используем Markup для безопасного отображения HTML
        html_result = Markup(formatted_result)

        # Возвращаем результат на страницу
        return render_template("base.html", result=html_result)

    except Exception as e:
        # Вывод ошибки в терминал для диагностики
        print(f"Ошибка обработки запроса: {str(e)}")
        return render_template("base.html", result=f"Ошибка: {str(e)}")

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
