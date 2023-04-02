from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
import sys
import time
from timer import Ui_MainWindow
from relax import Ui_WindowTimer
from configparser import ConfigParser
import ctypes
import pygame
import os
from win32com.client import Dispatch
import getpass

boop = 'sounds/boop.mp3'
beep = 'sounds/beep.mp3'
pygame.init()
pygame.mixer.init()

myappid = 'mycompany.myproduct.subproduct.version' # arbitrary string
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)


class RelaxTimer(QMainWindow):
    config = ConfigParser()
    config.read('config.ini')
    RelaxTime = int(config.get("Settings", "relaxtime"))
    RelaxTimeSec = RelaxTime * 60
    #fullscreenparam = config.get("Settings", "fullscreen")

    def __init__(self):
        super(RelaxTimer, self).__init__()
        self.ui = Ui_WindowTimer()
        self.ui.setupUi(self)
        self.topLeft()
        self.setWindowFlags(QtCore.Qt.WindowType.WindowStaysOnTopHint | QtCore.Qt.WindowType.FramelessWindowHint | QtCore.Qt.WindowType.Tool)
        #self.config.read('config.ini')
        """if self.config.get("Settings", "fullscreen") == "True":
            print("tRUE")
            #layoutGrid = QGridLayout()
            #self.setLayout(layoutGrid)
            #self.setWindowOpacity(0.5)
            #self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)
            #self.showFullScreen()
            self.resize(500,200)
        elif self.config.get("Settings", "fullscreen") == "False":
            self.showNormal()"""
        self.ui.lineEdit.mouseMoveEvent = self.mouseMoveEvent
        self.ui.lineEdit.mousePressEvent = self.mousePressEvent
        self.isStart = True
        self.startTime = time.time()
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.timerFunction)
        self.timer.start(1000)

    def topLeft(self):
        self.move(0,0)

    def mouseMoveEvent(self, event):
        self.move(self.pos() + event.globalPosition().toPoint() - self.dragPos)
        self.dragPos = event.globalPosition().toPoint()
        event.accept()
    def mousePressEvent(self, event):
        self.dragPos = event.globalPosition().toPoint()

    def timerFunction(self):
        if self.isStart is True:
            time_r = int(time.time() - self.startTime)
            minutes = (time_r % 3600) // 60
            seconds = time_r % 60
            if minutes >= self.RelaxTime:
                pygame.mixer.music.load(beep)
                pygame.mixer.music.play()
                self.close()
                self.timer.stop()
                self.isStart = False
                Settings().start()
            else:
                m, s = divmod(int(self.RelaxTimeSec), 60)
                min_sec_format = '{:02d}:{:02d}'.format(m, s)
                time_str = min_sec_format
                self.ui.lineEdit.setText(str(time_str))
                self.RelaxTimeSec -= 1

