import cv2
import time
import mediapipe as mp
import tkinter as tk
from PIL import ImageTk, Image

MODEL_PATH = "../res/face_landmarker.task"

EYES = [468,478]

calibration = []

mode_calibrate = False

main_window = tk.Tk()

# Face mesh set up
BaseOptions = mp.tasks.BaseOptions
FaceLandmarker = mp.tasks.vision.FaceLandmarker
FaceLandmarkerOptions = mp.tasks.vision.FaceLandmarkerOptions
VisionRunningMode = mp.tasks.vision.RunningMode

options = FaceLandmarkerOptions(
    base_options=BaseOptions(model_asset_path=MODEL_PATH),
    running_mode=VisionRunningMode.IMAGE,
    num_faces=1)

landmarker = FaceLandmarker.create_from_options(options)

# GUI work
def main():
    mode_calibrate = True
    global main_window

    if main_window is not None:
        main_window.destroy()

    main_window = tk.Tk()
    main_window.columnconfigure(0, minsize=200,weight=1)
    main_window.rowconfigure([0, 1, 2], minsize=50,weight=1)

    label = tk.Label(master=main_window, text="Your eyes are gonna need a break")
    label.grid(row=0,column=0,sticky="s",pady=5)

    button_opencv = tk.Button(master=main_window, text="OpenCV")
    button_opencv.grid(row=1,column=0,sticky="nsew",padx=20,pady=10)

    button_media = tk.Button(master=main_window,text="MediaPipe", command=tracking_menu)
    button_media.grid(row=2,column=0,sticky="nsew",padx=20, pady=10)

    main_window.mainloop()

# Signal to mark landmark coords as a calibration point
def flip_calibrate_mode():
    global mode_calibrate, cap

    _, frame = cap.read()
    if frame is None:
        return    
    mode_calibrate = True

# Start detection
def start_detect():
    
    global label_gaze, mode_calibrate, label_cam, cap

    baseline_point = (0,0)

    _, frame = cap.read()
    if frame is None:
        return
    frame = cv2.flip(frame, 1)
    frame_h, frame_w, _ = frame.shape # frame dims to calculate x and y coords
    # opencv to mp image
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame)


    landmark_points = landmarker.detect(mp_image)
    if landmark_points:
        landmarks = landmark_points.face_landmarks
        if landmarks:

            landmark = landmarks[0]
            # Actual landmark points
            for id, point in enumerate(landmark[226:227] + landmark[468:469]): # Slice for pupil landmarks                        

                # Corner of eye window
                if (id == 0):
                    x = int(point.x * frame_w)
                    y = int(point.y * frame_h)
                    baseline_point = (x,y)
                
                elif (id == 1):
                    x = abs(int(point.x * frame_w) - baseline_point[0])
                    y = abs(int(point.y * frame_h) - baseline_point[1])

                    true_x = int(point.x * frame_w)
                    true_y = int(point.y * frame_h)

                    cv2.circle(frame, (true_x,true_y), 1, (0,0,255), 1)
                    if len(calibration) == 2:
                        if calibration[1][1]-1 <= y and y <= calibration[0][1]+1 and \
                            calibration[0][0]-1 <= x and x <= calibration[1][0]+1:
                            label_gaze.config(text="Looking? YES")
                        else:
                            label_gaze.config(text="Looking? NO")
                    elif mode_calibrate:
                        calibration.append((x,y))
                        label_gaze.config(text="Now look at the bottom right of your monitor\n and hit calibrate")
                        mode_calibrate = False
    img_arr = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
    img = Image.fromarray(img_arr)
    imgtk = ImageTk.PhotoImage(image=img)
    label_cam.imgtk = imgtk
    label_cam.configure(image=imgtk)
    label_cam.after(1, start_detect)

# Start the webcam
def start_cam(button_start: tk.Button):
    global main_window, cap
    if button_start.cget("text") == "Start":
        cap = cv2.VideoCapture(0)
        button_start.config(text="Stop")
        label_gaze.config(text="Look at the top left corner of your monitor \nand hit calibrate")            
        start_detect()
    else:
        cap.release()
        button_start.config(text="Start")

