from partitioner import Partitioner
from operator import attrgetter
import sys
import math
import time
import os
from copy import deepcopy
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
    def findTileIndex(perp_group, shared_tile) -> int:
        if perp_group.orientation == 'H':
            index = shared_tile.col - perp_group.tiles[0].col
        else:
            index = shared_tile.row - perp_group.tiles[0].row
        return index
class Kakuro:
    VARIABLE_COUNT = 0
    class Tile:
        def __init__(self, row, col):
            self.row = row
            self.col = col
        def __str__(self):
            return f'[{self.row},{self.col}]'
        def __repr__(self):
            return self.__str__()
        def getTile(row, col, tile_list):
            for tile in tile_list:
                if (row == tile.row) and (col == tile.col):
                    return tile
    class Group:
        def __init__(self, rule, tiles, identifier, orientation):
            self.id = identifier
            self.orientation = orientation
            self.rule = rule
            self.tiles = tiles
            self.ratio = 0
        def calculateRatio(self, assignments):
            updated_rule = self.rule
            updated_tile_count = len(self.tiles)
            for tile in self.tiles:
                if tile in assignments:
                    updated_rule -= assignments[tile]
                    updated_tile_count -= 1
            if updated_tile_count == 0:
                self.ratio = 999
            else:
                rule_over_tile_count = updated_rule/updated_tile_count
                self.ratio = math.factorial(updated_tile_count) * min((9-rule_over_tile_count), rule_over_tile_count-1)
                return self
            tile_count = len(self.tiles)
            rule_remainder = self.rule
            idx_val_pair = []
            for tile in self.tiles:
                if tile in assignments:
                    rule_remainder -= assignments[tile]
                    tile_count -= 1
                    idx_val_pair.append((Utils.findTileIndex(self, tile),assignments[tile]))            
            # print(idx_tile_pairs)            
            partitions = Partitioner.getOrderedPartitions(rule_remainder, tile_count)
            for p in partitions:
                i = 0
                for idx_val in idx_val_pair:
                    p.insert(idx_val[0], idx_val[1])
                    i += 1
            partitions = Partitioner.remove_duplicates(partitions)
            self.partitions = partitions
        def generateDomain(self, assignments):
            reduced_tile_count = len(self.tiles)
            reduced_rule = self.rule
            unassigned_tiles = []
            used_digits = set()
            for tile in self.tiles:
                if tile in assignments:
                    reduced_tile_count -= 1
                    digit = assignments[tile]
                    reduced_rule -= digit
                    used_digits.add(digit)
                else: unassigned_tiles.append(tile)
            partitions = Partitioner.getOrderedPartitions(reduced_rule, reduced_tile_count)
            for p in partitions:
                if len(set(p)|used_digits) < len(p)+len(used_digits):
                    partitions.remove(p)
            return partitions, unassigned_tiles
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
        all_tiles = []

        # Create horizontal groups
        h_group_list = h_groups_string.split(sep=',')
        h_groups = []
        for h_group_condensed in h_group_list:
            h = [int(x) for x in h_group_condensed.split(sep=' ')]
            board_display_matrix[h[0]][h[1]-1] = Utils.COLOR_SEP + '/' + Utils.COLOR_H + str(h[3]) + Utils.END_COLOR
            h_tiles = []
            h_rule = h[3]
            for i in range(h[1],h[2]+1):
                board_display_matrix[h[0]][i] = Utils.EMPTY_TILE
                h_tiles.append(Kakuro.Tile(h[0],i))
            h_groups.append(Kakuro.Group(h_rule, h_tiles, len(h_groups), 'H'))
            for h in h_tiles:
                tile_map[h] = [h_groups[-1]]
            all_tiles = all_tiles + h_tiles

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
            for i in range(v[1],v[2]+1):
                v_tiles.append(Kakuro.Tile.getTile(i, v[0], all_tiles))
                board_display_matrix[i][v[0]] = Utils.EMPTY_TILE
            v_groups.append(Kakuro.Group(v_rule, v_tiles, len(v_groups), 'V'))
            for v in v_tiles:
                tile_map[v] = tile_map[v] + [v_groups[-1]]
            groups = [h_groups]
            groups.append(v_groups)
        return Kakuro(groups, tile_map), board_display_matrix
    def calculateRatios(self, assignments):
        unassigned_groups = []
        for g_list in self.groups:
            for g in g_list:
                group = g.calculateRatio(assignments)
                if group is not None:
                    unassigned_groups.append(group)
        return unassigned_groups
    def selectMostContrainedGroup(self, unassigned_groups) -> Group:
        return min(unassigned_groups, key=attrgetter('ratio'))
    def updatedBoard(assignments, new_assignment):
        updated_board = deepcopy(INPUT_BOARD_MATRIX)
        for tile, val in assignments.items():
            row = tile.row
            col = tile.col
            updated_board[row][col] = str(val)
        for tile, val in new_assignment.items():
            row = tile.row
            col = tile.col
            updated_board[row][col] = Utils.COLOR_LAST_ASSIGNMENT + str(val) + Utils.END_COLOR
        return updated_board
    def checkAssignmentCompleteness(assignments) -> bool:
        if len(assignments) == Kakuro.VARIABLE_COUNT:
            return True
        else:
            return False
    def checkCurrentConsistency(self, assignments, last_assignment):
        for tile, val in last_assignment.items():
            related_groups = self.tile_map[tile]
            for group in related_groups:
                for group_tile in group.tiles:
                    if group_tile in assignments:
                        if assignments[group_tile] == val:
                            return False
        return True
    def checkForwardConsistency(self, perpendicular_groups, assignments, last_assignment):
        merged_assignments = assignments | last_assignment
        for g in perpendicular_groups:
            domain, unassigned_tiles = g.generateDomain(merged_assignments)
            if len(unassigned_tiles) == 0: return True
            if len(domain) == 0: return False
        return True
    def checkIfTilesShareGroup(self, tile1, tile2):
        t1_groups = self.tile_map[tile1]
        t2_groups = self.tile_map[tile2]
        if t1_groups[0] == t2_groups[0] or t1_groups[1] == t2_groups[1]:
            return True
        else:
            return False
    def findPerpendicularGroup(self, other_group, tile):
        if other_group.orientation == 'H':
            index = 1
        else: index = 0
        return self.tile_map[tile][index]
    def solve(self, assignments = {}):
        # Check if assignment is complete
        if Kakuro.checkAssignmentCompleteness(assignments):
            return assignments
        
        # Choose a variable (group in this case) according to ratios
        selected_group = self.selectMostContrainedGroup(self.calculateRatios(assignments))
        
        # Generate chosen group's partitions
        domain, to_be_assigned_tiles = selected_group.generateDomain(assignments)

        # Find colliding groups
        perpendicular_groups = [self.findPerpendicularGroup(selected_group, tile) for tile in to_be_assigned_tiles]

        # Iterate over each partition, adding it to assignments and generating the restricted partition list for the affected groups;
        # Then check whether a group's partition list becomes empty. If so, remove assignment.
        for partition in domain:
            new_assignment = {}
            j = 0
            for tile in to_be_assigned_tiles:
                new_assignment[tile] = partition[j]
                j += 1
            # time.sleep(0.4)
            # # os.system("cls")
            # Utils.printBoard(Kakuro.updatedBoard(assignments, new_assignment))
            # print(f'Previous assignments -> {assignments}')
            # print(f'New assignment -> {new_assignment}')
            # print("--------------------------------------------------------")
            if not self.checkCurrentConsistency(assignments, new_assignment)\
                or not self.checkForwardConsistency(perpendicular_groups, assignments, new_assignment):
                continue
            assignments.update(new_assignment)
            result = self.solve(assignments)
            if result != -1:
                return result

            for key in new_assignment:
                assignments.pop(key)
        return -1

def main():
    N = 8
    easy_kakuro_1 = "1 2 4 19,1 6 7 10,2 1 7 39,3 1 2 15,3 4 5 10,4 2 3 16,4 5 6 4,5 3 4 9,5 6 7 12,6 1 7 35,7 1 2 16,7 4 6 7;"+\
    "1 2 3 16,1 6 7 14,2 1 4 30,2 6 7 16,3 1 2 4,3 4 6 23,4 1 3 24,4 5 7 6,5 2 4 9,5 6 7 4,6 1 2 4,6 4 7 10,7 1 2 16,7 5 6 16"
    game_board, board_display_matrix = Kakuro.createBoardFromString(N, easy_kakuro_1)
    global INPUT_BOARD_MATRIX
    INPUT_BOARD_MATRIX = board_display_matrix
    # Utils.printBoard(board_display_matrix)
    # game_board.printGroups()
    result = game_board.solve()
    print(result)

if __name__ == '__main__':
    main()