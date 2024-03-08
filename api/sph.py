import requests
from bs4 import BeautifulSoup

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
        print(self.password)
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
                print(self.cookies)
                return cookie.value
                
    def requestSph(self, route):
        print(self.cookies, sphHeaders)
        response = requests.post("https://start.schulportal.hessen.de/" + route, cookies=self.cookies,  headers=sphHeaders)
        print(response)
        soup = BeautifulSoup(response.text, 'html.parser')
        return soup
    
    def getVPlan(self):
        site = self.requestSph("vertretungsplan.php")
        table = site.select_one('table[id*=vtable]')
        tableArray = []

        if table:
            rows = table.find_all('tr')
            for row in rows:
                rowArray = []
                cells = row.find_all('td')
                if len(cells) >= 8: 
                    for x in range(7):
                        rowArray.append(cells[x].get_text(strip=True))
                if len(rowArray) > 0:
                    tableArray.append(rowArray)

        return tableArray
    
    def getCourses(self):
        courses = self.requestSph("lerngruppen.php")
        rows = courses.select('#LGs tr')[1:]
        data = [row.select('td:nth-of-type(2)')[0].get_text(strip=True) for row in rows]
        
        return data
    
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

