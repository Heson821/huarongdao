# Origin is at top left. Positive x is right, and positive y is down.
# width is along x; height is along y.
#
# Coordinates are (x,y) pairs.

import sys
import numpy as np

class Tile:
    """A tile is a rectangular block of dimensions dx, dy.
    It can move in four directions N E S W"""

    class Move:
        North = (0,-1)
        East = (1, 0)
        South = (0, 1)
        West = (-1, 0)

    def __init__(self, name, w, h):
        self._name = name
        self._w = w
        self._h = h

    @property
    def name(self):
        return self._name
    @property
    def w(self):
        return self._w
    @property
    def h(self):
        return self._h
    

class Board:
    """A board is a collection of tiles with given
    initial locations all inside a rectangular boundary.
    The board monitors the locations of all the tiles."""
    symbols = ["."] + list(map(str, np.arange(1,10)))\
              + [chr(ord("a")+i) for i in range(26)]

    def __init__(self, tiles, locations, w, h):
        """tiles and locations have index correspondence"""
        self._tiles = {tiles[i].name:(tiles[i],
                                      locations[i])
                       for i in range(len(tiles))}
        self._w = w
        self._h = h
        self._goal = None

    def _move_tile(self, name, direction):
        """Attempts to move `tile` for one step in `direction`.
        If succeed, return True. Otherwise False."""
        x, y = self._tiles[name][1]
        dx, dy = direction
        if x + dx < 0 or x + dx >= self._w:
            return False
        if y + dy < 0 or y + dy >= self._h:
            return False
        self._tiles[name] = (self._tiles[name][0],
                             (x+dx, y+dy))
        return True

    def print_ascii(self):
        grid = np.zeros((self._h, self._w), dtype=int)
        names = list(sorted(self._tiles.keys()))
        for i, name in enumerate(names):
            x, y = self._tiles[name][1]
            tile = self._tiles[name][0]
            for dy in range(tile.h):
                for dx in range(tile.w):
                    grid[y+dy, x+dx] = i+1
        for r in range(grid.shape[0]):
            for c in range(grid.shape[1]):
                sys.stdout.write(Board.symbols[grid[r,c]])
            sys.stdout.write("\n")
        print("")
        for i, name in enumerate(names):
            print("%s: %s" % (Board.symbols[i+1], name))
