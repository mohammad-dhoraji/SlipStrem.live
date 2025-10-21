# -- Main Window
import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QPushButton, QLabel,
    QVBoxLayout, QHBoxLayout, QStackedWidget, QFrame
)
from PyQt6.QtCore import Qt, QPropertyAnimation, QRect
from PyQt6.QtGui import QIcon

from ui.driverspage import DriversWindow
from ui.RaceSchedule import ScheduleWindow 
from ui.wdc import WdcWindow
from ui.wcc import WccWindow
from ui.d_details import DriverDetails
from ui.results import LatestRaceWindow
from config.colors import TEAM_COLORS

DEFAULT_GRADIENT = """
QMainWindow {
    background: qlineargradient(
        spread:pad, x1:0, y1:0, x2:1, y2:1,
        stop:0 #0D0D0D, stop:1 #1A1A1A
    );
    font-family: 'Segoe UI', Arial;
}
"""

SIDEBAR_STYLE = """
QFrame {
    background-color: #1A1A1A;
    border-right: 2px solid #2E2E2E;
}
QPushButton {
    background: #242424;
    color: #EAEAEA;
    padding: 12px;
    border-radius: 6px;
    font-weight: 600;
    font-size: 15px;
}
QPushButton:hover {
    background: #3C3C3C;
}
"""

