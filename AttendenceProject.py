from fileinput import FileInput
import cv2
import numpy as np
import face_recognition
import os
import mysql.connector

import csv
from datetime import datetime

# from PIL import ImageGrab

import pandas as pd
from datetime import datetime

conn = mysql.connector.connect(host="localhost",port="3307",user="root",password="pass",database="test")
cursor= conn.cursor()

d = datetime.now()
only_date, only_time = d.date(), d.time()
date = str(only_date)
df = pd.read_csv("sample.csv")
df[date] = "0"
df.to_csv("sample.csv", index=False)

path = 'image'
images = []
classNames = []
student=set()
myList = os.listdir(path)
print(myList)
for cl in myList:
    curImg = cv2.imread(f'{path}/{cl}')
    images.append(curImg)
    classNames.append(os.path.splitext(cl)[0])
print(classNames)
def updateInitialAttendance():
    selectquery = "select * from users"
    cursor.execute(selectquery)
    records = cursor.fetchall()
    #print("no. of students in the class", cursor.rowcount)
    for row in records:
        # print("student id: ", row[0])
        # print("student roll: ", row[1])
        # print("student email: ", row[2])
        # print()
        updateQuery="UPDATE users SET attendance = %s WHERE fullname= %s"
        att=row[4]
        #print(type(att))
     #   print(att)
        att=att+"0"
        value=(att,row[1])
        try:
            cursor.execute(updateQuery,value)
            conn.commit()
            print("updated")
        except:
             print("unable to update data")
updateInitialAttendance()

def MarkPresent(roll):
    roll= roll.lower()
    selectquery = "select * from users where fullname = %s"
    value=(roll,)
    cursor.execute(selectquery,value)
    records = cursor.fetchall()
    #print("no. of students in the class", cursor.rowcount)
    for row in records:
        # print("student id: ", row[0])
        # print("student roll: ", row[1])
        # print("student email: ", row[2])
        # print()
        updateQuery = "UPDATE users SET attendance = %s WHERE fullname = %s"
        att = row[4]
        temp=list(att)
        temp[-1]='1';
        att= "".join(temp)
        # print(type(att))
        #print(att)
        value = (att, row[1])
        try:
            cursor.execute(updateQuery, value)
            conn.commit()
            print("updated")
        except:
            print("unable to update data")

def findEncodings(images):
    encodeList = []
    for img in images:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(img)[0]
        encodeList.append(encode)
    return encodeList


def markAttendance(name):
    if name not in student:
        student.add(name)
        df = pd.read_csv("sample.csv")
        df.loc[df["Roll_NO"] ==name, date] ="1"
        df.to_csv("sample.csv", index=False)
        name=name.lower()
        print(name)
       # print(len(name))
        MarkPresent(name);
        #print(type(name))
        #print(name)

    return 1


encodeListKnown = findEncodings(images)
print('Encoding Complete')

cap = cv2.VideoCapture(0)

while True:
    flag = 0
    success, img = cap.read()
    # img = captureScreen()
    imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
    imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

    facesCurFrame = face_recognition.face_locations(imgS)
    encodesCurFrame = face_recognition.face_encodings(imgS, facesCurFrame)

    for encodeFace, faceLoc in zip(encodesCurFrame, facesCurFrame):
        matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
        faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)
        # print(faceDis)
        matchIndex = np.argmin(faceDis)

        if matches[matchIndex]:
            name = classNames[matchIndex].upper()
            # print(name)
            y1, x2, y2, x1 = faceLoc
            y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
            cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.rectangle(img, (x1, y2 - 35), (x2, y2), (0, 255, 0), cv2.FILLED)  # to filled the name
            cv2.putText(img, name, (x1 + 6, y2 - 6), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)
            markAttendance(name)
    cv2.imshow('Webcam', img)
    cv2.waitKey(1)
