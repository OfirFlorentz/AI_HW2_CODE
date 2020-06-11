from time import time as _time
import copy
import numpy as np
import random

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

        return (counter1, counter2)

    def make_move(self, time):  # time parameter is not used, we assume we have enough time.
        depth = 1
        ID_start_time = _time()
        # time = float('inf')
        while(True):
            copy_self = copy.deepcopy(self)
            assert self.count_players(self.board) == (1,1)
            try:
                    best_move, best_move_score, best_new_loc = copy_self.rb_minmax(depth, time - _time() + ID_start_time - 0.05 ,
                                                                          copy.deepcopy(self.board))
            except TimeoutError:
                break
            assert self.count_players(self.board) == (1, 1)
            depth += 1
        print('new', depth)
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


            self.loc = prev_loc
            board[self.loc] = 1
            assert (max_score <= 1 and max_score >= -1)
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
                    assert board[new_loc] == 0
                    self.rival_position = new_loc
                    board[new_loc] = 2
                    self.available -= 1
                    _, score, _ = self.rb_minmax(depth-1, time_left -_time() + start, board, 1-my_turn)
                    self.available += 1
                    board[new_loc] = 0

                    if score < min_score or min_score == float('inf'):
                        best_move, min_score, best_new_loc = d, score, new_loc

            self.rival_position = prev_loc
            board[self.rival_position] = 2
            return best_move, min_score, best_new_loc

    def state_score(self, my_turn, board):
        zero_board_1 = np.zeros([len(self.board), len(self.board[0])])
        zero_board_2 = np.zeros([len(self.board), len(self.board[0])])

        # get params
        distance_from_start = abs(self.starting_position[0] - self.loc[0]) + abs(self.starting_position[1] - self.loc[1])
        distance_from_start_opp = abs(self.rival_starting_position[0] - self.rival_position[0])\
                                  + abs(self.rival_starting_position[1] - self.rival_position[1])
        available_steps, found_opp = self.bfs(copy.deepcopy(board), zero_board_1, [self.loc])
        available_steps_opp, _ = self.bfs(copy.deepcopy(board), zero_board_2, [self.rival_position])

        # cant block each other, the one who have more steps win
        if not found_opp:
            directions = copy.deepcopy(self.directions)
            random.shuffle(directions)
            max_steps = self.longest(self.loc, copy.deepcopy(board), directions)
            max_steps_opp = self.longest(self.rival_position, copy.deepcopy(board), directions)


            if (max_steps_opp/(max_steps_opp + 0.01)) < 2 and (max_steps_opp/(max_steps + 0.01))< 2:
                directions.reverse()
                max_steps_2 = self.longest(self.loc, copy.deepcopy(board), directions)
                max_steps_opp_2 = self.longest(self.rival_position, copy.deepcopy(board), directions)
                max_steps = max(max_steps, max_steps_2)
                max_steps_opp = max(max_steps_opp, max_steps_opp_2)

            return (max_steps - max_steps_opp) / self.available

        else:
        # norm
            closer = self.closer(zero_board_1, zero_board_2) / (self.available + 0.001)
            norm_distance = (distance_from_start - distance_from_start_opp) / (len(self.board) * len(self.board[0]))
            return (closer * 6 + norm_distance) / 7
    
    def lite_score(self, my_turn, board):
        found=[]
        num, new, new_temp = 0, [self.loc], []
        num_opp, new_opp, new_opp_temp = 0, [self.rival_position], []
        
        if my_turn:
        
            while len(new)>0 or len(new_opp)>0:
                for loc in new:
                    for d in self.directions:
                        i = loc[0] + d[0]
                        j = loc[1] + d[1]
                        if 0 <= i < len(board) and 0 <= j < len(board[0]) and board[i][j] == 0 and (i,j) not in found:  # then move is legal
                            num += 1
                            new_temp.append ((i,j))
                            found.append ((i,j))
                            
                for loc in new_opp:
                    for d in self.directions:
                        i = loc[0] + d[0]
                        j = loc[1] + d[1]
                        if 0 <= i < len(board) and 0 <= j < len(board[0]) and board[i][j] == 0 and (i,j) not in found:  # then move is legal
                            num_opp += 1
                            new_opp_temp.append ((i,j))
                            found.append ((i,j))
                
                new=new_temp
                new_temp=[]
                new_opp=new_opp_temp
                new_opp_temp=[]
            
            return num/(num+num_opp)
        
        else:
            
            while len(new)>0 or len(new_opp)>0:
                                           
                for loc in new_opp:
                    for d in self.directions:
                        i = loc[0] + d[0]
                        j = loc[1] + d[1]
                        if 0 <= i < len(board) and 0 <= j < len(board[0]) and board[i][j] == 0 and (i,j) not in found:  # then move is legal
                            num_opp += 1
                            new_opp_temp.append ((i,j))
                            found.append ((i,j))
                
                for loc in new:
                    for d in self.directions:
                        i = loc[0] + d[0]
                        j = loc[1] + d[1]
                        if 0 <= i < len(board) and 0 <= j < len(board[0]) and board[i][j] == 0 and (i,j) not in found:  # then move is legal
                            num += 1
                            new_temp.append ((i,j))
                            found.append ((i,j))
                
                new=new_temp
                new_temp=[]
                new_opp=new_opp_temp
                new_opp_temp=[]
            
            return num/(num+num_opp)

    def bfs(self, board, zero_board, loc_q,  counter=0, depth=1, found_opp=False):
        if loc_q == []:
            return counter, found_opp
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
                        counter += 1
                        if zero_board[i][j] == 0:
                            zero_board[i][j] = depth
                    elif board[i][j] == 2:
                        found_opp = True
        return self.bfs(board, zero_board, new_q,  counter=counter, depth=depth+1, found_opp=found_opp)

    def longest(self, loc, board, directions, max_length=0):
        for d in directions:
            i = loc[0] + d[0]
            j = loc[1] + d[1]
            if 0 <= i < len(board) and 0 <= j < len(board[0]):
                if board[i][j] == 0:  # then move is legal
                    board[i][j] = -1
                    max_length = max(max_length, 1 + self.longest((i,j), board, directions))
        return max_length

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


    @staticmethod
    def closer(board1, board2):
        counter = 0
        for i in range(len(board1)):
            for j in range(len(board1[1])):
                if board1[i][j] < board2[i][j]:
                    counter += 1
                elif board1[i][j] > board2[i][j]:
                    counter -= 1
        return counter
