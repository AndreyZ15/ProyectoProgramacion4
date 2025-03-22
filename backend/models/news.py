from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime

from ..database.db_config import Base

class News(Base):
    __tablename__ = 'news'
    
    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    publish_date = Column(DateTime, default=datetime.utcnow)
    image_url = Column(String(255), nullable=True)
    author_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    is_featured = Column(Boolean, default=False)
    is_exclusive = Column(Boolean, default=False)  # Para contenido exclusivo para VIP
    category = Column(String(50), default='general')  # general, destination, events, tips, etc.
    tags = Column(String(255), nullable=True)  # tags separados por coma
    views_count = Column(Integer, default=0)
    
    # Relaciones
    author = relationship("User", back_populates="news")
    
    def __init__(self, title, content, publish_date=None, image_url=None, 
                 author_id=None, is_featured=False, is_exclusive=False, 
                 category='general', tags=None):
        self.title = title
        self.content = content
        self.publish_date = publish_date or datetime.utcnow()
        self.image_url = image_url
        self.author_id = author_id
        self.is_featured = is_featured
        self.is_exclusive = is_exclusive
        self.category = category
        self.tags = tags
        self.views_count = 0
    
    def increment_views(self):
        self.views_count += 1
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'publish_date': self.publish_date.isoformat() if self.publish_date else None,
            'image_url': self.image_url,
            'author_id': self.author_id,
            'author_name': self.author.name if self.author else None,
            'is_featured': self.is_featured,
            'is_exclusive': self.is_exclusive,
            'category': self.category,
            'tags': self.tags.split(',') if self.tags else [],
            'views_count': self.views_count
        }
    
    def get_preview(self, chars=150):
        """Retorna una vista previa del contenido limitada por cantidad de caracteres"""
        if len(self.content) <= chars:
            return self.content
        return self.content[:chars] + '...'
    
    def __repr__(self):
        return f"<News(id={self.id}, title='{self.title}', category='{self.category}')>"