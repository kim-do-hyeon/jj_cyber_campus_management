import os
import re
import sys
import webbrowser
from bs4 import BeautifulSoup
from selenium import webdriver
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5 import uic
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import * 

def timestamp():
    import datetime
    return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

def log(message): # LOG
            message = timestamp() + ' > ' + message
            print(message, file=log_file)

log_file = open("log.txt", 'w', -1, 'utf-8')
log("*** Start Program ***")
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
            log("Login > School id is blank")
        elif self.login_pw.text() == "" : # passwrod is blank
            QMessageBox.information(self, '로그인', '비밀번호를 입력해 주세요.', QMessageBox.Ok, QMessageBox.Ok)
            log("Login > School Password is blank")
        else : # login
            student_id = (self.login_id.text())
            student_pw = (self.login_pw.text())
            log("Login > Try Login")
            
            options = webdriver.ChromeOptions()
            options.add_argument('headless')
            options.add_argument('window-size=1920x1080')
            options.add_argument("disable-gpu")
            log("Webdriver > headless, window-size=1920x1080, disable-gpu options")

            global driver
            try : 
                driver = webdriver.Chrome('chromedriver.exe', chrome_options=options)
                log("Webdriver > Try to run Chrome")
            except :
                QMessageBox.warning(self, 'File Error', 'chromedriver.exe 파일을 찾을수 없습니다.', QMessageBox.Ok, QMessageBox.Ok)
                log("Webdriver > Does not exist chromedriver.exe")
                return
            
            login_url = "https://cyber.jj.ac.kr/login.php"
            class_url = "http://cyber.jj.ac.kr/local/ubion/user/"

            # login Page
            driver.get(login_url)
            log("Webdriver > Access Url > https://cyber.jj.ac.kr/login.php")
            driver.find_element_by_name('username').send_keys(student_id) # Send ID
            driver.find_element_by_name('password').send_keys(student_pw) # Send Password
            driver.find_element_by_xpath('/html/body/div[2]/div[2]/div/div/div/div/div[1]/div[1]/div[1]/form/div[2]/input').click() # Button Click
            log("Webdriver > Try to Login")

            # user info Page
            driver.get(class_url)
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

            if class_all == [] : # 강의가 없다면 로그인 실패
                QMessageBox.warning(self, '로그인 실패', '학번 또는 비밀번호를 확인해 주세요.', QMessageBox.Ok, QMessageBox.Ok)
                log("*** Login Fail ***")
            else :
                QMessageBox.information(self, '로그인 성공', '모든 강의를 확인하기 때문에 시간이 소요될수 있습니다.', QMessageBox.Ok, QMessageBox.Ok)
                log("*** Login Success ***")
                log("*** Get Notice ***")
                notice_url = "http://cyber.jj.ac.kr/local/ubnotification/"
                driver.get(notice_url)
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

                for i in range(len(notice_url_value)):
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

                # 강의 정보 (수강 시간 등)
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
                            log("Webdriver > Parse > Class Detail > " + str([class_name, title, need_time, my_time, class_process_url]))
                            class_detail.append([class_name, title, need_time, my_time, class_process_url])
                        except :
                            log("Webdriver > Parse > Class Detail > Error (No Videos)")
                            break
                # 강의 시청 링크
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

                self.management = MainWindow()
                self.management.show()
                self.close()

ui_main_path = "src/main.ui"
ui_main = uic.loadUiType(ui_main_path)[0]
class MainWindow(QMainWindow, ui_main):
    def __init__(self):
        log("*** Open MainWindow ***")
        super().__init__()
        self.setupUi(self)
        self.setWindowIcon(QIcon('src\icon.ico'))
        self.notice_listWidget.itemDoubleClicked.connect(self.notice_ItemDoubleClicked)
        self.class_listWidget.itemDoubleClicked.connect(self.class_ItemDoubleClicked)
        self.tableWidget.cellDoubleClicked.connect(self.table_ItemDoubleClicked)

        # Button
        self.assign_button.clicked.connect(self.assign)
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
        # School user id
        school_id = str(soup.select("#ubcompletion-progress-wrapper > div:nth-child(1) > table > tbody > tr:nth-child(1) > td"))
        regex = re.compile('{}(.*){}'.format(re.escape('<td class="text-left">'), re.escape('</td>')))
        global user_school_id
        user_school_id = regex.findall(school_id)[0]
        self.school_number_line.setText(str(user_school_id))
        log("Webdriver > Get Informtaion > " + str(user_school_id))

        # User Name
        name = str(soup.select("#ubcompletion-progress-wrapper > div:nth-child(1) > table > tbody > tr:nth-child(2) > td"))
        regex = re.compile('{}(.*){}'.format(re.escape('<td class="text-left">'), re.escape('</td>')))
        global user_name
        user_name = regex.findall(name)[0]
        self.name_line.setText(str(user_name))
        log("Webdriver > Get Informtaion > " + str(user_name))

        # User Phone Number
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
        self.tableWidget.setColumnWidth(2, 65)
        self.tableWidget.setColumnWidth(3, 65)
            
        for i in range(len(class_detail)):
            for j in range(4):
                item = self.tableWidget.item(i, j)
                item.setFlags(QtCore.Qt.ItemIsEnabled) # Locked Cell
                item.setText(_translate("MainWindow", str(class_detail[i][j])))
        self.tableWidget.setSortingEnabled(__sortingEnabled)

    def assign(self):
        log("*** Get Assignment ***")
        QMessageBox.information(self, "과제 확인", "과제를 확인하는데 시간이 소요될수 있습니다.", QMessageBox.Ok, QMessageBox.Ok)
        global assign
        assign = []
        for i in range(len(class_id)) :
            class_name = class_all[i][0]
            class_assign_url = "http://cyber.jj.ac.kr/mod/assign/index.php?id=" + class_id[i]
            driver.get(class_assign_url)
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
        self.assignment = AssignWindow()
        self.assignment.show()

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

    def exit(self) :
        log("*** Exit Program ***")
        self.close()

