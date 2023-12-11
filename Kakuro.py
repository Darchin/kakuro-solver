from partitioner import Partitioner
from operator import attrgetter
import sample_kakuro_puzzles
import sys
import math
import time
import os
from copy import deepcopy

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
    def set_display_settings(block_style, block_thickness = 3, h_color = COLOR_H, v_color = COLOR_V, sep_color = COLOR_SEP):
        if block_style == 'highlight':
            BLOCK_STYLE = '\033[107m'+ ' '*block_thickness +'\033[0m'
        elif block_style == 'filled-square':
            BLOCK_STYLE = '\u25A0'
        COLOR_H = Utils.COLORS[h_color]
        COLOR_V = Utils.COLORS[v_color]
        COLOR_SEP = Utils.COLORS[sep_color]
    def updateBoard(assignments, new_assignment = {}, highlight_latest_assignment = True):
        updated_board = deepcopy(Kakuro.STARTING_BOARD)
        for tile, val in assignments.items():
            row = tile.row
            col = tile.col
            updated_board[row][col] = str(val)
        if highlight_latest_assignment:
            for tile, val in new_assignment.items():
                row = tile.row
                col = tile.col
                updated_board[row][col] = Utils.COLOR_LAST_ASSIGNMENT + str(val) + Utils.END_COLOR
        return updated_board
    def printBoard(board_display_matrix):
        for i in board_display_matrix:
            print('\t'.join(map(str, i)))
class Kakuro:
    VARIABLE_COUNT = 0
    STARTING_BOARD = []
    class Tile:
        def __init__(self, row, col):
            self.row = row
            self.col = col
            self.hgroup = None
            self.vgroup = None
        def __str__(self):
            return f'[{self.row},{self.col}]'
        def __repr__(self):
            return self.__str__()
        def getTile(row, col, tile_list):
            for tile in tile_list:
                if (row == tile.row) and (col == tile.col):
                    return tile
    class Group:
        def __init__(self, rule, tiles):
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
            
            for p in partitions.copy():
                if len(set(p)|used_digits) < len(p)+len(used_digits):
                    partitions.remove(p)

            if reduced_rule == 0 and reduced_tile_count == 0:
                single_val_domain = [assignments[tile] for tile in self.tiles]
                partitions = [single_val_domain]
            return partitions, unassigned_tiles
        def __str__(self):
            string = f'Group ID: {self.id}-{self.orientation}\nRule = {self.rule}\nTiles = {self.tiles}\n'
            if self.ratio != 0: string += f'Ratio = {self.ratio}\n'
            return string
        def __repr__(self):
            return self.__str__()
    def __init__(self, groups):
        self.groups = groups
        Kakuro.VARIABLE_COUNT += sum([len(g.tiles) for g in groups[0]])
    def createBoardFromString(board_size, board_str): 
        board_display_matrix = [[Utils.BLOCK_STYLE]*board_size for _ in range(board_size)]
        h_groups_string, v_groups_string = board_str.split(sep=';')
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
            h_groups.append(Kakuro.Group(h_rule, h_tiles))
            for tile in h_tiles:
                tile.hgroup = h_groups[-1]
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
            v_groups.append(Kakuro.Group(v_rule, v_tiles))
            for tile in v_tiles:
               tile.vgroup = v_groups[-1]
            groups = [h_groups]
            groups.append(v_groups)
        return Kakuro(groups), board_display_matrix
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
    def checkAssignmentCompleteness(assignments) -> bool:
        if len(assignments) == Kakuro.VARIABLE_COUNT:
            return True
        else:
            return False
    def checkCurrentConsistency(self, assignments, last_assignment):
        for tile, val in last_assignment.items():
            related_groups = [tile.hgroup] + [tile.vgroup]
            for group in related_groups:
                for group_tile in group.tiles:
                    if group_tile in assignments:
                        if assignments[group_tile] == val:
                            return False
        return True
    def solve(self, assignments = {}):
        # Check if assignment is complete
        if Kakuro.checkAssignmentCompleteness(assignments):
            return assignments
        
        # Choose variables (or a group in simple terms) according to group ratios
        selected_group = self.selectMostContrainedGroup(self.calculateRatios(assignments))
        # selected_group = self.groups[0][iter]
        # Generate chosen group's partitions
        domain, to_be_assigned_tiles = selected_group.generateDomain(assignments)

        # Iterate over each partition, adding it to assignments and generating the restricted partition list for the affected groups;
        # Then check whether a group's partition list becomes empty. If so, remove assignment.
        for partition in domain:
            new_assignment = {}
            j = 0
            for tile in to_be_assigned_tiles:
                new_assignment[tile] = partition[j]
                j += 1

            # time.sleep(1)
            # Utils.printBoard(Utils.updateBoard(assignments, new_assignment))
            # print(f'Previous assignments -> {assignments}')
            # print(f'New assignment -> {new_assignment}')
            # print("--------------------------------------------------------")
            if not self.checkCurrentConsistency(assignments, new_assignment):
                continue
            assignments.update(new_assignment)
            result = self.solve(assignments)
            if result != -1:
                return result

            for key in new_assignment:
                assignments.pop(key)
        return -1

def main():
    try:
        selected_puzzle = sample_kakuro_puzzles.puzzles[sys.argv[1], int(sys.argv[2])]
    except:
        print("Puzzle not found.")
        return

    game_board, board_display_matrix = Kakuro.createBoardFromString(selected_puzzle[0], selected_puzzle[1])
    Kakuro.STARTING_BOARD = board_display_matrix

    print("\nPuzzle to solve:")
    Utils.printBoard(board_display_matrix)
    print("\n\nSolving...\n")
    start_time = time.time()
    final_assignments = game_board.solve()
    end_time = time.time()
    
    if final_assignments == -1:
        print("No solution found.")
        return
    else:
        print("A solution was found.")
        print(f'Time to solve: {int((end_time - start_time)*1000.0)} ms\n')
    Utils.printBoard(Utils.updateBoard(final_assignments))

if __name__ == '__main__':
    main()