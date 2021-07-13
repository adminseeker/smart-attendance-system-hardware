#!/usr/bin/env python3

import smtplib 
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import db
from datetime import datetime
import arrow

def send_mail(sender_mail,password,receivers_mail,subject,html_msg):
    try:

        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = sender_mail
        # Create the plain-text and HTML version of your message
        text = """\
        Absent Notification alert from SAS
        """
        html = """\
        <html>
        <body>
            """ + html_msg +"""
        </body>
        </html>
        """
        part1 = MIMEText(text, "plain")
        part2 = MIMEText(html, "html")
        message.attach(part1)
        message.attach(part2)
        text=message.as_string()
        obj = smtplib.SMTP('smtp.gmail.com', 587) 
        obj.starttls() 
        obj.login(sender_mail, password) 
        obj.sendmail(sender_mail, receivers_mail, text) 
        obj.quit()
    except Exception:
        print("Mail delivery failed.")

# to=["aravindarali121@gmail.com","aravindarali122@gmail.com","sasportal1337@gmail.com"]
# html_msg="<h1>Hello html testing 1 2 3...</h1><p>This is a paragraph</p>"
# send_mail("sasportal1337@gmail.com","portal1337",to,"SAS Notification Alert!",html_msg)


def get_room_id():
	room_id=""
	with open("/home/pi/smart-attendance-system-hardware/roomID","r") as file:
		room_id=file.readlines()[0].split("\n")[0]
		file.close()
	return room_id

def get_current_timing(timings):
	curr_time=datetime.now()
	for timing in timings:
		if  arrow.get(curr_time).time() >= arrow.get(timing['start_time']).time()  and arrow.get(curr_time).time() < arrow.get(timing['end_time']).time():
			return timing
	return False

def run():
    timings=db.get_timings(get_room_id())
    username=""
    password=""
    with open("/home/pi/smart-attendance-system-hardware/config.env", "r") as file:
        content=file.readlines()
        username=content[1].split("\n")[0]
        password=content[2]
        file.close()
    for timing in timings:
        absent_emails=db.get_absentees(timing)
        Class=timing['class']['class_name']
        start_time=str(arrow.get(timing['start_time']).time())
        end_time=str(arrow.get(timing['end_time']).time())
        subject="SAS Notification Alert!"
        html_msg="<h1>SAS Absent Alert</h1><p>Today you have missed the class</p><p>"+timing['class']['class_name'] +" during "+start_time +" - "+end_time+ "</p>"
        print(absent_emails,Class,start_time,end_time)
        send_mail(username,password,absent_emails,subject,html_msg)

run()