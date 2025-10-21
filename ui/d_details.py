import sys
import os
from pathlib import Path
import json
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout,
    QScrollArea, QGraphicsDropShadowEffect, QPushButton, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPixmap, QColor
from config.colors import TEAM_COLORS
from config.settings import DRIVER_IMAGES_DIR, FLAGS_IMAGES_DIR,CONSTRUCTOR_IMAGES_DIR

class DriverDetails(QWidget):

    driverSelected = pyqtSignal(str)

    def __init__(self, driver: dict, constructor: dict = None):
        super().__init__()
        self.driver = driver
        self.constructor = constructor
        self.initUI()

    def create_card(self, widgets: list, width=450, base_color="#2a2a3f"):
        """Card with background color and black text"""
        card = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(12)
        for w in widgets:
            layout.addWidget(w)
        card.setLayout(layout)
        card.setFixedWidth(width)
        card.setStyleSheet(f"""
            QWidget {{
                background-color: {base_color};
                border-radius: 16px;
                padding: 16px;
            }}
        """)
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(25)
        shadow.setOffset(0, 0)
        shadow.setColor(QColor(0, 0, 0, 100))
        card.setGraphicsEffect(shadow)
        return card

    def create_label(self, text, bold=False, font_size=16):
        label = QLabel(text)
        label.setWordWrap(True)
        style = f"color: black; font-size: {font_size}px;"
        if bold:
            style += " font-weight: bold;"
        label.setStyleSheet(style)
        return label

    def initUI(self):
        team_color = "#1e1e2f"  # default dark
        if self.constructor and self.constructor.get("name") in TEAM_COLORS:
            team_color = TEAM_COLORS[self.constructor["name"]]

        # --- Scrollable container ---
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea {border: none;}")

        container = QWidget()
        container_layout = QVBoxLayout()
        container_layout.setSpacing(30)

        # --- Top Horizontal Layout ---
        top_layout = QHBoxLayout()
        top_layout.setSpacing(30)

        # ---- LEFT PANEL: Info Cards ----
        info_layout = QVBoxLayout()
        info_layout.setSpacing(20)

        # ---- Driver Info Card ---- 
        name_label = self.create_label(self.driver.get('driverName', 'Unknown'), bold=True, font_size=24)
        flag_image_path = FLAGS_IMAGES_DIR / f"{self.driver['nationality']}.png"
        flag_pixmap = QPixmap(str(flag_image_path))
        if flag_pixmap.isNull():
            flag_pixmap = QPixmap(100, 100)
            flag_pixmap.fill(Qt.GlobalColor.lightGray)
        flag_pixmap = flag_pixmap.scaled(100, 100, Qt.AspectRatioMode.KeepAspectRatio,
                                        Qt.TransformationMode.SmoothTransformation)
        flag_label = QLabel()   
        flag_label.setPixmap(flag_pixmap)
        nationality_label = self.create_label(self.driver.get('nationality', 'Unknown'), bold=True, font_size=16)

        nat_layout = QHBoxLayout()
        nat_layout.addWidget(flag_label)
        nat_layout.addSpacing(12)
        nat_layout.addWidget(nationality_label)
        nat_widget = QWidget()
        nat_widget.setLayout(nat_layout)

        number_label = self.create_label(f"Number: {self.driver.get('permanentNumber', 'N/A')}", font_size=16)
        dob_label = self.create_label(f"DOB: {self.driver.get('dateOfBirth', 'N/A')}", font_size=16)
        code_label = self.create_label(f"Code: {self.driver.get('code', 'N/A')}", font_size=16)

        driver_card = self.create_card([name_label, nat_widget, number_label, dob_label, code_label],
                                       base_color=team_color)
        info_layout.addWidget(driver_card)

        # ---- Constructor Card ---- 
        if self.constructor:
            # Team Logo
            logo_path = CONSTRUCTOR_IMAGES_DIR / f"{self.constructor['constructorId']}.png"
            logo_pixmap = QPixmap(str(logo_path))
            if logo_pixmap.isNull():
                logo_pixmap = QPixmap(100, 100)
                logo_pixmap.fill(Qt.GlobalColor.lightGray)
            logo_pixmap = logo_pixmap.scaled(100, 100, Qt.AspectRatioMode.KeepAspectRatio,
                                            Qt.TransformationMode.SmoothTransformation)
            logo_label = QLabel()
            logo_label.setPixmap(logo_pixmap)

            # Team Name + Nationality
            constructor_name = self.create_label(
                f"Team: {self.constructor.get('name', 'N/A')}", bold=True, font_size=18
            )
            constructor_nat = self.create_label(
                f"Nationality: {self.constructor.get('nationality', 'N/A')}", font_size=16
            )

            # Layout with logo + text
            team_layout = QHBoxLayout()
            team_layout.addWidget(logo_label)
            team_layout.addSpacing(12)

            text_widget = QWidget()
            text_layout = QVBoxLayout()
            text_layout.setContentsMargins(0, 0, 0, 0)
            text_layout.addWidget(constructor_name)
            text_layout.addWidget(constructor_nat)
            text_widget.setLayout(text_layout)

            team_layout.addWidget(text_widget)
            team_widget = QWidget()
            team_widget.setLayout(team_layout)

            constructor_card = self.create_card([team_widget], base_color=team_color)
            info_layout.addWidget(constructor_card)

        # ---------------- Load driver stats from AppData ----------------
        appdata_dir = Path(os.getenv('APPDATA')) / "F1App"
        stats_file = appdata_dir / "drivers_stats.json"

        if stats_file.exists():
            with stats_file.open("r", encoding="utf-8") as f:
                all_drivers_stats = json.load(f)
        else:
            all_drivers_stats = []
        driver_id = self.driver.get('driverId') if self.driver else None
        if driver_id:
            json_driver = next((d for d in all_drivers_stats if d["driverId"] == driver_id), None)
            if json_driver:
                self.driver.update(json_driver)

        # ------------------- Stats Card -------------------
    

