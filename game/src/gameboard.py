from copy import deepcopy
from typing import List

from .consts import *
from .sources import GameSource, generate_moves
from .utils import calculate_yx

GAME_BOARD = '''

 BLACK



  ┌───┬───┬───┬───┬───┬───┬───┬───┐
8 │{:^3}│{:^3}│{:^3}│{:^3}│{:^3}│{:^3}│{:^3}│{:^3}│
  ├───┼───┼───┼───┼───┼───┼───┼───┤
7 │{:^3}│{:^3}│{:^3}│{:^3}│{:^3}│{:^3}│{:^3}│{:^3}│
  ├───┼───┼───┼───┼───┼───┼───┼───┤
6 │{:^3}│{:^3}│{:^3}│{:^3}│{:^3}│{:^3}│{:^3}│{:^3}│
  ├───┼───┼───┼───┼───┼───┼───┼───┤
5 │{:^3}│{:^3}│{:^3}│{:^3}│{:^3}│{:^3}│{:^3}│{:^3}│
  ├───┼───┼───┼───┼───┼───┼───┼───┤
4 │{:^3}│{:^3}│{:^3}│{:^3}│{:^3}│{:^3}│{:^3}│{:^3}│
  ├───┼───┼───┼───┼───┼───┼───┼───┤
3 │{:^3}│{:^3}│{:^3}│{:^3}│{:^3}│{:^3}│{:^3}│{:^3}│
  ├───┼───┼───┼───┼───┼───┼───┼───┤
2 │{:^3}│{:^3}│{:^3}│{:^3}│{:^3}│{:^3}│{:^3}│{:^3}│
  ├───┼───┼───┼───┼───┼───┼───┼───┤
1 │{:^3}│{:^3}│{:^3}│{:^3}│{:^3}│{:^3}│{:^3}│{:^3}│
  └───┴───┴───┴───┴───┴───┴───┴───┘
 A   B   C   D   E   F   G   H



 WHITE
'''


class GameBoard:
    def __init__(self, source: GameSource):
        self.source = source
        self.source.board = self
        self.reset_timer = True

    def get_field(self, highlight: str = None) -> str:
        field = deepcopy(self.source.get_field())
        field2 = deepcopy(field)

        if highlight is not None:
            y, x = calculate_yx(highlight[:2])
            field[y][x] = HIGHLIGHT + field[y][x] + HIGHLIGHT

            moves = generate_moves(field2, self.source.white_turn)
            for move in filter(lambda s: s[0] == f'{y}{x}', moves):
                move_y, move_x = calculate_yx(move[1])
                field[move_y][move_x] = HIGHLIGHT + field[move_y][move_x] + HIGHLIGHT

            if len(highlight) == 5:
                move_y, move_x = calculate_yx(highlight[3:5])
                field[move_y][move_x] = HIGHLIGHT * 3

        flatten = [item for sublist in field for item in sublist]
        return GAME_BOARD.format(*flatten)

    def make_move(self, chess_yx: str, move_yx: str, t: float):
        self.source.make_move(chess_yx, move_yx, t)

    def check_move(self, chess_yx: str, move_yx: str) -> bool:
        return check_move(self.source.get_field(), self.source.white_turn, chess_yx, move_yx)

    def move_checks(self, move_yx: str):
        self.source.move_checks(move_yx)

    def can_move(self):
        return self.source.can_move()


def check_move(field: List[List[str]], white_turn: bool, chess_yx: str, move_yx: str):
    if chess_yx == move_yx:
        return False

    chess_y, chess_x = calculate_yx(chess_yx)
    move_y, move_x = calculate_yx(move_yx)

    if field[chess_y][chess_x] == ' ':
        return False

    if ((field[chess_y][chess_x] in WHITE_PIECES) and not white_turn) or (
            (field[chess_y][chess_x] in BLACK_PIECES) and white_turn):
        return False

    if field[move_y][move_x] != ' ' and (field[move_y][move_x] in WHITE_PIECES) == (
            field[chess_y][chess_x] in WHITE_PIECES):  # check if player tries to eat his own chess
        return False

    stage1 = can_move_stage1(field[chess_y][chess_x], chess_yx, move_yx, field)  # check if chess can move like that
    if not stage1:
        return False

    return can_move_stage2(field[chess_y][chess_x], chess_yx, move_yx, field)


