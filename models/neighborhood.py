from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.types import Numeric
from sqlalchemy.dialects.postgresql import UUID, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import uuid


class State(Base):
    __tablename__ = "states"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False, unique=True)
    abbreviation = Column(String(2), nullable=False, unique=True, index=True)
    market_data = Column(JSON, nullable=True)  # General state-level market information
    
    # Relationships
    cities = relationship("City", back_populates="state", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<State(name='{self.name}', abbreviation='{self.abbreviation}')>"


class City(Base):
    __tablename__ = "cities"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False, index=True)
    state_id = Column(UUID(as_uuid=True), ForeignKey("states.id"), nullable=False)
    median_home_price = Column(Numeric(12, 2), nullable=True)
    population = Column(Integer, nullable=True)
    market_trends = Column(JSON, nullable=True)  # Market trend data
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    state = relationship("State", back_populates="cities")
    neighborhoods = relationship("Neighborhood", back_populates="city", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<City(name='{self.name}', state_id={self.state_id})>"


class Neighborhood(Base):
    __tablename__ = "neighborhoods"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(200), nullable=False, index=True)
    city_id = Column(UUID(as_uuid=True), ForeignKey("cities.id"), nullable=False)
    
    # Market data
    avg_home_price = Column(Numeric(12, 2), nullable=True)
    median_home_price = Column(Numeric(12, 2), nullable=True)
    price_per_sqft = Column(Numeric(8, 2), nullable=True)
    
    # Walkability and transportation
    walk_score = Column(Integer, nullable=True)  # 0-100 walkability score
    transit_score = Column(Integer, nullable=True)  # 0-100 transit score
    bike_score = Column(Integer, nullable=True)  # 0-100 bike score
    
    # Safety and demographics
    crime_rate = Column(Numeric(8, 4), nullable=True)  # Crime incidents per 1000 residents
    demographics = Column(JSON, nullable=True)  # Age, income, education demographics
    
    # Amenities and features
    school_rating = Column(Numeric(3, 1), nullable=True)  # Average school rating
    amenities = Column(JSON, nullable=True)  # Parks, restaurants, shopping, etc.
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    city = relationship("City", back_populates="neighborhoods")
    
    def __repr__(self):
        return f"<Neighborhood(name='{self.name}', city_id={self.city_id})>"


class MarketTrend(Base):
    __tablename__ = "market_trends"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    location_type = Column(String(20), nullable=False)  # 'city', 'neighborhood', 'state'
    location_id = Column(UUID(as_uuid=True), nullable=False)  # References city, neighborhood, or state
    
    # Trend data
    period = Column(String(20), nullable=False)  # 'monthly', 'quarterly', 'yearly'
    trend_date = Column(DateTime(timezone=True), nullable=False)
    median_price = Column(Numeric(12, 2), nullable=True)
    avg_price = Column(Numeric(12, 2), nullable=True)
    price_change_percent = Column(Numeric(5, 2), nullable=True)  # Month-over-month or year-over-year
    inventory_count = Column(Integer, nullable=True)
    days_on_market = Column(Integer, nullable=True)
    
    # Additional metrics
    sales_volume = Column(Integer, nullable=True)
    price_per_sqft = Column(Numeric(8, 2), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<MarketTrend(location_type='{self.location_type}', location_id={self.location_id}, period='{self.period}')>"