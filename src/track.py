import cv2
import numpy
import os

face_cascade = cv2.CascadeClassifier("../res/haarcascade_frontalface_default.xml")
eye_cascade = cv2.CascadeClassifier("../res/haarcascade_eye.xml")

img = cv2.imread("../res/sample_pic.jpg")

gray_picture = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
faces = face_cascade.detectMultiScale(gray_picture, 1.3, 5)

for (x,y,w,h) in faces:
    cv2.rectangle(img,(x,y),(x+w,y+h),(255,255,0),2)
    gray_face = gray_picture[y:y+h, x:x+w]
    face = img[y:y+h, x:x+w]
    eyes = eye_cascade.detectMultiScale(gray_face)
    for (ex,ey,ew,eh) in eyes: 
        cv2.rectangle(face,(ex,ey),(ex+ew,ey+eh),(0,225,255),2)


cv2.imshow('img', img)
cv2.waitKey(0)
cv2.destroyAllWindows