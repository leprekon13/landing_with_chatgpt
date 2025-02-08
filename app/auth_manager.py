from api_config import ALLOWED_API_KEYS  # API-ключи для доступа к API

class AuthManager:
    """Проверяет API-ключи"""

    @staticmethod
    def is_valid_api_key(api_key):
        """Проверяет, существует ли API-ключ в списке разрешенных"""
        return api_key in ALLOWED_API_KEYS
