from utils.db import db
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String

class Businesses(db.Model):
    __tablename__ = 'businesses'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    adress: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    mail: Mapped[str] = mapped_column(String(320), unique=True, nullable=False)
    phone: Mapped[str] = mapped_column(String(20), nullable=True)
    
    def __repr__(self):
        return f"<Business id = {self.id}, nombre = {self.name}, direccion = {self.adress}, mail = {self.mail}, telefono = {self.phone}"