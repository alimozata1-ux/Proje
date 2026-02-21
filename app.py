import json
import os
import sys
from dataclasses import asdict, dataclass
from urllib.parse import quote_plus

from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QAction, QColor
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QColorDialog,
    QDialog,
    QFormLayout,
    QFrame,
    QGraphicsDropShadowEffect,
    QGraphicsOpacityEffect,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QSlider,
    QSpinBox,
    QTabWidget,
    QToolBar,
    QVBoxLayout,
    QWidget,
)

CONFIG_FILE = "settings.json"
SEARCH_PROVIDERS = {
    "duckduckgo": "https://duckduckgo.com/?q={}",
    "google": "https://www.google.com/search?q={}",
    "yandex": "https://yandex.com/search/?text={}",
}


@dataclass
class BrowserSettings:
    toolbar_opacity: int = 75
    neon_color: str = "#00ffff"
    neon_thickness: int = 2
    glow_radius: int = 18
    corner_radius: int = 18
    home_page: str = "https://duckduckgo.com"
    search_provider: str = "duckduckgo"

    @property
    def search_engine(self) -> str:
        return SEARCH_PROVIDERS.get(self.search_provider, SEARCH_PROVIDERS["duckduckgo"])


class SettingsStore:
    @staticmethod
    def load() -> BrowserSettings:
        defaults = asdict(BrowserSettings())
        if not os.path.exists(CONFIG_FILE):
            return BrowserSettings()

        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (json.JSONDecodeError, TypeError):
            return BrowserSettings()

        # Eski yapıdan (search_engine URL) provider'a geçiş uyumluluğu
        if "search_provider" not in data and "search_engine" in data:
            old_search = str(data.get("search_engine", ""))
            for provider, template in SEARCH_PROVIDERS.items():
                if old_search == template:
                    data["search_provider"] = provider
                    break
            else:
                data["search_provider"] = "duckduckgo"

        merged = {**defaults, **data}
        return BrowserSettings(**{k: merged[k] for k in defaults})

    @staticmethod
    def save(settings: BrowserSettings) -> None:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(asdict(settings), f, ensure_ascii=False, indent=2)


