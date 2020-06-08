from time import time as _time
import copy
from OrderedAlphaBetaPlayer import OrderedAlphaBetaPlayer


class ContestPlayer(OrderedAlphaBetaPlayer):

    def state_score(self, my_turn, board):
        # get params
        distance_from_start = abs(self.starting_position[0] - self.loc[0]) + abs(self.starting_position[1] - self.loc[1])
        distance_from_start_opp = abs(self.rival_starting_position[0] - self.rival_position[0])\
                                  + abs(self.rival_starting_position[1] - self.rival_position[1])
        available_steps, found_opp = self.dfs(self.loc, copy.deepcopy(board))
        available_steps_opp, _ = self.dfs(self.rival_position, copy.deepcopy(board))

        # cant block each other, the one who have more steps win
        if not found_opp:
            if available_steps > available_steps_opp + int(my_turn):
                return 0.99 + (available_steps) / (self.board.size * self.board.size * 100)
            elif available_steps + int(not my_turn) < available_steps_opp:
                return -0.99 - (available_steps_opp) / (self.board.size * self.board.size * 100)
            return 0

        # norm
        distance_from_start = distance_from_start / (2*len(board))
        distance_from_start_opp = distance_from_start_opp / (2*len(board))

        available_steps = available_steps / (self.available + 0.001)
        available_steps_opp = available_steps_opp / (self.available + 0.001)

        return (available_steps - available_steps_opp + distance_from_start - distance_from_start_opp) / 2

    def dfs(self, loc, board, max_length=0, found_opp=False):
        for d in self.directions:
            i = loc[0] + d[0]
            j = loc[1] + d[1]
            if 0 <= i < len(board) and 0 <= j < len(board[0]):
                if board[i][j] == 0:  # then move is legal
                    board[i][j] = -1
                    length, found = self.dfs((i,j), board, found_opp)
                    max_length = max(max_length,1 + length)
                    found_opp = found_opp or found
                elif board[i][j] == 2:
                    found_opp = True
        return max_length, found_opp

    def steps_available(self, board):
        num_steps_available = 0
        num_steps_available_opp = 0
        for d in self.directions:
            i = self.loc[0] + d[0]
            j = self.loc[1] + d[1]
            if 0 <= i < len(board) and 0 <= j < len(board[0]) and board[i][j] == 0:  # then move is legal
                num_steps_available += 1

            i = self.rival_position[0] + d[0]
            j = self.rival_position[1] + d[1]
            if 0 <= i < len(board) and 0 <= j < len(board[0]) and board[i][j] == 0:  # then move is legal
                num_steps_available_opp += 1

        return num_steps_available, num_steps_available_opp

    def is_final(self, my_turn, board):
        steps, steps_opp = self.steps_available(board)
        # end of game
        if steps == steps_opp == 0:
            return True, 0
        if my_turn and steps == 0:
            return True, -1
        if not my_turn and steps_opp == 0:
            return True, 1
        return False, 0
