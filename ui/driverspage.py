import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout,
    QScrollArea, QGridLayout, QGraphicsDropShadowEffect, QPushButton
)
from PyQt6.QtCore import Qt, QPropertyAnimation, pyqtSignal
from PyQt6.QtGui import QPixmap, QColor, QFont
from collections import defaultdict
from config.settings import DRIVER_IMAGES_DIR
from services.worker import Worker
from utils.api_helper import on_failed as show_api_error
from services.d_standings import get_driver_standings
from config.colors import TEAM_COLORS
from ui.skeleton import DriverSkeleton
from ui.d_details import DriverDetails


class DriverCard(QWidget):
    driverClicked = pyqtSignal(str)

    def __init__(self, driver: dict):
        super().__init__()
        self.driver = driver
        self.initUI()
        self.setGraphicsEffect(None)

    def initUI(self):
        # --- Driver info
        name = self.driver.get("driverName", "Unknown")
        number = self.driver.get("permanentNumber", "N/A")
        team = self.driver.get("constructorName", "Unknown Team")
        nationality = self.driver.get("nationality", "Unknown")
        wins = self.driver.get("wins", "0")

        # --- Team color
        team_color = TEAM_COLORS.get(team, "#2A2F38")
        color = QColor(team_color)
        brightness = (color.red() * 0.299 + color.green() * 0.587 + color.blue() * 0.114)
        text_color =  "#000000"

        # --- Driver image
        driver_image_path = DRIVER_IMAGES_DIR / f"{self.driver['driverId']}.png"
        pixmap = QPixmap(str(driver_image_path))
        if pixmap.isNull():
            pixmap = QPixmap(500, 500)
            pixmap.fill(Qt.GlobalColor.lightGray)
        else:
            crop_height = pixmap.height() // 2
            pixmap = pixmap.copy(0, 0, pixmap.width(), crop_height)
        pixmap = pixmap.scaledToWidth(110, Qt.TransformationMode.SmoothTransformation)

        driverImg = QLabel()
        driverImg.setPixmap(pixmap)
        driverImg.setAlignment(Qt.AlignmentFlag.AlignCenter)
        driverImg.setStyleSheet(f"border-radius: 8px; border: 2px solid {text_color};")

        # --- Image container
        img_container = QWidget()
        img_layout = QVBoxLayout()
        img_layout.setContentsMargins(5, 5, 5, 5)
        img_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        img_container.setLayout(img_layout)
        img_container.setStyleSheet(f"background-color: {team_color}; border-radius: 12px;")
        img_layout.addWidget(driverImg)

        # --- Labels
        name_label = QLabel(f"#{number} {name}")
        team_label = QLabel(team)
        win_label = QLabel(f"Wins: {wins}")

        # ---- Fonts
        name_label.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        team_label.setFont(QFont("Segoe UI", 16, QFont.Weight.Medium))
        win_label.setFont(QFont("Segoe UI", 16))

        # ---- Colors
        name_label.setStyleSheet(f"color: {text_color};")
        team_label.setStyleSheet(f"color: {text_color};")
        if int(wins) > 0:
            win_label.setStyleSheet("color: #4a2c0a; font-weight: bold;")
        else:
            win_label.setStyleSheet(f"color: {text_color}; font-style: italic;")

        # --- Info layout
        info_layout = QVBoxLayout()
        info_layout.setSpacing(4)
        info_layout.setContentsMargins(12, 12, 12, 12)
        for lbl in [name_label, team_label, win_label]:
            lbl.setAlignment(Qt.AlignmentFlag.AlignLeft)
            info_layout.addWidget(lbl)

        # --- "More Info" button
        details_btn = QPushButton("More Info")
        details_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        details_btn.setFlat(True)
        details_btn.setStyleSheet("""
            QPushButton {
                color: #000;
                font-weight: bold;
                text-align: left;
                border: none;
                padding: 4px 8px;
                border-radius: 6px;
                background-color: rgba(255, 255, 255, 0);
            }
            QPushButton:hover {
                background-color: rgba(255, 217, 0, 0.2);
            }
            QPushButton:pressed {
                background-color: rgba(255, 217, 0, 0.4);
            }
        """)
        details_btn.clicked.connect(self.on_details_clicked)
        info_layout.addWidget(details_btn)


        info_container = QWidget()
        info_container.setLayout(info_layout)

        # --- Main layout
        inner_hbox = QHBoxLayout()
        inner_hbox.setSpacing(15)
        inner_hbox.setContentsMargins(12, 12, 12, 12)
        inner_hbox.addWidget(info_container, stretch=1)
        inner_hbox.addWidget(img_container, stretch=0)

        card_container = QWidget()
        card_container.setLayout(inner_hbox)
        card_container.setStyleSheet(f"""
            background-color: {team_color};
            border-radius: 12px;
        """)

        hbox = QHBoxLayout()
        hbox.addWidget(card_container)
        self.setLayout(hbox)
        self.setMaximumWidth(400)
        self.setMinimumHeight(pixmap.height() + 100)
        name_label.setWordWrap(True)

        # --- Shadow effect
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(35)
        shadow.setXOffset(5)
        shadow.setYOffset(10)
        shadow.setColor(QColor(0, 0, 0, 180))
        self.setGraphicsEffect(shadow)

    def on_details_clicked(self):
        driver_id = self.driver.get("driverId")
        self.driverClicked.emit(driver_id)


