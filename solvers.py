from board import Board


class Solver:

    def __init__(self, board):
        self._board = board

    def set_goal(self, target_tile_name, target_location):
        """Sets a goal of moving target tile to target location"""
        self._goal = (target_tile_name, target_location)

    def set_board(self, board):
        self._board = board

    @classmethod
    def solve(self):
        raise NotImplemented

    
