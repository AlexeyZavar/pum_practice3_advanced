from collections import defaultdict

from asciimatics.effects import Print
from asciimatics.particles import StarFirework
from asciimatics.renderers import FigletText, Fire
from asciimatics.scene import Scene
from asciimatics.screen import Screen
from asciimatics.widgets.utilities import THEMES

from screens import MainScreen, GameScreen, MultiplayerScreen, RegisterScreen, ScoreboardScreen


def main(screen: Screen):
    scenes = []

    az = FigletText('Chess by AlexeyZavar', 'banner3')
    fire = Fire(screen.height, screen.width // 2, '*' * 70, 0.6, 60, screen.colours, screen.colours >= 256)
    firework1 = StarFirework(screen, screen.width // 2 - 35, screen.height // 2 - 20, 40)
    firework2 = StarFirework(screen, screen.width // 2 + 35, screen.height // 2 - 20, 40)
    firework3 = StarFirework(screen, screen.width // 2 - 45, screen.height // 2 - 12, 40)
    firework4 = StarFirework(screen, screen.width // 2 + 45, screen.height // 2 - 12, 40)

    effects = [
        Print(screen, fire, 0, speed=0.5, transparent=False),
        firework1, firework2, firework3, firework4,
        Print(screen, az, (screen.height - 4) // 2, speed=1),
    ]
    scenes.append(Scene(effects, 40))

    try:
        screen.play(scenes, repeat=False)
    except KeyboardInterrupt:
        exit(0)

    screen.clear()

    THEMES['chess'] = defaultdict(
        lambda: (Screen.COLOUR_WHITE, Screen.A_BOLD, Screen.COLOUR_BLACK),
        {
            'edit_text': (Screen.COLOUR_GREEN, Screen.A_NORMAL, Screen.COLOUR_BLACK),
            'invalid': (Screen.COLOUR_RED, Screen.A_NORMAL, Screen.COLOUR_BLACK),
            'label': (Screen.COLOUR_WHITE, Screen.A_BOLD, Screen.COLOUR_BLACK),
            'control': (Screen.COLOUR_YELLOW, Screen.A_BOLD, Screen.COLOUR_BLACK),
            'focus_control': (Screen.COLOUR_YELLOW, Screen.A_BOLD, Screen.COLOUR_BLACK),
            'selected_focus_control': (Screen.COLOUR_YELLOW, Screen.A_BOLD, Screen.COLOUR_BLACK),
            'selected_focus_field': (Screen.COLOUR_YELLOW, Screen.A_BOLD, Screen.COLOUR_BLACK),
            'focus_button': (Screen.COLOUR_RED, Screen.A_BOLD, Screen.COLOUR_GREEN),
            'focus_edit_text': (Screen.COLOUR_YELLOW, Screen.A_BOLD, Screen.COLOUR_BLACK),
            'disabled': (Screen.COLOUR_BLACK, Screen.A_BOLD, Screen.COLOUR_BLACK),
        }
    )

    scenes = [
        Scene([RegisterScreen(screen)], -1, name='Register'),
        Scene([ScoreboardScreen(screen)], -1, name='Scoreboard'),
        Scene([MainScreen(screen)], -1, name='Main'),
        Scene([GameScreen(screen)], -1, name='Board'),
        Scene([MultiplayerScreen(screen)], -1, name='Join'),
    ]
    try:
        screen.play(scenes)
    except KeyboardInterrupt:
        exit(0)


if __name__ == '__main__':
    Screen.wrapper(main)
