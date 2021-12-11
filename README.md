# Chess

## Task

Russian full document: [*click*](https://radolyn.com/shared/Models.pdf)

The main goal is to create a chess game that works in a console using unicode symbols. Game board should be stored as a
2 dimensional array.

## Features

- Play with AI
- Play with friends over the network
- Stats synchronization (PvP)
- Scoreboard (PvP)

## Project structure

> backend

FAST API project that stores all user data and allows playing over the network.

> game

Main project that contains game itself.

### game

> main.py

Entry point

> screens.py

File containing main and game frames
