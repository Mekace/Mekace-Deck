import re
import markdown
from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QAction, QKeyEvent
from PySide6.QtWidgets import (
    QApplication, QFrame, QHBoxLayout, QLabel, QMenu,
    QPushButton, QSizePolicy, QTextEdit, QVBoxLayout, QWidget,
)
from core.translations import t
from ui.theme import (
    BORDER_DARK, BORDER_ORANGE, BURNT_ORANGE,
    CARD_USER, MELLOW_WHITE, MUTED_STONE, SPACE_BLACK, SURFACE_BLACK,
)


class DropdownButton(QPushButton):
    selection_changed = Signal(str)

    def __init__(self, items: list[str], prefix: str = ""):
        super().__init__()
        self.items = list(items)
        self.prefix = prefix
        self.current_value = self.items[0] if self.items else ""
        self.setObjectName("SecondaryBtn")
        self.setCursor(Qt.PointingHandCursor)
        self.update_label()
        self.clicked.connect(self.show_menu)

    def set_items(self, items: list[str], keep_current: bool = False):
        self.items = list(items)
        if not keep_current or self.current_value not in self.items:
            self.current_value = self.items[0] if self.items else ""
        self.update_label()

    def update_label(self):
        text = f"{self.prefix}{self.current_value}  ▾" if self.prefix else f"{self.current_value}  ▾"
        self.setText(text)

    def show_menu(self):
        menu = QMenu(self)
        menu.setStyleSheet(f"""
            QMenu {{
                background-color: {SURFACE_BLACK};
                border: 1px solid {BURNT_ORANGE};
                border-radius: 8px;
                padding: 4px;
                color: {MELLOW_WHITE};
                font-size: 12px;
            }}
            QMenu::item {{
                padding: 8px 16px;
                border-radius: 5px;
            }}
            QMenu::item:selected {{
                background-color: {BURNT_ORANGE};
                color: {MELLOW_WHITE};
            }}
        """)
        for item in self.items:
            action = QAction(item, menu)
            action.triggered.connect(lambda checked=False, val=item: self.select_item(val))
            menu.addAction(action)
        menu.exec(self.mapToGlobal(self.rect().bottomLeft()))

    def select_item(self, value: str):
        if value != self.current_value:
            self.current_value = value
            self.update_label()
            self.selection_changed.emit(value)

    def currentText(self) -> str:
        return self.current_value


class ChatInputBox(QTextEdit):
    submit_pressed = Signal()

    def __init__(self, placeholder: str = ""):
        super().__init__()
        self.setPlaceholderText(placeholder)
        self.setFixedHeight(48)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.textChanged.connect(self.adjust_height)

    def adjust_height(self):
        doc_height = int(self.document().size().height())
        new_height = max(48, min(doc_height + 16, 140))
        self.setFixedHeight(new_height)

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() in (Qt.Key_Return, Qt.Key_Enter) and not (event.modifiers() & Qt.ShiftModifier):
            self.submit_pressed.emit()
        else:
            super().keyPressEvent(event)


