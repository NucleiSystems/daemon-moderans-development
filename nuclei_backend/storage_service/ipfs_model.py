from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID

from ..database import Base


class DataStorage(Base):
    # The DataStorage class is a table that stores data about files.
    __tablename__ = "data_storage"

    id = Column(Integer, primary_key=True, index=True)
    file_name = Column(String)
    file_cid = Column(String)
    file_hash = Column(String)
    file_size = Column(Integer)
    file_type = Column(String)
    file_upload_date = Column(String)

    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    owner = relationship("User", back_populates="data")
