from utils.db import db
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, ForeignKey

class Clients(db.Model):
    __tablename__ = 'clients'
    id_client: Mapped[int] = mapped_column(primary_key=True)
    id_business: Mapped[int] = mapped_column(ForeignKey('businesses.id_business'), nullable=False)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    surename: Mapped[str] = mapped_column(String(50), nullable=False)
    mail: Mapped[str] = mapped_column(String(320), unique=True, nullable=False)
    phone: Mapped[str] = mapped_column(String(20), nullable=True)
    
    def __repr__(self):
        return f"<User id = {self.id}, nombre = {self.name}, apellido = {self.surename}, mail = {self.mail}, telefono = {self.phone}"