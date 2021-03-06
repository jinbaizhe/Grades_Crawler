import urllib,http.cookiejar
import sys,os,pickle,re,threading,time,io
from email.mime.text import MIMEText
from email.header import Header
from smtplib import SMTP_SSL
from bs4 import BeautifulSoup
from configparser import ConfigParser
import time
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
        info['year'] = cfg.get('Grade', 'year')
        info['term'] = cfg.get('Grade', 'term')
        if len(info['username']) > 0 and len(info['password']) > 0:
            print('已检测到保存过的学号信息:' + info['username'],flush=True)
            print('正在用此学号登录...',flush=True)
            autoLogin = True
    if not autoLogin:
        info['username'] = input('请输入学号:')
        info['password'] = input('请输入统一身份认证密码(默认身份证后六位):')
        info['year'] = '2016-2017'
        info['term'] = '2'
    if not os.path.isfile(config_path):
        cfg.add_section('Login')
        cfg.add_section('Grade')
        cfg.set('Login', 'account', info['username'])
        cfg.set('Login', 'password', info['password'])
        cfg.set('Grade', 'year', info['year'])
        cfg.set('Grade', 'term', info['term'])
        with open(config_path, 'w+') as f:
            cfg.write(f)
    return info
def login(info):
    postData = {
        'user': info['username'],
        'pass': info['password'],
        'inputCode': '1234',
        'url': 'http://my.zust.edu.cn/login',
    }
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.8',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Host': 'ez.zust.edu.cn',
        'Origin': 'https://ez.zust.edu.cn',
        'Referer': 'https://ez.zust.edu.cn/login?url=http://my.zust.edu.cn/',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36',
    }
    data = urllib.parse.urlencode(postData).encode(encoding='utf-8')
    request = urllib.request.Request('https://ez.zust.edu.cn/login', data, headers)
    response = opener.open(request)
    result = response.read().decode('utf-8', 'ignore')
    pattern = r'<DIV id="errmsg".*?>(.*?)</DIV>'
    match = re.search(pattern,result)
    if match:
        print(match.group(1))
        return False
    return result
def loginZHFW(info):#登录综合服务
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
def loginJWXT():
    response = opener.open('http://jwxt.zust.edu.cn.ez.zust.edu.cn/default_zzjk.aspx')
    result = response.read().decode()
    return result
def getUrlName(result):
    pattern_info = '<span id="xhxm">\d*\s*(\w*)</span></em>'
    return urllib.request.quote(re.search(pattern_info, result).group(1))
def getGradePage(urlName):
    url_cjcx = 'http://jwxt.zust.edu.cn.ez.zust.edu.cn/xscj_gc.aspx?xh=' + info['username'] + '&xm=' + urlName + '&gnmkdm=N121616'
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

    postData_cjcx = {
        '__VIEWSTATE': viewstate,
        'ddlXN': info['year'],
        'ddlXQ': info['term'],
        'Button1': '按学期查询',
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
    pattern_table = r'<table class="datelist" cellspacing="0" cellpadding="3" border="0" id="Datagrid1" width="100%">(.*?)</table>'
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
def getGrade(urlName,printToScreen):
    gradePage = getGradePage(urlName)
    (tableHeadList,subjectList) = parseGradesPage(gradePage)
    subjectMap = print_subejectInfo(tableHeadList,subjectList,printToScreen)
    return subjectMap
def getGradeThread(urlName,subjectMap):
    print("成绩监控开启成功",flush=True)
    while True:
        string=''
        try:
            tempMap = getGrade(urlName,False)
            if len(subjectMap) < len(tempMap):
                for item in tempMap.keys():
                    if (item not in subjectMap.keys()):
                        string += item + '  :  ' + (tempMap[item])[2] + '\n'
                        subjectMap[item] = tempMap[item]
                print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()) +':' +string, flush=True)
                sendEmail(receiver_mail='jinbaizhe@qq.com', mail_title='又有新的成绩出来了', mail_content=string)
                with open(subjectInfo_path, 'wb') as f:
                    pickle.dump(tempMap, f)
            else:
                print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()) + ":无新成绩", flush=True)
        except Exception as e1:
            print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()) + ":查询成绩时出错,错误信息:" + str(e1), flush=True)
            print("正在尝试重新登录",flush=True)
            try:
                loginZHFW(info)
                print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()) + ":重新登录成功")
            except Exception as e2:
                print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()) + ":重新登录失败"+"，错误信息:" + str(e2), flush=True)
        time.sleep(60 * 5)  # 间隔时间--待修改
