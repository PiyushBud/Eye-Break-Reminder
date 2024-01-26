import cv2
import numpy as np
import tkinter as tk

FACE_PATH = "../res/haarcascade_frontalface_default.xml"
EYE_NOGLASSES_PATH = "../res/haarcascade_eye.xml"
EYE_GLASSES_PATH = "../res/haarcascade_eye_tree_eyeglasses.xml"

EYE_PATH = EYE_GLASSES_PATH
THRESHOLD = 65

CAMERA_WINDOW = 'image'
GRAY_WINDOW = 'gray image'

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
    eyel = None
    eyer = None
    for (x, y, w, h) in eye_coords:
        if y+h > face_height/2:
            continue
        eye_center = x + (w/2)
        if eye_center < face_width * 0.5:
            if max_left < w * h:
                left_eye = img[y:y + h, x:x + w]
                eyel = (x, y, w, h)
        else:
            if max_right < w * h:
                right_eye = img[y:y + h, x:x + w]
                eyer = (x, y, w, h)
    if left_eye is not None:
        cv2.rectangle(img,(eyel[0],eyel[1]),(eyel[0]+eyel[2],eyel[1]+eyel[3]),(255,255,0),2)
    if right_eye is not None:
        cv2.rectangle(img,(eyer[0],eyer[1]),(eyer[0]+eyer[2],eyer[1]+eyer[3]),(255,255,0),2)
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
    threshold = cv2.getTrackbarPos('threshold', GRAY_WINDOW)
    _, thresh_img = cv2.threshold(img_gray, threshold, 255, cv2.THRESH_BINARY)
    thresh_img = cv2.erode(thresh_img, None, iterations=2)
    thresh_img = cv2.dilate(thresh_img, None, iterations=4)
    thresh_img = cv2.medianBlur(thresh_img, 5)
    keyPoints = detector.detect(thresh_img)
    return keyPoints

def find_contours(img):
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    threshold = cv2.getTrackbarPos('threshold', GRAY_WINDOW)
    _, thresh_img = cv2.threshold(img_gray, threshold, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(thresh_img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    for contour in contours:
        approx = cv2.approxPolyDP(contour, 3, True)
        center, radius = cv2.minEnclosingCircle(approx)
    cv2.drawContours(img, contours, -1, (0,255,0), 3)

def nothing(val):
    return

def thresh_frame(img):
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    threshold = cv2.getTrackbarPos('threshold', GRAY_WINDOW)
    _, thresh_img = cv2.threshold(img_gray, threshold, 255, cv2.THRESH_BINARY)
    # contours, _ = cv2.findContours(thresh_img, cv2.RETR_TREE,
    # cv2.CHAIN_APPROX_SIMPLE)
    # # drawing contours
    # cv2.drawContours(thresh_img, contours, -1, (0, 255, 0), 3)
    return thresh_img


def main():
    face_cascade = cv2.CascadeClassifier(FACE_PATH)
    eye_glasses_cascade = cv2.CascadeClassifier(EYE_PATH)

    detector_params = cv2.SimpleBlobDetector_Params()
    detector_params.filterByArea = True
    detector_params.maxArea = 1500
    detector = cv2.SimpleBlobDetector_create(detector_params)
    
    cap = cv2.VideoCapture(0)
    cv2.namedWindow(CAMERA_WINDOW)
    cv2.namedWindow(GRAY_WINDOW)
    cv2.createTrackbar('threshold', GRAY_WINDOW, 0, 100, nothing)
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
                    # find_contours(eye)
        cv2.imshow(CAMERA_WINDOW, frame)
        cv2.imshow(GRAY_WINDOW, thresh_frame(frame).copy())
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()

def single_image():
    img = cv2.imread("../res/sample_pic1.jpg")
    face_cascade = cv2.CascadeClassifier(FACE_PATH)
    eye_cascade = cv2.CascadeClassifier(EYE_PATH)
    face = find_face(img, face_cascade)
    if face is not None:
        eyes = find_eyes(face, eye_cascade)
        for eye in eyes:
            if eye is not None:
                img_gray = cv2.cvtColor(eye, cv2.COLOR_BGR2GRAY)
                threshold = 64
                _, thresh_img = cv2.threshold(img_gray, threshold, 255, cv2.THRESH_BINARY)
                contours, _ = cv2.findContours(thresh_img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
                for contour in contours:
                    approx = cv2.approxPolyDP(contour, 3, True)
                    center, radius = cv2.minEnclosingCircle(approx)
                cv2.drawContours(img, contours, -1, (0,0,255), 1)

    else:
        print("Could not find face.")
        return

    cv2.namedWindow(CAMERA_WINDOW)
    cv2.namedWindow(GRAY_WINDOW)
    cv2.createTrackbar('threshold', GRAY_WINDOW, 0, 100, nothing)
    while True:
        cv2.imshow(CAMERA_WINDOW, img)
        cv2.imshow(GRAY_WINDOW, thresh_frame(img).copy())
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