def can_move_stage1(piece: str, chess_yx: str, move_yx: str, field: List[List[str]]):
    #
    # Stage 1
    # well, it just checks if chess can move like that.
    #
    y1, x1 = calculate_yx(chess_yx)
    y2, x2 = calculate_yx(move_yx)

    # todo: combine black and white pawns
    if piece == BLACK_PAWN:
        if y1 == 1 and y2 in [2, 3] and x1 == x2:  # first move
            return True

        if y2 - y1 == 1 and x1 == x2:
            return True

        if y2 - y1 == 1 and abs(x1 - x2) == 1:
            return field[y2][x2] != ' '

        return False
    elif piece == WHITE_PAWN:
        if y1 == 6 and y2 in [5, 4] and x1 == x2:  # first move
            return True

        if y1 - y2 == 1 and x1 == x2:
            return True

        if y1 - y2 == 1 and abs(x1 - x2) == 1:
            return field[y2][x2] != ' '

        return False
    elif piece in (BLACK_ROOK, WHITE_ROOK):
        return x1 == x2 or y1 == y2
    elif piece in (BLACK_KING, WHITE_KING):
        return abs(x1 - x2) <= 1 and abs(y1 - y2) <= 1
    elif piece in (BLACK_BISHOP, WHITE_BISHOP):
        return abs(x1 - x2) == abs(y1 - y2)
    elif piece in (BLACK_QUEEN, WHITE_QUEEN):
        return abs(x1 - x2) == abs(y1 - y2) or x1 == x2 or y1 == y2
    elif piece in (BLACK_KNIGHT, WHITE_KNIGHT):
        t1 = abs(x1 - x2)
        t2 = abs(y1 - y2)

        return (t1 == 1 and t2 == 2) or (t1 == 2 and t2 == 1)
    else:
        print(piece)
        raise Exception()


def check_intersection(y, x, is_white: bool, field: List[List[str]]):
    chess = field[y][x]
    return not (chess != ' ' and is_white == (chess in WHITE_PIECES))


def can_move_stage2(piece: str, piece_yx: str, move_yx: str, field: List[List[str]]):
    #
    # Stage 2
    # it checks if chess intersects another chess
    #
    y1, x1 = calculate_yx(piece_yx)
    y2, x2 = calculate_yx(move_yx)

    is_white = piece in WHITE_PIECES

    if piece in (BLACK_PAWN, WHITE_PAWN):
        if x1 == x2:
            r = (y1 + 1, y2) if piece == BLACK_PAWN else (y2 - 1, y1, - 1)
            for y in range(*r):
                if not check_intersection(y, x1, is_white, field):
                    return False
            return True

        # x1 != x2, seems like player tries to eat a chess
        return True
    elif piece in (BLACK_ROOK, WHITE_ROOK):
        if x1 == x2:
            ma = max(y1, y2)
            mi = min(y1, y2)
            for y in range(mi + 1, ma):
                if not check_intersection(y, x1, is_white, field):
                    return False
            return True
        else:
            ma = max(x1, x2)
            mi = min(x1, x2)
            for x in range(mi + 1, ma):
                if not check_intersection(y1, x, is_white, field):
                    return False
            return True
    elif piece in (BLACK_KING, WHITE_KING):
        return True
    elif piece in (BLACK_BISHOP, WHITE_BISHOP):
        steps = abs(x1 - x2)

        step_x = -1 if x1 > x2 else 1
        step_y = -1 if y1 > y2 else 1

        for i in range(1, steps):
            if not check_intersection(y1 + i * step_y, x1 + i * step_x, is_white, field):
                return False
        return True
    elif piece in (BLACK_QUEEN, WHITE_QUEEN):
        if x1 == x2 or y1 == y2:  # up, down, left, right
            return can_move_stage2(WHITE_ROOK if piece in WHITE_PIECES else BLACK_ROOK, piece_yx, move_yx, field)
        else:  # diagonally
            return can_move_stage2(WHITE_BISHOP if piece in WHITE_PIECES else BLACK_BISHOP, piece_yx, move_yx, field)
    elif piece in (BLACK_KNIGHT, WHITE_KNIGHT):
        return True
    else:
        print(piece)
        raise Exception()
