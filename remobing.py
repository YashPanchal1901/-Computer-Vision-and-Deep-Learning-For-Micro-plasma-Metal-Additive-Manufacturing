import cv2
import numpy as np
import time
import math as m

hieght = float(input('enter the height : '))
# Create the background subtractor object
bg_subtractor = cv2.createBackgroundSubtractorMOG2(history=500, varThreshold=50, detectShadows=False)

# Open the video capture
video_path = r"D:\nk sir project\MPMAM-Deposition-videos\Co-Cr-Mo-4Ti-Powder-Deposition-Current-13-feedrate-45.avi"
cap = cv2.VideoCapture(video_path)

# Create a window
cv2.namedWindow('Video')

# find the feedrate
import re

# Filename
filename = video_path

# Regular expression to find the number after "feedrate-"
match = re.search(r'feedrate-(\d+)', filename)

# Extracting the number
feedrate = match.group(1)
feedrate = int(feedrate)
print("the feedrate is :",feedrate)

# Step 2: Get the frame rate (fps)
fps = cap.get(cv2.CAP_PROP_FPS)

# Step 3: Get the total number of frames
total_frames = cap.get(cv2.CAP_PROP_FRAME_COUNT)

# Step 4: Calculate the duration in seconds
duration_seconds = total_frames / fps

# Optionally, convert the duration to minutes and seconds
seconds = int(duration_seconds)
print('duration of vedio :',seconds)

lenght = (feedrate * seconds)/60
print("lenght of the deposition :",lenght)

def process_frame(frame):
    # Convert the frame to grayscale
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Define the lower and upper bounds for the black color
    lower_black = np.array([0, 0, 0])
    upper_black = np.array([1, 1, 1])  # Adjust the range as needed

    # Create a mask to isolate the black areas
    mask = cv2.inRange(hsv, lower_black, upper_black)

    # Find contours of the masked areas
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    area = 0
    # Draw the contours on the frame
    for contour in contours:
        area = cv2.contourArea(contour)
        if area < 15:  # Filter out small contours by area
            cv2.drawContours(frame, [contour], -1, (0, 255, 0), 2)
            # Draw the contour area on the frame
            x, y, w, h = cv2.boundingRect(contour)

    return frame, area

final_area = 0
s = time.time()

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # frame = cv2.resize(frame, (512, 512))


    # Apply the background subtractor to get the foreground mask
    fg_mask = bg_subtractor.apply(frame)

    # Invert the mask to keep the background and remove moving objects
    bg_only = cv2.bitwise_and(frame, frame, mask=cv2.bitwise_not(fg_mask))

    # Convert the background-only image to grayscale
    tmp = cv2.cvtColor(bg_only, cv2.COLOR_BGR2GRAY)

    # Apply thresholding technique
    _, alpha = cv2.threshold(tmp, 127, 255, cv2.THRESH_BINARY)

    # Split the background-only image into BGR channels
    b, g, r = cv2.split(bg_only)

    # Merge the BGR channels with the alpha channel
    rgba = [b, g, r, alpha]
    dst = cv2.merge(rgba)

    # Apply median blur to the merged image
    blur = cv2.medianBlur(dst, 5)

    area, a = process_frame(blur)
    if time.time() - s > 1 and seconds - time.time() < 1:
        final_area += a

    # Display the processed frame
    cv2.imshow('Video', area)

    # Break the loop if 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break


# Release the video capture and writer, and close all OpenCV windows
final_area = (final_area*6.8)/1000000
print('final area is :', final_area)
r_2 = m.sqrt(final_area/3.14)

volume = (4*3.14*m.pow(r_2, 3))/3
print('volume of spatter :', volume)

volume_2 = (4*lenght*m.pow(hieght, 3))/3
print('volume of deposition isn :', volume_2)

efficiency = (volume/(volume + volume_2))
print('the efficiency is :', efficiency)

cap.release()
cv2.destroyAllWindows()

