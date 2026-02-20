import sys
import os
import random
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLineEdit,
    QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QGraphicsOpacityEffect
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QObject, QSize, QPropertyAnimation, QEasingCurve, QPoint
from PyQt6.QtGui import QFont, QColor, QIcon, QPixmap
from PyQt6.QtGui import QPainter
from PyQt6.QtWidgets import QGraphicsDropShadowEffect


# --- Mock imports for functionality ---
try:
    from companion import Companion
    from planner import decide_next_action
    from controller import execute
except ImportError:
    class Companion(QWidget):
        def __init__(self): super().__init__(); self.animations = {}
        def speak(self, t): pass
        def set_state(self, s): pass
    def decide_next_action(g, p): return {"action": "execute_plan", "plan": []}
    def execute(s): pass

class Worker(QObject):
    finished = pyqtSignal()
    error = pyqtSignal()

    def __init__(self, goal):
        super().__init__()
        self.goal = goal

    def run(self):
        try:
            action = decide_next_action(self.goal, [])
            if action.get("action") == "execute_plan":
                for step in action["plan"]: execute(step)
            self.finished.emit()
        except: self.error.emit()

class CommandBar(QWidget):
    def __init__(self):
        super().__init__()
        self.personality = "robo"
        
        # ---------------- Window Setup ----------------
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # INCREASED WINDOW HEIGHT to 220 so the bow isn't cut off at the top
        self.setFixedSize(480, 220)

        # ---------------- Main Layout ----------------
        self.main_layout = QVBoxLayout(self)
        # Added more top margin (40) to give the bow "headroom"
        self.main_layout.setContentsMargins(30, 40, 30, 20)
        self.main_layout.setSpacing(12)

        self.cloud_layer = QLabel(self)

        original_cloud = QPixmap("assets/icons/cloud5.png")

        transform = QPixmap(original_cloud.size())
        transform.fill(Qt.GlobalColor.transparent)

        painter = QPainter(transform)
        painter.translate(original_cloud.width()/2, original_cloud.height()/2)
        painter.rotate(-12)   # ← anticlockwise tilt
        painter.translate(-original_cloud.width()/2, -original_cloud.height()/2)
        painter.drawPixmap(0, 0, original_cloud)
        painter.end()

        # Small cloud
        self.cloud_layer.setFixedSize(90, 70)

        # Temporary position (will adjust later)
        self.cloud_layer.move(0, 0)

      

        # ---------------- Textbar Container ----------------
        self.container = QWidget()
        self.container.setFixedHeight(58)
        self.container.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        
        container_layout = QHBoxLayout(self.container)
        container_layout.setContentsMargins(18, 0, 12, 0)
        container_layout.setSpacing(10)

        self.status_dot = QLabel()
        self.status_dot.setFixedSize(14, 14)

        self.input = QLineEdit()
        self.input.setPlaceholderText("Ask your desktop...")
        self.input.setFont(QFont("Segoe UI", 12))
        self.input.returnPressed.connect(self.handle_command)

        self.send_btn = QPushButton()
        self.send_btn.setFixedSize(38, 38)
        self.send_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.send_btn.clicked.connect(self.handle_command)

        container_layout.addWidget(self.status_dot)
        container_layout.addWidget(self.input)
        container_layout.addWidget(self.send_btn)

        # ---------------- Segmented Control ----------------
        self.segment_container = QWidget()
        self.segment_container.setFixedSize(160, 44)
        self.segment_container.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        self.segment_highlight = QWidget(self.segment_container)
        self.segment_highlight.setFixedSize(76, 36)
        self.segment_highlight.move(80, 4)

        seg_layout = QHBoxLayout(self.segment_container)
        seg_layout.setContentsMargins(4, 4, 4, 4)
        seg_layout.setSpacing(0)

        self.anime_btn = QPushButton("👧")
        self.robo_btn = QPushButton("🤖")
        for btn in (self.anime_btn, self.robo_btn):
            btn.setFixedSize(76, 36)
            btn.setFlat(True)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet("background: transparent; border: none; font-size: 16pt;")
        
        seg_layout.addWidget(self.anime_btn)
        seg_layout.addWidget(self.robo_btn)

        self.anime_btn.clicked.connect(lambda: self.switch_personality("anime"))
        self.robo_btn.clicked.connect(lambda: self.switch_personality("robo"))


