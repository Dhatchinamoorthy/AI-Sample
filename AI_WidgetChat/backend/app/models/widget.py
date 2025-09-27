from sqlalchemy import Column, Integer, String, Text, DateTime, JSON
from sqlalchemy.sql import func
from app.database import Base


class WidgetConfig(Base):
    __tablename__ = "widget_configs"
    
    id = Column(Integer, primary_key=True, index=True)
    widget_type = Column(String(100), nullable=False, index=True)
    user_id = Column(String(255), nullable=True, index=True)
    config = Column(JSON, nullable=False)  # Widget configuration as JSON
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class WidgetCache(Base):
    __tablename__ = "widget_cache"
    
    id = Column(Integer, primary_key=True, index=True)
    widget_type = Column(String(100), nullable=False, index=True)
    cache_key = Column(String(500), nullable=False, index=True)
    data = Column(JSON, nullable=False)  # Cached widget data as JSON
    expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
