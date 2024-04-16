import numpy as np
import pygame
import sys
from Visual_Analyzer import GameAnalyzer
import win32gui
import time
import random

"""
File:   Koutounidis_2019030138.py
Author: Koutounidis Christos-Angelos
Description: Main program code. It has functions for the creation of the random
             Environment, the GUI and the "game-play" 
"""

def draw_arrow(screen, direction, cell_rect):
    """
    Used to draw the best action to take in each box   ( ↑  ←  ↓  → )
    """
    center_x, center_y = cell_rect.center
    if direction == 0:  # UP arrow
        pygame.draw.polygon(screen, (0, 0, 0), [
            (center_x, center_y - 10),
            (center_x - 5, center_y),
            (center_x + 5, center_y)
        ])
        pygame.draw.line(screen, (0, 0, 0), (center_x, center_y), (center_x, center_y + 5), 2)
    elif direction == 1:  # LEFT arrow
        pygame.draw.polygon(screen, (0, 0, 0), [
            (center_x - 10, center_y),
            (center_x, center_y - 5),
            (center_x, center_y + 5)
        ])
        pygame.draw.line(screen, (0, 0, 0), (center_x, center_y), (center_x + 5, center_y), 2)
    elif direction == 2:  # DOWN arrow
        pygame.draw.polygon(screen, (0, 0, 0), [
            (center_x, center_y + 10),
            (center_x - 5, center_y),
            (center_x + 5, center_y)
        ])
        pygame.draw.line(screen, (0, 0, 0), (center_x, center_y), (center_x, center_y - 5), 2)
    elif direction == 3:  # RIGHT arrow
        pygame.draw.polygon(screen, (0, 0, 0), [
            (center_x + 10, center_y),
            (center_x, center_y - 5),
            (center_x, center_y + 5)
        ])
        pygame.draw.line(screen, (0, 0, 0), (center_x, center_y), (center_x - 5, center_y), 2)
    else:
        pass


