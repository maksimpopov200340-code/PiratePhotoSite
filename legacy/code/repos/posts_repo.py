from pydantic import BaseModel
import sqlite3
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

