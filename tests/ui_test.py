import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QTabWidget, QWidget,
    QVBoxLayout, QLabel, QPushButton, QLineEdit, QTextEdit
)
from PyQt6.QtCore import Qt


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("PyQt6 QTabWidget Example")
        self.setGeometry(200, 200, 600, 400)

        # Main Tab Widget
        self.tabs = QTabWidget()
        self.tabs.setTabPosition(QTabWidget.TabPosition.North)
        self.tabs.setMovable(True)  # allow dragging tabs around
        self.tabs.setDocumentMode(True)  # cleaner look

        # Add Tabs
        self.tabs.addTab(self.create_home_tab(), "🏠 Home")
        self.tabs.addTab(self.create_form_tab(), "📝 Form")
        self.tabs.addTab(self.create_notes_tab(), "📒 Notes")

        # Set QTabWidget as central widget
        self.setCentralWidget(self.tabs)

        # Apply some styling (QSS)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1e1e2f;
            }
            QTabWidget::pane {
                border: 2px solid #444;
                background: #2e2e3e;
                border-radius: 8px;
            }
            QTabBar::tab {
                background: #3a3a4d;
                color: white;
                padding: 8px 16px;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
            }
            QTabBar::tab:selected {
                background: #5a5aff;
                font-weight: bold;
            }
            QLabel {
                color: white;
                font-size: 14px;
            }
            QPushButton {
                background-color: #5a5aff;
                color: white;
                padding: 6px 12px;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #7878ff;
            }
            QLineEdit, QTextEdit {
                background: #2e2e3e;
                color: white;
                border: 1px solid #555;
                border-radius: 6px;
                padding: 4px;
            }
        """)

    def create_home_tab(self):
        """Tab 1: Just a welcome screen with a button"""
        widget = QWidget()
        layout = QVBoxLayout()

        label = QLabel("Welcome to the Home Tab!")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        button = QPushButton("Click Me")
        layout.addWidget(label)
        layout.addWidget(button, alignment=Qt.AlignmentFlag.AlignCenter)

        widget.setLayout(layout)
        return widget

    def create_form_tab(self):
        """Tab 2: A simple form with input fields"""
        widget = QWidget()
        layout = QVBoxLayout()

        layout.addWidget(QLabel("Enter your name:"))
        name_input = QLineEdit()
        layout.addWidget(name_input)

        layout.addWidget(QLabel("Enter your email:"))
        email_input = QLineEdit()
        layout.addWidget(email_input)

        submit_btn = QPushButton("Submit")
        layout.addWidget(submit_btn, alignment=Qt.AlignmentFlag.AlignRight)

        widget.setLayout(layout)
        return widget

    def create_notes_tab(self):
        """Tab 3: Notes area with text editor"""
        widget = QWidget()
        layout = QVBoxLayout()

        layout.addWidget(QLabel("Write your notes below:"))
        text_area = QTextEdit()
        layout.addWidget(text_area)

        save_btn = QPushButton("Save Notes")
        layout.addWidget(save_btn, alignment=Qt.AlignmentFlag.AlignRight)

        widget.setLayout(layout)
        return widget


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
