import os
from google import genai
from google.genai import types
from PySide6.QtCore import QDir, QEasingCurve, QPropertyAnimation, Qt, QTimer
from PySide6.QtWidgets import (
    QDialog, QFileDialog, QFileSystemModel, QFrame, QHBoxLayout,
    QLabel, QProgressBar, QPushButton, QScrollArea, QTreeView,
    QVBoxLayout, QWidget,
)
from core.config import DEFAULT_SYSTEM_PROMPT, load_config, save_config
from core.providers import PROVIDERS, THINKING_BUDGETS
from core.translations import t
from core.worker import AIWorker
from ui.settings_dialog import SettingsDialog
from ui.theme import (
    BORDER_DARK, BURNT_ORANGE, MAIN_STYLESHEET,
    SURFACE_BLACK, create_app_icon,
)
from ui.widgets import ChatInputBox, DropdownButton, MessageBubble


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.config = load_config()
        self.lang = self.config.get("language", "en")

        self.setWindowTitle(t(self.lang, "app_title"))
        self.setWindowIcon(create_app_icon())
        self.resize(1180, 760)

        self.selected_file_path = None
        self.sidebar_open = True
        self.auto_scroll = True
        self.client = None
        self.chat = None
        self.conversation_history = []
        self.thinking_key = "off"

        self.setup_ui()
        self.setup_loader()

        if self.config.get("gemini_key"):
            self.init_gemini_session()

    def get_active_models(self, provider: str) -> list[str]:
        enabled_map = self.config.get("enabled_models", {})
        models = enabled_map.get(provider)
        return models if models else list(PROVIDERS[provider]["models"])

    def get_thinking_labels(self) -> list[str]:
        return [
            t(self.lang, "thinking_off"),
            t(self.lang, "thinking_low"),
            t(self.lang, "thinking_medium"),
            t(self.lang, "thinking_high"),
            t(self.lang, "thinking_max"),
        ]

    def get_thinking_budget(self) -> int:
        label = self.thinking_btn.currentText()
        mapping = {
            t(self.lang, "thinking_low"): THINKING_BUDGETS["low"],
            t(self.lang, "thinking_medium"): THINKING_BUDGETS["medium"],
            t(self.lang, "thinking_high"): THINKING_BUDGETS["high"],
            t(self.lang, "thinking_max"): THINKING_BUDGETS["max"],
        }
        return mapping.get(label, THINKING_BUDGETS["off"])

    def apply_language(self):
        self.lang = self.config.get("language", "en")
        self.setWindowTitle(t(self.lang, "app_title"))
        self.open_folder_btn.setText(t(self.lang, "open_folder"))
        self.clear_chat_btn.setText(t(self.lang, "new_chat"))
        self.settings_btn.setText(t(self.lang, "settings"))
        self.send_btn.setText(t(self.lang, "send"))
        self.clear_file_btn.setText(t(self.lang, "remove"))
        self.input_box.setPlaceholderText(t(self.lang, "input_placeholder"))
        self.thinking_btn.set_items(self.get_thinking_labels())
        if self.selected_file_path:
            self.file_badge.setText(
                t(self.lang, "attached_file", name=os.path.basename(self.selected_file_path))
            )

    def open_settings(self):
        dialog = SettingsDialog(self.config, self)
        if dialog.exec() == QDialog.Accepted:
            self.config = dialog.get_updated_config()
            save_config(self.config)
            self.apply_language()
            provider = self.provider_btn.currentText()
            self.model_btn.set_items(self.get_active_models(provider), keep_current=True)
            if provider == "Gemini":
                self.init_gemini_session()
            self.add_message(
                t(self.lang, "role_system"),
                t(self.lang, "msg_settings_saved"),
                role="system",
            )

    def setup_ui(self):
        self.setStyleSheet(MAIN_STYLESHEET)

        root_layout = QHBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        self.sidebar = QFrame()
        self.sidebar.setMinimumWidth(0)
        self.sidebar.setMaximumWidth(260)
        self.sidebar.setStyleSheet(f"""
            QFrame {{
                background-color: {SURFACE_BLACK};
                border-right: 1px solid {BORDER_DARK};
            }}
        """)
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(12, 14, 12, 14)
        sidebar_layout.setSpacing(10)

        sidebar_header = QHBoxLayout()
        self.open_folder_btn = QPushButton(t(self.lang, "open_folder"))
        self.open_folder_btn.setObjectName("SecondaryBtn")
        self.open_folder_btn.setCursor(Qt.PointingHandCursor)
        self.open_folder_btn.setStyleSheet(
            f"min-height: 28px; padding: 0 10px; font-size: 11px; border: 1px solid {BORDER_DARK}; border-radius: 6px;"
        )
        self.open_folder_btn.clicked.connect(self.choose_folder)

        sidebar_header.addStretch()
        sidebar_header.addWidget(self.open_folder_btn)
        sidebar_layout.addLayout(sidebar_header)

        self.file_model = QFileSystemModel()
        self.file_model.setRootPath(QDir.currentPath())
        self.file_model.setFilter(QDir.AllDirs | QDir.Files | QDir.NoDotAndDotDot)

        self.tree_view = QTreeView()
        self.tree_view.setModel(self.file_model)
        self.tree_view.setRootIndex(self.file_model.index(QDir.currentPath()))
        self.tree_view.setHeaderHidden(True)
        for col in range(1, 4):
            self.tree_view.hideColumn(col)
        self.tree_view.doubleClicked.connect(self.on_file_selected)
        sidebar_layout.addWidget(self.tree_view)

        root_layout.addWidget(self.sidebar)

        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(20, 14, 20, 18)
        right_layout.setSpacing(10)

        self.top_bar = QHBoxLayout()
        self.top_bar.setSpacing(8)

        self.clear_chat_btn = QPushButton(t(self.lang, "new_chat"))
        self.clear_chat_btn.setObjectName("SecondaryBtn")
        self.clear_chat_btn.setCursor(Qt.PointingHandCursor)
        self.clear_chat_btn.clicked.connect(self.reset_chat)

        self.settings_btn = QPushButton(t(self.lang, "settings"))
        self.settings_btn.setObjectName("SecondaryBtn")
        self.settings_btn.setCursor(Qt.PointingHandCursor)
        self.settings_btn.clicked.connect(self.open_settings)

        self.thinking_btn = DropdownButton(self.get_thinking_labels())
        self.thinking_btn.selection_changed.connect(self.on_settings_changed)

        provider_names = list(PROVIDERS.keys())
        self.provider_btn = DropdownButton(provider_names)
        self.provider_btn.selection_changed.connect(self.on_provider_changed)

        self.model_btn = DropdownButton(self.get_active_models(provider_names[0]))
        self.model_btn.selection_changed.connect(self.on_settings_changed)

        self.top_bar.addWidget(self.clear_chat_btn)
        self.top_bar.addWidget(self.settings_btn)
        self.top_bar.addStretch()
        self.top_bar.addWidget(self.thinking_btn)
        self.top_bar.addWidget(self.provider_btn)
        self.top_bar.addWidget(self.model_btn)
        right_layout.addLayout(self.top_bar)

        self.chat_scroll = QScrollArea()
        self.chat_scroll.setWidgetResizable(True)
        self.chat_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.chat_scroll.setFrameShape(QFrame.NoFrame)
        self.chat_scroll.setStyleSheet("background: transparent;")
        self.chat_scroll.verticalScrollBar().rangeChanged.connect(self._on_scroll_range_changed)

        self.messages_container = QWidget()
        self.messages_container.setStyleSheet("background: transparent;")
        self.messages_layout = QVBoxLayout(self.messages_container)
        self.messages_layout.setContentsMargins(6, 10, 12, 10)
        self.messages_layout.setSpacing(12)
        self.messages_layout.addStretch()

        self.chat_scroll.setWidget(self.messages_container)
        right_layout.addWidget(self.chat_scroll, 1)

        self.file_badge_bar = QWidget()
        file_badge_layout = QHBoxLayout(self.file_badge_bar)
        file_badge_layout.setContentsMargins(2, 0, 2, 0)
        self.file_badge = QLabel("")
        self.file_badge.setStyleSheet(f"color: {BURNT_ORANGE}; font-size: 12px; font-weight: 600;")
        self.clear_file_btn = QPushButton(t(self.lang, "remove"))
        self.clear_file_btn.setObjectName("SecondaryBtn")
        self.clear_file_btn.setStyleSheet(
            f"min-height: 22px; font-size: 11px; padding: 0 8px; border: 1px solid {BORDER_DARK}; border-radius: 5px;"
        )
        self.clear_file_btn.clicked.connect(self.clear_selected_file)

        file_badge_layout.addWidget(self.file_badge)
        file_badge_layout.addWidget(self.clear_file_btn)
        file_badge_layout.addStretch()
        self.file_badge_bar.hide()
        right_layout.addWidget(self.file_badge_bar)

        self.status_holder = QWidget()
        self.status_holder.setFixedHeight(22)
        status_layout = QVBoxLayout(self.status_holder)
        status_layout.setContentsMargins(2, 0, 2, 0)
        status_layout.setSpacing(3)

        self.loading_label = QLabel("")
        self.loading_label.setStyleSheet(f"color: {BURNT_ORANGE}; font-size: 12px; font-weight: 500;")

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)
        self.progress_bar.setFixedHeight(2)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setStyleSheet(f"""
            QProgressBar {{
                background-color: {BORDER_DARK};
                border: none;
            }}
            QProgressBar::chunk {{
                background-color: {BURNT_ORANGE};
            }}
        """)
        self.progress_bar.hide()

        status_layout.addWidget(self.loading_label)
        status_layout.addWidget(self.progress_bar)
        self.status_holder.hide()
        right_layout.addWidget(self.status_holder)

        input_layout = QHBoxLayout()
        input_layout.setSpacing(10)
        input_layout.setAlignment(Qt.AlignBottom)

        self.input_box = ChatInputBox(t(self.lang, "input_placeholder"))
        self.input_box.submit_pressed.connect(self.send_message)

        self.send_btn = QPushButton(t(self.lang, "send"))
        self.send_btn.setCursor(Qt.PointingHandCursor)
        self.send_btn.clicked.connect(self.send_message)

        input_layout.addWidget(self.input_box, 1)
        input_layout.addWidget(self.send_btn)
        right_layout.addLayout(input_layout)

        root_layout.addWidget(right_panel, 1)

        self.sidebar_anim = QPropertyAnimation(self.sidebar, b"maximumWidth")
        self.sidebar_anim.setDuration(200)
        self.sidebar_anim.setEasingCurve(QEasingCurve.InOutCubic)

        self.toggle_sidebar_btn = QPushButton("☰", self)
        self.toggle_sidebar_btn.setObjectName("SecondaryBtn")
        self.toggle_sidebar_btn.setCursor(Qt.PointingHandCursor)
        self.toggle_sidebar_btn.setFixedSize(38, 38)
        self.toggle_sidebar_btn.move(12, 14)
        self.toggle_sidebar_btn.setStyleSheet(
            f"min-height: 36px; padding: 0; font-size: 16px; border: 1px solid {BORDER_DARK}; border-radius: 8px;"
        )
        self.toggle_sidebar_btn.clicked.connect(self.toggle_sidebar)
        self.toggle_sidebar_btn.raise_()

    def _on_scroll_range_changed(self, min_val, max_val):
        if self.auto_scroll:
            self.chat_scroll.verticalScrollBar().setValue(max_val)

    def toggle_sidebar(self):
        target = 0 if self.sidebar_open else 260
        self.sidebar_anim.stop()
        self.sidebar_anim.setStartValue(self.sidebar.width())
        self.sidebar_anim.setEndValue(target)
        self.sidebar_anim.start()
        self.sidebar_open = not self.sidebar_open
        self.top_bar.setContentsMargins(0 if self.sidebar_open else 40, 0, 0, 0)

    def reset_chat(self):
        while self.messages_layout.count() > 1:
            item = self.messages_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self.conversation_history.clear()
        if self.provider_btn.currentText() == "Gemini":
            self.init_gemini_session()
        self.add_message(t(self.lang, "role_system"), t(self.lang, "msg_new_chat"), role="system")

    def init_gemini_session(self):
        key = self.config.get("gemini_key", "").strip()
        selected_model = self.model_btn.currentText()
        if not key or self.provider_btn.currentText() != "Gemini":
            self.chat = None
            return

        budget = self.get_thinking_budget()

        self.client = genai.Client(api_key=key, http_options={"timeout": 60000})

        config_args = {
            "system_instruction": self.config.get("system_prompt", DEFAULT_SYSTEM_PROMPT),
            "temperature": 0.3,
        }

        if "lite" not in selected_model and budget > 0:
            config_args["thinking_config"] = types.ThinkingConfig(thinking_budget=budget)

        gemini_history = []
        for msg in self.conversation_history:
            role = "user" if msg["role"] == "user" else "model"
            gemini_history.append(
                types.Content(role=role, parts=[types.Part.from_text(text=msg["content"])])
            )

        self.chat = self.client.chats.create(
            model=selected_model,
            config=types.GenerateContentConfig(**config_args),
            history=gemini_history,
        )

    def on_provider_changed(self, provider: str):
        self.model_btn.set_items(self.get_active_models(provider))
        self.on_settings_changed()

    def on_settings_changed(self):
        provider = self.provider_btn.currentText()
        selected_model = self.model_btn.currentText()
        thinking_text = self.thinking_btn.currentText()
        if provider == "Gemini":
            self.init_gemini_session()
        self.add_message(
            t(self.lang, "role_system"),
            f"{provider}: {selected_model}  •  {thinking_text}",
            role="system",
        )

    def choose_folder(self):
        folder = QFileDialog.getExistingDirectory(
            self, t(self.lang, "select_folder_dialog"), QDir.currentPath()
        )
        if folder:
            self.file_model.setRootPath(folder)
            self.tree_view.setRootIndex(self.file_model.index(folder))
            if not self.sidebar_open:
                self.toggle_sidebar()

    def on_file_selected(self, index):
        path = self.file_model.filePath(index)
        if os.path.isfile(path):
            self.selected_file_path = path
            self.file_badge.setText(t(self.lang, "attached_file", name=os.path.basename(path)))
            self.file_badge_bar.show()
            self.input_box.setFocus()

    def clear_selected_file(self):
        self.selected_file_path = None
        self.file_badge.setText("")
        self.file_badge_bar.hide()

    def setup_loader(self):
        self.dot_count = 0
        self.anim_timer = QTimer(self)
        self.anim_timer.timeout.connect(self.update_loading_text)

    def update_loading_text(self):
        self.dot_count = (self.dot_count + 1) % 4
        self.loading_label.setText(t(self.lang, "generating") + "." * self.dot_count)

    def add_message(self, sender: str, text: str, role: str = "assistant", attachment: str = None):
        self.auto_scroll = True
        bubble = MessageBubble(sender, text, role=role, attachment=attachment, lang_code=self.lang)
        insert_pos = self.messages_layout.count() - 1
        self.messages_layout.insertWidget(insert_pos, bubble)

    def send_message(self):
        provider = self.provider_btn.currentText()
        selected_model = self.model_btn.currentText()
        budget = self.get_thinking_budget()

        key_field = PROVIDERS[provider]["key_field"]
        api_key = self.config.get(key_field, "").strip()

        if not api_key:
            self.add_message(
                t(self.lang, "role_system"),
                t(self.lang, "msg_missing_key", provider=provider),
                role="system",
            )
            self.open_settings()
            return

        if provider == "Gemini" and not self.chat:
            self.init_gemini_session()

        user_text = self.input_box.toPlainText().strip()
        if not user_text:
            return

        attached_name = None
        prompt_to_send = user_text

        if self.selected_file_path and os.path.exists(self.selected_file_path):
            try:
                with open(self.selected_file_path, "r", encoding="utf-8", errors="ignore") as f:
                    file_content = f.read()
                attached_name = os.path.basename(self.selected_file_path)
                prompt_to_send = f"File ({attached_name}):\n```\n{file_content}\n```\n\nQuestion: {user_text}"
            except Exception as e:
                self.add_message(
                    t(self.lang, "role_system"),
                    t(self.lang, "msg_file_read_error", error=str(e)),
                    role="system",
                )
                return

        self.add_message(t(self.lang, "role_user"), user_text, role="user", attachment=attached_name)
        self.conversation_history.append({"role": "user", "content": prompt_to_send})

        self.input_box.clear()
        self.input_box.setEnabled(False)
        self.send_btn.setEnabled(False)

        self.dot_count = 0
        self.loading_label.setText(t(self.lang, "generating"))
        self.status_holder.show()
        self.progress_bar.show()
        self.anim_timer.start(300)

        self.worker = AIWorker(
            provider=provider,
            model=selected_model,
            budget=budget,
            api_key=api_key,
            history=list(self.conversation_history),
            system_prompt=self.config.get("system_prompt", DEFAULT_SYSTEM_PROMPT),
            max_tokens=int(self.config.get("max_tokens", 4096)),
            chat_session=self.chat,
            user_message=prompt_to_send,
        )
        self.worker.response_ready.connect(self.handle_response)
        self.worker.error_occurred.connect(self.handle_error)
        self.worker.start()

    def handle_response(self, response_text: str):
        self.conversation_history.append({"role": "assistant", "content": response_text})
        self.add_message(t(self.lang, "role_assistant"), response_text, role="assistant")
        self.reset_input()

    def handle_error(self, error_msg: str):
        if self.conversation_history and self.conversation_history[-1]["role"] == "user":
            self.conversation_history.pop()
        self.add_message(
            t(self.lang, "role_system"),
            t(self.lang, "msg_error", error=error_msg),
            role="system",
        )
        self.reset_input()

    def reset_input(self):
        self.anim_timer.stop()
        self.loading_label.setText("")
        self.progress_bar.hide()
        self.status_holder.hide()
        self.input_box.setEnabled(True)
        self.send_btn.setEnabled(True)
        self.input_box.setFocus()