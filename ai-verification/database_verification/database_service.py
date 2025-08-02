"""
Database Verification Service for cross-checking with government databases
"""
import time
import hashlib
import requests
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from loguru import logger

from ..models.schemas import (
    DatabaseVerificationResult, DatabaseRecord, FieldMatch
)
from ..config.settings import settings


class DatabaseVerificationService:
    """Database verification service for identity cross-checking"""
    
    def __init__(self):
        self.cache = {}  # Simple in-memory cache
        self.cache_ttl = timedelta(hours=24)  # Cache for 24 hours
        logger.info("Database verification service initialized")
    
    def verify_identity(
        self,
        nric: str,
        name: str,
        date_of_birth: Optional[str] = None
    ) -> DatabaseVerificationResult:
        """
        Verify identity against government databases
        
        Args:
            nric: NRIC number
            name: Full name
            date_of_birth: Date of birth (optional)
            
        Returns:
            Database verification result
        """
        start_time = time.time()
        
        try:
            # Check cache first
            cache_key = self._generate_cache_key(nric, name, date_of_birth)
            cached_result = self._get_cached_result(cache_key)
            
            if cached_result:
                logger.info(f"Using cached result for NRIC: {nric[:4]}****")
                return cached_result
            
            # Perform verification checks
            verification_results = []
            
            # 1. Government Registry Check
            gov_result = self._check_government_registry(nric, name, date_of_birth)
            if gov_result:
                verification_results.append(gov_result)
            
            # 2. Identity Database Check
            identity_result = self._check_identity_database(nric, name, date_of_birth)
            if identity_result:
                verification_results.append(identity_result)
            
            # 3. Blacklist Check
            blacklist_clear = self._check_blacklist(nric, name)
            
            # 4. Sanctions Check
            sanctions_clear = self._check_sanctions_list(name, date_of_birth)
            
            # Determine overall verification status
            verification_status = self._determine_verification_status(verification_results)
            
            # Check if identity is valid
            is_valid = (
                verification_status in ["verified", "partial_match"] and
                blacklist_clear and
                sanctions_clear and
                len(verification_results) > 0
            )
            
            processing_time = time.time() - start_time
            
            result = DatabaseVerificationResult(
                success=True,
                is_valid=is_valid,
                verification_status=verification_status,
                matched_records=verification_results,
                blacklist_check=blacklist_clear,
                sanctions_check=sanctions_clear,
                processing_time=processing_time
            )
            
            # Cache the result
            self._cache_result(cache_key, result)
            
            logger.info(f"Database verification completed for NRIC: {nric[:4]}**** - Status: {verification_status}")
            return result
            
        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(f"Error in database verification: {e}")
            
            return DatabaseVerificationResult(
                success=False,
                is_valid=False,
                verification_status="error",
                matched_records=[],
                blacklist_check=False,
                sanctions_check=False,
                processing_time=processing_time
            )
    
    def _check_government_registry(
        self,
        nric: str,
        name: str,
        date_of_birth: Optional[str]
    ) -> Optional[DatabaseRecord]:
        """
        Check against Singapore government registry
        
        Args:
            nric: NRIC number
            name: Full name
            date_of_birth: Date of birth
            
        Returns:
            Database record if found, None otherwise
        """
        try:
            # In a real implementation, this would call actual government APIs
            # For simulation, we'll create mock responses based on NRIC validity
            
            logger.debug(f"Checking government registry for NRIC: {nric[:4]}****")
            
            # Simulate API call delay
            time.sleep(0.1)
            
            # Validate NRIC format first
            if not self._validate_nric_format(nric):
                return None
            
            # Mock government database response
            # In reality, this would be an authenticated API call
            mock_gov_data = self._simulate_government_response(nric, name, date_of_birth)
            
            if mock_gov_data:
                # Create field matches
                field_matches = []
                
                # Name match
                name_similarity = self._calculate_name_similarity(name, mock_gov_data["name"])
                field_matches.append(FieldMatch(
                    field="name",
                    input_value=name,
                    database_value=mock_gov_data["name"],
                    is_match=name_similarity > 0.8,
                    confidence=name_similarity
                ))
                
                # NRIC match (exact)
                field_matches.append(FieldMatch(
                    field="nric",
                    input_value=nric,
                    database_value=mock_gov_data["nric"],
                    is_match=nric.upper() == mock_gov_data["nric"].upper(),
                    confidence=1.0 if nric.upper() == mock_gov_data["nric"].upper() else 0.0
                ))
                
                # Date of birth match (if provided)
                if date_of_birth and mock_gov_data.get("date_of_birth"):
                    dob_match = self._compare_dates(date_of_birth, mock_gov_data["date_of_birth"])
                    field_matches.append(FieldMatch(
                        field="date_of_birth",
                        input_value=date_of_birth,
                        database_value=mock_gov_data["date_of_birth"],
                        is_match=dob_match,
                        confidence=1.0 if dob_match else 0.0
                    ))
                
                # Calculate overall match score
                match_score = sum(fm.confidence for fm in field_matches) / len(field_matches)
                
                return DatabaseRecord(
                    source="government_registry",
                    match_score=match_score,
                    field_matches=field_matches,
                    last_updated=datetime.utcnow()
                )
            
            return None
            
        except Exception as e:
            logger.error(f"Error checking government registry: {e}")
            return None
    
    def _check_identity_database(
        self,
        nric: str,
        name: str,
        date_of_birth: Optional[str]
    ) -> Optional[DatabaseRecord]:
        """
        Check against identity verification database
        
        Args:
            nric: NRIC number
            name: Full name
            date_of_birth: Date of birth
            
        Returns:
            Database record if found, None otherwise
        """
        try:
            logger.debug(f"Checking identity database for NRIC: {nric[:4]}****")
            
            # Simulate identity database check
            time.sleep(0.05)
            
            # Mock identity database response
            mock_identity_data = self._simulate_identity_database_response(nric, name)
            
            if mock_identity_data:
                field_matches = []
                
                # Name fuzzy match
                name_similarity = self._calculate_name_similarity(name, mock_identity_data["name"])
                field_matches.append(FieldMatch(
                    field="name",
                    input_value=name,
                    database_value=mock_identity_data["name"],
                    is_match=name_similarity > 0.7,
                    confidence=name_similarity
                ))
                
                # NRIC match
                nric_match = nric.upper() == mock_identity_data["nric"].upper()
                field_matches.append(FieldMatch(
                    field="nric",
                    input_value=nric,
                    database_value=mock_identity_data["nric"],
                    is_match=nric_match,
                    confidence=1.0 if nric_match else 0.0
                ))
                
                match_score = sum(fm.confidence for fm in field_matches) / len(field_matches)
                
                return DatabaseRecord(
                    source="identity_database",
                    match_score=match_score,
                    field_matches=field_matches,
                    last_updated=datetime.utcnow()
                )
            
            return None
            
        except Exception as e:
            logger.error(f"Error checking identity database: {e}")
            return None
    
    def _check_blacklist(self, nric: str, name: str) -> bool:
        """
        Check if identity is on any blacklists
        
        Args:
            nric: NRIC number
            name: Full name
            
        Returns:
            True if clear (not on blacklist), False if flagged
        """
        try:
            logger.debug(f"Checking blacklist for NRIC: {nric[:4]}****")
            
            # Simulate blacklist check
            time.sleep(0.02)
            
            # Mock blacklist check - for simulation, randomly flag some entries
            blacklist_hash = hashlib.md5(f"{nric}{name}".encode()).hexdigest()
            
            # Simulate that entries ending in certain patterns are flagged
            flagged_patterns = ['000', '111', '666', '999']
            is_flagged = any(blacklist_hash.endswith(pattern) for pattern in flagged_patterns)
            
            if is_flagged:
                logger.warning(f"Identity flagged in blacklist check: {nric[:4]}****")
            
            return not is_flagged
            
        except Exception as e:
            logger.error(f"Error checking blacklist: {e}")
            return False  # Assume flagged if error occurs
    
    def _check_sanctions_list(self, name: str, date_of_birth: Optional[str]) -> bool:
        """
        Check against international sanctions lists
        
        Args:
            name: Full name
            date_of_birth: Date of birth
            
        Returns:
            True if clear (not on sanctions list), False if flagged
        """
        try:
            logger.debug(f"Checking sanctions list for name: {name[:10]}****")
            
            # Simulate sanctions list check
            time.sleep(0.03)
            
            # Mock sanctions check - flag names containing certain patterns
            flagged_name_patterns = [
                'TERRORIST', 'CRIMINAL', 'SANCTIONS', 'BLOCKED'
            ]
            
            name_upper = name.upper()
            is_flagged = any(pattern in name_upper for pattern in flagged_name_patterns)
            
            if is_flagged:
                logger.warning(f"Identity flagged in sanctions check: {name[:10]}****")
            
            return not is_flagged
            
        except Exception as e:
            logger.error(f"Error checking sanctions list: {e}")
            return False  # Assume flagged if error occurs
    
    def _validate_nric_format(self, nric: str) -> bool:
        """Validate NRIC format"""
        import re
        nric_pattern = r'^[STFG]\d{7}[A-Z]$'
        return bool(re.match(nric_pattern, nric.upper()))
    
    def _simulate_government_response(
        self,
        nric: str,
        name: str,
        date_of_birth: Optional[str]
    ) -> Optional[Dict]:
        """
        Simulate government database response
        
        This would be replaced with actual API calls in production
        """
        try:
            # Validate NRIC checksum for more realistic simulation
            if not self._validate_nric_checksum(nric):
                return None
            
            # Generate mock data based on NRIC
            # In reality, this would come from actual government databases
            mock_data = {
                "nric": nric.upper(),
                "name": self._generate_mock_name(nric, name),
                "date_of_birth": self._generate_mock_dob(nric, date_of_birth),
                "nationality": "SINGAPORE",
                "status": "ACTIVE"
            }
            
            # Simulate some records not being found
            nric_hash = hashlib.md5(nric.encode()).hexdigest()
            if nric_hash.endswith(('a', 'b', 'c')):  # ~12% of records not found
                return None
            
            return mock_data
            
        except Exception as e:
            logger.error(f"Error simulating government response: {e}")
            return None
    
    def _simulate_identity_database_response(self, nric: str, name: str) -> Optional[Dict]:
        """Simulate identity database response"""
        try:
            # Simulate that most NRICs have some record
            nric_hash = hashlib.md5(nric.encode()).hexdigest()
            if nric_hash.endswith(('1', '2', '3', '4', '5')):  # ~50% have records
                return {
                    "nric": nric.upper(),
                    "name": self._generate_mock_name(nric, name),
                    "verification_count": int(nric_hash[-1], 16),
                    "last_verified": datetime.utcnow().isoformat()
                }
            return None
            
        except Exception as e:
            logger.error(f"Error simulating identity database response: {e}")
            return None
    
    def _validate_nric_checksum(self, nric: str) -> bool:
        """Validate NRIC checksum for more realistic simulation"""
        try:
            if len(nric) != 9:
                return False
            
            # NRIC checksum validation (simplified)
            weights = [2, 7, 6, 5, 4, 3, 2]
            digits = [int(d) for d in nric[1:8]]
            
            weighted_sum = sum(d * w for d, w in zip(digits, weights))
            remainder = weighted_sum % 11
            
            # Check letters for S/T vs F/G prefixes
            if nric[0] in 'ST':
                check_letters = 'ABCDEFGHIZJ'
            else:  # F/G
                check_letters = 'KLMNPQRTUWX'
            
            expected_letter = check_letters[remainder]
            return nric[-1].upper() == expected_letter
            
        except (ValueError, IndexError):
            return False
    
    def _generate_mock_name(self, nric: str, input_name: str) -> str:
        """Generate mock name for simulation"""
        # For simulation, slightly modify the input name or return it as-is
        nric_hash = hashlib.md5(nric.encode()).hexdigest()
        
        if nric_hash.endswith(('0', '1', '2', '3')):  # ~40% exact match
            return input_name.upper()
        elif nric_hash.endswith(('4', '5', '6')):  # ~30% slight variation
            # Add common name variations
            variations = [
                input_name.upper(),
                input_name.replace(' ', '').upper(),
                input_name.upper().replace('DAVID', 'DAVE'),
                input_name.upper().replace('MICHAEL', 'MIKE'),
                input_name.upper().replace('BENJAMIN', 'BEN')
            ]
            return variations[int(nric_hash[-1], 16) % len(variations)]
        else:  # Different name
            common_names = [
                'TAN MING WEI', 'LIM SIEW HONG', 'WONG KAR WAI',
                'LEE MING SHENG', 'ONG SIEW LI', 'CHAN WEI MING'
            ]
            return common_names[int(nric_hash[-1], 16) % len(common_names)]
    
    def _generate_mock_dob(self, nric: str, input_dob: Optional[str]) -> str:
        """Generate mock date of birth"""
        if input_dob:
            return input_dob
        
        # Generate DOB based on NRIC (first 2 digits often relate to birth year)
        try:
            year_digits = nric[1:3]
            if year_digits.startswith('0'):
                year = 2000 + int(year_digits)
            else:
                year = 1900 + int(year_digits)
            
            # Generate random month and day
            nric_hash = hashlib.md5(nric.encode()).hexdigest()
            month = (int(nric_hash[0], 16) % 12) + 1
            day = (int(nric_hash[1], 16) % 28) + 1
            
            return f"{year:04d}-{month:02d}-{day:02d}"
            
        except (ValueError, IndexError):
            return "1990-01-01"  # Default fallback
    
    def _calculate_name_similarity(self, name1: str, name2: str) -> float:
        """Calculate similarity between two names"""
        try:
            # Simple Levenshtein distance-based similarity
            name1 = name1.upper().strip()
            name2 = name2.upper().strip()
            
            if name1 == name2:
                return 1.0
            
            # Calculate Levenshtein distance
            distance = self._levenshtein_distance(name1, name2)
            max_len = max(len(name1), len(name2))
            
            if max_len == 0:
                return 1.0
            
            similarity = 1.0 - (distance / max_len)
            return max(0.0, similarity)
            
        except Exception as e:
            logger.error(f"Error calculating name similarity: {e}")
            return 0.0
    
    def _levenshtein_distance(self, s1: str, s2: str) -> int:
        """Calculate Levenshtein distance between two strings"""
        if len(s1) < len(s2):
            return self._levenshtein_distance(s2, s1)
        
        if len(s2) == 0:
            return len(s1)
        
        previous_row = range(len(s2) + 1)
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
        
        return previous_row[-1]
    
    def _compare_dates(self, date1: str, date2: str) -> bool:
        """Compare two date strings"""
        try:
            # Normalize date formats
            date1_normalized = self._normalize_date(date1)
            date2_normalized = self._normalize_date(date2)
            
            return date1_normalized == date2_normalized
            
        except Exception as e:
            logger.error(f"Error comparing dates: {e}")
            return False
    
    def _normalize_date(self, date_str: str) -> str:
        """Normalize date string to YYYY-MM-DD format"""
        try:
            # Handle different date formats
            date_str = date_str.strip()
            
            # Try different date formats
            from datetime import datetime
            
            formats = [
                '%Y-%m-%d',
                '%d/%m/%Y',
                '%m/%d/%Y',
                '%d-%m-%Y',
                '%Y/%m/%d'
            ]
            
            for fmt in formats:
                try:
                    dt = datetime.strptime(date_str, fmt)
                    return dt.strftime('%Y-%m-%d')
                except ValueError:
                    continue
            
            # If no format matches, return as-is
            return date_str
            
        except Exception as e:
            logger.error(f"Error normalizing date: {e}")
            return date_str
    
    def _determine_verification_status(self, records: List[DatabaseRecord]) -> str:
        """Determine overall verification status"""
        if not records:
            return "no_match"
        
        # Calculate average match score
        avg_score = sum(record.match_score for record in records) / len(records)
        
        if avg_score >= 0.9:
            return "verified"
        elif avg_score >= 0.7:
            return "partial_match"
        else:
            return "no_match"
    
    def _generate_cache_key(self, nric: str, name: str, date_of_birth: Optional[str]) -> str:
        """Generate cache key for verification request"""
        key_data = f"{nric}|{name}|{date_of_birth or ''}"
        return hashlib.sha256(key_data.encode()).hexdigest()[:16]
    
    def _get_cached_result(self, cache_key: str) -> Optional[DatabaseVerificationResult]:
        """Get cached verification result"""
        try:
            if cache_key in self.cache:
                cached_entry = self.cache[cache_key]
                if datetime.utcnow() - cached_entry['timestamp'] < self.cache_ttl:
                    return cached_entry['result']
                else:
                    # Remove expired entry
                    del self.cache[cache_key]
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting cached result: {e}")
            return None
    
    def _cache_result(self, cache_key: str, result: DatabaseVerificationResult):
        """Cache verification result"""
        try:
            self.cache[cache_key] = {
                'result': result,
                'timestamp': datetime.utcnow()
            }
            
            # Simple cache cleanup - remove oldest entries if cache gets too large
            if len(self.cache) > 1000:
                oldest_key = min(self.cache.keys(), 
                               key=lambda k: self.cache[k]['timestamp'])
                del self.cache[oldest_key]
                
        except Exception as e:
            logger.error(f"Error caching result: {e}")
    
    def clear_cache(self):
        """Clear all cached results"""
        self.cache.clear()
        logger.info("Database verification cache cleared")
    
    def get_cache_stats(self) -> Dict:
        """Get cache statistics"""
        return {
            "cache_size": len(self.cache),
            "cache_ttl_hours": self.cache_ttl.total_seconds() / 3600
        } 