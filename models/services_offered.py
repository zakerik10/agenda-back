from utils.db import db
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey

class ServicesOffered(db.Model):
    __tablename__ = 'services_offered'
    id_service: Mapped[int] = mapped_column(ForeignKey('services.id_service'), primary_key=True)
    id_employee: Mapped[int] = mapped_column(ForeignKey('employees.id_employee'), primary_key=True)
    
    def __repr__(self):
        return f"<ServiceOffered id_service = {self.id_service}, id_employee = {self.id_employee}"