from utils.db import db
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, ForeignKey

class Services(db.Model):
    __tablename__ = 'services'
    id_service: Mapped[int] = mapped_column(primary_key=True)
    id_owner: Mapped[int] = mapped_column(ForeignKey('owners.id_owner'), nullable=False)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[str] = mapped_column(String(500), nullable=True)
    price: Mapped[int] = mapped_column(nullable=False)
    duration: Mapped[int] = mapped_column(nullable=False)
    
    def __repr__(self):
        return f"<Service id = {self.id_service}, nombre = {self.name}, descripcion = {self.description}, precio = {self.price}, duracion = {self.duration}"