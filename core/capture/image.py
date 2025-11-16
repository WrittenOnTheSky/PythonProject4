"""
Методы захвата изображения через selection_capture
- select_area(): возвращает {'image': PIL.Image, 'rect': (x,y,w,h)}
"""


from selection_capture import capture_area


def select_area():
    """Выбор области экрана и возврат PIL.Image + координаты"""
    img, rect = capture_area() # capture_area() из selection_capture.py
    return {"image": img, "rect": rect}