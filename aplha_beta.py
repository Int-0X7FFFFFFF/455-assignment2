from board import GoBoard, GO_POINT
from board_base import GO_COLOR, opponent, EMPTY, BORDER, BLACK
import numpy as np

class LookUpTable:
    def __init__(self) -> None:
        self.table = {}

    def __repr__(self):
        return self.table.__repr__()

    def store(self, board:np.ndarray, value, goboard:GoBoard):
        self.table[(tuple(board))] = (value, goboard)

    def look_up(self, board:np.ndarray):
        return self.table.get(tuple(board))

def connect_cal(
        list_current: list, board: GoBoard, current_player: GO_COLOR
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

def h_fun(board: GoBoard, move: GO_POINT, current_player: GO_COLOR) -> int:
    h_value = 5
    board_copy = board.copy()
    board_copy.play_move(move, current_player)
    h_value = min(h_value, ((10 - board_copy.get_captures(current_player)) / 2))

    for row in board.rows:
        if move in row:
            counter = connect_cal(row, board_copy, current_player)
            # h_value -= self.next_two(row, board_copy, current_player, move)
            h_value = min(h_value, (5 - counter))
    for col in board.cols:
        if move in col:
            counter = connect_cal(col, board_copy, current_player)
            # h_value -= self.next_two(col, board_copy, current_player, move)
            h_value = min(h_value, (5 - counter))
    for diag in board.diags:
        if move in diag:
            counter = connect_cal(col, board_copy, current_player)
            h_value = min(h_value, (5 - counter))
    return h_value


def alpha_beta(board: GoBoard, alpha, beta, depth, color: GO_COLOR, table:LookUpTable):
    if board.is_terminal() or depth == 0:
        return board.statically_evaluate(color), None, board

    best_move = None
    best_board = None

    list_move = [(move, h_fun(board, move, color)) for move in board.get_empty_points()]
    sorted_list_move = sorted(list_move, key=lambda x: x[1], reverse=False)

    for move, _ in sorted_list_move:
        board_copy = board.copy()
        board_copy.play_move(move, color)
        look_up = table.look_up(board_copy.board)

        if look_up is not None and look_up[1] >= depth:
            value = look_up[0]
        else:
            res = alpha_beta(board_copy, -beta, -alpha, depth - 1, opponent(color), table)
            value = -res[0]
            table.store(board_copy.board, value, depth)

        if value > alpha:
            alpha = value
            best_move = move
            best_board = board_copy

        if alpha >= beta:
            break

    return alpha, best_move, best_board
