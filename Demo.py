import urllib,http.cookiejar
import sys,os,logging,pickle
import re
from urllib.request import urlopen
from email.mime.text import MIMEText
from email.header import Header
from smtplib import SMTP_SSL
from PIL import Image
logging.basicConfig(level=logging.INFO)
def debug_printResult(result,outputName):
    with open(outputName,'w') as f:
        print(result,file=f)
def print_align(text,width,align=0):
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
def print_subejectInfo(subjectList):
    for i in range(int(len(subjectList))):
        if i == 3:
            print_align(subjectList[i], 15, 0)
        elif i in [6, 7, 8]:
            print_align(subjectList[i], 5, 0)
    print()
def getLoginInfo():
    info = dict()
    autoLogin = False
    config_path = 'config.pcl'
    if os.path.isfile(config_path):
        with open(config_path, 'rb') as f:
            info = pickle.load(f)
        if len(info['username']) > 0 and len(info['password']) > 0 and len(info['password_jwxt']) > 0:
            print('已检测到保存过的学号信息:' + info['username'])
            temp = input('是否用此学号登录?(y/n):')
            if (temp in ['y', 'Y']):
                autoLogin = True
    if not autoLogin:
        info['username'] = input('请输入学号:')
        info['password'] = input('请输入统一身份认证密码(默认为身份证后六位):')
        info['password_jwxt'] = input('请输入教务系统密码:')
        # 保存账号信息到config.pcl中
        with open(config_path, 'wb') as f:
            pickle.dump(info, f)
    return info
def login(info):
    postData = {
        'user': info['username'],
        'pass': info['password'],
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
    request = urllib.request.Request('http://ez.zust.edu.cn/login', data, headers)
    response = opener.open(request)
    result = response.read().decode('utf-8', 'ignore')
    match = re.search(r'(?:<DIV id="errmsg".*?>(.*?)</DIV>)', result)
    if match:
        print(match.group(1))
        exit()
    return result
def getViewState():
    # 获取viewstate
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.8',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        'Host': 'jwxt.zust.edu.cn.ez.zust.edu.cn',
        'Referer': 'http://ez.zust.edu.cn/login',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36',
    }
    # 构造request请求
    request = urllib.request.Request("http://jwxt.zust.edu.cn.ez.zust.edu.cn/", headers=headers)
    response = opener.open(request)
    result = response.read().decode()
    pattern = r'<input type="hidden" name="__VIEWSTATE" value="(.*?)"'
    return re.search(pattern, result).group(1)
def loginJWXT(info):
    picture = opener.open('http://jwxt.zust.edu.cn.ez.zust.edu.cn/CheckCode.aspx').read()
    # 保存验证码到本地
    with open(sys.path[0] + '\\CheckCode.gif', 'wb') as f:
        f.write(picture)
    image = Image.open('CheckCode.gif')
    image.show()
    secretCode = input('请输入验证码(验证码图片(CheckCode.gif)在"' + sys.path[0] + '\\"下):')
    # 根据抓包信息 构造表单
    postData_jwxt = {
        '__VIEWSTATE': getViewState(),
        'TextBox1': info['username'],
        'TextBox2': info['password_jwxt'],
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
    request_jwxt = urllib.request.Request('http://jwxt.zust.edu.cn.ez.zust.edu.cn/default2.aspx', data_jwxt, headers_jwxt)
    response = opener.open(request_jwxt)
    result = response.read().decode()
    match = re.search(r"<script.*?>alert\('(.*?)'\);</script>", result)
    if match and len(match.group(1)) < 15:
        print(match.group(1))
        exit()
    return result
def getUrlName(result):
    pattern_info = '<span id="xhxm">\d*\s*(\w*)</span></em>'
    return urllib.request.quote(re.search(pattern_info, result).group(1))
def getGradePage(urlName):
    # 获得查询成绩的链接
    url_cjcx = 'http://jwxt.zust.edu.cn.ez.zust.edu.cn/xscj_gc.aspx?xh=' + info['username'] + '&xm=' + urlName + '&gnmkdm=N121616'
    # 获取__VIEWSTATE和__VIEWSTATEGENERATOR
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.8',
        'Connection': 'keep-alive',
        'Host': 'jwxt.zust.edu.cn.ez.zust.edu.cn',
        'Referer': 'http://jwxt.zust.edu.cn.ez.zust.edu.cn/xs_main.aspx?xh=' + info['username'],
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36',
    }
    request = urllib.request.Request(url_cjcx, headers=headers)
    response = opener.open(request)
    result = response.read().decode()
    pattern_viewstate = r'<input type="hidden" name="__VIEWSTATE" value="(.*?)"'
    viewstate = re.search(pattern_viewstate, result).group(1)

    # 根据抓包信息 构造表单
    postData_cjcx = {
        '__VIEWSTATE': viewstate,
        'ddlXN': year,
        'ddlXQ': term,
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
    # logging.info("开始查询成绩")
    # 生成post数据
    data_cjcx = urllib.parse.urlencode(postData_cjcx).encode()
    # 构造request请求
    request_cjcx = urllib.request.Request(url_cjcx, data_cjcx, headers_cjcx)
    response = opener.open(request_cjcx)
    return response.read().decode('utf-8')
    # logging.info("查询成绩成功")
def parseGradesPage(result_cjcx):
    pattern_table = r'<table class="datelist" cellspacing="0" cellpadding="3" border="0" id="Datagrid1" width="100%">(.*?)</table>'
    pattern_tableHead = r'<tr class="datelisthead">(.*?)</tr>'
    pattern_subjectItem = r'(?:<tr>|<tr class="alt">)(.*?)</tr>'
    pattern_subjectInfo = r'<td>(.*?)</td>'

    table = re.search(pattern_table, result_cjcx, re.DOTALL).group()
    tableHead = re.search(pattern_tableHead, table, re.DOTALL).group()
    tableHeadList = re.findall(r'<td>(.*?)</td>', tableHead)
    subjectList = []
    table = re.sub(r'&nbsp;', ' ', table)
    for item in re.findall(pattern_subjectItem, table, re.DOTALL):
        subjectList.append(re.findall(pattern_subjectInfo, item))
    print(year, "学年第", term, "学期")
    print_subejectInfo(tableHeadList)
    point = 0.0
    sumPoint = 0.0
    for subject in subjectList:
        print_subejectInfo(subject)
        point += float(subject[7]) * float(subject[6])
        sumPoint += float(subject[6])
    numOfSubject = '共' + str(len(subjectList)) + '门课'
    print(numOfSubject, "平均绩点:%.2f" % (point / (sumPoint * 5) * 5))
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
cookie = http.cookiejar.CookieJar()
handler = urllib.request.HTTPCookieProcessor(cookie)
opener = urllib.request.build_opener(handler)
year='2016-2017'
term='2'
info=getLoginInfo()
login(info)
result=loginJWXT(info)
urlName=getUrlName(result)
gradePage=getGradePage(urlName)
parseGradesPage(gradePage)
