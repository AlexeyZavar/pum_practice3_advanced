import json
import os.path
import random
import re
import sys
import time
from math import floor
from typing import Optional, Dict

import requests
from asciimatics.event import KeyboardEvent
from asciimatics.exceptions import NextScene
from asciimatics.particles import StarFirework, Rain, ParticleEffect
from asciimatics.widgets import Frame, Layout, Label, Button, Text, PopUpDialog

from src import calculate_yx, GameBoard, GameSource, LocalSource, LocalAISource, RemoteSource, GAME_BOARD, BACKEND_URL

TIPS = [
    'LEARN THE MOVES',
    'OPEN WITH A PAWN',
    'GET THE KNIGHTS AND BISHOPS OUT',
    'WATCH YOUR BACK!',
    'DON\'T WASTE TIME',
    '“CASTLE” EARLY',
    'ATTACK IN THE “MIDDLEGAME”',
    'LOSE PIECES WISELY',
    'DON\'T PLAY TOO FAST',
    'WIN THE ENDGAME',
    'HAVE A PLAN',
    'KEEP YOUR KING SAFE',
    'CONTROL THE CENTER',
    'ALWAYS BE ALERT',
    'BE PATIENT',
    'BE STRATEGIC'
]

DOT_USER = '.user2' if 'SECOND_USER' in os.environ else '.user'
BOARD: Optional[GameBoard] = None
USER: Dict = {}


class RegisterScreen(Frame):
    def __init__(self, screen):
        super().__init__(screen, 8, screen.width - 20)
        self.set_theme('chess')

        layout = Layout([100])
        self.add_layout(layout)

        self.username_textbox = Text('Username >', validator=self._validate_username, max_length=32)
        layout.add_widget(self.username_textbox)

        self.fix()

    @staticmethod
    def _validate_username(value):
        return len(value) > 4

    def _register(self):
        if not self.username_textbox.is_valid:
            return

        res = requests.post(BACKEND_URL + '/users/register', json={
            'username': self.username_textbox.value
        }).text

        self.username_textbox.value = ''

        with open(DOT_USER, 'w', encoding='utf-8') as f:
            f.write(res)

    def process_event(self, event):
        if event is not None and isinstance(event, KeyboardEvent) and event.key_code == 13:
            self._register()
            event = None

        return super().process_event(event)

    @staticmethod
    def _reset_user_data():
        os.remove(DOT_USER)
        sys.exit(-1)

    def update(self, frame_no):
        if os.path.isfile(DOT_USER):
            with open(DOT_USER, 'r', encoding='utf-8') as f:
                time.sleep(0.05)

                try:
                    global USER
                    USER = json.load(f)
                    USER = requests.post(BACKEND_URL + '/users/authorize',
                                         json={'id': USER['id'], 'password': USER['password']}).json()
                except:
                    self.add_effect(PopUpDialog(self.screen, ' Can\'t authorize. Resetting user data... ', ['OK'],
                                                on_close=self._reset_user_data, has_shadow=True, theme='chess'))
                    return

                raise NextScene('Main')

        super().update(frame_no)


