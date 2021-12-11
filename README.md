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

Entry point; Startup animation.

> screens.py

Main and game frames

> .user & .user2

User data (to change user, set 'SECOND_USER' env variable).

> consts.py

Backend url and symbols for game.

> gameboard.py

Proxy between a screen and game source. Contains all checks for pieces.

> sources.py

Games sources:

- **LocalSource** (PvP on the computer)
- **LocalAISource** (PvE on the computer)
- **RemoteSource** (PvP on remote)

> utils.py

**calculate_yx** — converter between user input and array accessors.

### backend

> main.py

Entry point; run with unicorn.

> models.py

Database models.

> schemas.py

Pydantic classes for requests.

> database.py

Database connector.

> crud.py

All the CRUD operations.
