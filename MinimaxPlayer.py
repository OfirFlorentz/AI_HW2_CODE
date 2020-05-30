from time import time as _time


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
        return counter

    def make_move(self, time):  # time parameter is not used, we assume we have enough time.
        ID_start_time = _time()
        depth = 0
        while (depth < 18):
            assert self.count_ones(self.board) == 1
            best_move, best_move_score, best_new_loc = self.rb_minmax(depth)
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


    def rb_minmax(self, depth, my_turn=True):
        assert self.count_ones(self.board) == 1
        if depth == 0:
            if my_turn == 1: # our turn
                return None, self.state_score(self.loc, my_turn), None
            else:
                return None, self.state_score(self.rival_position, my_turn), None

        if my_turn == 1:
            best_move, max_score, best_new_loc = None, float('-inf'), None
            prev_loc = self.loc
            self.board[prev_loc] = -1
            for d in self.directions:
                i = prev_loc[0] + d[0]
                j = prev_loc[1] + d[1]
                if 0 <= i < len(self.board) and 0 <= j < len(self.board[0]) and self.board[i][j] == 0:  # then move is legal
                    new_loc = (i, j)
                    # print('prev loc', prev_loc, 'new_loc:', new_loc, 'move:', (i, j))
                    assert self.board[new_loc] == 0
                    self.board[new_loc] = 1
                    self.loc = new_loc
                    _, score, _ = self.rb_minmax(depth-1, 1-my_turn)
                    # assert -1<= score <= 1
                    self.board[new_loc] = 0
                    if score > max_score or max_score == float('-inf'):
                        best_move, max_score, best_new_loc = d, score, new_loc
                        # print(best_move, max_score, best_new_loc)
                    assert self.count_ones(self.board) == 0
            self.loc = prev_loc
            self.board[self.loc] = 1
            return best_move, max_score, best_new_loc


        else:
            best_move, min_score, best_new_loc = None, float('inf'), None
            prev_loc = self.rival_position
            self.board[prev_loc] = -1
            for d in self.directions:
                i = prev_loc[0] + d[0]
                j = prev_loc[1] + d[1]
                if 0 <= i < len(self.board) and 0 <= j < len(self.board[0]) and self.board[i][j] == 0:  # then move is legal
                    new_loc = (i, j)
                    # print('prev loc', prev_loc, 'new_loc:', new_loc, 'move:', (i, j))
                    assert self.board[new_loc] == 0
                    self.rival_position = new_loc
                    self.board[new_loc] = 2
                    _,score,_ = self.rb_minmax(depth-1, 1-my_turn)
                    print(score)
                    self.board[new_loc] = 0
                    if score < min_score  or min_score == float('inf'):
                        best_move, min_score, best_new_loc = d, score, new_loc
            self.rival_position = prev_loc
            self.board[self.rival_position] = 2
            return best_move, min_score, best_new_loc

    def state_score(self, loc, turn):
        num_steps_available = 0
        for d in self.directions:
            i = loc[0] + d[0]
            j = loc[1] + d[1]
            if 0 <= i < len(self.board) and 0 <= j < len(self.board[0]) and self.board[i][j] == 0:  # then move is legal
                num_steps_available += 1

        # lossing, final position
        if num_steps_available == 0:
            if turn == 1:
                return -1
            return 1

        num_steps_available = 0
        for d in self.directions:
            i = loc[0] + d[0]
            j = loc[1] + d[1]
            if 0 <= i < len(self.board) and 0 <= j < len(self.board[0]) and self.board[i][j] == 0:  # then move is legal
                num_steps_available += 1


        if turn == 1:  # our turn
            distance_from_start = abs(self.starting_position[0] - loc[0]) + abs(self.starting_position[1] - loc[1])
            distance_from_rival = -1 * abs(self.rival_position[0] - loc[0]) + abs(self.rival_position[1] - loc[1])
            # state score is bounded between -1 to 1
            return (num_steps_available + distance_from_rival + distance_from_start) / (4 + 2*self.board.size)

        else: # rival turn
            distance_from_start = abs(self.rival_starting_position[0] - loc[0])\
                                  + abs(self.rival_starting_position[1] - loc[1])
            distance_from_rival = -1 * abs(self.loc[0] - loc[0]) + abs(self.loc[1] - loc[1])
            # state score is bounded between -1 to 1
            return -1*(num_steps_available + distance_from_rival + distance_from_start) / (4 + 2 * self.board.size)

