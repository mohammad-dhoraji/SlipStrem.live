import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout,
    QScrollArea, QFrame, QSizePolicy, QGraphicsDropShadowEffect
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QColor, QFont
from config.settings import DRIVER_IMAGES_DIR, CURCUITS_IMAGES_DIR
from config.colors import TEAM_COLORS
from services.worker import Worker
from utils.api_helper import on_failed as show_api_error
from services.results import get_last_race_results
from ui.skeleton import RaceResultsSkeleton


class LatestRaceWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Latest Race Results")
        self.resize(950, 700)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)  
        self.setStyleSheet("background: transparent;") 
        self.race_data = {}
        self.initUI()
        self.load_race_results()

    def initUI(self):
        self.main_layout = QVBoxLayout()
        self.main_layout.setSpacing(25)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.setLayout(self.main_layout)
        self.show_skeletons()

    def show_skeletons(self):
        self.clear_layout(self.main_layout)
        for _ in range(3):
            self.main_layout.addWidget(RaceResultsSkeleton())

    def load_race_results(self):
        self.worker = Worker(get_last_race_results)
        self.worker.finished.connect(self.on_data_loaded)
        self.worker.failed.connect(self.on_failed)
        self.worker.start()

    def clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

    def on_data_loaded(self, race_data):
        self.race_data = race_data
        self.render_race_results()

    def on_failed(self, error_msg):
        show_api_error(self, self.retry_load)

    def retry_load(self):
        self.show_skeletons()
        self.load_race_results()

    def render_race_results(self):
        self.clear_layout(self.main_layout)
        race = self.race_data
        results = race.get("Results", [])

        # ----  Race Info ---- 
        race_card = QFrame()
        race_card.setStyleSheet("background-color: #1E1E1E; border-radius: 15px;")
        race_card_layout = QVBoxLayout()
        race_card_layout.setContentsMargins(15, 15, 15, 15)

        header = QLabel(
            f"{race['raceName']}<br>"
            f"{race['circuit']} - {race['country']}<br>"
            f"{race['date']}"
        )
        header.setTextFormat(Qt.TextFormat.RichText)
        header.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        header.setStyleSheet("color: #FFD700;")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        race_card_layout.addWidget(header)
        race_card.setLayout(race_card_layout)

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(30)
        shadow.setXOffset(0)
        shadow.setYOffset(5)
        shadow.setColor(QColor(0, 0, 0, 200))
        race_card.setGraphicsEffect(shadow)

        self.main_layout.addWidget(race_card)

        # ---- Scrollable container ---- 
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("border: none; background-color: #121212;")

        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.setSpacing(25)
        container_layout.setContentsMargins(20, 20, 20, 20)

        # ---- All Drivers (including Top 3) ---- 
        for driver in results:
            driver_widget = QFrame()
            driver_widget.setStyleSheet(
                f"background-color: #1E1E1E; border-radius: 12px; padding: 12px;"
            )
            driver_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

            driver_layout = QHBoxLayout(driver_widget)
            driver_layout.setContentsMargins(10, 0, 10, 0)

            color_strip = QFrame()
            color_strip.setFixedWidth(6)
            team_color = TEAM_COLORS.get(driver['Constructor']['name'], "#2A2F38")
            color_strip.setStyleSheet(f"background-color: {team_color}; border-radius: 3px;")
            driver_layout.addWidget(color_strip)

            driver_name = QLabel(f"{driver['position']}. {driver['Driver']['givenName']} {driver['Driver']['familyName']}")
            driver_name.setFont(QFont("Segoe UI", 12))
            driver_name.setStyleSheet("color: #FFFFFF; background: transparent;")

            points = QLabel(f"Points: {driver['points']}")
            points.setFont(QFont("Segoe UI", 12))
            points.setStyleSheet("color: #FFFFFF; background: transparent;")

            time_text = driver.get("Time", {}).get("time", driver.get("status", "—"))
            time = QLabel(f"Time: {time_text}")
            time.setFont(QFont("Segoe UI", 12))
            time.setStyleSheet("color: #FFFFFF; background: transparent;")

            driver_layout.addWidget(driver_name)
            driver_layout.addStretch()
            driver_layout.addWidget(points)
            driver_layout.addWidget(time)

            shadow = QGraphicsDropShadowEffect()
            shadow.setBlurRadius(15)
            shadow.setXOffset(0)
            shadow.setYOffset(3)
            shadow.setColor(QColor(0, 0, 0, 180))
            driver_widget.setGraphicsEffect(shadow)

            container_layout.addWidget(driver_widget)

        # ----  Circuit Image ---- 
        circuit_img_path = CURCUITS_IMAGES_DIR / f"{self.race_data['circuitId']}.png"
        if circuit_img_path.exists():
            pixmap = QPixmap(str(circuit_img_path))
        else:
            pixmap = QPixmap(600, 300)
            pixmap.fill(QColor("#2A2F38"))

        pixmap = pixmap.scaled(900, 600, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        circuit_label = QLabel()
        circuit_label.setPixmap(pixmap)
        circuit_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        circuit_label.setStyleSheet("border-radius: 15px;")
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setXOffset(0)
        shadow.setYOffset(5)
        shadow.setColor(QColor(0, 0, 0, 180))
        circuit_label.setGraphicsEffect(shadow)

        container_layout.addWidget(circuit_label, alignment=Qt.AlignmentFlag.AlignCenter)
        container.setStyleSheet("background: transparent;")

        scroll_area.setWidget(container)
        self.main_layout.addWidget(scroll_area)
        scroll_area.setStyleSheet("border: none; background: transparent;") 


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LatestRaceWindow()
    window.show()
    sys.exit(app.exec())
