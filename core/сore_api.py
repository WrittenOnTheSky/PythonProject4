# ==================== project_root/core/core_api.py ====================
"""
Core API — единая точка доступа к возможностям ядра.
Плагины используют этот API для:
- захвата изображения
- захвата текста (OCR)
- захвата аудио

В будущем сюда можно добавлять новые модули
(вывод UI, системные функции, безопасность, синхронизация и т.д.).
"""

from core.capture import image, text, audio


class CoreAPI:
    """Основной интерфейс для плагинов и ядра."""
    def __init__(self):
        self.image = image      # select_area()
        self.text = text        # ocr(), ocr_from_image()
        self.audio = audio      # record(), record_snippet()


# Глобальный экземпляр API, который импортируют плагины
api = CoreAPI()
