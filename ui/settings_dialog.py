from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox, QComboBox, QDialog, QFormLayout, QFrame,
    QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QScrollArea, QSpinBox, QTabWidget, QTextEdit, QToolTip,
    QVBoxLayout, QWidget,
)
from core.config import DEFAULT_SYSTEM_PROMPT
from core.providers import PROVIDERS, get_model_info
from core.translations import t
from ui.theme import BURNT_ORANGE, DIALOG_STYLESHEET, MUTED_STONE


class InfoBadge(QLabel):
    def __init__(self, tip: str):
        super().__init__("i")
        self.tip = tip
        self.setAlignment(Qt.AlignCenter)
        self.setFixedSize(18, 18)
        self.setCursor(Qt.PointingHandCursor)
        self.setStyleSheet(f"""
            QLabel {{
                color: {MUTED_STONE};
                border: 1px solid {MUTED_STONE};
                border-radius: 9px;
                font-size: 11px;
                font-weight: 700;
                background: transparent;
            }}
            QLabel:hover {{
                color: {BURNT_ORANGE};
                border-color: {BURNT_ORANGE};
            }}
        """)

    def enterEvent(self, event):
        QToolTip.showText(self.mapToGlobal(self.rect().bottomRight()), self.tip, self)
        super().enterEvent(event)

    def leaveEvent(self, event):
        QToolTip.hideText()
        super().leaveEvent(event)


