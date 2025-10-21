# splashscreen.py

from PyQt6.QtWidgets import QSplashScreen
from PyQt6.QtGui import QPixmap, QFont, QIcon
from PyQt6.QtCore import Qt


class SplashScreen(QSplashScreen):
    def __init__(self, logo_path: str = "assets/logo/SlipStream.live.png"):
        
        pixmap = QPixmap(logo_path)
        scaled = pixmap.scaled(550, 550, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        super().__init__(scaled)

        font = QFont("Arial", 24, QFont.Weight.Bold)
        self.setFont(font)

        # self.showMessage(
            
        #     "Warming up the tires…",
            
        #     Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignCenter,
        #     Qt.GlobalColor.white,
            
        # )
        
