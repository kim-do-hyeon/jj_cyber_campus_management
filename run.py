import os
import re
import sys
from bs4 import BeautifulSoup
from selenium import webdriver
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5 import uic
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import * 

ui_path = "src/login.ui"
ui = uic.loadUiType(ui_path)[0] # Call ui file

class LoginWindow(QMainWindow, ui):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowIcon(QIcon('src\icon.ico'))

        # File Management Buttons
        self.login_button.clicked.connect(self.login)

    def login(self) :
        if self.login_id.text() == "" : # school id is blank
            QMessageBox.information(self, '로그인', '학번을 입력해주세요.', QMessageBox.Ok, QMessageBox.Ok)
        elif self.login_pw.text() == "" : # passwrod is blank
            QMessageBox.information(self, '로그인', '비밀번호를 입력해 주세요.', QMessageBox.Ok, QMessageBox.Ok)
        else : # login
            student_id = (self.login_id.text())
            student_pw = (self.login_pw.text())

            options = webdriver.ChromeOptions()
            options.add_argument('headless')
            options.add_argument('window-size=1920x1080')
            options.add_argument("disable-gpu")

            global driver
            driver = webdriver.Chrome('chromedriver.exe', chrome_options=options)

            login_url = "https://cyber.jj.ac.kr/login.php"
            class_url = "http://cyber.jj.ac.kr/local/ubion/user/"

            # login Page
            driver.get(login_url)
            driver.find_element_by_name('username').send_keys(student_id) # Send ID
            driver.find_element_by_name('password').send_keys(student_pw) # Send Password
            driver.find_element_by_xpath('/html/body/div[2]/div[2]/div/div/div/div/div[1]/div[1]/div[1]/form/div[2]/input').click() # Button Click

            # user info Page
            driver.get(class_url)
            html = driver.page_source
            soup = BeautifulSoup(html, 'html.parser')

            # Get Class Course Name
            class_url_html = str(soup.find_all(class_="coursefullname"))
            class_count = len(soup.find_all(class_='coursefullname'))
            class_name = []
            class_url = []
            for i in range(class_count) :
                class_name.append(soup.find_all(class_='coursefullname')[i].get_text())

            class_url_soup = BeautifulSoup(class_url_html)

            for a in class_url_soup.find_all('a', href=True):
                class_url.append(a['href'])
            
            global class_all
            class_all = []

            for i in range(class_count) :
                class_all.append([class_name[i], class_url[i]])
            
            if class_all == [] : # 강의가 없다면 로그인 실패
                QMessageBox.warning(self, '로그인 실패', '학번 또는 비밀번호를 확인해 주세요.', QMessageBox.Ok, QMessageBox.Ok)
            else :
                QMessageBox.information(self, '로그인 성공', '모든 강의를 확인하기 때문에 시간이 소요될수 있습니다.', QMessageBox.Ok, QMessageBox.Ok)
                
                notice_url = "http://cyber.jj.ac.kr/local/ubnotification/"
                driver.get(notice_url)
                html = driver.page_source
                soup = BeautifulSoup(html, 'html.parser')

                # Notice Value Url
                temp = str(soup.find_all(class_="well wellnopadding"))
                temp = BeautifulSoup(temp)
                notice_url_value = []

                global notice_value
                notice_value = []

                for a in temp.find_all('a', href=True):
                    notice_url_value.append(a['href'])\
                
                notice_url_value.pop()

                for i in range(len(notice_url_value)):
                    name = (soup.find_all(class_="media-heading")[i].get_text())
                    timeago = (soup.find_all(class_="timeago")[i].get_text())
                    message = str(soup.find_all(class_="media-body")[i])
                    message = message.partition("<p>")[-1].replace("</p></div>","")
                    notice_value.append([name, timeago, message, notice_url_value[i]])
  
                global class_id
                global class_detail
                class_id = []
                class_detail = []

                # Get class id
                for i in range(len(class_all)) :
                    class_id.append(class_all[i][1].split("?")[1][3:])

                # 강의 정보 (수강 시간 등)
                for i in range(len(class_id)) :
                    class_name = class_all[i][0]
                    class_process_url = "http://cyber.jj.ac.kr/report/ubcompletion/user_progress.php?id=" + class_id[i]
                    driver.get(class_process_url)
                    html = driver.page_source
                    soup = BeautifulSoup(html, 'html.parser')
                    for i in range(1,10) :
                        v = '#ubcompletion-progress-wrapper > div:nth-child(3) > table > tbody > tr:nth-child(' + str(i) + ')'
                        a = str(soup.select(v))
                        try :
                            regex = re.compile('{}(.*){}'.format(re.escape('icon"/>'), re.escape('</td><td class="text-center hidden-xs hidden-sm">')))
                            title = regex.findall(a)[0]

                            regex = re.compile('{}(.*){}'.format(re.escape('<td class="text-center hidden-xs hidden-sm">'), re.escape('</td><td class="text-center">')))
                            need_time = regex.findall(a)[0]

                            try :
                                regex = re.compile('{}(.*){}'.format(re.escape('<td class="text-center">'), re.escape('<br/>')))
                                my_time = regex.findall(a)[0]
                            except :
                                my_time = "미수강"

                            class_detail.append([class_name, title, need_time, my_time])
                        except :
                            break
                self.management = MainWindow()
                self.management.show()
                self.close()

