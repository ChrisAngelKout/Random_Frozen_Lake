from mss import mss
import cv2
import numpy as np

"""
File:   Koutounidis_2019030138.py
Author: Koutounidis Christos-Angelos
Description: Functions for the vizual analyzer
"""


class GameAnalyzer:
    def __init__(self, n, cell_size):
        self.n = n
        self.cell_size = cell_size
        self.window_size = ((n * cell_size) + 40, (n * cell_size + 2) + 40)
        # Defining the RGB colors for the game elements, that the visual analyzer will use
        self.colors = {
            "player": (20, 245, 20),
            "goal": (245, 20, 20),
            "holes": (20, 20, 245),
            "available": (225, 196, 255)
        }

    def capture_game_area(self):
        """
        Using mss library to take screenshot of the environment in order to be analyzed
        """
        with mss() as sct:
            monitor = {"top": 80, "left": 80, "width": self.window_size[0], "height": self.window_size[1]}
            sct_img = sct.grab(monitor)
            # Convert to an array that OpenCV can work with
            img = np.array(sct_img)

            # Convert from BGR (default OpenCV) to RGB
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

            return img

    def find_elements(self, img):
        """
        This function detects game elements based on their color and returns their positions
        """
        elements = {}
        for key, value in self.colors.items():
            # Creating a mask for the current color
            lower = np.array(value, dtype="uint8")
            upper = np.array(value, dtype="uint8")
            mask = cv2.inRange(img, lower, upper)
            elements[key] = mask

        return elements

    def get_positions(self, mask):
        """
        Getting the positions of the game elements on the screen. The precise x and y values
        is the center position of each element on the screen.
        """
        positions = []
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for contour in contours:
            M = cv2.moments(contour)
            if M['m00'] != 0:
                x = int(M['m10'] / M['m00'])
                y = int(M['m01'] / M['m00'])
                positions.append((x, y))
        return positions

    def get_adjacent_position(self, pos, direction):
        """
        This function returns the position of all the adjacent cells of the given cell
        """
        deltas = {0: (0, -40), 1: (-40, 0), 2: (0, 40), 3: (40, 0)}
        delta = deltas[direction]
        return (pos[0] + delta[0], pos[1] + delta[1])

    def is_opposite_direction(self, dir1, dir2):
        """
        Used to determine if the 2 given adjacent cells are pointing to each other.
        If they are, they are creating an infinite loop and have to be changed.
        """
        opposite_pairs = {(0, 2), (2, 0), (1, 3), (3, 1)}
        return (dir1, dir2) in opposite_pairs or (dir2, dir1) in opposite_pairs

    def calculate_best_moves(self, elements):
        """
        Used to visually determine the best moves for each cell, to move towards the Goal.
        Implements avoidance of holes and edges.
        """
        goal_pos = self.get_positions(elements['goal'])[0]
        hole_positions = self.get_positions(elements['holes'])
        combined_positions = elements['available'] + elements['holes'] + elements['player'] + elements['goal']
        available_positions = self.get_positions(combined_positions)

        directions = {}
        for position in available_positions:
            dx = goal_pos[0] - position[0]
            dy = goal_pos[1] - position[1]

            # Checking for holes around the current position and if the position is on the edge
            hole_up = (position[0], position[1] - 40) in hole_positions
            hole_down = (position[0], position[1] + 40) in hole_positions
            hole_left = (position[0] - 40, position[1]) in hole_positions
            hole_right = (position[0] + 40, position[1]) in hole_positions

            top_edge = (position[0], position[1] - 40) not in available_positions
            bottom_edge = (position[0], position[1] + 40) not in available_positions
            left_edge = (position[0] - 40, position[1]) not in available_positions
            right_edge = (position[0] + 40, position[1]) not in available_positions

            if abs(dx) > abs(dy):
                direction = 3 if dx >= 0 else 1  # Right or LEFT
            else:
                direction = 2 if dy >= 0 else 0  # UP or Down

            # Many if checks (THAT WORK :) !) after trial and error
            if abs(dx) > abs(dy):
                if not (hole_up or top_edge) and not (hole_down or bottom_edge) and not \
                        (hole_right or right_edge) and not (hole_left or left_edge):
                    direction = 3 if dx >= 0 else 1  # Right or LEFT
                elif dx >= 0:
                    direction = 3 if not (hole_right or right_edge) else (2 if not (hole_down or bottom_edge) else
                                                                          (0 if not (hole_up or top_edge) else 1))
                else:
                    direction = 1 if not (hole_left or left_edge) else (2 if not (hole_down or bottom_edge) else
                                                                        (0 if not (hole_up or top_edge) else 3))
            else:
                if not (hole_up or top_edge) and not (hole_down or bottom_edge) and not \
                        (hole_right or right_edge) and not (hole_left or left_edge):
                    direction = 2 if dy >= 0 else 0  # Down or UP
                elif dy >= 0:
                    direction = 2 if not (hole_down or bottom_edge) else (3 if not (hole_right or right_edge) else
                                                                          (1 if not (hole_left or left_edge) else 0))
                else:
                    direction = 0 if not (hole_up or top_edge) else (3 if not (hole_right or right_edge) else
                                                                     (1 if not (hole_left or left_edge) else 2))

            directions[position] = direction

        for i in range(4):
            for pos, move_dir in directions.items():
                adj_pos = self.get_adjacent_position(pos, move_dir)

                # Checking if the adjacent cell is within the bounds and not a hole
                if adj_pos in available_positions and adj_pos not in hole_positions:
                    adj_direction = directions.get(adj_pos)
                    # If the adjacent cell's direction points back to the current cell (infinite loop), it gets changed
                    if self.is_opposite_direction(move_dir, adj_direction):
                        all_directions = [0, 1, 2, 3]
                        all_directions.remove(move_dir)
                        alternative_direction = move_dir + 1 if (move_dir != 3) else 0
                        directions[pos] = alternative_direction

        return directions