class SettingsDialog(QDialog):
    def __init__(self, settings: BrowserSettings, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Detaylı Ayarlar")
        self.settings = BrowserSettings(**asdict(settings))

        tabs = QTabWidget()
        tabs.addTab(self._build_theme_tab(), "Tema / Aero")
        tabs.addTab(self._build_browser_tab(), "Tarayıcı")

        save_btn = QPushButton("Kaydet")
        save_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton("Vazgeç")
        cancel_btn.clicked.connect(self.reject)

        buttons = QHBoxLayout()
        buttons.addStretch()
        buttons.addWidget(cancel_btn)
        buttons.addWidget(save_btn)

        layout = QVBoxLayout(self)
        layout.addWidget(tabs)
        layout.addLayout(buttons)
        self.setMinimumWidth(500)

    def _build_theme_tab(self) -> QWidget:
        page = QWidget()
        form = QFormLayout(page)

        self.opacity_slider = QSlider(Qt.Horizontal)
        self.opacity_slider.setRange(35, 100)
        self.opacity_slider.setValue(self.settings.toolbar_opacity)
        self.opacity_value = QLabel(f"%{self.settings.toolbar_opacity}")
        self.opacity_slider.valueChanged.connect(lambda v: self.opacity_value.setText(f"%{v}"))

        opacity_box = QHBoxLayout()
        opacity_box.addWidget(self.opacity_slider)
        opacity_box.addWidget(self.opacity_value)

        self.color_btn = QPushButton(self.settings.neon_color)
        self.color_btn.clicked.connect(self._pick_color)
        self._paint_color_button()

        self.thickness_spin = QSpinBox()
        self.thickness_spin.setRange(1, 8)
        self.thickness_spin.setValue(self.settings.neon_thickness)

        self.glow_spin = QSpinBox()
        self.glow_spin.setRange(6, 45)
        self.glow_spin.setValue(self.settings.glow_radius)

        self.corner_spin = QSpinBox()
        self.corner_spin.setRange(8, 30)
        self.corner_spin.setValue(self.settings.corner_radius)

        form.addRow("Araç çubuğu şeffaflık:", self._wrap(opacity_box))
        form.addRow("Neon çizgi rengi:", self.color_btn)
        form.addRow("Neon çizgi kalınlığı:", self.thickness_spin)
        form.addRow("Neon parlama yarıçapı:", self.glow_spin)
        form.addRow("Köşe yuvarlaklığı:", self.corner_spin)
        return page

    def _build_browser_tab(self) -> QWidget:
        page = QWidget()
        form = QFormLayout(page)

        self.home_input = QLineEdit(self.settings.home_page)
        self.provider_combo = QComboBox()
        self.provider_combo.addItem("DuckDuckGo", "duckduckgo")
        self.provider_combo.addItem("Google", "google")
        self.provider_combo.addItem("Yandex", "yandex")

        current_index = self.provider_combo.findData(self.settings.search_provider)
        if current_index >= 0:
            self.provider_combo.setCurrentIndex(current_index)

        form.addRow("Anasayfa:", self.home_input)
        form.addRow("Arama sağlayıcısı:", self.provider_combo)
        return page

    def _wrap(self, layout: QHBoxLayout) -> QWidget:
        w = QWidget()
        w.setLayout(layout)
        return w

    def _pick_color(self):
        color = QColorDialog.getColor(QColor(self.settings.neon_color), self, "Neon Rengi")
        if color.isValid():
            self.settings.neon_color = color.name()
            self.color_btn.setText(self.settings.neon_color)
            self._paint_color_button()

    def _paint_color_button(self):
        self.color_btn.setStyleSheet(
            f"""
            QPushButton {{
                background-color: {self.settings.neon_color};
                color: #111;
                border-radius: 8px;
                font-weight: 700;
                padding: 6px 10px;
            }}
            """
        )

    def get_settings(self) -> BrowserSettings:
        self.settings.toolbar_opacity = self.opacity_slider.value()
        self.settings.neon_thickness = self.thickness_spin.value()
        self.settings.glow_radius = self.glow_spin.value()
        self.settings.corner_radius = self.corner_spin.value()
        self.settings.home_page = self.home_input.text().strip() or "https://duckduckgo.com"
        self.settings.search_provider = self.provider_combo.currentData()
        return self.settings


class NeonBrowser(QMainWindow):
    def __init__(self):
        super().__init__()
        self.settings = SettingsStore.load()

        self.setWindowTitle("Neon Aero Browser")
        self.resize(1240, 780)

        self.frame = QFrame()
        self.frame_layout = QVBoxLayout(self.frame)
        self.frame_layout.setContentsMargins(16, 16, 16, 16)
        self.frame_layout.setSpacing(8)

        self.toolbar = QToolBar("Gezinme")
        self.toolbar.setMovable(False)

        back_action = QAction("◀", self)
        back_action.triggered.connect(lambda: self.current_web_view().back())
        next_action = QAction("▶", self)
        next_action.triggered.connect(lambda: self.current_web_view().forward())
        refresh_action = QAction("⟳", self)
        refresh_action.triggered.connect(lambda: self.current_web_view().reload())
        home_action = QAction("⌂", self)
        home_action.triggered.connect(self.go_home)
        new_tab_action = QAction("＋ Sekme", self)
        new_tab_action.triggered.connect(lambda: self.add_new_tab(QUrl(self.settings.home_page), "Yeni Sekme"))
        close_tab_action = QAction("✕ Sekme", self)
        close_tab_action.triggered.connect(self.close_current_tab)
        settings_action = QAction("⚙ Ayarlar", self)
        settings_action.triggered.connect(self.open_settings)

        self.address_bar = QLineEdit()
        self.address_bar.returnPressed.connect(self.navigate)

        self.toolbar.addAction(back_action)
        self.toolbar.addAction(next_action)
        self.toolbar.addAction(refresh_action)
        self.toolbar.addAction(home_action)
        self.toolbar.addAction(new_tab_action)
        self.toolbar.addAction(close_tab_action)
        self.toolbar.addWidget(self.address_bar)
        self.toolbar.addAction(settings_action)

        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.tabs.currentChanged.connect(self._on_tab_changed)

        self.frame_layout.addWidget(self.toolbar)
        self.frame_layout.addWidget(self.tabs)
        self.setCentralWidget(self.frame)

        self.apply_theme()
        self.add_new_tab(QUrl(self.settings.home_page), "Ana Sayfa")

    def add_new_tab(self, url: QUrl, label: str):
        browser = QWebEngineView()
        browser.setUrl(url)
        browser.urlChanged.connect(lambda qurl, b=browser: self._on_url_changed(qurl, b))
        browser.titleChanged.connect(lambda title, b=browser: self._update_tab_title(b, title))

        index = self.tabs.addTab(browser, label)
        self.tabs.setCurrentIndex(index)

    def current_web_view(self) -> QWebEngineView:
        current = self.tabs.currentWidget()
        return current if isinstance(current, QWebEngineView) else QWebEngineView()

    def close_tab(self, index: int):
        if self.tabs.count() == 1:
            return
        self.tabs.removeTab(index)

    def close_current_tab(self):
        self.close_tab(self.tabs.currentIndex())

    def _on_tab_changed(self, index: int):
        widget = self.tabs.widget(index)
        if isinstance(widget, QWebEngineView):
            self.address_bar.setText(widget.url().toString())

    def _update_tab_title(self, browser: QWebEngineView, title: str):
        index = self.tabs.indexOf(browser)
        if index >= 0:
            self.tabs.setTabText(index, title[:25] if title else "Yeni Sekme")

    def apply_theme(self):
        rgba_opacity = int(max(0, min(self.settings.toolbar_opacity, 100)) * 2.55)
        neon = self.settings.neon_color

        shadow = QGraphicsDropShadowEffect(self.frame)
        shadow.setBlurRadius(self.settings.glow_radius)
        shadow.setColor(QColor(neon))
        shadow.setOffset(0, 0)
        self.frame.setGraphicsEffect(shadow)

        self.frame.setStyleSheet(
            f"""
            QFrame {{
                background-color: rgba(20, 24, 35, 220);
                border: {self.settings.neon_thickness}px solid {neon};
                border-radius: {self.settings.corner_radius}px;
            }}
            QLineEdit, QComboBox {{
                background-color: rgba(12, 16, 24, 220);
                color: #e8f7ff;
                border: 1px solid {neon};
                border-radius: 10px;
                padding: 6px;
            }}
            QToolBar {{
                spacing: 8px;
                border: none;
                background: transparent;
            }}
            QToolButton {{
                background-color: rgba(15, 25, 35, 200);
                color: {neon};
                border: 1px solid {neon};
                border-radius: 8px;
                padding: 6px 10px;
                font-weight: 700;
            }}
            QToolButton:hover {{
                background-color: rgba(35, 45, 65, 220);
            }}
            QTabBar::tab {{
                background: rgba(16, 22, 34, 220);
                color: #d9f5ff;
                border: 1px solid {neon};
                border-radius: 8px;
                padding: 6px 10px;
                margin-right: 4px;
            }}
            QTabBar::tab:selected {{
                background: rgba(28, 40, 58, 240);
                color: {neon};
            }}
            """
        )

        opacity = QGraphicsOpacityEffect(self.toolbar)
        opacity.setOpacity(rgba_opacity / 255)
        self.toolbar.setGraphicsEffect(opacity)
        self.setStyleSheet("QMainWindow { background-color: #0b0f18; }")

    def open_settings(self):
        dialog = SettingsDialog(self.settings, self)
        if dialog.exec() == QDialog.Accepted:
            self.settings = dialog.get_settings()
            SettingsStore.save(self.settings)
            self.apply_theme()

    def go_home(self):
        self.current_web_view().setUrl(QUrl(self.settings.home_page))

    def navigate(self):
        raw = self.address_bar.text().strip()
        if not raw:
            return

        target = self.current_web_view()
        if raw.startswith("http://") or raw.startswith("https://"):
            target.setUrl(QUrl(raw))
            return

        if "." in raw and " " not in raw:
            target.setUrl(QUrl("https://" + raw))
            return

        search_url = self.settings.search_engine.format(quote_plus(raw))
        target.setUrl(QUrl(search_url))

    def _on_url_changed(self, url: QUrl, browser: QWebEngineView):
        if browser == self.current_web_view():
            self.address_bar.setText(url.toString())


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Neon Aero Browser")
    window = NeonBrowser()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
