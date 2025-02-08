from flask import Flask, render_template, request, jsonify, Response
from ai_processor import AIProcessor
from image_handler import ImageHandler
from auth_manager import AuthManager
from markupsafe import Markup
import json


class FlaskApp:
    """Основное веб-приложение на Flask"""

    def __init__(self):
        self.app = Flask(__name__)
        self.ai_processor = AIProcessor()
        self.image_handler = ImageHandler()

        # Определение маршрутов
        self.setup_routes()

    def setup_routes(self):
        """Настройка маршрутов Flask"""

        @self.app.route("/")
        def index():
            return render_template("base.html", result=None)

        @self.app.route("/process", methods=["POST"])
        def process():
            """Обработчик формы (загрузка изображения + текст)"""
            try:
                uploaded_file = request.files.get("image_upload")
                text_prompt = request.form.get("text_prompt", "").strip()

                if not uploaded_file or not text_prompt:
                    return render_template("base.html", result="Загрузите фото и введите запрос.")

                if len(text_prompt.split()) > 300:
                    return render_template("base.html", result="Текстовый запрос не должен превышать 300 слов.")

                # Проверка формата изображения
                image_info = self.image_handler.validate_image(uploaded_file)
                if not image_info:
                    return render_template("base.html",
                                           result="Загрузите корректный файл изображения (jpg, png, bmp, gif и др.)")

                image_base64 = self.image_handler.encode_image_to_base64(uploaded_file)
                raw_result = self.ai_processor.analyze_image_with_text(image_base64, text_prompt)

                print(f"Сырой результат: {raw_result}")
                formatted_result = self.format_result(raw_result)
                html_result = Markup(formatted_result)

                return render_template("base.html", result=html_result)

            except Exception as e:
                print(f"Ошибка обработки запроса: {str(e)}")
                return render_template("base.html", result=f"Ошибка: {str(e)}")

        @self.app.route("/api/process", methods=["POST"])
        def api_process():
            """API-обработчик (POST-запросы с изображением и текстом)"""
            try:
                api_key = request.headers.get("X-API-KEY")
                if not api_key or not AuthManager.is_valid_api_key(api_key):
                    return jsonify({"error": "Unauthorized"}), 401

                uploaded_file = request.files.get("image")
                text_prompt = request.form.get("text_prompt", "").strip()

                if not uploaded_file or not text_prompt:
                    return jsonify({"error": "Image and text prompt are required"}), 400

                # Проверка формата изображения
                image_info = self.image_handler.validate_image(uploaded_file)
                if not image_info:
                    return jsonify({"error": "Invalid image format"}), 400

                image_base64 = self.image_handler.encode_image_to_base64(uploaded_file)
                raw_result = self.ai_processor.analyze_image_with_text(image_base64, text_prompt)

                formatted_result = self.format_result(raw_result)

                # Корректный возврат JSON с кодировкой UTF-8
                response_data = json.dumps({"result": formatted_result}, ensure_ascii=False)
                return Response(response_data, status=200, mimetype="application/json; charset=utf-8")

            except Exception as e:
                print(f"API Error: {str(e)}")
                response_data = json.dumps({"error": str(e)}, ensure_ascii=False)
                return Response(response_data, status=500, mimetype="application/json; charset=utf-8")

    @staticmethod
    def format_result(raw_text):
        """Форматирует текст в HTML"""
        paragraphs = raw_text.split("\n\n")  # Разделяем текст на абзацы
        formatted_paragraphs = [f"<p>{paragraph.strip()}</p>" for paragraph in paragraphs]
        return "\n".join(formatted_paragraphs)

    def run(self):
        """Запуск Flask-приложения"""
        self.app.run(debug=True, host="0.0.0.0")
