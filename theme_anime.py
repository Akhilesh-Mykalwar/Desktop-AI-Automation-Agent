from PyQt6.QtWidgets import QGraphicsDropShadowEffect
from PyQt6.QtCore import QPoint, QPointF, QPropertyAnimation, QEasingCurve, Qt
from PyQt6.QtGui import QIcon, QColor, QPixmap, QPainter, QRadialGradient, QBrush
import random


def _make_sparkle_overlay(width: int, height: int) -> QPixmap:
    px = QPixmap(width, height)
    px.fill(Qt.GlobalColor.transparent)
    painter = QPainter(px)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    rng = random.Random(7)  # fixed seed → stable sparkle positions

    # Soft pastel glows scattered across the bar
    for _ in range(10):
        cx = rng.uniform(12, width - 12)
        cy = rng.uniform(6, height - 6)
        r = rng.uniform(8, 20)
        hue = rng.choice([
            QColor(255, 180, 230, 30),  # pink
            QColor(200, 180, 255, 28),  # lavender
            QColor(180, 230, 255, 25),  # light blue
        ])
        grad = QRadialGradient(QPointF(cx, cy), r)
        grad.setColorAt(0.0, hue)
        grad.setColorAt(1.0, QColor(255, 255, 255, 0))
        painter.setBrush(QBrush(grad))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(QPointF(cx, cy), r, r)

    # Tiny star-sparkle dots (bright white/pink pinpoints)
    for _ in range(18):
        x = rng.uniform(8, width - 8)
        y = rng.uniform(4, height - 4)
        alpha = rng.randint(60, 160)
        size = rng.uniform(0.6, 1.6)
        painter.setBrush(QBrush(QColor(255, 220, 240, alpha)))
        painter.drawEllipse(QPointF(x, y), size, size)

    # A few 4-pointed star crosses (✦ feel) — tiny crosshair lines
    painter.setPen(QColor(255, 200, 230, 80))
    for _ in range(5):
        x = int(rng.uniform(15, width - 15))
        y = int(rng.uniform(6, height - 6))
        sz = int(rng.uniform(3, 6))
        painter.drawLine(x - sz, y, x + sz, y)
        painter.drawLine(x, y - sz, x, y + sz)

    painter.end()
    return px


def _install_sparkle_overlay(ui):
    container = ui.container
    w = container.width() or 410
    h = container.height() or 58
    sparkle_px = _make_sparkle_overlay(w, h)
    container._sparkle_px = sparkle_px

    if not getattr(container, "_sparkle_patch_applied", False):
        original_paint = container.__class__.paintEvent

        def _paint_with_sparkles(self_c, event):
            original_paint(self_c, event)
            p = QPainter(self_c)
            p.setRenderHint(QPainter.RenderHint.Antialiasing)
            p.drawPixmap(0, 0, self_c._sparkle_px)
            p.end()

        container.__class__ = type(
            "SparkleWidget",
            (container.__class__,),
            {"paintEvent": _paint_with_sparkles}
        )
        container._sparkle_patch_applied = True
    else:
        container._sparkle_px = sparkle_px


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

    # Paint sparkles on top of the pink gradient
    _install_sparkle_overlay(ui)
    ui.container.update()

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
        container_pos.x() + ui.container.width() - 38,
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