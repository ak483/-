# -*- codeing = utf-8 -*-
# @Time :2022/7/3 17:05
# @Author:Eric
# @File : 邮件自动发送.py
# @Software: PyCharm
import requests
from lxml import etree
import re
import pymysql
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import time
import datetime
import schedule
import time

while True:
    user = '****'
    pwd = '****'  # 邮箱的SMTP密码，看书第11章，申请很方便
    to = '1327928308@qq.com'  # 可以设置多个收件人，英文逗号隔开，如：'***@qq.com, ***@163.com'

    headers ={
        "User-Agent":'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'
    }

    db = pymysql.connect(host='**.**.***.*', port=3306, user=' ', password=' ', database=' ',
                         charset='utf8')
    company = '阿里巴巴'
    today = time.strftime("%Y-%m-%d")  # 这边采用标准格式的日期格式

    cur = db.cursor()  # 获取会话指针，用来调用SQL语句
    sql = 'SELECT * FROM test WHERE company = %s'
    cur.execute(sql, (company))
    data = cur.fetchall()  # 提取所有数据，并赋值给data变量

    db.commit()  # 这个其实可以不写，因为没有改变表结构
    cur.close()  # 关闭会话指针
    db.close()  # 关闭数据库链接

    mail_msg = []
    mail_msg.append('<p style="margin:0 auto">尊敬的小主，您好，以下是今天的舆情监控报告，望查阅：</p>')  # style="margin:0 auto"用来调节行间距
    mail_msg.append('<p style="margin:0 auto"><b>一、阿里巴巴舆情报告</b></p>')  # 加上<b>表示加粗
    for i in range(len(data)):
        href = '<p style="margin:0 auto"><a href="' + data[i][2] + '">' + str(i + 1) + '.' + data[i][1] + '</a></p>'
        mail_msg.append(href)

    mail_msg.append('<br>')  # <br>表示换行
    mail_msg.append('<p style="margin:0 auto">祝好</p>')
    mail_msg.append('<p style="margin:0 auto">椰子一号</p>')
    mail_msg = '\n'.join(mail_msg)

    # 3.添加正文内容
    msg = MIMEText(mail_msg, 'html', 'utf-8')

    # 4.设置邮件主题、发件人、收件人
    msg["Subject"] = "小椰舆情监控报告"
    msg["From"] = user
    msg["To"] = to

    # 5.发送邮件
    s = smtplib.SMTP_SSL('smtp.qq.com', 465)  # 选择qq邮箱服务，默认端口为465
    s.login(user, pwd)  # 登录qq邮箱
    s.send_message(msg)  # 发送邮件
    s.quit()  # 退出邮箱服务
    print('Success!')
    time.sleep(600)