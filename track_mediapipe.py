import cv2, multiprocessing, classes
import mediapipe as mp
import tkinter as tk
from tkinter import ttk
from PIL import ImageTk, Image
from datetime import datetime
from playsound import playsound
from pathlib import Path

MODEL_PATH = str(Path("res", "face_landmarker.task"))

time_to_seconds = {"5 sec": 5, "1 min": 60, "5 min": 300, "10 min": 600,\
                     "15 min": 900, "30 min": 1800, "45 min": 2700, "1 hr": 3600}

calibration = classes.Corners()

# To signal calibration
mode_calibrate = False

# To signal the user is looking at the screen
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

# Face mesh detector
landmarker = FaceLandmarker.create_from_options(options)

# Start detection
def start_detect(counter):
    
    global mode_calibrate, mode_looking

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
                            mode_looking = True
                            counter = 0
                        else:
                            label_gaze.config(text="Looking? NO ", bg="red")
                            if counter > 150:
                                mode_looking = False
                            else:
                                counter += 1

                    elif mode_calibrate:
                        calibration.add(landmark_coord)
                        label_gaze.config(text="Now look at the bottom right of your monitor\n and hit calibrate", bg="gray")
                        mode_calibrate = False
    
    img_arr = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
    img = Image.fromarray(img_arr)
    imgtk = ImageTk.PhotoImage(image=img)
    label_cam.imgtk = imgtk
    label_cam.configure(image=imgtk)
    label_cam.after(1, lambda :start_detect(counter))

# Start the webcam
def start_cam(button_start: tk.Button):
    global cap, mode_running, mode_looking

    if button_start.cget("text") == "Start":
        
        cap = cv2.VideoCapture(0)
        button_start["text"] = "Stop"
        label_gaze.config(text="Look at the top left corner of your monitor \nand hit calibrate", bg="gray")
        button_calibrate["state"] = "active"
        mode_running = True
        start_detect(0)
        launch_timer(time_to_seconds[combo_times.get()])
    
    # Stop cam
    else:
        cap.release()
        calibration.empty()
        mode_looking = False
        button_start["text"] = "Start"
        button_calibrate["state"] = "disabled"

# Calculate
def get_max_screen_time(combo_times):
    # combo_text = combo_times.get()
    return

# Function to launch the timer
def launch_timer(max_screen_time):
    global label_timer

    label_timer = tk.Label(master=frame_picture, bg="skyblue", font=("Arial", 18))
    label_timer.grid(row=0, column=0, sticky="n", padx=10, pady=10)
    counter = 0

    max_screen_time = time_to_seconds[combo_times.get()]

    # Timer for tracking time 
    def timer(counter, label_timer):
        
        if mode_looking and (not mode_calibrate):
            if counter >= max_screen_time:
                push_reminder()
                counter = -1
                return
            time_data = datetime.fromtimestamp(counter)
            label_timer["text"] = time_data.strftime("%M:%S")
            label_timer.after(1000, lambda: timer(counter+1, label_timer))
        else:
            label_timer["text"] = "00:00"
            label_timer.after(1000, lambda: timer(0, label_timer))

    timer(counter, label_timer)



# Creates pop up to notify user to take a break
def push_reminder():

    def close_reminder_window(window):

        window.destroy()
        p.terminate()
        launch_timer(time_to_seconds[combo_times.get()])

    remind_window = tk.Tk()
    remind_window.protocol("WM_DELETE_WINDOW", lambda : close_reminder_window(remind_window))
    label_remind = tk.Label(master=remind_window, text="TAKE A BREAK!!", font=("Arial", 24))
    label_remind.grid(row=0, column=0, padx=10, pady=5)

    button_exit = tk.Button(master=remind_window, text="Quit", command= lambda : close_reminder_window(remind_window))
    button_exit.grid(row=1, column=0, padx=10, pady=5)

    path = Path(".", "..", "res", "clock-alarm.mp3")
    p = multiprocessing.Process(target=loop_alarm, args=(str(path),))
    p.start()

def loop_alarm(path):
    while True:
        playsound(path, True)

