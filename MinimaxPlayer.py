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
        self.available = 0

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
                if val == 0:
                    self.available += 1

    def set_rival_move(self, loc):
        self.board[loc] = 2
        self.board[self.rival_position] = -1
        self.rival_position = loc

    def count_players(self, board):
        counter1 = 0
        counter2 = 0
        for i, row in enumerate(board):
            for j, val in enumerate(row):
                if val == 1:
                    counter1 += 1
                if val ==2:
                    counter2 +=1
        if counter1 !=1 or counter2 != 1:
            print(5)
        return (counter1, counter2)

    def make_move(self, time):  # time parameter is not used, we assume we have enough time.
        depth = 1
        ID_start_time = _time()
        while (True):
            copy_self = copy.deepcopy(self)
            assert self.count_players(self.board) == (1,1)
            try:
                best_move, best_move_score, best_new_loc = copy_self.rb_minmax(depth, time - _time() + ID_start_time - 0.05,
                                                                          copy.deepcopy(self.board))
            except TimeoutError:
                break
            assert self.count_players(self.board) == (1, 1)
            depth += 1

        if best_move is None:
            # print(self.board)
            exit()

        self.board[best_new_loc] = 1
        self.board[self.loc] = -1
        self.loc = best_new_loc
        self.available -= 2

        # print('returning move', best_move)
        return best_move

    def rb_minmax(self, depth, time_left, board, my_turn=True):
        start = _time()
        assert self.count_players(board) == (1,1)
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
                    self.available -= 1
                    _, score, _ = self.rb_minmax(depth=depth-1,  time_left=time_left - _time() + start, board= board, my_turn=1-my_turn)
                    self.available += 1
                    assert self.count_players(board) == (1,1)
                    board[new_loc] = 0
                    if score > max_score or max_score == float('-inf'):
                        best_move, max_score, best_new_loc = d, score, new_loc
                        # print(best_move, max_score, best_new_loc)
            self.loc = prev_loc
            board[self.loc] = 1
            return best_move, max_score, best_new_loc


        else:
            best_move, min_score, best_new_loc = None, float('inf'), None
            prev_loc = self.rival_position
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
                    self.available -= 1
                    _, score, _ = self.rb_minmax(depth-1, time_left -_time() + start, board, 1-my_turn)
                    self.available += 1
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

        # get params
        distance_from_start = abs(self.starting_position[0] - self.loc[0]) + abs(self.starting_position[1] - self.loc[1])
        distance_from_start_opp = abs(self.rival_starting_position[0] - self.rival_position[0])\
                                  + abs(self.rival_starting_position[1] - self.rival_position[1])
        available_steps, found_opp = self.dfs(self.loc, copy.deepcopy(board))
        available_steps_opp, _ = self.dfs(self.rival_position, copy.deepcopy(board))

        # cant block each other, the one who have more steps win
        if not found_opp:
            if available_steps > available_steps_opp + int(my_turn):
                return 0.999
            elif available_steps + int(not my_turn) < available_steps_opp :
                return -0.999
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
