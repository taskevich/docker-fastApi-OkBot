from sqlalchemy.orm import Session
from ..db.models import Events


def create_log(ids: str, type_action: str, db: Session):
    _event = Events(target_id=ids, type_action=type_action)
    db.add(_event)
    db.commit()
    db.refresh(_event)
    return _event