import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QPushButton, QLabel,
    QVBoxLayout, QHBoxLayout, QStackedWidget, QFrame
)
from PyQt6.QtCore import Qt


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Sidebar Navigation Example")
        self.setGeometry(200, 200, 800, 500)

        # --- Central Layout ---
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        # --- Sidebar (Initially hidden) ---
        self.sidebar = QFrame()
        self.sidebar.setFixedWidth(200)
        self.sidebar.setStyleSheet("background-color: #2e2e3e; color: white;")

        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(10, 10, 10, 10)

        btn_home = QPushButton("🏠 Home")
        btn_form = QPushButton("📝 Form")
        btn_notes = QPushButton("📒 Notes")

        for btn in (btn_home, btn_form, btn_notes):
            btn.setStyleSheet("""
                QPushButton {
                    background: #3a3a4d;
                    color: white;
                    padding: 10px;
                    border-radius: 6px;
                }
                QPushButton:hover {
                    background: #5a5aff;
                }
            """)
            sidebar_layout.addWidget(btn)

        sidebar_layout.addStretch()

        # --- Stacked Widget (Pages) ---
        self.stack = QStackedWidget()
        self.stack.addWidget(self.create_page("Home Page"))
        self.stack.addWidget(self.create_page("Form Page"))
        self.stack.addWidget(self.create_page("Notes Page"))

        # --- Connections ---
        btn_home.clicked.connect(lambda: self.stack.setCurrentIndex(0))
        btn_form.clicked.connect(lambda: self.stack.setCurrentIndex(1))
        btn_notes.clicked.connect(lambda: self.stack.setCurrentIndex(2))

        # --- Hamburger button (top-left) ---
        self.hamburger = QPushButton("☰")
        self.hamburger.setFixedSize(40, 40)
        self.hamburger.setStyleSheet("""
            QPushButton {
                background: #5a5aff;
                color: white;
                font-size: 18px;
                border-radius: 6px;
            }
            QPushButton:hover {
                background: #7878ff;
            }
        """)
        self.hamburger.clicked.connect(self.toggle_sidebar)

        # Top bar with hamburger
        top_bar = QHBoxLayout()
        top_bar.addWidget(self.hamburger, alignment=Qt.AlignmentFlag.AlignLeft)
        top_bar.addStretch()

        content_layout = QVBoxLayout()
        content_layout.addLayout(top_bar)
        content_layout.addWidget(self.stack)

        # --- Add sidebar + content to main layout ---
        main_layout.addWidget(self.sidebar)
        main_layout.addLayout(content_layout)

        # Sidebar starts hidden
        self.sidebar.setVisible(False)

        # Dark mode
        self.setStyleSheet("QMainWindow { background-color: #1e1e2f; } QLabel { color: white; font-size: 16px; }")

    def toggle_sidebar(self):
        self.sidebar.setVisible(not self.sidebar.isVisible())

    def create_page(self, text):
        page = QWidget()
        layout = QVBoxLayout(page)
        label = QLabel(text)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)
        return page


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
