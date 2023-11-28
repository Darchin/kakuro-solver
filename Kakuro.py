import numpy as np

class Kakuro:
    class Tile:
        def __init__(self, row, col):
            self.row = row
            self.col = col
        def __str__(self):
            return f'[{self.row},{self.col}]'
        def __repr__(self):
            return self.__str__()
    class Group:
        def __init__(self, rule, tiles):
            self.rule = rule
            self.tiles = tiles.copy()
        def __str__(self):
            return f'Rule = {self.rule}\nTiles = {self.tiles}'
        def __repr__(self):
            return self.__str__()
    def __init__(self, h_groups, v_groups, board_size):
        self.board = np.zeros(shape=(board_size,board_size), dtype=int)
        self.h_groups = h_groups
        self.v_groups = v_groups
    def createBoardString(board_size, board_str):
        h_str, v_str = board_str.split(sep=';')
        # Create horizontal groups
        h_list = h_str.split(sep=',')
        h_groups = []
        for h_condensed in h_list:
            h = [int(x) for x in h_condensed.split(sep=' ')]
            h_tiles = []
            h_rule = h[3]
            for i in range(h[1],h[2]+1):
                h_tiles.append(Kakuro.Tile(h[0],i))
            h_groups.append(Kakuro.Group(h_rule, h_tiles))

        # Create vertical groups
        v_list = v_str.split(sep=',')
        v_groups = []
        for v_condensed in v_list:
            v = [int(x) for x in v_condensed.split(sep=' ')]
            v_tiles = []
            v_rule = v[3]
            for i in range(v[1],v[2]+1):
                v_tiles.append(Kakuro.Tile(i,v[0]))
            v_groups.append(Kakuro.Group(v_rule, v_tiles))
        
        return Kakuro(h_groups, v_groups, board_size)
    def setTile(self, tile, value):
        self.board[tile.row, tile.col] = value
    def printGroups(self):
        print("HORIZONTAL GROUPS:")
        for i in range(len(self.h_groups)):
            print(f'Horizontal group {i}:')
            print(f'{self.h_groups[i]}\n')
        print("-------------\n")
        print("VERTICAL GROUPS:")
        for i in range(len(self.v_groups)):
            print(f'Vertical group {i}:')
            print(f'{self.h_groups[i]}\n')
def main():
    N = 10
    inputBoard = "1 1 2 10,1 3 4 20;3 5 6 11"
    game_board = Kakuro.createBoardString(N, inputBoard)
    game_board.printGroups()

main()