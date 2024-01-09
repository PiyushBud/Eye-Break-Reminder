import cv2
import numpy as np
import os

FACE_PATH = "../res/haarcascade_frontalface_default.xml"
EYE_PATH = "../res/haarcascade_eye.xml"
EYE_GLASSES_PATH = "../res/haarcascade_eye_tree_eyeglasses.xml"

face_cascade = cv2.CascadeClassifier(FACE_PATH)
eye_glasses_cascade = cv2.CascadeClassifier(EYE_GLASSES_PATH)

img = cv2.imread("../res/sample_pic.jpg")

detector_params = cv2.SimpleBlobDetector_Params()
detector_params.filterByArea = True
detector_params.maxArea = 1500
detector = cv2.SimpleBlobDetector_create(detector_params)

# Filter out bad eye detections
def find_eyes(img, classifier):
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    eye_coords = classifier.detectMultiScale(img_gray)
    face_height = np.size(img, 0)
    face_width = np.size(img, 1)
    max_left = 0
    max_right = 0
    left_eye = None
    right_eye = None
    for (x, y, w, h) in eye_coords:
        if y+h > face_height/2:
            continue
        eye_center = x + (w/2)
        if eye_center < face_width * 0.5:
            if max_left < w * h:
                left_eye = img[y:y + h, x:x + w]
        else:
            if max_right < w * h:
                right_eye = img[y:y + h, x:x + w]
    return (left_eye, right_eye)

def find_face(img, classifier):
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    face_coords = classifier.detectMultiScale(img_gray, 1.3, 5)
    max = 0
    for (x,y,w,h) in face_coords:
        if max < w * h:
            face = img[y:y+h, x:x+w]
        # cv2.rectangle(img,(x,y),(x+w,y+h),(255,255,0),2)
    return face

face = find_face(img, face_cascade)
left_eye, right_eye = find_eyes(face, eye_glasses_cascade)
height, width = left_eye.shape[:2]
eyebrow_h = int(height / 4)
left_eye = left_eye[eyebrow_h:height, 0:width]

threshold = 65
gray = cv2.cvtColor(left_eye, cv2.COLOR_BGR2GRAY)

_, thresh_img = cv2.threshold(gray, threshold, 255, cv2.THRESH_BINARY)
thresh_img = cv2.erode(thresh_img, None, iterations=2)
thresh_img = cv2.dilate(thresh_img, None, iterations=4)
thresh_img = cv2.medianBlur(thresh_img, 5)
keypoints = detector.detect(thresh_img)
cv2.drawKeypoints(thresh_img, keypoints, thresh_img, (0, 0, 255), cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)


cv2.imshow('img', thresh_img)
cv2.waitKey(0)
cv2.destroyAllWindows