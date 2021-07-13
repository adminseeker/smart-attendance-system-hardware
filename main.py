#!/usr/bin/env python3

from os import access
import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522
import time
import paho.mqtt.client as paho
import requests
import sys
import json
import db
from datetime import datetime
import arrow

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
red=4
green=17
blue=16
yellow=20
buzz=27
GPIO.setup(red,GPIO.OUT)
GPIO.setup(green,GPIO.OUT)
GPIO.setup(blue,GPIO.OUT)
GPIO.setup(yellow,GPIO.OUT)
GPIO.setup(buzz,GPIO.OUT)

broker="aravindweb.in"
port=1883
client1= paho.Client("client1")

def on_message(client, userdata, message):
	msg=message.payload.decode("utf-8")
	print(msg)
	if(msg=="true"):
		GPIO.output(red,GPIO.LOW)
		GPIO.output(green,GPIO.HIGH)
		time.sleep(2)
	else:
		GPIO.output(buzz,GPIO.HIGH)

def get_room_id():
	room_id=""
	with open("/home/pi/smart-attendance-system-hardware/roomID","r") as file:
		room_id=file.readlines()[0].split("\n")[0]
		file.close()
	return room_id

def get_reset_id():
	reset_id=""
	with open("/home/pi/smart-attendance-system-hardware/resetID","r") as file:
		reset_id=file.readlines()[0].split("\n")[0]
		file.close()
	return reset_id

def reset_mode():
	try:
		GPIO.output(red,GPIO.HIGH)
		GPIO.output(green,GPIO.HIGH)
		room_id=get_room_id()
		reset_id=get_reset_id()
		admin_access_ids=db.get_admin_access_ids()
		timings=db.get_timings(room_id)
		GPIO.output(red,GPIO.LOW)
		GPIO.output(green,GPIO.LOW)
		return room_id,reset_id,admin_access_ids,timings
	except:
		print("failed to start! Check room id...")
		print("restarting in 5 seconds...")
		time.sleep(5)
		reset_mode()

def admin_mode():
	GPIO.output(blue,GPIO.HIGH)
	admin=1
	while admin:
		try:
			GPIO.output(red,GPIO.HIGH)
			GPIO.output(buzz,GPIO.LOW)
			GPIO.output(green,GPIO.LOW)
			client1.connect(broker,port)
			id, output = reader.read()
			id=str(id)
			print(id)
			data={"id":id}
			toSend=json.dumps(data)
			if id in admin_access_ids:
				admin=0
				GPIO.output(blue,GPIO.LOW)
				break
			if id==reset_id:
				GPIO.output(blue,GPIO.LOW)
				admin=0
				return id
			client1.publish("rfid_add",toSend)
			client1.loop_start()   
			res,mid=client1.subscribe("rfid_reply")
			client1.on_message=on_message
			time.sleep(2)                  
			client1.loop_stop()
			
		except KeyboardInterrupt:
			break
		except:
			print("execption in reading rfid")
			continue

reader = SimpleMFRC522()

room_id,reset_id,admin_access_ids,timings = reset_mode()
	


def get_current_timing(timings):
	curr_time=datetime.now()
	for timing in timings:
		if  arrow.get(curr_time).time() >= arrow.get(timing['start_time']).time()  and arrow.get(curr_time).time() < arrow.get(timing['end_time']).time():
			return timing,curr_time
	return False,curr_time

try:
	pass
	while True:
		try:
			print(room_id,'room_id')
			GPIO.output(red,GPIO.HIGH)
			GPIO.output(buzz,GPIO.LOW)
			GPIO.output(green,GPIO.LOW)
			GPIO.output(blue,GPIO.LOW)
			GPIO.output(yellow,GPIO.LOW)
			client1.connect(broker,port)
			id, output = reader.read()
			id=str(id)
			print(id)
			data={"id":id}
			toSend=json.dumps(data)
			r=""
			if id in admin_access_ids:
				r=admin_mode()
				continue
			if r==reset_id or id==reset_id:
				room_id,reset_id,admin_access_ids,timings = reset_mode()
				continue
			current_timing,curr_time=get_current_timing(timings)
			valid,user=db.verify_access_id(id,current_timing)
			if current_timing or valid=="admin":
				GPIO.output(yellow,GPIO.LOW)
				valid=db.mark_attendance(id,current_timing,curr_time,valid,user)
				print(valid)
				if valid:
					GPIO.output(red,GPIO.LOW)
					GPIO.output(buzz,GPIO.LOW)
					GPIO.output(green,GPIO.HIGH)
					time.sleep(2)
				else:
					GPIO.output(red,GPIO.HIGH)
					GPIO.output(buzz,GPIO.HIGH)
					GPIO.output(green,GPIO.LOW)
					time.sleep(1)					
			else:
				GPIO.output(buzz,GPIO.HIGH)
				GPIO.output(yellow,GPIO.HIGH)
				time.sleep(2)
			
			
		except KeyboardInterrupt:
			break
		except Exception as e:
			print(e)
			print("execption in reading rfid")
			continue
finally:
        GPIO.cleanup()
