from PyQt5.QtWidgets import QApplication
import sys
from main_window import MainWindow
from database import UserManager

if __name__ == "__main__":
    app = QApplication(sys.argv)
    user_manager = UserManager()
    window = MainWindow(user_manager)
    window.show()
    sys.exit(app.exec_()) 