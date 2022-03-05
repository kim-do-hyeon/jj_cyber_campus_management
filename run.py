# Call Module
import os
import sys
import sqlite3
import zipfile
from bs4 import BeautifulSoup
from selenium import webdriver
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5 import uic
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import * 
from requests import get
from pathlib import Path
import pandas as pd
from datetime import datetime

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

# Check Os
import platform
global check_os
check_os = platform.system()
if check_os == "Linux" : 
    check_os = "Linux"
elif check_os == "Windows" :
    check_os = "Windows"
else :
    check_os = "Error"

# Check Chrome Version
global chrome_vesrion
if check_os == "Windows" :
    try :
        try :
            chrome_version = os.listdir('C:/Program Files (x86)/Google/Chrome/Application/')[0]
            log("Chrome Version : " + str(chrome_version))
        except :
            chrome_version = os.listdir('C:/Program Files/Google/Chrome/Application/')[0]
            log("Chrome Version : " + str(chrome_version))
        chrome_check = 1
    except :
        chrome_check = 0
    fileObj = Path("chromedriver.exe")
    if fileObj.is_file() == True :
        check = 1
    else :
        check = 0
elif check_os == "Linux" :
    try :
        chrome_version = os.popen("google-chrome --version").read()
        chrome_version = (chrome_version[14:16])
        chrome_check = 1
    except :
        chrome_check = 0
    fileObj = Path("chromedriver")
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
            chrome_version_url = 'https://chromedriver.storage.googleapis.com/' + chrome_version + '/chromedriver_win32.zip'
            download(chrome_version_url, "chromedriver.zip")
            log("Download Chromedriver Version " + chrome_version)
            zipfile.ZipFile('chromedriver.zip').extract('chromedriver.exe')
            log("Unziped Chromedriver.zip")

        elif check == 1 :
            log("Chromedriver is installed")
        
        self.setupUi(self)
        self.setWindowIcon(QIcon('src\icon.ico')) # Icon setting

        # Auto login check file (user.db)
        global auto_login_check
        auto_login_check = 0
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
                auto_login_check = 1
        except :
            pass

        # Login Buttons
        self.login_button.clicked.connect(self.login)
        self.login_id.returnPressed.connect(self.listener_login_id)
        self.login_pw.returnPressed.connect(self.listener_login_pw)
    

    def listener_login_id(self) :
        self.login()

    def listener_login_pw(self) :
        self.login()
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
            global driver
            if check_os == "Windows" :
                ''' Windows '''
                args = ["hide_console", ]
                options = webdriver.ChromeOptions()
                options.add_argument('headless')
                options.add_argument('window-size=1920x1080')
                options.add_argument("disable-gpu")
                driver = webdriver.Chrome('chromedriver.exe', service_args=args, chrome_options=options) # Run chromedriver.exe
                # driver = webdriver.Chrome('chromedriver.exe') # Run chromedriver.exe
            elif check_os == "Linux" :
                ''' Linux '''
                cwd = os.getcwd() + "/chromedriver"
                print(cwd)
                chrome_options = webdriver.ChromeOptions()
                chrome_options.add_argument('--headless')
                chrome_options.add_argument('--no-sandbox')
                chrome_options.add_argument('--disable-dev-shm-usage')
                driver = webdriver.Chrome(executable_path=cwd,chrome_options=chrome_options)
            
            try : 
                log("Webdriver > Try to run Chrome")
                QMessageBox.information(self, 'Notice', '모든 강의를 확인하기 때문에 시간이 소요될수 있습니다.', QMessageBox.Ok, QMessageBox.Ok)
            except :
                QMessageBox.warning(self, 'File Error', 'chromedriver.exe 파일을 찾을수 없습니다.', QMessageBox.Ok, QMessageBox.Ok)
                log("Webdriver > Does not exist chromedriver.exe")
                return
            
            class_url = "https://cyber.jj.ac.kr/local/ubion/user/index.php?year=2022&semester=10"
            login_url = "https://cyber.jj.ac.kr/login.php"

            student_id = (self.login_id.text())
            student_pw = (self.login_pw.text())
        
            # Login Page
            driver.get(login_url) # Open Login Page
            log("Webdriver > Access Url > https://cyber.jj.ac.kr/login.php")
            driver.find_element_by_name('username').send_keys(student_id) # Send ID
            driver.find_element_by_name('password').send_keys(student_pw) # Send Password
            driver.find_element_by_xpath('//*[@id="region-main"]/div/form/div[2]/input').click() # Button Click
            log("Webdriver > Try to Login")

            # user info Page
            driver.get(class_url) # Open User Info Page
            log("Webdriver > Access Url > https://cyber.jj.ac.kr/local/ubion/user/index.php")

            html = driver.page_source
            soup = BeautifulSoup(html, 'lxml')

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
                    if reply == QMessageBox.Yes :
                        try :
                            auto_login(student_id, student_pw)
                        except :
                            QMessageBox.warning(self, '자동 로그인', '이미 자동로그인 기능이 활성화 되어 있습니다.', QMessageBox.Ok, QMessageBox.Ok)
                else :
                    pass

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
                    class_process_url = "https://cyber.jj.ac.kr/report/ubcompletion/user_progress.php?id=" + class_id[i]
                    driver.get(class_process_url)
                    log("Webdriver > Access Url > " + str(class_process_url))
                    html = driver.page_source
                    soup = BeautifulSoup(html, 'lxml')

                    time_url = "https://cyber.jj.ac.kr/course/view.php?id=" + class_id[i]
                    driver.get(time_url)
                    html_time = driver.page_source
                    soup_time = BeautifulSoup(html_time, 'lxml')
                    deadline = soup_time.find_all(class_="text-ubstrap")
                    try :
                        data = soup.find("table",{"class":"table table-bordered user_progress table-coursemos"})
                        table_html = str(data)
                        table_df_list = pd.read_html(table_html)
                        table_df_list[0] = table_df_list[0].dropna(how = "any")
                        for j in range(100):
                            try :
                                title = (table_df_list[0]['강의 자료'][j])
                                need_time = (table_df_list[0]['콘텐츠 길이'][j])
                                my_time = (table_df_list[0]['최대 학습위치'][j][:-8])
                                if my_time == "" :
                                    my_time = "미수강"
                                check = (table_df_list[0]['진도율'][j])
                                if check == "-" :
                                    check = "X"
                                try : 
                                    deadline_txt = str(deadline[j])[50:60]
                                except Exception as e:
                                    deadline_txt = "Error"
                                try :
                                    now  = datetime.now()
                                    compare_time = datetime.strptime(deadline_txt, "%Y-%m-%d")
                                    date_diff = compare_time - now
                                    date_diff = date_diff.days + 1
                                    if date_diff < 0 :
                                        date_diff = "Timeout"
                                except :
                                    date_diff = "Error"
                                class_detail.append([class_name, title, need_time, my_time, deadline_txt, date_diff, check])
                            except Exception as e:
                                j += 1
                    except :
                        pass

                # Call Main Window
                self.management = MainWindow()
                self.management.show()
                self.close()


