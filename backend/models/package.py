from sqlalchemy import Column, Integer, String, Float, Boolean, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime

from ..database.db_config import Base

class Package(Base):
    __tablename__ = 'packages'
    
    id = Column(Integer, primary_key=True)
    destination = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    price = Column(Float, nullable=False)
    duration = Column(Integer, nullable=False)  # duración en días
    included_services = Column(Text, nullable=True)  # servicios incluidos (hospedaje, transporte, alimentación, etc.)
    images = Column(Text, nullable=True)  # lista de URLs de imágenes separadas por coma
    availability = Column(Boolean, default=True)
    max_travelers = Column(Integer, default=20)  # número máximo de viajeros por fecha
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Campos opcionales para más detalles
    location_coordinates = Column(String(50), nullable=True)  # coordenadas geográficas
    difficulty_level = Column(String(20), nullable=True)  # fácil, moderado, difícil
    recommended_age = Column(String(50), nullable=True)  # rango de edad recomendado
    season = Column(String(50), nullable=True)  # temporada recomendada
    
    # Relaciones
    bookings = relationship("Booking", back_populates="package", cascade="all, delete-orphan")
    reviews = relationship("Review", back_populates="package", cascade="all, delete-orphan")
    
    def __init__(self, destination, description, price, duration, included_services=None, 
                 images=None, availability=True, max_travelers=20):
        self.destination = destination
        self.description = description
        self.price = price
        self.duration = duration
        self.included_services = included_services
        self.images = images
        self.availability = availability
        self.max_travelers = max_travelers
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def to_dict(self):
        return {
            'id': self.id,
            'destination': self.destination,
            'description': self.description,
            'price': self.price,
            'duration': self.duration,
            'included_services': self.included_services,
            'images': self.images.split(',') if self.images else [],
            'availability': self.availability,
            'max_travelers': self.max_travelers,
            'location_coordinates': self.location_coordinates,
            'difficulty_level': self.difficulty_level,
            'recommended_age': self.recommended_age,
            'season': self.season,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def get_average_rating(self):
        if not self.reviews:
            return 0
        return sum(review.rating for review in self.reviews) / len(self.reviews)
    
    def __repr__(self):
        return f"<Package(id={self.id}, destination='{self.destination}', price={self.price})>"