# ------------------- Stats Card -------------------
        stats_widgets = []

        def add_stat_widget(text):
            
            label = self.create_label(text, font_size=16)
            stats_widgets.append(label)

            line = QFrame()
            line.setFrameShape(QFrame.Shape.HLine)
            line.setFrameShadow(QFrame.Shadow.Sunken)
            line.setStyleSheet("background-color: #EAEAEA; max-height: 1px;")  
            stats_widgets.append(line)

        add_stat_widget(f"Total Points: {self.driver.get('totalPoints', 0)}")
        add_stat_widget(f"Total Poles: {self.driver.get('totalPoles', 0)}")
        add_stat_widget(f"Total Wins: {self.driver.get('totalWins', 0)}")
        add_stat_widget(f"Total Podiums: {self.driver.get('totalPodiums', 0)}")
        add_stat_widget(f"Seasons Raced: {self.driver.get('seasonsRaced', 0)}")
        if isinstance(stats_widgets[-1], QFrame):
            stats_widgets.pop()

        stats_card = self.create_card(stats_widgets, base_color=team_color)
        info_layout.addWidget(stats_card)


        # ----  Back Button ---- 
        back_btn = QPushButton("← Back")
        back_btn.setFixedWidth(120)
        back_btn.setStyleSheet(f"""
            QPushButton {{
                color: black;
                background-color: {team_color};
                border-radius: 8px;
                padding: 8px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {team_color};
                opacity: 0.85;
            }}
        """)
        back_btn.clicked.connect(lambda: self.driverSelected.emit("back"))
        info_layout.addWidget(back_btn, alignment=Qt.AlignmentFlag.AlignLeft)
        info_layout.addStretch()

        top_layout.addLayout(info_layout, 2)

        # ---- RIGHT PANEL: Driver Image ----
        image_label = QLabel()
        driver_image_path = DRIVER_IMAGES_DIR / f"{self.driver['driverId']}.png"
        pixmap = QPixmap(str(driver_image_path))
        if pixmap.isNull():
            pixmap = QPixmap(800, 1000)
            pixmap.fill(Qt.GlobalColor.lightGray)
        pixmap = pixmap.scaled(
            650, 900, Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        
        image_label.setPixmap(pixmap)
        image_label.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        top_layout.addWidget(image_label, alignment=Qt.AlignmentFlag.AlignCenter, stretch=3)

        container_layout.addLayout(top_layout)
        container.setLayout(container_layout)
        scroll.setWidget(container)

        # ---- Main layout ---- 
        main_layout = QVBoxLayout()
        main_layout.addWidget(scroll)
        self.setLayout(main_layout)
        
        self.setStyleSheet(f"""
            QWidget {{
                background: transparent;
            }}
        """)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DriverDetails()
    window.resize(1200, 800)
    window.show()
    sys.exit(app.exec())
