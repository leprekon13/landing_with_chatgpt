from flask import Flask, render_template, request, jsonify, Response
from openai import OpenAI
import base64
import json
from datetime import datetime
from config import OPENAI_API_KEY  # API-ключ для ChatGPT
from api_config import ALLOWED_API_KEYS  # API-ключи для доступа к API
from markupsafe import Markup
import imghdr  # Определение типа изображения

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
                            "url": f"data:image/jpeg;base64,{image_base64}",
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
    formatted_paragraphs = [f"<p>{paragraph.strip()}</p>" for paragraph in paragraphs]
    return "\n".join(formatted_paragraphs)

# Проверка API-ключа
def is_valid_api_key(api_key):
    return api_key in ALLOWED_API_KEYS

@app.route("/")
def index():
    return render_template("base.html", result=None)

@app.route("/process", methods=["POST"])
def process():
    try:
        uploaded_file = request.files.get("image_upload")
        text_prompt = request.form.get("text_prompt", "").strip()

        if not uploaded_file or not text_prompt:
            return render_template("base.html", result="Загрузите фото и введите запрос.")

        if len(text_prompt.split()) > 300:
            return render_template("base.html", result="Текстовый запрос не должен превышать 300 слов.")

        file_type = imghdr.what(uploaded_file)
        if not file_type:
            return render_template("base.html", result="Загрузите корректный файл изображения (jpg, png, bmp, gif и др.)")

        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        uploaded_file.filename = f"{timestamp}.{file_type}"

        image_base64 = encode_image_to_base64(uploaded_file)
        raw_result = analyze_image_with_text(image_base64, text_prompt)
        print(f"Сырой результат: {raw_result}")

        formatted_result = format_result(raw_result)
        html_result = Markup(formatted_result)
        return render_template("base.html", result=html_result)

    except Exception as e:
        print(f"Ошибка обработки запроса: {str(e)}")
        return render_template("base.html", result=f"Ошибка: {str(e)}")

@app.route("/api/process", methods=["POST"])
def api_process():
    try:
        api_key = request.headers.get("X-API-KEY")
        if not api_key or not is_valid_api_key(api_key):
            return jsonify({"error": "Unauthorized"}), 401

        uploaded_file = request.files.get("image")
        text_prompt = request.form.get("text_prompt", "").strip()

        if not uploaded_file or not text_prompt:
            return jsonify({"error": "Image and text prompt are required"}), 400

        file_type = imghdr.what(uploaded_file)
        if not file_type:
            return jsonify({"error": "Invalid image format"}), 400

        image_base64 = encode_image_to_base64(uploaded_file)
        raw_result = analyze_image_with_text(image_base64, text_prompt)

        formatted_result = format_result(raw_result)

        # Корректный возврат JSON с кодировкой UTF-8
        response_data = json.dumps({"result": formatted_result}, ensure_ascii=False)
        return Response(response_data, status=200, mimetype="application/json; charset=utf-8")

    except Exception as e:
        print(f"API Error: {str(e)}")
        response_data = json.dumps({"error": str(e)}, ensure_ascii=False)
        return Response(response_data, status=500, mimetype="application/json; charset=utf-8")

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
