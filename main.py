import os
import sys

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from PyQt5.QtWidgets import QApplication

from Timer import Timer


class DataUpdateHandler(FileSystemEventHandler):
	def __init__(self):
		self.action = None
	
	def on_modified(self, event):
		print(1)
		self.action()
	
	def assign_action(self, action):
		self.action = action


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
	
	observer = Observer()
	event_handler = DataUpdateHandler()
	event_handler.assign_action(timer.config_update)
	
	observer.schedule(event_handler, os.path.join(path, 'data'), recursive=True)
	observer.start()
	
	timer.show()
	sys.exit(app.exec_())
