from time import time as _time
from MinimaxPlayer import MinimaxPlayer


class AlphaBetaPlayer(MinimaxPlayer):

    def rb_minmax(self, depth, time_left, board, my_turn=True, alpha=float('-inf'), beta=float('inf')):
        start = _time()
        is_final, score = self.is_final(my_turn, board)
        if is_final:  # no move left
            return None, score, None
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
                    board[new_loc] = 1
                    self.loc = new_loc
                    self.available -= 1
                    _, score, _ = self.rb_minmax(depth-1,  time_left - _time() + start, board, 1-my_turn, alpha, beta)
                    self.available += 1
                    board[new_loc] = 0
                    if score > max_score or max_score == float('-inf'):
                        best_move, max_score, best_new_loc = d, score, new_loc
                    alpha = max([alpha, max_score])
                    if score>=beta:
                        max_score=1
                        break
                        
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
                    self.rival_position = new_loc
                    board[new_loc] = 2
                    self.available -= 1
                    _, score, _ = self.rb_minmax(depth-1, time_left -_time() + start, board, 1-my_turn, alpha, beta)
                    self.available += 1
                    board[new_loc] = 0
                    if score < min_score or min_score == float('inf'):
                        best_move, min_score, best_new_loc = d, score, new_loc
                    beta = min([beta, min_score])
                    if score<=alpha:
                        min_score=-1
                        break
            self.rival_position = prev_loc
            board[self.rival_position] = 2
            return best_move, min_score, best_new_loc
