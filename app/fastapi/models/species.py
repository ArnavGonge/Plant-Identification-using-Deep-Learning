from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Species(Base):
    __tablename__ = 'Species_Final'

    Serial_No = Column(Integer, primary_key=True)
    Species_Name = Column(Text)
    Common_name = Column(String(255), nullable=True)
    Uses = Column(Text)

    def __str__(self):
        return self.Species_Name

