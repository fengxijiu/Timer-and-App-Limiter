import json

from PyQt5 import uic, QtCore, QtMultimedia, Qt
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QMainWindow, QSystemTrayIcon, QMenu, QAction
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
		self.path = path
		
		self.learn_time, self.break_time, self.apps, self.rest_period, self.tone = 0, 0, [], [], None
		
		self.config_update()
		
		self.rest_time = self.learn_time * 60
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
		# 创建系统托盘图标
		self.createTrayIcon(rf'{path}/data/clock.png')
		
		# # 设置窗口属性 - 隐藏任务栏图标
		self.setWindowFlags(self.windowFlags() | QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowMinimizeButtonHint)
	
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
			self.pause = True
			self.playSwitch.setText('PLAY')
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
			self.timerSwitch.setText('stopwatch')
		else:
			self.timerSwitch.setText('stopwatch')
			self.playSwitch.setText('PLAY' if self.pause else 'PAUSE')
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
		        for a in self.apps if not if_in_rest(get_time(), self.rest_period)]
	
	def createTrayIcon(self, path):
		# 创建系统托盘图标
		self.trayIcon = QSystemTrayIcon(self)
		self.trayIcon.setIcon(QIcon(path))  # 替换为你的图标路径
		
		# 创建托盘菜单
		trayMenu = QMenu()
		
		# 添加菜单项
		showAction = QAction("显示", self)
		showAction.triggered.connect(self.showNormal)
		trayMenu.addAction(showAction)
		
		exitAction = QAction("退出", self)
		exitAction.triggered.connect(self.closeApp)
		trayMenu.addAction(exitAction)
		
		self.trayIcon.setContextMenu(trayMenu)
		self.trayIcon.show()
		
		# 托盘图标点击事件
		self.trayIcon.activated.connect(self.onTrayIconActivated)
	
	def onTrayIconActivated(self, reason):
		# 双击托盘图标显示窗口
		if reason == QSystemTrayIcon.DoubleClick:
			self.showFullScreen()
	
	def closeApp(self):
		self.trayIcon.hide()
		QApplication.quit()
	
	def closeEvent(self, event):
		# 重写关闭事件，使其最小化到托盘而不是退出
		if self.trayIcon.isVisible():
			self.hide()
			event.ignore()
	
	def config_update(self):
		with open(rf'{self.path}/data/config.json', 'r') as f:
			config = json.load(f)
			self.learn_time = config['learn_time']
			self.break_time = config['break_time']
			self.tone = QtMultimedia.QSound(rf'{self.path}/data/{config["tone"]}')
			
			if config['appLimiter_if_open']:
				self.apps = config['apps']
				self.rest_period = config['rest_periods']
				self.al_timer = QTimer()
				self.al_timer.start(10)
				self.al_timer.timeout.connect(self.app_limit)
			f.close()