class CodeBlockWidget(QFrame):
    def __init__(self, language: str, code: str, lang_code: str = "en"):
        super().__init__()
        self.code_text = code
        self.lang_code = lang_code
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {SPACE_BLACK};
                border: 1px solid {BORDER_DARK};
                border-radius: 8px;
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        header = QWidget()
        header.setStyleSheet(f"""
            background-color: #181B22;
            border-top-left-radius: 8px;
            border-top-right-radius: 8px;
            border-bottom: 1px solid {BORDER_DARK};
        """)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(12, 6, 10, 6)

        lang_label = QLabel(language.upper() if language else t(lang_code, "code_default"))
        lang_label.setStyleSheet(f"color: {MUTED_STONE}; font-size: 11px; font-weight: 700; border: none;")

        self.copy_btn = QPushButton(t(lang_code, "copy"))
        self.copy_btn.setCursor(Qt.PointingHandCursor)
        self.copy_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {MELLOW_WHITE};
                border: 1px solid {BORDER_DARK};
                border-radius: 4px;
                padding: 2px 10px;
                min-height: 22px;
                font-size: 11px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                border-color: {BURNT_ORANGE};
                color: {BURNT_ORANGE};
            }}
        """)
        self.copy_btn.clicked.connect(self.copy_code)

        header_layout.addWidget(lang_label)
        header_layout.addStretch()
        header_layout.addWidget(self.copy_btn)
        layout.addWidget(header)

        code_label = QLabel(code)
        code_label.setTextFormat(Qt.PlainText)
        code_label.setWordWrap(True)
        code_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        code_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        code_label.setStyleSheet(f"""
            color: {MELLOW_WHITE};
            font-family: 'JetBrains Mono', 'Fira Code', Consolas, monospace;
            font-size: 13px;
            padding: 12px 14px;
            border: none;
            background: transparent;
        """)
        layout.addWidget(code_label)

    def copy_code(self):
        QApplication.clipboard().setText(self.code_text)
        self.copy_btn.setText(t(self.lang_code, "copied"))
        QTimer.singleShot(1500, lambda: self.copy_btn.setText(t(self.lang_code, "copy")))


class MessageBubble(QWidget):
    def __init__(self, sender: str, text: str, role: str = "assistant", attachment: str = None, lang_code: str = "en"):
        super().__init__()
        self.lang_code = lang_code
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        outer_layout = QHBoxLayout(self)
        outer_layout.setContentsMargins(0, 4, 0, 4)

        if role == "system":
            pill = QLabel(text)
            pill.setAlignment(Qt.AlignCenter)
            pill.setWordWrap(True)
            pill.setMaximumWidth(680)
            pill.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
            pill.setTextInteractionFlags(Qt.TextSelectableByMouse)
            pill.setStyleSheet(f"""
                background-color: {SURFACE_BLACK};
                color: {MUTED_STONE};
                border: 1px solid {BORDER_DARK};
                border-radius: 10px;
                padding: 6px 14px;
                font-size: 11px;
            """)
            outer_layout.setAlignment(Qt.AlignHCenter)
            outer_layout.addWidget(pill)
            return

        is_user = (role == "user")
        card = QFrame()
        card.setMaximumWidth(780)

        if is_user:
            card.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Minimum)
            card.setStyleSheet(f"""
                QFrame {{
                    background-color: {CARD_USER};
                    border: 1px solid {BORDER_ORANGE};
                    border-radius: 14px;
                    border-bottom-right-radius: 4px;
                }}
            """)
        else:
            card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
            card.setStyleSheet(f"""
                QFrame {{
                    background-color: {SURFACE_BLACK};
                    border: 1px solid {BORDER_DARK};
                    border-radius: 14px;
                    border-bottom-left-radius: 4px;
                }}
            """)

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(14, 10, 14, 14)
        card_layout.setSpacing(8)

        header_row = QHBoxLayout()
        sender_lbl = QLabel(sender)
        sender_lbl.setStyleSheet(f"""
            color: {BURNT_ORANGE if is_user else MUTED_STONE};
            font-size: 11px;
            font-weight: 700;
            letter-spacing: 0.6px;
            border: none;
            background: transparent;
        """)
        header_row.addWidget(sender_lbl)

        if attachment:
            file_tag = QLabel(attachment)
            file_tag.setStyleSheet(f"""
                background-color: {SPACE_BLACK};
                color: {BURNT_ORANGE};
                border: 1px solid {BORDER_DARK};
                border-radius: 4px;
                padding: 1px 6px;
                font-size: 11px;
            """)
            header_row.addWidget(file_tag)

        header_row.addStretch()
        card_layout.addLayout(header_row)

        if is_user:
            body_lbl = QLabel(text)
            body_lbl.setWordWrap(True)
            body_lbl.setTextInteractionFlags(Qt.TextSelectableByMouse)
            body_lbl.setStyleSheet(f"""
                color: {MELLOW_WHITE};
                font-size: 14px;
                line-height: 1.5;
                border: none;
                background: transparent;
            """)
            card_layout.addWidget(body_lbl)
        else:
            self._render_assistant_content(card_layout, text)

        if is_user:
            outer_layout.addStretch()
            outer_layout.addWidget(card)
        else:
            outer_layout.addWidget(card)
            outer_layout.addStretch()

    def _render_assistant_content(self, layout: QVBoxLayout, text: str):
        pattern = re.compile(r"```([a-zA-Z0-9_+-]*)\n?(.*?)```", re.DOTALL)
        last_idx = 0

        for match in pattern.finditer(text):
            plain_part = text[last_idx:match.start()].strip()
            if plain_part:
                layout.addWidget(self._make_rich_label(plain_part))

            lang = match.group(1).strip()
            code_body = match.group(2).strip("\n")
            layout.addWidget(CodeBlockWidget(lang, code_body, self.lang_code))
            last_idx = match.end()

        remaining = text[last_idx:].strip()
        if remaining:
            layout.addWidget(self._make_rich_label(remaining))

    def _make_rich_label(self, md_text: str) -> QLabel:
        html = markdown.markdown(md_text)
        html = html.replace(
            "<code>",
            f'<code style="background-color:{SPACE_BLACK}; padding:2px 5px; border-radius:4px; '
            f'font-family:Consolas,monospace; color:{BURNT_ORANGE};">',
        )
        lbl = QLabel(html)
        lbl.setWordWrap(True)
        lbl.setOpenExternalLinks(True)
        lbl.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        lbl.setTextInteractionFlags(Qt.TextSelectableByMouse | Qt.LinksAccessibleByMouse)
        lbl.setStyleSheet(f"""
            color: {MELLOW_WHITE};
            font-size: 14px;
            line-height: 1.55;
            border: none;
            background: transparent;
        """)
        return lbl