TOPBAR_STYLE = """
QPushButton {
    background: #5A5AFF;
    color: white;
    font-size: 18px;
    border-radius: 6px;
}
QPushButton:hover {
    background: #7878FF;
}
QLabel {
    color: white;
    font-size: 18px;
    font-weight: 700;
}
"""


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SlipStream.Live - A F1 Dashboard")
        self.setWindowIcon(QIcon("assets/logo/SlipStream.live.png")) 
        self.hamburger = QPushButton("☰")
        self.stack = QStackedWidget()

        # ---- Page storage ----
        self.page_map = {}

        self.initUI()
        self.load_page("Results - GP")
        self.stack.setCurrentWidget(self.page_map["Results - GP"])
        
    def initUI(self):
        # ---- Hamburger ---- 
        self.hamburger.setFixedSize(40, 40)
        self.hamburger.setStyleSheet(TOPBAR_STYLE)
        self.hamburger.clicked.connect(self.toggle_sidebar)
        
        # --- Page Title ---
        self.page_title = QLabel(" Results - GP ")
        self.page_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.page_title.setStyleSheet("color: white; font-size: 18px; font-weight: 700;")

        # --- Top Bar Layout ---
        topHbox = QHBoxLayout()
        topHbox.setContentsMargins(10, 10, 10, 10)
        topHbox.addWidget(self.hamburger, alignment=Qt.AlignmentFlag.AlignLeft)
        topHbox.addStretch()
        topHbox.addWidget(self.page_title)
        topHbox.addStretch()

        # --- Central Layout ---
        self.central_widget = QWidget()
        self.central_widget.setObjectName("central_widget")
        self.setCentralWidget(self.central_widget)
        self.stack.setStyleSheet("background: transparent;")

        mainvbox = QVBoxLayout(self.central_widget)
        mainvbox.setContentsMargins(0, 0, 0, 0)
        mainvbox.addLayout(topHbox)
        mainvbox.addWidget(self.stack)
        
        self.sidebar = QFrame(self)
        self.sidebar.setObjectName("sidebar")
        self.sidebar.setGeometry(-200, 0, 200, self.height())
        self.sidebar.setStyleSheet(SIDEBAR_STYLE)

        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(10, 20, 10, 10)
        sidebar_layout.setSpacing(10)

        # ---- Sidebar Buttons ---- 
        btn_drivers = QPushButton("🏎 Drivers")
        btn_schedule = QPushButton("📅 Schedule")
        btn_wdc = QPushButton("🏆 WDC")
        btn_construct = QPushButton("🏆 WCC")
        last_race = QPushButton("Results - GP")

        button_map = {
            btn_drivers: "drivers",
            btn_schedule: "schedule",
            btn_wdc: "wdc", 
            btn_construct: "wcc",
            last_race: "Results - GP"
        }

        for btn, name in button_map.items():
            btn.setStyleSheet("""
                QPushButton {
                    background: #242424;
                    color: #EAEAEA;
                    padding: 12px;
                    border-radius: 8px;
                    font-weight: 600;
                    font-size: 15px;
                }
                QPushButton:hover {
                    background: #3C3C3C;
                }
            """)
            sidebar_layout.addWidget(btn)
            btn.clicked.connect(lambda _, n=name: self.switch_page(n))

        sidebar_layout.addStretch()

        # ---- Sidebar Animation ----
        self.anim = QPropertyAnimation(self.sidebar, b"geometry")
        self.anim.setDuration(300)
        self.sidebar_open = False
        self.setStyleSheet(DEFAULT_GRADIENT)
        
    def toggle_sidebar(self):
        if self.sidebar_open:
            self.anim.setStartValue(QRect(0, 0, 200, self.height()))
            self.anim.setEndValue(QRect(-200, 0, 200, self.height()))
        else:
            self.anim.setStartValue(QRect(-200, 0, 200, self.height()))
            self.anim.setEndValue(QRect(0, 0, 200, self.height()))
        self.anim.start()
        self.sidebar_open = not self.sidebar_open

    def load_page(self, name):
        """Lazy-load pages by name"""
        if name not in self.page_map:
            if name == "drivers":
                widget = DriversWindow()
                widget.driverClickedGlobal.connect(self.show_driver_details)
            elif name == "schedule":
                widget = ScheduleWindow()
            elif name == "wdc":
                widget = WdcWindow()
            elif name == "wcc":
                widget = WccWindow()
            elif name == "Results - GP":
                widget = LatestRaceWindow()
            else:
                return
            self.page_map[name] = widget
            self.stack.addWidget(widget)

    def switch_page(self, name):
        self.load_page(name)
        self.stack.setCurrentWidget(self.page_map[name])

        title_map = {
            "drivers": "Drivers - 2025 Grid",
            "schedule": "Race Schedule",
            "wdc": "World Drivers Championship",
            "wcc": "World Constructors Championship",
            "Results - GP": "Latest Race Results"
        }

        page_title_text = title_map.get(name, "")
        self.page_title.setText(page_title_text)
        self.setWindowTitle(f"SlipStream.Live - {page_title_text}")

        self.toggle_sidebar()
        self.setStyleSheet(DEFAULT_GRADIENT)

    def set_team_background(self, team_name: str):
        """Change main window gradient based on team"""
        if not team_name or team_name not in TEAM_COLORS:
            self.setStyleSheet(DEFAULT_GRADIENT)
            return
        color = TEAM_COLORS[team_name]
        gradient = f"""
        QMainWindow {{
            background: qlineargradient(
                x1:0, y1:0, x2:0, y2:1,
                stop:0 {color},
                stop:1 #000
            );
        }}
        """
        self.setStyleSheet(gradient)




    def show_driver_details(self, driver_id: str):
        drivers_window = self.page_map["drivers"]
        driver = next((d for d in drivers_window.drivers if d["driverId"] == driver_id), None)
        if not driver:
            return

        constructor = {
            "name": driver.get("constructorName", "N/A"),
            "nationality": driver.get("constructorNationality", "N/A"),
            "constructorId": driver.get("constructorId", "N/A")
        }

        details_page = DriverDetails(driver, constructor)
        details_page.driverSelected.connect(self.handle_details_signal)
        self.stack.addWidget(details_page)
        self.stack.setCurrentWidget(details_page)

        full_name = f"{driver.get('givenName', 'Driver')} {driver.get('familyName', '')}"
        page_title_text = f"Drivers - {full_name}"
        self.page_title.setText(page_title_text)
        self.setWindowTitle(f"SlipStream.Live - {page_title_text}")
        self.set_team_background(constructor["name"])
            
    def handle_details_signal(self, msg: str):
        if msg == "back":
            self.stack.setCurrentWidget(self.page_map["drivers"])
            self.page_title.setText("Drivers - 2025 Grid")  
            self.setStyleSheet(DEFAULT_GRADIENT)
        

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    app.setWindowIcon(QIcon("assets/logo/SlipStream.live.png"))
    screen = app.primaryScreen()
    screen_size = screen.availableGeometry()  
    width = int(screen_size.width() * 0.9)
    height = int(screen_size.height() * 0.9)
    window.resize(width, height)
    x = (screen_size.width() - width) // 2
    y = (screen_size.height() - height) // 2
    window.move(x, y)
    window.show()
    import services.update_json
    services.update_json.run_in_background()
    sys.exit(app.exec())