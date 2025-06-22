import pandas as pd
from typing import Dict, List, Any, Tuple
import logging
from difflib import SequenceMatcher
import re
from geopy.distance import geodesic

logger = logging.getLogger(__name__)


class DuplicateHandler:
    """
    Handles detection and resolution of duplicate properties from multiple sources
    """
    
    def __init__(self, address_threshold: float = 0.85, coordinate_threshold: float = 0.1):
        self.address_threshold = address_threshold  # Similarity threshold for addresses
        self.coordinate_threshold = coordinate_threshold  # Distance threshold in km
    
    def find_duplicates(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Find and mark duplicate properties in the DataFrame
        """
        if df.empty:
            return df
        
        try:
            # Add duplicate group column
            df['duplicate_group'] = None
            df['is_duplicate'] = False
            df['duplicate_confidence'] = 0.0
            
            # Find duplicates using multiple methods
            df = self._find_address_duplicates(df)
            df = self._find_coordinate_duplicates(df)
            df = self._find_fuzzy_duplicates(df)
            
            # Resolve conflicts and merge data
            df = self._resolve_duplicates(df)
            
            duplicate_count = df['is_duplicate'].sum()
            logger.info(f"Found {duplicate_count} duplicate properties out of {len(df)}")
            
            return df
            
        except Exception as e:
            logger.error(f"Error finding duplicates: {e}")
            return df
    
    def _find_address_duplicates(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Find exact address matches
        """
        if not all(col in df.columns for col in ['address', 'city', 'state']):
            return df
        
        # Create normalized address key
        df['_address_key'] = (
            df['address'].astype(str).str.lower().str.strip() + '|' +
            df['city'].astype(str).str.lower().str.strip() + '|' +
            df['state'].astype(str).str.upper().str.strip()
        )
        
        # Find duplicates
        duplicate_mask = df.duplicated(subset=['_address_key'], keep=False)
        
        if duplicate_mask.any():
            # Assign group IDs to duplicates
            for address_key in df[duplicate_mask]['_address_key'].unique():
                mask = df['_address_key'] == address_key
                group_id = f"addr_{hash(address_key) % 10000}"
                df.loc[mask, 'duplicate_group'] = group_id
                df.loc[mask, 'is_duplicate'] = True
                df.loc[mask, 'duplicate_confidence'] = 1.0
        
        # Clean up temporary column
        df = df.drop('_address_key', axis=1)
        
        return df
    
    def _find_coordinate_duplicates(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Find properties with very close coordinates
        """
        if not all(col in df.columns for col in ['latitude', 'longitude']):
            return df
        
        # Filter rows with valid coordinates
        coord_df = df.dropna(subset=['latitude', 'longitude']).copy()
        
        if len(coord_df) < 2:
            return df
        
        # Compare each pair of coordinates
        for i, row1 in coord_df.iterrows():
            if df.loc[i, 'is_duplicate']:
                continue  # Already marked as duplicate
            
            coord1 = (row1['latitude'], row1['longitude'])
            
            for j, row2 in coord_df.iterrows():
                if i >= j or df.loc[j, 'is_duplicate']:
                    continue
                
                coord2 = (row2['latitude'], row2['longitude'])
                
                try:
                    distance = geodesic(coord1, coord2).kilometers
                    
                    if distance <= self.coordinate_threshold:
                        # Check if addresses are similar too
                        addr_similarity = self._calculate_address_similarity(
                            row1.get('address', ''), row2.get('address', '')
                        )
                        
                        if addr_similarity > 0.7:  # Lower threshold for coordinate matches
                            group_id = f"coord_{i}_{j}"
                            df.loc[i, 'duplicate_group'] = group_id
                            df.loc[j, 'duplicate_group'] = group_id
                            df.loc[i, 'is_duplicate'] = True
                            df.loc[j, 'is_duplicate'] = True
                            confidence = min(0.9, 0.5 + addr_similarity * 0.4)
                            df.loc[i, 'duplicate_confidence'] = max(df.loc[i, 'duplicate_confidence'], confidence)
                            df.loc[j, 'duplicate_confidence'] = max(df.loc[j, 'duplicate_confidence'], confidence)
                            
                except Exception as e:
                    logger.warning(f"Error calculating distance between coordinates: {e}")
                    continue
        
        return df
    
    def _find_fuzzy_duplicates(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Find duplicates using fuzzy string matching
        """
        if 'address' not in df.columns:
            return df
        
        # Only check non-duplicate rows
        non_duplicate_df = df[~df['is_duplicate']].copy()
        
        if len(non_duplicate_df) < 2:
            return df
        
        for i, row1 in non_duplicate_df.iterrows():
            for j, row2 in non_duplicate_df.iterrows():
                if i >= j:
                    continue
                
                # Calculate address similarity
                addr_similarity = self._calculate_address_similarity(
                    row1.get('address', ''), row2.get('address', '')
                )
                
                # Calculate city similarity
                city_similarity = self._calculate_string_similarity(
                    row1.get('city', ''), row2.get('city', '')
                )
                
                # Combined similarity score
                combined_similarity = (addr_similarity * 0.8 + city_similarity * 0.2)
                
                if combined_similarity >= self.address_threshold:
                    # Additional checks for property characteristics
                    char_similarity = self._calculate_property_similarity(row1, row2)
                    final_confidence = (combined_similarity * 0.7 + char_similarity * 0.3)
                    
                    if final_confidence >= 0.75:
                        group_id = f"fuzzy_{i}_{j}"
                        df.loc[i, 'duplicate_group'] = group_id
                        df.loc[j, 'duplicate_group'] = group_id
                        df.loc[i, 'is_duplicate'] = True
                        df.loc[j, 'is_duplicate'] = True
                        df.loc[i, 'duplicate_confidence'] = max(df.loc[i, 'duplicate_confidence'], final_confidence)
                        df.loc[j, 'duplicate_confidence'] = max(df.loc[j, 'duplicate_confidence'], final_confidence)
        
        return df
    
    def _calculate_address_similarity(self, addr1: str, addr2: str) -> float:
        """
        Calculate similarity between two addresses
        """
        if not addr1 or not addr2:
            return 0.0
        
        # Normalize addresses
        addr1_norm = self._normalize_address_for_comparison(addr1)
        addr2_norm = self._normalize_address_for_comparison(addr2)
        
        return SequenceMatcher(None, addr1_norm, addr2_norm).ratio()
    
    def _normalize_address_for_comparison(self, address: str) -> str:
        """
        Normalize address for comparison
        """
        if not address:
            return ""
        
        # Convert to lowercase and remove extra spaces
        normalized = address.lower().strip()
        
        # Replace common abbreviations
        replacements = {
            r'\bstreet\b': 'st',
            r'\bavenue\b': 'ave',
            r'\bboulevard\b': 'blvd',
            r'\bdrive\b': 'dr',
            r'\broad\b': 'rd',
            r'\blane\b': 'ln',
            r'\bcourt\b': 'ct',
            r'\bplace\b': 'pl',
            r'\bapartment\b': 'apt',
            r'\bunit\b': 'apt',
            r'\bnorth\b': 'n',
            r'\bsouth\b': 's',
            r'\beast\b': 'e',
            r'\bwest\b': 'w'
        }
        
        for pattern, replacement in replacements.items():
            normalized = re.sub(pattern, replacement, normalized)
        
        # Remove punctuation and extra spaces
        normalized = re.sub(r'[^\w\s]', '', normalized)
        normalized = re.sub(r'\s+', ' ', normalized).strip()
        
        return normalized
    
    def _calculate_string_similarity(self, str1: str, str2: str) -> float:
        """
        Calculate similarity between two strings
        """
        if not str1 or not str2:
            return 0.0
        
        str1_norm = str1.lower().strip()
        str2_norm = str2.lower().strip()
        
        return SequenceMatcher(None, str1_norm, str2_norm).ratio()
    
    def _calculate_property_similarity(self, prop1: pd.Series, prop2: pd.Series) -> float:
        """
        Calculate similarity based on property characteristics
        """
        similarities = []
        
        # Compare numeric fields
        numeric_fields = ['bedrooms', 'bathrooms', 'square_feet', 'year_built']
        
        for field in numeric_fields:
            val1 = prop1.get(field)
            val2 = prop2.get(field)
            
            if pd.notna(val1) and pd.notna(val2):
                if val1 == val2:
                    similarities.append(1.0)
                elif field == 'square_feet':
                    # Allow 10% difference for square footage
                    diff_ratio = abs(val1 - val2) / max(val1, val2)
                    similarities.append(max(0, 1 - diff_ratio * 2))
                elif field == 'year_built':
                    # Allow 2 year difference
                    diff = abs(val1 - val2)
                    similarities.append(max(0, 1 - diff / 10))
                else:
                    similarities.append(0.5 if abs(val1 - val2) <= 1 else 0.0)
        
        # Compare property type
        type1 = prop1.get('property_type', '')
        type2 = prop2.get('property_type', '')
        if type1 and type2:
            similarities.append(1.0 if type1.lower() == type2.lower() else 0.0)
        
        return sum(similarities) / len(similarities) if similarities else 0.0
    
    def _resolve_duplicates(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Resolve duplicates by merging data and keeping the best record
        """
        if not df['is_duplicate'].any():
            return df
        
        # Group duplicates and merge data
        duplicate_groups = df[df['is_duplicate']]['duplicate_group'].unique()
        
        for group_id in duplicate_groups:
            if pd.isna(group_id):
                continue
            
            group_mask = df['duplicate_group'] == group_id
            group_df = df[group_mask].copy()
            
            if len(group_df) <= 1:
                continue
            
            # Choose the best record (highest confidence, most complete data)
            best_idx = self._choose_best_record(group_df)
            
            # Merge data from other records
            merged_record = self._merge_duplicate_records(group_df, best_idx)
            
            # Update the best record with merged data
            for col, value in merged_record.items():
                if col in df.columns:
                    df.loc[best_idx, col] = value
            
            # Mark other records for removal
            other_indices = group_df.index[group_df.index != best_idx]
            df.loc[other_indices, 'is_duplicate'] = True
            df.loc[best_idx, 'is_duplicate'] = False  # Keep the best one
        
        return df
    
    def _choose_best_record(self, group_df: pd.DataFrame) -> int:
        """
        Choose the best record from a group of duplicates
        """
        # Score each record based on completeness and confidence
        scores = []
        
        for idx, row in group_df.iterrows():
            score = 0
            
            # Confidence score
            score += row.get('duplicate_confidence', 0) * 10
            
            # Completeness score
            important_fields = ['address', 'city', 'state', 'latitude', 'longitude', 
                              'bedrooms', 'bathrooms', 'square_feet', 'current_price']
            
            for field in important_fields:
                if field in row and pd.notna(row[field]) and row[field] != '':
                    score += 1
            
            # Prefer records with more recent data
            if 'updated_at' in row and pd.notna(row['updated_at']):
                score += 5
            
            scores.append((idx, score))
        
        # Return index of record with highest score
        return max(scores, key=lambda x: x[1])[0]
    
    def _merge_duplicate_records(self, group_df: pd.DataFrame, best_idx: int) -> Dict[str, Any]:
        """
        Merge data from duplicate records
        """
        best_record = group_df.loc[best_idx].to_dict()
        
        # Merge data from other records
        for idx, row in group_df.iterrows():
            if idx == best_idx:
                continue
            
            for col, value in row.items():
                # Skip metadata columns
                if col in ['duplicate_group', 'is_duplicate', 'duplicate_confidence']:
                    continue
                
                # If best record is missing this value, use from other record
                if (pd.isna(best_record.get(col)) or best_record.get(col) == '') and \
                   (pd.notna(value) and value != ''):
                    best_record[col] = value
        
        return best_record
    
    def remove_duplicates(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Remove duplicate records, keeping only the best ones
        """
        if 'is_duplicate' not in df.columns:
            df = self.find_duplicates(df)
        
        # Remove records marked as duplicates
        cleaned_df = df[~df['is_duplicate']].copy()
        
        # Clean up duplicate detection columns
        columns_to_drop = ['duplicate_group', 'is_duplicate', 'duplicate_confidence']
        cleaned_df = cleaned_df.drop(columns=[col for col in columns_to_drop if col in cleaned_df.columns])
        
        removed_count = len(df) - len(cleaned_df)
        logger.info(f"Removed {removed_count} duplicate records, kept {len(cleaned_df)} unique properties")
        
        return cleaned_df