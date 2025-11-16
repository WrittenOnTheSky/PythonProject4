# ==================== core/core_api.py ====================
"""
Core Capture API — предоставляет плагинам доступ к системным сенсорным функциям:
- image: захват экрана
- text: OCR/распознавание текста
- audio: запись аудио
"""

import core.capture.image as ci
import core.capture.text as ct
import core.capture.audio as ca

class CaptureAPI:
    def __init__(self):
        self.image = ci
        self.text = ct
        self.audio = ca

# Плагин получает объект API через ядро
api = CaptureAPI()
# Использование в плагине:
# img_dict = api.image.select_area()
# text = api.text.from_image(img)
# audio = api.audio.record(5)
