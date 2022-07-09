# -*- codeing = utf-8 -*-
# @Time :2022/6/22 20:46
# @Author:Eric
# @File : 金融.py
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

# user = '1327928308@qq.com'
# pwd = 'imusrttythppijej'  # 邮箱的SMTP密码，看书第11章，申请很方便
# to = '1327928308@qq.com'  # 可以设置多个收件人，英文逗号隔开，如：'***@qq.com, ***@163.com'

headers ={
    "User-Agent":'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'
}

def baidu(company):

    url = 'https://www.baidu.com/s?rtt=1&bsst=1&cl=2&tn=news&ie=utf-8&word='+company
    res = requests.get(url=url, headers=headers).text
    tree = etree.HTML(res)
    div_list = tree.xpath('//*[@id="content_left"]/div')

    source = []
    date = []
    href = []
    title = []
    # 循环列表
    for div in div_list[1:]:
        # 来源
        source_t = div.xpath('./div/div/div[2]/div/a[1]/span/text()')
        if len(source_t) == 0:
            source_t = div.xpath('./div/div/div/div/a[1]/span/text()')
        source.append(source_t[0])
        # 时间
        date_t = div.xpath('./div/div/div[2]/span[1]/text()')
        if len(date_t) == 0:
            date_t = div.xpath('./div/div/div/span[1]/text()')
        date.append(date_t[0])
        # 链接
        href_t = div.xpath('./div/div/div/a[1]/@href')
        if len(href_t) == 0:
            href_t = div.xpath('./div/h3/a/@href')
        href.append(href_t[0])
        # 标题
        title_t = div.xpath('./div/h3/a/@aria-label')
        title_t = re.sub('标题：', '', str(title_t))
        title_t = title_t.split('\'')
        title.append(title_t[1])

    for i in range(len(source)):
        # 统一日期格式（参考5.1节）
        date[i] = re.sub('年', '-', date[i])
        date[i] = re.sub('月', '-', date[i])
        date[i] = re.sub('日', '', date[i])
        if ('小时前' in date[i])  or ('今天' in date[i])or ('分钟前' in date[i]):

            date[i] = time.strftime("%Y-%m-%d")

        elif ('昨天' in date[i]):
            today = datetime.date.today()
            yesterday = today - datetime.timedelta(days=1)
            date[i] = yesterday.strftime("%Y-%m-%d")

        elif ('前天' in date[i]):
            today = datetime.date.today()
            yesterday = today - datetime.timedelta(days=2)
            date[i] = yesterday.strftime("%Y-%m-%d")
        else:
            date[i] = date[i]


    score = []
    keywords = ['违约', '诉讼', '兑付', '阿里', '百度', '京东', '互联网']
    for i in range(len(title)):
        num = 0
        try:
            article = requests.get(href[i], headers=headers, timeout=10).text
        except:
            article = '爬取失败'

        try:
            article = article.encode('ISO-8859-1').decode('utf-8')
        except:
            try:
                article = article.encode('ISO-8859-1').decode('gbk')
            except:
                article = article
        p_article = '<p>(.*?)</p>'
        article_main = re.findall(p_article, article)  # 获取<p>标签里的正文信息
        article = ''.join(article_main)  # 将列表转换成为字符串
        for k in keywords:
            if (k in article) or (k in title[i]):
                num -= 5
        score.append(num)

     # 5.打印清洗后的数据（参考3.1节）
    for i in range(len(title)):
        print(str(i + 1) + '.' + title[i] + '(' + date[i] + ' ' + source[i] + ')')
        print(href[i])
        print(company + '该条新闻的舆情评分为' + str(score[i]))

    # 6.数据导入数据库及数据去重（参考4.4节和5.1节） ！为快速尝试，可以先把下面的内容注释掉，如果开启数据库后，可以取消注释运行
    for i in range(len(title)):
        db = pymysql.connect(host='182.61.132.25', port=3306, user='pycharm', password='5YtG5aztwDPLiEyy',database='pycharm', charset='utf8')
        cur = db.cursor()  # 获取会话指针，用来调用SQL语句

        # 6.1 查询数据，为之后的数据去重做准备
        sql_1 = 'SELECT * FROM article WHERE company =%s'
        cur.execute(sql_1, company)
        data_all = cur.fetchall()
        title_all = []
        for j in range(len(data_all)):
            title_all.append(data_all[j][1])

        # 6.2 判断数据是否在原数据库中，不在的话才进行数据存储
        if title[i] not in title_all:
            sql_2 = 'INSERT INTO article(company,title,href,source,date,score) VALUES (%s,%s,%s,%s,%s,%s)'  # 编写SQL语句
            cur.execute(sql_2, (company, title[i], href[i], source[i], date[i], score[i]))  # 执行SQL语句
            db.commit()  # 当改变表结构后，更新数据表的操作
        cur.close()  # 关闭会话指针
        db.close()  # 关闭数据库链接
print('------------------------------------')  # 分割符
while True:
    companys = ['阿里巴巴','腾讯']
    for company in companys:
        try:
            baidu(company)
            print(company + '数据爬取并导入数据库成功')
        except:
            print(company + '数据爬取并导入数据库失败')
    time.sleep(600)

# schedule.every(10).minutes.do()

# db = pymysql.connect(host='182.61.132.25', port=3306, user='pycharm', password='5YtG5aztwDPLiEyy', database='pycharm',
#                      charset='utf8')
# company = '阿里巴巴'
# today = time.strftime("%Y-%m-%d")  # 这边采用标准格式的日期格式
#
# cur = db.cursor()  # 获取会话指针，用来调用SQL语句
# sql = 'SELECT * FROM test WHERE company = %s'
# cur.execute(sql, (company))
# data = cur.fetchall()  # 提取所有数据，并赋值给data变量
#
# db.commit()  # 这个其实可以不写，因为没有改变表结构
# cur.close()  # 关闭会话指针
# db.close()  # 关闭数据库链接
#
# mail_msg = []
# mail_msg.append('<p style="margin:0 auto">尊敬的小主，您好，以下是今天的舆情监控报告，望查阅：</p>')  # style="margin:0 auto"用来调节行间距
# mail_msg.append('<p style="margin:0 auto"><b>一、阿里巴巴舆情报告</b></p>')  # 加上<b>表示加粗
# for i in range(len(data)):
#     href = '<p style="margin:0 auto"><a href="' + data[i][2] + '">' + str(i + 1) + '.' + data[i][1] + '</a></p>'
#     mail_msg.append(href)
#
# mail_msg.append('<br>')  # <br>表示换行
# mail_msg.append('<p style="margin:0 auto">祝好</p>')
# mail_msg.append('<p style="margin:0 auto">椰子一号</p>')
# mail_msg = '\n'.join(mail_msg)
#
# # 3.添加正文内容
# msg = MIMEText(mail_msg, 'html', 'utf-8')
#
# # 4.设置邮件主题、发件人、收件人
# msg["Subject"] = "小椰舆情监控报告"
# msg["From"] = user
# msg["To"] = to
#
# # 5.发送邮件
# s = smtplib.SMTP_SSL('smtp.qq.com', 465)  # 选择qq邮箱服务，默认端口为465
# s.login(user, pwd)  # 登录qq邮箱
# s.send_message(msg)  # 发送邮件
# s.quit()  # 退出邮箱服务
# print('Success!')