ui_assign_path = "src/assign.ui"
ui_assign = uic.loadUiType(ui_assign_path)[0]
class AssignWindow(QMainWindow, ui_assign):
    def __init__(self):
        log("*** Open Assinment Window ***")
        super().__init__()
        self.setupUi(self)
        self.setWindowIcon(QIcon('src\icon.ico'))

        # Button - Exit
        self.exit_button.clicked.connect(self.exit)

        _translate = QCoreApplication.translate
        self.assign_tableWidget.setColumnCount(6)
        self.assign_tableWidget.setRowCount(len(assign))
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

        for i in range(len(assign)):
            for j in range(6):
                item = self.assign_tableWidget.item(i, j)
                item.setFlags(QtCore.Qt.ItemIsEnabled) # Locked Cell
                item.setText(_translate("MainWindow", str(assign[i][j])))
        self.assign_tableWidget.setSortingEnabled(__sortingEnabled)

    def exit(self) :
        log("*** Exit Assignment Window ***")
        self.close()

ui_error_path = "src/error.ui"
ui_error = uic.loadUiType(ui_error_path)[0]
class ErrorWindow(QMainWindow, ui_error):
    def __init__(self):
        log("*** Open Error Report Window ***")
        super().__init__()
        self.setupUi(self)
        self.setWindowIcon(QIcon('src\icon.ico'))

        # Button
        self.send_button.clicked.connect(self.send)

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

    def send(self) :

        import socket
        import re, uuid
        User_Host_Name = socket.gethostname()
        User_IP_Internal = socket.gethostbyname(socket.gethostname())
        User_IP_External = socket.gethostbyname(socket.getfqdn())
        User_Mac = ':'.join(re.findall('..', '%012x' % uuid.getnode()))
        User_Computer_Information = [User_Host_Name, User_IP_Internal, User_IP_External, User_Mac]

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
                contact = [user_school_id, user_name, user_phone_number]
            else :
                contact = "익명"
        except :
            QMessageBox.information(self, "오류제보", "작성자 공개 여부를 체크해주세요.", QMessageBox.Ok, QMessageBox.Ok)
            log("Error Report > Send > Error Disclosure_status")
            return

        user_contact = self.contact_message.toPlainText()
        if user_contact == "" :
            user_contact = "익명"
        
        content = content + "\n\n" + str(contact) + "\n\n" + str(user_contact) + "\n\n" + str(User_Computer_Information)
        try :
            import smtplib
            from email.mime.text import MIMEText
            s = smtplib.SMTP('smtp.gmail.com', 587)
            s.starttls()
            s.login('pental.system32@gmail.com', 'emwqpqjkhjbeoern')
            msg = MIMEText(content)
            msg['Subject'] = title
            s.sendmail("pental.system32@gmail.com", "pental@kakao.com", msg.as_string())
            s.quit()
            log("Error Report > Send > Success")
            QMessageBox.information(self, "오류제보", "오류제보가 정상적으로 처리되었습니다.", QMessageBox.Ok, QMessageBox.Ok)
        except :
            log("Error Report > Send > Fail")
            QMessageBox.information(self, "오류제보", "문제가 발생하였습니다.", QMessageBox.Ok, QMessageBox.Ok)

def main():
    app = QApplication(sys.argv)
    window = LoginWindow()
    window.show()
    app.exec_()

if __name__ == "__main__":
    main()