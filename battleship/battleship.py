"""
A battleship game.

There are two 10x10 grids. One for your ships and one to track your shots.
Each player gets a fleet of 10 ships. The ships are:
    1x Aircraft Carrier (4 squares)
    2x Battleship (3 squares)
    3x Cruiser (2 squares)
    4x Destroyer (1 square)

The game is played in turns. Each turn, the player chooses a square to shoot
at. If the square contains a ship, it is marked as hit and the player gets
another turn. If the square does not contain a ship, it is marked as miss
and the turn ends. The game ends when all ships have been sunk. The ships cannot be placed diagonally and cannot be adjacent to each other, not even diagonally.

Finally the game needs to be able to save and load the game state, because we are going to train an AI to play the game.
"""

from dataclasses import dataclass, field
import random
import copy
import threading
import time
from typing import Set, List


def get_neighbours(x, y):
    """Return the neighbours of a square."""
    neighbours = []
    for i in range(-1, 2):
        for j in range(-1, 2):
            neighbours.append((x + i, y + j))
    return neighbours


@dataclass
class Ship:
    """A ship in the game."""
    size: int
    squares: list[tuple[int, int]]


@dataclass
class Player:
    """A player in the game."""
    ships_left: int = 10
    ships: list[Ship] = field(default_factory=list)

    # Board is a 2D array, where
    # 0 is unknown
    # 1 is a miss
    # 2 is a hit
    guesses: list[list[int]] = field(default_factory=lambda: [[0] * 10 for _ in range(10)])

    def random_place_ships(self):
        """Place the ships randomly, but make sure they don't overlap and are not adjacent."""

        ships = [4, 3, 3, 2, 2, 2, 1, 1, 1, 1]
        occupied_squares = set()
        for ship in ships:
            while True:
                x = random.randint(0, 10 - ship)
                y = random.randint(0, 10 - ship)
                if random.choice([True, False]):
                    squares = [(x + i, y) for i in range(ship)]
                else:
                    squares = [(x, y + i) for i in range(ship)]
                if any(square in occupied_squares for square in squares):
                    continue
                self.ships.append(Ship(ship, squares))
                for square in squares:
                    occupied_squares.add(square)
                    for neighbour in get_neighbours(*square):
                        occupied_squares.add(neighbour)
                break


class Game:
    def __init__(self, players=[Player(), Player()]):
        self.players: List[Player] = players
        self.current_player = 0
        self.victory = -1
        self.step = 0

    def check_legal(self, x, y, player):
        """Check if a shot is legal."""
        if x < 0 or x > 9 or y < 0 or y > 9:
            return False
        if self.players[player].guesses[x][y] != 0:
            return False
        return True

    def turn(self, x, y):
        """Take a turn."""
        # check if the shot is legal - an illegal move will be ignored
        if self.victory != -1:
            return
        self.step += 1
        if not self.check_legal(x, y, self.current_player):
            return
        # check if the shot hit a ship
        for ship in self.players[1 - self.current_player].ships:
            if (x, y) in ship.squares:
                ship.size -= 1
                self.players[self.current_player].guesses[x][y] = 2
                if ship.size == 0:
                    # mark all the squares around the ship as misses
                    for square in ship.squares:
                        for neighbour in get_neighbours(*square):
                            if self.check_legal(*neighbour, self.current_player):
                                self.players[self.current_player].guesses[neighbour[0]][neighbour[1]] = 1
                    self.players[1-self.current_player].ships_left -= 1
                    if self.players[1-self.current_player].ships_left == 0:
                        self.victory = self.current_player
                break
        else:
            # if the shot didn't hit a ship, change the current player
            # self.current_player = 1 - self.current_player
            self.players[self.current_player].guesses[x][y] = 1
