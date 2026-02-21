from PyQt6.QtGui import QIcon, QColor, QPixmap, QPainter, QRadialGradient, QBrush
from PyQt6.QtCore import QPoint, QPointF, Qt
import random


def _make_starry_overlay(width: int, height: int) -> QPixmap:
    px = QPixmap(width, height)
    px.fill(Qt.GlobalColor.transparent)
    painter = QPainter(px)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    star_count = 20
    rng = random.Random(42)  # fixed seed → stable star positions

    # Pinpoint stars
    for _ in range(star_count):
        x = rng.uniform(8, width - 8)
        y = rng.uniform(5, height - 5)
        alpha = rng.randint(90, 230)
        size = rng.uniform(0.7, 2.0)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(QColor(210, 220, 255, alpha)))
        painter.drawEllipse(QPointF(x, y), size, size)

    # Soft nebula glows
    for cx, cy, r in [
        (width * 0.22, height * 0.5,  32),
        (width * 0.68, height * 0.4,  26),
        (width * 0.50, height * 0.75, 18),
    ]:
        grad = QRadialGradient(QPointF(cx, cy), r)
        grad.setColorAt(0.0, QColor(120, 150, 255, 35))
        grad.setColorAt(1.0, QColor(120, 150, 255, 0))
        painter.setBrush(QBrush(grad))
        painter.drawEllipse(QPointF(cx, cy), r, r)

    # Two bright feature stars
    for cx, cy in [(width * 0.15, height * 0.28), (width * 0.85, height * 0.68)]:
        for radius, alpha in [(3.5, 15), (1.8, 55), (0.9, 210)]:
            painter.setBrush(QBrush(QColor(235, 242, 255, alpha)))
            painter.drawEllipse(QPointF(cx, cy), radius, radius)

    painter.end()
    return px


def _install_star_overlay(ui):
    container = ui.container
    w = container.width() or 410
    h = container.height() or 58
    star_px = _make_starry_overlay(w, h)
    container._star_px = star_px

    if not getattr(container, "_star_patch_applied", False):
        original_paint = container.__class__.paintEvent

        def _paint_with_stars(self_c, event):
            original_paint(self_c, event)
            p = QPainter(self_c)
            p.setRenderHint(QPainter.RenderHint.Antialiasing)
            p.drawPixmap(0, 0, self_c._star_px)
            p.end()

        container.__class__ = type(
            "StarryWidget",
            (container.__class__,),
            {"paintEvent": _paint_with_stars}
        )
        container._star_patch_applied = True
    else:
        container._star_px = star_px


def apply(ui):
    """Apply knight theme to the CommandBar ui instance."""

    # Deep space gradient background
    ui.container.setStyleSheet("""
        background: qlineargradient(
            x1:0, y1:0, x2:1, y2:1,
            stop:0   rgba(8,  10,  28, 252),
            stop:0.3 rgba(14, 18,  45, 252),
            stop:0.7 rgba(10, 14,  38, 252),
            stop:1   rgba(6,  8,   22, 252)
        );
        border-radius: 29px;
        border: 1.5px solid rgba(110, 140, 220, 140);
    """)

    # Paint stars on top of the gradient
    _install_star_overlay(ui)
    ui.container.update()

    ui.input.setStyleSheet("background: transparent; border: none; color: #dde4f0;")
    ui.input.setPlaceholderText("Command, my lord...")

    ui.send_btn.setIcon(QIcon("assets/icons/send.png"))
    ui.send_btn.setStyleSheet("""
        QPushButton {
            background: qlineargradient(
                x1:0, y1:0, x2:0, y2:1,
                stop:0 rgba(80, 95, 130, 220),
                stop:1 rgba(55, 65, 95, 220)
            );
            border-radius: 19px;
            border: 1px solid rgba(120, 140, 180, 80);
        }
        QPushButton:hover {
            background: qlineargradient(
                x1:0, y1:0, x2:0, y2:1,
                stop:0 rgba(100, 120, 165, 240),
                stop:1 rgba(70, 85, 125, 240)
            );
        }
    """)

    ui.segment_container.setStyleSheet("""
        background: qlineargradient(
            x1:0, y1:0, x2:0, y2:1,
            stop:0 rgba(40, 45, 60, 220),
            stop:1 rgba(28, 32, 44, 220)
        );
        border-radius: 18px;
        border: 1px solid rgba(80, 100, 140, 80);
    """)
    ui.segment_highlight.setStyleSheet("""
        background: qlineargradient(
            x1:0, y1:0, x2:0, y2:1,
            stop:0 rgba(90, 110, 155, 240),
            stop:1 rgba(65, 80, 120, 240)
        );
        border-radius: 14px;
    """)

    # Hide anime decorations
    ui.bow.hide()
    ui.cloud_layer.hide()
    if hasattr(ui, "cloud_anim"):
        ui.cloud_anim.stop()

    # --- Sword: top-left, hugging the bar at a shallower angle ---
    ui.sword_layer.show()
    ui.sword_layer.raise_()
    container_pos = ui.container.mapTo(ui, ui.container.rect().topLeft())
    ui.sword_layer.move(
        container_pos.x() - 10,
        container_pos.y() - 18
    )
    ui.sword_anim.start()

    # --- Shield: badge-style overlapping top-right corner of the bar ---
    ui.shield.show()
    ui.shield.raise_()
    ui.shield.move(
        container_pos.x() + ui.container.width() - 28,
        container_pos.y() - 16
    )