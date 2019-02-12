from board import Board, Tile
from collections import deque
import copy
import random
import sys


class Solver:

    def __init__(self, board):
        self._board = board

    def set_goal(self, target_tile_name, target_location):
        """Sets a goal of moving target tile to target location (top-left)"""
        self._goal = (target_tile_name, target_location)

    def set_board(self, board):
        self._board = board

    def solve(self):
        raise NotImplemented


class BFSSolver(Solver):

    """Solves the problem with BFS."""
    # TODO: This is computationally very expensive
    # due to all the copy calls, and "not in"
    def solve(self):
        q = deque()
        path = {}
        q.append(self._board)
        visited = set({self._board})
        while len(q) > 0:
            current = q.popleft()
            # Check if goxal is reached
            if current.tile_loc(self._goal[0]) == self._goal[1]:
                # Return path: a list of boards
                trace = [current]
                b = current
                seen = set()
                while b not in seen:
                    seen.add(b)
                    if b in path:
                        trace.append(path[b])
                        b = path[b]
                    if b == trace[0]:
                        break
                return list(reversed(trace))
            # Explore all possible actions
            actions = current.generate_possible_moves()
            sys.stdout.write("Exploring board %s" % current)
            for name, a in actions:
                currentcopy = copy.deepcopy(current)
                if currentcopy.move_tile(name, a):
                    if currentcopy not in visited:
                        visited.add(currentcopy)
                        q.append(currentcopy)
                        path[currentcopy] = current
                        sys.stdout.write("%s-%s " % (name,
                                                     Tile.Move.to_str(a)))
                        sys.stdout.flush()
            sys.stdout.write("\n")
        return None
