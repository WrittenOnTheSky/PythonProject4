"""
Пример интеграции плагина qwen3_analyzer с CoreApp
- Тестовый запуск потока: захват экрана → мульти-ввод → локальный LLM
"""

from core_app import CoreApp
import plugins.qwen3_analyzer as qwen_plugin

# Создаем экземпляр CoreApp
app = CoreApp(plugins_path='plugins')

# Регистрируем плагин вручную для теста
qwen_plugin.register(app.plugin_manager._make_api())

# Пример запуска захвата
import threading

def start_capture():
    while True:
        # Захват области экрана каждые 10 секунд (пример)
        app.screen_capture()
        import time
        time.sleep(10)

# Запускаем capture loop в отдельном потоке
threading.Thread(target=start_capture, daemon=True).start()

# Запускаем основной цикл CoreApp (heartbeat и плагины)
app.start(heartbeat_interval=2.0)
