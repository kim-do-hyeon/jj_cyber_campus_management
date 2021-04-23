# Call Module
import os
import re
import sys
import sqlite3
import webbrowser
import zipfile\
from bs4 import BeautifulSoup
from selenium import webdriver
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5 import uic
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import * 
from requests import get
from pathlib import Path

# File Download Function
def download(url, file_name):
    with open(file_name, "wb") as file:
        response = get(url)
        file.write(response.content)

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
log("*** Start Program ***")

# Check Chrome Version
try :
    chrome_version = os.listdir('C:/Program Files (x86)/Google/Chrome/Application/')[0][:2]
    log("Chrome browser is installed.")
    chrome_check = 1
except :
    log("Chrome browser is not installed.")
    chrome_check = 0

# Check chromedriver is exist
fileObj = Path("chromedriver.exe")
if fileObj.is_file() == True :
    check = 1
else :
    check = 0

# Auto login Check Function
def auto_login(student_id, student_pw):
    result = [student_id, student_pw]
    conn = sqlite3.connect("user.db")
    cur = conn.cursor()
    cur.execute("create table user (user_id text, user_pw text)")
    cur.execute("insert into user values (?, ?)", result)
    conn.commit()
    conn.close()

# Call ui(Login.ui) File
ui_path = "src/login.ui"
ui = uic.loadUiType(ui_path)[0]