# Starting menu GUI
def starting_menu():

    global main_window

    if main_window is not None:
        main_window.destroy()

    main_window = tk.Tk()
    main_window.columnconfigure(0, minsize=200, weight=1)
    main_window.rowconfigure([0, 1, 2], minsize=50, weight=1)

    label = tk.Label(master=main_window, text="Your eyes are gonna need a break")
    label.grid(row=0,column=0,sticky="s",pady=5)

    # button_opencv = tk.Button(master=main_window, text="OpenCV")
    # button_opencv.grid(row=1, column=0, sticky="nsew", padx=20, pady=10)

    button_media = tk.Button(master=main_window, text="MediaPipe", command=tracking_menu)
    button_media.grid(row=1, column=0, sticky="nsew", padx=20, pady=10)

    main_window.mainloop()

# Function to return to the main menu
def back_to_main():
    global calibration

    cap.release()

    calibration = classes.Corners()

    starting_menu()

# Signal to mark landmark coords as a calibration point
def flip_calibrate_mode():
    global mode_calibrate, mode_looking

    _, frame = cap.read()
    if frame is None:
        return
    
    # Recalibration
    if calibration.complete:
        label_gaze.config(text="Look at the top left corner of your monitor \nand hit calibrate", bg="grey")
        calibration.complete = False
        mode_looking = False
    else:
        mode_calibrate = True


# Menu for displaying webcam footage
def tracking_menu():

    global main_window, label_gaze, label_cam, frame_picture, combo_times, button_calibrate

    if main_window is not None:
        main_window.destroy()

    main_window = tk.Tk()
    main_window.columnconfigure([0, 1], weight=1)
    main_window.rowconfigure([0, 1], weight=1)

    # Frame for buttons and information labels
    frame_buttons = tk.Frame(master=main_window, width=200, height=500, bg="grey")
    frame_buttons.grid(row=0, column=0, padx=10, pady=10)
    frame_buttons.rowconfigure([0,1,2,3,4], minsize=70)
    frame_buttons.columnconfigure(0, minsize=200)

    # Frame for web camera feed and timer
    frame_picture = tk.Frame(master=main_window, width=500, height=500, bg="skyblue")
    frame_picture.grid(row=0, column=1, padx=10, pady=10)
    frame_picture.rowconfigure([0,1], weight=1)
    frame_picture.columnconfigure([0,1], weight=1)

    # Initial picture
    img_arr = cv2.cvtColor(cv2.imread("../res/bg.JPG"), cv2.COLOR_BGR2RGBA)
    img = Image.fromarray(img_arr)
    imgtk = ImageTk.PhotoImage(image=img)

    label_cam = tk.Label(master=frame_picture)
    label_cam.grid(row=1, column=0, padx=10, pady=10)
    label_cam.imgtk = imgtk
    label_cam.configure(image=imgtk)

    # Label for calibration guide and indicates whether user is looking at the screen
    label_gaze = tk.Label(master=frame_buttons, text="Select a max screen time\nand hit start!", bg=frame_buttons["background"])
    label_gaze.grid(row=0, column=0, padx=5, pady=5)

    combo_times = ttk.Combobox(
        master= frame_buttons,
        state="readonly",
        values=list(time_to_seconds.keys()))
    
    combo_times.current(0)
    combo_times.grid(row=1, column=0, padx=10, pady=5)

    button_start = tk.Button(master=frame_buttons, text="Start")
    button_start.config(command=lambda b=button_start:start_cam(b))
    button_start.grid(row=2, column=0, sticky="nsew", padx=10, pady=5)

    button_calibrate = tk.Button(master=frame_buttons, text="Calibrate",\
                                 command=flip_calibrate_mode, state="disabled")
    button_calibrate.grid(row=3, column=0, sticky="nsew", padx=10, pady=5)

    button_back = tk.Button(master=frame_buttons, text="Back", command=back_to_main)
    button_back.grid(row=4, column=0, sticky="nsew", padx=10, pady=5)

    main_window.mainloop()

if __name__ == "__main__":
    starting_menu()