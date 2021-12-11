import secrets
import string

from sqlalchemy.orm import Session

from . import models, schemas


def create_user(db: Session, user: schemas.CreateUser):
    db_user = models.User(username=user.username,
                          password=''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(64)),
                          wins=0, looses=0)

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user


def auth_user(db: Session, auth: schemas.Authorize):
    return db.query(models.User).filter(models.User.id == auth.id).filter(models.User.password == auth.password).first()


def get_user(db: Session, id: int):
    return db.query(models.User).get(id)


def get_users(db: Session):
    return db.query(models.User).order_by(-models.User.wins).limit(10).all()
