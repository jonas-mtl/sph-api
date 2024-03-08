from flask import Flask, request
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)
            
sphHeaders = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0",
    "Accept": "*/*",
    "Accept-Language": "de,en-US;q=0.7,en;q=0.3",
    "Accept-Encoding": "gzip, deflate, br",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "X-Requested-With": "XMLHttpRequest",
    "Origin": "https://start.schulportal.hessen.de",
    "Referer": "https://start.schulportal.hessen.de/vertretungsplan.php",
    "Connection": "keep-alive",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin"
}
loginHeaders = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Content-Type": "application/x-www-form-urlencoded",
    "Sec-GPC": "1",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-User": "?1"
}

class Sph:
    cookies = {}

    username = ""
    password = ""

    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.getSessionID()

    def getSessionID(self):
        data = {
            "url": "",
            "timezone": "1",
            "skin": "sp",
            "user2": self.username,
            "user": "5220." + self.username,
            "password": self.password
        }
        response = requests.post("https://login.schulportal.hessen.de/?i=5220", headers=loginHeaders, data=data)
        for cookie in response.cookies:
            if cookie.name == 'sid':
                self.cookies = {
                    "schulportal_lastschool": "5220",
                    "sph-login-upstream": "2",
                    "schulportal_logindomain": "login.schulportal.hessen.de",
                    "i": "5220",
                    "sid": cookie.value,
                    "SPH-Session": "572feaefbf77008b4c7954e9f5896f379fb358987c3234d27dedff86ad484c59"
                }
                return cookie.value
                
    def requestSph(self, route):
        response = requests.post("https://start.schulportal.hessen.de/" + route, cookies=self.cookies,  headers=sphHeaders)
        soup = BeautifulSoup(response.text, 'html.parser')
        return soup
    
    def getVPlan(self, day):
        if day not in [0, 1]:
            raise ValueError("Day parameter must be 0 or 1")

        site = self.requestSph("vertretungsplan.php")

        table = site.find('table[id*=vtable]')
        tableArray = []

        tables = site.find_all("table", id=lambda x: x and "vtable" in x)

        rows = tables[day].find_all('tr')
        for row in rows:
            rowArray = []
            cells = row.find_all('td')
            if len(cells) >= 8: 
                for x in range(7):
                    rowArray.append(cells[x].get_text(strip=True))
            if len(rowArray) > 0:
                tableArray.append(rowArray)

        print(tableArray)
        return tableArray
    
    def getCourses(self):
        courses = self.requestSph("lerngruppen.php")
        rows = courses.select('#LGs tr')[1:]
        data = [row.select('td:nth-of-type(2)')[0].get_text(strip=True) for row in rows]
        
        return data
    
    def getHomework(self):
        site = self.requestSph("meinunterricht.php")
        homework_divs = site.find_all("div", class_=lambda c: c and "realHomework" in c)

        homework = []

        for div in homework_divs:
            content = div.get_text(strip=True)

            printable_parent = div.find_parent("tr", class_="printable")
            homework_index = printable_parent.get("data-entry")
            homework_id = printable_parent.get("data-book")
            
            span_name = printable_parent.find("span", class_="name")

            content_decoded = content.encode("utf-8").decode("utf-8")

            homeworkObj = {
                "class": span_name.get_text(strip=True).split(" ")[0],
                "content": content_decoded
            }

            homework.append(homeworkObj)

            # mark as done
            requests.post("https://start.schulportal.hessen.de/meinunterricht.php" , cookies=self.cookies,  headers=sphHeaders, data= {
                "a": "sus_homeworkDone",
                "id": homework_id,
                "entry": homework_index
            })

        return homework
    
    def parseCourseNumbers(self, course):
        start_index = course.find("(")
        if start_index != -1:
            end_index = course.find(")", start_index)
            if end_index != -1:
                substring_inside_parentheses = course[start_index + 1:end_index]
                substring_inside_parentheses = substring_inside_parentheses[2:].split(" - ")[0].replace("0", "")

                if "POWI" in substring_inside_parentheses: substring_inside_parentheses = substring_inside_parentheses.replace("POWI", "PW")
                if "INFO" in substring_inside_parentheses: substring_inside_parentheses = substring_inside_parentheses.replace("INFO", "I")
                if "KU" in substring_inside_parentheses: substring_inside_parentheses = substring_inside_parentheses.replace("KU", "K")
                if "SPO" in substring_inside_parentheses: substring_inside_parentheses = substring_inside_parentheses.replace("SPO", "S")
                if "REV" in substring_inside_parentheses: substring_inside_parentheses = substring_inside_parentheses.replace("REV", "EV")

                return substring_inside_parentheses

@app.route('/')
def home():
    return {"message": "Welcome to sph-api"}

@app.get("/plan/<int:page_id>")
def today(page_id):
    
    if page_id > 1 or None:
        return {"error": "Plan index out of range [0-1]"}, 400 

    username = request.headers.get('username')
    password = request.headers.get('password')

    if password == None or username == None:
        return {"error": "Missing parameters"}, 400 

    sph = Sph(username, password)

    if "sid" not in sph.cookies:
        return {"error": "Incorrect password or username"}, 401 

    courseNumbers = []
    courses = sph.getCourses()
    courseNumbers.append('m5')
    courseNumbers.append('et5')

    for course in courses:
        courseNumbers.append(sph.parseCourseNumbers(course))

    if len(courseNumbers) == 0:
        return {"error": "Could not get user courses"}, 500

    vplan = sph.getVPlan(page_id)
    
    vplanCourses = []

    for entry in vplan:
        if len(entry) > 4:
            lowerArray = [x.lower() for x in courseNumbers]
            if entry[4].lower() in lowerArray:
                vplanCourses.append(entry)
    
    headers = {}
    for i, row in enumerate(vplanCourses, start=1):
        headers[str(i)] = row

    return headers

@app.get('/classes')
def classes():
    username = request.headers.get('username')
    password = request.headers.get('password')

    if password == None or username == None:
        return {"message": "Missing parameters"}, 400 

    sph = Sph(username, password)

    if "sid" not in sph.cookies:
        return {"error": "Incorrect password or username"}, 401 
    
    homework = sph.getHomework()

    return homework


@app.route('/favicon.ico')
def favicon():
    return