class AlignDelegate(QtWidgets.QStyledItemDelegate):
    def initStyleOption(self, option, index):
        super(AlignDelegate, self).initStyleOption(option, index)
        option.displayAlignment = QtCore.Qt.AlignCenter

# Call ui(main.ui) File
ui_main_path = "src/main.ui"
ui_main = uic.loadUiType(ui_main_path)[0]

# Call Gui Enviroment (MainWindow)
class MainWindow(QMainWindow, ui_main):
    def __init__(self):
        log("*** Open MainWindow ***")
        super().__init__()
        self.setupUi(self)

        # Show Date
        self.date = QDate.currentDate()
        self.statusBar.showMessage(str("오늘 날짜 : " + self.date.toString(Qt.DefaultLocaleLongDate)))
        
        self.setWindowIcon(QIcon('src\icon.ico'))

        # Item Double Clicked Function
        self.class_listWidget.itemDoubleClicked.connect(self.class_ItemDoubleClicked)
        # self.tableWidget.cellDoubleClicked.connect(self.table_ItemDoubleClicked)

        # Button
        self.message_button.clicked.connect(self.message)
        self.assign_button.clicked.connect(self.assign)
        self.video_chat_button.clicked.connect(self.video_chat)
        self.exit_button.clicked.connect(self.exit)

        # Logo
        self.logo_label.setPixmap(QPixmap('src\logo.jpg'))


        #Get User Infomormation
        get_user_url = "https://cyber.jj.ac.kr/report/ubcompletion/user_progress_a.php?id=" + class_id[0]
        driver.get(get_user_url)
        log("Webdriver > Access Url > " + str(get_user_url))
        
        html = driver.page_source
        soup = BeautifulSoup(html, 'lxml')

        # Get School User ID
        school_id = driver.find_element_by_xpath('//*[@id="ubcompletion-progress-wrapper"]/div[1]/table/tbody/tr[1]/td').text
        global user_school_id
        user_school_id = school_id
        self.school_number_line.setText(str(user_school_id))
        log("Webdriver > Get Informtaion > " + str(user_school_id))

        # Get User Name
        global user_name
        user_name = driver.find_element_by_xpath('//*[@id="ubcompletion-progress-wrapper"]/div[1]/table/tbody/tr[2]/td').text
        self.name_line.setText(str(user_name))
        log("Webdriver > Get Informtaion > " + str(user_name))

        # Get User Phone Number
        phone_number = driver.find_element_by_xpath('//*[@id="ubcompletion-progress-wrapper"]/div[1]/table/tbody/tr[3]/td').text
        global user_phone_number
        user_phone_number = phone_number
        self.phone_number_line.setText(str(user_phone_number))
        log("Webdriver > Get Informtaion > " + str(user_phone_number))

        for i in range(len(class_all)) :
            self.class_listWidget.addItem(class_all[i][0])

        # QtableWidget - Class Table
        _translate = QCoreApplication.translate
        self.tableWidget.setColumnCount(7)
        self.tableWidget.setRowCount(len(class_detail))

        for i in range(len(class_detail)):
            item = QTableWidgetItem()
            self.tableWidget.setVerticalHeaderItem(i, item)

        for i in range(7):
            item = QTableWidgetItem()
            self.tableWidget.setHorizontalHeaderItem(i, item)
        item = QTableWidgetItem()

        for i in range(len(class_detail)):
            for j in range(7):
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
        item.setText(_translate("MainWindow", "마감일"))
        item = self.tableWidget.horizontalHeaderItem(5)
        item.setText(_translate("MainWindow", "잔여"))
        item = self.tableWidget.horizontalHeaderItem(6)
        item.setText(_translate("MainWindow", "통과"))
        __sortingEnabled = self.tableWidget.isSortingEnabled()
        self.tableWidget.setSortingEnabled(False)

        self.tableWidget.setColumnWidth(0, 200)
        self.tableWidget.setColumnWidth(1, 300)
        self.tableWidget.setColumnWidth(2, 65)
        self.tableWidget.setColumnWidth(3, 65)
        self.tableWidget.setColumnWidth(4, 100)
        self.tableWidget.setColumnWidth(5, 65)
        self.tableWidget.verticalHeader().setVisible(False)

        for i in range(len(class_detail)):
            for j in range(7):
                item = self.tableWidget.item(i, j)
                item.setFlags(QtCore.Qt.ItemIsEnabled) # Locked Cell
                if str(class_detail[i][j]) == "미수강" or str(class_detail[i][j]) == "X":
                    item.setForeground(QBrush(Qt.red))
                    item.setBackground(QBrush(Qt.yellow))
                    item.setText(_translate("MainWindow", str(class_detail[i][j])))
                else :
                    item.setText(_translate("MainWindow", str(class_detail[i][j])))
        self.tableWidget.setSortingEnabled(__sortingEnabled)
        self.tableWidget.setSortingEnabled(True)
        self.tableWidget.sortItems(0, QtCore.Qt.AscendingOrder)
        delegate = AlignDelegate(self.tableWidget)
        self.tableWidget.setItemDelegate(delegate)

    # Call Assign Function
    def assign(self):
        log("*** Get Assignment ***")
        QMessageBox.information(self, "과제 확인", "과제를 확인하는데 시간이 소요될수 있습니다.", QMessageBox.Ok, QMessageBox.Ok)
        global assign
        assign = []
        for i in range(len(class_id)) :
            class_name = class_all[i][0]
            class_assign_url = "https://cyber.jj.ac.kr/mod/assign/index.php?id=" + class_id[i]
            driver.get(class_assign_url) # Open Class Assign Page
            log("Webdriver > Access Url > " + str(class_assign_url))
            try :
                html = driver.page_source
                soup = BeautifulSoup(html, 'lxml')
                data = soup.find("table",{"class":"generaltable"})
                table_html = str(data)
                table_df_list = pd.read_html(table_html)
                table_df_list[0] = table_df_list[0].dropna(how = "any")
                for j in range(100):
                    try :
                        class_title = class_name
                        title = (table_df_list[0]['주제'][j])
                        subject = (table_df_list[0]['과제'][j])
                        deadline = (table_df_list[0]['종료 일시'][j])
                        check = (table_df_list[0]['제출'][j])
                        scroe = (table_df_list[0]['성적'][j])
                        assign.append([class_title, title, subject, deadline, check, scroe])
                    except Exception as e:
                        j += 1
            except Exception as e :
                pass
                # print(e)
        
        # Call Assign Window
        self.assignment = AssignWindow()
        self.assignment.show()

    # Call Video Chat Function
    def video_chat(self):
        log("*** Get Video Chat ***")
        QMessageBox.information(self, "화상강의 확인", "화상강의를 확인하는데 시간이 소요될수 있습니다.", QMessageBox.Ok, QMessageBox.Ok)
        global webex_detail
        webex_detail = []
        for i in range(len(class_id)) :
            class_name = class_all[i][0]
            webexactivity = "https://cyber.jj.ac.kr/mod/webexactivity/index.php?id=" + class_id[i]
            driver.get(webexactivity)
            log("Webdriver > Access Url > " + str(webexactivity))
            html = driver.page_source
            soup = BeautifulSoup(html, 'lxml')
            try :
                data = soup.find("table",{"class":"generaltable"})
                table_html = str(data)
                table_df_list = pd.read_html(table_html)
                for j in range(100):
                    try :
                        subject = (table_df_list[0]['주제'][j])
                        title = (table_df_list[0]['제목'][j])
                        start_time = (table_df_list[0]['시작 시간'][j])
                        recordings = (table_df_list[0]['Recordings'][j])
                        webex_detail.append([subject, title, start_time, recordings])
                    except Exception as e:
                        j += 1
            except Exception as e:
                pass
            #     table_df_list[0] = table_df_list[0].dropna(how = "any")
            #     for j in range(100):
            #         try :
            #             title = (table_df_list[0]['강의 자료'][j])
            #             need_time = (table_df_list[0]['콘텐츠 길이'][j])
            #             my_time = (table_df_list[0]['최대 학습위치'][j][:-8])
            #             if my_time == "" :
            #                 my_time = "미수강"
            #             check = (table_df_list[0]['진도율'][j])
            #             if check == "-" :
            #                 check = "X"
            #             try : 
            #                 deadline_txt = str(deadline[j])[50:60]
            #             except Exception as e:
            #                 deadline_txt = "Error"
            #             try :
            #                 now  = datetime.now()
            #                 compare_time = datetime.strptime(deadline_txt, "%Y-%m-%d")
            #                 date_diff = compare_time - now
            #                 date_diff = date_diff.days + 1
            #                 if date_diff < 0 :
            #                     date_diff = "Timeout"
            #             except :
            #                 date_diff = "Error"
            #             class_detail.append([class_name, title, need_time, my_time, deadline_txt, date_diff, check])
            #         except Exception as e:
            #             j += 1
            # except :
            #     pass
        # Call Grade Window
        self.video_chat = Video_Chat_Window()
        self.video_chat.show()

    # Call New Message Window
    def message(self):
        try :
            self.new_message = MessageWindow()
            self.new_message.show()
        except :
            QMessageBox.warning(self, '오류', '메시지를 불러오는데 오류가 발생하였습니다.', QMessageBox.Ok, QMessageBox.Ok)

    def class_ItemDoubleClicked(self) :
        log("DoubleClick > Class Detail")
        row = self.class_listWidget.currentRow()
        class_number = class_all[row][1][-5:]
        global class_detail_select
        class_detail_select = []
        
        class_name = class_all[row][0]
        class_process_url = "https://cyber.jj.ac.kr/report/ubcompletion/user_progress.php?id=" + class_number
        driver.get(class_process_url)
        log("Webdriver > Access Url > " + str(class_process_url))
        html = driver.page_source
        soup = BeautifulSoup(html, 'lxml')
        time_url = "https://cyber.jj.ac.kr/course/view.php?id=" + class_number
        driver.get(time_url)
        html_time = driver.page_source
        soup_time = BeautifulSoup(html_time, 'lxml')
        deadline = soup_time.find_all(class_="text-ubstrap")
        
        try :
            data = soup.find("table",{"class":"table table-bordered user_progress table-coursemos"})
            table_html = str(data)
            table_df_list = pd.read_html(table_html)
            table_df_list[0] = table_df_list[0].dropna(how = "any")
            for j in range(100):
                try :
                    title = (table_df_list[0]['강의 자료'][j])
                    need_time = (table_df_list[0]['콘텐츠 길이'][j])
                    my_time = (table_df_list[0]['최대 학습위치'][j][:-8])
                    if my_time == "" :
                        my_time = "미수강"
                    check = (table_df_list[0]['진도율'][j])
                    if check == "-" :
                        check = "X"
                    deadline_txt = str(deadline[j-1])[50:61]
                    
                    class_detail_select.append([class_name, title, need_time, my_time, deadline_txt, check])
                except Exception as e:
                    # print(e)
                    pass
        except :
            pass
        self.select_class = SelectClass()
        self.select_class.show()
    # Exit Function (Close Program)
    def exit(self) :
        log("*** Exit Program ***")
        self.close()


