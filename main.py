from RandomFrozenLake import RandomFrozenLake

"""
File:   main.py
Author: Koutounidis Christos-Angelos
Description: Main call file for the program
"""

# Creating an random Frozen Lake environment
FL_Environment = RandomFrozenLake()
FL_Environment.play_game()

# Printing the initial random map
print("Initial Random Map:")
FL_Environment.render()
