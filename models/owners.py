from utils.db import db
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String
from werkzeug.security import generate_password_hash, check_password_hash

class Owners(db.Model):
    __tablename__ = 'owners'
    id_owner: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    mail: Mapped[str] = mapped_column(String(320), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[str] = mapped_column(String(20), nullable=True)
        
    def set_password(self, password):
        """Hashea la contraseña y la guarda en la columna contraseña_hash."""
        self.password = generate_password_hash(password)

    def check_password(self, password):
        """Verifica una contraseña dada contra el hash guardado."""
        return check_password_hash(self.password, password)    
    
    def __repr__(self):
        return f"<Owner id = {self.id_owner}, usuario = {self.username}"