import http.cookiejar
import urllib
import re
from urllib.request import urlopen
from email.mime.text import MIMEText
from email.header import Header
from smtplib import SMTP_SSL
import logging
import sys,os
logging.basicConfig(level=logging.INFO)

def print_subejectInfo(text,width,align=0):
    if len(text)>width:
        print(text,end='')
        return
    numOfChinese=len(re.findall('[\u4e00-\u9fa5]',text))
    numOfOthers = len(text) - numOfChinese
    if align==0:
        print(text,end='')
        print(' '*(width*2-numOfOthers-numOfChinese*2),end='')
    else:
        print(' '*(width*2-numOfOthers-numOfChinese*2),end='')
        print(text,end='')

cookie = http.cookiejar.CookieJar()
handler = urllib.request.HTTPCookieProcessor(cookie)
opener = urllib.request.build_opener(handler)

firstPostUrl = "http://ez.zust.edu.cn/login"
captchaUrl_jwxt = "http://jwxt.zust.edu.cn.ez.zust.edu.cn/CheckCode.aspx"
postUrl_jwxt = "http://jwxt.zust.edu.cn.ez.zust.edu.cn/default2.aspx"
config_path=sys.path[0]+'\\config.txt'
username=''
password=''
password_jwxt=''
autoLogin=False
if os.path.isfile(config_path):
    with open(config_path,'r') as f:
        info=f.read()
    if re.search(r'(?<=username:)(.*)', info):
        username = re.search(r'(?<=username:)(.*)', info).group()
    if re.search(r'(?<=password:)(.*)', info):
        password = re.search(r'(?<=password:)(.*)', info).group()
    if re.search(r'(?<=password_jwxt:)(.*)', info):
        password_jwxt = re.search(r'(?<=password_jwxt:)(.*)', info).group()
    if len(username) > 0 and len(password) > 0 and len(password_jwxt) > 0:
        print('已检测到保存过的学号信息:' + username)
        temp=input('是否用此学号登录?(y/n):')
        if ( temp== 'y' or temp=='Y'):
            autoLogin=True
if not autoLogin:
    username = input('请输入学号:')
    password = input('请输入身份证号码后六位:')
    password_jwxt = input('请输入教务系统密码:')
    # 保存账号信息到config.txt中
    with open(config_path, 'w') as f:
        print('username:' + username, file=f)
        print('password:' + password, file=f)
        print('password_jwxt:' + password_jwxt, file=f)

postData = {
        'user': username,
        'pass': password,
        'inputCode': '1234',
        'url': 'http://jwxt.zust.edu.cn/',
    }
# 根据抓包信息 构造headers
headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'zh-CN,zh;q=0.8',
    'Cache-Control': 'max-age=0',
    'Connection': 'keep-alive',
    'Content-Type': 'application/x-www-form-urlencoded',
    'Host': 'ez.zust.edu.cn',
    'Origin': 'http://ez.zust.edu.cn',
    'Referer': 'http://ez.zust.edu.cn/login?url=http://jwxt.zust.edu.cn/',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36',
}

# 生成post数据
data = urllib.parse.urlencode(postData).encode(encoding='utf-8')
# 构造request请求
request = urllib.request.Request(firstPostUrl, data, headers)
response = opener.open(request)

#获取viewstate
headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'zh-CN,zh;q=0.8',
    'Cache-Control': 'max-age=0',
    'Connection': 'keep-alive',
    'Host': 'jwxt.zust.edu.cn.ez.zust.edu.cn',
    'Referer': firstPostUrl,
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36',
}
# 构造request请求
request = urllib.request.Request("http://jwxt.zust.edu.cn.ez.zust.edu.cn/",headers=headers)
try:
    response = opener.open(request)
except urllib.error.HTTPError:
    print("身份证后六位数字不正确,请重试")
    exit()
result = response.read().decode()
pattern=r'<input type="hidden" name="__VIEWSTATE" value="(.*?)"'
viewstate=re.findall(pattern,result)[0]

#开始登录第二层
picture = opener.open(captchaUrl_jwxt).read()
# 保存验证码到本地
local = open(sys.path[0]+'\\CheckCode.gif', 'wb')
local.write(picture)
local.close()
secretCode = input('请输入验证码(验证码图片在"'+sys.path[0]+'\\CheckCode.gif'+'"下):')
# 根据抓包信息 构造表单
postData_jwxt = {
    '__VIEWSTATE': viewstate,
    'TextBox1': username,
    'TextBox2': password_jwxt,
    'TextBox3': secretCode,
    'RadioButtonList1': '学生',
    'Button1': '',
    'lbLanguage': '',
}
# 根据抓包信息 构造headers
headers_jwxt = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'zh-CN,zh;q=0.8',
    'Cache-Control': 'max-age=0',
    'Connection': 'keep-alive',
    'Content-Type': 'application/x-www-form-urlencoded',
    'Host': 'jwxt.zust.edu.cn.ez.zust.edu.cn',
    'Origin': 'http://jwxt.zust.edu.cn.ez.zust.edu.cn',
    'Referer': 'http://jwxt.zust.edu.cn.ez.zust.edu.cn/',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36',
}
# 生成post数据
data_jwxt = urllib.parse.urlencode(postData_jwxt).encode(encoding='utf-8')
# 构造request请求
request_jwxt = urllib.request.Request(postUrl_jwxt, data_jwxt, headers_jwxt)
response=opener.open(request_jwxt)
result = response.read().decode()
#获得查询成绩的链接
pattern_info='<span id="xhxm">\d*\s*(\w*)</span></em>'
try:
    urlName = urllib.request.quote(re.findall(pattern_info, result)[0])
