class AllJunctions:
    def __init__(self, sumoparser):
        self.sumoparser = sumoparser
        self.data = None
        self.run()

    def run(self):
        self.data = [
            (junction["x"] - self.sumoparser.x_offset, junction["y"] - self.sumoparser.y_offset)
            for junction in self.sumoparser.junctions
        ]
