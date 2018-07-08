import urllib,http.cookiejar
import sys,os,pickle,re,threading,io
from email.mime.text import MIMEText
from email.header import Header
from smtplib import SMTP_SSL
from configparser import ConfigParser
import time,logging


def print_align(text,width,align=0):
    if len(text)>width:
        text=text[:(width-3)]+'...'
    numOfChinese=len(re.findall('[\u2E80-\uFE4F]',text))
    numOfOthers = len(text) - numOfChinese
    if align==0:
        print(text,end='')
        print(' '*(width*2-numOfOthers-numOfChinese*2),end='')
    else:
        print(' '*(width*2-numOfOthers-numOfChinese*2),end='')
        print(text,end='')


def print_subejectInfo(tableHeadList,subjectList,printToScreen):
    point = 0.0
    sumPoint = 0.0
    subjectMap=dict()
    numOfSubject = '共' + str(len(subjectList)) + '门课'
    for subject in subjectList:
        subjectMap[subject[3]] = subject[6:9]
        point += float(subject[7]) * float(subject[6])
        sumPoint += float(subject[6])
    if printToScreen:
        print(info['year'], "学年第", info['term'], "学期")
        print_align(tableHeadList[3], 15, 0)
        for item in tableHeadList[6:9]:
            print_align(item, 5, 0)
        print()
        for name in subjectMap.keys():
            print_align(name, 15, 0)
            for item in subjectMap[name]:
                print_align(item, 5, 0)
            print()
        if sumPoint!=0:
            print(numOfSubject, "平均绩点:%.2f" % (point / (sumPoint * 5) * 5))
        else:
            print('暂时无成绩')
    return subjectMap


def getLoginInfo():
    info = dict()
    autoLogin = False
    cfg=ConfigParser()
    if os.path.isfile(config_path):
        cfg.read(config_path)
        info['username']=cfg.get('Login','account')
        info['password']=cfg.get('Login','password')
        info['email']=cfg.get('Login','email')
        info['year'] = cfg.get('Grade', 'year')
        info['term'] = cfg.get('Grade', 'term')
        if len(info['username']) > 0 and len(info['password']) > 0:
            print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()) +':' +'已检测到保存过的学号信息:' + info['username'],flush=True)
            print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()) +':' +'正在用此学号登录...',flush=True)
            autoLogin = True
    if not autoLogin:
        info['username'] = input('请输入学号:')
        info['password'] = input('请输入统一身份认证密码(默认身份证后六位):')
        info['email'] = input('请输入接受成绩通知的邮箱:')
        info['year'] = input('请输入学年(例如:2017-2018):')
        info['term'] = input('请输入学期(例如:1):')
    if not os.path.isfile(config_path):
        cfg.add_section('Login')
        cfg.add_section('Grade')
        cfg.set('Login', 'account', info['username'])
        cfg.set('Login', 'password', info['password'])
        cfg.set('Login', 'email', info['email'])
        cfg.set('Grade', 'year', info['year'])
        cfg.set('Grade', 'term', info['term'])
        with open(config_path, 'w+') as f:
            cfg.write(f)
    return info


def loginZHFW(info,opener):#登录综合服务
    request = urllib.request.Request('http://authserver.zust.edu.cn/authserver/login?service=http://my.zust.edu.cn.ez.zust.edu.cn')
    response = opener.open(request)
    result = response.read().decode('utf-8', 'ignore')
    pattern = r'<input type="hidden" name="lt" value="(.*?)"/>'
    match = re.search(pattern, result)
    if match:
        lt=match.group(1)
    postData = {
        'username': info['username'],
        'password': info['password'],
        'lt': lt,
        'dllt': 'userNamePasswordLogin',
        'execution': 'e1s1',
        '_eventId': 'submit',
        'rmShown': '1',
    }
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Host': 'authserver.zust.edu.cn',
        'Origin': 'http://authserver.zust.edu.cn',
        'Referer': 'http://authserver.zust.edu.cn/authserver/login?service=http://my.zust.edu.cn.ez.zust.edu.cn',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36',
    }
    data = urllib.parse.urlencode(postData).encode()
    request = urllib.request.Request('http://authserver.zust.edu.cn/authserver/login?service=http://my.zust.edu.cn.ez.zust.edu.cn', data, headers)
    response = opener.open(request)


def loginJWXT(opener):
    response = opener.open('http://jwxt.zust.edu.cn.ez.zust.edu.cn/default_zzjk.aspx')
    result = response.read().decode()
    return result


def getUrlName(result):
    pattern_info = '<span id="xhxm">\d*\s*(\w*)</span></em>'
    return urllib.request.quote(re.search(pattern_info, result).group(1))


