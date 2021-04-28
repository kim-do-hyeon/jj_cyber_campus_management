# Call Module
import os
import sys
import requests
import urllib.request
import subprocess
from bs4 import BeautifulSoup
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5 import uic
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import * 
from requests import get
from pathlib import Path

# Log Timestamp Function
def timestamp():
    import datetime
    return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

# Log Function
def log(message):
    message = timestamp() + ' > ' + message
    print(message, file=log_file)

# Open log file (log.txt)
log_file = open("log.txt", 'w', -1, 'utf-8')
log("*** Start Update Program ***")

# Call ui(Login.ui) File
ui_update_path = "src/update.ui"
ui_update = uic.loadUiType(ui_update_path)[0]

# Call Gui Enviroment (Update)
class update(QMainWindow, ui_update):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowIcon(QIcon('src\icon.ico')) # Icon setting
        self.show()
        self.update_bar.setValue(0)
        self.update()

    def update(self):
        fileObj = Path("src/file.exe")
        if fileObj.is_file() == False :
            QMessageBox.information(self, 'Download', '새로운 버전을 다운 받습니다.', QMessageBox.Ok, QMessageBox.Ok)
            self.update_file()
        else :
            f = open("src/version", "r")
            current_version = f.read()
            log("Current Version : " + str(current_version))
            version_url = "https://github.com/kim-do-hyeon/jj_cyber_campus_management/blob/main/src/version"
            global latest_version
            response = requests.get(version_url)
            webpage = urllib.request.urlopen(version_url)
            soup = BeautifulSoup(webpage, 'html.parser')
            latest_version = soup.find_all(class_='blob-code blob-code-inner js-file-line')[0].get_text()
            log("Latest Version : " + str(latest_version))
            if current_version != latest_version :
                reply = QMessageBox.question(self, '업데이트 확인', '새로운 버전을 다운받겠습니까?', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                if reply == QMessageBox.Yes :
                    log("Download New Version : " + str(latest_version))
                    self.update_file()
                elif reply == QMessageBox.No :
                    log("No Download")
                    self.run_file()
            else :
                self.run_file()

    def update_file(self):
        try :
            log("Remove Current Version File")
            os.remove("src/file.exe")
        except:
            pass
        link = "https://git.pdm0205.com/pental/jj_cyber_management/-/raw/master/share/src/file.exe?inline=false"
        path = "src/file.exe"
        with open(path, 'wb') as f:
            log("Download New Version File")
            response = requests.get(link, stream=True)
            total_length = response.headers.get('content-length')
            if total_length is None:
                f.write(response.content)
            else:
                dl = 0
                total_length = int(total_length)
                for data in response.iter_content(chunk_size=4096):
                    dl += len(data)
                    f.write(data)
                    done = int(50 * dl / total_length)
                    self.update_bar.setValue(done * 2)
            log("Download Success")
        f = open('src/version', mode='wt', encoding='utf-8')
        f.write(latest_version)
        f.close()
        self.run_file()
        
    def run_file(self):
        self.close()
        log("Run Main File")
        path = os.getcwd() + "/src/file.exe"
        log("Path : " + str(path))
        subprocess.call(path)
        quit()

def main():
    app = QApplication(sys.argv)
    window = update()
    window.show()
    app.exec_()

if __name__ == "__main__":
    main()