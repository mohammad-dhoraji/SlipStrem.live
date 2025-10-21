# -- ui/constructors.py

import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QFrame, QScrollArea, QGraphicsDropShadowEffect
)
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QPixmap, QColor
from services.c_standings import get_constructors_standings
from services.worker import Worker
from ui.skeleton import WDCSkeleton
from utils.api_helper import on_failed as show_api_error
from config.settings import CONSTRUCTOR_IMAGES_DIR
from config import colors

PODIUM_COLORS = ["#FFFFFFF5", "#FFFFFFF5", "#FFFFFFF5"] 

class PodiumTeams(QWidget):
    
    def __init__(self, teams: dict, size=(290, 170)):
        
        super().__init__()
        self.teams = teams
        self.size = size
        self.setFixedSize(self.size[0], self.size[1]+100)
        self.initUI()
        
    def initUI(self):
        
        vbox = QVBoxLayout()
        vbox.setAlignment(Qt.AlignmentFlag.AlignCenter)
        vbox.setSpacing(5)
        
        # --- Team Logo
        
        constructor_image_path = CONSTRUCTOR_IMAGES_DIR / f"{self.teams['constructorId']}.png"
        pixmap = QPixmap(str(constructor_image_path))
        
        if pixmap.isNull():
            pixmap = QPixmap(self.size[0], self.size[1])
            pixmap.fill(Qt.GlobalColor.lightGray)
        else:
            pixmap = pixmap.scaled(self.size[0], self.size[1], 
                       Qt.AspectRatioMode.KeepAspectRatio,
                       Qt.TransformationMode.SmoothTransformation)

        TeamLabel = QLabel()
        TeamLabel.setPixmap(pixmap)
        TeamLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        TeamLabel.setStyleSheet("border-radius: 12px;")
        TeamLabel.setFixedSize(self.size[0], self.size[1]) 
        vbox.addWidget(TeamLabel)

        
        # ---- Name + Points
        constructor_name = self.teams.get("constructorName", "Unknown")
        team_color = colors.TEAM_COLORS.get(constructor_name, "#EAEAEA")  
        name_label = QLabel(constructor_name)
        name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        name_label.setWordWrap(True)
        name_label.setStyleSheet(f"font-weight: bold; font-size: 18px; color: {team_color};")
        
        points_label = QLabel(f"{self.teams.get('points', '0')} pts")
        points_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        points_label.setStyleSheet("""
            font-size: 14px;
            color: #EAEAEA;
            background-color: #2A2A2A;
            border-radius: 8px;
            padding: 4px 8px;
        """)

        
        win_label = QLabel(f"{self.teams.get('wins', '0')} wins")
        win_label.setStyleSheet("font-size: 14px; color: #EAEAEA;")
        win_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        win_label.setStyleSheet("""
            font-size: 14px;
            color: #EAEAEA;
            background-color: #2A2A2A;
            border-radius: 8px;
            padding: 4px 8px;
        """)
        
        vbox.addWidget(name_label)
        vbox.addWidget(points_label)
        vbox.addWidget(win_label)

        self.setLayout(vbox)
        self.setMaximumWidth(self.size[0] + 40)
        self.setMinimumHeight(self.size[1] + 90)

        # --- Shadow effect
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(25)
        shadow.setXOffset(0)
        shadow.setYOffset(5)
        shadow.setColor(QColor(0,0,0,160))
        self.setGraphicsEffect(shadow)

        idx = int(self.teams.get("position", 4)) - 1
        if idx < 3:
            self.setStyleSheet(f"background-color: {PODIUM_COLORS[idx]}; border-radius: 12px;")
        else:
            self.setStyleSheet("background-color: #1E1E1E; border-radius: 12px;")
            
            
