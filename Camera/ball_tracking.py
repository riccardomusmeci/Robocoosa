from collections import deque
import numpy as np
import math
import imutils
import argparse
import cv2
import socket
import time
from object import Object

ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video",
	help="path to the (optional) video file")
ap.add_argument("-b", "--buffer", type=int, default=64,
	help="max buffer size")
args = vars(ap.parse_args())

# connessione socket
server_address = '192.168.0.102'
server_port = 1931

red = Object("red")
blue = Object("blue")
yellow = Object("yellow")
green = Object("green")

# distanza tra due punti -> serve a calcolare angolo
def distance((x1, y1), (x2,y2)):
    dist = math.sqrt((math.fabs(x2-x1))**2+((math.fabs(y2-y1)))**2)
    return dist

def findColor(color):
	mask = cv2.inRange(hsv, color.lower, color.upper)
	mask = cv2.erode(mask, None, iterations=2)
	mask = cv2.dilate(mask, None, iterations=2)
	  
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
		if radius > 12:
			# draw the circle and centroid on the frame,
			# then update the list of tracked points
			return True
	
def findObject(targetColor, othercolor):
	mask = cv2.inRange(hsv, targetColor.lower, targetColor.upper)
	mask = cv2.erode(mask, None, iterations=2)
	mask = cv2.dilate(mask, None, iterations=2)
	  
	cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
			cv2.CHAIN_APPROX_SIMPLE)[-2]
	center = None

	# only proceed if at least one contour was found
	if len(cnts) > 0 and findColor(othercolor):
		# find the largest contour in the mask, then use
		# it to compute the minimum enclosing circle and
		# centroid
		c = max(cnts, key=cv2.contourArea)
		((x, y), radius) = cv2.minEnclosingCircle(c)
		M = cv2.moments(c)
		center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))

		# only proceed if the radius meets a minimum size
		if radius > 12:
			# draw the circle and centroid on the frame,
			# then update the list of tracked points
			cv2.circle(frame, (int(x), int(y)), int(radius),(0, 255, 255), 2) # Cerchio
			cv2.circle(frame, center, 5, (0, 0, 255), -1)						#Centro
			print "Found Object " + targetColor.type

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
				#print 90 - angle
				if center_x < center_frame_x:
					msg = {
						'ID' : 'Camera',
						'differenza_angolo' : 90 - angle,
						'verso_rotazione' : 0,
						'target' : 'oggetto'
					}
					print msg
					sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
					sock.connect((server_address, server_port))
					sock.sendall(str(msg))
					sock.close()
					#sock.sendall(str(msg))
					#sock.close()
					#cv2.putText(frame, str(int(angle)), (center_x-30, center_y), cv2.FONT_HERSHEY_SCRIPT_COMPLEX, 1, (0,128,220), 2)
				elif center_x > center_frame_x:
					msg = {
						'ID' : 'Camera',
						'differenza_angolo' : 90 - angle,
						'verso_rotazione' : 1,
						'target' : 'oggetto'
					}
					print msg
					sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
					sock.connect((server_address, server_port))
					sock.sendall(str(msg))
					sock.close()

def findArea(lower, upper, othercolor):
	mask = cv2.inRange(hsv, targetColor.lower, targetColor.upper)
	mask = cv2.erode(mask, None, iterations=2)
	mask = cv2.dilate(mask, None, iterations=2)
	  
	cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
			cv2.CHAIN_APPROX_SIMPLE)[-2]
	center = None

	# only proceed if at least one contour was found
	if len(cnts) > 0 and not findColor(othercolor):
		# find the largest contour in the mask, then use
		# it to compute the minimum enclosing circle and
		# centroid
		c = max(cnts, key=cv2.contourArea)
		((x, y), radius) = cv2.minEnclosingCircle(c)
		M = cv2.moments(c)
		center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))

		# only proceed if the radius meets a minimum size
		if radius > 12:
			# draw the circle and centroid on the frame,
			# then update the list of tracked points
			cv2.circle(frame, (int(x), int(y)), int(radius),(0, 255, 255), 2) # Cerchio
			cv2.circle(frame, center, 5, (0, 0, 255), -1)						#Centro
			print "Found Area " + targetColor.type

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
				#print 90 - angle
				if center_x < center_frame_x:
					msg = {
						'ID' : 'Camera',
						'differenza_angolo' : 90 - angle,
						'verso_rotazione' : 0,
						'target' : 'area'
					}
					print msg
					sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
					sock.connect((server_address, server_port))
					sock.sendall(str(msg))
					sock.close()
					#cv2.putText(frame, str(int(angle)), (center_x-30, center_y), cv2.FONT_HERSHEY_SCRIPT_COMPLEX, 1, (0,128,220), 2)
				elif center_x > center_frame_x:
					msg = {
						'ID' : 'Camera',
						'differenza_angolo' : 90 - angle,
						'verso_rotazione' : 1,
						'target' : 'area'
					}
					print msg
					sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
					sock.connect((server_address, server_port))
					sock.sendall(str(msg))
					sock.close()


pts = deque(maxlen=args["buffer"])


# sorgente camera
camera = cv2.VideoCapture("rtsp://@192.168.0.101:554/live/ch00_0", cv2.CAP_FFMPEG)

while True:
	startTime = time.time()
	# prendiamo i frame
	(grabbed, frame) = camera.read()

	# get di altezza e larghezza del frame
	width = camera.get(cv2.CAP_PROP_FRAME_WIDTH)   # float
	height = camera.get(cv2.CAP_PROP_FRAME_HEIGHT) # float
	
	# calcoliamo il centro del frame
	(center_frame_x, center_frame_y) = (int(width / 2), height)

	# blurred = cv2.GaussianBlur(frame, (11, 11), 0)
	hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

	findObject(red, blue)
	

	# show the frame to our screen
	cv2.imshow("Frame", frame)
	key = cv2.waitKey(1) & 0xFF

	# if the 'q' key is pressed, stop the loop
	if key == ord("q"):
		break

# cleanup the camera and close any open windows
camera.release()
cv2.destroyAllWindows()