# Menu for displaying webcam footage
def tracking_menu():

    global main_window, label_gaze, label_cam

    if main_window is not None:
        main_window.destroy()

    main_window = tk.Tk()
    main_window.columnconfigure([0, 1], weight=1)
    main_window.rowconfigure([0, 1], weight=1)

    frame_buttons = tk.Frame(master=main_window, width=200, height=500, bg="grey")
    frame_buttons.grid(row=0, column=0, padx=10, pady=10)

    frame_picture = tk.Frame(master=main_window, width=500, height=500, bg="skyblue")
    frame_picture.grid(row=0, column=1, padx=10, pady=10)

    img_arr = cv2.cvtColor(cv2.imread("../res/bg.JPG"), cv2.COLOR_BGR2RGBA)
    img = Image.fromarray(img_arr)
    imgtk = ImageTk.PhotoImage(image=img)

    label_cam = tk.Label(master=frame_picture)
    label_cam.pack()
    label_cam.imgtk = imgtk
    label_cam.configure(image=imgtk)

    label_gaze = tk.Label(master=frame_buttons, text="Calibration required",bg=frame_buttons["background"])
    label_gaze.grid(row=0,column=0,padx=5,pady=5)

    button_start = tk.Button(master=frame_buttons, text="Start")
    button_start.config(command=lambda b=button_start:start_cam(b))
    button_start.grid(row=1,column=0,padx=5,pady=5)

    button_calibrate = tk.Button(master=frame_buttons, text="Calibrate", command=flip_calibrate_mode)
    button_calibrate.grid(row=2,column=0,padx=5,pady=5)

    button_back = tk.Button(master=main_window,text="Back", command=main)
    button_back.grid(row=3,column=0,sticky="nsew",padx=20,pady=10)

    main_window.mainloop()

def track():
    cap = cv2.VideoCapture(0)

    # Face mesh set up
    BaseOptions = mp.tasks.BaseOptions
    FaceLandmarker = mp.tasks.vision.FaceLandmarker
    FaceLandmarkerOptions = mp.tasks.vision.FaceLandmarkerOptions
    VisionRunningMode = mp.tasks.vision.RunningMode

    options = FaceLandmarkerOptions(
        base_options=BaseOptions(model_asset_path=MODEL_PATH),
        running_mode=VisionRunningMode.IMAGE,
        num_faces=1)
    

    with FaceLandmarker.create_from_options(options) as landmarker:
        baseline_point = (0,0)
        while True:
            
            _, frame = cap.read()
            frame = cv2.flip(frame, 1)
            frame_h, frame_w, _ = frame.shape # frame dims to calculate x and y coords
            # opencv to mp image
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame)
            landmark_points = landmarker.detect(mp_image)
            if landmark_points:
                landmarks = landmark_points.face_landmarks
                if landmarks:

                    landmark = landmarks[0]
                    # Actual landmark points
                    for id, point in enumerate(landmark[226:227] + landmark[468:469]): # Slice for pupil landmarks                        

                        # Corner of eye window
                        if (id == 0):
                            x = int(point.x * frame_w)
                            y = int(point.y * frame_h)
                            baseline_point = (x,y)
                        
                        elif (id == 1):
                            x = abs(int(point.x * frame_w) - baseline_point[0])
                            y = abs(int(point.y * frame_h) - baseline_point[1])

                            true_x = int(point.x * frame_w)
                            true_y = int(point.y * frame_h)

                            cv2.circle(frame, (true_x,true_y), 1, (0,0,255), 1)
                            if len(calibration) == 2:
                                if calibration[1][1]-1 <= y and y <= calibration[0][1]+1 and \
                                    calibration[0][0]-1 <= x and x <= calibration[1][0]+1:
                                    print("YES")
                                else:
                                    print(calibration)
                                    print("x ", x, "y ",y)
                            elif cv2.waitKey(1) & 0xFF == ord('c'):
                                calibration.append((x,y))
            cv2.imshow("Testing", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()