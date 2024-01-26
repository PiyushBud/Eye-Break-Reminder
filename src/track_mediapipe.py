import cv2
import mediapipe as mp
import tkinter as tk

MODEL_PATH = "../res/face_landmarker.task"

EYES = [468,478]

calibration = []

global main_window


# GUI work
def main():
    main_window = tk.Tk()
    main_window.columnconfigure(0, minsize=200,weight=1)
    main_window.rowconfigure([0, 1, 2, 3], minsize=50,weight=1)

    label = tk.Label(master=main_window, text="Your eyes are gonna need a break")
    label.grid(row=0,column=0,sticky="s",pady=5)

    button_opencv = tk.Button(master=main_window, text="OpenCV")
    button_opencv.grid(row=1,column=0,sticky="nsew",padx=20,pady=10)

    button_calibrate = tk.Button(master=main_window,text="Calibrate")
    button_calibrate.grid(row=2,column=0,sticky="nsew",padx=20, pady=10)

    main_window.mainloop()

def find_screen_dims():
    main_window = tk.Tk()
    main_window.columnconfigure(0, minsize=200,weight=1)
    main_window.rowconfigure([0, 1, 2, 3], minsize=50,weight=1)

    label_width = tk.Label(master=main_window, text="Enter your monitor width")
    # entry_width

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

        while True:
            _, frame = cap.read()
            frame = cv2.flip(frame, 1)
            frame_h, frame_w, _ = frame.shape # frame dims to calculate x and y coords
            # opencv to mp image
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame)
            landmark_points = landmarker.detect(mp_image)
            if landmark_points:
                landmarks = landmark_points.face_landmarks
                print(len(landmarks))
                for landmark in landmarks:

                    # Actual landmark points
                    for eye_points in landmark[468:478]: # Slice for pupil landmarks

                        # Map coords of eyes
                        x = int(eye_points.x * frame_w)
                        y = int(eye_points.y * frame_h)
                        cv2.circle(frame, (x,y), 1, (0,0,255), 1)
                        # if len(calibration) == 4:
                        #     if calibration[1] < x and x < calibration[0] and 
                        #     print()
                        # elif cv2.waitKey(1) & 0xFF == ord('c'):


            cv2.imshow("Testing", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    track()