class MainScreen(Frame):
    def __init__(self, screen):
        super().__init__(screen, 14, screen.width // 2)
        self.set_theme('chess')

        layout = Layout([100])
        self.add_layout(layout)

        self.howto_label = Label('', height=3, align='^')

        layout.add_widget(self.howto_label)
        layout.add_widget(Button('locally', self._play_locally))
        layout.add_widget(Button('with AI', self._play_ai))
        layout.add_widget(Button('over network', self._play_network))

        layout.add_widget(Label('\nOther', height=3, align='^'))
        layout.add_widget(Button('scoreboard', self._scoreboard))
        layout.add_widget(Button('exit', sys.exit))

        self.fix()

    def _play_locally(self):
        self._play(LocalSource())

    def _play_ai(self):
        self._play(LocalAISource(USER['username']))

    def _play_network(self):
        raise NextScene('Join')

    def _play(self, source: GameSource):
        global BOARD
        BOARD = GameBoard(source)

        raise NextScene('Board')

    def _scoreboard(self):
        raise NextScene('Scoreboard')

    def update(self, frame_no):
        self.howto_label.text = f'\nHow you want to play today, {USER["username"]}?'

        if frame_no % 40 == 0 or frame_no == 1:
            self.add_effect(StarFirework(self.screen, self.screen.width // 2, 4, 40))
            self.add_effect(StarFirework(self.screen, self.screen.width // 2 - 30, 10, 40))
            self.add_effect(StarFirework(self.screen, self.screen.width // 2 + 30, 10, 40))

        super().update(frame_no)


class ScoreboardScreen(Frame):
    def __init__(self, screen):
        super().__init__(screen, 21, 65)
        self.set_theme('chess')

        layout = Layout([100])
        self.add_layout(layout)

        layout.add_widget(Label('Scoreboard (TOP 10)', height=2, align='^'))

        self.scoreboard_label = Label('', 12, align='^')
        layout.add_widget(self.scoreboard_label)

        layout.add_widget(Button('return', self._return))

        self.scoreboard = []

        self._fetch()

        self.fix()

    def _return(self):
        raise NextScene('Main')

    def _fetch(self):
        try:
            self.scoreboard = requests.get(BACKEND_URL + '/users/scoreboard').json()
        except:
            self.scoreboard = [{'username': 'Can\'t fetch data', 'wins': -1, 'looses': -1}]

    def update(self, frame_no):
        if frame_no == 1 or frame_no % 10 == 0:
            self.add_effect(StarFirework(self.screen, self.screen.width // 2 - 35, self.screen.height // 2, 20))
            self.add_effect(StarFirework(self.screen, self.screen.width // 2 + 35, self.screen.height // 2, 20))

            self.add_effect(StarFirework(self.screen, self.screen.width // 2 - 45, self.screen.height // 2 - 15, 20))
            self.add_effect(StarFirework(self.screen, self.screen.width // 2 + 45, self.screen.height // 2 - 15, 20))

            self._fetch()

        if frame_no % 20 == 0:
            self.add_effect(StarFirework(self.screen, self.screen.width // 2, 4, 20))

        self.scoreboard_label.text = '\n'.join(
            [f'{player["username"]}: {player["wins"]} wins, {player["looses"]} looses' for player in self.scoreboard])

        super().update(frame_no)


class MultiplayerScreen(Frame):
    def __init__(self, screen):
        super(MultiplayerScreen, self).__init__(screen, 8, 65)
        self.set_theme('chess')

        layout = Layout([100])
        self.add_layout(layout)

        layout.add_widget(Label('Enter GAME_ID to join or ENEMY_ID to host a game.'))

        self.id_textbox = Text('>', validator=self._validate_id)
        layout.add_widget(self.id_textbox)

        layout.add_widget(Button('join', self._join))
        layout.add_widget(Button('host', self._host))
        layout.add_widget(Button('return', self._return))

        self.fix()

    @staticmethod
    def _validate_id(value):
        try:
            int(value)
            return True
        except:
            return False

    def _join(self):
        if not self.id_textbox.is_valid:
            return

        try:
            global BOARD, USER
            BOARD = GameBoard(RemoteSource(USER, False, int(self.id_textbox.value)))
        except:
            self.scene.add_effect(
                PopUpDialog(self.screen, ' Can\'t join the game. Check GAME_ID. ', ['OK'], has_shadow=True,
                            theme='chess'))
            return

        raise NextScene('Board')

    def _host(self):
        if not self.id_textbox.is_valid:
            return

        try:
            global BOARD, USER
            BOARD = GameBoard(RemoteSource(USER, True, int(self.id_textbox.value)))
        except:
            self.scene.add_effect(
                PopUpDialog(self.screen, ' Can\'t host the game. Check USER_ID. ', ['OK'], has_shadow=True,
                            theme='chess'))
            return

        raise NextScene('Board')

    def _return(self):
        raise NextScene('Main')


class GameScreen(Frame):
    def __init__(self, screen):
        super().__init__(screen, screen.height - 8, screen.width - 20)
        self.set_theme('chess')

        self.turn_start = time.time()

        layout = Layout([2, 1])
        self.add_layout(layout)

        self.title_label = Label('', 1, '^')
        self.board_label = Label('', len(GAME_BOARD.split('\n')), '^')

        layout.add_widget(self.title_label)
        layout.add_widget(self.board_label)

        self.move_textbox = Text('>', validator=self._validate_move, max_length=5)
        layout.add_widget(self.move_textbox, 1)

        self.turn_duration_label = Label('', 1)
        self.current_turn_label = Label('', 1)
        self.history_label = Label('', 12)

        layout.add_widget(self.turn_duration_label, 1)
        layout.add_widget(self.current_turn_label, 1)
        layout.add_widget(self.history_label, 1)

        self.tip_label = Label('', 4)
        layout.add_widget(self.tip_label, 1)

        layout.add_widget(Button('return', self._leave), 1)

        self.ended_games = []

        self.fix()

    @staticmethod
    def _validate_move(value: str):
        value = value.upper()

        if re.match(r'[A-H][1-8] [A-H][1-8]', value) is None:
            return False

        s = value.split()
        chess_yx = s[0]
        move_yx = s[1]

        return BOARD.check_move(chess_yx, move_yx)

    def _make_move(self):
        if not self.move_textbox.is_valid:
            return

        value = self.move_textbox.value.upper()
        self.move_textbox.value = ''

        s = value.split()
        BOARD.make_move(s[0], s[1], time.time() - self.turn_start)
        BOARD.move_checks(s[1])

        self.turn_start = time.time()

    def _leave(self):
        text = 'Do you want to leave the game?'
        if isinstance(BOARD.source, RemoteSource):
            text += ' The game won\'t end, you can rejoin later.'

        text = f' {text} '

        self.scene.add_effect(
            PopUpDialog(self.screen, text, ['YES', 'NO'], on_close=self._leave_confirm, has_shadow=True, theme='chess'))

    def _leave_confirm(self, btn):
        if btn == 1:
            return

        raise NextScene('Main')

    def _on_game_end(self, _):
        raise NextScene('Main')

    def process_event(self, event):
        if event is not None and isinstance(event, KeyboardEvent) and event.key_code == 13:
            self._make_move()
            event = None

        return super().process_event(event)

    def update(self, frame_no):
        # if we start a new game
        if BOARD not in self.ended_games and (BOARD.reset_timer or not BOARD.can_move()):
            for eff in self.scene.effects:
                if isinstance(eff, ParticleEffect):
                    self.scene.remove_effect(eff)

            self.add_effect(Rain(self.screen, 30))

            self.turn_start = time.time()
            BOARD.reset_timer = False

        # next tip
        if frame_no == 1 or frame_no % 100 == 0:
            self.tip_label.text = 'TIP: ' + random.choice(TIPS)
            self.scene.add_effect(
                StarFirework(self.screen, self.screen.width // 4 * 3, self.screen.height // 3 * 2, 40))

        # do not update game if it ended
        if BOARD in self.ended_games:
            self.turn_start = time.time()
            self.tip_label.text = ''
        else:

            if len(self.move_textbox.value) >= 2:
                try:
                    y, x = calculate_yx(self.move_textbox.value[:2])
                    if y in range(8) and x in range(8):
                        self.board_label.text = BOARD.get_field(self.move_textbox.value)
                except:
                    self.board_label.text = BOARD.get_field()
            else:
                self.board_label.text = BOARD.get_field()

        self.current_turn_label.text = 'Current turn: ' + ('WHITE' if BOARD.source.white_turn else 'BLACK')
        self.history_label.text = '\n'.join(BOARD.source.get_history())
        self.turn_duration_label.text = f'Turn duration: {floor(time.time() - self.turn_start):2} s'
        self.move_textbox.readonly = not BOARD.can_move()
        self.title_label.text = BOARD.source.get_title()

        # if someone won
        if BOARD.source.get_white_won() is not None and BOARD not in self.ended_games:
            self.scene.add_effect(
                PopUpDialog(self.screen, (' White' if BOARD.source.get_white_won() else ' Black') + ' wins ', ['OK'],
                            on_close=self._on_game_end, has_shadow=True, theme='chess'))

            self.add_effect(StarFirework(self.screen, self.screen.width // 2 - 20, self.screen.height // 2, 40))
            self.add_effect(StarFirework(self.screen, self.screen.width // 2 + 20, self.screen.height // 2, 40))

            self.ended_games.append(BOARD)

        super().update(frame_no)