# Call ui(message.ui) File
ui_message_path = "src/message.ui"
ui_message = uic.loadUiType(ui_message_path)[0]

# Call Gui Enviroment (MessageWindow)
class MessageWindow(QMainWindow, ui_message):
    def __init__(self):
        log("*** Open Message Window ***")
        super().__init__()
        self.setupUi(self)
        self.setWindowIcon(QIcon('src\icon.ico'))

        self.notice_listWidget.itemDoubleClicked.connect(self.notice_ItemDoubleClicked)

        # Button - Exit
        self.exit_button.clicked.connect(self.exit)


        notice_url = "https://cyber.jj.ac.kr/local/ubnotification/"
        driver.get(notice_url) # Open Notice Page
        log("Webdriver > Access Url > https://cyber.jj.ac.kr/local/ubnotification/")
        html = driver.page_source
        soup = BeautifulSoup(html, 'lxml')

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
            try :
                try :
                    name = soup.find_all(class_="media-heading")[i].get_text()
                except :
                    name = "Error"
                try :
                    timeago = (soup.find_all(class_="timeago")[i].get_text())
                except :
                    timeago = "Error"
                try :
                    message = str(soup.find_all(class_="media-body")[i])
                except :
                    message = "Error"
                try :
                    message = message.partition("<p>")[-1].replace("</p></div>","")
                except :
                    message = "Error"
                log("Webdriver > Parse > Notice > " + str([name, timeago, message, notice_url_value[i]]))
                notice_value.append([name, timeago, message, notice_url_value[i]])
            except :
                notice_value.append(["Error", "Error", 'Error', "Error"])
        notice_value.pop()
        notice_value.pop()
        for i in range(len(notice_value)) :
            self.notice_listWidget.addItem(notice_value[i][0])

    def notice_ItemDoubleClicked(self) :
        get_notice_url = notice_value[self.notice_listWidget.currentRow()][3]
        driver.get(get_notice_url)
        log("DoubleClick > Notice > " + str([notice_value[self.notice_listWidget.currentRow()][0], notice_value[self.notice_listWidget.currentRow()][1], notice_value[self.notice_listWidget.currentRow()][2], notice_value[self.notice_listWidget.currentRow()][3]]))
        html = driver.page_source
        soup = BeautifulSoup(html, 'lxml')
        title = self.notice_listWidget.currentItem().text()
        message = "작성시간 : " + str(notice_value[self.notice_listWidget.currentRow()][1]) + "\n"  + str(notice_value[self.notice_listWidget.currentRow()][2])
        QMessageBox.information(self, title, message, QMessageBox.Ok, QMessageBox.Ok)

    # Exit Function (Close Message Window)
    def exit(self) :
        log("*** Exit Message Window ***")
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
        item.setText(_translate("MainWindow", "과목"))
        item = self.assign_tableWidget.horizontalHeaderItem(1)
        item.setText(_translate("MainWindow", "주제"))
        item = self.assign_tableWidget.horizontalHeaderItem(2)
        item.setText(_translate("MainWindow", "과제"))
        item = self.assign_tableWidget.horizontalHeaderItem(3)
        item.setText(_translate("MainWindow", "종료 일시"))
        item = self.assign_tableWidget.horizontalHeaderItem(4)
        item.setText(_translate("MainWindow", "제출"))
        item = self.assign_tableWidget.horizontalHeaderItem(5)
        item.setText(_translate("MainWindow", "성적"))
        __sortingEnabled = self.assign_tableWidget.isSortingEnabled()
        self.assign_tableWidget.setSortingEnabled(False)

        self.assign_tableWidget.setColumnWidth(0, 170)
        self.assign_tableWidget.setColumnWidth(1, 160)
        self.assign_tableWidget.setColumnWidth(2, 200)
        self.assign_tableWidget.setColumnWidth(3, 120)
        self.assign_tableWidget.setColumnWidth(4, 60)
        self.assign_tableWidget.setColumnWidth(5, 60)

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

