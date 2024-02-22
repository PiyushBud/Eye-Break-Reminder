class Coord:
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y
    
    def copy(self):
        return Coord(self.x, self.y)

class Corners:
    def __init__(self, p1: Coord = None, p2: Coord = None):
        self.p1 = p1
        self.p2 = p2
        self.complete = False

    # add corner
    def add(self, point: Coord):
        if self.p1 is None:
            self.p1 = point
            self.p2 = None
            self.complete = False

        elif self.p2 is None:
            self.p2 = point
            self.complete = True

        else:
            self.p1 = point
            self.p2 = None
            self.complete = False
    
    # Check if point is within the corners
    def within(self, point: Coord):
        if not self.complete:
            return False
        
        if self.p2.y -1 <= point.y and point.y <= self.p1.y +1 and \
            self.p1.x -1 <= point.x and point.x <= self.p2.x +1:
            return True
        
        return False
    
    def copy(self):
        return Corners(self.p1, self.p2)

    def empty(self):
        self.p1 = None
        self.p2 = None
        self.complete = False
    
# class SlidingWindow:

#     def __init__(self, cap: int = 10):
#         self.cap = cap
#         self.index = 0
#         self.arr = list()

#     def add(self, val):
#         if self.index >= self.cap:
#             self.index = 0
#         self.arr.