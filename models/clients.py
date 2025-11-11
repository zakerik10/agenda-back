from utils.db import db
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String
from werkzeug.security import generate_password_hash, check_password_hash

class Users(db.Model):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    surename: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    mail: Mapped[str] = mapped_column(String(320), unique=True, nullable=False)
    phone: Mapped[str] = mapped_column(String(20), nullable=True)
    
    def __repr__(self):
        return f"<User id = {self.id}, nombre = {self.name}, apellido = {self.surename}, mail = {self.mail}, telefono = {self.phone}"