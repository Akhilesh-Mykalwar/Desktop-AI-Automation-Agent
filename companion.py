import os
from PyQt6.QtWidgets import QWidget, QLabel
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QMovie
from PyQt6.QtWidgets import QApplication


class Companion(QWidget):

    def __init__(self):
        super().__init__()

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )

        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.setFixedSize(180, 180)

        self.label = QLabel(self)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setGeometry(0, 0, 180, 180)

        self.animations = {
            "ready": "assets/anime/IDLE.gif",
            "running": "assets/anime/RUN.gif",
            "error": "assets/anime/ERROR.gif"
        }

        self.current_movie = None
        self.set_state("ready")

        self.move_bottom_right()

    def move_bottom_right(self):
        screen = QApplication.primaryScreen().geometry()
        x = screen.width() - self.width() - 40
        y = screen.height() - self.height() - 60
        self.move(x, y)

    def set_state(self, state):
        path = self.animations.get(state)

        if not path or not os.path.exists(path):
            return

        if self.current_movie:
            self.current_movie.stop()

        self.current_movie = QMovie(path)
        self.label.setMovie(self.current_movie)
        self.current_movie.start()
