# ==================== project_root/selection_capture.py ====================
"""
Модуль выделения области экрана с мышью (Qt + mss).
- capture_area() возвращает PIL.Image и координаты выделенной области
- Никакого CoreApp или EventBus здесь нет
"""

from PySide6.QtWidgets import QApplication, QWidget
from PySide6.QtGui import QPainter, QColor, QPen
from PySide6.QtCore import Qt, QRect, QPoint
import mss
from PIL import Image
import sys

class SelectionWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setWindowState(Qt.WindowFullScreen)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.origin = QPoint()
        self.end = QPoint()
        self.dragging = False
        self.selected_rect = None

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = True
            self.origin = event.pos()
            self.end = event.pos()
            self.update()

    def mouseMoveEvent(self, event):
        if self.dragging:
            self.end = event.pos()
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = False
            rect = QRect(self.origin, self.end).normalized()
            self.selected_rect = rect
            self.close()

    def paintEvent(self, event):
        if not self.dragging:
            return
        painter = QPainter(self)
        painter.setOpacity(0.3)
        painter.fillRect(self.rect(), Qt.black)
        painter.setOpacity(1)
        pen = QPen(QColor(0, 180, 255), 2)
        painter.setPen(pen)
        painter.drawRect(QRect(self.origin, self.end))


def capture_area():
    app = QApplication.instance() or QApplication(sys.argv)

    selector = SelectionWidget()
    selector.show()

    app.exec()

    rect = selector.selected_rect
    if rect is None:
        return None, None

    x = rect.x()
    y = rect.y()
    w = rect.width()
    h = rect.height()

    with mss.mss() as sct:
        monitor = {'top': y, 'left': x, 'width': w, 'height': h}
        sct_img = sct.grab(monitor)
        img = Image.frombytes('RGB', sct_img.size, sct_img.rgb)

    return img, (x, y, w, h)
