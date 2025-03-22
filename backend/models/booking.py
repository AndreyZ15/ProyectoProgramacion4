from sqlalchemy import Column, Integer, String, Float, Boolean, Text, ForeignKey, DateTime, Date
from sqlalchemy.orm import relationship
from datetime import datetime

from ..database.db_config import Base

class Booking(Base):
    __tablename__ = 'bookings'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    package_id = Column(Integer, ForeignKey('packages.id'), nullable=False)
    travel_date = Column(Date, nullable=False)
    status = Column(String(20), default='pending')  # pending, confirmed, cancelled
    booking_number = Column(String(20), unique=True, nullable=True)
    number_of_travelers = Column(Integer, default=1)
    special_requests = Column(Text, nullable=True)
    total_price = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    priority = Column(Boolean, default=False)  # Para clientes VIP
    
    # Relaciones
    user = relationship("User", back_populates="bookings")
    package = relationship("Package", back_populates="bookings")
    payments = relationship("Payment", back_populates="booking", cascade="all, delete-orphan")
    
    def __init__(self, user_id, package_id, travel_date, status='pending', 
                 number_of_travelers=1, special_requests=None, priority=False):
        self.user_id = user_id
        self.package_id = package_id
        self.travel_date = travel_date
        self.status = status
        self.number_of_travelers = number_of_travelers
        self.special_requests = special_requests
        self.priority = priority
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        self.booking_number = self._generate_booking_number()
    
    def _generate_booking_number(self):
        # Genera un número de reserva único basado en timestamp y otros datos
        timestamp = int(datetime.utcnow().timestamp())
        return f"BK{timestamp}"
    
    def calculate_total_price(self, package_price):
        self.total_price = package_price * self.number_of_travelers
        return self.total_price
    
    def is_fully_paid(self):
        if not self.payments:
            return False
        
        total_paid = sum(payment.amount for payment in self.payments if payment.status == 'completed')
        return total_paid >= self.total_price
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'package_id': self.package_id,
            'travel_date': self.travel_date.isoformat() if self.travel_date else None,
            'status': self.status,
            'booking_number': self.booking_number,
            'number_of_travelers': self.number_of_travelers,
            'special_requests': self.special_requests,
            'total_price': self.total_price,
            'priority': self.priority,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'is_fully_paid': self.is_fully_paid(),
            'user_name': self.user.name if self.user else None,
            'destination': self.package.destination if self.package else None
        }
    
    def __repr__(self):
        return f"<Booking(id={self.id}, booking_number='{self.booking_number}', status='{self.status}')>"