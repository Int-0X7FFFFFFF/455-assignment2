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

def is_unbeatable_sequence(list_current: list, board: GoBoard, player: GO_COLOR) -> bool:
    seq_length = 0
    idx = 0
    while idx < len(list_current):
        if board.get_color(list_current[idx]) == player:
            start_idx = idx
            while idx < len(list_current) and board.get_color(list_current[idx]) == player:
                seq_length += 1
                idx += 1

            if seq_length == 4:
                # Check if there's a space before and after the sequence
                if start_idx - 1 < 0 or board.get_color(list_current[start_idx - 1]) == EMPTY:
                    if idx == len(list_current) or board.get_color(list_current[idx]) == EMPTY:
                        return True
        else:
            seq_length = 0
            idx += 1
    return False

def next_two(
    list_current: list, board: GoBoard, current_player: GO_COLOR, move: GO_POINT
):
    d1 = 0
    d2 = 0
    index = list_current.index(move)
    if 0 <= (index + 3) < len(list_current):
        if (
            board.get_color(list_current[index + 1]) == opponent(current_player)
            and board.get_color(list_current[index + 2]) == EMPTY
            and board.get_color(list_current[index + 3]) == EMPTY
        ):
            d1 = 0.25
        if (
            board.get_color(list_current[index + 2]) == opponent(current_player)
            and board.get_color(list_current[index + 1]) == opponent(current_player)
            and board.get_color(list_current[index + 3]) == EMPTY
        ):
            d1 = 0.5
    if 0 <= (index - 3) < len(list_current):
        if (
            board.get_color(list_current[index - 1]) == opponent(current_player)
            and board.get_color(list_current[index - 2]) == EMPTY
            and board.get_color(list_current[index - 3]) == EMPTY
        ):
            d2 = 0.25
        if (
            list_current[index - 2] == opponent(current_player)
            and board.get_color(list_current[index - 1]) == opponent(current_player)
            and board.get_color(list_current[index - 3]) == EMPTY
        ):
            d2 = 0.5
    return max(d1, d2)


def connect_cal(list_current: list, board: GoBoard, current_player: GO_COLOR) -> int:
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
    h_cap_op = 5
    board_copy = board.copy()
    board_copy.play_move(move, current_player)
    board_copy_op = board.copy()
    board_copy.play_move(move, opponent(current_player))
    h_value_cap = min(h_value, ((10 - board_copy.get_captures(current_player)) / 2))
    h_cap_op = min(
        h_value, ((10 - board_copy_op.get_captures(opponent(current_player))) / 2)
    )

    for row in board.rows:
        if move in row:
            counter = connect_cal(row, board_copy, current_player)
            counter_op = connect_cal(row, board_copy_op, opponent(current_player))
            h_tmp = h_value_cap - next_two(row, board_copy, current_player, move)
            h_tmp_op = h_cap_op - next_two(
                row, board_copy_op, opponent(current_player), move
            )
            h_value = min(h_value, (5 - counter), (5 - counter_op), h_tmp, h_tmp_op)
    for col in board.cols:
        if move in col:
            counter = connect_cal(col, board_copy, current_player)
            counter_op = connect_cal(col, board_copy_op, opponent(current_player))
            h_tmp = h_value_cap - next_two(col, board_copy, current_player, move)
            h_tmp_op = h_cap_op - next_two(
                col, board_copy_op, opponent(current_player), move
            )
            h_value = min(h_value, (5 - counter), (5 - counter_op), h_tmp, h_tmp_op)
    for diag in board.diags:
        if move in diag:
            counter = connect_cal(diag, board_copy, current_player)
            counter_op = connect_cal(diag, board_copy_op, opponent(current_player))
            h_tmp = h_value_cap - next_two(diag, board_copy, current_player, move)
            h_tmp_op = h_cap_op - next_two(
                diag, board_copy_op, opponent(current_player), move
            )
            h_value = min(h_value, (5 - counter), (5 - counter_op), h_tmp, h_tmp_op)
    return h_value


def alpha_beta(board: GoBoard, alpha, beta, depth, color: GO_COLOR, table: LookUpTable):
    if board.is_terminal() or depth == 0:
        return board.statically_evaluate(color), None, board
    
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
            res = alpha_beta(
                board_copy, -beta, -alpha, depth - 1, opponent(color), table
            )
            value = -res[0]
            table.store(board_copy.board, value, depth)

        if value > alpha:
            alpha = value
            best_move = move
            best_board = board_copy

        if alpha >= beta:
            break

    return alpha, best_move, best_board
