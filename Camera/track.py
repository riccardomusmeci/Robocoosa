import cv2
from object import Object
import numpy as np


FRAME_WIDTH = 640
FRAME_HEIGHT = 480

MAX_NUM_OBJECTS = 4

MIN_OBJECT_AREA = 12*12
MAX_OBJECT_AREA = FRAME_HEIGHT*FRAME_WIDTH/1.5

windowName = "Original Image"
windowName1 = "HSV Image"
windowName2 = "Thresholded Image"
windowName3 = "After Morphological Operations"
trackbarWindowName = "Colorbars"

# Canny edge detec
size = FRAME_WIDTH, FRAME_HEIGHT, 3
dst = np.zeros(size, dtype=np.uint8)
detected_edges = np.zeros(size, dtype=np.uint8)
src = np.zeros(size, dtype=np.uint8)
src_gray = np.zeros(size, dtype=np.uint8)
cameraFeed = np.zeros(size, dtype=np.uint8)
threshold = np.zeros(size, dtype=np.uint8)
HSV = np.zeros(size, dtype=np.uint8)

# global dst, detected_edges, src, src_gray, lowThreshold, cameraFeed, threshold, HSV
lowThreshold = 1
edgeThresh = 1
max_lowThreshold = 100
ratio = 3
kernel_size = 3
window_name = "Edge Map"

def CannyThreshold(value):
    global detected_edges, dst
    detected_edges = cv2.blur(src_gray,(5,5))

    detected_edges = cv2.Canny(detected_edges,value,value*ratio, kernel_size)
    dst[np.where(detected_edges==0)] = 0

    cv2.imshow(window_name, dst)

def nothing(x):
    pass

def createTrackbars():
    global trackbarWindowName
    cv2.namedWindow(trackbarWindowName)
    #assign strings for ease of coding
    hh = 'Hue High'
    hl = 'Hue Low'
    sh = 'Saturation High'
    sl = 'Saturation Low'
    vh = 'Value High'
    vl = 'Value Low'
	    #Begin Creating trackbars for each
    cv2.createTrackbar(hl, trackbarWindowName,0,179,nothing)
    cv2.createTrackbar(hh, trackbarWindowName,0,179,nothing)
    cv2.createTrackbar(sl, trackbarWindowName,0,255,nothing)
    cv2.createTrackbar(sh, trackbarWindowName,0,255,nothing)
    cv2.createTrackbar(vl, trackbarWindowName,0,255,nothing)
    cv2.createTrackbar(vh, trackbarWindowName,0,255,nothing)


def drawObject(theObjects, frame, temp = None, contours = None, hierarchy = None):
    if ((temp is None) and (contours is None) and (hierarchy is None)):
        for obj in theObjects:
            cv2.circle(frame, (int(obj.x), int(obj.y)), 10, (0,0,255))
            cv2.putText(frame, str(str(obj.x) + " , " + str(obj.y)), (int(obj.x), int(obj.y) + 20), 1, 1, (0,255,0))
            cv2.putText(frame, str(obj.type), (int(obj.x), int(obj.y) - 30), 1, 2, obj.Color)
    else:
        for idx, obj in enumerate(theObjects):
            cv2.drawContours(frame, contours, idx, obj.Color, 3, 8, hierarchy)
            cv2.circle(frame,(int(obj.x), int(obj.y)), 5, obj.Color)
            cv2.putText(frame, str(str(obj.x) + " , " + str(obj.y)), (int(obj.x), int(obj.y) + 20), 1, 1, obj.Color)
            cv2.putText(frame, str(obj.type), (int(obj.x), int(obj.y) - 20), 1, 2, obj.Color)

def morphOps(thresh):
    erodeElement = cv2.getStructuringElement(cv2.MORPH_RECT,(3,3))
    dilateElement = cv2.getStructuringElement(cv2.MORPH_RECT,(8,8))

    cv2.erode(thresh,thresh,erodeElement)
    cv2.erode(thresh,thresh,erodeElement)

    cv2.dilate(thresh,thresh,dilateElement)
    cv2.dilate(thresh,thresh,dilateElement)

