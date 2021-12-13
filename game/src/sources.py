import time
from copy import deepcopy
from typing import List, Dict

import requests

from .consts import *
from .utils import calculate_yx, alphabet

AI_DEPTH = 2


#
# Alpha-beta pruning
#

def reverse(data: List):
    return list(reversed(deepcopy(data)))


PAWN_EVAL_WHITE = [
    [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0],
    [1.0, 1.0, 2.0, 3.0, 3.0, 2.0, 1.0, 1.0],
    [0.5, 0.5, 1.0, 2.5, 2.5, 1.0, 0.5, 0.5],
    [0.0, 0.0, 0.0, 2.0, 2.0, 0.0, 0.0, 0.0],
    [0.5, -0.5, -1.0, 0.0, 0.0, -1.0, -0.5, 0.5],
    [0.5, 1.0, 1.0, -2.0, -2.0, 1.0, 1.0, 0.5],
    [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
]
PAWN_EVAL_BLACK = reverse(PAWN_EVAL_WHITE)

KNIGHT_EVAL = [
    [-5.0, -4.0, -3.0, -3.0, -3.0, -3.0, -4.0, -5.0],
    [-4.0, -2.0, 0.0, 0.0, 0.0, 0.0, -2.0, -4.0],
    [-3.0, 0.0, 1.0, 1.5, 1.5, 1.0, 0.0, -3.0],
    [-3.0, 0.5, 1.5, 2.0, 2.0, 1.5, 0.5, -3.0],
    [-3.0, 0.0, 1.5, 2.0, 2.0, 1.5, 0.0, -3.0],
    [-3.0, 0.5, 1.0, 1.5, 1.5, 1.0, 0.5, -3.0],
    [-4.0, -2.0, 0.0, 0.5, 0.5, 0.0, -2.0, -4.0],
    [-5.0, -4.0, -3.0, -3.0, -3.0, -3.0, -4.0, -5.0]
]

BISHOP_EVAL_WHITE = [
    [-2.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -2.0],
    [-1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -1.0],
    [-1.0, 0.0, 0.5, 1.0, 1.0, 0.5, 0.0, -1.0],
    [-1.0, 0.5, 0.5, 1.0, 1.0, 0.5, 0.5, -1.0],
    [-1.0, 0.0, 1.0, 1.0, 1.0, 1.0, 0.0, -1.0],
    [-1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, -1.0],
    [-1.0, 0.5, 0.0, 0.0, 0.0, 0.0, 0.5, -1.0],
    [-2.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -2.0]
]
BISHOP_EVAL_BLACK = reverse(BISHOP_EVAL_WHITE)

ROOK_EVAL_WHITE = [
    [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [0.5, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.5],
    [-0.5, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -0.5],
    [-0.5, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -0.5],
    [-0.5, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -0.5],
    [-0.5, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -0.5],
    [-0.5, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -0.5],
    [0.0, 0.0, 0.0, 0.5, 0.5, 0.0, 0.0, 0.0]
]
ROOK_EVAL_BLACK = reverse(ROOK_EVAL_WHITE)

QUEEN_EVAL = [
    [-2.0, -1.0, -1.0, -0.5, -0.5, -1.0, -1.0, -2.0],
    [-1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -1.0],
    [-1.0, 0.0, 0.5, 0.5, 0.5, 0.5, 0.0, -1.0],
    [-0.5, 0.0, 0.5, 0.5, 0.5, 0.5, 0.0, -0.5],
    [0.0, 0.0, 0.5, 0.5, 0.5, 0.5, 0.0, -0.5],
    [-1.0, 0.5, 0.5, 0.5, 0.5, 0.5, 0.0, -1.0],
    [-1.0, 0.0, 0.5, 0.0, 0.0, 0.0, 0.0, -1.0],
    [-2.0, -1.0, -1.0, -0.5, -0.5, -1.0, -1.0, -2.0]
]

KING_EVAL_WHITE = [
    [-3.0, -4.0, -4.0, -5.0, -5.0, -4.0, -4.0, -3.0],
    [-3.0, -4.0, -4.0, -5.0, -5.0, -4.0, -4.0, -3.0],
    [-3.0, -4.0, -4.0, -5.0, -5.0, -4.0, -4.0, -3.0],
    [-3.0, -4.0, -4.0, -5.0, -5.0, -4.0, -4.0, -3.0],
    [-2.0, -3.0, -3.0, -4.0, -4.0, -3.0, -3.0, -2.0],
    [-1.0, -2.0, -2.0, -2.0, -2.0, -2.0, -2.0, -1.0],
    [2.0, 2.0, 0.0, 0.0, 0.0, 0.0, 2.0, 2.0],
    [2.0, 3.0, 1.0, 0.0, 0.0, 1.0, 3.0, 2.0]
]
KING_EVAL_BLACK = reverse(KING_EVAL_WHITE)


class Player:
    def __init__(self, id: int, username: str):
        self.id = id
        self.username = username


class GameSource:
    def __init__(self):
        self.white_turn = True
        self.board = None

    def get_field(self) -> List[List[str]]:
        raise NotImplementedError()

    def get_player(self) -> Player:
        raise NotImplementedError()

    def get_enemy(self) -> Player:
        raise NotImplementedError()

    def get_history(self) -> List[str]:
        raise NotImplementedError()

    def get_white_won(self):
        raise NotImplementedError()

    def make_move(self, piece_yx: str, move_yx: str, t: float):
        raise NotImplementedError()

    def move_checks(self, move_yx: str):
        raise NotImplementedError()

    def can_move(self):
        raise NotImplementedError()

    def get_title(self):
        raise NotImplementedError()


def king_eatable(field: List[List[str]], king_yx, white_turn: bool):
    # generate moves for opponent
    moves = generate_moves(field, not white_turn)

    for move in moves:
        if move[1] == king_yx:
            return True

    return False


class LocalSource(GameSource):
    def __init__(self, player1=None, player2=None):
        super().__init__()

        self.field = []
        self.field.append(
            [BLACK_ROOK, BLACK_KNIGHT, BLACK_BISHOP, BLACK_QUEEN, BLACK_KING, BLACK_BISHOP, BLACK_KNIGHT, BLACK_ROOK])
        self.field.append([BLACK_PAWN] * 8)
        self.field.append([' '] * 8)
        self.field.append([' '] * 8)
        self.field.append([' '] * 8)
        self.field.append([' '] * 8)
        self.field.append([WHITE_PAWN] * 8)
        self.field.append(
            [WHITE_ROOK, WHITE_KNIGHT, WHITE_BISHOP, WHITE_QUEEN, WHITE_KING, WHITE_BISHOP, WHITE_KNIGHT, WHITE_ROOK])

        self.player1 = player1
        self.player2 = player2

        if player1 is None:
            self.player1 = Player(-1, 'Player 1')
        if player2 is None:
            self.player2 = Player(-1, 'Player 2')

        self.white_won = None  # None if the game is running, false if black won, true if white won.
        self.history = []

    def get_field(self):
        return self.field

    def get_player(self):
        return self.player1

    def get_enemy(self):
        return self.player2

    def get_history(self):
        history = deepcopy(self.history)[-8:][::-1]
        if len(history) < 8:
            history += ['.'] * (8 - len(history))

        return history

    def get_white_won(self):
        return self.white_won

    def make_move(self, chess_yx: str, move_yx: str, t: float):
        try:
            int(chess_yx)
            int(move_yx)
            chess_yx = f'{alphabet[int(chess_yx[1])]}{8 - int(chess_yx[0])}'
            move_yx = f'{alphabet[int(move_yx[1])]}{8 - int(move_yx[0])}'
        except:
            pass

        chess_yx = chess_yx.upper()
        move_yx = move_yx.upper()

        chess_y, chess_x = calculate_yx(chess_yx)
        move_y, move_x = calculate_yx(move_yx)

        self.field[move_y][move_x] = self.field[chess_y][chess_x]
        self.field[chess_y][chess_x] = ' '

        self.white_turn = not self.white_turn

        self.history.append(f'{chess_yx} → {move_yx} ({round(t, 1):4} s)')

    def move_checks(self, move_yx: str):
        if not any(BLACK_KING in x for x in self.field):
            self.white_won = True
            return
        if not any(WHITE_KING in x for x in self.field):
            self.white_won = False
            return

        y, x = calculate_yx(move_yx)

        chess = self.field[y][x]

        if chess == WHITE_PAWN and y == 7:
            self.field[y][x] = WHITE_QUEEN
        if chess == BLACK_PAWN and y == 0:
            self.field[y][x] = BLACK_QUEEN

        # find king on the board
        king_yx = None
        for y in range(len(self.field)):
            for x in range(len(self.field[y])):
                if self.field[y][x] == (WHITE_KING if self.white_turn else BLACK_KING):
                    king_yx = f'{y}{x}'
                    break

        #
        # Checkmate
        #
        if king_eatable(self.field, king_yx, self.white_turn):
            moves = generate_moves(self.field, not self.white_turn)

            # filter king moves
            king_moves = filter(lambda x: x[0] == king_yx, moves)

            # check if king can escape
            for move in king_moves:
                virtual_move(self.field, *move)
                if not king_eatable(self.field, move[1], self.white_turn):
                    return
                virtual_move(self.field, *reversed(move))

            # king fucked up
            self.white_won = not self.white_turn

    def can_move(self):
        return self.get_white_won() is None

    def get_title(self):
        return 'Local game: Player1 VS Player2'


def get_chess_value(field, y, x):
    if field[y][x] == ' ':
        return 0

    if field[y][x] in (WHITE_PAWN, BLACK_PAWN):
        value = 10 + (PAWN_EVAL_WHITE[y][x] if field[y][x] in WHITE_PIECES else PAWN_EVAL_BLACK[y][x])
    elif field[y][x] in (WHITE_ROOK, BLACK_ROOK):
        value = 50 + (ROOK_EVAL_WHITE[y][x] if field[y][x] in WHITE_PIECES else ROOK_EVAL_BLACK[y][x])
    elif field[y][x] in (WHITE_KNIGHT, BLACK_KNIGHT):
        value = 30 + KNIGHT_EVAL[y][x]
    elif field[y][x] in (WHITE_BISHOP, BLACK_BISHOP):
        value = 30 + (BISHOP_EVAL_WHITE[y][x] if field[y][x] in WHITE_PIECES else BISHOP_EVAL_BLACK[y][x])
    elif field[y][x] in (WHITE_QUEEN, BLACK_QUEEN):
        value = 90 + QUEEN_EVAL[y][x]
    else:
        value = 900 + (KING_EVAL_WHITE[y][x] if field[y][x] in WHITE_PIECES else KING_EVAL_BLACK[y][x])

    return value if field[y][x] in WHITE_PIECES else -value


def generate_moves(field: List[List[str]], white_turn: bool = False):
    from .gameboard import check_move
    moves = []

    for y in range(len(field)):
        for x in range(len(field[y])):
            if field[y][x] == ' ':
                continue

            for y2 in range(len(field)):
                for x2 in range(len(field[y2])):
                    s1 = f'{y}{x}'
                    s2 = f'{y2}{x2}'

                    if check_move(field, white_turn, s1, s2):
                        moves.append((s1, s2))

    return moves


def virtual_move(field: List[List[str]], chess_yx, move_yx):
    piece_y, piece_x = calculate_yx(chess_yx)
    move_y, move_x = calculate_yx(move_yx)

    field[move_y][move_x] = field[piece_y][piece_x]
    field[piece_y][piece_x] = ' '


class LocalAISource(LocalSource):
    def __init__(self, username: str):
        super().__init__(Player(-1, username), Player(-1, 'AI'))

    def make_move(self, chess_yx: str, move_yx: str, t: float):
        super(LocalAISource, self).make_move(chess_yx, move_yx, t)

        # https://github.com/lhartikk/simple-chess-ai/blob/665606d574ba83a7f958121bd7c58903f162f902/script.js#L6
        t1 = time.time()
        field = deepcopy(self.field)

        is_maximising_player = True
        moves = generate_moves(field)

        # check if we can eat something
        possible_eats = []
        for move in moves:
            y, x = calculate_yx(move[1])
            if field[y][x] in WHITE_PIECES:
                possible_eats.append(move)

        if possible_eats:
            if len(possible_eats) == 1:
                move = possible_eats[0]
            else:
                move = max(possible_eats, key=lambda m: abs(get_chess_value(self.field, int(m[1][0]), int(m[1][1]))))

            super(LocalAISource, self).make_move(move[0], move[1], time.time() - t1)
            return

        best_move = -9999
        best_move_found = None

        for move in moves:
            virtual_move(field, *move)
            value = self._minimax(field, AI_DEPTH - 1, -10000, 10000, not is_maximising_player)
            virtual_move(field, *reversed(move))

            if value >= best_move:
                best_move = value
                best_move_found = move

        t2 = time.time()
        t = t2 - t1

        super(LocalAISource, self).make_move(best_move_found[0], best_move_found[1], t)

    def _minimax(self, field: List[List[str]], depth: int, alpha, beta, is_maximising_player: bool):
        if depth == 0:
            return -self.evaluate_board(field)

        moves = generate_moves(field)

        if is_maximising_player:
            best_move = -9999
            for move in moves:
                virtual_move(field, *move)
                best_move = max(best_move, self._minimax(field, depth - 1, alpha, beta, not is_maximising_player))
                virtual_move(field, *reversed(move))
                alpha = max(alpha, best_move)
                if beta <= alpha:
                    return best_move

            return best_move
        else:
            best_move = 9999
            for move in moves:
                virtual_move(field, *move)
                best_move = min(best_move, self._minimax(field, depth - 1, alpha, beta, not is_maximising_player))
                virtual_move(field, *reversed(move))
                alpha = min(alpha, best_move)
                if beta <= alpha:
                    return best_move

            return best_move

    def evaluate_board(self, field: List[List[str]]):
        total = 0

        for y in range(len(field)):
            for x in range(len(field[y])):
                total += get_chess_value(field, y, x)

        return total

    def get_title(self):
        return f'Local game: {self.player1.username} VS AI'


class RemoteSource(GameSource):
    def __init__(self, local_user: Dict, locally_created: bool, game_id: int):
        super().__init__()

        self.game_id = game_id
        self.data = {}
        self.local_turn = locally_created

        self.local_user = local_user

        if locally_created:
            self.game_id = requests.post(BACKEND_URL + '/games/create', json={
                'creator_id': local_user['id'],
                'enemy_id': game_id
            }).json()['id']

        self.update()
        self.update_counter = 0

    def update(self):
        self.data = requests.get(BACKEND_URL + f'/games/{self.game_id}',
                                 json={'user_id': self.local_user['id']}).json()
        self.white_turn = self.data['white_turn']

        self.local_turn = self.data['player1']['id'] == self.local_user['id']

    def get_field(self) -> List[List[str]]:
        if self.update_counter >= 10:
            self.update_counter = 0
            self.update()

        self.update_counter += 1

        return self.data['field']

    def get_player(self) -> Player:
        raise NotImplementedError()

    def get_enemy(self) -> Player:
        raise NotImplementedError()

    def get_history(self) -> List[str]:
        return self.data['history']

    def make_move(self, chess_yx: str, move_yx: str, t: float):
        requests.post(BACKEND_URL + f'/games/{self.game_id}/move', json={
            'chess_yx': chess_yx,
            'move_yx': move_yx,
            't': t
        })
        self.update()

    def move_checks(self, move_yx: str):  # already checked on the server
        pass

    def can_move(self):
        if self.local_turn:
            return self.data['white_turn']

        return not self.data['white_turn']

    def get_title(self):
        return f'{self.data["player1"]["username"]} vs {self.data["player2"]["username"]} (GAME_ID: {self.game_id})'

    def get_white_won(self):
        return self.data['white_won']
