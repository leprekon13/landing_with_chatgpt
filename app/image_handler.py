import base64
import imghdr
from datetime import datetime


class ImageHandler:
    """Обрабатывает изображения: кодирование, проверка формата"""

    @staticmethod
    def encode_image_to_base64(image_file):
        """Кодирует изображение в Base64"""
        return base64.b64encode(image_file.read()).decode("utf-8")

    @staticmethod
    def validate_image(image_file):
        """Проверяет корректность формата изображения"""
        file_type = imghdr.what(image_file)
        if not file_type:
            return None
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        image_file.filename = f"{timestamp}.{file_type}"
        return image_file.filename, file_type