ui_main_path = "src/main.ui"
ui_main = uic.loadUiType(ui_main_path)[0]
class MainWindow(QMainWindow, ui_main):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowIcon(QIcon('src\icon.ico'))
        self.notice_listWidget.itemDoubleClicked.connect(self.notice_ItemDoubleClicked)
        self.class_listWidget.itemDoubleClicked.connect(self.class_ItemDoubleClicked)
        # self.tableWidget.cellDoubleClicked.connect(self.table_ItemDoubleClicked)

        # Logo
        self.logo_label.setPixmap(QPixmap('src\logo.jpg'))

        #Get User Infomormation
        get_user_url = "http://cyber.jj.ac.kr/report/ubcompletion/user_progress.php?id=" + class_id[0]
        driver.get(get_user_url)
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        # School user id
        school_id = str(soup.select("#ubcompletion-progress-wrapper > div:nth-child(1) > table > tbody > tr:nth-child(1) > td"))
        regex = re.compile('{}(.*){}'.format(re.escape('<td class="text-left">'), re.escape('</td>')))
        school_id = regex.findall(school_id)[0]
        self.school_number_line.setText(str(school_id))
        # User Name
        name = str(soup.select("#ubcompletion-progress-wrapper > div:nth-child(1) > table > tbody > tr:nth-child(2) > td"))
        regex = re.compile('{}(.*){}'.format(re.escape('<td class="text-left">'), re.escape('</td>')))
        name = regex.findall(name)[0]
        self.name_line.setText(str(name))
        # User Phone Number
        phone_number = str(soup.select("#ubcompletion-progress-wrapper > div:nth-child(1) > table > tbody > tr:nth-child(3) > td"))
        regex = re.compile('{}(.*){}'.format(re.escape('<td class="text-left">'), re.escape('</td>')))
        phone_number = regex.findall(phone_number)[0]
        self.phone_number_line.setText(str(phone_number))

        for i in range(len(class_all)) :
            self.class_listWidget.addItem(class_all[i][0])

        for i in range(len(notice_value)) :
            self.notice_listWidget.addItem(notice_value[i][0])

        _translate = QCoreApplication.translate
        self.tableWidget.setColumnCount(4)
        self.tableWidget.setRowCount(len(class_detail))
        for i in range(len(class_detail)):
            item = QTableWidgetItem()
            self.tableWidget.setVerticalHeaderItem(i, item)
        for i in range(4):
            item = QTableWidgetItem()
            self.tableWidget.setHorizontalHeaderItem(i, item)
        item = QTableWidgetItem()
        for i in range(len(class_detail)):
            for j in range(4):
                self.tableWidget.setItem(i, j, item)
                item = QTableWidgetItem()
        for i in range(len(class_detail)) :
            item = self.tableWidget.verticalHeaderItem(i)
            item.setText(_translate("MainWindow", str(i)))
        item = self.tableWidget.horizontalHeaderItem(0)
        item.setText(_translate("MainWindow", "강의 이름"))
        item = self.tableWidget.horizontalHeaderItem(1)
        item.setText(_translate("MainWindow", "강의 제목"))
        item = self.tableWidget.horizontalHeaderItem(2)
        item.setText(_translate("MainWindow", "인정 시간"))
        item = self.tableWidget.horizontalHeaderItem(3)
        item.setText(_translate("MainWindow", "들은 시간"))
        __sortingEnabled = self.tableWidget.isSortingEnabled()
        self.tableWidget.setSortingEnabled(False)

        self.tableWidget.setColumnWidth(0, 150)
        self.tableWidget.setColumnWidth(1, 340)
        self.tableWidget.setColumnWidth(2, 70)
        self.tableWidget.setColumnWidth(3, 70)
            
        for i in range(len(class_detail)):
            for j in range(4):
                item = self.tableWidget.item(i, j)
                item.setFlags(QtCore.Qt.ItemIsEnabled) # Locked Cell
                item.setText(_translate("MainWindow", str(class_detail[i][j])))
        self.tableWidget.setSortingEnabled(__sortingEnabled)

    def notice_ItemDoubleClicked(self) :
        get_notice_url = notice_value[self.notice_listWidget.currentRow()][3]
        driver.get(get_notice_url)
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        try : 
            title = soup.find_all(class_="subject")[0].get_text()
            time = (soup.select("#region-main > div > div > div > div.well > div:nth-child(2) > div.date")[0].get_text())
            time = time.replace("\n", "").replace(" ", "").replace("\t","")
            time = (time[:14] + " " + time[14:])
            message = "작성시간 : " + str(notice_value[self.notice_listWidget.currentRow()][1]) + " (" + time + ")" + "\n"  + str(soup.find_all(class_="text_to_html")[0].get_text())
            message = message.replace(".", ".\n")
        except :
            title = self.notice_listWidget.currentItem().text()
            message = "작성시간 : " + str(notice_value[self.notice_listWidget.currentRow()][1]) + "\n"  + str(notice_value[self.notice_listWidget.currentRow()][2])
        QMessageBox.information(self, title, message, QMessageBox.Ok, QMessageBox.Ok)

    def class_ItemDoubleClicked(self) :
        import webbrowser
        row = self.class_listWidget.currentRow()
        url = class_all[row][1]
        webbrowser.open(url)

def main():
    app = QApplication(sys.argv)
    window = LoginWindow()
    window.show()
    app.exec_()

if __name__ == "__main__":
    main()