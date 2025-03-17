import uuid as uuid_module

from sqlalchemy.orm import Session as Db_session
from starlette.responses import JSONResponse

from app.model.dao.deck_model_dao import Session

class SessionHandler:

    async def get_or_create_session_handler(self, db: Db_session, session_uuid: str) -> JSONResponse:

        session = db.query(Session).filter_by(session_uuid=session_uuid).first()
        if session:
            return JSONResponse(content=session_uuid, status_code=200)

        new_session = Session(session_uuid=str(uuid_module.uuid4()))
        db.add(new_session)
        db.commit()
        db.refresh(new_session)

        return JSONResponse(content=new_session.session_uuid, status_code=200)