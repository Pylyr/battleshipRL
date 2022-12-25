"""
A battleship game.

There are two grids. One for your ships and one to track your shots.
Each player gets a fleet of ships. The ships are:
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
from typing import Set, List
import numpy as np

LENGTH = 10
WIDTH = 10
SHIP_SIZES = [4, 4, 4]


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
    squares: Set[tuple[int, int]]

    def __hash__(self) -> int:
        return hash(tuple(self.squares))


@dataclass
class Player:
    """A player in the game."""
    ships_left: int = len(SHIP_SIZES)
    ships: Set[Ship] = field(default_factory=set)

    # Board is a 2D array, where
    # 0 is unknown
    # 1 is a miss
    # 2 is a hit

    guesses: np.ndarray = field(default_factory=lambda: np.zeros((LENGTH, WIDTH), dtype=int))

    def random_place_ships(self):
        """Place the ships randomly, but make sure they don't overlap and are not adjacent."""

        occupied_squares = set()
        for ship_size in SHIP_SIZES:
            while True:
                x = random.randint(0, LENGTH - ship_size)
                y = random.randint(0, WIDTH - ship_size)
                # pick a random direction between up, down, left and right
                direction = random.randint(0, 3)
                # check that the ship fits on the board
                if direction == 0 and y + ship_size >= WIDTH:
                    continue
                elif direction == 1 and y - ship_size < 0:
                    continue
                elif direction == 2 and x - ship_size < 0:
                    continue
                elif direction == 3 and x + ship_size >= LENGTH:
                    continue

                if direction == 0:
                    squares = {(x, y + i) for i in range(ship_size)}
                elif direction == 1:
                    squares = {(x, y - i) for i in range(ship_size)}
                elif direction == 2:
                    squares = {(x - i, y) for i in range(ship_size)}
                else:
                    squares = {(x + i, y) for i in range(ship_size)}

                # check if the squares are occupied
                if squares & occupied_squares:
                    continue

                # add the squares and the neighbours to the occupied squares
                new_squares = squares.copy()
                for square in squares:
                    new_squares |= set(get_neighbours(*square))
                occupied_squares |= new_squares
                self.ships.add(Ship(ship_size, squares))
                break


class Game:
    def __init__(self, players=[Player(), Player()]):
        self.players: List[Player] = players
        self.current_player = 0
        self.victory = -1
        self.step = 0

    def check_legal(self, x, y, player):
        """Check if a shot is legal."""
        if x < 0 or x >= LENGTH or y < 0 or y >= WIDTH:
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


p = Player()
print(p.random_place_ships())
