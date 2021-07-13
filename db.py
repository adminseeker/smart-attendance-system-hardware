#!/usr/bin/env python3

import pymongo
from bson.objectid import ObjectId
from datetime import datetime
import arrow


mongo_url=""
with open("/home/pi/smart-attendance-system-hardware/config.env", "r") as file:
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
     
def verify_access_id(access_id,timing):
    try:
        student = Students.find({"access_id":access_id})[0]
        print(student['_id'])
        found=False
        for i in timing['class']['students']:
            print(i['student'],student['_id'])
            if i['student']== student['_id']:
                found=True
                return "student", student
    except:
        pass
    try:
        teacher = Teachers.find({"access_id":access_id})[0]
        # print(teacher)
        print(timing)
        print(timing['class']['teacher'],teacher['_id'])
        if timing['class']['teacher']==teacher['_id']:
            found=True
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
            try:
                start_time=timing['start_time'].time()
                end_time=timing['end_time'].time()
                curr_date=curr_time.date()
                start_datetime = datetime.combine(curr_date,start_time)
                end_datetime = datetime.combine(curr_date,end_time)
                print(start_datetime," ",end_datetime)
                y=StudentAttendances.find({"student":user['_id'],"timing":timing['_id'],"lastUpdated":{"$gte":start_datetime,"$lt":end_datetime}})[0]
                print("found already"," from db")
            except Exception as e:
                print(e)
                x=StudentAttendances.insert_one({"student":user['_id'],"timing":timing['_id'],"class":timing['class']['_id'],"lastUpdated":curr_time})
                print("Added new entry"," from db")
            return True
        elif valid=="teacher":
            try:
                start_time=timing['start_time'].time()
                end_time=timing['end_time'].time()
                curr_date=curr_time.date()
                start_datetime = datetime.combine(curr_date,start_time)
                end_datetime = datetime.combine(curr_date,end_time)
                print(start_datetime," ",end_datetime)
                y=TeacherAttendances.find({"teacher":user['_id'],"lastUpdated":{"$gte":start_datetime,"$lt":end_datetime}})[0]
                print("found already"," from db")
            except Exception as e:
                print(e)
                x=TeacherAttendances.insert_one({"teacher":user['_id'],"timing":timing['_id'],"class":timing['class']['_id'],"lastUpdated":curr_time})
                # print(1)
                y=Classes.find_one_and_update({"_id":timing['class']['_id']},{"$inc":{"total_classes":1}})
                print("classes",y)
                # print(2)
                print("Added new entry"," from db")
            return True
        elif valid=="admin":
            print(curr_time)
            y=AdminAttendances.find_one_and_update({"admin":user['_id'],"lastUpdated":curr_time.date().isoformat()},{"$set":{"admin":user['_id'],"lastUpdated":curr_time.date().isoformat()}},upsert=True)
            return "admin"
    else:
        return False

def get_absentees(timing):
    try:
        start_time=timing['start_time'].time()
        end_time=timing['end_time'].time()
        curr_date=datetime.now().date()
        start_datetime = datetime.combine(curr_date,start_time)
        end_datetime = datetime.combine(curr_date,end_time)
        Class = timing['class']
        students=Class['students']
        student_present_ids=[]
        student_absent_ids=[]
        for entry in StudentAttendances.find({"timing":timing['_id'],"lastUpdated":{"$gte":start_datetime,"$lt":end_datetime}}):
            student_present_ids.append(entry['student'])
        for student in students:
            if student['student'] not in student_present_ids:
                student_absent_ids.append(student['student'])
        print(student_absent_ids)
        absent_emails=[]
        student_uids=[]
        for student in Students.find({"_id":{"$in":student_absent_ids}}):
            student_uids.append(student['user'])
        for user in Users.find({"_id":{"$in":student_uids}}):
            absent_emails.append(user['email'])
        #print(absent_emails)
        return absent_emails
    except Exception as e:
        print(e)




