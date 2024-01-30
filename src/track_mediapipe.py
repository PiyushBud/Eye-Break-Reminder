import cv2, classes
import mediapipe as mp
import tkinter as tk
from PIL import ImageTk, Image
from datetime import datetime

MODEL_PATH = "../res/face_landmarker.task"

EYES = [468,478]

calibration = classes.Corners()

mode_calibrate = False
mode_running = False
mode_looking = False

main_window = None

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

# Main meun GUI
def main():

    global main_window

    if main_window is not None:
        main_window.destroy()

    main_window = tk.Tk()
    main_window.columnconfigure(0, minsize=200, weight=1)
    main_window.rowconfigure([0, 1, 2], minsize=50, weight=1)

    label = tk.Label(master=main_window, text="Your eyes are gonna need a break")
    label.grid(row=0,column=0,sticky="s",pady=5)

    button_opencv = tk.Button(master=main_window, text="OpenCV")
    button_opencv.grid(row=1, column=0, sticky="nsew", padx=20, pady=10)

    button_media = tk.Button(master=main_window, text="MediaPipe", command=tracking_menu)
    button_media.grid(row=2, column=0, sticky="nsew", padx=20, pady=10)

    main_window.mainloop()

# Function to return to the main menu
def back_to_main():
    global cap, calibration

    cap.release()

    calibration = classes.Corners()

    main()

# Signal to mark landmark coords as a calibration point
def flip_calibrate_mode():
    global mode_calibrate, mode_running, label_gaze, cap

    _, frame = cap.read()
    if frame is None:
        return
    
    if calibration.complete:
        label_gaze.config(text="Look at the top left corner of your monitor \nand hit calibrate", bg="grey")
        calibration.complete = False
        mode_running = False
    else:
        mode_calibrate = True

# Start detection
def start_detect():
    
    global label_gaze, label_cam, mode_calibrate, mode_looking, cap

    baseline_point = (0,0)

    _, frame = cap.read()
    if frame is None:
        return
    frame = cv2.flip(frame, 1)
    frame_h, frame_w, _ = frame.shape # frame dimensions to calculate x and y coords
    # opencv to mp image
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame)


    landmark_points = landmarker.detect(mp_image)
    if landmark_points:
        landmarks = landmark_points.face_landmarks
        if landmarks:

            landmark = landmarks[0]
            # Actual landmark points
            for id, point in enumerate(landmark[226:227] + landmark[468:469]): # Slice for pupil landmarks                        

                landmark_coord = classes.Coord()
                # Corner of eye, landmark[226]
                if (id == 0):
                    landmark_coord.x = int(point.x * frame_w)
                    landmark_coord.y = int(point.y * frame_h)
                    baseline_point = landmark_coord.copy()
                
                # Pupil center, landmark[468]
                elif (id == 1):
                    landmark_coord.x = abs(int(point.x * frame_w) - baseline_point.x)
                    landmark_coord.y = abs(int(point.y * frame_h) - baseline_point.y)

                    true_x = int(point.x * frame_w)
                    true_y = int(point.y * frame_h)

                    cv2.circle(frame, (true_x,true_y), 1, (0,0,255), 1)
                    if calibration.complete:
                        if calibration.within(landmark_coord):
                            label_gaze.config(text="Looking? YES", bg="green")
                        else:
                            label_gaze.config(text="Looking? NO ", bg="red")

                    elif mode_calibrate:
                        calibration.add(landmark_coord)
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
    global main_window, cap, mode_running
    if button_start.cget("text") == "Start":
        cap = cv2.VideoCapture(0)
        button_start["text"] = "Stop"
        label_gaze["text"] = "Look at the top left corner of your monitor \nand hit calibrate"     
        mode_running = True
        start_detect()
    else:
        cap.release()
        button_start["text"] = "Start"

# TFunction to launch the timer
def launch_timer():
    global label_timer, frame_picture
    label_timer = tk.Label(master=frame_picture, bg="skyblue")
    label_timer.grid(row=1, column=0, sticky="n", padx=10, pady=10)
    counter = 0
    # Timer for tracking time 
    def timer(counter, label_timer):
        if mode_running:
            time_data = datetime.fromtimestamp(counter)
            label_timer["text"] = time_data.strftime("%M:%S")
            label_timer.after(1000, lambda: timer(counter+1))
        else:
            label_timer["text"] = ""

    timer(counter, label_timer)



# Menu for displaying webcam footage
def tracking_menu():

    global main_window, label_gaze, label_cam, frame_picture

    if main_window is not None:
        main_window.destroy()

    main_window = tk.Tk()
    main_window.columnconfigure([0, 1], weight=1)
    main_window.rowconfigure([0, 1], weight=1)

    frame_buttons = tk.Frame(master=main_window, width=200, height=500, bg="grey")
    frame_buttons.grid(row=0, column=0, padx=10, pady=10)
    frame_buttons.rowconfigure([0,1,2,3], minsize=70)
    frame_buttons.columnconfigure(0, minsize=200)

    frame_picture = tk.Frame(master=main_window, width=500, height=500, bg="skyblue")
    frame_picture.grid(row=0, column=1, padx=10, pady=10)
    frame_picture.rowconfigure([0,1], weight=1)
    frame_picture.columnconfigure([0,1], weight=1)

    img_arr = cv2.cvtColor(cv2.imread("../res/bg.JPG"), cv2.COLOR_BGR2RGBA)
    img = Image.fromarray(img_arr)
    imgtk = ImageTk.PhotoImage(image=img)

    label_cam = tk.Label(master=frame_picture)
    label_cam.grid(row=1, column=0, padx=10, pady=10)
    label_cam.imgtk = imgtk
    label_cam.configure(image=imgtk)

    label_gaze = tk.Label(master=frame_buttons, text="Hit Start!", bg=frame_buttons["background"])
    label_gaze.grid(row=0, column=0, padx=5, pady=5)

    button_start = tk.Button(master=frame_buttons, text="Start")
    button_start.config(command=lambda b=button_start:start_cam(b))
    button_start.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)

    button_calibrate = tk.Button(master=frame_buttons, text="Calibrate", command=flip_calibrate_mode)
    button_calibrate.grid(row=2, column=0, sticky="nsew", padx=10,pady=5)

    button_back = tk.Button(master=frame_buttons, text="Back", command=back_to_main)
    button_back.grid(row=3, column=0, sticky="nsew", padx=10, pady=5)

    main_window.mainloop()

if __name__ == "__main__":
    main()