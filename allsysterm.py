# =============================================================================
# 2.3.1 获取百度新闻网页源代码 by 王宇韬 代码更新：www.huaxiaozhi.com 资料下载区
# =============================================================================

import requests
from lxml import etree
import re
import pymysql
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import time

user = '1327928308@qq.com'
pwd = 'imusrttythppijej'  # 邮箱的SMTP密码，看书第11章，申请很方便
to = '1327928308@qq.com'  # 可以设置多个收件人，英文逗号隔开，如：'***@qq.com, ***@163.com'




headers ={
    "User-Agent":'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.0.0 Safari/537.36'
}

def baidu(company):

    url = 'https://www.baidu.com/s?rtt=1&bsst=1&cl=2&tn=news&ie=utf-8&word='+company
    res = requests.get(url=url, headers=headers).text
    #print(res)
    tree = etree.HTML(res)
    div_list = tree.xpath('//*[@id="content_left"]/div')

    #循环列表
    for div in div_list[1:]:
        #来源
        source = div.xpath('./div/div/div[2]/div/a[1]/span/text()')
        if len(source) == 0:
            source = div.xpath('./div/div/div/div/a[1]/span/text()')

        #时间
        date = div.xpath('./div/div/div[2]/span[1]/text()')
        if len(date) == 0:
            date = div.xpath('./div/div/div/span[1]/text()')

        #链接
        href = div.xpath('./div/div/div/a[1]/@href')
        if len(href) == 0:
            href = div.xpath('./div/h3/a/@href')

        #标题
        title = div.xpath('./div/h3/a/@aria-label')
        title = re.sub('标题：', '', str(title))


        # 检测标题是否包含公司名称
        if company not in title:
             del title
             del source
             del href
             del date
             continue

        score = []
        keywords = ['违约', '诉讼', '兑付', '阿里', '百度', '京东', '互联网','港股']
        num = 0
        for k in keywords:
            if k in title:
                num -= 5
        score.append(num)

        print(score)

        db = pymysql.connect(host='182.61.132.25', port=3306, user='pycharm', password='sWeCiRwF3TJLbrCb',database='pycharm', charset='utf8')
        # 插入数据
        cur = db.cursor()  # 获取会话指针，用来调用SQL语句
        # 6.1 查询数据，为之后的数据去重做准备
        sql_1 = 'SELECT * FROM article WHERE company =%s'
        cur.execute(sql_1, company)#选取对应的company数据
        data_all = cur.fetchall()#提取所有数据
        title_all = []#创建空列表来存储新闻标题
        for j in range(len(data_all)):#遍历提取到的数据
            title_all.append(data_all[j][1])#将数据中的新闻标题存入列表
        #  6.2 判断数据是否在原数据库中，不在的话才进行数据存储
        if title not in title_all:
           sql_2 = 'INSERT INTO article(company,title,href,source,date,score) VALUES (%s,%s,%s,%s,%s,%s)'  # 编写SQL语句
           cur.execute(sql_2, (company, title, href, source, date, score))
           db.commit()
        cur.close()
        db.close()


companys = ['阿里巴巴']
for i in companys:
    baidu(i)

    print('成功！')

db = pymysql.connect(host='182.61.132.25', port=3306, user='pycharm', password='sWeCiRwF3TJLbrCb',database='pycharm', charset='utf8')
company = '阿里巴巴'
today = time.strftime("%Y-%m-%d")  # 这边采用标准格式的日期格式

cur = db.cursor()  # 获取会话指针，用来调用SQL语句
sql = 'SELECT * FROM test WHERE company = %s'
cur.execute(sql, (company))
data = cur.fetchall()  # 提取所有数据，并赋值给data变量
print(data)
db.commit()  # 这个其实可以不写，因为没有改变表结构
cur.close()  # 关闭会话指针
db.close()  # 关闭数据库链接

# 2.利用从数据库里提取的内容编写邮件正文内容
mail_msg = []
mail_msg.append('<p style="margin:0 auto">尊敬的小主，您好，以下是今天的舆情监控报告，望查阅：</p>')  # style="margin:0 auto"用来调节行间距
mail_msg.append('<p style="margin:0 auto"><b>一、阿里巴巴舆情报告</b></p>')  # 加上<b>表示加粗
for i in range(len(data)):
    href = '<p style="margin:0 auto"><a href="' + data[i][2] + '">' + str(i+1) + '.' + data[i][1] + '</a></p>'
    mail_msg.append(href)

mail_msg.append('<br>')  # <br>表示换行
mail_msg.append('<p style="margin:0 auto">祝好</p>')
mail_msg.append('<p style="margin:0 auto">华小智</p>')
mail_msg = '\n'.join(mail_msg)
print(mail_msg)

# 3.添加正文内容
msg = MIMEText(mail_msg, 'html', 'utf-8')

# 4.设置邮件主题、发件人、收件人
msg["Subject"] = "华小智舆情监控报告"
msg["From"] = user
msg["To"] = to

# 5.发送邮件
s = smtplib.SMTP_SSL('smtp.qq.com', 465)  # 选择qq邮箱服务，默认端口为465
s.login(user, pwd)  # 登录qq邮箱
s.send_message(msg)  # 发送邮件
s.quit()  # 退出邮箱服务
print('Success!')