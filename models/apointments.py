from utils.db import db
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, ForeignKey

class Apointments(db.Model):
    __tablename__ = 'apointments'
    id_apointment: Mapped[int] = mapped_column(primary_key=True)
    id_service: Mapped[int] = mapped_column(ForeignKey('services.id_service'), nullable=False)
    id_employee: Mapped[int] = mapped_column(ForeignKey('employees.id_employee'), nullable=False)
    id_business: Mapped[int] = mapped_column(ForeignKey('businesses.id_business'), nullable=False)
    time_start: Mapped[str] = mapped_column(nullable=False)
    
    def __repr__(self):
        return f"<Apointments id_apointment = {self.id_apointment}, id_service = {self.id_service}, id_employee = {self.id_employee}, id_business = {self.id_business}, time_start = {self.time_start}"