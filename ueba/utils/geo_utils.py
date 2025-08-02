"""
Geographic Analysis Utilities for UEBA System
"""
import math
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple, Any
from loguru import logger
from collections import defaultdict


class GeoAnalyzer:
    """Geographic analysis utilities for behavioral analytics"""
    
    def __init__(self):
        # Earth's radius in kilometers
        self.earth_radius_km = 6371.0
        # Maximum reasonable travel speeds (km/h)
        self.max_speeds = {
            'walking': 5,
            'driving': 120,
            'commercial_flight': 900,
            'private_jet': 800
        }
        
    def calculate_distance(
        self,
        lat1: float,
        lon1: float,
        lat2: float,
        lon2: float
    ) -> float:
        """
        Calculate the great circle distance between two points on Earth
        using the Haversine formula
        
        Args:
            lat1, lon1: Latitude and longitude of first point
            lat2, lon2: Latitude and longitude of second point
            
        Returns:
            Distance in kilometers
        """
        try:
            # Convert latitude and longitude from degrees to radians
            lat1_rad = math.radians(lat1)
            lon1_rad = math.radians(lon1)
            lat2_rad = math.radians(lat2)
            lon2_rad = math.radians(lon2)
            
            # Differences
            dlat = lat2_rad - lat1_rad
            dlon = lon2_rad - lon1_rad
            
            # Haversine formula
            a = (math.sin(dlat / 2) ** 2 +
                 math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2) ** 2)
            c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
            
            distance = self.earth_radius_km * c
            return distance
            
        except Exception as e:
            logger.error(f"Error calculating distance: {e}")
            return 0.0
    
    async def calculate_location_distances(
        self,
        locations: List[Dict[str, Any]]
    ) -> List[float]:
        """
        Calculate distances between consecutive locations
        
        Args:
            locations: List of location dictionaries with lat/lon
            
        Returns:
            List of distances in kilometers
        """
        distances = []
        
        try:
            for i in range(1, len(locations)):
                prev_loc = locations[i-1]
                curr_loc = locations[i]
                
                # Extract coordinates
                prev_lat = self._extract_latitude(prev_loc)
                prev_lon = self._extract_longitude(prev_loc)
                curr_lat = self._extract_latitude(curr_loc)
                curr_lon = self._extract_longitude(curr_loc)
                
                if all(coord is not None for coord in [prev_lat, prev_lon, curr_lat, curr_lon]):
                    distance = self.calculate_distance(prev_lat, prev_lon, curr_lat, curr_lon)
                    distances.append(distance)
                else:
                    distances.append(0.0)
            
        except Exception as e:
            logger.error(f"Error calculating location distances: {e}")
        
        return distances
    
    async def detect_impossible_travel(
        self,
        events: List[Any],
        max_speed_kmh: float = 1000.0
    ) -> List[Dict[str, Any]]:
        """
        Detect impossible travel between event locations
        
        Args:
            events: List of events with timestamp and location data
            max_speed_kmh: Maximum reasonable travel speed
            
        Returns:
            List of impossible travel scenarios
        """
        impossible_travel = []
        
        try:
            # Sort events by timestamp
            sorted_events = sorted(events, key=lambda x: x.timestamp)
            
            for i in range(1, len(sorted_events)):
                prev_event = sorted_events[i-1]
                curr_event = sorted_events[i]
                
                # Extract location data
                prev_location = getattr(prev_event, 'source_location', None)
                curr_location = getattr(curr_event, 'source_location', None)
                
                if not prev_location or not curr_location:
                    continue
                
                # Calculate distance and time difference
                distance_km = await self._calculate_event_distance(prev_event, curr_event)
                time_diff = curr_event.timestamp - prev_event.timestamp
                time_diff_hours = time_diff.total_seconds() / 3600
                
                if distance_km > 0 and time_diff_hours > 0:
                    required_speed = distance_km / time_diff_hours
                    
                    if required_speed > max_speed_kmh:
                        impossible_travel.append({
                            'earlier_event': prev_event,
                            'later_event': curr_event,
                            'distance': distance_km,
                            'time_diff': time_diff_hours,
                            'required_speed': required_speed,
                            'max_reasonable_speed': max_speed_kmh,
                            'impossibility_factor': required_speed / max_speed_kmh
                        })
            
        except Exception as e:
            logger.error(f"Error detecting impossible travel: {e}")
        
        return impossible_travel
    
    async def analyze_location_patterns(
        self,
        locations: List[Dict[str, Any]],
        timestamps: List[datetime]
    ) -> Dict[str, Any]:
        """
        Analyze geographic patterns in location data
        
        Args:
            locations: List of location dictionaries
            timestamps: Corresponding timestamps
            
        Returns:
            Geographic pattern analysis
        """
        try:
            if len(locations) != len(timestamps):
                logger.error("Locations and timestamps must have same length")
                return {}
            
            analysis = {
                'unique_locations': len(set(str(loc) for loc in locations)),
                'total_distance': 0.0,
                'geographic_spread': 0.0,
                'location_frequency': {},
                'temporal_location_patterns': {},
                'mobility_metrics': {}
            }
            
            # Calculate total distance traveled
            distances = await self.calculate_location_distances(locations)
            analysis['total_distance'] = sum(distances)
            
            # Geographic spread (maximum distance between any two points)
            analysis['geographic_spread'] = await self._calculate_geographic_spread(locations)
            
            # Location frequency analysis
            location_counts = defaultdict(int)
            for loc in locations:
                loc_str = str(loc)
                location_counts[loc_str] += 1
            
            analysis['location_frequency'] = dict(location_counts)
            
            # Temporal location patterns
            analysis['temporal_location_patterns'] = self._analyze_temporal_location_patterns(
                locations, timestamps
            )
            
            # Mobility metrics
            analysis['mobility_metrics'] = self._calculate_mobility_metrics(
                locations, timestamps, distances
            )
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing location patterns: {e}")
            return {}
    
    def detect_location_anomalies(
        self,
        current_location: Dict[str, Any],
        baseline_locations: List[Dict[str, Any]],
        threshold_km: float = 500.0
    ) -> List[Dict[str, Any]]:
        """
        Detect location-based anomalies
        
        Args:
            current_location: Current location to check
            baseline_locations: Historical baseline locations
            threshold_km: Distance threshold for anomaly detection
            
        Returns:
            List of detected location anomalies
        """
        anomalies = []
        
        try:
            current_lat = self._extract_latitude(current_location)
            current_lon = self._extract_longitude(current_location)
            
            if current_lat is None or current_lon is None:
                return anomalies
            
            # Calculate minimum distance to any baseline location
            min_distance = float('inf')
            closest_baseline = None
            
            for baseline_loc in baseline_locations:
                baseline_lat = self._extract_latitude(baseline_loc)
                baseline_lon = self._extract_longitude(baseline_loc)
                
                if baseline_lat is not None and baseline_lon is not None:
                    distance = self.calculate_distance(
                        current_lat, current_lon, baseline_lat, baseline_lon
                    )
                    
                    if distance < min_distance:
                        min_distance = distance
                        closest_baseline = baseline_loc
            
            # Check if current location is anomalous
            if min_distance > threshold_km:
                anomalies.append({
                    'type': 'distant_location',
                    'current_location': current_location,
                    'closest_baseline': closest_baseline,
                    'distance_km': min_distance,
                    'threshold_km': threshold_km,
                    'severity': min(min_distance / threshold_km, 10.0)  # Cap at 10x
                })
            
        except Exception as e:
            logger.error(f"Error detecting location anomalies: {e}")
        
        return anomalies
    
    def find_location_clusters(
        self,
        locations: List[Dict[str, Any]],
        cluster_radius_km: float = 50.0
    ) -> List[Dict[str, Any]]:
        """
        Find clusters of locations within a given radius
        
        Args:
            locations: List of location dictionaries
            cluster_radius_km: Maximum radius for clustering
            
        Returns:
            List of location clusters
        """
        clusters = []
        
        try:
            visited = set()
            
            for i, location in enumerate(locations):
                if i in visited:
                    continue
                
                cluster = {'center': location, 'locations': [location], 'indices': [i]}
                visited.add(i)
                
                center_lat = self._extract_latitude(location)
                center_lon = self._extract_longitude(location)
                
                if center_lat is None or center_lon is None:
                    continue
                
                # Find all locations within cluster radius
                for j, other_location in enumerate(locations):
                    if j in visited:
                        continue
                    
                    other_lat = self._extract_latitude(other_location)
                    other_lon = self._extract_longitude(other_location)
                    
                    if other_lat is not None and other_lon is not None:
                        distance = self.calculate_distance(
                            center_lat, center_lon, other_lat, other_lon
                        )
                        
                        if distance <= cluster_radius_km:
                            cluster['locations'].append(other_location)
                            cluster['indices'].append(j)
                            visited.add(j)
                
                # Add cluster statistics
                cluster['size'] = len(cluster['locations'])
                cluster['radius_km'] = cluster_radius_km
                
                clusters.append(cluster)
            
        except Exception as e:
            logger.error(f"Error finding location clusters: {e}")
        
        return clusters
    
    def calculate_location_entropy(
        self,
        locations: List[Dict[str, Any]]
    ) -> float:
        """
        Calculate entropy of location distribution
        
        Args:
            locations: List of location dictionaries
            
        Returns:
            Location entropy value
        """
        try:
            if not locations:
                return 0.0
            
            # Count location frequencies
            location_counts = defaultdict(int)
            for loc in locations:
                loc_str = str(loc)
                location_counts[loc_str] += 1
            
            # Calculate probabilities
            total_count = sum(location_counts.values())
            probabilities = [count / total_count for count in location_counts.values()]
            
            # Calculate entropy
            entropy = 0.0
            for p in probabilities:
                if p > 0:
                    entropy -= p * math.log2(p)
            
            return entropy
            
        except Exception as e:
            logger.error(f"Error calculating location entropy: {e}")
            return 0.0
    
    async def _calculate_event_distance(self, event1: Any, event2: Any) -> float:
        """Calculate distance between two events"""
        try:
            loc1 = getattr(event1, 'source_location', None)
            loc2 = getattr(event2, 'source_location', None)
            
            if not loc1 or not loc2:
                return 0.0
            
            lat1 = self._extract_latitude(loc1)
            lon1 = self._extract_longitude(loc1)
            lat2 = self._extract_latitude(loc2)
            lon2 = self._extract_longitude(loc2)
            
            if all(coord is not None for coord in [lat1, lon1, lat2, lon2]):
                return self.calculate_distance(lat1, lon1, lat2, lon2)
            
            return 0.0
            
        except Exception as e:
            logger.error(f"Error calculating event distance: {e}")
            return 0.0
    
    async def _calculate_geographic_spread(self, locations: List[Dict[str, Any]]) -> float:
        """Calculate maximum distance between any two locations"""
        max_distance = 0.0
        
        try:
            for i in range(len(locations)):
                for j in range(i + 1, len(locations)):
                    lat1 = self._extract_latitude(locations[i])
                    lon1 = self._extract_longitude(locations[i])
                    lat2 = self._extract_latitude(locations[j])
                    lon2 = self._extract_longitude(locations[j])
                    
                    if all(coord is not None for coord in [lat1, lon1, lat2, lon2]):
                        distance = self.calculate_distance(lat1, lon1, lat2, lon2)
                        max_distance = max(max_distance, distance)
            
        except Exception as e:
            logger.error(f"Error calculating geographic spread: {e}")
        
        return max_distance
    
    def _analyze_temporal_location_patterns(
        self,
        locations: List[Dict[str, Any]],
        timestamps: List[datetime]
    ) -> Dict[str, Any]:
        """Analyze how locations change over time"""
        patterns = {}
        
        try:
            # Group locations by hour of day
            hourly_locations = defaultdict(list)
            for loc, ts in zip(locations, timestamps):
                hour = ts.hour
                hourly_locations[hour].append(str(loc))
            
            # Analyze hourly patterns
            patterns['hourly_diversity'] = {}
            for hour, hour_locations in hourly_locations.items():
                unique_locations = len(set(hour_locations))
                total_locations = len(hour_locations)
                diversity = unique_locations / total_locations if total_locations > 0 else 0
                patterns['hourly_diversity'][hour] = diversity
            
            # Find most common location by time of day
            patterns['common_locations_by_hour'] = {}
            for hour, hour_locations in hourly_locations.items():
                if hour_locations:
                    most_common = max(set(hour_locations), key=hour_locations.count)
                    patterns['common_locations_by_hour'][hour] = most_common
            
        except Exception as e:
            logger.error(f"Error analyzing temporal location patterns: {e}")
        
        return patterns
    
    def _calculate_mobility_metrics(
        self,
        locations: List[Dict[str, Any]],
        timestamps: List[datetime],
        distances: List[float]
    ) -> Dict[str, float]:
        """Calculate various mobility metrics"""
        metrics = {}
        
        try:
            if distances:
                metrics['total_distance_km'] = sum(distances)
                metrics['average_trip_distance_km'] = np.mean(distances)
                metrics['max_trip_distance_km'] = max(distances)
                metrics['distance_std_km'] = float(np.std(distances))
            else:
                metrics.update({
                    'total_distance_km': 0.0,
                    'average_trip_distance_km': 0.0,
                    'max_trip_distance_km': 0.0,
                    'distance_std_km': 0.0
                })
            
            # Calculate time-based metrics
            if len(timestamps) > 1:
                time_span = (max(timestamps) - min(timestamps)).total_seconds() / 3600  # hours
                if time_span > 0:
                    metrics['mobility_rate_km_per_hour'] = metrics['total_distance_km'] / time_span
                else:
                    metrics['mobility_rate_km_per_hour'] = 0.0
            else:
                metrics['mobility_rate_km_per_hour'] = 0.0
            
            # Location diversity
            unique_locations = len(set(str(loc) for loc in locations))
            total_locations = len(locations)
            metrics['location_diversity'] = unique_locations / total_locations if total_locations > 0 else 0
            
            # Calculate entropy
            metrics['location_entropy'] = self.calculate_location_entropy(locations)
            
        except Exception as e:
            logger.error(f"Error calculating mobility metrics: {e}")
        
        return metrics
    
    def _extract_latitude(self, location: Dict[str, Any]) -> Optional[float]:
        """Extract latitude from location dictionary"""
        try:
            # Try common field names
            for field in ['lat', 'latitude', 'y']:
                if field in location:
                    return float(location[field])
            return None
        except (ValueError, TypeError):
            return None
    
    def _extract_longitude(self, location: Dict[str, Any]) -> Optional[float]:
        """Extract longitude from location dictionary"""
        try:
            # Try common field names
            for field in ['lon', 'lng', 'longitude', 'x']:
                if field in location:
                    return float(location[field])
            return None
        except (ValueError, TypeError):
            return None 