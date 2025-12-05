import sys
import os
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QComboBox
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt
from dotenv import load_dotenv
from profile_detector import detect_chrome_profiles

load_dotenv()

CHROME_DIR = os.getenv("CHROME_DIR")

class ProfileSelector(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Selectează profil Facebook")
        self.setFixedSize(380, 200)

        # ───────── STYLE GLOBAL (Modern UI) ─────────
        self.setStyleSheet("""
            QWidget {
                background-color: #f7f9fc;
                font-family: 'Segoe UI';
            }
            QLabel {
                font-size: 16px;
                color: #2a2a2a;
                font-weight: bold;
            }
            QComboBox {
                font-size: 15px;
                padding: 6px;
                border-radius: 6px;
                border: 1px solid #aab7c4;
                background-color: white;
            }
            QPushButton {
                background-color: #4a90e2;
                color: white;
                font-size: 15px;
                border-radius: 8px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #357abd;
            }
            QPushButton:pressed {
                background-color: #2d63a3;
            }
        """)

        # ───────── Layout principal ─────────
        layout = QVBoxLayout()
        layout.setContentsMargins(30, 25, 30, 25)
        layout.setSpacing(20)

        self.label = QLabel("Alege profilul Facebook:")
        self.label.setAlignment(Qt.AlignmentFlag.AlignLeft)

        self.combo = QComboBox()

        # Detectăm profilurile
        profiles = detect_chrome_profiles(CHROME_DIR)
        self.combo.addItems(profiles)

        self.button = QPushButton("Pornește cu acest profil")
        self.button.clicked.connect(self.start_with_profile)

        layout.addWidget(self.label)
        layout.addWidget(self.combo)
        layout.addWidget(self.button, alignment=Qt.AlignmentFlag.AlignCenter)

        self.setLayout(layout)

    def start_with_profile(self):
        profile = self.combo.currentText()
        print(f"[INFO] Pornesc cu profilul: {profile}")

        # îl trimitem către scriptul principal
        os.system(f'py share_fb.py "{profile}"')

        self.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = ProfileSelector()
    window.show()

    sys.exit(app.exec())
