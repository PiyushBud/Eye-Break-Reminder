import cv2
import numpy as np
import os

FACE_PATH = "../res/haarcascade_frontalface_default.xml"
EYE_PATH = "../res/haarcascade_eye.xml"
EYE_GLASSES_PATH = "../res/haarcascade_eye_tree_eyeglasses.xml"
THRESHOLD = 65

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

def trim_brows(img):
    height, width = img.shape[:2]
    eyebrow_h = int(height / 4)
    return img[eyebrow_h:height, 0:width]

def find_face(img, classifier):
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    face_coords = classifier.detectMultiScale(img_gray, 1.3, 5)
    max = 0
    face = None
    for (x,y,w,h) in face_coords:
        if max < w * h:
            face = img[y:y+h, x:x+w]
        # cv2.rectangle(img,(x,y),(x+w,y+h),(255,255,0),2)
    return face

def process_blob(img, detector):
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    threshold = cv2.getTrackbarPos('threshold', 'image')
    _, thresh_img = cv2.threshold(img_gray, threshold, 255, cv2.THRESH_BINARY)
    thresh_img = cv2.erode(thresh_img, None, iterations=2)
    thresh_img = cv2.dilate(thresh_img, None, iterations=4)
    thresh_img = cv2.medianBlur(thresh_img, 5)
    keyPoints = detector.detect(thresh_img)
    return keyPoints

def nothing(val):
    return
def main():
    face_cascade = cv2.CascadeClassifier(FACE_PATH)
    eye_glasses_cascade = cv2.CascadeClassifier(EYE_GLASSES_PATH)

    detector_params = cv2.SimpleBlobDetector_Params()
    detector_params.filterByArea = True
    detector_params.maxArea = 1500
    detector = cv2.SimpleBlobDetector_create(detector_params)
    
    cap = cv2.VideoCapture(0)
    cv2.namedWindow('image')
    cv2.createTrackbar('threshold', 'image', 0, 100, nothing)
    while True:
        _, frame = cap.read()
        face = find_face(frame, face_cascade)
        if face is not None:
            eyes = find_eyes(face, eye_glasses_cascade)
            for eye in eyes:
                if eye is not None:
                    # eye = trim_brows(eye)
                    keyPoints = process_blob(eye, detector)
                    cv2.drawKeypoints(eye, keyPoints, eye, (0, 0, 255), cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
        cv2.imshow('image', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
