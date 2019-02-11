# Origin is at top left. Positive x is right, and positive y is down.
# width is along x; height is along y.
#
# Coordinates are (x,y) pairs.

import sys
import numpy as np
import random

class Tile:
    """A tile is a rectangular block of dimensions dx, dy.
    It can move in four directions N E S W"""

    class Move:
        North = (0,-1)
        East = (1, 0)
        South = (0, 1)
        West = (-1, 0)
        
        @classmethod
        def to_str(cls, direction):
            if direction == Tile.Move.North:
                return "N"
            if direction == Tile.Move.South:
                return "S"
            if direction == Tile.Move.East:
                return "E"
            if direction == Tile.Move.West:
                return "W"
            raise ValueError("Unrecognized direction %s" % (direction))

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

    def __init__(self, tiles, locations, w, h, board_id=0):
        """tiles and locations have index correspondence
        Assumption: If two boards have the same id, they are exactly
        the same But two exactly the same boards may not have the
        same ids
        """
        self._tiles = {tiles[i].name:(tiles[i],
                                      locations[i])
                       for i in range(len(tiles))}
        self._w = w
        self._h = h
        self._goal = None
        # Internal representation - a grid. Each cell
        # is an integer. If non-zero, refers to one cell
        # in the tile mapped by that integer. If zero, empty.
        self._rep = None
        names = list(sorted(self._tiles.keys()))
        self._name_to_id = {names[i]:(i+1) for i in range(len(names))}
        self._id_to_name = {(i+1):names[i] for i in range(len(names))}
        self._update_internal_rep()

        self._board_id = board_id

    def set_board_id(self, board_id):
        """
        Assumption: If two boards have the same id, they are exactly
        the same But two exactly the same boards may not have the
        same ids
        """
        self._board_id = board_id

    @property
    def board_id(self):
        return self._board_id
        
    def _update_internal_rep(self):
        self._rep = np.zeros((self._h, self._w), dtype=int)
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

    def tile_loc(self, name):
        """Returns the top-left corner coordinates of tile `name`"""
        return self._tiles[name][1]

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
        region = self._rep[y+dy:y+h+dy, x+dx:x+w+dx]
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
        w, h = self._tiles[name][0].dim
        dx, dy = direction
        if self.movable(name, direction):            
            self._tiles[name] = (self._tiles[name][0],
                                 (x+dx, y+dy))
            self._rep[y:y+h, x:x+w] = 0
            self._rep[y+dy:y+h+dy, x+dx:x+w+dx] = self._name_to_id[name]
            self._board_id = random.randint(0, 10000)
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
    
    def __eq__(self, other):
        # if self._rep.shape == other._rep.shape:
        #     uniq = np.unique(self._rep == other._rep)
        #     return len(uniq) == 1 and uniq[0] is True
        # return False
        return self._board_id == other._board_id

    def __hash__(self):
        """If two boards are the same, their has must be the same"""
        return self._board_id
        
