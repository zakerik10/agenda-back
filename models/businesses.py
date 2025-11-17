from utils.db import db
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, ForeignKey

class Businesses(db.Model):
    __tablename__ = 'businesses'
    id_business: Mapped[int] = mapped_column(primary_key=True)
    id_owner: Mapped[int] = mapped_column(ForeignKey('owners.id_owner'), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    address: Mapped[str] = mapped_column(String(255), nullable=False)
    mail: Mapped[str] = mapped_column(String(320), unique=True, nullable=False)
    phone: Mapped[str] = mapped_column(String(20), nullable=True)
    
    def __repr__(self):
        return f"<Business id = {self.id_business}, nombre = {self.name}, direccion = {self.address}, mail = {self.mail}, telefono = {self.phone}"