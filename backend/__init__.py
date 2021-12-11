import secrets
import string

from sqlalchemy.orm import Session

from . import models, schemas


def create_user(db: Session, username: str):
    password = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(64))

    user = models.User(username=username, password=password)
    db.add(user)
    db.commit()
    db.refresh(user)

    return user
