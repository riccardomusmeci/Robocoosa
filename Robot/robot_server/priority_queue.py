import heapq

class PriorityQueue:
    def __init__(self):
        self.elements = []

    def empty(self):
        return len(self.elements) == 0

    def put(self, item, priority):
        #print "Putting " + str(item) + " with priority " + str(priority)
        heapq.heappush(self.elements, (priority, item))
        #print "Elements are now: ", self.elements

    def get(self):
        return heapq.heappop(self.elements)
