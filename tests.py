from board import Tile, Board

if __name__ == "__main__":
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
    tiles = [t[0] for t in setup]
    locations = [t[1] for t in setup]
    board = Board(tiles, locations, 4, 5)
    board.print_ascii()
