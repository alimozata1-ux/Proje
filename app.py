import sys
from datetime import datetime

from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QApplication,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMenu,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)
import qtawesome as qta


class DesktopIcon(QFrame):
    def __init__(self, icon_name: str, title: str, callback, parent=None):
        super().__init__(parent)
        self.setObjectName("desktopIcon")
        self.setFixedSize(120, 120)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        btn = QPushButton()
        btn.setObjectName("iconButton")
        btn.setIcon(qta.icon(icon_name, color="#ffffff"))
        btn.setIconSize(btn.sizeHint())
        btn.setFixedSize(56, 56)
        btn.clicked.connect(callback)

        label = QLabel(title)
        label.setObjectName("iconLabel")
        label.setWordWrap(True)
        label.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        layout.addWidget(btn, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)


class Win7Simulator(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Windows 7 Simülatör (Python)")
        self.resize(1200, 740)
        self.setMinimumSize(900, 600)

        self.central = QWidget()
        self.central.setObjectName("desktop")
        self.setCentralWidget(self.central)

        root_layout = QVBoxLayout(self.central)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        self.desktop_area = QWidget()
        desktop_layout = QGridLayout(self.desktop_area)
        desktop_layout.setContentsMargins(20, 20, 20, 20)
        desktop_layout.setHorizontalSpacing(18)
        desktop_layout.setVerticalSpacing(18)
        desktop_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)

        desktop_layout.addWidget(
            DesktopIcon("fa5s.folder", "Belgeler", self.open_documents), 0, 0
        )
        desktop_layout.addWidget(
            DesktopIcon("fa5s.image", "Resimler", self.open_gallery), 1, 0
        )
        desktop_layout.addWidget(
            DesktopIcon("fa5s.globe", "Tarayıcı", self.open_browser), 2, 0
        )

        self.window_panel = QTextEdit()
        self.window_panel.setReadOnly(True)
        self.window_panel.setObjectName("windowPanel")
        self.window_panel.setPlaceholderText(
            "Bir masaüstü ikonuna tıklayarak simülasyondaki pencereleri açabilirsin..."
        )

        desktop_layout.addWidget(self.window_panel, 0, 1, 3, 3)

        root_layout.addWidget(self.desktop_area, stretch=1)
        root_layout.addWidget(self.create_taskbar())

        self.apply_styles()

    def create_taskbar(self):
        taskbar = QFrame()
        taskbar.setObjectName("taskbar")
        taskbar.setFixedHeight(52)

        layout = QHBoxLayout(taskbar)
        layout.setContentsMargins(8, 6, 8, 6)
        layout.setSpacing(10)

        self.start_button = QPushButton(" Başlat")
        self.start_button.setObjectName("startButton")
        self.start_button.setIcon(qta.icon("fa5s.windows", color="#ffffff"))
        self.start_button.clicked.connect(self.show_start_menu)

        self.quick_btn1 = QPushButton()
        self.quick_btn1.setObjectName("quickButton")
        self.quick_btn1.setIcon(qta.icon("fa5s.folder-open", color="#ffffff"))
        self.quick_btn1.clicked.connect(self.open_documents)

        self.quick_btn2 = QPushButton()
        self.quick_btn2.setObjectName("quickButton")
        self.quick_btn2.setIcon(qta.icon("fa5s.globe", color="#ffffff"))
        self.quick_btn2.clicked.connect(self.open_browser)

        self.clock = QLabel()
        self.clock.setObjectName("clockLabel")
        self.update_clock()

        timer = QTimer(self)
        timer.timeout.connect(self.update_clock)
        timer.start(1000)

        layout.addWidget(self.start_button)
        layout.addWidget(self.quick_btn1)
        layout.addWidget(self.quick_btn2)
        layout.addStretch(1)
        layout.addWidget(self.clock)

        return taskbar

    def show_start_menu(self):
        menu = QMenu(self)
        menu.setObjectName("startMenu")

        actions = [
            ("fa5s.folder", "Bilgisayar", self.open_documents),
            ("fa5s.image", "Resimler", self.open_gallery),
            ("fa5s.globe", "İnternet", self.open_browser),
            ("fa5s.power-off", "Kapat", self.close),
        ]

        for icon_name, label, callback in actions:
            action = QAction(qta.icon(icon_name, color="#0f2c56"), label, self)
            action.triggered.connect(callback)
            menu.addAction(action)

        menu.exec(self.start_button.mapToGlobal(self.start_button.rect().bottomLeft()))

    def update_clock(self):
        self.clock.setText(datetime.now().strftime("%H:%M\n%d.%m.%Y"))

    def open_documents(self):
        self.window_panel.setPlainText(
            "[Belgeler]\n\n- Odevler.docx\n- Sunum.pptx\n- ProjePlan.xlsx"
        )

    def open_gallery(self):
        self.window_panel.setPlainText(
            "[Resimler]\n\n- yaz_tatili.jpg\n- wallpaper_windows7.png\n- notlar.png"
        )

    def open_browser(self):
        self.window_panel.setPlainText(
            "[İnternet Gezgini]\n\nwww.example.com\n\nBu alan, bir tarayıcı görünümü"
            " gibi davranan demo panelidir."
        )

    def apply_styles(self):
        self.setStyleSheet(
            """
            QWidget#desktop {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #0b3b7a, stop:0.55 #0f5bb0, stop:1 #2f90d4);
            }
            QFrame#desktopIcon {
                border-radius: 8px;
                background: rgba(255,255,255,0.04);
            }
            QPushButton#iconButton {
                border-radius: 28px;
                border: 1px solid rgba(255,255,255,0.25);
                background-color: rgba(30,100,180,0.45);
            }
            QPushButton#iconButton:hover {
                background-color: rgba(60,130,220,0.6);
            }
            QLabel#iconLabel {
                color: #ffffff;
                font-size: 13px;
                text-shadow: 1px 1px #000;
            }
            QTextEdit#windowPanel {
                background-color: rgba(255,255,255,0.90);
                border: 1px solid #8fb4e8;
                border-radius: 7px;
                padding: 12px;
                font-size: 14px;
            }
            QFrame#taskbar {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #2a68ad, stop:1 #0f3f7f);
                border-top: 1px solid #84aee2;
            }
            QPushButton#startButton {
                color: #ffffff;
                font-weight: 700;
                border: 1px solid #66b66a;
                border-radius: 16px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #6fd66f, stop:1 #2d9e36);
                padding: 6px 14px;
            }
            QPushButton#startButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #82e982, stop:1 #3cb145);
            }
            QPushButton#quickButton {
                min-width: 32px;
                max-width: 32px;
                min-height: 32px;
                max-height: 32px;
                border-radius: 6px;
                border: 1px solid rgba(255,255,255,0.22);
                background: rgba(255,255,255,0.12);
            }
            QPushButton#quickButton:hover {
                background: rgba(255,255,255,0.23);
            }
            QLabel#clockLabel {
                color: #ffffff;
                padding: 2px 10px;
                border-left: 1px solid rgba(255,255,255,0.3);
                font-size: 12px;
            }
            QMenu#startMenu {
                background-color: #f2f8ff;
                border: 1px solid #7aa7d8;
                padding: 6px;
            }
            QMenu#startMenu::item {
                padding: 7px 22px 7px 12px;
                border-radius: 4px;
                color: #16395d;
            }
            QMenu#startMenu::item:selected {
                background-color: #d4e8ff;
            }
            """
        )


def main():
    app = QApplication(sys.argv)
    win = Win7Simulator()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
