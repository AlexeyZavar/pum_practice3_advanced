import sys

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

sys.path.append('..')
sys.path.append('../game')
sys.path.append('../game/src')

from game.src import *
from . import crud, models, schemas
from .database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI(debug=False)


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


GAMES_COUNTER = 0
GAMES_STORAGE: Dict[int, GameBoard] = {}


@app.post('/users/register')
def create_user(user: schemas.CreateUser, db: Session = Depends(get_db)):
    return crud.create_user(db, user)


@app.post('/users/authorize')
def authorize(auth: schemas.Authorize, db: Session = Depends(get_db)):
    return crud.auth_user(db, auth)


@app.get('/users/scoreboard')
def scoreboard(db: Session = Depends(get_db)):
    users = crud.get_users(db)
    return users


@app.post('/games/create')
def create_game(create: schemas.CreateGame, db: Session = Depends(get_db)):
    if create.creator_id == create.enemy_id:
        raise HTTPException(400)

    global GAMES_COUNTER

    player1 = crud.get_user(db, create.creator_id)
    player2 = crud.get_user(db, create.enemy_id)

    GAMES_COUNTER += 1
    id = GAMES_COUNTER

    GAMES_STORAGE[id] = GameBoard(
        LocalSource(Player(create.creator_id, player1.username), Player(create.enemy_id, player2.username)))

    return {'id': id}


@app.get('/games/{game_id}')
def get_game(game: schemas.GetGame, game_id: int):
    field = GAMES_STORAGE[game_id].source.get_field()
    history = GAMES_STORAGE[game_id].source.get_history()
    player1 = GAMES_STORAGE[game_id].source.get_player()
    player2 = GAMES_STORAGE[game_id].source.get_enemy()
    white_turn = GAMES_STORAGE[game_id].source.white_turn
    white_won = GAMES_STORAGE[game_id].source.get_white_won()

    if game.user_id != player1.id and game.user_id != player2.id:
        raise HTTPException(401)

    return {
        'field': field,
        'history': history,
        'player1': player1,
        'player2': player2,
        'white_turn': white_turn,
        'white_won': white_won
    }


@app.post('/games/{game_id}/move')
def make_move(move: schemas.MakeMove, game_id: int, db: Session = Depends(get_db)):
    if GAMES_STORAGE[game_id].source.get_white_won() is not None:
        raise HTTPException(400)

    GAMES_STORAGE[game_id].make_move(move.chess_yx, move.move_yx, move.t)
    GAMES_STORAGE[game_id].move_checks(move.move_yx)

    if GAMES_STORAGE[game_id].source.get_white_won() is not None:
        player1 = crud.get_user(db, GAMES_STORAGE[game_id].source.get_player().id)
        player2 = crud.get_user(db, GAMES_STORAGE[game_id].source.get_enemy().id)

        if GAMES_STORAGE[game_id].source.get_white_won():
            player1.wins += 1
            player2.looses += 1
        else:
            player1.looses += 1
            player2.wins += 1

        db.commit()
