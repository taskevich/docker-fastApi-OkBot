from sqlalchemy.orm import Session
from ..db.models import Bots


def create_new_bot(name: str, account_id: int, db: Session):
    _bot = Bots(
        name=name,
        account_id=account_id,
    )
    db.add(_bot)
    db.commit()
    db.refresh(_bot)
    return _bot


def get_bot_by_id(db: Session, id: int):
    return db.query(Bots).filter(Bots.id == id).first()


def get_all_bots(db: Session):
    return db.query(Bots).all()


def get_count_bots(db: Session):
    return db.query(Bots).count()


def update_bot_active(id: int, db: Session, is_active: bool = False):
    _bot = get_bot_by_id(db, id)
    _bot.is_active = is_active
    db.commit()
    db.refresh(_bot)
    return _bot
    

def delete_bot_by_accout_id(db: Session, id: int):
    _bot = db.query(Bots).filter(Bots.account_id == id).delete(synchronize_session=False)
    db.commit()
    return True