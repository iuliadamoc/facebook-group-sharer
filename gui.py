import sys
import os
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QComboBox, QLineEdit
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
        self.setFixedSize(420, 280)

        self.setStyleSheet("""
            QWidget { background-color: #f7f9fc; font-family: 'Segoe UI'; }
            QLabel { font-size: 15px; color: #2a2a2a; font-weight: bold; }
            QLineEdit {
                font-size: 16px;
                padding: 8px;
                border-radius: 8px;
                border: 1px solid #aab7c4;
                background-color: white;
                min-height: 20px;
            }

            QComboBox {
                font-size: 14px;
                padding: 6px;
                border-radius: 6px;
                border: 1px solid #aab7c4;
                background-color: white;
            }
            QPushButton {
                background-color: #4a90e2;
                color: white;
                font-size: 16px;
                border-radius: 8px;
                padding: 12px 20px;
                min-width: 220px;
                min-height: 14px;
            }

            QPushButton:hover { background-color: #357abd; }
            QPushButton:pressed { background-color: #2d63a3; }
        """)

        layout = QVBoxLayout()
        layout.setContentsMargins(30, 25, 30, 25)
        layout.setSpacing(20)

        # Selectare profil
        self.label = QLabel("Alege profilul Facebook:")
        self.combo = QComboBox()

        profiles = detect_chrome_profiles(CHROME_DIR)
        self.combo.addItems(profiles)

        # Mesaj pentru postare
        self.msg_label = QLabel("Mesaj pentru postare:")
        self.message_box = QLineEdit()
        self.message_box.setPlaceholderText("Scrie mesajul pentru postare...")

        # Buton start
        self.button = QPushButton("Pornește cu acest profil")
        self.button.clicked.connect(self.start_with_profile)

        layout.addWidget(self.label)
        layout.addWidget(self.combo)

        layout.addWidget(self.msg_label)
        # self.message_box.setMinimumWidth(260)
        layout.addWidget(self.message_box)

        layout.addWidget(self.button, alignment=Qt.AlignmentFlag.AlignCenter)

        self.setLayout(layout)

    def start_with_profile(self):
        profile = self.combo.currentText()
        message = self.message_box.text().replace('"', "'")

        print(f"[INFO] Profil selectat: {profile}")
        print(f"[INFO] Mesaj introdus: {message}")

        os.system(f'py share_fb.py "{profile}" "{message}"')

        self.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ProfileSelector()
    window.show()
    sys.exit(app.exec())
