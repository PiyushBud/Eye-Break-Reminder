# Eye-Break-Reminder
 Python program that tracks eyes and reminds users to take an eye break if they have been staring at the computer screen for too long.

## Usage
Start app

Select a max screen time for the program to push a break reminder

Press 'Start' to initiate camera

Calibrate by looking at the top left corner of the user's monitor and then hit 'Calibrate'
Then repeat for the bottom right corner of the user's monitor and once again hit 'Calibrate'

The program will indicate if the user is looking at the screen and start a timer for screen time

Once the selected max screen time is hit, a break reminder will be pushed

## Demo



## Mechanisms
Uses mediapipe library's facemesh to track users pupils and other facial features. The user calibrates pupil location relative to surrounding facial features
to determine if the user is looking at their screen.
