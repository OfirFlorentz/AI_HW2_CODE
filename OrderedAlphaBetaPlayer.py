from time import time as _time
import copy
from AlphaBetaPlayer import AlphaBetaPlayer


class OrderedAlphaBetaPlayer(AlphaBetaPlayer):
    def __init__(self):
        super().__init__()
        self.score_dict = {}
        for d in self.directions:
            self.score_dict[d] = 0

    def make_move(self, time):  # time parameter is not used, we assume we have enough time.
        depth = 1
        ID_start_time = _time()
        while (True):
            copy_self = copy.deepcopy(self)
            assert self.count_players(self.board) == (1,1)
            try:
                best_move, best_move_score, best_new_loc, self.score_dict = copy_self.rb_minmax(depth, time - _time() + ID_start_time - 0.05,
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

    def rb_minmax(self, depth, time_left, board, my_turn=True, alpha=-3, beta=3, isRoot=True):
        start = _time()
        assert self.count_players(board) == (1,1)
        
        is_final, score = self.is_final(my_turn)
        if is_final:  # no move left
            return None, score, None, None
        
        if depth == 0:
            score=self.state_score(my_turn, board)
            return None, score, None, None

        if my_turn == 1:
            best_move, max_score, best_new_loc = None, -2, None
            prev_loc = self.loc
            board[prev_loc] = -1
            
            arr = self.directions
            if isRoot:
                arr = sorted(self.directions, key = lambda d: self.score_dict[d], reverse = True)
            score_dict = {}
            for d in arr:
                score_dict[d] = 0
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
                    _, score, _, _ = self.rb_minmax(depth-1,  time_left - _time() + start, board, 1-my_turn, alpha, beta, False)
                    score_dict[d] = score
                    self.available += 1
                    assert self.count_players(board) == (1,1)
                    board[new_loc] = 0
                    if score > max_score or max_score == -2:
                        best_move, max_score, best_new_loc = d, score, new_loc
                        # print(best_move, max_score, best_new_loc)
                    alpha = max([alpha, max_score])
                    if score>=beta:
                        max_score=1
                        break
                        
            self.loc = prev_loc
            board[self.loc] = 1
            return best_move, max_score, best_new_loc, score_dict


        else:
            best_move, min_score, best_new_loc = None, 2, None
            prev_loc = self.rival_position
            prev_loc = self.rival_position
            board[prev_loc] = -1
            #self.directions.sort(key = lambda d: self.score_dict[hash256(path+str(d[0])+str(d[1]))] if hash256(path+str(d[0])+str(d[1])) in self.score_dict else 0)
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
                    _, score, _, _ = self.rb_minmax(depth-1, time_left -_time() + start, board, 1-my_turn, alpha, beta, False)
                    self.available += 1
                    # print(score)
                    board[new_loc] = 0
                    if score < min_score or min_score == 2:
                        best_move, min_score, best_new_loc = d, score, new_loc
                    beta = min([beta, min_score])
                    if score<=alpha:
                        min_score=-1
                        break
            self.rival_position = prev_loc
            board[self.rival_position] = 2
            return best_move, min_score, best_new_loc, None
