from flask import Flask, request
import sph as sphHandler

app = Flask(__name__)

@app.route('/')
def home():
    return 'Hello, World!'

@app.get("/today")
def today():
    username = request.args.get('username')
    password = request.args.get('password')

    if password == None or username == None:
        return {"message": "Missing parameters"}

    sph = sphHandler.Sph(username, password)

    if "sid" not in sph.cookies:
        return {"error": "Incorrect password or username"}

    courseNumbers = []
    courses = sph.getCourses()
    courseNumbers.append('m5')

    for course in courses:
        courseNumbers.append(sph.parseCourseNumbers(course))

    if len(courseNumbers) == 0:
        return {"error": "Could not get user courses"}

    vplan = sph.getVPlan()
    
    vplanCourses = []

    for entry in vplan:
        if len(entry) > 4:
            lowerArray = [x.lower() for x in courseNumbers]
            if entry[4].lower() in lowerArray:
                vplanCourses.append(entry)

    return vplanCourses
