import socket
import sys
from PySide6.QtWidgets import QApplication
from ui.main_window import MainWindow

old_getaddrinfo = socket.getaddrinfo


def new_getaddrinfo(*args, **kwargs):
    return [r for r in old_getaddrinfo(*args, **kwargs) if r[0] == socket.AF_INET]


socket.getaddrinfo = new_getaddrinfo


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())