# Call ui(video_chat.ui) File
ui_video_chat_path = "src/video_chat.ui"
ui_video = uic.loadUiType(ui_video_chat_path)[0]

# Call Gui Enviroment (Video Chat Window)
class Video_Chat_Window(QMainWindow, ui_video):
    def __init__(self):
        log("*** Open Video Chat Window ***")
        super().__init__()
        self.setupUi(self)
        self.setWindowIcon(QIcon('src\icon.ico'))

        # Button - Exit
        self.exit_button.clicked.connect(self.exit)

        # QtableWidget - Grade Table
        _translate = QCoreApplication.translate
        self.grade_tableWidget.setColumnCount(4)
        self.grade_tableWidget.setRowCount(len(webex_detail))
        self.grade_tableWidget.verticalHeader().setVisible(False)

        for i in range(len(webex_detail)):
            item = QTableWidgetItem()
            self.grade_tableWidget.setVerticalHeaderItem(i, item)

        for i in range(4):
            item = QTableWidgetItem()
            self.grade_tableWidget.setHorizontalHeaderItem(i, item)
        item = QTableWidgetItem()

        for i in range(len(webex_detail)):
            for j in range(4):
                self.grade_tableWidget.setItem(i, j, item)
                item = QTableWidgetItem()

        for i in range(len(webex_detail)) :
            item = self.grade_tableWidget.verticalHeaderItem(i)
            item.setText(_translate("MainWindow", str(i)))

        item = self.grade_tableWidget.horizontalHeaderItem(0)
        item.setText(_translate("MainWindow", "주제"))
        item = self.grade_tableWidget.horizontalHeaderItem(1)
        item.setText(_translate("MainWindow", "제목"))
        item = self.grade_tableWidget.horizontalHeaderItem(2)
        item.setText(_translate("MainWindow", "시작 시간"))
        item = self.grade_tableWidget.horizontalHeaderItem(3)
        item.setText(_translate("MainWindow", "Recordings"))
        __sortingEnabled = self.grade_tableWidget.isSortingEnabled()
        self.grade_tableWidget.setSortingEnabled(False)

        self.grade_tableWidget.setColumnWidth(0, 200)
        self.grade_tableWidget.setColumnWidth(1, 280)
        self.grade_tableWidget.setColumnWidth(2, 150)
        self.grade_tableWidget.setColumnWidth(4, 55)
 
        for i in range(len(webex_detail)):
            for j in range(4):
                item = self.grade_tableWidget.item(i, j)
                item.setFlags(QtCore.Qt.ItemIsEnabled) # Locked Cell
                item.setText(_translate("MainWindow", str(webex_detail[i][j])))
        self.grade_tableWidget.setSortingEnabled(__sortingEnabled)
    
    # Exit Function (Close Video Chat Window)
    def exit(self) :
        log("*** Exit Video Chat Window ***")
        self.close()