class SettingsDialog(QDialog):
    def __init__(self, config: dict, parent=None):
        super().__init__(parent)
        self.config = dict(config)
        self.lang = self.config.get("language", "en")
        self.key_inputs = {}
        self.model_checkboxes = {}
        self.setWindowTitle(t(self.lang, "settings_title"))
        self.setMinimumSize(540, 480)
        self.setup_ui()

    def setup_ui(self):
        self.setStyleSheet(DIALOG_STYLESHEET)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(14)

        tabs = QTabWidget()

        # Sekme 1: API Anahtarları
        api_tab = QWidget()
        api_tab.setStyleSheet("background: transparent;")
        api_layout = QVBoxLayout(api_tab)
        api_layout.setSpacing(12)

        form = QFormLayout()
        form.setSpacing(10)
        form.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)

        for info in PROVIDERS.values():
            field = info["key_field"]
            inp = QLineEdit()
            inp.setEchoMode(QLineEdit.Password)
            inp.setPlaceholderText(info["placeholder"])
            inp.setText(self.config.get(field, ""))
            self.key_inputs[field] = inp
            form.addRow(QLabel(f"{info['label']}:"), inp)

        api_layout.addLayout(form)

        self.show_keys_cb = QCheckBox(t(self.lang, "show_keys"))
        self.show_keys_cb.toggled.connect(self.toggle_key_visibility)
        api_layout.addWidget(self.show_keys_cb)
        api_layout.addStretch()

        tabs.addTab(api_tab, t(self.lang, "tab_api_keys"))

        # Sekme 2: Modeller (Aç/Kapat)
        models_tab = QWidget()
        models_tab.setStyleSheet("background: transparent;")
        models_outer = QVBoxLayout(models_tab)
        models_outer.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("background: transparent;")

        scroll_content = QWidget()
        scroll_content.setStyleSheet("background: transparent;")
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setSpacing(8)

        enabled_map = self.config.get("enabled_models", {})

        for provider_name, info in PROVIDERS.items():
            header = QLabel(info["label"])
            header.setStyleSheet(
                f"color: {BURNT_ORANGE}; font-size: 12px; font-weight: 700; margin-top: 6px;"
            )
            scroll_layout.addWidget(header)

            active_models = enabled_map.get(provider_name, info["models"])
            self.model_checkboxes[provider_name] = {}

            for model_id in info["models"]:
                row = QHBoxLayout()
                row.setSpacing(8)
                row.setContentsMargins(0, 0, 0, 0)

                cb = QCheckBox(model_id)
                cb.setChecked(model_id in active_models)
                self.model_checkboxes[provider_name][model_id] = cb

                info_icon = InfoBadge(get_model_info(model_id, self.lang))

                row.addWidget(cb)
                row.addWidget(info_icon)
                row.addStretch()
                scroll_layout.addLayout(row)

        scroll_layout.addStretch()
        scroll.setWidget(scroll_content)
        models_outer.addWidget(scroll)

        models_tab_label = "Modeller" if self.lang == "tr" else "Models"
        tabs.addTab(models_tab, models_tab_label)

        # Sekme 3: Genel Ayarlar
        general_tab = QWidget()
        general_tab.setStyleSheet("background: transparent;")
        gen_layout = QVBoxLayout(general_tab)
        gen_layout.setSpacing(12)

        lang_row = QHBoxLayout()
        lang_row.addWidget(QLabel(t(self.lang, "language_label")))
        self.lang_combo = QComboBox()
        self.lang_combo.addItem("English", "en")
        self.lang_combo.addItem("Türkçe", "tr")
        idx = self.lang_combo.findData(self.lang)
        if idx >= 0:
            self.lang_combo.setCurrentIndex(idx)
        lang_row.addWidget(self.lang_combo)
        lang_row.addStretch()
        gen_layout.addLayout(lang_row)

        gen_layout.addWidget(QLabel(t(self.lang, "system_prompt_label")))
        self.sys_prompt_edit = QTextEdit()
        self.sys_prompt_edit.setFixedHeight(100)
        self.sys_prompt_edit.setPlainText(self.config.get("system_prompt", DEFAULT_SYSTEM_PROMPT))
        gen_layout.addWidget(self.sys_prompt_edit)

        token_row = QHBoxLayout()
        token_row.addWidget(QLabel(t(self.lang, "max_tokens_label")))
        self.max_tokens_spin = QSpinBox()
        self.max_tokens_spin.setRange(256, 32768)
        self.max_tokens_spin.setSingleStep(512)
        self.max_tokens_spin.setValue(int(self.config.get("max_tokens", 4096)))
        token_row.addWidget(self.max_tokens_spin)
        token_row.addStretch()
        gen_layout.addLayout(token_row)
        gen_layout.addStretch()

        tabs.addTab(general_tab, t(self.lang, "tab_general"))
        layout.addWidget(tabs)

        btn_row = QHBoxLayout()
        btn_row.addStretch()

        cancel_btn = QPushButton(t(self.lang, "cancel"))
        cancel_btn.setObjectName("CancelBtn")
        cancel_btn.setCursor(Qt.PointingHandCursor)
        cancel_btn.clicked.connect(self.reject)

        save_btn = QPushButton(t(self.lang, "save"))
        save_btn.setCursor(Qt.PointingHandCursor)
        save_btn.clicked.connect(self.accept)

        btn_row.addWidget(cancel_btn)
        btn_row.addWidget(save_btn)
        layout.addLayout(btn_row)

    def toggle_key_visibility(self, checked: bool):
        mode = QLineEdit.Normal if checked else QLineEdit.Password
        for inp in self.key_inputs.values():
            inp.setEchoMode(mode)

    def get_updated_config(self) -> dict:
        updated = dict(self.config)
        for field, inp in self.key_inputs.items():
            updated[field] = inp.text().strip()

        enabled_models = {}
        for provider_name, cb_map in self.model_checkboxes.items():
            selected = [m for m, cb in cb_map.items() if cb.isChecked()]
            enabled_models[provider_name] = selected if selected else [PROVIDERS[provider_name]["models"][0]]
        updated["enabled_models"] = enabled_models

        updated["language"] = self.lang_combo.currentData()
        updated["system_prompt"] = self.sys_prompt_edit.toPlainText().strip() or DEFAULT_SYSTEM_PROMPT
        updated["max_tokens"] = self.max_tokens_spin.value()
        return updated