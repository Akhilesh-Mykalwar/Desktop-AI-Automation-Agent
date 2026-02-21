from PyQt6.QtGui import QIcon
from PyQt6.QtCore import QPoint


def apply(ui):
    """Apply knight theme to the CommandBar ui instance."""

    # Premium dark steel bar with subtle blue-grey glow border
    ui.container.setStyleSheet("""
        background: qlineargradient(
            x1:0, y1:0, x2:0, y2:1,
            stop:0 rgba(30, 32, 40, 250),
            stop:1 rgba(18, 20, 26, 250)
        );
        border-radius: 29px;
        border: 1px solid rgba(100, 120, 160, 120);
    """)

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
        container_pos.x() - 10,   # closer to bar, less floaty
        container_pos.y() - 18    # tighter vertical overlap
    )
    ui.sword_anim.start()

    # --- Shield: badge-style overlapping top-right corner of the bar ---
    ui.shield.show()
    ui.shield.raise_()
    ui.shield.move(
        container_pos.x() + ui.container.width() - 28,  # overlaps corner, stays in window
        container_pos.y() - 16                           # sits just above the bar edge
    )