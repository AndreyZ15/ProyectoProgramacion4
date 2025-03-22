from sqlalchemy import Column, Integer, String, Text, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime

from ..database.db_config import Base

class Review(Base):
    __tablename__ = 'reviews'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    package_id = Column(Integer, ForeignKey('packages.id'), nullable=False)
    comment = Column(Text, nullable=False)
    rating = Column(Integer, nullable=False)  # 1-5 estrellas
    date = Column(DateTime, default=datetime.utcnow)
    is_approved = Column(Integer, default=1)  # 0=pendiente, 1=aprobado, 2=rechazado
    
    # Relaciones
    user = relationship("User", back_populates="reviews")
    package = relationship("Package", back_populates="reviews")
    
    def __init__(self, user_id, package_id, comment, rating, date=None, is_approved=1):
        self.user_id = user_id
        self.package_id = package_id
        self.comment = comment
        self.rating = rating
        self.date = date or datetime.utcnow()
        self.is_approved = is_approved
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'user_name': self.user.name if self.user else None,
            'package_id': self.package_id,
            'package_destination': self.package.destination if self.package else None,
            'comment': self.comment,
            'rating': self.rating,
            'date': self.date.isoformat() if self.date else None,
            'is_approved': self.is_approved
        }
    
    def __repr__(self):
        return f"<Review(id={self.id}, user_id={self.user_id}, package_id={self.package_id}, rating={self.rating})>"