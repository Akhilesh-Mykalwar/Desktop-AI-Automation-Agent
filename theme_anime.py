from PyQt6.QtWidgets import QGraphicsDropShadowEffect
from PyQt6.QtCore import QPoint, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QIcon, QColor, QPixmap, QPainter
from PyQt6.QtCore import Qt


def apply(ui):
    """Apply anime theme to the CommandBar ui instance."""

    # Hide knight decorations
    if hasattr(ui, "sword_layer"):
        ui.sword_layer.hide()
        ui.sword_anim.stop()
    if hasattr(ui, "shield"):
        ui.shield.hide()

    ui.container.setStyleSheet("""
        background: qlineargradient(
            x1:0, y1:0, x2:0, y2:1,
            stop:0 #fff3fb,
            stop:0.4 #ffe6f5,
            stop:1 #ffcce8
        );
        border-radius: 29px;
        border: 1px solid #ffb3df;
    """)

    ui.status_dot.setStyleSheet("background-color: #6fdc9e; border-radius: 7px;")
    ui.input.setStyleSheet("background: transparent; border: none; color: #444;")
    ui.input.setPlaceholderText("Ask your desktop...")

    ui.send_btn.setIcon(QIcon("assets/icons/send_dark.png"))
    ui.send_btn.setStyleSheet("""
        QPushButton {
            background: qradialgradient(cx:0.5, cy:0.4, radius:0.9, stop:0 #ffffff, stop:1 #f5d7e8);
            border: 1px solid #ffb3df;
            border-radius: 19px;
        }
        QPushButton:hover {
            background: qradialgradient(cx:0.5, cy:0.4, radius:0.9, stop:0 #ffffff, stop:1 #ffd9f2);
        }
    """)

    ui.segment_container.setStyleSheet("background-color: rgba(255, 200, 230, 220); border-radius: 18px;")
    ui.segment_highlight.setStyleSheet("background-color: white; border-radius: 14px;")

    # --- Bow: top-right ---
    ui.bow.show()
    ui.bow.raise_()
    container_pos = ui.container.mapTo(ui, ui.container.rect().topLeft())
    ui.bow.move(
        container_pos.x() + ui.container.width() - 14,
        container_pos.y() - 20
    )

    # --- Cloud: top-left ---
    ui.cloud_layer.show()
    ui.cloud_layer.raise_()
    ui.cloud_layer.move(
        container_pos.x() - 30,
        container_pos.y() - 30
    )

    start_pos = ui.cloud_layer.pos()
    ui.cloud_anim.setStartValue(start_pos)
    ui.cloud_anim.setEndValue(start_pos + QPoint(0, 5))
    ui.cloud_anim.start()