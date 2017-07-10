
from collections import deque
import numpy as np
import math
import imutils
import argparse
import cv2
import socket

ap = argparse.ArgumentParser()
args = vars(ap.parse_args())

# connessione socket
server_address = '192.168.1.58'
server_port = 1931
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((server_address, server_port))

# distanza tra due punti -> serve a calcolare angolo
def distance((x1, y1), (x2,y2)):
    dist = math.sqrt((math.fabs(x2-x1))**2+((math.fabs(y2-y1)))**2)
    return dist


# boundary HSV per colori, in questo caso solo rosso
boundaries = [
	((163, 100, 100), (178, 255, 255))
]

pts = deque(maxlen=args["buffer"])


# sorgente camera
camera = cv2.VideoCapture("rtsp://@192.168.0.101:554/live/ch00_0", cv2.CAP_FFMPEG)

while True:
	# prendiamo i frame
	(grabbed, frame) = camera.read()

	# get di altezza e larghezza del frame
	width = camera.get(cv2.CAP_PROP_FRAME_WIDTH)   # float
	height = camera.get(cv2.CAP_PROP_FRAME_HEIGHT) # float
	
	# calcoliamo il centro del frame
	(center_frame_x, center_frame_y) = (int(width / 2), int(height / 2))

	# blurred = cv2.GaussianBlur(frame, (11, 11), 0)
	hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

	# construct a mask for the color "green", then perform
	# a series of dilations and erosions to remove any small
	# blobs left in the mask
	for (lower, upper) in boundaries:
		mask = cv2.inRange(hsv, lower, upper)
		mask = cv2.erode(mask, None, iterations=2)
		mask = cv2.dilate(mask, None, iterations=2)

		# find contours in the mask and initialize the current
		# (x, y) center of the ball
		cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
			cv2.CHAIN_APPROX_SIMPLE)[-2]
		center = None

		# only proceed if at least one contour was found
		if len(cnts) > 0:
			# find the largest contour in the mask, then use
			# it to compute the minimum enclosing circle and
			# centroid
			c = max(cnts, key=cv2.contourArea)
			((x, y), radius) = cv2.minEnclosingCircle(c)
			M = cv2.moments(c)
			center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))

			# only proceed if the radius meets a minimum size
			if radius > 10:
				# draw the circle and centroid on the frame,
				# then update the list of tracked points
				cv2.circle(frame, (int(x), int(y)), int(radius),(0, 255, 255), 2) # Cerchio
				cv2.circle(frame, center, 5, (0, 0, 255), -1)						#Centro

		# update the points queue
		pts.appendleft(center)

		if center:
			(center_x, center_y) = center
			#quantifies the hypotenuse of the triangle
			hypotenuse =  distance((center_x,center_y), (center_frame_x, center_frame_y))
			#quantifies the horizontal of the triangle
			horizontal = distance((center_x, center_y), (center_frame_x, center_y))
			#makes the third-line of the triangle
			thirdline = distance((center_frame_x, center_frame_y), (center_frame_x, center_y))
			#calculates the angle using trigonometry
			angle = np.arcsin((thirdline/hypotenuse))* 180/math.pi

			if center_frame_y < center_y and center_frame_x > center_x:
				sock.sendall(str(angle))
    			#cv2.putText(frame, str(int(angle)), (center_x-30, center_y), cv2.FONT_HERSHEY_SCRIPT_COMPLEX, 1, (0,128,220), 2)
			elif center_frame_y < center_y and center_frame_x < center_x:
				sock.sendall(str(180 - angle))
				#cv2.putText(frame, str(int(180 - angle)),(center_x-30, center_y), cv2.FONT_HERSHEY_SCRIPT_COMPLEX, 1, (0,128,220), 2)
			elif center_frame_y > center_y and center_frame_x < center_x:
				sock.sendall(str(180 + angle))
				#cv2.putText(frame, str(int(180 + angle)),(center_x-30, center_y), cv2.FONT_HERSHEY_SCRIPT_COMPLEX, 1, (0,128,220), 2)
			elif center_frame_y > center_y and center_frame_x > center_x:
				sock.sendall(str(360 - angle))
				#cv2.putText(frame, str(int(360 - angle)),(center_x-30, center_y), cv2.FONT_HERSHEY_SCRIPT_COMPLEX, 1, (0,128, 229), 2)

			#draws all 3 lines
			#cv2.line(frame, (center_x, center_y), (center_frame_x, center_frame_y), (0, 0, 255), 2)
			#cv2.line(frame, (center_x, center_y), (center_frame_x, center_y), (0, 0, 255), 2)
			#cv2.line(frame, (center_frame_x,center_frame_y), (center_frame_x, center_y), (0,0,255), 2)

		
		# 	#draws all 3 lines
		# 	cv2.line(frame, center, (center_frame_x, center_frame_y), (0, 0, 255), 2)
		# 	cv2.line(frame, center, (center_frame_x, center_y), (0, 0, 255), 2)
		# 	cv2.line(frame, (center_frame_x,center_frame_y), (center_frame_x, center_y), (0,0,255), 2)

		# loop over the set of tracked points
		for i in xrange(1, len(pts)):
			# if either of the tracked points are None, ignore
			# them
			if pts[i - 1] is None or pts[i] is None:
				continue

			# otherwise, compute the thickness of the line and
			# draw the connecting lines
			thickness = int(np.sqrt(args["buffer"] / float(i + 1)) * 2.5)
			cv2.line(frame, pts[i - 1], pts[i], (0, 0, 255), thickness)  #traccia

	# show the frame to our screen
	cv2.imshow("Frame", frame)
	key = cv2.waitKey(1) & 0xFF

	# if the 'q' key is pressed, stop the loop
	if key == ord("q"):
		break

# cleanup the camera and close any open windows
camera.release()
cv2.destroyAllWindows()