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
        board_ids = set({self._board.board_id})
        q = deque()
        visited = set()
        path = {}
        q.append(self._board)
        while len(q) > 0:
            current = q.popleft()
            # Check if goal is reached
            if current.tile_loc(self._goal[0]) == self._goal[1]:
                # Return path: a list of boards
                trace = [current]
                while True:
                    b = current
                    if b in path:
                        trace.append(path[b])
                        b = path[b]
                    else:
                        break
                return trace
            # Explore all possible actions
            actions = current.generate_possible_moves()
            sys.stdout.write("Exploring board %d... " % current.board_id)
            for name, a in actions:
                currentcopy = copy.deepcopy(current)
                if currentcopy.move_tile(name, a):
                    new_id = random.randint(0, 1000000)
                    while new_id in board_ids:
                        new_id = random.randint(0, 1000000)
                    currentcopy.set_board_id(new_id)
                    path[currentcopy] = current
                    if currentcopy not in visited:
                        visited.add(currentcopy)
                        q.append(currentcopy)
                        sys.stdout.write("%s (%d)" % (Tile.Move.to_str(a),
                                                      currentcopy.board_id))
                        sys.stdout.flush()
            sys.stdout.write("\n")
        return None
