import uuid as uuid_module

from sqlalchemy.orm import Session as Db_session
from starlette.responses import JSONResponse

from app.model.dao.deck_model_dao import Session

class SessionHandler:

    async def get_or_create_session_handler(self, db: Db_session, uuid: str) -> JSONResponse:

        session = db.query(Session).filter_by(uuid=uuid).first()
        if session:
            return JSONResponse(content=uuid, status_code=200)

        new_session = Session(uuid=str(uuid_module.uuid4()))
        db.add(new_session)
        db.commit()
        db.refresh(new_session)

        return JSONResponse(content=new_session.uuid, status_code=200)