import cv2
import pyvirtualcam
import datetime
import time
import keyboard
from collections import deque

from sharedstate import shared_state
from twitchapi import TwitchAPI

## constants

#1280,720

WIDTH = 1920
HEIGHT = 1080
# WIDTH = 640
# HEIGHT = 480
DSHOW = 1

box_scaling_factor = 1

font = cv2.FONT_HERSHEY_SIMPLEX
font_scale = 1.5
font_weight = 2 #int
font_color = (255,255,255) # BGR not RGB, 0-255
shadow_color = (0,0,0)
shadow_WIDTH = 1
text_spacing = int(25 * font_scale)
horizontal_margin = 20
vertical_margin = 20
text_shadow = True

## objects
cv2.destroyAllWindows()
background_subtractor = cv2.createBackgroundSubtractorMOG2()

class Box: # box object for focusing on parts of screen
    def __init__(self, x, y, w, h, threshold):
        self.x = x  # X-coordinate
        self.y = y  # Y-coordinate
        self.w = w  # WIDTH
        self.h = h  # HEIGHT
        self.threshold = threshold
        self.motion = False

boxes = list()

boxes.append(
    Box(int(1000 * box_scaling_factor), 
        int(520 * box_scaling_factor), 
        int(800 * box_scaling_factor), 
        int(360 * box_scaling_factor),
        2000))

## definitions

def detect_motion(frame):

    # Convert to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # # Apply the background subtractor
    fg_mask = background_subtractor.apply(gray)

    # # Focus on the rectangular areas of interest
    rois = list()
    for i in boxes:
        rois.append(fg_mask[i.y:i.y+i.h, i.x:i.x+i.w])

    motion = False
    for indx, roi in enumerate(rois):
        boxes[indx].motion = False

        # # Detect motion (you can adjust the threshold value)
        _, thresh = cv2.threshold(roi, 25, 255, cv2.THRESH_BINARY)
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # # Check if there is motion in the area of interest
        if any(cv2.contourArea(contour) > boxes[indx].threshold for contour in contours):  # Adjust contour area threshold
            motion = True
            boxes[indx].motion = True

    return motion


## init
def start_catcam():
    print('opening camera with opencv on slot 0, may take a sec')
    
    try:
        # initialize webcam with opencv
        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW if DSHOW == 1 else None)

    except:
        print('error on slot 0, trying slot 1')
        cap = cv2.VideoCapture(1, cv2.CAP_DSHOW if DSHOW == 1 else None)


    cap.set(3,WIDTH)
    cap.set(4,HEIGHT)
    pwidth = cap.get(3)
    pheight = cap.get(4)
    
    
    

    #display camera info
    if 0:
        for i in range(18): # display cam properties
            print(cap.get(propId=i))

    print('setting up virtual camera')
    with pyvirtualcam.Camera(width=int(pwidth), height=int(pheight), fps=30) as cam:
        print('starting live feed - press ctrl+alt+z to exit')
        
        # runtime variables
        active_count = 0
        last_active_time = None
        starttime = time.time()
        motion = False
        motion_history = deque(maxlen=30)
        last_call = starttime

        while not shared_state.should_shutdown():
            ret, oframe = cap.read()
            if not ret:
                print("couldn't grab frame, closing...")
                break

            frame = cv2.flip(oframe, 0)
            
            motion_last_frame = motion
            motion = detect_motion(frame)
            motion_history.append(motion)

            if (sum(motion_history) > 10) & (time.time() - last_call > 30):
                twitch = TwitchAPI()
                TwitchAPI.create_clip(twitch)
                print('generating clip...')
                last_call = time.time()

            ##print(time.time() - starttime)
            if time.time() - starttime < 10:
                motion = False

            if motion:
                if not motion_last_frame:
                    active_count += 1
                last_active_time = datetime.datetime.now() 

            if shared_state.get_show_boxes():
                for b in boxes:
                    # Draw a rectangle on the frame
                    color = (0, 255, 0) if b.motion else (0, 0, 255)  # Green if motion detected, red otherwise
                    cv2.rectangle(frame, (b.x, b.y), (b.x+b.w, b.y+b.h), color, 1)

            if shared_state.get_show_text():
                lines = list()
                lines.append(f"{'true' if motion else 'false'}")
                #lines.append(f"times seen: {active_count}")
                if last_active_time: dt = datetime.datetime.now() - last_active_time
                lines.append(f"last seen: {int(dt.seconds / 3600)} h, {int((int(dt.seconds) % 3600) / 60)} m, {int(dt.seconds) % 60} s ago" if last_active_time else "last seen: N/A")
                lines.append(datetime.datetime.now().strftime('%I:%M:%S %p'))

                for indx, line in enumerate(lines):
                    if text_shadow:
                        cv2.putText(frame, line, (horizontal_margin, HEIGHT - (text_spacing * indx + vertical_margin)), font, font_scale, shadow_color, font_weight + shadow_WIDTH, cv2.LINE_AA)
                    cv2.putText(frame, line, (horizontal_margin, HEIGHT - (text_spacing * indx + vertical_margin)), font, font_scale, font_color, font_weight, cv2.LINE_AA)

            # Display the color corrected frame
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            #cv2.imshow('Frame', frame)

            # Send the frame to the virtual camera
            cam.send(frame_rgb)

            # Wait until it's time for the next frame.
            cam.sleep_until_next_frame()

            # listen for quit (q key)
            if keyboard.is_pressed('ctrl+alt+z'):
                break

        # Release the video capture object
        cap.release()
        cv2.destroyAllWindows()
        exit()

if __name__ == "__main__":
    start_catcam()