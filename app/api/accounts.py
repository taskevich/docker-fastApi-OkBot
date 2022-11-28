from ..core.config import get_db, SessionLocal
from sqlalchemy.orm import Session
from ..db.models import Accounts


def create_new_account(login: str, password: str, db: Session):
    _account = Accounts(login=login,
                        password=password)
    db.add(_account)
    db.commit()
    db.refresh(_account)
    return _account


def get_account_by_id(db: Session, id: int):
    return db.query(Accounts).filter(Accounts.id == id).first()


def delete_account_by_id(db: Session, id: int):
    _account = db.query(Accounts).filter(Accounts.id == id).delete(synchronize_session=False)
    db.commit()
    return True


def get_all_accounts():
    db = SessionLocal()
    return db.query(Accounts).all()


def get_account_by_login(db: Session, login: str):
    return db.query(Accounts).filter(Accounts.login == login).first()