class DriversWindow(QWidget):
    driverClickedGlobal = pyqtSignal(str)
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Drivers")
        self.drivers = []
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)


        self.setStyleSheet("""
            
            QWidget {
                background-color: transparent;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QScrollArea {
                border: none;
            }
            QScrollBar:vertical {
                width: 8px;
                background: #2A2F38;
                margin: 0px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background: #555;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical:hover {
                background: #888;
            }
        """)
        self.initUI()

    def initUI(self):
        self.mainVbox = QVBoxLayout()
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.container = QWidget()
        self.gbox = QGridLayout()
        self.gbox.setSpacing(12)
        self.container.setLayout(self.gbox)
        self.scroll.setWidget(self.container)
        self.mainVbox.addWidget(self.scroll)
        self.setLayout(self.mainVbox)

        self.show_skeletons()
        self.load_drivers()

    def show_skeletons(self):
        self.clear_layout(self.gbox)
        for i in range(6):
            card = DriverSkeleton()
            row, col = divmod(i, 2)
            self.gbox.addWidget(card, row, col)

    def load_drivers(self):
        self.worker = Worker(get_driver_standings)
        self.worker.finished.connect(self.on_data_loaded)
        self.worker.failed.connect(self.on_failed)
        self.worker.start()

    def clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

    def on_data_loaded(self, drivers):
        
        self.clear_layout(self.gbox)
        self.drivers = drivers
        
        teams = defaultdict(list)
        for d in drivers:
            team_name = d.get("constructorName", "unknown")
            teams[team_name].append(d)

        sorted_drivers = []
        for team, members in teams.items():
            sorted_drivers.extend(members)

        for i, driver in enumerate(sorted_drivers):
            card = DriverCard(driver)
            card.driverClicked.connect(self.open_driver_detail_page)
            row, col = divmod(i, 2)
            self.gbox.addWidget(card, row, col)

            anim = QPropertyAnimation(card, b"windowOpacity")
            anim.setDuration(400)
            anim.setStartValue(0)
            anim.setEndValue(1)
            anim.start()
            

    def on_failed(self, error_msg):
        show_api_error(self.container, self.retry_load)

    def retry_load(self):
        self.show_skeletons()
        self.load_drivers()

    def open_driver_detail_page(self, driver_id):
        self.driverClickedGlobal.emit(driver_id)    


    def on_driver_selected_from_details(self, driver_id: str):
        pass

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DriversWindow()
    window.resize(800, 600)
    window.show()
    sys.exit(app.exec())