# Call ui(select_class.ui) File
ui_select_class_path = "src/select_class.ui"
ui_select_class = uic.loadUiType(ui_select_class_path)[0]

# Call Gui Enviroment (Select Class Window)
class SelectClass(QMainWindow, ui_select_class):
    def __init__(self):
        log("*** Open Select Class Window ***")
        super().__init__()
        self.setupUi(self)
        self.setWindowIcon(QIcon('src\icon.ico'))

        # Button - Exit
        self.exit_button.clicked.connect(self.exit)

        # QtableWidget - Select Class Table
        _translate = QCoreApplication.translate
        self.tableWidget.setColumnCount(6)
        self.tableWidget.setRowCount(len(class_detail_select))

        for i in range(len(class_detail_select)):
            item = QTableWidgetItem()
            self.tableWidget.setVerticalHeaderItem(i, item)

        for i in range(6):
            item = QTableWidgetItem()
            self.tableWidget.setHorizontalHeaderItem(i, item)
        item = QTableWidgetItem()

        for i in range(len(class_detail_select)):
            for j in range(6):
                self.tableWidget.setItem(i, j, item)
                item = QTableWidgetItem()

        for i in range(len(class_detail_select)) :
            item = self.tableWidget.verticalHeaderItem(i)
            item.setText(_translate("MainWindow", str(i)))

        item = self.tableWidget.horizontalHeaderItem(0)
        item.setText(_translate("MainWindow", "강의 이름"))
        item = self.tableWidget.horizontalHeaderItem(1)
        item.setText(_translate("MainWindow", "강의 제목"))
        item = self.tableWidget.horizontalHeaderItem(2)
        item.setText(_translate("MainWindow", "요구"))
        item = self.tableWidget.horizontalHeaderItem(3)
        item.setText(_translate("MainWindow", "학습"))
        item = self.tableWidget.horizontalHeaderItem(4)
        item.setText(_translate("MainWindow", "마감일"))
        item = self.tableWidget.horizontalHeaderItem(5)
        item.setText(_translate("MainWindow", "통과"))
        __sortingEnabled = self.tableWidget.isSortingEnabled()
        self.tableWidget.setSortingEnabled(False)

        self.tableWidget.setColumnWidth(0, 130)
        self.tableWidget.setColumnWidth(1, 180)
        self.tableWidget.setColumnWidth(2, 55)
        self.tableWidget.setColumnWidth(3, 55)
        self.tableWidget.setColumnWidth(4, 280)
        self.tableWidget.setColumnWidth(5, 50)
        self.tableWidget.verticalHeader().setVisible(False)

        for i in range(len(class_detail_select)):
            for j in range(6):
                item = self.tableWidget.item(i, j)
                item.setFlags(QtCore.Qt.ItemIsEnabled) # Locked Cell
                if str(class_detail_select[i][j]) == "미수강" or str(class_detail_select[i][j]) == "X":
                    item.setForeground(QBrush(Qt.red))
                    item.setBackground(QBrush(Qt.yellow))
                    item.setText(_translate("MainWindow", str(class_detail_select[i][j])))
                else :
                    item.setText(_translate("MainWindow", str(class_detail_select[i][j])))
        self.tableWidget.setSortingEnabled(__sortingEnabled)
        self.tableWidget.setSortingEnabled(True)
        self.tableWidget.sortItems(0, QtCore.Qt.AscendingOrder)
        delegate = AlignDelegate(self.tableWidget)
        self.tableWidget.setItemDelegate(delegate)
    
    # Exit Function (Close Select Class Window)
    def exit(self) :
        log("*** Exit Select Class Window ***")
        self.close()

# Main Function
def main():
    app = QApplication(sys.argv)
    window = LoginWindow()
    window.show()
    app.exec_()

if __name__ == "__main__":
    main()