def getCardInfo():
    opener.open('http://ecard.zust.edu.cn.ez.zust.edu.cn/zghyportalHome.action')
    headers = {
        'Accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding' : 'gzip, deflate',
        'Accept-Language' : 'zh-CN,zh;q=0.8',
        'Connection' : 'keep-alive',
        'Host' : 'ecard.zust.edu.cn.ez.zust.edu.cn',
        'Referer' : 'http://ecard.zust.edu.cn.ez.zust.edu.cn/accleftframe.action',
        'Upgrade-Insecure-Requests' : '1',
        'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36'
    }
    request = urllib.request.Request('http://ecard.zust.edu.cn.ez.zust.edu.cn/accountcardUser.action',headers=headers)
    response =opener.open(request)
    result = response.read().decode('utf-8','ignore')
    pattern = r'余&nbsp;&nbsp;&nbsp;&nbsp;额.*?<td class="neiwen">(.*?)</td>'
    match = re.search(pattern,result,re.DOTALL)
    return match.group(1)
def getLibraryInfo():
    opener.open('http://my.lib.zust.edu.cn.ez.zust.edu.cn/idstar.aspx')
    headers = {
        'Accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding' : 'gzip, deflate',
        'Accept-Language' : 'zh-CN,zh;q=0.8',
        'Connection' : 'keep-alive',
        'Host' : 'my.lib.zust.edu.cn.ez.zust.edu.cn',
        'Referer' : 'http://my.lib.zust.edu.cn.ez.zust.edu.cn/Borrowing.aspx',
        'Upgrade-Insecure-Requests' : '1',
        'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36'
    }
    request = urllib.request.Request('http://my.lib.zust.edu.cn.ez.zust.edu.cn/Borrowing.aspx',headers=headers)
    response =opener.open(request)
    result = response.read().decode('utf8')
    soup = BeautifulSoup(result, 'html.parser')
    table=str(soup.find('table',id="ctl00_ContentPlaceHolder1_GridView1"))
    pattern = r'<table.*?<a.*?>(.*?)<.*?借书时间.*?>(.*?)<.*?应还日期.*?>(.*?)<.*?续借次数.*?>(.*?)<.*?超期情况.*?>(.*?)<.*?</table>'
    match = re.findall(pattern,table,re.DOTALL)
    for item in ['书名','借书时间','应还日期','续借次数','超期情况']:
        print_align(item, 13, 0)
    print()
    for book in match:
        for item in book:
            print_align(item,13,0)
        print()
def sendEmail(receiver_mail='',mail_title='', mail_content='',host_server='smtp.qq.com', sender_qq='25497020', pwd='ntngqxpiegzkbgjc', sender_qq_mail='25497020@qq.com'):
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

sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf8')
cookie = http.cookiejar.CookieJar()
handler = urllib.request.HTTPCookieProcessor(cookie)
opener = urllib.request.build_opener(handler)
config_path = 'config.ini'
subjectInfo_path = 'SubjectInfo.pcl'
urlName = ''
info = getLoginInfo()
# state = login(info)
# while not state:
#     getLoginInfo()
#     state = login(info)
state=False
while state==False:
    try:
        loginZHFW(info)
        state=True
    except Exception as e:
        state=False
        print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()) + ":登录失败，将于3分钟后重试", flush=True)
        print("错误信息:"+str(e),flush=True)
        time.sleep(3*60)
while True:
    select = input("1.成绩查询\n2.图书馆借书情况查询\n3.一卡通查询\n4.开启成绩监控\n5.切换账号\n6.设置(尚未完成)\n7.退出\n")
    if select == '1':
        result = loginJWXT()
        # print(result);
        urlName=getUrlName(result)
        subjectMap=getGrade(urlName,True)
        with open(subjectInfo_path, 'wb') as f:
            pickle.dump(subjectMap, f)
    elif select == '2':  # 图书馆借书情况查询
        getLibraryInfo()
    elif select == '3':#一卡通查询
        print(getCardInfo())
    elif select == '4':
        if os.path.isfile(subjectInfo_path):
            with open(subjectInfo_path, 'rb') as f:
                subjectMap = pickle.load(f)
        else:
            subjectMap = dict()
        if urlName == '':
            result = loginJWXT()
            urlName = getUrlName(result)
        t = threading.Thread(target=getGradeThread,args=(urlName,subjectMap))
        t.start()
        break
    elif select == '5':#切换账号
        state = False
        while state == False:
            getLoginInfo()
            state = login(info)
        loginZHFW(info)
    elif select == '6':
        pass
    elif select == '7':
        sys.exit()
    input("输入回车返回上级菜单")