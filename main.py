import os
import sys

from PyQt5.QtWidgets import QApplication

from Timer import Timer

def get_path():
	if getattr(sys, 'frozen', False):
		base_path = sys._MEIPASS
	else:
		base_path = os.path.dirname(os.path.abspath(__file__))
	
	return base_path

if __name__ == "__main__":
	path = get_path()
	app = QApplication(sys.argv)
	timer = Timer(path)
	timer.show()
	sys.exit(app.exec_())