class WccWindow(QWidget):
    
    def __init__(self):
        
        super().__init__()
        self.setWindowTitle("World Constructors' Championship")
        self.setStyleSheet("""
            QWidget { background-color: transparent;; font-family: 'Segoe UI', Arial, sans-serif; }
            QScrollArea { border: none; }
            QScrollBar:vertical { width: 8px; background: #2A2F38; margin: 0px; border-radius: 4px; }
            QScrollBar::handle:vertical { background: #555; border-radius: 4px; }
            QScrollBar::handle:vertical:hover { background: #888; }
        """)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.initUI()
        
    def initUI(self):
        
        self.MainVbox = QVBoxLayout()
        self.setLayout(self.MainVbox)
        
        # --- Podium placeholder container
        self.podium_container = QVBoxLayout()
        self.MainVbox.addLayout(self.podium_container)

        # --- Scroll area for driver list
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.container = QWidget()
        self.list_vbox = QVBoxLayout()
        self.list_vbox.setSpacing(10)
        self.container.setLayout(self.list_vbox)
        self.scroll.setWidget(self.container)
        self.MainVbox.addWidget(self.scroll)
        self.skeleton = WDCSkeleton()
        self.podium_container.addWidget(self.skeleton)
        self.load_Teams()
        
    def load_Teams(self):
        self.worker = Worker(get_constructors_standings)
        self.worker.finished.connect(self.on_Teams_loaded)
        self.worker.failed.connect(self.on_failed)
        self.worker.start()

    def clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
    
    def on_Teams_loaded(self, drivers):
        
        # --- Clear podium skeleton
        self.clear_layout(self.podium_container)

        # --- Podium
        podium_hbox = QHBoxLayout()
        podium_hbox.setSpacing(30)
        podium_hbox.setAlignment(Qt.AlignmentFlag.AlignCenter)
        podium_heights = [50, 0, 50]  
        podium_order = [drivers[1], drivers[0], drivers[2]]  # 2nd, 1st, 3rd
        podium_sizes = [(200,200), (240,240), (200,200)]

        for i, driver in enumerate(podium_order):
            vbox = QVBoxLayout()
            vbox.addSpacing(podium_heights[i])
            card = PodiumTeams(driver, size=podium_sizes[i])
            vbox.addWidget(card)
            vbox.addStretch()
            podium_hbox.addLayout(vbox)

        self.podium_container.addLayout(podium_hbox)
        self.podium_container.addSpacing(20)

        # --- Remaining drivers list
        self.clear_layout(self.list_vbox)
        for d in drivers[3:]:
            card = QFrame()
            card.setStyleSheet("background-color: #1E1E1E; border-radius: 12px;")
            card_layout = QHBoxLayout()
            card_layout.setContentsMargins(15,10,15,10)
            card_layout.setSpacing(20)

            pos_label = QLabel(d["positionText"])
            pos_label.setStyleSheet("color: #FFD700; font-weight: bold; min-width: 30px;")
            name_label = QLabel(f" {d['constructorName']}")
            name_label.setStyleSheet("color: #EAEAEA; font-weight: bold;")
            points_label = QLabel(f"{d['points']} pts")
            points_label.setStyleSheet("color: #CCCCCC;")
            win_label = QLabel(f"{d['wins']} wins")
            win_label.setStyleSheet("color: #AAAAAA;")

            for lbl in [pos_label, name_label, points_label, win_label]:
                card_layout.addWidget(lbl)

            card.setLayout(card_layout)

            shadow = QGraphicsDropShadowEffect(card)
            shadow.setBlurRadius(15)
            shadow.setXOffset(0)
            shadow.setYOffset(3)
            shadow.setColor(QColor(0,0,0,140))
            card.setGraphicsEffect(shadow)

            self.list_vbox.addWidget(card)

    def on_failed(self, error_msg):
        show_api_error(self.podium_container, self.retry_load, message=f"Error: {error_msg}")

        
    def retry_load(self):
        self.clear_layout(self.podium_container)
        self.clear_layout(self.list_vbox)
        self.skeleton = WDCSkeleton()
        self.podium_container.addWidget(self.skeleton)
        self.load_Teams()
        
    
        
        
       
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = WccWindow()
    window.resize(900, 700)
    window.show()
    sys.exit(app.exec()) 
        
        