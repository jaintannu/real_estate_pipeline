from sqlalchemy import Column, String, Integer, DateTime, Text, Boolean, ForeignKey
from sqlalchemy.types import Numeric
from sqlalchemy.dialects.postgresql import UUID, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import uuid


class Property(Base):
    __tablename__ = "properties"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    address = Column(String(500), nullable=False, index=True)
    city = Column(String(100), nullable=False, index=True)
    state = Column(String(2), nullable=False, index=True)
    zip_code = Column(String(10), nullable=True, index=True)
    latitude = Column(Numeric(10, 8), nullable=True)
    longitude = Column(Numeric(11, 8), nullable=True)
    
    # Property details
    property_type = Column(String(50), nullable=True, index=True)  # house, condo, apartment, etc.
    bedrooms = Column(Integer, nullable=True)
    bathrooms = Column(Integer, nullable=True)
    square_feet = Column(Integer, nullable=True)
    lot_size = Column(Numeric(10, 2), nullable=True)  # in acres
    year_built = Column(Integer, nullable=True)
    
    # Financial information
    current_price = Column(Numeric(12, 2), nullable=True)
    listing_status = Column(String(50), nullable=True, index=True)  # active, sold, pending, etc.
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    history = relationship("PropertyHistory", back_populates="property", cascade="all, delete-orphan")
    features = relationship("PropertyFeature", back_populates="property", cascade="all, delete-orphan")
    api_sources = relationship("ApiSource", back_populates="property", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Property(id={self.id}, address='{self.address}', city='{self.city}')>"


class PropertyHistory(Base):
    __tablename__ = "property_history"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    property_id = Column(UUID(as_uuid=True), ForeignKey("properties.id"), nullable=False)
    price = Column(Numeric(12, 2), nullable=False)
    event_type = Column(String(50), nullable=False)  # listing, sale, price_change, etc.
    event_date = Column(DateTime(timezone=True), nullable=False)
    source = Column(String(100), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    property = relationship("Property", back_populates="history")
    
    def __repr__(self):
        return f"<PropertyHistory(property_id={self.property_id}, price={self.price}, event_type='{self.event_type}')>"


class PropertyFeature(Base):
    __tablename__ = "property_features"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    property_id = Column(UUID(as_uuid=True), ForeignKey("properties.id"), nullable=False)
    feature_type = Column(String(100), nullable=False)  # amenity, appliance, etc.
    feature_value = Column(Text, nullable=False)
    source = Column(String(100), nullable=True)
    
    # Relationships
    property = relationship("Property", back_populates="features")
    
    def __repr__(self):
        return f"<PropertyFeature(property_id={self.property_id}, type='{self.feature_type}', value='{self.feature_value}')>"


class ApiSource(Base):
    __tablename__ = "api_sources"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    property_id = Column(UUID(as_uuid=True), ForeignKey("properties.id"), nullable=False)
    api_name = Column(String(100), nullable=False, index=True)
    external_id = Column(String(200), nullable=True)
    raw_data = Column(JSON, nullable=True)
    last_updated = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    property = relationship("Property", back_populates="api_sources")
    
    def __repr__(self):
        return f"<ApiSource(property_id={self.property_id}, api_name='{self.api_name}', external_id='{self.external_id}')>"