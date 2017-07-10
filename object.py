import numpy as np

class Object:
    def __init__(self, name = "Object"):
        self.xPos = 0
        self.yPos = 0
        self.type = name

        if name == "red":
            self.HSVmin = np.array([163, 100, 100])
            self.HSVmax = np.array([178, 255, 255])
	        #BGR value for Red:
            self.Color = (0,0,255)

        elif name == "yellow":
            self.HSVmin = np.array([15, 100, 100])
            self.HSVmax = np.array([42, 255, 255])
	        #BGR value for Yellow:
            self.Color = (0,255,255)

        elif name == "green":
            self.HSVmin = np.array([62, 100, 47])
            self.HSVmax = np.array([100, 255, 166])
	        #BGR value for green:
            self.Color = (0,255,0)

        elif name == "blue":
            self.HSVmin = np.array([92, 100, 76])
            self.HSVmax = np.array([125, 255, 255])
	        #BGR value for Blue:
            self.Color = (255,0,0)

        else:
            self.HSVmin = np.array([0,0,0])
            self.HSVmax = np.array([0,0,0])
            self.Color = (0,0,0)
