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
    @property
    def dim(self):
        return (self._w, self._h)
    

class Board:
    """A board is a collection of tiles with given
    initial locations all inside a rectangular boundary.
    The board monitors the locations of all the tiles,
    therefore, the object is mutable.
    """
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
        # Internal representation - a grid. Each cell
        # is an integer. If non-zero, refers to one cell
        # in the tile mapped by that integer. If zero, empty.
        self._rep = np.zeros((self._h, self._w), dtype=int)
        names = list(sorted(self._tiles.keys()))
        self._name_to_id = {names[i]:(i+1) for i in range(len(names))}
        self._id_to_name = {(i+1):names[i] for i in range(len(names))}
        self._update_internal_rep()
        
    def _update_internal_rep(self):
        for name in self._name_to_id:
            x, y = self._tiles[name][1]
            tile = self._tiles[name][0]
            tid = self._name_to_id[name]
            for dy in range(tile.h):
                for dx in range(tile.w):
                    self._rep[y+dy, x+dx] = tid

    def generate_possible_moves(self):
        """Returns a set of moves (name, (dx, dy))
        that are possible for the current board configuration"""
        directions = [Tile.Move.North,
                      Tile.Move.East,
                      Tile.Move.South,
                      Tile.Move.West]
        actions = []
        for name in self._tiles:
            tile = self._tiles[name][0]
            for d in directions:
                if self.movable(name, d):
                    actions.append((name, d))
        return actions

    def tile_at(self, x, y):
        """Returns the name of the tile at location (x,y). If
        empty, return None"""
        if self._rep[x,y] == 0:
            return None
        else:
            return self._id_to_name[self._rep[x,y]]

    def will_collide(self, name, direction):
        # Move tile with `name` along direction.
        # Check if there is non-zero numbers in the region
        # occupied in the moved area.
        x, y = self._tiles[name][1]
        w, h = self._tiles[name][0].dim
        dx, dy = direction
        region = self._rep[x+dx:x+w+dx, y+dy:y+h+dy]
        if np.sum(region) == 0:
            return False
        return True

    def movable(self, name, direction):
        x, y = self._tiles[name][1]
        w, h = self._tiles[name][0].dim
        dx, dy = direction
        # within boundary
        if x + dx < 0 or x + w-1 + dx >= self._w:
            return False
        if y + dy < 0 or y + h-1 + dy >= self._h:
            return False
        # check collision
        if self.will_collide(name, direction):
            return False
        return True

    def move_tile(self, name, direction):
        """Attempts to move `tile` for one step in `direction`.
        If succeed, return True. Otherwise False."""
        x, y = self._tiles[name][1]
        dx, dy = direction
        if self.movable(name, direction):
            self._tiles[name] = (self._tiles[name][0],
                                 (x+dx, y+dy))
            
            return True
        else:
            return False

    def print_ascii(self):
        for r in range(self._rep.shape[0]):
            for c in range(self._rep.shape[1]):
                sys.stdout.write(Board.symbols[self._rep[r,c]])
            sys.stdout.write("\n")
        print("")
        for tid in sorted(self._id_to_name):
            print("%s: %s" % (Board.symbols[tid], self._id_to_name[tid]))
