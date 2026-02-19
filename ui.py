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
        self.setFixedHeight(85)

        # ---------------- Shadow ----------------
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(35)
        shadow.setXOffset(0)
        shadow.setYOffset(8)
        shadow.setColor(QColor(0, 0, 0, 180))
        self.setGraphicsEffect(shadow)

        # ---------------- Layout ----------------
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 15, 20, 15)

        container = QWidget()
        container.setStyleSheet("""
            QWidget {
                background-color: rgba(20, 20, 20, 235);
                border-radius: 20px;
            }
        """)

        container_layout = QHBoxLayout()
        container_layout.setContentsMargins(15, 10, 15, 10)

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
                background-color: transparent;
                color: white;
                border: none;
                padding-left: 10px;
            }
        """)

        container_layout.addWidget(self.status_dot)
        container_layout.addWidget(self.input)
        container.setLayout(container_layout)

        main_layout.addWidget(container)
        self.setLayout(main_layout)

        self.move_top_right()
        self.companion = Companion()
        self.companion.show()


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




if __name__ == "__main__":
    os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "0"

    app = QApplication(sys.argv)
    window = CommandBar()
    window.show()
    sys.exit(app.exec())
