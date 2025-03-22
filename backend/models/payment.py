from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime

from ..database.db_config import Base

class Payment(Base):
    __tablename__ = 'payments'
    
    id = Column(Integer, primary_key=True)
    booking_id = Column(Integer, ForeignKey('bookings.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    amount = Column(Float, nullable=False)
    payment_method = Column(String(50), nullable=False)  # credit_card, paypal, bank_transfer, etc.
    transaction_id = Column(String(100), nullable=True)
    status = Column(String(20), default='pending')  # pending, completed, failed, refunded
    payment_date = Column(DateTime, default=datetime.utcnow)
    card_last_digits = Column(String(4), nullable=True)
    billing_address = Column(String(255), nullable=True)
    
    # Relaciones
    booking = relationship("Booking", back_populates="payments")
    user = relationship("User")
    
    def __init__(self, booking_id, user_id, amount, payment_method, transaction_id=None,
                 status='pending', card_last_digits=None, billing_address=None):
        self.booking_id = booking_id
        self.user_id = user_id
        self.amount = amount
        self.payment_method = payment_method
        self.transaction_id = transaction_id
        self.status = status
        self.payment_date = datetime.utcnow()
        self.card_last_digits = card_last_digits
        self.billing_address = billing_address
    
    def complete_payment(self, transaction_id):
        self.status = 'completed'
        self.transaction_id = transaction_id
        return True
    
    def refund_payment(self):
        if self.status == 'completed':
            self.status = 'refunded'
            return True
        return False
    
    def to_dict(self):
        return {
            'id': self.id,
            'booking_id': self.booking_id,
            'user_id': self.user_id,
            'amount': self.amount,
            'payment_method': self.payment_method,
            'transaction_id': self.transaction_id,
            'status': self.status,
            'payment_date': self.payment_date.isoformat() if self.payment_date else None,
            'card_last_digits': self.card_last_digits,
            'user_name': self.user.name if self.user else None,
            'booking_number': self.booking.booking_number if self.booking else None
        }
    
    def __repr__(self):
        return f"<Payment(id={self.id}, booking_id={self.booking_id}, amount={self.amount}, status='{self.status}')>"