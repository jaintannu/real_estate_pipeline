import pandas as pd
from typing import Dict, List, Any, Optional
import logging
import re
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError
import time

logger = logging.getLogger(__name__)


class DataNormalizer:
    """
    Normalizes and standardizes real estate data from multiple sources
    """
    
    def __init__(self):
        self.geocoder = Nominatim(user_agent="real_estate_pipeline")
        self.state_abbreviations = {
            'alabama': 'AL', 'alaska': 'AK', 'arizona': 'AZ', 'arkansas': 'AR',
            'california': 'CA', 'colorado': 'CO', 'connecticut': 'CT', 'delaware': 'DE',
            'florida': 'FL', 'georgia': 'GA', 'hawaii': 'HI', 'idaho': 'ID',
            'illinois': 'IL', 'indiana': 'IN', 'iowa': 'IA', 'kansas': 'KS',
            'kentucky': 'KY', 'louisiana': 'LA', 'maine': 'ME', 'maryland': 'MD',
            'massachusetts': 'MA', 'michigan': 'MI', 'minnesota': 'MN', 'mississippi': 'MS',
            'missouri': 'MO', 'montana': 'MT', 'nebraska': 'NE', 'nevada': 'NV',
            'new hampshire': 'NH', 'new jersey': 'NJ', 'new mexico': 'NM', 'new york': 'NY',
            'north carolina': 'NC', 'north dakota': 'ND', 'ohio': 'OH', 'oklahoma': 'OK',
            'oregon': 'OR', 'pennsylvania': 'PA', 'rhode island': 'RI', 'south carolina': 'SC',
            'south dakota': 'SD', 'tennessee': 'TN', 'texas': 'TX', 'utah': 'UT',
            'vermont': 'VT', 'virginia': 'VA', 'washington': 'WA', 'west virginia': 'WV',
            'wisconsin': 'WI', 'wyoming': 'WY'
        }
    
    def normalize_properties_batch(self, properties: List[Dict[str, Any]]) -> pd.DataFrame:
        """
        Normalize a batch of properties and return as DataFrame
        """
        if not properties:
            return pd.DataFrame()
        
        try:
            # Convert to DataFrame for easier processing
            df = pd.DataFrame(properties)
            
            # Apply normalization functions
            df = self._normalize_addresses(df)
            df = self._normalize_property_types(df)
            df = self._normalize_prices(df)
            df = self._normalize_numeric_fields(df)
            df = self._normalize_coordinates(df)
            df = self._validate_data(df)
            
            logger.info(f"Normalized {len(df)} properties")
            return df
            
        except Exception as e:
            logger.error(f"Error normalizing properties batch: {e}")
            return pd.DataFrame()
    
    def _normalize_addresses(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Standardize address formats
        """
        if 'address' in df.columns:
            # Clean and standardize addresses
            df['address'] = df['address'].astype(str).str.strip()
            df['address'] = df['address'].str.replace(r'\s+', ' ', regex=True)  # Multiple spaces to single
            df['address'] = df['address'].str.title()  # Title case
        
        if 'city' in df.columns:
            df['city'] = df['city'].astype(str).str.strip().str.title()
        
        if 'state' in df.columns:
            df['state'] = df['state'].apply(self._normalize_state)
        
        if 'zip_code' in df.columns:
            df['zip_code'] = df['zip_code'].apply(self._normalize_zip_code)
        
        return df
    
    def _normalize_state(self, state: Any) -> Optional[str]:
        """
        Normalize state to 2-letter abbreviation
        """
        if pd.isna(state) or state == '':
            return None
        
        state_str = str(state).strip().lower()
        
        # If already 2-letter abbreviation
        if len(state_str) == 2 and state_str.upper() in self.state_abbreviations.values():
            return state_str.upper()
        
        # If full state name
        if state_str in self.state_abbreviations:
            return self.state_abbreviations[state_str]
        
        # Try partial matching
        for full_name, abbrev in self.state_abbreviations.items():
            if state_str in full_name or full_name in state_str:
                return abbrev
        
        logger.warning(f"Could not normalize state: {state}")
        return str(state).strip().upper()[:2] if state else None
    
    def _normalize_zip_code(self, zip_code: Any) -> Optional[str]:
        """
        Normalize ZIP code format
        """
        if pd.isna(zip_code) or zip_code == '':
            return None
        
        zip_str = str(zip_code).strip()
        
        # Extract 5-digit ZIP code
        zip_match = re.search(r'\b(\d{5})\b', zip_str)
        if zip_match:
            return zip_match.group(1)
        
        return None
    
    def _normalize_property_types(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Standardize property type values
        """
        if 'property_type' not in df.columns:
            return df
        
        type_mapping = {
            'single family': 'house',
            'single-family': 'house',
            'sfh': 'house',
            'detached': 'house',
            'multi family': 'multifamily',
            'multi-family': 'multifamily',
            'duplex': 'multifamily',
            'triplex': 'multifamily',
            'fourplex': 'multifamily',
            'condominium': 'condo',
            'condo': 'condo',
            'townhouse': 'townhome',
            'townhome': 'townhome',
            'apartment': 'apartment',
            'apt': 'apartment',
            'mobile home': 'mobile',
            'manufactured': 'mobile',
            'land': 'lot',
            'vacant land': 'lot'
        }
        
        df['property_type'] = df['property_type'].astype(str).str.lower().str.strip()
        df['property_type'] = df['property_type'].replace(type_mapping)
        
        return df
    
    def _normalize_prices(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Normalize price fields
        """
        price_columns = ['current_price', 'price', 'rent', 'list_price']
        
        for col in price_columns:
            if col in df.columns:
                df[col] = df[col].apply(self._clean_price)
        
        return df
    
    def _clean_price(self, price: Any) -> Optional[float]:
        """
        Clean and convert price to float
        """
        if pd.isna(price) or price == '':
            return None
        
        if isinstance(price, (int, float)):
            return float(price) if price > 0 else None
        
        # Remove currency symbols and commas
        price_str = str(price).replace('$', '').replace(',', '').strip()
        
        try:
            price_float = float(price_str)
            return price_float if price_float > 0 else None
        except (ValueError, TypeError):
            return None
    
    def _normalize_numeric_fields(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Normalize numeric fields and convert NaN to None for JSON compatibility
        """
        numeric_fields = ['bedrooms', 'bathrooms', 'square_feet', 'lot_size', 'year_built']
        
        for field in numeric_fields:
            if field in df.columns:
                df[field] = pd.to_numeric(df[field], errors='coerce')
                
                # Apply reasonable bounds
                if field == 'bedrooms':
                    df[field] = df[field].where((df[field] >= 0) & (df[field] <= 20))
                elif field == 'bathrooms':
                    df[field] = df[field].where((df[field] >= 0) & (df[field] <= 20))
                elif field == 'square_feet':
                    df[field] = df[field].where((df[field] >= 100) & (df[field] <= 50000))
                elif field == 'year_built':
                    df[field] = df[field].where((df[field] >= 1800) & (df[field] <= 2025))
                
                # Convert NaN to None for JSON compatibility
                df[field] = df[field].where(pd.notna(df[field]), None)
        
        return df
    
    def _normalize_coordinates(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Validate and normalize latitude/longitude coordinates
        """
        if 'latitude' in df.columns and 'longitude' in df.columns:
            df['latitude'] = pd.to_numeric(df['latitude'], errors='coerce')
            df['longitude'] = pd.to_numeric(df['longitude'], errors='coerce')
            
            # Validate coordinate ranges for US
            df['latitude'] = df['latitude'].where(
                (df['latitude'] >= 24.0) & (df['latitude'] <= 71.0)
            )
            df['longitude'] = df['longitude'].where(
                (df['longitude'] >= -180.0) & (df['longitude'] <= -66.0)
            )
        
        return df
    
    def _validate_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Perform final data validation
        """
        # Remove rows with missing critical fields
        required_fields = ['address', 'city', 'state']
        for field in required_fields:
            if field in df.columns:
                df = df.dropna(subset=[field])
                df = df[df[field].astype(str).str.strip() != '']
        
        # Remove duplicate addresses
        if all(col in df.columns for col in ['address', 'city', 'state']):
            df = df.drop_duplicates(subset=['address', 'city', 'state'], keep='first')
        
        return df
    
    def geocode_address(self, address: str, city: str, state: str) -> tuple:
        """
        Geocode an address to get latitude/longitude
        """
        try:
            full_address = f"{address}, {city}, {state}"
            location = self.geocoder.geocode(full_address, timeout=10)
            
            if location:
                return location.latitude, location.longitude
            else:
                logger.warning(f"Could not geocode address: {full_address}")
                return None, None
                
        except (GeocoderTimedOut, GeocoderServiceError) as e:
            logger.warning(f"Geocoding service error for {address}: {e}")
            time.sleep(1)  # Rate limiting
            return None, None
        except Exception as e:
            logger.error(f"Unexpected geocoding error for {address}: {e}")
            return None, None