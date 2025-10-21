import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QFrame,
    QScrollArea, QGraphicsDropShadowEffect
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QColor, QFont
from services.d_standings import get_driver_standings
from services.worker import Worker
from ui.skeleton import WDCSkeleton
from utils.api_helper import on_failed as show_api_error
from config.settings import DRIVER_IMAGES_DIR


PODIUM_COLORS = {
    1: "#C9A34E",  
    2: "#B5B5B5", 
    3: "#B5B5B5"  
}


class PodiumDriverCard(QWidget):
    def __init__(self, driver: dict, position: int):
        super().__init__()
        self.driver = driver
        self.position = position
        self.initUI()

    def initUI(self):
        self.setFixedSize(220, 330)

        main_vbox = QVBoxLayout()
        main_vbox.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_vbox.setContentsMargins(0, 0, 0, 0)
        main_vbox.setSpacing(6)

        bg_color = PODIUM_COLORS.get(self.position, "#1E1E1E")
        self.setStyleSheet(f"""
            background-color: {bg_color};
            border-radius: 18px;
        """)

        # ----  Position number
        pos_label = QLabel(str(self.position))
        pos_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        pos_label.setStyleSheet("""
            font-size: 52px;
            font-weight: 900;
            color: white;
        """)

        # --- Driver image 
        img_label = QLabel()
        driver_image_path = DRIVER_IMAGES_DIR / f"{self.driver['driverId']}.png"
        pixmap = QPixmap(str(driver_image_path))

        if pixmap.isNull():
            pixmap = QPixmap(200, 200)
            pixmap.fill(Qt.GlobalColor.lightGray)
        else:
            crop_height = pixmap.height() // 2
            pixmap = pixmap.copy(0, 0, pixmap.width(), crop_height)

        pixmap = pixmap.scaledToWidth(110, Qt.TransformationMode.SmoothTransformation)

        img_label.setPixmap(pixmap)
        img_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        img_label.setStyleSheet("border-radius: 8px; border: 2px solid #555;")


        # ---- Driver name
        name_label = QLabel(self.driver.get("driverName", "Unknown"))
        name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        name_label.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            color: white;
        """)

        # ---- Team + points
        points_label = QLabel(f"{self.driver.get('points', '0')} PTS")
        points_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        points_label.setStyleSheet("""
            background-color: rgba(0,0,0,0.4);
            color: white;
            font-weight: 600;
            border-radius: 10px;
            padding: 6px 12px;
        """)

        team_label = QLabel(self.driver.get("constructorName", ""))
        team_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        team_label.setStyleSheet("""
            color: white;
            font-size: 14px;
        """)

        main_vbox.addWidget(pos_label)
        main_vbox.addWidget(img_label)
        main_vbox.addWidget(name_label)
        main_vbox.addWidget(team_label)
        main_vbox.addWidget(points_label)

        self.setLayout(main_vbox)

        # ---- Drop shadow
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(40)
        shadow.setOffset(0, 6)
        shadow.setColor(QColor(0, 0, 0, 180))
        self.setGraphicsEffect(shadow)


class WdcWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("F1 Race Results")
        self.setStyleSheet("""
            QWidget {
                background-color: qlineargradient(
                    spread:pad, x1:0, y1:0, x2:1, y2:1,
                    stop:0 #0D0D0D, stop:1 #1A1A1A
                );
                font-family: 'Segoe UI', Arial;
            }
            QScrollArea {
                border: none;
            }
        """)
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)

        self.podium_container = QHBoxLayout()
        self.podium_container.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.podium_container.setSpacing(30)
        layout.addLayout(self.podium_container)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        container = QWidget()
        self.list_layout = QVBoxLayout(container)
        self.list_layout.setSpacing(10)
        self.scroll.setWidget(container)    
        layout.addWidget(self.scroll)

        self.setLayout(layout)
        self.load_drivers()

    def load_drivers(self):
        self.worker = Worker(get_driver_standings)
        self.worker.finished.connect(self.on_data_loaded)
        self.worker.failed.connect(self.on_failed)
        self.worker.start()

    def on_data_loaded(self, drivers):
        if not drivers:
            return

        for i in reversed(range(self.podium_container.count())):
            item = self.podium_container.takeAt(i)
            if item.widget():
                item.widget().deleteLater()

        # Podium layout
        podium_order = [drivers[1], drivers[0], drivers[2]]
        offsets = [40, 0, 40]
        for i, d in enumerate(podium_order):
            card = PodiumDriverCard(d, position=int(d["position"]))
            vbox = QVBoxLayout()
            vbox.setAlignment(Qt.AlignmentFlag.AlignHCenter)
            vbox.addSpacing(offsets[i])
            vbox.addWidget(card)
            self.podium_container.addLayout(vbox)

        
        for i in reversed(range(self.list_layout.count())):
            item = self.list_layout.takeAt(i)
            if item.widget():
                item.widget().deleteLater()

        for d in drivers[3:]:
            card = QFrame()
            card.setStyleSheet("""
                background-color: #141414;
                border-radius: 12px;
            """)
            hbox = QHBoxLayout(card)
            hbox.setContentsMargins(15, 10, 15, 10)
            hbox.setSpacing(20)

            pos = QLabel(d["positionText"])
            pos.setStyleSheet("color: #F44336; font-weight: bold; font-size: 16px;")

            name = QLabel(d["driverName"])
            name.setStyleSheet("color: white; font-weight: bold;")

            team = QLabel(d.get("constructorName", ""))
            team.setStyleSheet("color: #BBBBBB;")

            points = QLabel(f"{d['points']} PTS")
            points.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            points.setStyleSheet("color: #EAEAEA; font-weight: bold;")

            hbox.addWidget(pos)
            hbox.addWidget(name)
            hbox.addWidget(team)
            hbox.addStretch()
            hbox.addWidget(points)

            shadow = QGraphicsDropShadowEffect(card)
            shadow.setBlurRadius(25)
            shadow.setColor(QColor(0, 0, 0, 160))
            shadow.setYOffset(4)
            card.setGraphicsEffect(shadow)

            self.list_layout.addWidget(card)

    def on_failed(self, error_msg):
        show_api_error(self, self.load_drivers)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = WdcWindow()
    window.resize(1000, 720)
    window.show()
    sys.exit(app.exec())
