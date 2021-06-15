from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow
import sys

from pipGUI import pipGUI

app = QApplication(sys.argv)

window = pipGUI()

window.show()

sys.exit(app.exec())