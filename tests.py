from board import Tile, Board
from pprint import pprint
from solvers import BFSSolver

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
    return setup, (4, 5), (1, 3)

def simple():
    setup = [
        (Tile("cao", 2, 2), [0, 0])
    ]
    return setup, (3, 3), (1, 1)

if __name__ == "__main__":
    setup, shape, goal = prob1()
    w, h = shape

    tiles = [t[0] for t in setup]
    locations = [t[1] for t in setup]
    board = Board(tiles, locations, w, h)
    board.print_ascii()
    pprint(board.generate_possible_moves())

    solver = BFSSolver(board)
    solver.set_goal("cao", goal)
    trace = solver.solve()
    print("==================")
    for i in range(len(trace)):
        print("-------")
        print("Step %d" % i)
        print("-------")
        if i < len(trace)-1:
            trace[i].print_ascii(legend=False)
        else:
            trace[i].print_ascii(legend=True)
