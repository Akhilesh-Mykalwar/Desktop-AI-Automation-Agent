import sys
from PyQt6.QtWidgets import QApplication, QWidget, QLineEdit, QVBoxLayout
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from planner import decide_next_action
from controller import execute


class CommandBar(QWidget):

    def __init__(self):
        super().__init__()

        # Window settings
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )

        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.setFixedWidth(700)
        self.setFixedHeight(70)

        # Layout
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 15, 20, 15)

        self.input = QLineEdit()
        self.input.setPlaceholderText("Ask your desktop...")
        self.input.setFont(QFont("Segoe UI", 15))
        self.input.returnPressed.connect(self.handle_command)

        # Modern glass style
        self.input.setStyleSheet("""
            QLineEdit {
                background-color: rgba(25, 25, 25, 230);
                color: white;
                border: 2px solid rgba(255, 255, 255, 40);
                border-radius: 20px;
                padding: 12px;
            }

            QLineEdit:focus {
                border: 2px solid rgba(0, 170, 255, 180);
            }
        """)

        layout.addWidget(self.input)
        self.setLayout(layout)

        self.center_top()

    def center_top(self):
        screen = QApplication.primaryScreen().geometry()
        x = (screen.width() - self.width()) // 2
        y = 60
        self.move(x, y)

    def handle_command(self):
        goal = self.input.text().strip()
        if not goal:
            return

        action = decide_next_action(goal, [])

        if action.get("action") == "execute_plan":
            for step in action["plan"]:
                execute(step)

        self.input.clear()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CommandBar()
    window.show()
    sys.exit(app.exec())