def getGradePage(urlName,opener):
    url_cjcx = 'http://jwxt.zust.edu.cn.ez.zust.edu.cn/xscjcx.aspx?xh=' + info['username'] + '&xm=' + urlName + '&gnmkdm=N121605'
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
    pattern_viewstate = r'<input[^>]*name="__VIEWSTATE"[^>]*value="(.*?)"'
    pattern_eventvalidation = r'<input[^>]*name="__EVENTVALIDATION"[^>]*value="(.*?)"'
    viewstate = re.search(pattern_viewstate, result).group(1)
    eventvalidation = re.search(pattern_eventvalidation, result).group(1)
    postData_cjcx = {
        '__EVENTTARGET': "",
        '__EVENTARGUMENT': "",
        '__VIEWSTATE': viewstate,
        '__EVENTVALIDATION': eventvalidation,
        'hidLanguage': "",
        'ddlXN': info['year'],
        'ddlXQ': info['term'],
        'ddl_kcxz': "",
        'btn_xq': '学期成绩',
    }
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
    data_cjcx = urllib.parse.urlencode(postData_cjcx).encode()
    request_cjcx = urllib.request.Request(url_cjcx, data_cjcx, headers_cjcx)
    response = opener.open(request_cjcx)
    return response.read().decode('utf-8')


def parseGradesPage(result_cjcx):
    pattern_table = r'<table class="datelist"[^>]*>(.*?)</table>'
    pattern_tableHead = r'<tr class="datelisthead">(.*?)</tr>'
    pattern_subjectItem = r'(?:<tr>|<tr class="alt">)(.*?)</tr>'
    pattern_subjectInfo = r'<td>(.*?)</td>'

    table = re.search(pattern_table, result_cjcx, re.DOTALL).group()
    tableHead = re.search(pattern_tableHead, table, re.DOTALL).group()
    tableHeadList = re.findall(r'<td>(.*?)</td>', tableHead)
    subjectList = list()
    table = re.sub(r'&nbsp;', ' ', table)
    for item in re.findall(pattern_subjectItem, table, re.DOTALL):
        subjectList.append(re.findall(pattern_subjectInfo, item))
    return (tableHeadList,subjectList)


def getGrade(urlName,printToScreen,opener):
    gradePage = getGradePage(urlName, opener)
    (tableHeadList, subjectList) = parseGradesPage(gradePage)
    subjectMap = print_subejectInfo(tableHeadList,subjectList,printToScreen)
    return subjectMap


def logoutJWXT(opener):
    response = opener.open('http://jwxt.zust.edu.cn.ez.zust.edu.cn/default_ldap.aspx')


def logoutZHFW(opener):
    response = opener.open('http://authserver.zust.edu.cn.ez.zust.edu.cn/authserver/logout?service=http://my.zust.edu.cn.ez.zust.edu.cn/')


def getGradeThread(subjectMap):
    logging.info(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()) + ':Thread is running')
    while True:
        cookie = http.cookiejar.CookieJar()
        handler = urllib.request.HTTPCookieProcessor(cookie)
        opener = urllib.request.build_opener(handler)
        string=''
        try:
            loginZHFW(info, opener)
            result = loginJWXT(opener)
            urlName = getUrlName(result)
            tempMap = getGrade(urlName,False,opener)
            if len(subjectMap) < len(tempMap):
                for item in tempMap.keys():
                    if (item not in subjectMap.keys()):
                        string += item + '  :  ' + (tempMap[item])[2] + '\n'
                        subjectMap[item] = tempMap[item]
                logging.info(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()) +':' +'New grades coming')
                sendEmail(receiver_mail=info["email"], mail_title='又有新的成绩出来了', mail_content=string)
                with open(subjectInfo_path, 'wb') as f:
                    pickle.dump(tempMap, f)
            else:
                logging.info(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()) + ":It's up to date")
        except Exception as e:
            logging.info(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()) + ":Error message:" + str(e))
        finally:
            try:
                logoutJWXT(opener)
                logoutZHFW(opener)
            except Exception as e:
                logging.info(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()) + ":Error message:" + str(e))
        time.sleep(60 * 5)


def sendEmail(receiver_mail='',mail_title='', mail_content='', host_server='smtp.qq.com', sender_qq='25497020', pwd='ntngqxpiegzkbgjc', sender_qq_mail='25497020@qq.com'):
    # qq邮箱smtp服务器
    # sender_qq为发件人的qq号码
    # pwd为qq邮箱的授权码
    # 发件人的邮箱
    # 收件人邮箱
    # 邮件标题
    # 邮件的正文内容
    # ssl登录
    smtp = SMTP_SSL(host_server)
    smtp.ehlo(host_server)
    smtp.login(sender_qq, pwd)

    msg = MIMEText(mail_content, "plain", 'utf-8')
    msg["Subject"] = Header(mail_title, 'utf-8')
    msg["From"] = sender_qq_mail
    msg["To"] = receiver_mail
    smtp.sendmail(sender_qq_mail, receiver_mail, msg.as_string())
    smtp.quit()


sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf8')
config_path = './config.ini'
subjectInfo_path = './SubjectInfo.pcl'
date_string = time.strftime("%Y-%m-%d")
filename = './thread.'+date_string+'.log'
logging.basicConfig(filename=filename, level=logging.INFO, filemode='a')
info = getLoginInfo()

if os.path.isfile(subjectInfo_path):
    with open(subjectInfo_path, 'rb') as f:
        subjectMap = pickle.load(f)
else:
    subjectMap = dict()

t = threading.Thread(target=getGradeThread, args=(subjectMap,), daemon=True)
t.start()
t.join()
