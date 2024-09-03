from point import Point
from controller import Robot as WebotsRobot
TIME_STEP = 16

class Mapa:
    def __init__(self, robot):
        self.robot = WebotsRobot()
        self.robot = robot
        self.gps = self.robot.getDevice("gps")
        self.gps.enable(TIME_STEP)
   
    def update_vars(self):
        self.update_position()

    def update_position(self):
        x, _, y = self.gps.getValues()
        self.position = Point(x, y)

    def check_tile_forward(self):
        axis_y = self.robot.position['y']
        tile_forward_to_check = axis_y - 0.12
        return tile_forward_to_check

    def check_tile_right(self):
        axis_x = self.robot.position['x']
        tile_right_to_check = axis_x + 0.12
        return tile_right_to_check

    def check_tile_left(self):
        axis_x = self.position['x']
        tile_left_to_check = axis_x - 0.12
        return tile_left_to_check

    def isVisited(self, walks_tiles, initial_position):
        gridIndex = self.position_to_grid(initial_position)
        if not gridIndex in walks_tiles:
            walks_tiles.append(gridIndex)
            return walks_tiles
        return True

    def position_to_grid(self, initial_position):
        grill = []
        column = round((self.position['x'] - initial_position['x']) / 0.12)
        grill.append(column)
        row = round((self.position['y'] - initial_position['y']) / 0.12)
        grill.append(row)
        tuple_grill = tuple(grill)
        return tuple_grill