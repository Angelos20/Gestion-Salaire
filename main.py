import sys
from PySide6.QtWidgets import QApplication
from modules.auth.login import PageLogin
from configuration.database import init_db, seed_data

init_db()
seed_data()

def center_window(window):
    screen = window.screen().availableGeometry()
    size = window.geometry()
    x = (screen.width() - size.width()) // 2
    y = (screen.height() - size.height()) // 2
    window.move(x, y)

if __name__ == "__main__":

    app = QApplication.instance()
    if not app:
        app = QApplication(sys.argv)

    window = PageLogin()
    window.resize(500, 350)
    center_window(window)
    window.show()
    sys.exit(app.exec())