#!/usr/bin/env python3

from flask import Flask, request
from flask_cors import CORS
import base64
import pymongo
from bson.objectid import ObjectId
from datetime import datetime
import bcrypt
import json


mongo_url=""
with open("config.env", "r") as file:
    mongo_url=file.readlines()[0].split("\n")[0]
    file.close()

client = pymongo.MongoClient(mongo_url)

db = client.get_database("smart-attendance-system")

Users = db['users']

def id(oid):
    return ObjectId(oid)

app = Flask(__name__)
CORS(app)


def get_room_id():
	room_id=""
	with open("roomID","r") as file:
		room_id=file.readlines()[0].split("\n")[0]
		file.close()
	return room_id

def write_room_id(id):
    with open("roomID","w") as file:
        file.write(id)
        file.close()

@app.route('/api/rpi')
def home():
    return json.dumps({"msg": "Made with pain by adminseeker && Bhanu Prakash"})


@app.route('/api/rpi/login', methods=["POST"])
def login():
    if request.method=="POST":
        data=request.get_json()
        room_id=data['room_id']
        email=data['email']
        password=data['password']
        try:
            user=Users.find({"email":email})[0]
            if bcrypt.checkpw(password.encode(),user['password'].encode()) and user['role']=="admin":
                if room_id!="":
                    write_room_id(room_id)
                    return json.dumps({"msg": "Room ID Updated"})
                return json.dumps({"msg": "Room ID Empty!"})
            else:
                raise Exception('!')
        except:
           return json.dumps({"msg": "Authentication Error!"})

@app.route('/api/rpi/roomid', methods=["GET"])
def r():
    if request.method=="GET":
        rid=get_room_id()
        return json.dumps({"room_id":rid})

       



if __name__ == "__main__":
    app.run(debug=False,host="0.0.0.0")