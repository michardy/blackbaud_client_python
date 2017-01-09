import sys
import BaseHTTPServer
import urllib2
import urllib
import cookielib
import time
import json
import re
from datetime import date, timedelta, datetime
from os.path import expanduser


home = expanduser("~")
cjp = home + "\\AppData\\Local\\UAC\\cookie.dat"
HOST_NAME = 'localhost'
PORT_NUMBER = 9777

cj = cookielib.CookieJar()
fcj = cookielib.LWPCookieJar(cjp)
reqD = urllib2.build_opener(urllib2.HTTPCookieProcessor(fcj))

class MyHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    def do_HEAD(s):
        s.send_response(200)
        s.send_header("Content-type", "text/html")
        s.send_header('Access-Control-Allow-Origin', '*')
        s.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        s.send_header("Access-Control-Allow-Headers", "X-Requested-With")
        s.send_header("Access-Control-Allow-Headers", "Content-Type")
        s.end_headers()
    def do_GET(s):
        page = ""
        if s.path == "/":
            s.send_response(200)
            page = '''Unified Assignment Center Whipple Hill/Blackbaud client'''
            s.send_header('Access-Control-Allow-Origin', '*')
            s.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
            s.send_header("Access-Control-Allow-Headers", "X-Requested-With")
            s.send_header("Access-Control-Allow-Headers", "Content-Type")
            s.send_header("Content-type", "text/html")
            s.end_headers()
        elif s.path == "/CSLogin":
            s.send_response(200)
            s.send_header("Content-type", "text/html")
            s.end_headers()
            page = '''<form action="/BCSlogin" method="post">
<input name="uname" type="text"></input>
<input name="pswd" type="password"></input>
<button type="submit">Submit</button>
</form>'''
        if s.path == "/WALogin":
            s.send_response(200)
            s.send_header("Content-type", "text/html")
            s.end_headers()
            page = '''<form action="/WAlogin" method="post">
<input name="uname" type="text"></input>
<input name="pswd" type="password"></input>
<button type="submit">Submit</button>
</form>'''
        elif s.path == "/day":
            fcj.load(filename=cjp, ignore_discard=True, ignore_expires=True)
            ntime = datetime.now()+timedelta(5)
            cdate = time.strftime('%m/%d/%Y')
            date = ntime.strftime('%m/%d/%Y')
            print(date)
            print(fcj)
            req = reqD.open("https://bayschoolsf.myschoolapp.com/api/DataDirect/AssignmentCenterAssignments/?format=json&filter=1&dateStart="+cdate+"&dateEnd="+date+"&persona=2&sta=2&statusList=&sectionList=")
            page = req.read()
            s.send_response(200)
            s.send_header("Content-type", "application/json")
            s.send_header('Access-Control-Allow-Origin', '*')
            s.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
            s.send_header("Access-Control-Allow-Headers", "X-Requested-With")
            s.send_header("Access-Control-Allow-Headers", "Content-Type")
            s.end_headers()
        elif s.path[:10] == "/CSdetail/":
            req = reqD.open("https://bayschoolsf.myschoolapp.com/api/assignment2/read/"+s.path[10:]+"/?format=json")
            page = req.read()
            s.send_response(200)
            s.send_header("Content-type", "application/json")
            s.send_header('Access-Control-Allow-Origin', '*')
            s.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
            s.send_header("Access-Control-Allow-Headers", "X-Requested-With")
            s.send_header("Access-Control-Allow-Headers", "Content-Type")
            s.end_headers()
        elif s.path[:11] == "/ftpimages/":
            req = reqD.open("https://bayschoolsf.myschoolapp.com/ftpimages/"+s.path[11:])
            page = req.read()
            s.send_response(200)
            s.send_header('Access-Control-Allow-Origin', '*')
            s.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
            s.send_header("Access-Control-Allow-Headers", "X-Requested-With")
            s.send_header("Access-Control-Allow-Headers", "Content-Type")
            s.end_headers()
        elif s.path == "/schedule":
            fcj.load(filename=cjp, ignore_discard=True, ignore_expires=True)
            cdate = time.strftime('%m/%d/%Y')
            req = reqD.open('https://bayschoolsf.myschoolapp.com/api/webapp/context')#There was an argument to this call.  One day they will kill this code by requiring it
            userinfo = json.loads(req.read())
            req = reqD.open('https://bayschoolsf.myschoolapp.com/api/schedule/MyDayCalendarStudentList/?scheduleDate='+cdate+'&personaId=1')
            page = req.read()
            req = reqD.open('https://bayschoolsf.myschoolapp.com/api/schedule/ScheduleCurrentDayAnnouncmentParentStudent/?mydayDate='+cdate+'&viewerId='+str(userinfo['UserInfo']['UserId'])+'&viewerPersonaId=2')
            page += ',' + req.read()
        s.wfile.write(page)

    def do_POST(s):
        l = int(s.headers['Content-Length'])
        data = urllib.unquote_plus(s.rfile.readline(l))
        LID = {}
        split = data.split("&")
        for i in split:
            tl = i.split('=')
            LID[tl[0]] = tl[1]
        if s.path == "/AStat":
            dat = b'{"assignmentIndexId":'+LID['indexID']+',"assignmentStatus":'+LID['stat']+'}'
            req = reqD.open('https://bayschoolsf.myschoolapp.com/api/assignment2/assignmentstatusupdate/?format=json&assignmentIndexId='+LID['indexID']+'&assignmentStatus='+LID['stat'], dat)
            req.read()
            s.send_response(204)
            s.send_header("Content-type", "application/json")
            s.send_header('Access-Control-Allow-Origin', '*')
            s.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
            s.send_header("Access-Control-Allow-Headers", "X-Requested-With")
            s.send_header("Access-Control-Allow-Headers", "Content-Type")
            s.end_headers()
        elif s.path == "/BCSlogin":
            req = reqD.open('https://bayschoolsf.myschoolapp.com/app')
            hp = req.read()
            #m = re.match('<div id="__AjaxAntiForgery">[\s]*<input name="__RequestVerificationToken" type="hidden" value="([\da-zA-Z-]{108})"[ ]*\/>[\s]*<\/div>', hp)
            login = {"From": '', "Username": LID['uname'], "Password": LID['pswd'], "remember":"false","InterfaceSource":"WebApp"}
            payload = urllib.urlencode(login)
            payload = payload.encode('UTF-8')
            req = reqD.open("https://bayschoolsf.myschoolapp.com/api/SignIn", payload)
            print(req.read())
            fcj.save(filename=cjp, ignore_discard=True, ignore_expires=True)
            s.send_response(301)
            s.send_header('Location','http://unified-assignment-center.appspot.com')
            s.end_headers()
        elif s.path == "/WAlogin":
            login = {"WebAssignUsername": LID['uname'], "WebAssignInstitution": "", "WebAssignPassword": LID['pswd']}
            payload = urllib.urlencode(login)
            payload = payload.encode('UTF-8')
            s.send_response(200)
            s.send_header("Content-type", "application/json")
            s.end_headers()
            req = reqD.open("https://webassign.net/login.html", payload)
            req.add_header('User-agent', 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:42.0) Gecko/20100101 Firefox/42.0')
            res = req.read()
            #externalRedirect('http://www.webassign.net/v4cgi/student.pl?UserPass=
            fcj.save()
            print(fcj)
            #TODO: handle redirect

if __name__ == '__main__':
    server_class = BaseHTTPServer.HTTPServer
    httpd = server_class((HOST_NAME, PORT_NUMBER), MyHandler)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
