from board import GoBoard, GO_POINT
from board_base import GO_COLOR, opponent, EMPTY, BORDER, BLACK
import numpy as np
from board_util import GoBoardUtil


class LookUpTable:
    def __init__(self) -> None:
        self.table = {}

    def __repr__(self):
        return self.table.__repr__()

    def store(self, board: np.ndarray, value, goboard: GoBoard):
        self.table[(tuple(board))] = (value, goboard)

    def look_up(self, board: np.ndarray):
        return self.table.get(tuple(board))


def connect_cal(list_current: list, board: GoBoard, current_player: GO_COLOR) -> int:
    U = -1
    prev = BORDER
    counter = 1
    for index, stone in enumerate(list_current):
        if board.get_color(stone) == prev and prev == current_player:
            counter += 1
        else:
            if counter > U:
                if counter == 4:
                # Check if there's a space before and after the sequence
                    if (index - 5 >= 0 and board.get_color(list_current[index - 5]) == EMPTY) and \
                    (board.get_color(stone) == EMPTY):
                        return 105
                U = counter
            counter = 1
            prev = board.get_color(stone)
    if counter != -1:
        return counter
    else:
        return 0


def h_fun(board: GoBoard, move: GO_POINT, current_player: GO_COLOR) -> int:
    h_value = 5
    arraycopy = board.board.copy()
    w_e = board.white_captures
    b_e = board.black_captures
    board.play_move(move, current_player)

    for row in board.rows:
        if move in row:
            counter = connect_cal(row, board, current_player)
            if counter == 5 or counter == 105:
                board.board = arraycopy
                board.white_captures = w_e
                board.black_captures = b_e
                return -100
            h_value = min(h_value, (5 - counter))
    for col in board.cols:
        if move in col:
            counter = connect_cal(col, board, current_player)
            if counter == 5 or counter == 105:
                board.board = arraycopy
                board.white_captures = w_e
                board.black_captures = b_e
                return -100
            h_value = min(h_value, (5 - counter))
    for diag in board.diags:
        if move in diag:
            counter = connect_cal(diag, board, current_player)
            if counter == 5 or counter == 105:
                board.board = arraycopy
                board.white_captures = w_e
                board.black_captures = b_e
                return -100
            h_value = min(h_value, (5 - counter))

    board.board = arraycopy
    board.white_captures = w_e
    board.black_captures = b_e
    board.winner = None
    return h_value


def alpha_beta(board: GoBoard, alpha, beta, depth, color: GO_COLOR, table: LookUpTable):
    if board.is_terminal() or depth == 0:
        return board.statically_evaluate(color), None

    # unbeatable = False

    # for sequence in [board.rows, board.cols, board.diags]:
    #     for line in sequence:
    #         if is_unbeatable_sequence(line, board, opponent(color)):
    #             unbeatable = True
    #             break

    # if unbeatable:
    #     for move in board.get_empty_points():
    #         board_copy = board.copy()
    #         board_copy.play_move(move, color)
    #         if board_copy.is_terminal():
    #             return 1, move, board
    # if unbeatable:
    #     return -1, None, board

    best_move = None

    list_move = [(move, h_fun(board, move, color)) for move in board.get_empty_points()]
    sorted_list_move = sorted(list_move, key=lambda x: x[1], reverse=False)

    if len(sorted_list_move)!= 0 and sorted_list_move[0][1] == -100:
        return 1, sorted_list_move[0][0]

    for move, _ in sorted_list_move:
        arraycopy = board.board.copy()
        winner = board.winner
        w_e = board.white_captures
        b_e = board.black_captures
        board.play_move(move, color)
        look_up = table.look_up(board.board)

        if look_up is not None and look_up[1] >= depth:
            value = look_up[0]
        else:
            res = alpha_beta(board, -beta, -alpha, depth - 1, opponent(color), table)
            value = -res[0]
            table.store(board.board, value, depth)

        board.board = arraycopy
        board.white_captures = w_e
        board.black_captures = b_e
        board.winner = winner

        if value > alpha:
            alpha = value
            best_move = move

        if alpha >= beta:
            break

    return alpha, best_move
