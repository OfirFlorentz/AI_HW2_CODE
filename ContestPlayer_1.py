from time import time as _time
import copy


class MinimaxPlayer():
    def __init__(self):
        self.loc = None
        self.board = None
        self.directions = [(1, 0), (0, 1), (-1, 0), (0, -1)]
        self.starting_position = None
        self.rival_starting_position = None
        self.rival_position = None

    def set_game_params(self,board):
        self.board = board
        for i, row in enumerate(board):
            for j, val in enumerate(row):
                if val == 1:
                    self.loc = (i, j)
                    self.starting_position = (i,j)
                if val == 2:
                    self.rival_position = (i,j)
                    self.rival_starting_position = (i,j)
                if self.loc is not None and self.rival_position is not None:
                    break

    def set_rival_move(self, loc):
        self.board[loc] = 2
        self.board[self.rival_position] = -1
        self.rival_position = loc

    def count_ones(self, board):
        counter = 0
        for i, row in enumerate(board):
            for j, val in enumerate(row):
                if val == 1:
                    counter += 1
                if counter > 1:
                    print(5)
        return counter

    def make_move(self, time):  # time parameter is not used, we assume we have enough time.
        depth = 1
        ID_start_time = _time()
        while True:
            print(depth)
            copy_self = copy.deepcopy(self)
            assert self.count_ones(self.board) == 1
            try:
                best_move, best_move_score, best_new_loc = copy_self.rb_minmax(depth, time - _time() + ID_start_time - 0.05,
                                                                          copy.deepcopy(self.board))
            except TimeoutError:
                break
            assert self.count_ones(self.board) == 1
            depth += 1

        if best_move is None:
            # print(self.board)
            exit()

        self.board[best_new_loc] = 1
        self.board[self.loc] = -1
        self.loc = best_new_loc

        # print('returning move', best_move)
        return best_move

    def rb_minmax(self, depth, time_left, board, my_turn=True):
        start = _time()
        assert self.count_ones(board) == 1
        if depth == 0:
            return None, self.state_score(my_turn, board), None

        if my_turn == 1:
            best_move, max_score, best_new_loc = None, float('-inf'), None
            prev_loc = self.loc
            board[prev_loc] = -1
            for d in self.directions:
                if _time() - start > time_left:
                    raise TimeoutError()
                i = prev_loc[0] + d[0]
                j = prev_loc[1] + d[1]
                if 0 <= i < len(board) and 0 <= j < len(board[0]) and board[i][j] == 0:  # then move is legal
                    new_loc = (i, j)
                    # print('prev loc', prev_loc, 'new_loc:', new_loc, 'move:', (i, j))
                    assert board[new_loc] == 0
                    board[new_loc] = 1
                    self.loc = new_loc
                    _, score, _ = self.rb_minmax(depth-1,  time_left -_time() + start, board, 1-my_turn)
                    # assert -1<= score <= 1
                    board[new_loc] = 0
                    if score > max_score or max_score == float('-inf'):
                        best_move, max_score, best_new_loc = d, score, new_loc
                        # print(best_move, max_score, best_new_loc)
                    assert self.count_ones(board) == 0
            self.loc = prev_loc
            board[self.loc] = 1
            return best_move, max_score, best_new_loc


        else:
            best_move, min_score, best_new_loc = None, float('inf'), None
            prev_loc = self.rival_position
            board[prev_loc] = -1
            for d in self.directions:
                if _time() - start > time_left:
                    raise TimeoutError()
                i = prev_loc[0] + d[0]
                j = prev_loc[1] + d[1]
                if 0 <= i < len(board) and 0 <= j < len(board[0]) and board[i][j] == 0:  # then move is legal
                    new_loc = (i, j)
                    # print('prev loc', prev_loc, 'new_loc:', new_loc, 'move:', (i, j))
                    assert board[new_loc] == 0
                    self.rival_position = new_loc
                    board[new_loc] = 2
                    _, score, _ = self.rb_minmax(depth-1, time_left -_time() + start, board, 1-my_turn)
                    # print(score)
                    board[new_loc] = 0
                    if score < min_score or min_score == float('inf'):
                        best_move, min_score, best_new_loc = d, score, new_loc
            self.rival_position = prev_loc
            board[self.rival_position] = 2
            return best_move, min_score, best_new_loc

    def state_score(self, my_turn, board):
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

        # end of game
        if num_steps_available == num_steps_available_opp == 0:
            return 0
        if my_turn and num_steps_available == 0:
            return -1
        if not my_turn and num_steps_available_opp == 0:
            return 1

        distance_from_start = abs(self.starting_position[0] - self.loc[0]) + abs(self.starting_position[1] - self.loc[1])
        distance_from_start_opp = abs(self.rival_starting_position[0] - self.rival_position[0])\
                                  + abs(self.rival_starting_position[1] - self.rival_position[1])

        return (num_steps_available - num_steps_available_opp + distance_from_start - distance_from_start_opp) / (4 + 2*board.size)

    def bfs(self, loc, board, counter=0):
        for d in self.directions:
            i = loc[0] + d[0]
            j = loc[1] + d[1]
            if 0 <= i < len(board) and 0 <= j < len(board[0]) and board[i][j] == 0:  # then move is legal
                board[i][j] = -1
                counter += self.bfs((i,j), board)
        return counter