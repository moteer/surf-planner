from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.db import Base

class Tide(Base):
    __tablename__ = "tides"

    id = Column(Integer, primary_key=True, index=True)
    location_id = Column(Integer, ForeignKey("locations.id"), nullable=False)
    timestamp = Column(DateTime, nullable=False)
    height = Column(Float, nullable=False)
    weight = Column(Float, nullable=True)  # Assuming this is a valid field

    # Relationship to Location Model
    location = relationship("Location", back_populates="tides")
