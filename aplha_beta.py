from board import GoBoard, GO_POINT
from board_base import GO_COLOR, opponent, EMPTY, BORDER

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


def alpha_beta(board: GoBoard, alpha, beta, depth, color: GO_COLOR):
    draw = None
    draw_b = None
    if board.is_terminal() or depth == 0:
        return board.statically_evaluate(color), None, board
    list_move = [(move, h_fun(board, move, color)) for move in board.get_empty_points()]
    sorted_list_move = sorted(list_move, key=lambda x: x[1], reverse=False)
    for index, (move, _) in enumerate(sorted_list_move):
        board_copy = board.copy()
        board_copy.play_move(move, color)
        res = alpha_beta(board_copy, -beta, -alpha, depth - 1, opponent(color))
        value = -res[0]
        if value > alpha:
            alpha = value
        if value >= beta:
            return beta, move, board_copy
        if value == EMPTY and draw == None:
            draw = move
            draw_b = board_copy
    return alpha, draw, draw_b

