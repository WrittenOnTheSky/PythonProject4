# ==================== project_root/plugins/qwen3_analyzer/plugin.py ====================
from core.сore_api import api

class Plugin:
    def __init__(self):
        pass

    def qwen3_analyze(self, data):
        """
        Принимает мульти-ввод:
        - data['image'] : PIL.Image
        - data['text'] : str
        - data['audio'] : bytes
        """
        # Здесь будет вызов локальной модели Qwen3 через Ollama
        # Для MVP просто эхо данных
        result = {
            "image_received": bool(data.get("image")),
            "text_received": bool(data.get("text")),
            "audio_received": bool(data.get("audio")),
            "analysis": "Модель пока не подключена, это заглушка"
        }
        return result
