import requests
from bs4 import BeautifulSoup
import pandas as pd
import datetime

url ="https://cyber.jj.ac.kr/login/index.php"

id = "***"
pw = "**"
payload = {'username':id, 'password':pw}

s = requests.Session()
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'
}
s.headers.update(headers)
res = s.post(url, payload)
page= (s.get("https://cyber.jj.ac.kr/user/edit.php").content)
soup = BeautifulSoup(page, 'html.parser')
user = (soup.find_all(class_="form-control"))
for i in user :
    value = i.attrs['value']
    print(value)

course = s.get("https://cyber.jj.ac.kr/local/ubion/user/index.php?year=2022&semester=20").content
soup = BeautifulSoup(course, 'html.parser')

''' Get Course Link '''
link = soup.find_all(class_="coursefullname")
link_value = []
for i in link :
    value = i.attrs['href']
    link_value.append(value)

''' Get Course Title '''
data=(soup.find(class_="table table-bordered table-coursemos"))
table_html = str(data)
table_df_list = pd.read_html(table_html)
print(table_df_list)
class_detail = []
for i in link_value :
    url = "https://cyber.jj.ac.kr/report/ubcompletion/user_progress_a.php?id=" + str(i.split("=")[1])
    page= (s.get(url).content)
    soup = BeautifulSoup(page, 'html.parser')
    data = (soup.find(class_="table table-bordered user_progress_table table-coursemos"))
    table_html = str(data)
    table_df_list = pd.read_html(table_html)
    # table_df_list[0] = table_df_list[0].dropna(how = "any")
    value = []
    week = (table_df_list[0]['Unnamed: 0'])
    title = (table_df_list[0]['강의 자료'])
    need = (table_df_list[0]['출석인정 요구시간'])
    study = (table_df_list[0]['총 학습시간'])
    attendance = (table_df_list[0]['출석'])
    attendance_week = (table_df_list[0]['주차 출석'])
    for j in range(len(week)) :
        value_week = week[j]
        value_title = title[j]
        value_need = need[j]
        value_study = study[j]
        value_attendance = attendance[j]
        value_attendance_week = attendance_week[j]
        value.append([value_week, value_title, value_need, value_study, value_attendance, value_attendance_week])
    class_detail.append(value)
    class_url = "https://cyber.jj.ac.kr/course/view.php?id=" + str(i.split("=")[1])
    page = (s.get(class_url).content)
    soup = BeautifulSoup(page, 'html.parser')
    deadline = (soup.find_all(class_="text-ubstrap"))
    print(deadline)
    # break


print(class_detail)

