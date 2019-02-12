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
    
    def same_shape_as(self, other_tile):
        return self.dim == other_tile.dim
    

class Board:
    """A board is a collection of tiles with given
    initial locations all inside a rectangular boundary.
    The board monitors the locations of all the tiles,
    therefore, the object is mutable.
    """
    symbols = ["."] + list(map(str, np.arange(1,10)))\
              + [chr(ord("a")+i) for i in range(26)]

    def __init__(self, tiles, locations, w, h, unique_tiles=False):
        """tiles and locations have index correspondence.
        `unique_tiles` is True if tiles of the same shape are
        treated as different.
        """
        self._tiles = {tiles[i].name:(tiles[i],
                                      locations[i])
                       for i in range(len(tiles))}
        self._w = w
        self._h = h
        self._goal = None
        self._unique_tiles = unique_tiles
        # Internal representation - a grid. Each cell
        # is an integer. If non-zero, refers to one cell
        # in the tile mapped by that integer. If zero, empty.
        self._rep = None

        names = list(sorted(self._tiles.keys()))
        self._name_to_id = {names[i]:(i+1) for i in range(len(names))}
        self._id_to_name = {(i+1):names[i] for i in range(len(names))}

        if not self._unique_tiles:
            self._rep_shape = None  # tiles with the same shape map to the same integer
            self._name_to_shape_id = {}
            shapes = {}
            for name in self._tiles:
                sh = self._tiles[name][0].dim
                if sh not in shapes:
                    shapes[sh] = set()
                shapes[sh].add(name)
            for i, sh in enumerate(sorted(shapes)):
                for name in shapes[sh]:
                    self._name_to_shape_id[name] = i+1  # +1 since 0 means empty
        self._update_internal_rep()
        
    def _update_internal_rep(self):
        self._rep = np.zeros((self._h, self._w), dtype=int)
        if not self._unique_tiles:
            self._rep_shape = np.zeros((self._h, self._w), dtype=int)
        for name in self._name_to_id:
            x, y = self._tiles[name][1]
            tile = self._tiles[name][0]
            tid = self._name_to_id[name]
            self._rep[y:y+tile.h, x:x+tile.w] = tid
            if not self._unique_tiles:
                sid = self._name_to_shape_id[name]
                self._rep_shape[y:y+tile.h, x:x+tile.w] = sid

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
        # occupied by other tiles in the moved area.
        x, y = self._tiles[name][1]
        w, h = self._tiles[name][0].dim
        dx, dy = direction
        region = self._rep[y+dy:y+h+dy, x+dx:x+w+dx]
        present_tids = sorted(np.unique(region))
        if len(present_tids) == 1\
           and present_tids[0] == 0:
            return False
        elif len(present_tids) == 2\
             and present_tids[0] == 0\
             and present_tids[1] == self._name_to_id[name]:
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
            if not self._unique_tiles:
                self._rep_shape[y:y+h, x:x+w] = 0
                self._rep_shape[y+dy:y+h+dy, x+dx:x+w+dx] = self._name_to_shape_id[name]
            return True
        else:
            return False

    def print_ascii(self, legend=True):
        for r in range(self._rep.shape[0]):
            for c in range(self._rep.shape[1]):
                sys.stdout.write(Board.symbols[self._rep[r,c]])
            sys.stdout.write("\n")
        if legend:
            print("")
            for tid in sorted(self._id_to_name):
                print("%s: %s" % (Board.symbols[tid], self._id_to_name[tid]))
    
    def __eq__(self, other):
        if self._rep.shape == other._rep.shape:
            if self._unique_tiles:
                uniq = np.unique(self._rep == other._rep)
            else:
                uniq = np.unique(self._rep_shape == other._rep_shape)
            return len(uniq) == 1 and uniq[0] == True
        return False
        # return self._board_id == other._board_id

    def __hash__(self):
        """If two boards are the same, their hash must be the same"""
        return int(np.sum(np.array([self._rep[:2], self._rep[-2:]])))
        
    def __str__(self):
        return self.__repr__()
    
    def __repr__(self):
        res = "\n"
        for r in range(self._rep.shape[0]):
            for c in range(self._rep.shape[1]):
                res += Board.symbols[self._rep[r,c]]
            res += "\n"
        return res
