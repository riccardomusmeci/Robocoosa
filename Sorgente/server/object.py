import numpy as np

class Object:
    def __init__(self, name = "Object"):
        self.type = name

        if name == "red":
            self.lower = (163, 100, 100)
            self.upper = (178, 255, 255)
            self.complementare = "blue"

        elif name == "yellow":
            self.lower = (15, 100, 100)
            self.upper = (42, 255, 255)
            self.complementare = "blue"

        elif name == "green":
            self.lower = (62, 100, 47)
            self.upper = (100, 255, 166)

        elif name == "blue":
            self.lower = (92, 100, 76)
            self.upper = (125, 255, 255)
            self.complementare = "yellow"

        else:
            self.lower = (0,0,0)
            self.upper = (0,0,0)