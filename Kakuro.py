import partitioner
import numpy as np
class Utils:
    # DEFAULT DISPLAY SETTINGS
    COLORS = {'RED':'\033[91m','EMERALD':'\033[92m','YELLOW':'\033[93m','BLUE1':'\033[94m','PINK':'\033[95m','BLUE2':'\033[96m','WHITE':'\033[97m'}
    BLOCK_STYLE = '\u25A0'
    COLOR_H = COLORS['YELLOW']
    COLOR_V = COLORS['BLUE2']
    COLOR_SEP = COLORS['WHITE']
    END_COLOR = '\033[0m'
    EMPTY_TILE = '\u002D'
    def set_display_settings(block_style, block_thickness, h_color, v_color, sep_color):
        if block_style == 'highlight':
            BLOCK_STYLE = '\033[107m'+ ' '*block_thickness +'\033[0m'
        elif block_style == 'filled-square':
            BLOCK_STYLE = '\u25A0'
        COLOR_H = Utils.COLORS[h_color]
        COLOR_V = Utils.COLORS[v_color]
        COLOR_SEP = Utils.COLORS[sep_color]
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
    def __init__(self, h_groups, v_groups, board_display, board_size):
        self.board_display = board_display
        self.board = [[0]*board_size for _ in range(board_size)]
        self.h_groups = h_groups
        self.v_groups = v_groups
    def createBoardFromString(board_size, board_str): 
        board_display = [[Utils.BLOCK_STYLE]*board_size for _ in range(board_size)]
        h_str, v_str = board_str.split(sep=';')

        # Create horizontal groups
        h_list = h_str.split(sep=',')
        h_groups = []
        for h_condensed in h_list:
            h = [int(x) for x in h_condensed.split(sep=' ')]
            board_display[h[0]][h[1]-1] = Utils.COLOR_SEP + '/' + Utils.COLOR_H + str(h[3]) + Utils.END_COLOR
            h_tiles = []
            h_rule = h[3]
            for i in range(h[1],h[2]+1):
                board_display[h[0]][i] = Utils.EMPTY_TILE
                h_tiles.append(Kakuro.Tile(h[0],i))
            h_groups.append(Kakuro.Group(h_rule, h_tiles))
        # Create vertical groups
        v_list = v_str.split(sep=',')
        v_groups = []
        for v_condensed in v_list:
            v = [int(x) for x in v_condensed.split(sep=' ')]
            if board_display[v[1]-1][v[0]] == Utils.BLOCK_STYLE:
                board_display[v[1]-1][v[0]] = Utils.COLOR_V + str(v[3]) + Utils.COLOR_SEP + '/' + Utils.END_COLOR
            else:
                board_display[v[1]-1][v[0]] = Utils.COLOR_V + str(v[3]) + board_display[v[1]-1][v[0]]
            v_tiles = []
            v_rule = v[3]
            for i in range(v[1],v[2]+1):
                v_tiles.append(Kakuro.Tile(i,v[0]))
                board_display[i][v[0]] = Utils.EMPTY_TILE
            v_groups.append(Kakuro.Group(v_rule, v_tiles))
        return Kakuro(h_groups, v_groups, board_display, board_size)
    
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
    def printBoard(self):
        for i in self.board_display:
            print('\t'.join(map(str, i)))
def main():
    N = 8
    easy_kakuro_1 = "1 2 4 19,1 6 7 10,2 1 7 39,3 1 2 15,3 4 5 10,4 2 3 16,4 5 6 4,5 3 4 9,5 6 7 12,6 1 7 35,7 1 2 16,7 4 6 7;"+\
    "1 2 3 16,1 6 7 14,2 1 4 30,2 6 7 16,3 1 2 4,3 4 6 23,4 1 3 24,4 5 7 6,5 2 4 9,5 6 7 4,6 1 2 4,6 4 7 10,7 1 2 16,7 5 6 16"
    game_board = Kakuro.createBoardFromString(N, easy_kakuro_1)
    game_board.printBoard()

main()