class RandomFrozenLake:
    def __init__(self, n=None):
        self.n = np.random.randint(5, 23)
        self.grid_size = (self.n, self.n)
        self.start = (0, 0)
        if random.random() <= 0.5:
            self.goal = (np.random.randint(int(np.ceil(self.n/2)), self.n), np.random.randint(int(self.n/4), self.n))
        else:
            self.goal = (np.random.randint(int(self.n/4), self.n), np.random.randint(int(np.ceil(self.n/2)), self.n))
        self.holes = set()
        self.state = self.start
        self.done = False
        self.slip = 0
        self.best_move_per_cell = np.full(np.prod(self.grid_size), None)
        # Defining the Q learning parameters (γ and α)
        self.gamma = 0.95
        self.alpha = 0.25

    def generate_holes(self):
        """
        Generated holes based on the slipperiness of the environment
        """
        if self.slip == 0:
            holes_num = int(self.n * (self.n / 5))      # holes are (n^2)/5
        elif self.slip == 1:
            holes_num = int(self.n * (self.n / 7.5))    # holes are (n^2)/7.5
        elif self.slip == 2:
            holes_num = int((self.n ** (3 / 2)) / 2)  # holes are (n^(3/2))/2.5
        holes = set()
        while len(holes) < holes_num:
            hole = (np.random.randint(self.n), np.random.randint(self.n))
            if hole != self.start and hole != self.goal:
                holes.add(hole)
        return holes

    def step(self, action):
        """
        This function determines the FINAL action taken based on the slip probabilities.
        It takes as input the "inputed" action and returns the calculated REAL action.
        """
        if self.done:
            print("Game is over. Reset the environment to play again.")
            return self.state, 0, self.done

        # Available moves
        moves = {0: (-1, 0), 1: (0, -1), 2: (1, 0), 3: (0, 1)}  # Up, Left, Down, Right

        if self.slip == 0:
            slip_probabilities = [1.0, 0.0, 0.0]    # Deterministic
        elif self.slip == 1:
            slip_probabilities = [0.7, 0.15, 0.15]  # Slippery
        elif self.slip == 2:
            slip_probabilities = [0.4, 0.3, 0.3]    # Very slippery
        else:
            slip_probabilities = [1.0, 0.0, 0.0]    # Deterministic

        # Calculating the move based on the probabilities of slipping each time
        if action == 0:     # Up (↑)
            choices = [0, 1, 3]         # Up (↑) P(1), Left (←) P(2), Right (→) P(3)
        elif action == 1:   # Left (←)
            choices = [1, 2, 0]         # Left (←) P(1), Down (↓) P(2), Up (↑) P(3)
        elif action == 2:   # Down (↓)
            choices = [2, 1, 3]         # Down (↓) P(1), Left (←) P(2), Right (→) P(3)
        elif action == 3:   # Right (→)
            choices = [3, 2, 0]         # Right (→) P(1), Down (↓) P(2), Up (↑) P(3)

        # Action based on slip probabilities
        final_action = np.random.choice(choices, p=slip_probabilities)
        move = moves[final_action]

        # Calculate new position
        new_row = np.clip(self.state[0] + move[0], 0, self.n - 1)
        new_col = np.clip(self.state[1] + move[1], 0, self.n - 1)
        self.state = (new_row, new_col)

        # Check for holes and goal
        if self.state in self.holes:
            self.done = True
            return self.state, -20, self.done   # Hole
        elif self.state == self.goal:
            self.done = True
            return self.state, 100, self.done   # Goal
        return self.state, -0.1, self.done      # Safe

    def reset(self):
        """
        Resets the game state to the starting state
        """
        self.state = self.start
        self.done = False
        return self.state

    def render(self):
        """
        Renders the environment in the terminal
        """
        print(" " + "_" * ((3*self.n)-1))
        for i in range(self.n):
            row = "|"
            for j in range(self.n):
                if (i, j) == self.state:
                    cell = "P"
                elif (i, j) == self.goal:
                    cell = "G"
                elif (i, j) in self.holes:
                    cell = "X"
                else:
                    cell = " "
                if j == self.n - 1:
                    row += f"{cell} |"
                else:
                    row += f"{cell}  "
            print(row)
        print(" " + "‾" * ((3*self.n)-1))

    def print_best_actions_grid(self):
        """
        Function to print grid with best actions in the Terminal
        """
        action_symbols = ['↑', '←', '↓', '→']  # Up, Left, Down, Right
        best_actions = np.zeros(self.grid_size, dtype=str)

        for row in range(self.grid_size[0]):
            for col in range(self.grid_size[1]):
                state_vector = np.zeros(np.prod(self.grid_size))
                state_index = np.ravel_multi_index((row, col), self.grid_size)
                state_vector[state_index] = 1
                state_vector = np.reshape(state_vector, [1, -1])

                best_action = self.best_move_per_cell[state_index]
                best_actions[row, col] = action_symbols[best_action]

        # Placing symbols for goal(G), and holes(X)
        best_actions[self.goal] = 'G'   # goal
        for hole in self.holes:
            best_actions[hole] = 'X'    # holes

        print("Best actions grid:")
        for row in range(self.grid_size[0]):
            print(' '.join(best_actions[row]))

    def set_best_move(self, state_index, best_move):
        self.best_move_per_cell[state_index] = best_move

    def play_game(self):
        """
        Game setup function.
        Here the 2 user choice GUI's are created and the parameters chosen are stored in order
        to create the environment. This function also directs the program to 1 of the 2 main
        game functions (User plays and Agent plays).
        """
        # initializing Pygame
        pygame.init()

        black = (0, 0, 0)
        grey = (211, 211, 211)
        player_color = (20, 150, 20)
        agent_color = (150, 20, 20)
        slip_buttons_color = (91, 146, 229)

        screen = pygame.display.set_mode((560, 350))

        # Background -> grey
        screen.fill(grey)

        font = pygame.font.Font(None, 36)
        title_font = pygame.font.Font(None, 58)
        title_font.set_underline(5)

        title_text_1 = title_font.render("Game  Mode  Selection", False, black)
        title_text_2_1 = title_font.render("Choose the Slipperiness", False, black)
        title_text_2_2 = title_font.render("of the environment", False, black)

        # Buttons for "Player", "Agent", "Not Slippery", "Slippery" and "Very Slippery"
        player_button = pygame.Rect(80, 190, 150, 50)
        agent_button = pygame.Rect(330, 190, 150, 50)
        not_slippery_button = pygame.Rect(15, 230, 180, 50)
        slippery_button = pygame.Rect(220, 230, 120, 50)
        very_slippery_button = pygame.Rect(365, 230, 180, 50)

        running = True
        Selection_1 = True
        Player = False

        while running:
            if Selection_1:
                title_rect = title_text_1.get_rect(center=(280, 100))
                screen.blit(title_text_1, title_rect)
                # Draw buttons
                pygame.draw.rect(screen, player_color, player_button)
                pygame.draw.rect(screen, agent_color, agent_button)
                # Button labels
                player_label = font.render("Player", True, black)
                agent_label = font.render("Agent", True, black)

                screen.blit(player_label, (player_button.x + 40, player_button.y + 10))
                screen.blit(agent_label, (agent_button.x + 40, agent_button.y + 10))
            elif not Selection_1:
                title_rect = title_text_2_1.get_rect(center=(280, 60))
                screen.blit(title_text_2_1, title_rect)
                title_rect = title_text_2_2.get_rect(center=(280, 120))
                screen.blit(title_text_2_2, title_rect)
                # Draw buttons
                pygame.draw.rect(screen, slip_buttons_color, not_slippery_button)
                pygame.draw.rect(screen, slip_buttons_color, slippery_button)
                pygame.draw.rect(screen, slip_buttons_color, very_slippery_button)
                # Button labels
                not_slippery_label = font.render("NOT Slippery", True, black)
                slippery_label = font.render("Slippery", True, black)
                very_slippery_label = font.render("Very Slippery", True, black)

                screen.blit(not_slippery_label, (not_slippery_button.x + 10, not_slippery_button.y + 12))
                screen.blit(slippery_label, (slippery_button.x + 10, slippery_button.y + 12))
                screen.blit(very_slippery_label, (very_slippery_button.x + 10, very_slippery_button.y + 12))

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    pygame.quit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if Selection_1:
                        if player_button.collidepoint(event.pos):
                            Player = True
                            Selection_1 = False
                            screen.fill(grey)

                        elif agent_button.collidepoint(event.pos):
                            Player = False
                            Selection_1 = False
                            screen.fill(grey)

                    elif not Selection_1:
                        if not_slippery_button.collidepoint(event.pos):
                            self.slip = 0
                            self.gamma = 0.6
                            self.alpha = 0.35
                            self.holes = self.generate_holes()
                            print("\nInitial Random Map:")
                            self.render()
                            print("\n")
                            if Player:
                                self.player_plays_game()
                            elif not Player:
                                self.agent_plays_game(self.gamma, self.alpha)
                            running = False

                        elif slippery_button.collidepoint(event.pos):
                            self.slip = 1
                            self.gamma = 0.95
                            self.alpha = 0.45
                            self.holes = self.generate_holes()
                            print("\nInitial Random Map:")
                            self.render()
                            print("\n")
                            if Player:
                                self.player_plays_game()
                            elif not Player:
                                self.agent_plays_game(self.gamma, self.alpha)
                            running = False

                        elif very_slippery_button.collidepoint(event.pos):
                            self.slip = 2
                            self.gamma = 0.95
                            self.alpha = 0.35
                            self.holes = self.generate_holes()
                            print("\nInitial Random Map:")
                            self.render()
                            print("\n")
                            if Player:
                                self.player_plays_game()
                            elif not Player:
                                self.agent_plays_game(self.gamma, self.alpha)
                            running = False

    def agent_plays_game(self, gamma, alpha, cell_size=40):
        """
        Used when the "agent" option is chosen
        The function initiates the game, the Graphical Interface and the graphical analyzer
        that suggests the best moves.
        After that the "AGENT" plays based on the best determined moves.
        Using Q-learning we are making the agent adapt each time he plays the game
        :param gamma: discount factor
        :param alpha: learning rate
        :param cell_size: DON'T CHANGE IT !, predetermined cell size in pixels (40x40). Crucial for visual analyzer !
        """
        Q = {}  # Initialize Q as an empty dictionary

        # initializing Pygame
        pygame.init()

        white = (255, 255, 255)
        black = (0, 0, 0)
        lilac = (225,196,255)
        red = (245, 20, 20)
        blue = (20, 20, 245)
        green = (20, 245, 20)

        # Setting the display size to be the environment grid and some buffer zone on the screen
        window_size = ((self.n * cell_size)+40, (self.n * cell_size+2)+40)
        screen = pygame.display.set_mode(window_size)
        pygame.display.set_caption('Random Frozen Lake MAP')

        # Moving the window to a specific location on the screen, for the analyzer to be able to see it
        moving_window = win32gui.FindWindow(None, 'Random Frozen Lake MAP')
        win32gui.SetWindowPos(moving_window, 0, 80, 80, 0, 0, 0x0001)

        # Background -> white
        screen.fill(white)

        font = pygame.font.Font(None, 36)
        outline_font = pygame.font.Font(None, 36)
        # Game loop
        running = True
        total_reward = 0
        index = 0
        counter = 0
        past_states = []
        state_visit_counts = {}

        while running:
            # Render the game state
            screen.fill(white)
            k = 0

            # Creating the graphical interface
            for i in range(self.n):
                for j in range(self.n):
                    rect_1 = pygame.Rect(j * cell_size + 20, i * cell_size + 20, cell_size, cell_size)
                    rect_2 = pygame.Rect(j * cell_size + 21, i * cell_size + 21, cell_size - 2, cell_size - 2)
                    pygame.draw.rect(screen, black, rect_1, 1)

                    if (i, j) == self.state and not self.done:
                        pygame.draw.rect(screen, green, rect_2)
                        # Arrows for the best move in the cell we are at, at the moment
                        best_move = self.best_move_per_cell[k]
                        draw_arrow(screen, best_move, rect_2)
                    elif (i, j) == self.goal:
                        pygame.draw.rect(screen, red, rect_2)
                    elif (i, j) in self.holes:
                        pygame.draw.rect(screen, blue, rect_2)
                    else:
                        pygame.draw.rect(screen, lilac, rect_2)
                        # Arrows for the best move in each cell (not including holes and goal since they are END states)
                        best_move = self.best_move_per_cell[k]
                        draw_arrow(screen, best_move, rect_2)

                    k += 1

            pygame.display.flip()  # Update the display

            if index == 0:
                time.sleep(1)
                # Using the visual Analyzer
                Agent_suggestions = GameAnalyzer(self.n, cell_size)
                image = Agent_suggestions.capture_game_area()           # Getting the screenshot using MSS
                elements = Agent_suggestions.find_elements(image)       # Proccesing the screenshot using OpenCV
                best_moves = Agent_suggestions.calculate_best_moves(elements)   # Calculating the best moves using the data gained
                sorted_positions = sorted(best_moves.keys(), key=lambda position: (position[1], position[0]))
                ordered_best_moves = {pos: best_moves[pos] for pos in sorted_positions}
                for pos, move in ordered_best_moves.items():
                    self.set_best_move(index, move)
                    index += 1

                self.print_best_actions_grid()
                # Initializing Q-values based on the vizual analyzer's best moves
                for s in range(self.n * self.n):
                    Q[s] = {}  # Initialize Q[s] as an empty dictionary
                    for a in range(4):
                        if self.best_move_per_cell[s] == a:
                            Q[s][a] = 10
                        else:
                            Q[s][a] = 0

            # new game state (kainourgia kinisi)
            state_index = self.state[0] * self.n + self.state[1]
            # Counting how many times we visited each state
            if state_index in state_visit_counts:
                state_visit_counts[state_index] += 1
            else:
                state_visit_counts[state_index] = 1
            # Keeping a list of all past states to use to improve our best_moves
            past_states.append(state_index)
            # Checking if we are stuck in an infinite loop (only in Non-slippery environments)
            if self.slip == 0 and state_visit_counts[state_index] > 5:
                all_directions = [0, 1, 2, 3]
                move_dir = self.best_move_per_cell[state_index]
                all_directions.remove(move_dir)
                alternative_direction = random.choice(all_directions)
                next_state, reward, done = self.step(alternative_direction)
                self.set_best_move(state_index, alternative_direction)
            else:
                next_state, reward, done = self.step(self.best_move_per_cell[state_index])
            total_reward += reward
            next_state_index = next_state[0] * self.n + next_state[1]
            # Computing the new Q value for this state
            # Q_new = Q_old + α(reward + γ(max(Q_next_state.values)) - Q_old)
            Q[state_index][self.best_move_per_cell[state_index]] = Q[state_index][self.best_move_per_cell[state_index]] +\
                alpha * (reward + gamma * max(Q[next_state_index].values()) - Q[state_index][self.best_move_per_cell[state_index]])

            time.sleep(0.025)
            counter += 1

            if done:  # If we get to a final state, i print the reward and reset the game
                message = f"Final Reward: {round(total_reward, 2)}"
                message_2 = "Recalculating best moves"

                for dx, dy in [(x, y) for x in range(-2, 3) for y in range(-2, 3) if x != 0 or y != 0]:
                    outline_text = outline_font.render(message, True, (0, 0, 0))
                    outline_text_2 = outline_font.render(message_2, True, (0, 0, 0))
                    text_rect = outline_text.get_rect(center=(window_size[0] // 2 + dx, window_size[1] // 2 + dy))
                    text_rect_2 = outline_text.get_rect(center=(window_size[0] // 2 + dx - 35, window_size[1] // 2 + dy + 25))
                    screen.blit(outline_text, text_rect)
                    screen.blit(outline_text_2, text_rect_2)

                text = font.render(message, True, red)
                text_2 = font.render(message_2, True, red)
                text_rect = text.get_rect(center=(window_size[0] // 2, window_size[1] // 2))
                text_rect_2 = text.get_rect(center=(window_size[0] // 2 - 35, window_size[1] // 2 + 25))
                screen.blit(text, text_rect)
                screen.blit(text_2, text_rect_2)

                pygame.display.flip()
                self.reset()
                print("Reward of this game: \t", total_reward, "\n")
                total_reward = 0
                past_states = []
                state_visit_counts = {}
                counter = 0
                for s in range(self.n * self.n):
                    self.set_best_move(s, max(Q[s], key=Q[s].get))
                self.print_best_actions_grid()
                pygame.time.wait(269)
                time.sleep(0.25)

            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

        pygame.quit()
        sys.exit()

    def player_plays_game(self, cell_size=40):
        """
        Used when the "player" option is chosen
        The function initiates the game, the Graphical Interface and the graphical analyzer
        that suggests the best moves.
        After that the "USER" can play the game using the Arrow keys.
        NOTE:   There is no underlying agent, thus the suggested moves don't change.
                They get set from the visual analyzer, who has a good estimate, but
                if there are mistakes they don't get corrected. It is just a space
                for the user to try out the Frozen Lake environment / game!!!
        """
        # initializing Pygame
        pygame.init()

        white = (255, 255, 255)
        black = (0, 0, 0)
        lilac = (225,196,255)
        red = (245, 20, 20)
        blue = (20, 20, 245)
        green = (20, 245, 20)

        # Setting the display size to be the environment grid and some buffer zone on the screen
        window_size = ((self.n * cell_size)+40, (self.n * cell_size+2)+40)
        screen = pygame.display.set_mode(window_size)
        pygame.display.set_caption('Random Frozen Lake MAP')

        # Moving the window to a specific location on the screen, for the analyzer to be able to see it
        moving_window = win32gui.FindWindow(None, 'Random Frozen Lake MAP')
        win32gui.SetWindowPos(moving_window, 0, 80, 80, 0, 0, 0x0001)

        # Background -> white
        screen.fill(white)

        # Key presses mapping
        key_action_mapping = {
            pygame.K_UP: 0,
            pygame.K_LEFT: 1,
            pygame.K_DOWN: 2,
            pygame.K_RIGHT: 3
        }

        font = pygame.font.Font(None, 36)
        outline_font = pygame.font.Font(None, 36)
        # Game loop
        running = True
        total_reward = 0
        index = 0
        while running:
            # Render the game state
            screen.fill(white)
            k = 0

            # Creating the graphical interface
            for i in range(self.n):
                for j in range(self.n):
                    rect_1 = pygame.Rect(j * cell_size + 20, i * cell_size + 20, cell_size, cell_size)
                    rect_2 = pygame.Rect(j * cell_size + 21, i * cell_size + 21, cell_size - 2, cell_size - 2)
                    pygame.draw.rect(screen, black, rect_1, 1)

                    if (i, j) == self.state and not self.done:
                        pygame.draw.rect(screen, green, rect_2)
                        # Arrows for the best move in the cell we are at, at the moment
                        best_move = self.best_move_per_cell[k]
                        draw_arrow(screen, best_move, rect_2)
                    elif (i, j) == self.goal:
                        pygame.draw.rect(screen, red, rect_2)
                    elif (i, j) in self.holes:
                        pygame.draw.rect(screen, blue, rect_2)
                    else:
                        pygame.draw.rect(screen, lilac, rect_2)
                        # Arrows for the best move in each cell (not including holes and goal since they are END states)
                        best_move = self.best_move_per_cell[k]
                        draw_arrow(screen, best_move, rect_2)

                    k += 1

            pygame.display.flip()  # Update the display

            if index == 0:
                time.sleep(1)
                # Using the visual Analyzer
                Agent_suggestions = GameAnalyzer(self.n, cell_size)
                image = Agent_suggestions.capture_game_area()           # Getting the screenshot using MSS
                elements = Agent_suggestions.find_elements(image)       # Proccesing the screenshot using OpenCV
                best_moves = Agent_suggestions.calculate_best_moves(elements)   # Calculating the best moves using the data gained
                sorted_positions = sorted(best_moves.keys(), key=lambda position: (position[1], position[0]))
                ordered_best_moves = {pos: best_moves[pos] for pos in sorted_positions}
                for pos, move in ordered_best_moves.items():
                    self.set_best_move(index, move)
                    index += 1

                self.print_best_actions_grid()

            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key in key_action_mapping:
                        # new game state (kainourgia kinisi)
                        next_state, reward, done = self.step(key_action_mapping[event.key])
                        total_reward += reward

                        if done:  # If we get to a final state, i print the reward and reset the game
                            message = f"Final Reward: {round(total_reward,2)}"

                            for dx, dy in [(x, y) for x in range(-2, 3) for y in range(-2, 3) if x != 0 or y != 0]:
                                outline_text = outline_font.render(message, True, (0, 0, 0))
                                text_rect = outline_text.get_rect(center=(window_size[0] // 2 + dx, window_size[1] // 2 + dy))
                                screen.blit(outline_text, text_rect)

                            text = font.render(message, True, red)
                            text_rect = text.get_rect(center=(window_size[0] // 2, window_size[1] // 2))
                            screen.blit(text, text_rect)

                            pygame.display.flip()
                            self.reset()
                            print("Reward of this game: \t", total_reward, "\n")
                            total_reward = 0
                            pygame.time.wait(2069)
                            time.sleep(2)

        pygame.quit()
        sys.exit()

