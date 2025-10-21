import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QIcon
from ui.splashscreen import SplashScreen
from ui.main_window import MainWindow  


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon("assets/logo/SlipStream.live.png"))
    splash = SplashScreen("assets/logo/SlipStream.live.png")
    splash.show()
    
    def show_main():
        app.main_window = MainWindow()  
        window = app.main_window
        screen = app.primaryScreen()
        screen_size = screen.availableGeometry()  
        width = int(screen_size.width() * 0.9)
        height = int(screen_size.height() * 0.9)
        window.resize(width, height)
        x = (screen_size.width() - width) // 2
        y = (screen_size.height() - height) // 2
        window.move(x, y)
        window.show()
        splash.finish(window)


    QTimer.singleShot(2500, show_main)

    sys.exit(app.exec())
