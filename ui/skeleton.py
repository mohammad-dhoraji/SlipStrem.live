# ui/skeletons.py
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFrame, QLabel,QSizePolicy
)
from PyQt6.QtCore import Qt

class SkeletonLoader(QFrame):
    """Simple gray block used inside skeletons."""
    def __init__(self, width=200, height=20, parent=None):
        super().__init__(parent)
        self.setFixedSize(width, height)
        self.setStyleSheet("""
            background-color: #333;   /* dark-ish grey fits your app theme */
            border-radius: 8px;
        """)


class DriverSkeleton(QWidget):
    """Skeleton layout for DriverCard placeholders."""
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout()
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(12)
        img = SkeletonLoader(100, 100)
        v = QVBoxLayout()
        v.setSpacing(8)
        v.addWidget(SkeletonLoader(180, 20))   # name
        v.addWidget(SkeletonLoader(140, 18))   # team
        v.addWidget(SkeletonLoader(120, 16))   # nationality/wins
        layout.addLayout(v)
        layout.addWidget(img, alignment=Qt.AlignmentFlag.AlignVCenter)

        self.setLayout(layout)


class ScheduleSkeleton(QWidget):
    """Skeleton layout for Timeline race cards (accepts side 'left'|'right')."""
    def __init__(self, side='left', parent=None):
        super().__init__(parent)
        main = QHBoxLayout()
        main.setContentsMargins(40, 0, 40, 0)
        main.setSpacing(20)

        # ----  timeline dot + line area
        timeline_box = QVBoxLayout()
        timeline_box.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
        dot = QLabel("●")
        dot.setStyleSheet("color: #555; font-size: 20px;")
        line = QFrame()
        line.setFrameShape(QFrame.Shape.VLine)
        line.setFixedWidth(3)
        line.setStyleSheet("background-color: #555;")
        timeline_box.addWidget(dot)
        timeline_box.addWidget(line, 1)

        timeline_container = QWidget()
        timeline_container.setLayout(timeline_box)
        timeline_container.setFixedWidth(50)

        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                border-radius: 12px;
                background-color: #2a2a2a;
                padding: 12px;
            }
        """)
        card_layout = QVBoxLayout()
        card_layout.setSpacing(10)
        card_layout.addWidget(SkeletonLoader(260, 22))  # race name
        card_layout.addWidget(SkeletonLoader(180, 18))  # date
        card_layout.addWidget(SkeletonLoader(220, 16))  # circuit/location
        card.setLayout(card_layout)

        if side == 'left':
            main.addWidget(card)
            main.addWidget(timeline_container)
            main.addStretch()
        else:
            main.addStretch()
            main.addWidget(timeline_container)
            main.addWidget(card)

        self.setLayout(main)


# --- ui/skeleton.py 
class WDCSkeleton(QWidget):
    def __init__(self, podium_count=3, list_count=6, parent=None):
        super().__init__(parent)
        self.podium_count = podium_count
        self.list_count = list_count
        self.initUI()

    def initUI(self):
        mainVbox = QVBoxLayout()
        mainVbox.setSpacing(20)
        
        # --- Podium skeleton
        podium_hbox = QHBoxLayout()
        podium_hbox.setSpacing(30)
        podium_hbox.setAlignment(Qt.AlignmentFlag.AlignCenter)

        for i in range(self.podium_count):
            vbox = QVBoxLayout()
            placeholder = QFrame()
            placeholder.setFixedSize(200, 200)
            placeholder.setStyleSheet("""
                background-color: #444449;
                border-radius: 12px;
            """)
            vbox.addWidget(placeholder)
            vbox.addStretch()
            podium_hbox.addLayout(vbox)

        mainVbox.addLayout(podium_hbox)

        # --- Remaining drivers list skeleton
        for _ in range(self.list_count):
            card = QFrame()
            card.setStyleSheet("""
                background-color: #444444;
                border-radius: 12px;
            """)
            card.setFixedHeight(60)
            mainVbox.addWidget(card)

        self.setLayout(mainVbox)

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QScrollArea
from PyQt6.QtCore import Qt

class RaceResultsSkeleton(QWidget):
    """Fullscreen skeleton layout for LatestRaceWindow"""
    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)

        # --- Race Info Placeholder ---
        race_info = QFrame()
        race_info.setFixedHeight(120)
        race_info.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        race_info.setStyleSheet("""
            background-color: #2A2F38;
            border-radius: 15px;
        """)
        layout.addWidget(race_info)

        # --- Driver List Placeholders ---
        for _ in range(8):
            driver_placeholder = QFrame()
            driver_placeholder.setFixedHeight(60)
            driver_placeholder.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            driver_placeholder.setStyleSheet("""
                background-color: #2A2F38;
                border-radius: 12px;
            """)
            layout.addWidget(driver_placeholder)

        # --- Circuit Image Placeholder ---
        circuit_placeholder = QFrame()
        circuit_placeholder.setFixedHeight(300)
        circuit_placeholder.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        circuit_placeholder.setStyleSheet("""
            background-color: #2A2F38;
            border-radius: 15px;
        """)
        layout.addWidget(circuit_placeholder)

        self.setLayout(layout)