# Call Gui Enviroment (Login)
class LoginWindow(QMainWindow, ui):
    def __init__(self):
        super().__init__()

        # Download Chromedriver
        if chrome_check == 0 :
            QMessageBox.information(self, 'Chrome Browser', '크롬 브라우져를 설치해주세요.', QMessageBox.Ok, QMessageBox.Ok)
            quit()
        if check == 0 :
            QMessageBox.information(self, 'ChromeDriver', '필요한 프로그램을 다운받습니다.', QMessageBox.Ok, QMessageBox.Ok)
            log("Download Chromedriver")
            if chrome_version == '90' :
                chrome_version_90 = 'https://chromedriver.storage.googleapis.com/90.0.4430.24/chromedriver_win32.zip'
                download(chrome_version_90, "chromedriver.zip")
                log("Download Chromedriver Version 90")
                zipfile.ZipFile('chromedriver.zip').extract('chromedriver.exe')
                log("Unziped Chromedriver.zip")
            elif chrome_version == '89' :
                chrome_version_89 = 'https://chromedriver.storage.googleapis.com/89.0.4389.23/chromedriver_win32.zip'
                download(chrome_version_89, "chromedriver.zip")
                log("Download Chromedriver Version 89")
                zipfile.ZipFile('chromedriver.zip').extract('chromedriver.exe')
                log("Unziped Chromedriver.zip")
            elif chrome_version == '88' :
                chrome_version_88 = 'https://chromedriver.storage.googleapis.com/88.0.4324.96/chromedriver_win32.zip'
                download(chrome_version_88, "chromedriver.zip")
                log("Download Chromedriver Version 988")
                zipfile.ZipFile('chromedriver.zip').extract('chromedriver.exe')
                log("Unziped Chromedriver.zip")
            elif chrome_version == '87' :
                chrome_version_87 = 'https://chromedriver.storage.googleapis.com/87.0.4280.88/chromedriver_win32.zip'
                download(chrome_version_87, "chromedriver.zip")
                log("Download Chromedriver Version 87")
                zipfile.ZipFile('chromedriver.zip').extract('chromedriver.exe')
                log("Unziped Chromedriver.zip")
        elif check == 1 :
            log("Chromedriver is installed")
        
        self.setupUi(self)
        self.setWindowIcon(QIcon('src\icon.ico')) # Icon setting

        # Auto login check file (user.db)
        try :
            fileObj = Path("user.db")
            if fileObj.is_file() == True :
                conn = sqlite3.connect("user.db")
                cur = conn.cursor()
                cur.execute('select * from user')
                global user
                user = cur.fetchall()
                user_id = user[0][0]
                user_pw = user[0][1]
                self.login_id.setText(user_id)
                self.login_pw.setText(user_pw)
                global auto_login_check
                auto_login_check = 1
        except :
            pass

        # Login Buttons
        self.login_button.clicked.connect(self.login)

    # Login Function
    def login(self) :
        if self.login_id.text() == "" : # school id is blank
            QMessageBox.information(self, '로그인', '학번을 입력해주세요.', QMessageBox.Ok, QMessageBox.Ok)
            log("Login > School id is blank")
        elif self.login_pw.text() == "" : # passwrod is blank
            QMessageBox.information(self, '로그인', '비밀번호를 입력해 주세요.', QMessageBox.Ok, QMessageBox.Ok)
            log("Login > School Password is blank")
        else : # login
            log("Login > Try Login")
            options = webdriver.ChromeOptions()
            options.add_argument('headless')
            options.add_argument('window-size=1920x1080')
            options.add_argument("disable-gpu")
            log("Webdriver > headless, window-size=1920x1080, disable-gpu options")
            global driver
            try : 
                driver = webdriver.Chrome('chromedriver.exe', chrome_options=options) # Run chromedriver.exe
                log("Webdriver > Try to run Chrome")
                QMessageBox.information(self, 'Notice', '모든 강의를 확인하기 때문에 시간이 소요될수 있습니다.', QMessageBox.Ok, QMessageBox.Ok)
            except :
                QMessageBox.warning(self, 'File Error', 'chromedriver.exe 파일을 찾을수 없습니다.', QMessageBox.Ok, QMessageBox.Ok)
                log("Webdriver > Does not exist chromedriver.exe")
                return
            
            login_url = "https://cyber.jj.ac.kr/login.php"
            class_url = "http://cyber.jj.ac.kr/local/ubion/user/"

            student_id = (self.login_id.text())
            student_pw = (self.login_pw.text())
        
            # Login Page
            driver.get(login_url) # Open Login Page
            log("Webdriver > Access Url > https://cyber.jj.ac.kr/login.php")
            driver.find_element_by_name('username').send_keys(student_id) # Send ID
            driver.find_element_by_name('password').send_keys(student_pw) # Send Password
            driver.find_element_by_xpath('/html/body/div[2]/div[2]/div/div/div/div/div[1]/div[1]/div[1]/form/div[2]/input').click() # Button Click
            log("Webdriver > Try to Login")

            # user info Page
            driver.get(class_url) # Open User Info Page
            log("Webdriver > Access Url > http://cyber.jj.ac.kr/local/ubion/user/")

            html = driver.page_source
            soup = BeautifulSoup(html, 'html.parser')

            # Get Class Course Name
            log("*** Get Class Course Name ***")
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

            for i in range(len(class_all)) :
                log("Webdriver > Parse > Class > " + str(class_all[i]))

            if class_all == [] : # If class is blank, Login Fail
                QMessageBox.warning(self, '로그인 실패', '학번 또는 비밀번호를 확인해 주세요.', QMessageBox.Ok, QMessageBox.Ok)
                log("*** Login Fail ***")
            else : # If class is full, Login Success
                # Auto Login Function Activation
                log("*** Login Success ***")
                if auto_login_check == 0 :
                    reply = QMessageBox.question(self, '로그인 성공', '자동 로그인 기능을 활성화 하시겠습니까?', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                    if reply == QMessageBox.No :
                        return
                    elif reply == QMessageBox.Yes :
                        try :
                            auto_login(student_id, student_pw)
                        except :
                            QMessageBox.warning(self, '자동 로그인', '이미 자동로그인 기능이 활성화 되어 있습니다.', QMessageBox.Ok, QMessageBox.Ok)
                else :
                    pass
                log("*** Get Notice ***")
                notice_url = "http://cyber.jj.ac.kr/local/ubnotification/"
                driver.get(notice_url) # Open Notice Page
                log("Webdriver > Access Url > http://cyber.jj.ac.kr/local/ubnotification/")
                html = driver.page_source
                soup = BeautifulSoup(html, 'html.parser')

                # Notice Value Url
                temp = str(soup.find_all(class_="well wellnopadding"))
                temp = BeautifulSoup(temp)
                notice_url_value = []

                global notice_value
                notice_value = []

                for a in temp.find_all('a', href=True):
                    notice_url_value.append(a['href'])
                notice_url_value.pop()

                for i in range(len(notice_url_value)): # Get Notice Detail
                    name = (soup.find_all(class_="media-heading")[i].get_text())
                    timeago = (soup.find_all(class_="timeago")[i].get_text())
                    message = str(soup.find_all(class_="media-body")[i])
                    message = message.partition("<p>")[-1].replace("</p></div>","")
                    log("Webdriver > Parse > Notice > " + str([name, timeago, message, notice_url_value[i]]))
                    notice_value.append([name, timeago, message, notice_url_value[i]])

                global class_id
                global class_detail
                class_id = []
                class_detail = []

                # Get class id
                for i in range(len(class_all)) :
                    class_id.append(class_all[i][1].split("?")[1][3:])

                # Class Detail (Run time, etc)
                log("*** Get Class Detail ***")
                for i in range(len(class_id)) :
                    class_name = class_all[i][0]
                    class_process_url = "http://cyber.jj.ac.kr/report/ubcompletion/user_progress.php?id=" + class_id[i]
                    driver.get(class_process_url)
                    log("Webdriver > Access Url > " + str(class_process_url))
                    html = driver.page_source
                    soup = BeautifulSoup(html, 'html.parser')
                    for j in range(1,50) :
                        v = '#ubcompletion-progress-wrapper > div:nth-child(3) > table > tbody > tr:nth-child(' + str(j) + ')'
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
                            
                            check_need_time = int(need_time.replace(":",""))
                            if my_time == "미수강" :
                                check_my_time = 0
                            else :
                                check_my_time = int(my_time.replace(":",""))
                            if check_my_time > check_need_time :
                                check = "PASS"
                            else :
                                check = "FAIL"
                            log("Webdriver > Parse > Class Detail > " + str([class_name, title, need_time, my_time, check, check_my_time, check_need_time]))
                            class_detail.append([class_name, title, need_time, my_time, check])
                        except :
                            log("Webdriver > Parse > Class Detail > Error (No Videos)")
                            break

                # Get Link for Watch Cyber class
                log("*** Get Watch Video Link ***")
                video = []
                for i in range(len(class_id)) :
                    video_url = "http://cyber.jj.ac.kr/mod/vod/index.php?id=" + class_id[i]
                    driver.get(video_url)
                    log("Webdriver > Access Url > " + str(video_url))
                    html = driver.page_source
                    soup = BeautifulSoup(html, 'html.parser')
                    for j in range(100) :
                        html_1 = str(soup.select("#region-main > div > table > tbody > tr:nth-child(" + str(j) + ") > td.cell.c1 > a"))
                        url_soup = BeautifulSoup(html_1)
                        for a in url_soup.find_all('a', href=True):
                            log("Webdriver > Parse > Video Link > " + str([class_id[i], a['href']]))
                            video.append([class_id[i], a['href']])
                
                for i in range(len(class_detail)) :
                    class_detail[i].append(video[i])

                # Call Main Window
                self.management = MainWindow()
                self.management.show()
                self.close()

# Call ui(main.ui) File
ui_main_path = "src/main.ui"
ui_main = uic.loadUiType(ui_main_path)[0]

# Call Gui Enviroment (MainWindow)
class MainWindow(QMainWindow, ui_main):
    def __init__(self):
        log("*** Open MainWindow ***")
        super().__init__()
        self.setupUi(self)
        self.setWindowIcon(QIcon('src\icon.ico'))

        # Item Double Clicked Function
        self.notice_listWidget.itemDoubleClicked.connect(self.notice_ItemDoubleClicked)
        self.class_listWidget.itemDoubleClicked.connect(self.class_ItemDoubleClicked)
        self.tableWidget.cellDoubleClicked.connect(self.table_ItemDoubleClicked)

        # Button
        self.assign_button.clicked.connect(self.assign)
        self.grade_button.clicked.connect(self.grade)
        self.error_send.clicked.connect(self.error)
        self.exit_button.clicked.connect(self.exit)

        # Logo
        self.logo_label.setPixmap(QPixmap('src\logo.jpg'))

        #Get User Infomormation
        get_user_url = "http://cyber.jj.ac.kr/report/ubcompletion/user_progress.php?id=" + class_id[0]
        driver.get(get_user_url)
        log("Webdriver > Access Url > " + str(get_user_url))
        
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')

        # Get School User ID
        school_id = str(soup.select("#ubcompletion-progress-wrapper > div:nth-child(1) > table > tbody > tr:nth-child(1) > td"))
        regex = re.compile('{}(.*){}'.format(re.escape('<td class="text-left">'), re.escape('</td>')))
        global user_school_id
        user_school_id = regex.findall(school_id)[0]
        self.school_number_line.setText(str(user_school_id))
        log("Webdriver > Get Informtaion > " + str(user_school_id))

        # Get User Name
        name = str(soup.select("#ubcompletion-progress-wrapper > div:nth-child(1) > table > tbody > tr:nth-child(2) > td"))
        regex = re.compile('{}(.*){}'.format(re.escape('<td class="text-left">'), re.escape('</td>')))
        global user_name
        user_name = regex.findall(name)[0]
        self.name_line.setText(str(user_name))
        log("Webdriver > Get Informtaion > " + str(user_name))

        # Get User Phone Number
        phone_number = str(soup.select("#ubcompletion-progress-wrapper > div:nth-child(1) > table > tbody > tr:nth-child(3) > td"))
        regex = re.compile('{}(.*){}'.format(re.escape('<td class="text-left">'), re.escape('</td>')))
        global user_phone_number
        user_phone_number = regex.findall(phone_number)[0]
        self.phone_number_line.setText(str(user_phone_number))
        log("Webdriver > Get Informtaion > " + str(user_phone_number))

        for i in range(len(class_all)) :
            self.class_listWidget.addItem(class_all[i][0])

        for i in range(len(notice_value)) :
            self.notice_listWidget.addItem(notice_value[i][0])

        # QtableWidget - Class Table
        _translate = QCoreApplication.translate
        self.tableWidget.setColumnCount(5)
        self.tableWidget.setRowCount(len(class_detail))

        for i in range(len(class_detail)):
            item = QTableWidgetItem()
            self.tableWidget.setVerticalHeaderItem(i, item)

        for i in range(5):
            item = QTableWidgetItem()
            self.tableWidget.setHorizontalHeaderItem(i, item)
        item = QTableWidgetItem()

        for i in range(len(class_detail)):
            for j in range(5):
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
        item = self.tableWidget.horizontalHeaderItem(4)
        item.setText(_translate("MainWindow", "통과"))
        __sortingEnabled = self.tableWidget.isSortingEnabled()
        self.tableWidget.setSortingEnabled(False)

        self.tableWidget.setColumnWidth(0, 150)
        self.tableWidget.setColumnWidth(1, 360)
        self.tableWidget.setColumnWidth(2, 65)
        self.tableWidget.setColumnWidth(3, 65)
        self.tableWidget.verticalHeader().setVisible(False)

        for i in range(len(class_detail)):
            for j in range(5):
                item = self.tableWidget.item(i, j)
                item.setFlags(QtCore.Qt.ItemIsEnabled) # Locked Cell
                if str(class_detail[i][j]) == "미수강" or str(class_detail[i][j]) == "FAIL":
                    item.setForeground(QBrush(Qt.red))
                    item.setBackground(QBrush(Qt.yellow))
                    item.setText(_translate("MainWindow", str(class_detail[i][j])))
                else :
                    item.setText(_translate("MainWindow", str(class_detail[i][j])))
        self.tableWidget.setSortingEnabled(__sortingEnabled)

    # Call Assign Function
    def assign(self):
        log("*** Get Assignment ***")
        QMessageBox.information(self, "과제 확인", "과제를 확인하는데 시간이 소요될수 있습니다.", QMessageBox.Ok, QMessageBox.Ok)
        global assign
        assign = []
        for i in range(len(class_id)) :
            class_name = class_all[i][0]
            class_assign_url = "http://cyber.jj.ac.kr/mod/assign/index.php?id=" + class_id[i]
            driver.get(class_assign_url) # Open Class Assign Page
            log("Webdriver > Access Url > " + str(class_assign_url))
            html = driver.page_source
            soup = BeautifulSoup(html, 'html.parser')
            temp = (soup.select("#region-main > div > table > tbody > tr:nth-child(1)"))
            temp1 = []
            temp2 = []
            for i in soup.select("#region-main > div > table > tbody > tr:nth-child(1)") :
                string = i.text.split("\n")
                string.pop()
                del string[0]
                temp1 = (string)
            temp = (soup.select("#region-main > div > table > tbody > tr.lastrow"))
            for i in soup.select("#region-main > div > table > tbody > tr.lastrow") :
                string = i.text.split("\n")
                string.pop()
                del string[0]
                temp2 = (string)
            if temp1 == [] :
                continue
            else :
                temp1.insert(0, class_name)
                temp2.insert(0,class_name)
                if temp1 == temp2 :
                    assign.append(temp1)
                    log("Webdriver > Parse > Get Assignment > " + str(temp1))
                else :
                    assign.append(temp1)
                    assign.append(temp2)
                    log("Webdriver > Parse > Get Assignment > " + str([temp1, temp2]))
        
        # Call Assign Window
        self.assignment = AssignWindow()
        self.assignment.show()

    # Call Grade Function
    def grade(self):
        log("*** Get Grade ***")
        QMessageBox.information(self, "성작 확인", "성적을 확인하는데 시간이 소요될수 있습니다.", QMessageBox.Ok, QMessageBox.Ok)
        grade_url = "http://cyber.jj.ac.kr/local/ubion/user/grade.php"
        driver.get(grade_url) # Open Grade Page
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        global grade_all
        grade_all = []
        try :
            for j in range(1, 9) :
                for i in soup.select("#region-main > div > div > div > table > tbody > tr:nth-child(" + str(j) + ") > td:nth-child(1)"):
                    year = (i.text)
                for i in soup.select("#region-main > div > div > div > table > tbody > tr:nth-child(" + str(j) + ") > td:nth-child(2)"):
                    semester = (i.text)
                for i in soup.select("#region-main > div > div > div > table > tbody > tr:nth-child(" + str(j) + ") > td:nth-child(3)"):
                    classname = (i.text)
                for i in soup.select("#region-main > div > div > div > table > tbody > tr:nth-child(" + str(j) + ") > td:nth-child(4)"):
                    professor = (i.text)
                for i in soup.select("#region-main > div > div > div > table > tbody > tr:nth-child(" + str(j) + ") > td:nth-child(5)"):
                    grade = (i.text)
                for i in soup.select("#region-main > div > div > div > table > tbody > tr:nth-child(" + str(j) + ") > td:nth-child(6)"):
                    grade_percent = (i.text)
                for i in soup.select("#region-main > div > div > div > table > tbody > tr:nth-child(" + str(j) + ") > td:nth-child(7)"):
                    complete_grade = (i.text)
                log("Webdriver > Parse > Grade > " + str([year, semester, classname, professor, grade, grade_percent, complete_grade]))
                grade_all.append([year, semester, classname, professor, grade, grade_percent, complete_grade])
        except :
            QMessageBox.warning(self, '오류', '성적을 가져오는데 오류가 발생하였습니다.\n오류 제보를 통해서 log.txt 파일을 보내주세요', QMessageBox.Ok, QMessageBox.Ok)
        
        # Call Grade Window
        self.grade = GradeWindow()
        self.grade.show()

    # Call Error Window
    def error(self) :
        self.error_window = ErrorWindow()
        self.error_window.show()

    def notice_ItemDoubleClicked(self) :
        get_notice_url = notice_value[self.notice_listWidget.currentRow()][3]
        driver.get(get_notice_url)
        log("DoubleClick > Notice > " + str([notice_value[self.notice_listWidget.currentRow()][0], notice_value[self.notice_listWidget.currentRow()][1], notice_value[self.notice_listWidget.currentRow()][2], notice_value[self.notice_listWidget.currentRow()][3]]))
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
        row = self.class_listWidget.currentRow()
        url = class_all[row][1]
        log("DoubleClick > Class > " + str([row, url]))
        webbrowser.open(url)
        log("DoubleClick > Class > Open > " + str(url))
    
    def table_ItemDoubleClicked(self) :
        row = self.tableWidget.currentRow()
        column = self.tableWidget.currentColumn()
        msgbox_title = self.tableWidget.item(self.tableWidget.currentRow(), 0).text()
        need_time = self.tableWidget.item(self.tableWidget.currentRow(), 2).text()
        my_time = self.tableWidget.item(self.tableWidget.currentRow(), 3).text()
        log("DoubleClick > Class Detail > " + str([msgbox_title, need_time, my_time]))
        if self.tableWidget.item(row, 3).text() == "미수강" or need_time > my_time:
            reply = QMessageBox.question(self, msgbox_title, '미수강된 강의입니다.\n강의 홈페이지로 이동하기를 원하십니까?', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.Yes:
                log("DoubleClick > Class Detail > Question > Y")
                url = (class_detail[row][5][1]).replace("view.php?id=", 'http://cyber.jj.ac.kr/mod/vod/view.php?id=')     
                webbrowser.open(url)
                log("DoubleClick > Class Detail > Open > " + str(url))
            else:
                log("DoubleClick > Class Detail > Question > N")
                return
        else :
            reply = QMessageBox.question(self, msgbox_title, '수강완료된 강의입니다.\n강의 홈페이지로 이동하기를 원하십니까?', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.Yes:
                log("DoubleClick > Class Detail > Question > Y")
                url = (class_detail[row][5][1]).replace("view.php?id=", 'http://cyber.jj.ac.kr/mod/vod/view.php?id=')
                webbrowser.open(url)
                log("DoubleClick > Class Detail > Open > " + str(url))
            else:
                log("DoubleClick > Class Detail > Question > N")
                return
    
    # Exit Function (Close Program)
    def exit(self) :
        log("*** Exit Program ***")
        self.close()

# Call ui(assign.ui) File
ui_assign_path = "src/assign.ui"
ui_assign = uic.loadUiType(ui_assign_path)[0]

# Call Gui Enviroment (AssignWindow)
class AssignWindow(QMainWindow, ui_assign):
    def __init__(self):
        log("*** Open Assinment Window ***")
        super().__init__()
        self.setupUi(self)
        self.setWindowIcon(QIcon('src\icon.ico'))

        # Button - Exit
        self.exit_button.clicked.connect(self.exit)

        # QtableWidget - Assign Table
        _translate = QCoreApplication.translate
        self.assign_tableWidget.setColumnCount(6)
        self.assign_tableWidget.setRowCount(len(assign))
        self.assign_tableWidget.verticalHeader().setVisible(False)

        for i in range(len(assign)):
            item = QTableWidgetItem()
            self.assign_tableWidget.setVerticalHeaderItem(i, item)

        for i in range(6):
            item = QTableWidgetItem()
            self.assign_tableWidget.setHorizontalHeaderItem(i, item)
        item = QTableWidgetItem()

        for i in range(len(assign)):
            for j in range(6):
                self.assign_tableWidget.setItem(i, j, item)
                item = QTableWidgetItem()

        for i in range(len(assign)) :
            item = self.assign_tableWidget.verticalHeaderItem(i)
            item.setText(_translate("MainWindow", str(i)))

        item = self.assign_tableWidget.horizontalHeaderItem(0)
        item.setText(_translate("MainWindow", "강의 이름"))
        item = self.assign_tableWidget.horizontalHeaderItem(1)
        item.setText(_translate("MainWindow", "주차"))
        item = self.assign_tableWidget.horizontalHeaderItem(2)
        item.setText(_translate("MainWindow", "과제명"))
        item = self.assign_tableWidget.horizontalHeaderItem(3)
        item.setText(_translate("MainWindow", "종료일"))
        item = self.assign_tableWidget.horizontalHeaderItem(4)
        item.setText(_translate("MainWindow", "제출여부"))
        item = self.assign_tableWidget.horizontalHeaderItem(5)
        item.setText(_translate("MainWindow", "성적"))
        __sortingEnabled = self.assign_tableWidget.isSortingEnabled()
        self.assign_tableWidget.setSortingEnabled(False)

        self.assign_tableWidget.setColumnWidth(0, 135)
        self.assign_tableWidget.setColumnWidth(1, 170)
        self.assign_tableWidget.setColumnWidth(2, 200)
        self.assign_tableWidget.setColumnWidth(3, 130)
        self.assign_tableWidget.setColumnWidth(4, 100)
        self.assign_tableWidget.setColumnWidth(5, 30)

        for i in range(len(assign)):
            for j in range(6):
                item = self.assign_tableWidget.item(i, j)
                item.setFlags(QtCore.Qt.ItemIsEnabled) # Locked Cell
                item.setText(_translate("MainWindow", str(assign[i][j])))
        self.assign_tableWidget.setSortingEnabled(__sortingEnabled)

    # Exit Function (Close Assignment Window)
    def exit(self) :
        log("*** Exit Assignment Window ***")
        self.close()

# Call ui(grade.ui) File
ui_grade_path = "src/grade.ui"
ui_grade = uic.loadUiType(ui_grade_path)[0]

# Call Gui Enviroment (Grade Window)
class GradeWindow(QMainWindow, ui_grade):
    def __init__(self):
        log("*** Open Grade Window ***")
        super().__init__()
        self.setupUi(self)
        self.setWindowIcon(QIcon('src\icon.ico'))

        # Button - Exit
        self.exit_button.clicked.connect(self.exit)

        # QtableWidget - Grade Table
        _translate = QCoreApplication.translate
        self.grade_tableWidget.setColumnCount(7)
        self.grade_tableWidget.setRowCount(len(grade_all))
        self.grade_tableWidget.verticalHeader().setVisible(False)

        for i in range(len(grade_all)):
            item = QTableWidgetItem()
            self.grade_tableWidget.setVerticalHeaderItem(i, item)

        for i in range(7):
            item = QTableWidgetItem()
            self.grade_tableWidget.setHorizontalHeaderItem(i, item)
        item = QTableWidgetItem()

        for i in range(len(grade_all)):
            for j in range(7):
                self.grade_tableWidget.setItem(i, j, item)
                item = QTableWidgetItem()

        for i in range(len(grade_all)) :
            item = self.grade_tableWidget.verticalHeaderItem(i)
            item.setText(_translate("MainWindow", str(i)))

        item = self.grade_tableWidget.horizontalHeaderItem(0)
        item.setText(_translate("MainWindow", "연도"))
        item = self.grade_tableWidget.horizontalHeaderItem(1)
        item.setText(_translate("MainWindow", "학기"))
        item = self.grade_tableWidget.horizontalHeaderItem(2)
        item.setText(_translate("MainWindow", "강좌명"))
        item = self.grade_tableWidget.horizontalHeaderItem(3)
        item.setText(_translate("MainWindow", "담당교수"))
        item = self.grade_tableWidget.horizontalHeaderItem(4)
        item.setText(_translate("MainWindow", "성적"))
        item = self.grade_tableWidget.horizontalHeaderItem(5)
        item.setText(_translate("MainWindow", "백분환산점수"))
        item = self.grade_tableWidget.horizontalHeaderItem(6)
        item.setText(_translate("MainWindow", "최종성적"))
        __sortingEnabled = self.grade_tableWidget.isSortingEnabled()
        self.grade_tableWidget.setSortingEnabled(False)

        for i in range(len(grade_all)):
            for j in range(7):
                item = self.grade_tableWidget.item(i, j)
                item.setFlags(QtCore.Qt.ItemIsEnabled) # Locked Cell
                item.setText(_translate("MainWindow", str(grade_all[i][j])))
        self.grade_tableWidget.setSortingEnabled(__sortingEnabled)
    
    # Exit Function (Close Grade Window)
    def exit(self) :
        log("*** Exit Grade Window ***")
        self.close()

# Call ui(error.ui) File
ui_error_path = "src/error.ui"
ui_error = uic.loadUiType(ui_error_path)[0]

# Call Gui Enviroment (Error Window)
class ErrorWindow(QMainWindow, ui_error):
    def __init__(self):
        log("*** Open Error Report Window ***")
        super().__init__()
        self.setupUi(self)
        self.setWindowIcon(QIcon('src\icon.ico'))

        # Button
        self.send_button.clicked.connect(self.send)
        self.include_button.clicked.connect(self.error_file_select)

        # radio
        self.writer_open_radio.clicked.connect(self.groupboxRadFunction)
        self.writer_close_radio.clicked.connect(self.groupboxRadFunction)
    
    def groupboxRadFunction(self) :
        global Disclosure_status
        if self.writer_open_radio.isChecked() :
            Disclosure_status = 1
            log("Error Report > Disclosure_status = 1")
        elif self.writer_close_radio.isChecked() :
            Disclosure_status = 0
            log("Error Report > Disclosure_status = 0")

    # Path Select 
    def error_file_select(self) :
        try:
            log("Error Report > Include File > Try")
            dialog = QFileDialog()
            global file_path
            file_filter = 'All files (*.*)'
            file_path = QFileDialog.getOpenFileName(self, 'Select File', filter=file_filter)
            file_path = file_path[0]
            self.file_label.setText(str(file_path))
            log("Error Report > Include File > " + file_path)
        except :
            log("Error Report > Include File > Fail")
            QMessageBox.information(self, "오류제보", "Error", QMessageBox.Ok, QMessageBox.Ok)

    # Mail Send Function
    def send(self) :
        from requests import get
        import socket
        import re, uuid
        User_Host_Name = socket.gethostname()
        User_IP_Internal = socket.gethostbyname(socket.gethostname())
        User_IP_External = get("https://api.ipify.org").text
        User_Mac = ':'.join(re.findall('..', '%012x' % uuid.getnode()))
        User_Computer_Information = "Information : " + str([User_Host_Name, User_IP_Internal, User_IP_External, User_Mac])

        log("Error Report > Send > Try")
        title = self.title_message.toPlainText()
        if title == "" :
            QMessageBox.information(self, "오류제보", "제목을 입력해주세요.", QMessageBox.Ok, QMessageBox.Ok)
            log("Error Report > Send > Blank Title")
            return
        content = str(self.content_message.toPlainText())
        if content == "" :
            QMessageBox.information(self, "오류제보", "내용을 입력해주세요.", QMessageBox.Ok, QMessageBox.Ok)
            log("Error Report > Send > Blank Content")
            return
        
        try :
            if Disclosure_status == 1:
                contact = "작성자 공개 : " + str([user_school_id, user_name, user_phone_number])
            else :
                contact = "작성자 공개 : 익명"
        except :
            QMessageBox.information(self, "오류제보", "작성자 공개 여부를 체크해주세요.", QMessageBox.Ok, QMessageBox.Ok)
            log("Error Report > Send > Error Disclosure_status")
            return

        user_contact = "연락쳐 : " + str(self.contact_message.toPlainText())
        if user_contact == "" :
            user_contact = "연락쳐 : 익명"
        
        content = content + "\n\n=====================================\n\n" + str(contact) + "\n\n" + str(user_contact) + "\n\n" + str(User_Computer_Information)

        try :
            import smtplib
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart
            from email.mime.base import MIMEBase
            from email import encoders
            s = smtplib.SMTP('smtp.gmail.com', 587)
            s.starttls()
            s.login('pental.system32@gmail.com', 'emwqpqjkhjbeoern')
            msg = MIMEMultipart()
            msg['Subject'] = title
            msg.attach(MIMEText(content, 'plain'))
            try :
                #File Upload
                attachment = open(file_path, 'rb')
                part = MIMEBase('application', 'octet-stream')
                part.set_payload((attachment).read())
                encoders.encode_base64(part)
                file_name = file_path.split("/")[-1]
                part.add_header('Content-Disposition', "attachment; filename= " + file_name)
                msg.attach(part)
            except :
                pass
            s.sendmail("pental.system32@gmail.com", "pental@kakao.com", msg.as_string())
            s.quit()
            log("Error Report > Send > Success")
            QMessageBox.information(self, "오류제보", "오류제보가 정상적으로 처리되었습니다.", QMessageBox.Ok, QMessageBox.Ok)
        except :
            log("Error Report > Send > Fail")
            QMessageBox.information(self, "오류제보", "문제가 발생하였습니다.", QMessageBox.Ok, QMessageBox.Ok)

# Main Function
def main():
    app = QApplication(sys.argv)
    window = LoginWindow()
    window.show()
    app.exec_()

if __name__ == "__main__":
    main()