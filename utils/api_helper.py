import requests
from PyQt6.QtWidgets import QWidget, QLabel, QPushButton, QVBoxLayout
from PyQt6.QtCore import Qt

BASE_URL = "https://api.jolpi.ca/ergast/f1"

def fetch_api(endpoint: str):
    try:
        url = f"{BASE_URL}/{endpoint}.json"
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        raise Exception(f"Error fetching {endpoint}: {e}")


def on_failed(widget: QWidget, retry_callback, message=None):
    """Display a centered error message with a styled Retry button."""
    
    if widget.layout() is None:
        layout = QVBoxLayout()
        widget.setLayout(layout)
    else:
        layout = widget.layout()
        for i in reversed(range(layout.count())):
            item = layout.takeAt(i)
            w = item.widget()
            if w:
                w.deleteLater()

        if not isinstance(layout, QVBoxLayout):
            new_layout = QVBoxLayout()
            new_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            new_layout.setSpacing(20)
            widget.setLayout(new_layout)
            layout = new_layout

    layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
    layout.setSpacing(20)

    # --- Error message ---
    friendly_msg = message or "⚠️ Failed to load data. Please check your internet or try again."
    error_label = QLabel(friendly_msg)
    error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    error_label.setWordWrap(True)
    error_label.setStyleSheet("""
        color: #FF4C4C;
        font-size: 18px;
        font-weight: bold;
    """)

    # --- Retry button ---
    retry_button = QPushButton("Retry")
    retry_button.setFixedWidth(150)
    retry_button.setStyleSheet("""
        QPushButton {
            background-color: #FFD700;
            color: #1E1E2F;
            font-weight: bold;
            font-size: 16px;
            padding: 10px 20px;
            border-radius: 12px;
        }
        QPushButton:hover { background-color: #FFC107; }
        QPushButton:pressed { background-color: #E6B800; }
    """)
    retry_button.clicked.connect(retry_callback)
    # print(message)

    # --- Add widgets ---
    layout.addStretch(1)
    layout.addWidget(error_label, alignment=Qt.AlignmentFlag.AlignCenter)
    layout.addWidget(retry_button, alignment=Qt.AlignmentFlag.AlignCenter)
    layout.addStretch(1)