except IndexError:#查找不到姓名信息，即登录失败，验证码或教务系统密码不正确
    print("验证码或教务系统密码不正确,请重试")
    exit()
url_cjcx='http://jwxt.zust.edu.cn.ez.zust.edu.cn/xscj_gc.aspx?xh='+username+'&xm='+urlName+'&gnmkdm=N121616'

#获取__VIEWSTATE和__VIEWSTATEGENERATOR
headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'zh-CN,zh;q=0.8',
    'Connection': 'keep-alive',
    'Host': 'jwxt.zust.edu.cn.ez.zust.edu.cn',
    'Referer': 'http://jwxt.zust.edu.cn.ez.zust.edu.cn/xs_main.aspx?xh='+username,
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36',
}
request = urllib.request.Request(url_cjcx,headers=headers)
response=opener.open(request)
result = response.read().decode()
pattern_viewstate=r'<input type="hidden" name="__VIEWSTATE" value="(.*?)"'
viewstate=(re.findall(pattern_viewstate,result))[0]

# 根据抓包信息 构造表单
postData_cjcx = {
    '__VIEWSTATE': viewstate,
    'ddlXN': '2016-2017',
    'ddlXQ': '2',
    'Button1': '按学期查询',
}
# 根据抓包信息 构造headers
headers_cjcx = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'zh-CN,zh;q=0.8',
    'Cache-Control': 'max-age=0',
    'Connection': 'keep-alive',
    'Content-Type': 'application/x-www-form-urlencoded',
    'Host': 'jwxt.zust.edu.cn.ez.zust.edu.cn',
    'Origin': 'http://jwxt.zust.edu.cn.ez.zust.edu.cn',
    'Referer': url_cjcx,
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36',
}
logging.info("开始查询成绩")
# 生成post数据
data_cjcx = urllib.parse.urlencode(postData_cjcx).encode()
# 构造request请求
request_cjcx = urllib.request.Request(url_cjcx, data_cjcx, headers_cjcx)
response = opener.open(request_cjcx)
result_cjcx = response.read().decode('utf-8')
logging.info("查询成绩成功")

# 开始分析数据
pattern_table=r'<table class="datelist"(.*?)</table>'
pattern_tableHead=r'<tr class="datelisthead">(.*?)</tr>'
pattern_subjectItem=r'(?:<tr>|<tr class="alt">)(.*?)</tr>'
pattern_subjectInfo=r'<td>(.*?)</td>'

table=re.search(pattern_table,result_cjcx,re.DOTALL).group()
tableHead=re.search(pattern_tableHead,table,re.DOTALL).group()
tableHeadList=re.findall(r'<td>(.*?)</td>',tableHead)
subjectList=[]
table=re.sub(r'&nbsp;',' ',table)

for item in re.findall(pattern_subjectItem,table,re.DOTALL):
    subjectList.append(re.findall(pattern_subjectInfo,item))
for item in tableHeadList:
    print_subejectInfo(item, 16, 0)
print()
for subject in subjectList:
    for item in subject:
        print_subejectInfo(item, 16, 0)
    print()
numOfSubject = '共'+ str(len(subjectList))+'门课'
print(numOfSubject)

def sendEmail(host_server, sender_qq, pwd, sender_qq_mail, receiver_mail, mail_title, mail_content):
    logging.info('开始发送邮件')
    # qq邮箱smtp服务器
    # sender_qq为发件人的qq号码
    # pwd为qq邮箱的授权码
    # 发件人的邮箱
    # 收件人邮箱
    # 邮件标题
    # 邮件的正文内容
    # ssl登录
    smtp = SMTP_SSL(host_server)
    # set_debuglevel()是用来调试的。参数值为1表示开启调试模式，参数值为0关闭调试模式
    # smtp.set_debuglevel(1)
    smtp.ehlo(host_server)
    smtp.login(sender_qq, pwd)

    msg = MIMEText(mail_content, "plain", 'utf-8')
    msg["Subject"] = Header(mail_title, 'utf-8')
    msg["From"] = sender_qq_mail
    msg["To"] = receiver_mail
    smtp.sendmail(sender_qq_mail, receiver_mail, msg.as_string())
    smtp.quit()
    logging.info('邮件发送成功')

