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
        """Returns a list of board states, actions, and number of exploration steps
        TODO: it should be optinal to return board states."""
        raise NotImplemented


class BruteForceSolver(Solver):

    """Solves the problem with brute force (BFS or DFS)."""
    def __init__(self, board, method="DFS"):
        super(BruteForceSolver, self).__init__(board)
        self._method = method
    
    # TODO: This is computationally very expensive
    # due to all the copy calls, and "not in"
    def solve(self):
        q = deque()
        path = {}
        q.append(self._board)
        visited = set({self._board})
        step_count = 0
        while len(q) > 0:
            if self._method == "BFS":
                current = q.popleft()
            elif self._method == "DFS":
                current = q.pop()
            else:
                raise ValueError("Unknown method %s" % self._method)
            
            # Check if goal is reached
            if current.tile_loc(self._goal[0]) == self._goal[1]:
                # Return path: a list of boards
                trace = [current]
                actions = [None]
                b = current
                seen = set()
                while b not in seen:
                    seen.add(b)
                    if b in path:
                        b, name, a = path[b]
                        trace.append(b)
                        actions.append("%s-%s" % (name, Tile.Move.to_str(a)))
                    if b == trace[0]:
                        break
                return list(reversed(trace)), list(reversed(actions)), step_count
            # Explore all possible actions
            actions = current.generate_possible_moves()
            sys.stdout.write("(%d) Exploring board %s" % (step_count, current))
            step_count += 1
            for name, a in actions:
                currentcopy = copy.deepcopy(current)
                if currentcopy.move_tile(name, a):
                    if currentcopy not in visited:
                        visited.add(currentcopy)
                        q.append(currentcopy)
                        path[currentcopy] = (current, name, a)
                        sys.stdout.write("%s-%s " % (name,
                                                     Tile.Move.to_str(a)))
                        sys.stdout.flush()
            sys.stdout.write("\n")
        return None, None, step_count
