#!/usr/bin/env python3

import pymongo
from bson.objectid import ObjectId
from datetime import datetime


mongo_url=""
with open("config.env", "r") as file:
    mongo_url=file.readlines()[0].split("\n")[0]
    file.close()

client = pymongo.MongoClient(mongo_url)

db = client.get_database("smart-attendance-system")

Rooms = db['rooms']
Timings=db['timings']
Classes=db['classes']
Users=db['users']
Admins=db['admins']
Teachers=db['teachers']
Students=db['students']
StudentAttendances=db['studentAttendances']
TeacherAttendances=db['teacherAttendances']
AdminAttendances=db['adminAttendances']

def id(oid):
    return ObjectId(oid)

# def get_schedule():
#     today=datetime.now().strftime("%w")
    

def get_timings(room_id):
    room=Rooms.find({"_id":id(room_id)})[0]
    room_timings = room['timings']
    timings=[]
    today=datetime.now().strftime("%w")
    for t in room_timings:
        try:
            timing=Timings.find({"_id":t['timing'],"day":today})[0]
            timing['class']=Classes.find({"_id":timing['class']})[0]
            timings.append(timing)
        except:
            continue
    
    return timings

def get_admin_access_ids():
    access_ids=[]
    for admin in Admins.find({},{"admin_access_id":1}):
        access_ids.append(admin['admin_access_id'])
    return access_ids
     
def verify_access_id(access_id):
    try:
        student = Students.find({"access_id":access_id})[0]
        return "student", student
    except:
        pass
    try:
        teacher = Teachers.find({"access_id":access_id})[0]
        return "teacher",teacher
    except:
        pass
    try:
        admin = Admins.find({"access_id":access_id})[0]
        return "admin",admin
    except:
        pass
    
    return False,{}

#print(verify_access_id("140741455635"))

def mark_attendance(access_id,timing,curr_time,valid,user):
    if valid:
        if valid=="student":
            x=StudentAttendances.find_one_and_update({"student":user['_id'],"timing":timing['_id']},{"$set":{"student":user['_id'],"timing":timing['_id'],"class":timing['class']['_id'],"lastUpdated":curr_time}},upsert=True)
            return True
        elif valid=="teacher":
            x=TeacherAttendances.find_one_and_update({"teacher":user['_id'],"timing":timing['_id']},{"$set":{"teacher":user['_id'],"timing":timing['_id'],"class":timing['class']['_id'],"lastUpdated":curr_time}},upsert=True)
            return True
        elif valid=="admin":
            print(curr_time)
            y=AdminAttendances.find_one_and_update({"admin":user['_id'],"lastUpdated":curr_time.date().isoformat()},{"$set":{"admin":user['_id'],"lastUpdated":curr_time.date().isoformat()}},upsert=True)
            return "admin"
    else:
        return False