# --- Cloud Decoration ---
        self.cloud_layer = QLabel(self)

        cloud_pixmap = QPixmap("assets/icons/cloud5.png").scaled(
            130, 70,   # bigger now
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )

        rotated_cloud = QPixmap(cloud_pixmap.size())
        rotated_cloud.fill(Qt.GlobalColor.transparent)

        cloud_painter = QPainter(rotated_cloud)
        cloud_painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        cloud_painter.translate(cloud_pixmap.width()/2, cloud_pixmap.height()/2)
        cloud_painter.rotate(-10)   # slightly more tilt
        cloud_painter.translate(-cloud_pixmap.width()/2, -cloud_pixmap.height()/2)
        cloud_painter.drawPixmap(0, 0, cloud_pixmap)
        cloud_painter.end()

        self.cloud_layer.setPixmap(rotated_cloud)
        self.cloud_layer.setFixedSize(rotated_cloud.size())
        self.cloud_layer.hide()

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(12)
        shadow.setOffset(0, 3)
        shadow.setColor(QColor(0, 0, 0, 60))
        self.cloud_layer.setGraphicsEffect(shadow)


        self.cloud_anim = QPropertyAnimation(self.cloud_layer, b"pos")
        self.cloud_anim.setDuration(6000)
        self.cloud_anim.setEasingCurve(QEasingCurve.Type.InOutSine)
        self.cloud_anim.setLoopCount(-1)


      # --- Bow Decoration ---
        self.bow = QLabel(self)

        bow_pixmap = QPixmap("assets/icons/bow.png").scaled(
            36, 36,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )

        rotated_bow = QPixmap(bow_pixmap.size())
        rotated_bow.fill(Qt.GlobalColor.transparent)

        bow_painter = QPainter(rotated_bow)
        bow_painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        bow_painter.translate(bow_pixmap.width()/2, bow_pixmap.height()/2)
        bow_painter.rotate(6)  # slight tilt
        bow_painter.translate(-bow_pixmap.width()/2, -bow_pixmap.height()/2)
        bow_painter.drawPixmap(0, 0, bow_pixmap)
        bow_painter.end()

        self.bow.setPixmap(rotated_bow)
        self.bow.setFixedSize(rotated_bow.size())
        self.bow.hide()


        # ---------------- Assembly ----------------
        self.main_layout.addWidget(self.container)
        self.main_layout.addWidget(self.segment_container)

        self.setLayout(self.main_layout)

        self.companion = Companion()
        self.companion.show()

        self.apply_theme()
        self.move_top_right()
        self.set_status("ready")


    def apply_theme(self):
        if self.personality == "anime":
            self.container.setStyleSheet("""
                background: qlineargradient(
                    x1:0, y1:0, x2:0, y2:1,
                    stop:0 #fff3fb,
                    stop:0.4 #ffe6f5,
                    stop:1 #ffcce8
                );
                border-radius: 29px;
                border: 1px solid #ffb3df;
            """)          
            
            self.status_dot.setStyleSheet("""
                background-color: #6fdc9e;
                border-radius: 7px;
            """)
            
            self.input.setStyleSheet("background: transparent; border: none; color: #444;")
            self.send_btn.setIcon(QIcon("assets/icons/send_dark.png"))
            self.send_btn.setStyleSheet("""
                QPushButton {
                    background: qradialgradient(
                        cx:0.5, cy:0.4, radius:0.9,
                        stop:0 #ffffff,
                        stop:1 #f5d7e8
                    );
                    border: 1px solid #ffb3df;
                    border-radius: 19px;
                }
                QPushButton:hover {
                    background: qradialgradient(
                        cx:0.5, cy:0.4, radius:0.9,
                        stop:0 #ffffff,
                        stop:1 #ffd9f2
                    );
                }
            """)
            self.segment_container.setStyleSheet("background-color: rgba(255, 200, 230, 220); border-radius: 22px;")
            self.segment_highlight.setStyleSheet("background-color: white; border-radius: 18px;")
            
            # Repositioned Bow: Higher Y (10) and further right (405)
            self.bow.show()
            self.bow.raise_()
            container_pos = self.container.pos()
            self.bow.move(container_pos.x() + self.container.width() - 45,
                        container_pos.y() - 18)
            

            self.cloud_layer.show()
            self.cloud_layer.raise_()

            container_pos = self.container.pos()

            self.cloud_layer.move(
                container_pos.x() - 10,
                container_pos.y() - 40
            )
            start_pos = self.cloud_layer.pos()
            self.cloud_anim.setStartValue(start_pos)
            self.cloud_anim.setEndValue(start_pos + QPoint(0, 4))
            self.cloud_anim.start()

        else:
            self.container.setStyleSheet("background-color: rgba(20, 20, 25, 240); border-radius: 29px; border: 1px solid #333;")
            self.input.setStyleSheet("background: transparent; border: none; color: white;")
            self.send_btn.setIcon(QIcon("assets/icons/send.png"))
            self.send_btn.setStyleSheet("QPushButton { background-color: rgba(80, 80, 100, 230); border-radius: 19px; } QPushButton:hover { background-color: rgba(110, 110, 140, 230); }")
            self.segment_container.setStyleSheet("background-color: rgba(40, 40, 50, 220); border-radius: 22px;")
            self.segment_highlight.setStyleSheet("background-color: rgba(90, 90, 110, 240); border-radius: 18px;")
            self.bow.hide()
            self.cloud_layer.hide()

    def switch_personality(self, p):
        if self.personality == p: return
        self.personality = p
        target_x = 4 if p == "anime" else 80
        self.anim = QPropertyAnimation(self.segment_highlight, b"pos")
        self.anim.setDuration(250)
        self.anim.setEndValue(QPoint(target_x, 4))
        self.anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.anim.start()
        self.apply_theme()




    def handle_command(self):
        goal = self.input.text().strip()
        if not goal: return
        self.set_status("running")

        if hasattr(self, "companion"):
            self.companion.set_state("running")
            self.companion.speak("Working on it...")

        self.thread = QThread()
        self.worker = Worker(goal)

        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.on_finished)
        self.worker.error.connect(self.on_error)
        self.worker.finished.connect(self.thread.quit)
        self.worker.error.connect(self.thread.quit)


        self.thread.start()
        self.input.clear()

    def set_status(self, state):
        colors = {"ready": "#2ecc71", "running": "#3498db", "error": "#e74c3c"}
        self.status_dot.setStyleSheet(f"background-color: {colors[state]}; border-radius: 7px;")

    def move_top_right(self):
        screen = QApplication.primaryScreen().geometry()
        # Adjusted for the new wider/taller window
        self.move(screen.width() - self.width() - 40, 40)

    def on_finished(self):
        self.set_status("ready")
        if hasattr(self, "companion"):
            self.companion.set_state("ready")
            self.companion.speak("Done.")

    def on_error(self):
        self.set_status("error")
        if hasattr(self, "companion"):
            self.companion.set_state("error")
            self.companion.speak("Something went wrong.")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CommandBar()
    window.show()
    sys.exit(app.exec())