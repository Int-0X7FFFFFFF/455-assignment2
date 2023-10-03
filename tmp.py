    def connect_cal(
        self, list_current: list, board: GoBoard, current_player: GO_COLOR
    ) -> int:
        U = -1
        prev = BORDER
        counter = 1
        for stone in list_current:
            if board.get_color(stone) == prev and prev == current_player:
                counter += 1
            else:
                if counter > U:
                    U = counter
                counter = 1
                prev = board.get_color(stone)
        if counter != -1:
            return counter
        else:
            return 0
        
    def next_two(self, list_current:list, board:GO_COLOR, current_player:GO_COLOR, move:GO_POINT):
        d1 = 0
        d2 = 0
        index = list_current.index(move)
        if (index + 3) <= len(list_current):
            if list_current[index + 1] == opponent(current_player) and list_current[index + 2] == EMPTY and list_current[index + 3] == EMPTY:
                d1 = 0.25
            if list_current[index + 2] == opponent(current_player) and list_current[index + 1] == opponent(current_player) and list_current[index + 3] == EMPTY:
                d1 = 0.5
        if (index - 3) <= len(list_current):
            if list_current[index - 1] == opponent(current_player) and list_current[index - 2] == EMPTY and list_current[index - 3] == EMPTY:
                d2 = 0.25
            if list_current[index - 2] == opponent(current_player) and list_current[index - 1] == opponent(current_player) and list_current[index - 3] == EMPTY:
                d2 = 0.5 
        return max(d1, d2)

    def h_fun(self, board: GoBoard, move: GO_POINT, current_player: GO_COLOR) -> int:
        h_value = 5
        board_copy = board.copy()
        board_copy.play_move(move, current_player)
        h_value = min(h_value, ((10 - board_copy.get_captures(current_player)) / 2))

        for row in board.rows:
            if move in row:
                counter = self.connect_cal(row, board_copy, current_player)
                h_value -= self.next_two(row, board_copy, current_player, move)
                h_value = min(h_value, (5 - counter))
        for col in board.cols:
            if move in col:
                counter = self.connect_cal(col, board_copy, current_player)
                h_value -= self.next_two(col, board_copy, current_player, move)
                h_value = min(h_value, (5 - counter))
        for diag in board.diags:
            if move in diag:
                counter = self.connect_cal(col, board_copy, current_player)
                h_value = min(h_value, (5 - counter))
        return h_value

def alpha_beta(self, current_player: GO_COLOR, board: GoBoard, alpha, beta, ply):
        """
        The function returns values:
        1. the score of the optimal move for the player who is to act;
        2. the optimal move
        """
        _no_win = False
        _no_win_move = None
        _first = False
        if self.init_search == 1:
            self.init_search = -1
            _first = True
            # print("")
        if self.is_terminal(board):
            return self.statically_evaluate(board), None
        # if ply == 0:
        #     return 0, None

        list_move = [
            (move, self.h_fun(board, move, current_player))
            for move in board.get_empty_points()
        ]
        sorted_list_move = sorted(list_move, key=lambda x: x[1], reverse=False)

        other_player = opponent(current_player)

        # if current_player == BLACK:
        #     m = inf
        #     U = [inf for move in board.get_empty_points()]
        # else:
        #     m = -inf
        #     U = [-inf for move in board.get_empty_points()]

        for index, (move, _) in enumerate(sorted_list_move):
            if current_player == WHITE:
                board_copy = board.copy()
                board_copy.play_move(move, current_player)
                try:
                    score_this, opt_move = self.alpha_beta(
                        other_player, board_copy, alpha, beta, ply - 1
                    )
                except RecursionError:
                    continue
                if score_this == 1:
                    return score_this, move
                if score_this == 0:
                    _no_win = True
                    _no_win_move = move
                # m = max(score_this, m)
                # if m >= beta:
                #     return m, move
                # alpha = min(alpha, m)
            else:
                board_copy = board.copy()
                board_copy.play_move(move, current_player)
                try:
                    score_this, opt_move = self.alpha_beta(
                        other_player, board_copy, alpha, beta, ply - 1
                    )
                except RecursionError:
                    continue
                if score_this == -1:
                    return score_this, move
                else:
                    _no_win == True
                    _no_win_move == move
                # m = min(score_this, m)
                # if m <= alpha:
                #     return m, move
                # beta = min(alpha, beta)

            # if not _first:
            #     if current_player == BLACK:
            #         if score_this == -1:
            #             return -1, move
            #     else:
            #         if score_this == 1:
            #             return 1, move


        if _no_win:
            return 0, _no_win_move
        else:
            if current_player == WHITE:
                return 0, None
            else:
                return 1, None
    
    def negamax_go(self, current_board:GoBoard, current_player:GO_COLOR):
        if self.is_terminal(current_board):
            return self.statically_evaluate_str(current_board)
        
        _have_draw = False

        list_move = [
            (move, self.h_fun(current_board, move, current_player))
            for move in current_board.get_empty_points()
        ]
        sorted_list_move = sorted(list_move, key=lambda x: x[1], reverse=False)
        
        for (move, _) in sorted_list_move:
            board = current_board.copy()
            board.play_move(move, current_player)
            res= self.negamax_go(board, opponent(current_player))
            if res == "draw":
                _have_draw = True
            if current_player == BLACK:
                if res == "b":
                    return res
            else:
                if res == "w":
                    return res

        if _have_draw:
            return "draw"
        else:
            if current_player == BLACK:
                return "w"
            else:
                return "b"

    def negamax(self, current_board:GoBoard, player:GO_COLOR):
        heap = []
        heap_m = []
        for move in current_board.get_empty_points():
            h_value = self.h_fun(current_board, move, player)
            board = current_board.copy()
            item = HeapItem()
            item.set_up(move, h_value)
            heapq.heappush(heap, item)
        current_player = opponent(player)
        while len(heap) == 0 and len(heap_m) == 0:
            if current_player == player:
                pass
            else:
                pass

        pass