def trackFilteredObject(threshold, HSV, cameraFeed, theObject = None):

    objects = []

    temp = threshold.copy()

    #find contours of filtered image using openCV findContours function
    temp, contours, hierarchy = cv2.findContours(temp, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)

    # use moments method to find our filtered object
    refArea = 0
    objectFound = False
    if (len(hierarchy) > 0):
        numObjects = len(hierarchy)

        # if number of objects greater than MAX_NUM_OBJECTS we have a noisy filter
        if(numObjects<MAX_NUM_OBJECTS):
            index = 0
            while index >= 0:
                index = hierarchy[0][index][0]
                moment = cv2.moments(contours[index])
                area = moment["m00"]

                # if the area is less than 20 px by 20px then it is probably just noise
                # if the area is the same as the 3/2 of the image size, probably just a bad filter
                # we only want the object with the largest area so we safe a reference area each
                # iteration and compare it to the area in the next iteration.
                if(area>MIN_OBJECT_AREA):
                    object = Object()

                    object.x = int(moment["m10"]/area)
                    object.y = int(moment["m01"]/area)
                    if theObject is not None:
                        object.type = theObject.type
                        object.Color = theObject.Color

                    objects.append(object)

                    objectFound = True

                else:
                    objectFound = False

            #let user know you found an object
            if(objectFound == True):
                if theObject is not None:
                    drawObject(objects, cameraFeed, temp, contours, hierarchy)
                else:
                    drawObject(objects, cameraFeed)
            else:
                cv2.putText(cameraFeed,"TOO MUCH NOISE! ADJUST FILTER", (0,50),1,2, (0,0,255))
    else:
        cv2.putText(cameraFeed,"TOO MUCH NOISE! ADJUST FILTER", (0,50),1,2, (0,0,255))


calibrationMode = False
# global cameraFeed, threshold, HSV


if(calibrationMode):
    #create slider bars for HSV filtering
    createTrackbars()

cap = cv2.VideoCapture("rtsp://@192.168.0.101:554/live/ch00_0", cv2.CAP_FFMPEG)
#cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH,FRAME_WIDTH)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT,FRAME_HEIGHT)

cv2.waitKey(1000)

while(cap.isOpened()):
    ret, cameraFeed = cap.read()

    src = cameraFeed

    if cameraFeed is False or ret is False:
        break

    HSV = cv2.cvtColor(cameraFeed, cv2.COLOR_BGR2HSV)

    if calibrationMode == True:

        #need to find the appropriate color range values
        #calibrationMode must be false

        #if in calibration mode, we track objects based on the HSV slider values.
        HSV = cv2.cvtColor(cameraFeed, cv2.COLOR_BGR2HSV)

        hul=cv2.getTrackbarPos('Hue Low', trackbarWindowName)
        huh=cv2.getTrackbarPos('Hue High', trackbarWindowName)
        sal=cv2.getTrackbarPos('Saturation Low', trackbarWindowName)
        sah=cv2.getTrackbarPos('Saturation High', trackbarWindowName)
        val=cv2.getTrackbarPos('Value Low', trackbarWindowName)
        vah=cv2.getTrackbarPos('Value High', trackbarWindowName)

        HSVLOW = np.array([hul,sal,val])
        HSVHIGH = np.array([huh,sah,vah])

        threshold = cv2.inRange(HSV, HSVLOW, HSVHIGH)
        morphOps(threshold)
        cv2.imshow(windowName2,threshold)

        #//the folowing for canny edge detec
        #/// Create a matrix of the same type and size as src (for dst)
        dst = src.copy()
        src_gray = cv2.cvtColor(src, cv2.COLOR_BGR2GRAY)

        # Create a window
        cv2.namedWindow( window_name, cv2.WINDOW_AUTOSIZE )

        # Create a Trackbar for user to enter threshold
        cv2.createTrackbar('minT', window_name,0,max_lowThreshold,CannyThreshold)

        # Show the image
        trackFilteredObject(threshold,HSV,cameraFeed)
    else:
        #create some temp fruit objects so that
        #we can use their member functions/information
		blue = Object("blue")
		yellow = Object("yellow")
		red = Object("red")
		green = Object("green")

        #first find blue objects
		HSV = cv2.cvtColor(cameraFeed,cv2.COLOR_BGR2HSV)
		threshold = cv2.inRange(HSV,blue.HSVmin,blue.HSVmax)
		morphOps(threshold)
		trackFilteredObject(threshold, HSV, cameraFeed, blue)
        #then yellows
		HSV = cv2.cvtColor(cameraFeed,cv2.COLOR_BGR2HSV)
		threshold = cv2.inRange(HSV,yellow.HSVmin,yellow.HSVmax)
		morphOps(threshold)
		trackFilteredObject(threshold, HSV, cameraFeed, yellow)
        #then reds
		HSV = cv2.cvtColor(cameraFeed,cv2.COLOR_BGR2HSV)
		threshold = cv2.inRange(HSV,red.HSVmin,red.HSVmax)
		morphOps(threshold)
		trackFilteredObject(threshold,HSV, cameraFeed, red)
        #then greens
		HSV = cv2.cvtColor(cameraFeed,cv2.COLOR_BGR2HSV)
		threshold = cv2.inRange(HSV,green.HSVmin,green.HSVmax)
		morphOps(threshold)
		trackFilteredObject(threshold,HSV, cameraFeed, green)


    cv2.imshow(windowName,cameraFeed)
    cv2.waitKey(1)

cap.release()
cv2.destroyAllWindows()
