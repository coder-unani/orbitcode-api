from sqlalchemy import Column, Integer, String, DateTime


from app.database.database import Base 


class AccessLog(Base):
    __tablename__ = 'access_log'

    id = Column(Integer, primary_key=True, index=True)
    status = Column(Integer, nullable=False)
    path = Column(String, nullable=False)
    ip = Column(String, nullable=False)
    user_id = Column(Integer, nullable=True)
    message = Column(String)
    created_at = Column(DateTime)






