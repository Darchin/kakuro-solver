from partitioner import Partitioner
from operator import attrgetter
import sys
sys.setrecursionlimit(1000000)
INPUT_BOARD_MATRIX = []
class Utils:
    # DEFAULT DISPLAY SETTINGS
    COLORS = {'RED':'\033[91m','EMERALD':'\033[92m','YELLOW':'\033[93m','BLUE1':'\033[94m','PINK':'\033[95m','BLUE2':'\033[96m','WHITE':'\033[97m'}
    BLOCK_STYLE = '\u25A0'
    COLOR_LAST_ASSIGNMENT = COLORS['RED']
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
    def printBoard(board_display_matrix):
        for i in board_display_matrix:
            print('\t'.join(map(str, i)))
    def findPartitionOffset(perp_group, shared_tile):
        if perp_group.orientation == 'H':
            offset = shared_tile.col - perp_group.tiles[0].col
        else:
            offset = shared_tile.row - perp_group.tiles[0].row
        return offset
class Kakuro:
    VARIABLE_COUNT = 0
    class Tile:
        def __init__(self, row, col, val = 0):
            self.row = row
            self.col = col
            self.val = val
        def __str__(self):
            return f'[{self.row},{self.col}]'
        def __repr__(self):
            return self.__str__()
    class Group:
        def __init__(self, rule, tiles, identifier, orientation):
            self.unassigned_tile_count = len(tiles)
            self.id = identifier
            self.orientation = orientation
            self.rule = rule
            self.rule_remainder = rule
            self.tiles = tiles.copy()
            self.partitions = []
            self.partition_mask = []
            self.ratio = 0
        def calculateRatio(self, assigned = False):
            # Do not recalculate ratio for current assignments
            if assigned:
                return
            updated_rule = self.rule
            updated_tile_count = self.unassigned_tile_count
            for tile in self.tiles:
                if tile.val != 0:
                    updated_rule -= tile.val
                    updated_tile_count -= 1
            self.rule_remainder = updated_rule
            self.unassigned_tile_count = updated_tile_count
            rule_over_tile_count = self.rule_remainder/self.unassigned_tile_count
            self.ratio = min((9-rule_over_tile_count), rule_over_tile_count-1)
        def generatePartitions(self):
            self.partitions = Partitioner.getOrderedPartitions(self.rule, len(self.tiles))
            self.partition_mask = Partitioner.generatePartitionMask(self.partitions)
        def generateRestrictedPartitions(self, partition_offset, shared_digit):
            partitions = Partitioner.getOrderedPartitions( (self.rule-shared_digit), len(self.tiles)-1)
            for p in partitions:
                p.insert(partition_offset, shared_digit)
            self.partitions = partitions
            self.partition_mask = Partitioner.generatePartitionMask(partitions)
        def __str__(self):
            string = f'Group ID: {self.id}-{self.orientation}\nRule = {self.rule}\nTiles = {self.tiles}\n'
            if self.ratio != 0: string += f'Ratio = {self.ratio}\n'
            return string
        def __repr__(self):
            return self.__str__()
    def __init__(self, groups, tile_map):
        self.groups = groups
        self.tile_map = tile_map
        Kakuro.VARIABLE_COUNT += sum([len(g.tiles) for g in groups[0]])
    def createBoardFromString(board_size, board_str): 
        board_display_matrix = [[Utils.BLOCK_STYLE]*board_size for _ in range(board_size)]
        h_groups_string, v_groups_string = board_str.split(sep=';')
        tile_map = {}

        # Create horizontal groups
        h_group_list = h_groups_string.split(sep=',')
        h_groups = []
        for h_group_condensed in h_group_list:
            h = [int(x) for x in h_group_condensed.split(sep=' ')]
            board_display_matrix[h[0]][h[1]-1] = Utils.COLOR_SEP + '/' + Utils.COLOR_H + str(h[3]) + Utils.END_COLOR
            h_tiles = []
            h_rule = h[3]
            group_num = len(h_groups)
            for i in range(h[1],h[2]+1):
                board_display_matrix[h[0]][i] = Utils.EMPTY_TILE
                h_tiles.append(Kakuro.Tile(h[0],i))
                tile_map[h[0],i] = [group_num]
            h_groups.append(Kakuro.Group(h_rule, h_tiles, group_num, 'H'))

        # Create vertical groups
        v_group_list = v_groups_string.split(sep=',')
        v_groups = []
        for v_group_condensed in v_group_list:
            v = [int(x) for x in v_group_condensed.split(sep=' ')]
            if board_display_matrix[v[1]-1][v[0]] == Utils.BLOCK_STYLE:
                board_display_matrix[v[1]-1][v[0]] = Utils.COLOR_V + str(v[3]) + Utils.COLOR_SEP + '/' + Utils.END_COLOR
            else:
                board_display_matrix[v[1]-1][v[0]] = Utils.COLOR_V + str(v[3]) + board_display_matrix[v[1]-1][v[0]]
            v_tiles = []
            v_rule = v[3]
            group_num = len(v_groups)
            for i in range(v[1],v[2]+1):
                v_tiles.append(Kakuro.Tile(i,v[0]))
                board_display_matrix[i][v[0]] = Utils.EMPTY_TILE
                tile_map[i,v[0]] = tile_map[i,v[0]] + [group_num]
            v_groups.append(Kakuro.Group(v_rule, v_tiles, group_num, 'V'))
            groups = [h_groups]
            groups.append(v_groups)
        return Kakuro(groups, tile_map), board_display_matrix
    def calculateRatios(self, assignments = {}):
        for g_list in self.groups:
            for g in g_list:
                if f'{g.orientation}{g.id}' in assignments:
                    g.calculateRatio(True)
                else: g.calculateRatio()
    def selectMostContrainedGroup(self, group_assignments) -> Group:
        unassigned_groups = self.groups.copy()
        for G in unassigned_groups: # iterating over horizontal and vertical groups
            for g in G:
                if g in group_assignments:
                    unassigned_groups.remove(g)
        min_h_group = min(unassigned_groups[0], key=attrgetter('ratio'))
        min_v_group = min(unassigned_groups[1], key=attrgetter('ratio'))
        return min(min_h_group,min_v_group, key=attrgetter('ratio'))
    def findGroup(self, group_pair) -> Group:
        group_id = int(group_pair[1:])
        if group_pair[0] == 'H':
            index = 0
        else:
            index = 1
        return self.groups[index][group_id]
    def updateBoard(self, assignments, group_key):
        updated_board = INPUT_BOARD_MATRIX.copy()
        for var, val in assignments.items(): # 'var' is a group {orientation}{id} pair - like H2
            i = 0
            assigned_group = self.findGroup(var)
            for num in val: # 'val' is a partition
                row = assigned_group.tiles[i].row
                col = assigned_group.tiles[i].col
                updated_board[row][col] = str(num)
                i += 1

        last_assigned_group = self.findGroup(group_key)
        i = 0
        for num in assignments[group_key]:
            row = last_assigned_group.tiles[i].row
            col = last_assigned_group.tiles[i].col
            updated_board[row][col] = Utils.COLOR_LAST_ASSIGNMENT + str(num) + Utils.END_COLOR
            i += 1
        return updated_board
    def checkAssignment(assignments) -> bool:
        if len(assignments) == Kakuro.VARIABLE_COUNT:
            return True
        else:
            return False
    def solve(self, assignments = {}, group_assignments = {}):
        if Kakuro.checkAssignment(assignments):
            return assignments

        # Choose a variable (group in this case) according to ratios
        self.calculateRatios(assignments)
        group = self.selectMostContrainedGroup(group_assignments)
        # group_key = f'{group.orientation}{group.id}'
        
        # Generate chosen group's partitions
        group.generatePartitions()

        # Find colliding groups
        perp_groups = []
        offsets = []
        for tile in group.tiles:
            # Perp is short for 'perpendicular' - Basically we find vertical groups sharing a tile with a horizontal group and vice-versa
            perp_group = self.getPerpendicularGroup(group, tile)
            perp_groups.append(perp_group)
            partition_offset = Utils.findPartitionOffset(perp_group, tile)
            offsets.append(partition_offset)

        # Iterate over each partition, adding it to assignments and generating the restricted partition list for the affected groups;
        # Then check whether if a group's partition list becomes empty. If so, remove assignment.
        for p in group.partitions:
            next_board = Kakuro(self.groups, self.tile_map)
            next_board.getCorrespondingGroup(group).partitions = [p]
            inconsistent_partition = False
            assignments[group_key] = p.copy()
            # Utils.printBoard(next_board.updateBoard(assignments, group_key))

            for i in range(len(perp_groups)):
                shared_digit = p[i]
                perp_groups[i].generateRestrictedPartitions(partition_offset, shared_digit)
                if len(perp_groups[i].partitions) == 0:
                    inconsistent_partition = True
                    break
            if inconsistent_partition:
                del assignments[group_key]
                continue
            # If this point is reached, the current partition has been consistent, therefore we call solve again and move onto deeper assignment
            if len(assignments) != L:
                return result
            result = next_board.solve(assignments)
            return result
    def getPerpendicularGroup(self, original_group, shared_tile):
        group_pair = self.tile_map[shared_tile.row, shared_tile.col]
        if original_group.orientation == 'H':
            index = 1
        else: 
            index = 0
        return self.groups[index][group_pair[index]]
    
    def printGroups(self):
        h_groups = self.groups[0]
        v_groups = self.groups[1]
        print("HORIZONTAL GROUPS:\n")
        for i in range(len(h_groups)):
            print(f'{h_groups[i]}\n')
        print("-------------\n\n")
        print("VERTICAL GROUPS:\n")
        for i in range(len(v_groups)):
            print(f'{v_groups[i]}\n')
def main():
    N = 8
    easy_kakuro_1 = "1 2 4 19,1 6 7 10,2 1 7 39,3 1 2 15,3 4 5 10,4 2 3 16,4 5 6 4,5 3 4 9,5 6 7 12,6 1 7 35,7 1 2 16,7 4 6 7;"+\
    "1 2 3 16,1 6 7 14,2 1 4 30,2 6 7 16,3 1 2 4,3 4 6 23,4 1 3 24,4 5 7 6,5 2 4 9,5 6 7 4,6 1 2 4,6 4 7 10,7 1 2 16,7 5 6 16"
    game_board, board_display_matrix = Kakuro.createBoardFromString(N, easy_kakuro_1)
    print(game_board.VARIABLE_COUNT)
    # global INPUT_BOARD_MATRIX
    # INPUT_BOARD_MATRIX = board_display_matrix
    # print(game_board.selectGroup())
    # Utils.printBoard(board_display_matrix)
    # game_board.printGroups()
    # game_board.solve()

if __name__ == '__main__':
    main()