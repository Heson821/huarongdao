from board import Tile, Board
from pprint import pprint
from solvers import BruteForceSolver
import copy
import sys
import time

def prob1():
    setup = [
        (Tile("cao", 2, 2), [1, 0]),
        (Tile("guan", 2, 1), [1, 2]),  
        (Tile("zhang", 1, 2), [0, 0]), 
        (Tile("zhao", 1, 2), [0, 2]),  
        (Tile("ma", 1, 2), [3, 0]),    
        (Tile("huang", 1, 2), [3, 2]), 
        (Tile("zz1", 1, 1), [0, 4]),    
        (Tile("zz2", 1, 1), [1, 3]),    
        (Tile("zz3", 1, 1), [2, 3]),    
        (Tile("zz4", 1, 1), [3, 4])     
    ]
    return setup, (4, 5), (2,1) #(1, 3)

def simple():
    setup = [
        (Tile("cao", 2, 2), [0, 0]),
        (Tile("guan", 1, 1), [1, 2])
    ]
    return setup, (3, 3), (1, 1)

def test_equality(board):
    board2 = copy.deepcopy(board)
    print(board == board2)

if __name__ == "__main__":
    if len(sys.argv) <= 1:
        print("Usage: tests.py <method:BFS|DFS>")
        sys.exit(1)
    method = sys.argv[1]
    
    setup, shape, goal = prob1()
    w, h = shape

    tiles = [t[0] for t in setup]
    locations = [t[1] for t in setup]
    board = Board(tiles, locations, w, h)
    # test_equality(board)
    board.print_ascii()

    solver = BruteForceSolver(board, method=method)
    solver.set_goal("cao", goal)
    start_time = time.time()
    trace, actions, step_count = solver.solve()
    end_time = time.time()
    if trace is None:
        print("No solution found.")
        sys.exit(1)
    print("========== Solution ===========")
    for i in range(len(trace)):
        print("-------")
        print("Step %d" % i)
        print("-------")
        if i < len(trace)-1:
            trace[i].print_ascii(legend=False)
            print("[" + actions[i] + "]")
        else:
            trace[i].print_ascii(legend=True)
    print("Total exploration steps: %d" % step_count)
    print("Solution found in %.9fs" % (end_time - start_time))
