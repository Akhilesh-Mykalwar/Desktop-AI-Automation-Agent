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

# pynput runs in its own thread and works even when the Qt window is hidden

from pynput import keyboard as pynput_keyboard

import theme_anime
import theme_knight

try:
    from companion import Companion
    from planner import decide_next_action
    from controller import execute
except ImportError:
    class Companion(QWidget):
        def __init__(self): super().__init__(); self.animations = {}
        def speak(self, t): pass
        def set_state(self, s): pass
        def set_personality(self, p): pass
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
        except:
            self.error.emit()


class HotkeyListener(QObject):
    """
    Runs pynput in a background thread.
    Emits toggle_signal on the Qt main thread via signal,
    so it's safe to call show/hide from the slot.
    """
    toggle_signal = pyqtSignal()

    def __init__(self):
        super().__init__()
        self._listener = None

    def start(self):
        def on_press(key):
            if key == pynput_keyboard.Key.f2:
                self.toggle_signal.emit()

        self._listener = pynput_keyboard.Listener(on_press=on_press)
        self._listener.daemon = True   # dies with the main process
        self._listener.start()

    def stop(self):
        if self._listener:
            self._listener.stop()


class CommandBar(QWidget):
    def __init__(self):
        super().__init__()
        self.personality = "robo"
        self._ui_visible = True

        # ---------------- Window Setup ----------------
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(520, 160)

        # ---------------- Main Layout ----------------
        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(0, 40, 0, 20)
        self.main_layout.setSpacing(0)

        self.left_deco_spacer = QWidget()
        self.left_deco_spacer.setFixedWidth(55)
        self.left_deco_spacer.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

        self.right_deco_spacer = QWidget()
        self.right_deco_spacer.setFixedWidth(55)
        self.right_deco_spacer.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

        # ---------------- Center panel ----------------
        center_panel = QWidget()
        center_layout = QVBoxLayout(center_panel)
        center_layout.setContentsMargins(0, 0, 0, 0)
        center_layout.setSpacing(10)

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
        self.segment_container.setFixedSize(120, 36)
        self.segment_container.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        self.segment_highlight = QWidget(self.segment_container)
        self.segment_highlight.setFixedSize(56, 28)
        self.segment_highlight.move(60, 4)

        seg_layout = QHBoxLayout(self.segment_container)
        seg_layout.setContentsMargins(4, 4, 4, 4)
        seg_layout.setSpacing(0)

        self.anime_btn = QPushButton("👧")
        self.robo_btn = QPushButton("🤖")
        for btn in (self.anime_btn, self.robo_btn):
            btn.setFixedSize(56, 28)
            btn.setFlat(True)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet("background: transparent; border: none; font-size: 13pt;")

        seg_layout.addWidget(self.anime_btn)
        seg_layout.addWidget(self.robo_btn)

        self.anime_btn.clicked.connect(lambda: self.switch_personality("anime"))
        self.robo_btn.clicked.connect(lambda: self.switch_personality("knight"))

        seg_row = QHBoxLayout()
        seg_row.setContentsMargins(6, 0, 0, 0)
        seg_row.addWidget(self.segment_container)
        seg_row.addStretch()

        center_layout.addWidget(self.container)
        center_layout.addLayout(seg_row)

        self.main_layout.addWidget(self.left_deco_spacer)
        self.main_layout.addWidget(center_panel)
        self.main_layout.addWidget(self.right_deco_spacer)
        self.setLayout(self.main_layout)

        # ---------------- Cloud Decoration (anime) ----------------
        self.cloud_layer = QLabel(self)
        cloud_pixmap = QPixmap("assets/icons/cloud5.png").scaled(
            120, 65,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        rotated_cloud = QPixmap(cloud_pixmap.size())
        rotated_cloud.fill(Qt.GlobalColor.transparent)
        cloud_painter = QPainter(rotated_cloud)
        cloud_painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        cloud_painter.translate(cloud_pixmap.width() / 2, cloud_pixmap.height() / 2)
        cloud_painter.rotate(-10)
        cloud_painter.translate(-cloud_pixmap.width() / 2, -cloud_pixmap.height() / 2)
        cloud_painter.drawPixmap(0, 0, cloud_pixmap)
        cloud_painter.end()
        self.cloud_layer.setPixmap(rotated_cloud)
        self.cloud_layer.setFixedSize(rotated_cloud.size())
        self.cloud_layer.hide()

        cloud_shadow = QGraphicsDropShadowEffect()
        cloud_shadow.setBlurRadius(12)
        cloud_shadow.setOffset(0, 3)
        cloud_shadow.setColor(QColor(0, 0, 0, 60))
        self.cloud_layer.setGraphicsEffect(cloud_shadow)

        self.cloud_anim = QPropertyAnimation(self.cloud_layer, b"pos")
        self.cloud_anim.setDuration(6000)
        self.cloud_anim.setEasingCurve(QEasingCurve.Type.InOutSine)
        self.cloud_anim.setLoopCount(-1)

        # ---------------- Bow Decoration (anime) ----------------
        self.bow = QLabel(self)
        bow_pixmap = QPixmap("assets/icons/bow.png").scaled(
            38, 38,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        rotated_bow = QPixmap(bow_pixmap.size())
        rotated_bow.fill(Qt.GlobalColor.transparent)
        bow_painter = QPainter(rotated_bow)
        bow_painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        bow_painter.translate(bow_pixmap.width() / 2, bow_pixmap.height() / 2)
        bow_painter.rotate(6)
        bow_painter.translate(-bow_pixmap.width() / 2, -bow_pixmap.height() / 2)
        bow_painter.drawPixmap(0, 0, bow_pixmap)
        bow_painter.end()
        self.bow.setPixmap(rotated_bow)
        self.bow.setFixedSize(rotated_bow.size())
        self.bow.hide()

        # ---------------- Sword Decoration (knight) ----------------
        self.sword_layer = QLabel(self)
        sword_pixmap = QPixmap("assets/icons/sword.png").scaled(
            120, 65,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        rotated_sword = QPixmap(sword_pixmap.size())
        rotated_sword.fill(Qt.GlobalColor.transparent)
        sword_painter = QPainter(rotated_sword)
        sword_painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        sword_painter.translate(sword_pixmap.width() / 2, sword_pixmap.height() / 2)
        sword_painter.rotate(-10)
        sword_painter.translate(-sword_pixmap.width() / 2, -sword_pixmap.height() / 2)
        sword_painter.drawPixmap(0, 0, sword_pixmap)
        sword_painter.end()
        self.sword_layer.setPixmap(rotated_sword)
        self.sword_layer.setFixedSize(rotated_sword.size())
        self.sword_layer.hide()

        self.sword_opacity = QGraphicsOpacityEffect()
        self.sword_layer.setGraphicsEffect(self.sword_opacity)
        self.sword_opacity.setOpacity(1.0)

        self.sword_anim = QPropertyAnimation(self.sword_opacity, b"opacity")
        self.sword_anim.setDuration(1800)
        self.sword_anim.setStartValue(0.4)
        self.sword_anim.setEndValue(1.0)
        self.sword_anim.setEasingCurve(QEasingCurve.Type.InOutSine)
        self.sword_anim.setLoopCount(-1)

        # ---------------- Shield Decoration (knight) ----------------
        self.shield = QLabel(self)
        shield_pixmap = QPixmap("assets/icons/shield.png").scaled(
            42, 42,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        rotated_shield = QPixmap(shield_pixmap.size())
        rotated_shield.fill(Qt.GlobalColor.transparent)
        shield_painter = QPainter(rotated_shield)
        shield_painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        shield_painter.translate(shield_pixmap.width() / 2, shield_pixmap.height() / 2)
        shield_painter.rotate(-8)
        shield_painter.translate(-shield_pixmap.width() / 2, -shield_pixmap.height() / 2)
        shield_painter.drawPixmap(0, 0, shield_pixmap)
        shield_painter.end()
        self.shield.setPixmap(rotated_shield)
        self.shield.setFixedSize(rotated_shield.size())
        self.shield.hide()

        # ---------------- Init ----------------
        self.companion = Companion()
        self.companion.set_personality("knight")
        self.companion.show()

        self.apply_theme()
        self.move_top_right()
        self.set_status("ready")

        # ---------------- Global F2 Hotkey (pynput) ----------------
        self._hotkey = HotkeyListener()
        self._hotkey.toggle_signal.connect(self.toggle_ui)
        self._hotkey.start()

    # ------------------------------------------------------------------ #
    # Toggle — called from pynput thread via Qt signal (thread-safe)      #
    # ------------------------------------------------------------------ #
    def toggle_ui(self):
        self._ui_visible = not self._ui_visible
        if self._ui_visible:
            self.show()
            self.companion.show()
        else:
            self.companion.bubble.hide()
            self.companion.hide()
            self.hide()

    def apply_theme(self):
        if self.personality == "anime":
            theme_anime.apply(self)
        else:
            theme_knight.apply(self)

    def switch_personality(self, p):
        if self.personality == p:
            return
        self.personality = p
        target_x = 4 if p == "anime" else 60
        self.anim = QPropertyAnimation(self.segment_highlight, b"pos")
        self.anim.setDuration(250)
        self.anim.setEndValue(QPoint(target_x, 4))
        self.anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.anim.start()
        self.apply_theme()
        if hasattr(self, "companion"):
            self.companion.set_personality(p)

    def handle_command(self):
        goal = self.input.text().strip()
        if not goal:
            return
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
        self.status_dot.setStyleSheet(
            f"background-color: {colors[state]}; border-radius: 7px;"
        )

    def move_top_right(self):
        screen = QApplication.primaryScreen().geometry()
        self.move(screen.width() - self.width() - 20, 40)

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

    def closeEvent(self, event):
        self._hotkey.stop()
        super().closeEvent(event)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CommandBar()
    window.show()
    sys.exit(app.exec())