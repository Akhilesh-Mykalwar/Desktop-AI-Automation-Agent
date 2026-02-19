import os
from PyQt6.QtWidgets import QWidget, QLabel, QApplication
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QMovie
from PyQt6.QtWidgets import QGraphicsDropShadowEffect
from PyQt6.QtGui import QColor

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

        # Character display
        self.label = QLabel(self)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setGeometry(0, 0, 180, 180)

        # Animations
        self.animations = {
            "ready": "assets/anime/IDLE.gif",
            "running": "assets/anime/RUN.gif",
            "error": "assets/anime/ERROR.gif"
        }

        self.current_movie = None

        # Speech bubble (separate window)
        self.bubble = QLabel()
        self.bubble.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.bubble.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)


        shadow = QGraphicsDropShadowEffect(self.bubble)
        shadow.setBlurRadius(25)
        shadow.setXOffset(0)
        shadow.setYOffset(6)
        shadow.setColor(QColor(0, 0, 0, 180))


        self.bubble.setGraphicsEffect(shadow)

        self.bubble.setWordWrap(True)
        self.bubble.setMaximumWidth(240)

        self.bubble.setStyleSheet("""
            QLabel {
                background-color: rgba(255, 255, 255, 245);
                color: black;
                border-radius: 16px;
                padding: 14px 18px;
                border: 1px solid rgba(0, 0, 0, 30);
                font-size: 11pt;
            }
        """)




        self.bubble.hide()

        self.move_bottom_right()
        self.set_state("ready")

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

    def speak(self, text):
        self.bubble.setText(text)
        self.bubble.adjustSize()

        companion_pos = self.pos()

        bubble_width = self.bubble.width()
        bubble_height = self.bubble.height()

        x = companion_pos.x() + (self.width() - bubble_width) // 2
        y = companion_pos.y() - bubble_height - 4


        self.bubble.move(x, y)
        self.bubble.show()

        QTimer.singleShot(3000, self.bubble.hide)
