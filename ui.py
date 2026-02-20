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

        # ---------------- Cloud Layer ----------------
        # self.cloud_layer = QLabel(self)
        # self.cloud_layer.setPixmap(QPixmap("assets/icons/cloud.png"))
        # self.cloud_layer.setScaledContents(True)
        
        # # Tightened cloud size to encase the bar better
        # self.cloud_layer.setFixedSize(500, 130)
        # self.cloud_layer.move(-10, 30)
        # self.cloud_layer.lower() 

        # self.cloud_opacity = QGraphicsOpacityEffect()
        # self.cloud_opacity.setOpacity(0.28)
        # self.cloud_layer.setGraphicsEffect(self.cloud_opacity)

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

        # ---------------- Decoration (The Bow) ----------------
        self.bow = QLabel(self)

        original_pixmap = QPixmap("assets/icons/bow.png")

        transform = QPixmap(original_pixmap.size())
        transform.fill(Qt.GlobalColor.transparent)

        painter = QPainter(transform)
        painter.translate(original_pixmap.width()/2, original_pixmap.height()/2)
        painter.rotate(0)  # ← tilt angle here
        painter.translate(-original_pixmap.width()/2, -original_pixmap.height()/2)
        painter.drawPixmap(0, 0, original_pixmap)
        painter.end()

        self.bow.setPixmap(transform)
        self.bow.setScaledContents(True)
        self.bow.setFixedSize(36, 36)
        self.bow.hide()

        # Assembly
        self.main_layout.addWidget(self.container)
        self.main_layout.addWidget(self.segment_container)

        self.companion = Companion()
        self.companion.show()
        # self.start_cloud_animation()
        self.apply_theme()
        self.move_top_right()
        self.set_status("ready")

    # def start_cloud_animation(self):
    #     self.cloud_anim = QPropertyAnimation(self.cloud_layer, b"pos")
    #     self.cloud_anim.setDuration(5000)
    #     self.cloud_anim.setStartValue(QPoint(20, 20))
    #     self.cloud_anim.setEndValue(QPoint(20, 28)) # Subtle floating
    #     self.cloud_anim.setEasingCurve(QEasingCurve.Type.InOutSine)
    #     self.cloud_anim.setLoopCount(-1)
    #     self.cloud_anim.start()

    def apply_theme(self):
        if self.personality == "anime":
            self.container.setStyleSheet("""
                    background: qlineargradient(
                        x1:0, y1:0, x2:0, y2:1,
                        stop:0 #ffe4f5,
                        stop:1 #ffcce8
                    );
                    border-radius: 29px;
                    border: 1px solid #ffb3df;
                    """)
         
            self.input.setStyleSheet("background: transparent; border: none; color: #444;")
            self.send_btn.setIcon(QIcon("assets/icons/send_dark.png"))
            self.send_btn.setStyleSheet("QPushButton { background-color: white; border-radius: 19px; } QPushButton:hover { background-color: #ffe0f2; }")
            self.segment_container.setStyleSheet("background-color: rgba(255, 200, 230, 220); border-radius: 22px;")
            self.segment_highlight.setStyleSheet("background-color: white; border-radius: 18px;")
            
            # Repositioned Bow: Higher Y (10) and further right (405)
            self.bow.show()
            self.bow.raise_()
            container_pos = self.container.pos()
            self.bow.move(container_pos.x() + self.container.width() - 36,
                        container_pos.y() - 18)
        else:
            self.container.setStyleSheet("background-color: rgba(20, 20, 25, 240); border-radius: 29px; border: 1px solid #333;")
            self.input.setStyleSheet("background: transparent; border: none; color: white;")
            self.send_btn.setIcon(QIcon("assets/icons/send.png"))
            self.send_btn.setStyleSheet("QPushButton { background-color: rgba(80, 80, 100, 230); border-radius: 19px; } QPushButton:hover { background-color: rgba(110, 110, 140, 230); }")
            self.segment_container.setStyleSheet("background-color: rgba(40, 40, 50, 220); border-radius: 22px;")
            self.segment_highlight.setStyleSheet("background-color: rgba(90, 90, 110, 240); border-radius: 18px;")
            self.bow.hide()

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
        self.thread = QThread()
        self.worker = Worker(goal)
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(lambda: (self.set_status("ready"), self.thread.quit()))
        self.worker.error.connect(lambda: (self.set_status("error"), self.thread.quit()))
        self.thread.start()
        self.input.clear()

    def set_status(self, state):
        colors = {"ready": "#2ecc71", "running": "#3498db", "error": "#e74c3c"}
        self.status_dot.setStyleSheet(f"background-color: {colors[state]}; border-radius: 7px;")

    def move_top_right(self):
        screen = QApplication.primaryScreen().geometry()
        # Adjusted for the new wider/taller window
        self.move(screen.width() - self.width() - 40, 40)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CommandBar()
    window.show()
    sys.exit(app.exec())