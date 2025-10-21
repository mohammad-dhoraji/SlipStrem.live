import sys
import os
from pathlib import Path
import json
from datetime import datetime, timezone
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout,
    QScrollArea, QFrame, QGraphicsDropShadowEffect,QPushButton
)
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QPixmap, QColor
from services.worker import Worker
from utils.api_helper import on_failed as show_api_error
from services.Schedule import get_race_schedule
from services.results import get_all_race_winners
from ui.skeleton import ScheduleSkeleton


class TimelineRaceCard(QWidget):
    def __init__(self, race, side='left', highlight_upcoming=False):
        super().__init__()
        self.race = race
        self.side = side
        self.highlight_upcoming = highlight_upcoming
        self.initUI()
        self.setGraphicsEffect(None)

    def initUI(self):
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(40, 0, 40, 0)
        main_layout.setSpacing(20)

        # --- Date check
        race_time = self.race.get('time', '00:00:00')
        race_datetime = datetime.fromisoformat(
            f"{self.race['date']}T{race_time.replace('Z','')}"
        ).replace(tzinfo=timezone.utc)
        now = datetime.now(timezone.utc)

        # --- Labels
        circuit_name = QLabel(self.race['circuitName'])
        race_title = QLabel(f"Round {self.race['round']}: {self.race['raceName']}")
        location = f"{self.race['locality']}, {self.race['country']}"
        date_label = QLabel(f"Date & Time: {race_datetime.strftime('%d %b %Y, %H:%M UTC')}")
        loc_label = QLabel(location)

        # --- Colors
        if race_datetime < now:
            timeline_color = "#aaa"
            card_bg = "#4A4639"
        else:
            timeline_color = "#00b7ff"
            card_bg = "#2a2a2a"

        if self.highlight_upcoming:
            card_bg = "#033d16"
            timeline_color = "#0eff3a"

        # --- Timeline
        timeline_widget = QVBoxLayout()
        timeline_widget.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
        circle = QLabel("●")
        circle.setStyleSheet(f"color: {timeline_color}; font-size: 22px;")
        circle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        timeline_widget.addWidget(circle)

        line = QFrame()
        line.setFrameShape(QFrame.Shape.VLine)
        line.setStyleSheet(f"background-color: {timeline_color};")
        line.setFixedWidth(4)
        timeline_widget.addWidget(line, 1)

        timeline_container = QWidget()
        timeline_container.setLayout(timeline_widget)
        timeline_container.setFixedWidth(50)

        # --- Card
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                border-radius: 16px;
                background-color: {card_bg};
                padding: 15px;
            }}
        """)

        # --- Shadow effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(35)
        shadow.setXOffset(0)
        shadow.setYOffset(5)
        shadow.setColor(QColor(0,0,0,180))
        card.setGraphicsEffect(shadow)

        card_layout = QVBoxLayout()
        card_layout.setSpacing(8)

        # --- Track image
        pixmap = QPixmap(f"assets/circuits/{self.race['circuitId']}.png")
        if pixmap.isNull():
            pixmap = QPixmap(300, 180)
            pixmap.fill(Qt.GlobalColor.lightGray)
        scaled_pixmap = pixmap.scaledToHeight(180, Qt.TransformationMode.SmoothTransformation)
        img_label = QLabel()
        img_label.setPixmap(scaled_pixmap)
        img_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(img_label)

        # --- Race info
        race_title.setStyleSheet("color: #F44; font-weight: bold; font-size: 14px;")
        race_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(race_title)

        circuit_name.setStyleSheet("color: #ccc; font-size: 12px;")
        circuit_name.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(circuit_name)

        loc_label.setStyleSheet("color: #ccc; font-size: 12px;")
        loc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(loc_label)

        date_label.setStyleSheet("color: #ccc; font-size: 12px;")
        date_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(date_label)

        # --- Winner info
        if "winner" in self.race:
            w = self.race["winner"]
            winner_label = QLabel(f"Winner: {w['driverName']} ({w['constructor']})")
            winner_label.setStyleSheet("color: gold; font-size: 12px; font-weight: bold;")
            winner_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            card_layout.addWidget(winner_label)

        card.setLayout(card_layout)

        # --- Hover animation
        self.anim = QPropertyAnimation(card, b"geometry")
        self.anim.setDuration(150)
        self.anim.setEasingCurve(QEasingCurve.Type.InOutQuad)
        self.card = card

        # --- Layout
        if self.side == 'left':
            main_layout.addWidget(card)
            main_layout.addWidget(timeline_container)
            main_layout.addStretch()
        else:
            main_layout.addStretch()
            main_layout.addWidget(timeline_container)
            main_layout.addWidget(card)

        self.setLayout(main_layout)



class ScheduleWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("F1 2025 Race Schedule Timeline")
        self.setStyleSheet("""
            QWidget {background-color: transparent; font-family: 'Segoe UI', Arial, sans-serif; }
            QScrollArea { border: none; }
            QScrollBar:vertical { width: 8px; background: #2A2F38; margin: 0px; border-radius: 4px; }
            QScrollBar::handle:vertical { background: #555; border-radius: 4px; }
            QScrollBar::handle:vertical:hover { background: #888; }
        """)
        self.initUI()

    def initUI(self):
        self.main_layout = QVBoxLayout()
        self.progress_label = QLabel("Loading race schedule...")
        self.progress_label.setStyleSheet("color: white; font-size: 25px; font-weight: bold;")
        self.progress_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.main_layout.addWidget(self.progress_label)
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.container = QWidget()
        self.vbox = QVBoxLayout()
        self.vbox.setSpacing(30)
        self.vbox.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
        self.container.setLayout(self.vbox)
        self.scroll.setWidget(self.container)
        self.main_layout.addWidget(self.scroll)
        self.setLayout(self.main_layout)
        self.show_skeletons()
        self.load_schedule()

    def show_skeletons(self):
        for i in range(6):
            side = 'left' if i % 2 == 0 else 'right'
            self.vbox.addWidget(ScheduleSkeleton(side))

    def load_schedule(self):
        self.race_worker = Worker(get_race_schedule)
        self.race_worker.finished.connect(self.on_races_loaded)
        self.race_worker.failed.connect(self.on_failed)
        self.race_worker.start()

    def clear_vbox(self):
        while self.vbox.count():
            item = self.vbox.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

    def on_races_loaded(self, races):
        self.races = races
        appdata_dir = Path.home() / "AppData" / "Roaming" / "F1App"
        appdata_dir.mkdir(exist_ok=True)
        schedule_file = appdata_dir / "race_schedule.json"
        try:
            with schedule_file.open("w", encoding="utf-8") as f:
                json.dump(races, f, indent=4, ensure_ascii=False)
            print(f"✅ Race schedule saved to {schedule_file}")
        except Exception as e:
            print(f"❌ Failed to save race schedule: {e}")
            # --- Processed races file ---
        processed_file = appdata_dir / "processed_races.json"
        if not processed_file.exists():
            try:
                with processed_file.open("w", encoding="utf-8") as f:
                    json.dump([], f, indent=4)
                print(f"✅ Created empty processed_races.json at {processed_file}")
            except Exception as e:
                print(f"❌ Failed to create processed_races.json: {e}")
                
        self.winner_worker = Worker(get_all_race_winners)
        self.winner_worker.finished.connect(self.on_winners_loaded)
        self.winner_worker.failed.connect(self.on_failed)
        self.winner_worker.start()

    def on_winners_loaded(self, winners):
        for race in self.races:
            round_no = race.get("round")
            if round_no in winners:
                race["winner"] = winners[round_no]

        self.clear_vbox()
        now = datetime.now(timezone.utc)
        done_count = 0
        upcoming_race = None

        for race in self.races:
            race_time = race.get('time', '00:00:00')
            race_datetime = datetime.fromisoformat(
                f"{race['date']}T{race_time.replace('Z','')}"
            ).replace(tzinfo=timezone.utc)
            if race_datetime < now:
                done_count += 1
            elif upcoming_race is None:
                upcoming_race = race

        total_races = len(self.races)
        if upcoming_race:
            next_gp_name = upcoming_race['raceName']
            next_gp_round = upcoming_race['round']
            self.progress_label.setText(
                f"Up Next: {next_gp_name} | Race {next_gp_round} of {total_races}"
            )
        else:
            self.progress_label.setText("All races completed!")

        for i, race in enumerate(self.races):
            side = 'left' if i % 2 == 0 else 'right'
            highlight = (race == upcoming_race)
            card = TimelineRaceCard(race, side, highlight_upcoming=highlight)
            card.setGraphicsEffect(None)

            # ---- Fade-in animation ---- 
            anim = QPropertyAnimation(card, b"windowOpacity")
            anim.setDuration(400)
            anim.setStartValue(0)
            anim.setEndValue(1)
            anim.start()
            self.vbox.addWidget(card)

    def on_failed(self, error_msg):
        show_api_error(self.container, self.retry_load)

        
    def retry_load(self):
        self.clear_vbox()
        self.progress_label.setText("Retrying to load race schedule...")
        self.show_skeletons()
        self.load_schedule()



if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ScheduleWindow()
    window.resize(900, 800)
    window.show()
    sys.exit(app.exec())
