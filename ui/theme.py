from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QIcon, QPainter, QPen, QPixmap

SPACE_BLACK = "#0B0C0E"
SURFACE_BLACK = "#13151A"
CARD_USER = "#1C1410"
BORDER_DARK = "#242832"
BORDER_ORANGE = "#6E3208"
BURNT_ORANGE = "#CC5500"
BURNT_ORANGE_HOVER = "#E0630B"
MELLOW_WHITE = "#EAE6DF"
MUTED_STONE = "#9A958E"


def create_app_icon() -> QIcon:
    pixmap = QPixmap(64, 64)
    pixmap.fill(Qt.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)

    painter.setBrush(QColor(SURFACE_BLACK))
    painter.setPen(QPen(QColor(BURNT_ORANGE), 3))
    painter.drawRoundedRect(4, 4, 56, 56, 14, 14)

    pen = QPen(QColor(BURNT_ORANGE), 4, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
    painter.setPen(pen)
    painter.drawLine(20, 22, 30, 32)
    painter.drawLine(30, 32, 20, 42)

    pen.setColor(QColor(MELLOW_WHITE))
    painter.setPen(pen)
    painter.drawLine(34, 42, 46, 42)

    painter.end()
    return QIcon(pixmap)


MAIN_STYLESHEET = f"""
    QWidget {{
        background-color: {SPACE_BLACK};
        color: {MELLOW_WHITE};
        font-family: 'Inter', 'Segoe UI', sans-serif;
    }}
    QTreeView {{
        background-color: transparent;
        border: none;
        padding: 4px;
        font-size: 13px;
        color: {MELLOW_WHITE};
        outline: none;
    }}
    QTreeView::item {{
        padding: 6px 8px;
        border-radius: 6px;
    }}
    QTreeView::item:hover {{
        background-color: #1D2028;
    }}
    QTreeView::item:selected {{
        background-color: {BURNT_ORANGE};
        color: {MELLOW_WHITE};
    }}
    QScrollBar:vertical {{
        background: transparent;
        width: 8px;
        margin: 4px 2px;
    }}
    QScrollBar::handle:vertical {{
        background: #2C303C;
        border-radius: 4px;
        min-height: 30px;
    }}
    QScrollBar::handle:vertical:hover {{
        background: {BURNT_ORANGE};
    }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical,
    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
        height: 0px;
        width: 0px;
    }}
    QLineEdit, QTextEdit {{
        background-color: {SURFACE_BLACK};
        border: 1px solid {BORDER_DARK};
        border-radius: 10px;
        padding: 10px 14px;
        font-size: 14px;
        color: {MELLOW_WHITE};
    }}
    QLineEdit:focus, QTextEdit:focus {{
        border: 1px solid {BURNT_ORANGE};
    }}
    QTextEdit:disabled {{
        color: #55524E;
        background-color: #0E1014;
    }}
    QPushButton {{
        background-color: {BURNT_ORANGE};
        color: {MELLOW_WHITE};
        border: none;
        border-radius: 10px;
        padding: 0 20px;
        min-height: 46px;
        font-size: 13px;
        font-weight: 600;
    }}
    QPushButton:hover {{
        background-color: {BURNT_ORANGE_HOVER};
    }}
    QPushButton:disabled {{
        background-color: #1C1F26;
        color: #5C5954;
    }}
    QPushButton#SecondaryBtn {{
        background-color: {SURFACE_BLACK};
        border: 1px solid {BORDER_DARK};
        border-radius: 8px;
        color: {MELLOW_WHITE};
        min-height: 36px;
        padding: 0 12px;
        font-size: 12px;
    }}
    QPushButton#SecondaryBtn:hover {{
        border: 1px solid {BURNT_ORANGE};
    }}
"""

DIALOG_STYLESHEET = f"""
    QDialog {{
        background-color: {SPACE_BLACK};
        color: {MELLOW_WHITE};
        font-family: 'Inter', 'Segoe UI', sans-serif;
    }}
    QTabWidget::pane {{
        border: 1px solid {BORDER_DARK};
        border-radius: 8px;
        background-color: {SURFACE_BLACK};
        padding: 12px;
    }}
    QTabBar::tab {{
        background-color: {SPACE_BLACK};
        color: {MUTED_STONE};
        border: 1px solid {BORDER_DARK};
        border-bottom: none;
        border-top-left-radius: 6px;
        border-top-right-radius: 6px;
        padding: 8px 16px;
        margin-right: 4px;
        font-size: 12px;
        font-weight: 600;
    }}
    QTabBar::tab:selected {{
        background-color: {SURFACE_BLACK};
        color: {MELLOW_WHITE};
        border-color: {BURNT_ORANGE};
    }}
    QLabel {{
        color: {MELLOW_WHITE};
        font-size: 12px;
        background: transparent;
    }}
    QLineEdit, QTextEdit, QSpinBox, QComboBox {{
        background-color: {SPACE_BLACK};
        border: 1px solid {BORDER_DARK};
        border-radius: 6px;
        padding: 7px 10px;
        color: {MELLOW_WHITE};
        font-size: 13px;
    }}
    QLineEdit:focus, QTextEdit:focus, QSpinBox:focus, QComboBox:focus {{
        border: 1px solid {BURNT_ORANGE};
    }}
    QCheckBox {{
        color: {MELLOW_WHITE};
        font-size: 12px;
        background: transparent;
        spacing: 8px;
    }}
    QPushButton {{
        background-color: {BURNT_ORANGE};
        color: {MELLOW_WHITE};
        border: none;
        border-radius: 8px;
        padding: 8px 18px;
        font-size: 13px;
        font-weight: 600;
    }}
    QPushButton:hover {{
        background-color: {BURNT_ORANGE_HOVER};
    }}
    QPushButton#CancelBtn {{
        background-color: {SURFACE_BLACK};
        border: 1px solid {BORDER_DARK};
    }}
    QPushButton#CancelBtn:hover {{
        border: 1px solid {BURNT_ORANGE};
    }}

    QToolTip {{
        background-color: {SPACE_BLACK};
        color: {MELLOW_WHITE};
        border: 1px solid {BURNT_ORANGE};
        border-radius: 6px;
        padding: 6px 10px;
        font-size: 12px;
    }}
"""