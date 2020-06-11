from time import time as _time
import copy
from OrderedAlphaBetaPlayer import OrderedAlphaBetaPlayer


DIR = [[(0,1), (1, 0), (0, -1), (-1, 0)], [(1, 0), (0, -1), (-1, 0), (0, 1)], [(0, -1), (-1, 0), (0, 1), (1, 0)],
[(-1, 0), (0, 1), (1, 0), (0, -1)]]


class ContestPlayer(OrderedAlphaBetaPlayer):
    def __init__(self):
        super().__init__()
        self.separate = False


    def make_move(self, time):  # time parameter is not used, we assume we have enough time.
        ID_start_time = _time()
        # separate from opp, act alone
        if self.separate == False:
            self.separate = self.check_separate(copy.deepcopy(self.board), [self.loc])
        print(self.separate)
        depth = 1
        while (True):
            copy_self = copy.deepcopy(self)
            assert self.count_players(self.board) == (1, 1)
            try:
                if self.separate:
                    best_move, best_move_score, best_new_loc = copy_self.move_separate(depth, time - _time() + ID_start_time - 0.05, copy.deepcopy(self.board))
                else:
                    best_move, best_move_score, best_new_loc, self.score_dict = copy_self.rb_minmax(depth, time - _time() + ID_start_time - 0.05,  copy.deepcopy(self.board))
            except TimeoutError:
                break
            assert self.count_players(self.board) == (1, 1)
            depth += 1
        print('depth:', depth)

        if best_move is None:
            # print(self.board)
            exit()

        print('score:', best_move_score)
        self.board[best_new_loc] = 1
        self.board[self.loc] = -1
        self.loc = best_new_loc
        self.available -= 2

        # print('returning move', best_move)
        return best_move

    def check_separate(self, board, loc_q):
        if loc_q == []:
            return True
        new_q = []
        for loc in loc_q:
            loc_q = loc_q[1:]
            for d in self.directions:
                i = loc[0] + d[0]
                j = loc[1] + d[1]
                if 0 <= i < len(board) and 0 <= j < len(board[0]):
                    if board[i][j] == 0:  # then move is legal
                        board[i][j] = -1
                        new_q.append((i, j))
                    if board[i][j] == 2:
                        return False
        return self.check_separate(board, new_q)



    def move_separate(self, depth, time_left, board):
        start = _time()
        if depth == 0:
            max_steps = 0
            for d in DIR:
                max_steps = max(max_steps, self.longest(self.loc, copy.deepcopy(board), d))
            return None, max_steps, None

        best_move, max_score, best_new_loc = None, 0, None
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
                _, score, _ = self.move_separate(depth=depth - 1, time_left=time_left - _time() + start, board=board)
                assert self.count_players(board) == (1, 1)
                score += 1 # one more step
                board[new_loc] = 0
                if score > max_score:
                    best_move, max_score, best_new_loc = d, score, new_loc
        self.loc = prev_loc
        board[self.loc] = 1
        assert self.count_players(self.board) == (1, 1)
        return best_move, max_score, best_new_loc

