import json

from PyQt5 import uic, QtCore, QtMultimedia, Qt
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication, QMainWindow
import sys
import time

from appLimiter import *


class Timer(QMainWindow):
	def __init__(self, path: str):
		super().__init__()
		uic.loadUi(rf"{path}/ui/Timer.ui", self)
		self.timer = None
		self.font_size = None
		self.first_show = True
		self.timer_flag = 'clock'
		with open(rf'{path}/data/config.json', 'r') as f:
			config = json.load(f)
			self.learn_time = config['learn_time']
			self.break_time = config['break_time']
			
			if config['appLimiter_if_open']:
				self.apps = config['apps']
				self.rest_period = config['rest_periods']
				self.al_timer = QTimer()
				self.al_timer.start(10)
				self.al_timer.timeout.connect(self.app_limit)
				
		self.rest_time = self.learn_time * 60
		self.tone = QtMultimedia.QSound(rf'{path}/data/{config["tone"]}')
		self.set_font_size()
		self.timerSwitch.clicked.connect(self.timer_switch)
		self.timerSwitch.setText('stopwatch')
		self.playSwitch.clicked.connect(self.play_switch)
		self.playSwitch.setText('')
		
		self.music.setText('music')
		
		self.centralwidget.setMouseTracking(True)
		self.centralwidget.installEventFilter(self)
		self.buttonView.setMouseTracking(True)
		self.buttonView.installEventFilter(self)
		self.timeBrowser.setMouseTracking(True)
		self.timeBrowser.installEventFilter(self)
		
		self.idle_timer = QTimer()
		self.idle_timer.start(5000)
		self.idle_timer.timeout.connect(self.set_button_view_invisible)
		self.init_timer()
		self.showFullScreen()
		
		self.pause = False
	
	def set_time(self):
		if self.first_show:
			self.first_show = False
			return
		if self.timer_flag == 'clock':
			t = time.localtime()
			current_time = time.strftime("%H:%M:%S", t)
		else:
			if self.rest_time <= 0:
				self.tone.play()
				if self.timer_flag == 'stopwatch':
					self.timer_flag = 'break'
					self.rest_time = float(self.break_time * 60)
				elif self.timer_flag == 'break':
					self.timer_flag = 'clock'
					self.rest_time = float(self.learn_time * 60)
			current_time = f"{int(self.rest_time) // 60 // 60:02d}:{int(self.rest_time) // 60:02d}:{int(self.rest_time) % 60:02d}"
			if not self.pause:
				self.rest_time -= 0.1
		
		browser_height = self.timeBrowser.size().height()
		self.set_font_size()
		self.timeBrowser.setText(f'''
					<div align="center" style="font-size: {self.font_size}px; height: {browser_height}px; line-height: {browser_height - self.font_size // 2}px">
						{current_time}
					</div>
					''')
	
	def set_button_view_invisible(self):
		self.timerSwitch.setText('')
		self.playSwitch.setText('')
		self.music.setText('')
	
	def init_timer(self):
		self.timer = QtCore.QTimer(self)
		self.timer.timeout.connect(self.set_time)
		self.timer.start(100)
	
	def set_font_size(self):
		window_size = self.size()
		font_size = window_size.width() // 5
		self.font_size = font_size
	
	def timer_switch(self):
		if self.timer_flag == 'clock':
			self.timer_flag = 'stopwatch'
			self.timerSwitch.setText('clock')
			self.playSwitch.setText('PAUSE')
		else:
			self.timer_flag = 'clock'
			self.rest_time = self.learn_time * 60
			self.timerSwitch.setText('stopwatch')
			self.playSwitch.setText('')
		self.set_time()
	
	def play_switch(self):
		if self.timer_flag == 'stopwatch' or self.timer_flag == 'break':
			if self.pause:
				self.pause = False
				self.playSwitch.setText('PAUSE')
			else:
				self.pause = True
				self.playSwitch.setText('PLAY')
	
	def keyPressEvent(self, event):
		if event.key() == QtCore.Qt.Key.Key_F11:
			if self.isFullScreen():
				self.showNormal()
			else:
				self.showFullScreen()
		elif event.key() == QtCore.Qt.Key.Key_Escape:
			if self.isFullScreen():
				self.showNormal()
	
	def play_music(self):
		return
	
	def reset_button_view_timer(self):
		if self.timer_flag == 'clock':
			self.timerSwitch.setText('clock')
		else:
			self.timerSwitch.setText('stopwatch')
			self.playSwitch.setText('pause' if self.pause else 'play')
		self.music.setText('music')
		
		self.idle_timer.stop()
		self.idle_timer.start(5000)
	
	def eventFilter(self, obj, event):
		"""事件过滤器，检测用户操作"""
		event_type = event.type()
		
		# 检测鼠标移动、点击或键盘按键
		if event_type in [event.MouseMove, event.MouseButtonPress, event.KeyPress]:
			self.reset_button_view_timer()
		
		return super().eventFilter(obj, event)
	
	def app_limit(self):
		processes = get_processes()
		return [limit_processes(processes, a)
		        for a in self.apps if not if_in_rest(get_time(), self.rest_time)]
