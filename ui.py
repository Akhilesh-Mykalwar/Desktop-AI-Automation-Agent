import sys
import os
from companion import Companion
import random
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLineEdit,
    QVBoxLayout, QHBoxLayout, QLabel,
    QGraphicsDropShadowEffect
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor

from planner import decide_next_action
from controller import execute
from PyQt6.QtCore import QThread, pyqtSignal, QObject
from PyQt6.QtWidgets import QPushButton
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import QSize



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
                for step in action["plan"]:
                    execute(step)
            self.finished.emit()
        except:
            self.error.emit()



class CommandBar(QWidget):

    def __init__(self):
        super().__init__()

        # ---------------- Window Setup ----------------
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )

        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedWidth(420)
        self.setFixedHeight(140)

        # ---------------- Shadow ----------------



        # ---------------- Main Layout ----------------
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 15, 20, 15)
        main_layout.setSpacing(0)

        # Wrapper for shadow
        self.wrapper = QWidget()
        wrapper_layout = QVBoxLayout()
        wrapper_layout.setContentsMargins(0, 0, 0, 0)
        wrapper_layout.setSpacing(0)
        self.wrapper.setLayout(wrapper_layout)

        # Apply shadow to wrapper ONLY
        self.shadow = QGraphicsDropShadowEffect(self.wrapper)
        self.shadow.setBlurRadius(35)
        self.shadow.setXOffset(0)
        self.shadow.setYOffset(8)
        self.shadow.setColor(QColor(0, 0, 0, 180))
        self.wrapper.setGraphicsEffect(self.shadow)


        # ---------------- Textbar Container ----------------
        self.container = QWidget()
        self.container.setStyleSheet("""
                QWidget {
                    background-color: rgba(240, 240, 240, 230);
                    border-radius: 28px;
                }
            """)


        container_layout = QHBoxLayout()
        container_layout.setContentsMargins(15, 14, 15, 14)

        container_layout.setSpacing(8)

        # ---------------- Status Indicator ----------------
        self.status_dot = QLabel()
        self.status_dot.setFixedSize(14, 14)
        self.status_dot.setStyleSheet("""
            background-color: #2ecc71;
            border-radius: 7px;
        """)

        # ---------------- Input Field ----------------
        self.input = QLineEdit()
        self.input.setPlaceholderText("Ask your desktop...")
        self.input.setFont(QFont("Segoe UI", 13))
        self.input.returnPressed.connect(self.handle_command)

        self.input.setStyleSheet("""
            QLineEdit {
                background: transparent;
                border: none;
                color: #444;
                font-size: 12pt;
            }
        """)

        # ---------------- Send Button ----------------
       # ---------------- Send Button ----------------
        self.send_btn = QPushButton()
        self.send_btn.setFixedSize(36, 36)
        self.send_btn.setCursor(Qt.CursorShape.PointingHandCursor)

        self.send_btn.setIcon(QIcon("assets/icons/send.png"))
        self.send_btn.setIconSize(QSize(18, 18))

        self.send_btn.clicked.connect(self.handle_command)


        container_layout.addWidget(self.status_dot, alignment=Qt.AlignmentFlag.AlignVCenter)
        container_layout.addWidget(self.input)
        container_layout.addWidget(self.send_btn, alignment=Qt.AlignmentFlag.AlignVCenter)



        self.container.setLayout(container_layout)

        # ---------------- Segmented Control ----------------
        self.segment_container = QWidget()
        self.segment_container.setFixedSize(160, 44)

        self.segment_container.setStyleSheet("""
            QWidget {
                background-color: rgba(235, 235, 235, 230);
                border-radius: 22px;
            }
        """)

        segment_layout = QHBoxLayout()
        segment_layout.setContentsMargins(4, 4, 4, 4)
        segment_layout.setSpacing(0)

        self.anime_btn = QPushButton("👧")
        self.robo_btn = QPushButton("🤖")

        for btn in (self.anime_btn, self.robo_btn):
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setFixedSize(76, 36)
            btn.setStyleSheet("""
                QPushButton {
                    background: transparent;
                    border: none;
                    font-size: 16pt;
                }
            """)

        segment_layout.addWidget(self.anime_btn)
        segment_layout.addWidget(self.robo_btn)

        self.segment_container.setLayout(segment_layout)

        # Highlight (placed AFTER layout so it sits behind buttons)
        self.segment_highlight = QWidget(self.segment_container)
        self.segment_highlight.setGeometry(4, 4, 76, 36)
        self.segment_highlight.setStyleSheet("""
            background-color: white;
            border-radius: 18px;
        """)
        self.segment_highlight.lower()  # send behind buttons

        self.anime_btn.clicked.connect(lambda: self.switch_personality("anime"))
        self.robo_btn.clicked.connect(lambda: self.switch_personality("robo"))


        # ---------------- Add To Main Layout ----------------
        wrapper_layout.addWidget(self.container)
        wrapper_layout.addSpacing(8)
        wrapper_layout.addWidget(self.segment_container)

        main_layout.addWidget(self.wrapper)
        self.setLayout(main_layout)

        # ---------------- Personality State ----------------
        self.personality = "robo"

        # ---------------- Companion ----------------
        self.companion = Companion()
        self.companion.show()

        # ---------------- Final Setup ----------------
        self.move_top_right()
        self.apply_theme()



    # ---------------- Position Top Right ----------------
    def move_top_right(self):
        screen = QApplication.primaryScreen().geometry()
        x = screen.width() - self.width() - 40
        y = 40
        self.move(x, y)

    # ---------------- Status Colors ----------------
    def set_status(self, state):
        colors = {
            "ready": "#2ecc71",
            "running": "#3498db",
            "error": "#e74c3c"
        }

        self.status_dot.setStyleSheet(f"""
            background-color: {colors[state]};
            border-radius: 7px;
        """)

        if hasattr(self, "companion"):
            self.companion.set_state(state)


    # ---------------- Execute Command ----------------
    def handle_command(self):
        goal = self.input.text().strip()
        if not goal:
            return

        self.set_status("running")

        self.thread = QThread()
        self.worker = Worker(goal)
        self.worker.moveToThread(self.thread)



        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.on_finished)
        self.worker.error.connect(self.on_error)
        self.worker.finished.connect(self.thread.quit)
        self.worker.error.connect(self.thread.quit)


        if hasattr(self, "companion"):
            self.companion.speak("Working on it...")

        self.thread.start()

        self.input.clear()


    def on_finished(self):
        self.set_status("ready")
        if hasattr(self, "companion"):
            responses = [
                "Done.",
                "All set.",
                "Task complete.",
                "Finished.",
            ]

            self.companion.speak(random.choice(responses))



    def on_error(self):
        self.set_status("error")
        if hasattr(self, "companion"):
            self.companion.speak("Something went wrong.")



    def switch_personality(self, personality):
        self.personality = personality

        if personality == "anime":
            self.segment_highlight.move(4, 4)
        else:
            self.segment_highlight.move(80, 4)

        if personality == "anime":
            self.companion.animations = {
                "ready": "assets/anime/IDLE.gif",
                "running": "assets/anime/RUN.gif",
                "error": "assets/anime/ERROR.gif"
            }
        else:
            self.companion.animations = {
                "ready": "assets/robo/IDLE.gif",
                "running": "assets/robo/RUN.gif",
                "error": "assets/robo/ERROR.gif"
            }

        self.companion.set_state("ready")
        self.apply_theme()





    def apply_theme(self):
        if self.personality == "anime":

            # Textbar
            self.container.setStyleSheet("""
                QWidget {
                    background-color: rgba(255, 230, 245, 240);
                    border-radius: 28px;
                }
            """)

            self.input.setStyleSheet("""
                QLineEdit {
                    background: transparent;
                    border: none;
                    color: #444;
                    font-size: 12pt;
                    padding-left: 6px;
                }
            """)

            # Segmented control
            self.segment_container.setStyleSheet("""
                QWidget {
                    background-color: rgba(255, 200, 230, 220);
                    border-radius: 22px;
                }
            """)

            self.segment_highlight.setStyleSheet("""
                background-color: white;
                border-radius: 18px;
            """)

            self.send_btn.setStyleSheet("""
                QPushButton {
                    background-color: #f5a9c9;
                    border-radius: 18px;
                    color: white;
                    font-size: 14pt;
                }
                QPushButton:hover {
                    background-color: #ff85b5;
                }
            """)


        else:

            # Textbar
            self.container.setStyleSheet("""
                QWidget {
                    background-color: rgba(20, 20, 25, 240);
                    border-radius: 28px;
                }
            """)

            self.input.setStyleSheet("""
                QLineEdit {
                    background: transparent;
                    border: none;
                    color: white;
                    font-size: 12pt;
                    padding-left: 6px;
                }
            """)

            # Segmented control
            self.segment_container.setStyleSheet("""
                QWidget {
                    background-color: rgba(40, 40, 50, 220);
                    border-radius: 22px;
                }
            """)

            self.segment_highlight.setStyleSheet("""
                background-color: rgba(90, 90, 110, 240);
                border-radius: 18px;
            """)

            self.send_btn.setStyleSheet("""
                QPushButton {
                    background-color: rgba(80, 80, 100, 230);
                    border-radius: 18px;
                    color: white;
                    font-size: 14pt;
                }
                QPushButton:hover {
                    background-color: rgba(110, 110, 140, 230);
                }
            """)





if __name__ == "__main__":
    os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "0"

    app = QApplication(sys.argv)
    window = CommandBar()
    window.show()
    sys.exit(app.exec())