class Settings(QMainWindow):
    tray = None
    username = getpass.getuser()
    config = ConfigParser()
    config.read('config.ini')
    RelaxTime = int(config.get("Settings", "relaxtime"))
    RelaxTimeSec = RelaxTime*60
    fullscreenparam = config.get("Settings", "fullscreen")
    m, s = divmod(int(RelaxTimeSec), 60)
    min_sec_format = '{:02d}:{:02d}'.format(m, s)
    time_str = min_sec_format
    isStart = False

    def __init__(self):
        super(Settings, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        if self.fullscreenparam == "True":
            self.ui.checkBox.setChecked(True)
        self.setWindowFlags(QtCore.Qt.WindowType.WindowStaysOnTopHint | QtCore.Qt.WindowType.FramelessWindowHint)
        self.ui.WorkTime.setValue(int(self.config.get("Settings", "worktime")))
        self.ui.RelaxTime.setValue(self.RelaxTime)
        self.ui.Timer.setText(str(self.time_str))
        self.ui.checkBox.stateChanged.connect(self.getcheckbox)
        self.ui.WorkTime.valueChanged.connect(self.get_minutesWorkTime)
        self.ui.RelaxTime.valueChanged.connect(self.get_minutesRelaxTime)
        self.ui.HideTrayButton.clicked.connect(self.hideintray)
        self.ui.SaveSettingsButton.clicked.connect(self.savesettings)
        self.setWindowIcon(QtGui.QIcon("images/eyetrayicon-transformed.png"))
        if self.config.get("Settings", "firstlaunch") == "True":
            self.askuser()
        self.tray()
        self.start()

    def getcheckbox(self):
        if self.ui.checkBox.isChecked():
            self.config.set('Settings', 'FullScreen', 'True')
        else:
            self.config.set('Settings', 'FullScreen', 'False')
        self.writeinconfig()
    def mouseMoveEvent(self, event):
        self.move(self.pos() + event.globalPosition().toPoint() - self.dragPos)
        self.dragPos = event.globalPosition().toPoint()
        event.accept()

    def mousePressEvent(self, event):
        self.dragPos = event.globalPosition().toPoint()

    def tray(self):
        self.icon = QIcon("images/eyetrayicon-transformed.png")
        self.iconfornotify = QIcon("images/eyetrayicon-transformed.png")
        self.tray = QSystemTrayIcon()
        self.tray.setIcon(self.icon)
        self.tray.setVisible(True)
        self.tray.activated.connect(self.restore_window)
        self.menu = QMenu()
        self.action = QAction("Show")
        self.action.triggered.connect(self.show)
        self.menu.addAction(self.action)
        self.quit = QAction("Quit")
        self.quit.triggered.connect(sys.exit)
        self.hideaction = QAction("Hide")
        self.menu.addAction(self.hideaction)
        self.hideaction.triggered.connect(self.hide)
        self.menu.addAction(self.quit)
        self.tray.setContextMenu(self.menu)
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.timerFunction)
        self.timer.start(1000)

    def closeEvent(self, event):
        event.ignore()
        self.hide()
        self.tray.showMessage("EYECHILL", "Application was minimized to Tray", self.iconfornotify, 2000)

    def hideintray(self):
        self.hide()
        self.tray.showMessage("EYECHILL", "Application was minimized to Tray", self.iconfornotify, 2000)

    def restore_window(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            if self.isHidden():
                self.tray.show()
                self.showNormal()
    def savesettings(self):
        self.get_minutesWorkTime()
        self.get_minutesRelaxTime()

    def get_minutesWorkTime(self):
        value = self.ui.WorkTime.value()
        value = str(value)
        self.config.set('Settings', 'WorkTime', value)
        self.writeinconfig()

    def get_minutesRelaxTime(self):
        value = self.ui.RelaxTime.value()
        value = str(value)
        self.config.set('Settings', 'RelaxTime', value)
        self.writeinconfig()

    def start(self):
        global startTime, isStart, WorkTimeSec
        self.WorkTime = int(self.config.get("Settings", "worktime"))
        WorkTimeSec = self.WorkTime * 60
        startTime = time.time()
        time.sleep(1)
        isStart = True

    def timerFunction(self):
        global WorkTimeSec, isStart, startTime
        if isStart:
            time_r = int(time.time() - startTime)
            minutes = (time_r % 3600) // 60
            seconds = time_r % 60
            if self.ui.Timer.text() == "00:30":
                pygame.mixer.music.load(boop)
                self.tray.showMessage("EYECHILL", "30 seconds before break", self.iconfornotify, 2000)
                pygame.mixer.music.play()
            if minutes >= self.WorkTime:
                RelaxTimer().show()
                isStart = False
                self.tray.setToolTip("Break")
            else:
                m, s = divmod(int(WorkTimeSec), 60)
                min_sec_format = '{:02d}:{:02d}'.format(m, s)
                time_str = min_sec_format
                self.ui.Timer.setText(str(time_str))
                self.tray.setToolTip(f'Time to break: {str(time_str)}')
                WorkTimeSec -= 1

    def askuser(self):
        reply = QMessageBox.question(self, 'Launch with windows', 'Add program in startup?', QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self.add_to_startup()
        if reply == QMessageBox.StandardButton.No:
            self.delete_from_startup()
    def add_to_startup(self):
        path = r'C:\Users\%s\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup\EyeChill.lnk' % self.username
        work_dir = os.getcwd()
        target = work_dir + "\eyechill.exe"

        shell = Dispatch('WScript.Shell')
        shortcut = shell.CreateShortCut(path)
        shortcut.Targetpath = target
        shortcut.WorkingDirectory = work_dir
        shortcut.save()

    def delete_from_startup(self):
        for file in os.listdir(f"C:/Users/{self.username}/AppData/Roaming/Microsoft/Windows/Start Menu/Programs/Startup/"):
            if file == "EyeChill.lnk":
                os.remove(f"C:/Users/{self.username}/AppData/Roaming/Microsoft/Windows/Start Menu/Programs/Startup/" + file)

    def writeinconfig(self):
        with open('config.ini', "w") as config_file:
            self.config.write(config_file)

def main():
    app = QtWidgets.QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    window = Settings()
    if window.config.get("Settings", "firstlaunch") == "True":
        window.config.set("Settings", "firstlaunch", "False")
        window.writeinconfig()
        window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()


