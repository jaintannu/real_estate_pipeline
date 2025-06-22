import pandas as pd
from typing import Dict, List, Any, Optional
import logging
import numpy as np
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class DataEnricher:
    """
    Enriches property data with calculated metrics and derived insights
    """
    
    def __init__(self):
        self.current_year = datetime.now().year
    
    def enrich_properties(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Enrich property data with calculated fields and metrics
        """
        if df.empty:
            return df
        
        try:
            # Add calculated fields
            df = self._calculate_price_metrics(df)
            df = self._calculate_property_age(df)
            df = self._calculate_size_metrics(df)
            df = self._add_market_segments(df)
            df = self._calculate_investment_metrics(df)
            df = self._add_location_features(df)
            
            logger.info(f"Enriched {len(df)} properties with calculated metrics")
            return df
            
        except Exception as e:
            logger.error(f"Error enriching property data: {e}")
            return df
    
    def _calculate_price_metrics(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate price-related metrics
        """
        # Price per square foot
        if 'current_price' in df.columns and 'square_feet' in df.columns:
            df['price_per_sqft'] = df.apply(
                lambda row: row['current_price'] / row['square_feet'] 
                if pd.notna(row['current_price']) and pd.notna(row['square_feet']) and row['square_feet'] > 0
                else None, axis=1
            )
        
        # Price categories
        if 'current_price' in df.columns:
            df['price_category'] = df['current_price'].apply(self._categorize_price)
        
        # Price percentiles within city
        if 'current_price' in df.columns and 'city' in df.columns:
            df['price_percentile_city'] = df.groupby('city')['current_price'].rank(pct=True)
        
        return df
    
    def _categorize_price(self, price: float) -> str:
        """
        Categorize property price into segments
        """
        if pd.isna(price):
            return 'unknown'
        
        if price < 200000:
            return 'budget'
        elif price < 500000:
            return 'moderate'
        elif price < 1000000:
            return 'premium'
        elif price < 2000000:
            return 'luxury'
        else:
            return 'ultra_luxury'
    
    def _calculate_property_age(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate property age and age-related metrics
        """
        if 'year_built' in df.columns:
            df['property_age'] = df['year_built'].apply(
                lambda year: self.current_year - year if pd.notna(year) else None
            )
            
            df['age_category'] = df['property_age'].apply(self._categorize_age)
            
            # Renovation likelihood (older properties more likely to need renovation)
            df['renovation_likelihood'] = df['property_age'].apply(
                lambda age: min(1.0, age / 50) if pd.notna(age) else None
            )
        
        return df
    
    def _categorize_age(self, age: float) -> str:
        """
        Categorize property age
        """
        if pd.isna(age):
            return 'unknown'
        
        if age < 5:
            return 'new'
        elif age < 15:
            return 'modern'
        elif age < 30:
            return 'established'
        elif age < 50:
            return 'mature'
        else:
            return 'vintage'
    
    def _calculate_size_metrics(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate size-related metrics
        """
        # Size categories
        if 'square_feet' in df.columns:
            df['size_category'] = df['square_feet'].apply(self._categorize_size)
        
        # Bedrooms per square foot (space efficiency)
        if 'bedrooms' in df.columns and 'square_feet' in df.columns:
            df['space_efficiency'] = df.apply(
                lambda row: row['square_feet'] / row['bedrooms']
                if pd.notna(row['bedrooms']) and pd.notna(row['square_feet']) and row['bedrooms'] > 0
                else None, axis=1
            )
        
        # Lot size to house size ratio
        if 'lot_size' in df.columns and 'square_feet' in df.columns:
            df['lot_to_house_ratio'] = df.apply(
                lambda row: row['lot_size'] / (row['square_feet'] / 43560)  # Convert sqft to acres
                if pd.notna(row['lot_size']) and pd.notna(row['square_feet']) and row['square_feet'] > 0
                else None, axis=1
            )
        
        return df
    
    def _categorize_size(self, sqft: float) -> str:
        """
        Categorize property size
        """
        if pd.isna(sqft):
            return 'unknown'
        
        if sqft < 800:
            return 'compact'
        elif sqft < 1500:
            return 'medium'
        elif sqft < 2500:
            return 'large'
        elif sqft < 4000:
            return 'very_large'
        else:
            return 'mansion'
    
    def _add_market_segments(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Add market segment classifications
        """
        # Family-friendly score
        if 'bedrooms' in df.columns and 'bathrooms' in df.columns:
            df['family_friendly_score'] = df.apply(self._calculate_family_score, axis=1)
        
        # Investment potential score
        df['investment_score'] = df.apply(self._calculate_investment_score, axis=1)
        
        # First-time buyer suitability
        df['first_time_buyer_suitable'] = df.apply(self._is_first_time_buyer_suitable, axis=1)
        
        return df
    
    def _calculate_family_score(self, row: pd.Series) -> float:
        """
        Calculate family-friendly score (0-1)
        """
        score = 0.0
        
        # More bedrooms = more family friendly
        bedrooms = row.get('bedrooms', 0)
        if pd.notna(bedrooms):
            score += min(0.4, bedrooms * 0.1)
        
        # More bathrooms = more family friendly
        bathrooms = row.get('bathrooms', 0)
        if pd.notna(bathrooms):
            score += min(0.3, bathrooms * 0.1)
        
        # Larger size = more family friendly
        sqft = row.get('square_feet', 0)
        if pd.notna(sqft) and sqft > 0:
            score += min(0.3, sqft / 5000)
        
        return min(1.0, score)
    
    def _calculate_investment_score(self, row: pd.Series) -> float:
        """
        Calculate investment potential score (0-1)
        """
        score = 0.0
        
        # Price per sqft efficiency
        price_per_sqft = row.get('price_per_sqft')
        if pd.notna(price_per_sqft):
            # Lower price per sqft can indicate better value
            if price_per_sqft < 150:
                score += 0.3
            elif price_per_sqft < 250:
                score += 0.2
            elif price_per_sqft < 350:
                score += 0.1
        
        # Property age (newer properties might appreciate better)
        age = row.get('property_age')
        if pd.notna(age):
            if age < 10:
                score += 0.2
            elif age < 25:
                score += 0.15
            elif age < 50:
                score += 0.1
        
        # Size considerations
        sqft = row.get('square_feet')
        if pd.notna(sqft):
            if 1200 <= sqft <= 2500:  # Sweet spot for rentability
                score += 0.2
        
        # Bedrooms (2-4 bedrooms are typically most rentable)
        bedrooms = row.get('bedrooms')
        if pd.notna(bedrooms) and 2 <= bedrooms <= 4:
            score += 0.3
        
        return min(1.0, score)
    
    def _is_first_time_buyer_suitable(self, row: pd.Series) -> bool:
        """
        Determine if property is suitable for first-time buyers
        """
        price = row.get('current_price')
        bedrooms = row.get('bedrooms')
        age = row.get('property_age')
        
        # Price threshold (varies by market, using general threshold)
        if pd.notna(price) and price > 600000:
            return False
        
        # Too many bedrooms might be overwhelming/expensive
        if pd.notna(bedrooms) and bedrooms > 4:
            return False
        
        # Very old properties might need too much work
        if pd.notna(age) and age > 80:
            return False
        
        return True
    
    def _calculate_investment_metrics(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate investment-specific metrics
        """
        # Estimated rental yield (simplified calculation)
        if 'current_price' in df.columns:
            df['estimated_monthly_rent'] = df['current_price'].apply(
                lambda price: price * 0.01 / 12 if pd.notna(price) else None  # 1% rule approximation
            )
            
            df['estimated_annual_yield'] = df['current_price'].apply(
                lambda price: 0.08 if pd.notna(price) else None  # Rough 8% yield estimate
            )
        
        # Cash flow potential (simplified)
        if 'estimated_monthly_rent' in df.columns and 'current_price' in df.columns:
            df['monthly_mortgage_estimate'] = df['current_price'].apply(
                lambda price: price * 0.005 if pd.notna(price) else None  # Rough 0.5% of price
            )
            
            df['estimated_cash_flow'] = df.apply(
                lambda row: (row.get('estimated_monthly_rent', 0) - 
                           row.get('monthly_mortgage_estimate', 0) - 500)  # -500 for expenses
                if pd.notna(row.get('estimated_monthly_rent')) and 
                   pd.notna(row.get('monthly_mortgage_estimate'))
                else None, axis=1
            )
        
        return df
    
    def _add_location_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Add location-based features
        """
        # Urban vs suburban classification based on price and size
        if 'price_per_sqft' in df.columns and 'square_feet' in df.columns:
            df['location_type'] = df.apply(self._classify_location_type, axis=1)
        
        # Distance to city center (placeholder - would need actual city center coordinates)
        if 'latitude' in df.columns and 'longitude' in df.columns:
            df['estimated_distance_to_center'] = df.apply(self._estimate_distance_to_center, axis=1)
        
        return df
    
    def _classify_location_type(self, row: pd.Series) -> str:
        """
        Classify location type based on property characteristics
        """
        price_per_sqft = row.get('price_per_sqft')
        sqft = row.get('square_feet')
        
        if pd.isna(price_per_sqft) or pd.isna(sqft):
            return 'unknown'
        
        # High price per sqft + smaller size = urban
        if price_per_sqft > 300 and sqft < 1500:
            return 'urban'
        # Lower price per sqft + larger size = suburban
        elif price_per_sqft < 200 and sqft > 2000:
            return 'suburban'
        # Very low price per sqft + very large = rural
        elif price_per_sqft < 150 and sqft > 3000:
            return 'rural'
        else:
            return 'mixed'
    
    def _estimate_distance_to_center(self, row: pd.Series) -> Optional[str]:
        """
        Estimate distance to city center (placeholder implementation)
        """
        # This would require actual city center coordinates
        # For now, return a placeholder based on price per sqft
        price_per_sqft = row.get('price_per_sqft')
        
        if pd.isna(price_per_sqft):
            return None
        
        if price_per_sqft > 400:
            return 'close'
        elif price_per_sqft > 250:
            return 'moderate'
        else:
            return 'far'
    
    def calculate_market_statistics(self, df: pd.DataFrame, group_by: str = 'city') -> pd.DataFrame:
        """
        Calculate market statistics grouped by specified column
        """
        if df.empty or group_by not in df.columns:
            return pd.DataFrame()
        
        try:
            stats = df.groupby(group_by).agg({
                'current_price': ['count', 'mean', 'median', 'std', 'min', 'max'],
                'price_per_sqft': ['mean', 'median'],
                'square_feet': ['mean', 'median'],
                'bedrooms': ['mean'],
                'property_age': ['mean'],
                'investment_score': ['mean'],
                'family_friendly_score': ['mean']
            }).round(2)
            
            # Flatten column names
            stats.columns = ['_'.join(col).strip() for col in stats.columns.values]
            
            return stats.reset_index()
            
        except Exception as e:
            logger.error(f"Error calculating market statistics: {e}")
            return pd.DataFrame()