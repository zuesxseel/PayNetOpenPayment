"""
Time Analysis Utilities for UEBA System
"""
import numpy as np
import pandas as pd
from datetime import datetime, timedelta, time
from typing import List, Dict, Optional, Tuple, Any
from loguru import logger
import pytz
from collections import defaultdict


class TimeAnalyzer:
    """Time-based analysis utilities for behavioral analytics"""
    
    def __init__(self):
        self.business_hours = (9, 17)  # 9 AM to 5 PM
        self.weekend_days = [5, 6]  # Saturday, Sunday
        
    def analyze_temporal_patterns(self, timestamps: List[datetime]) -> Dict[str, Any]:
        """
        Analyze temporal patterns in a list of timestamps
        
        Args:
            timestamps: List of datetime objects
            
        Returns:
            Dictionary containing temporal pattern analysis
        """
        if not timestamps:
            return {}
        
        try:
            # Convert to pandas for easier analysis
            df = pd.DataFrame({'timestamp': timestamps})
            df['hour'] = df['timestamp'].dt.hour
            df['day_of_week'] = df['timestamp'].dt.dayofweek
            df['day_of_month'] = df['timestamp'].dt.day
            df['month'] = df['timestamp'].dt.month
            df['is_weekend'] = df['day_of_week'].isin(self.weekend_days)
            df['is_business_hours'] = df['hour'].between(*self.business_hours)
            
            analysis = {
                'total_events': len(timestamps),
                'time_span_hours': self._calculate_time_span_hours(timestamps),
                'hourly_distribution': self._get_hourly_distribution(df),
                'daily_distribution': self._get_daily_distribution(df),
                'monthly_distribution': self._get_monthly_distribution(df),
                'business_hours_ratio': float(df['is_business_hours'].mean()),
                'weekend_ratio': float(df['is_weekend'].mean()),
                'activity_patterns': self._identify_activity_patterns(df),
                'peak_activity_periods': self._find_peak_periods(df),
                'consistency_metrics': self._calculate_consistency_metrics(df)
            }
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing temporal patterns: {e}")
            return {}
    
    def detect_time_anomalies(
        self,
        current_timestamp: datetime,
        baseline_patterns: Dict[str, Any],
        threshold: float = 0.1
    ) -> List[Dict[str, Any]]:
        """
        Detect temporal anomalies based on baseline patterns
        
        Args:
            current_timestamp: Current event timestamp
            baseline_patterns: Historical temporal patterns
            threshold: Anomaly detection threshold
            
        Returns:
            List of detected anomalies
        """
        anomalies = []
        
        try:
            current_hour = current_timestamp.hour
            current_day = current_timestamp.weekday()
            
            # Check hour-based anomalies
            hourly_baseline = baseline_patterns.get('hourly_distribution', {})
            if hourly_baseline:
                expected_frequency = hourly_baseline.get(str(current_hour), 0)
                max_frequency = max(hourly_baseline.values()) if hourly_baseline.values() else 1
                
                if expected_frequency / max_frequency < threshold:
                    anomalies.append({
                        'type': 'unusual_hour',
                        'current_hour': current_hour,
                        'expected_frequency': expected_frequency,
                        'severity': 1.0 - (expected_frequency / max_frequency)
                    })
            
            # Check day-based anomalies
            daily_baseline = baseline_patterns.get('daily_distribution', {})
            if daily_baseline:
                expected_frequency = daily_baseline.get(str(current_day), 0)
                max_frequency = max(daily_baseline.values()) if daily_baseline.values() else 1
                
                if expected_frequency / max_frequency < threshold:
                    anomalies.append({
                        'type': 'unusual_day',
                        'current_day': current_day,
                        'expected_frequency': expected_frequency,
                        'severity': 1.0 - (expected_frequency / max_frequency)
                    })
            
            # Check business hours compliance
            is_business_hours = self.business_hours[0] <= current_hour <= self.business_hours[1]
            baseline_business_ratio = baseline_patterns.get('business_hours_ratio', 0.8)
            
            if not is_business_hours and baseline_business_ratio > 0.7:
                anomalies.append({
                    'type': 'off_hours_activity',
                    'current_hour': current_hour,
                    'business_hours_compliance': baseline_business_ratio,
                    'severity': 0.7
                })
            
        except Exception as e:
            logger.error(f"Error detecting time anomalies: {e}")
        
        return anomalies
    
    def calculate_activity_regularity(self, timestamps: List[datetime]) -> float:
        """
        Calculate how regular the activity pattern is (0-1 scale)
        
        Args:
            timestamps: List of datetime objects
            
        Returns:
            Regularity score (0 = irregular, 1 = very regular)
        """
        if len(timestamps) < 2:
            return 0.0
        
        try:
            # Calculate intervals between consecutive events
            intervals = []
            sorted_timestamps = sorted(timestamps)
            
            for i in range(1, len(sorted_timestamps)):
                interval = (sorted_timestamps[i] - sorted_timestamps[i-1]).total_seconds() / 3600
                intervals.append(interval)
            
            if not intervals:
                return 0.0
            
            # Calculate coefficient of variation (inverse of regularity)
            mean_interval = np.mean(intervals)
            std_interval = np.std(intervals)
            
            if mean_interval == 0:
                return 0.0
            
            cv = std_interval / mean_interval
            regularity = max(0.0, 1.0 - min(cv, 1.0))
            
            return float(regularity)
            
        except Exception as e:
            logger.error(f"Error calculating activity regularity: {e}")
            return 0.0
    
    def detect_impossible_time_sequences(
        self,
        timestamps: List[datetime],
        locations: List[str],
        max_travel_speed_kmh: float = 1000  # Conservative for air travel
    ) -> List[Dict[str, Any]]:
        """
        Detect impossible time sequences (too fast travel between locations)
        
        Args:
            timestamps: List of event timestamps
            locations: List of location identifiers corresponding to timestamps
            max_travel_speed_kmh: Maximum reasonable travel speed
            
        Returns:
            List of impossible sequences detected
        """
        impossible_sequences = []
        
        if len(timestamps) != len(locations) or len(timestamps) < 2:
            return impossible_sequences
        
        try:
            # This is a simplified version - in practice would need actual geo calculations
            for i in range(1, len(timestamps)):
                time_diff_hours = (timestamps[i] - timestamps[i-1]).total_seconds() / 3600
                
                if time_diff_hours > 0 and locations[i] != locations[i-1]:
                    # Assume different locations require some minimum travel time
                    min_travel_time_hours = 0.5  # 30 minutes minimum
                    
                    if time_diff_hours < min_travel_time_hours:
                        impossible_sequences.append({
                            'start_timestamp': timestamps[i-1],
                            'end_timestamp': timestamps[i],
                            'start_location': locations[i-1],
                            'end_location': locations[i],
                            'time_difference_hours': time_diff_hours,
                            'reason': 'insufficient_travel_time'
                        })
            
        except Exception as e:
            logger.error(f"Error detecting impossible time sequences: {e}")
        
        return impossible_sequences
    
    def find_activity_clusters(
        self,
        timestamps: List[datetime],
        cluster_threshold_hours: float = 4.0
    ) -> List[Dict[str, Any]]:
        """
        Find clusters of activity in time
        
        Args:
            timestamps: List of datetime objects
            cluster_threshold_hours: Maximum gap within a cluster
            
        Returns:
            List of activity clusters
        """
        if len(timestamps) < 2:
            return []
        
        try:
            clusters = []
            sorted_timestamps = sorted(timestamps)
            
            current_cluster = [sorted_timestamps[0]]
            
            for i in range(1, len(sorted_timestamps)):
                time_gap = (sorted_timestamps[i] - sorted_timestamps[i-1]).total_seconds() / 3600
                
                if time_gap <= cluster_threshold_hours:
                    current_cluster.append(sorted_timestamps[i])
                else:
                    # Save current cluster and start new one
                    if len(current_cluster) > 1:
                        clusters.append({
                            'start_time': current_cluster[0],
                            'end_time': current_cluster[-1],
                            'event_count': len(current_cluster),
                            'duration_hours': (current_cluster[-1] - current_cluster[0]).total_seconds() / 3600
                        })
                    current_cluster = [sorted_timestamps[i]]
            
            # Don't forget the last cluster
            if len(current_cluster) > 1:
                clusters.append({
                    'start_time': current_cluster[0],
                    'end_time': current_cluster[-1],
                    'event_count': len(current_cluster),
                    'duration_hours': (current_cluster[-1] - current_cluster[0]).total_seconds() / 3600
                })
            
            return clusters
            
        except Exception as e:
            logger.error(f"Error finding activity clusters: {e}")
            return []
    
    def calculate_work_pattern_compliance(
        self,
        timestamps: List[datetime],
        expected_work_hours: Tuple[int, int] = (9, 17),
        expected_work_days: List[int] = [0, 1, 2, 3, 4]  # Monday-Friday
    ) -> Dict[str, float]:
        """
        Calculate compliance with expected work patterns
        
        Args:
            timestamps: List of event timestamps
            expected_work_hours: Tuple of (start_hour, end_hour)
            expected_work_days: List of expected work days (0=Monday)
            
        Returns:
            Dictionary with compliance metrics
        """
        if not timestamps:
            return {}
        
        try:
            total_events = len(timestamps)
            work_hour_events = 0
            work_day_events = 0
            
            for ts in timestamps:
                # Check work hours compliance
                if expected_work_hours[0] <= ts.hour <= expected_work_hours[1]:
                    work_hour_events += 1
                
                # Check work days compliance
                if ts.weekday() in expected_work_days:
                    work_day_events += 1
            
            return {
                'work_hours_compliance': work_hour_events / total_events,
                'work_days_compliance': work_day_events / total_events,
                'off_hours_activity_ratio': (total_events - work_hour_events) / total_events,
                'weekend_activity_ratio': (total_events - work_day_events) / total_events
            }
            
        except Exception as e:
            logger.error(f"Error calculating work pattern compliance: {e}")
            return {}
    
    def _calculate_time_span_hours(self, timestamps: List[datetime]) -> float:
        """Calculate time span in hours"""
        if len(timestamps) < 2:
            return 0.0
        
        return (max(timestamps) - min(timestamps)).total_seconds() / 3600
    
    def _get_hourly_distribution(self, df: pd.DataFrame) -> Dict[str, float]:
        """Get hourly activity distribution"""
        hourly_counts = df['hour'].value_counts().to_dict()
        total = len(df)
        
        # Normalize to percentages
        return {str(hour): count / total for hour, count in hourly_counts.items()}
    
    def _get_daily_distribution(self, df: pd.DataFrame) -> Dict[str, float]:
        """Get daily activity distribution"""
        daily_counts = df['day_of_week'].value_counts().to_dict()
        total = len(df)
        
        # Convert to day names
        day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        return {day_names[day]: count / total for day, count in daily_counts.items()}
    
    def _get_monthly_distribution(self, df: pd.DataFrame) -> Dict[str, float]:
        """Get monthly activity distribution"""
        monthly_counts = df['month'].value_counts().to_dict()
        total = len(df)
        
        return {str(month): count / total for month, count in monthly_counts.items()}
    
    def _identify_activity_patterns(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Identify common activity patterns"""
        patterns = {}
        
        try:
            # Most active hour
            most_active_hour = df['hour'].mode().iloc[0] if not df['hour'].mode().empty else None
            
            # Most active day
            most_active_day = df['day_of_week'].mode().iloc[0] if not df['day_of_week'].mode().empty else None
            
            # Activity concentration
            hour_entropy = self._calculate_entropy(df['hour'].value_counts().values)
            day_entropy = self._calculate_entropy(df['day_of_week'].value_counts().values)
            
            patterns = {
                'most_active_hour': int(most_active_hour) if most_active_hour is not None else None,
                'most_active_day': int(most_active_day) if most_active_day is not None else None,
                'hour_diversity': float(hour_entropy),
                'day_diversity': float(day_entropy),
                'activity_concentration': {
                    'highly_concentrated_hours': float((df['hour'].value_counts() > len(df) * 0.2).sum()),
                    'spread_across_days': float((df['day_of_week'].value_counts() > 0).sum())
                }
            }
            
        except Exception as e:
            logger.error(f"Error identifying activity patterns: {e}")
        
        return patterns
    
    def _find_peak_periods(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Find peak activity periods"""
        try:
            hour_counts = df['hour'].value_counts().sort_index()
            
            # Find consecutive high-activity hours
            threshold = hour_counts.quantile(0.75)  # Top 25% of hours
            peak_hours = hour_counts[hour_counts >= threshold].index.tolist()
            
            # Find consecutive sequences
            peak_periods = []
            if peak_hours:
                current_period = [peak_hours[0]]
                
                for i in range(1, len(peak_hours)):
                    if peak_hours[i] == peak_hours[i-1] + 1:
                        current_period.append(peak_hours[i])
                    else:
                        if len(current_period) > 1:
                            peak_periods.append({
                                'start_hour': current_period[0],
                                'end_hour': current_period[-1],
                                'duration': len(current_period)
                            })
                        current_period = [peak_hours[i]]
                
                # Don't forget the last period
                if len(current_period) > 1:
                    peak_periods.append({
                        'start_hour': current_period[0],
                        'end_hour': current_period[-1],
                        'duration': len(current_period)
                    })
            
            return {
                'peak_periods': peak_periods,
                'peak_hours': peak_hours,
                'activity_threshold': float(threshold)
            }
            
        except Exception as e:
            logger.error(f"Error finding peak periods: {e}")
            return {}
    
    def _calculate_consistency_metrics(self, df: pd.DataFrame) -> Dict[str, float]:
        """Calculate temporal consistency metrics"""
        try:
            # Calculate standard deviations as measures of consistency
            hour_std = float(df['hour'].std())
            day_std = float(df['day_of_week'].std())
            
            # Calculate regularity (inverse of standard deviation, normalized)
            hour_regularity = max(0.0, 1.0 - (hour_std / 12.0))  # Normalize by max possible std
            day_regularity = max(0.0, 1.0 - (day_std / 3.5))     # Normalize by max possible std
            
            return {
                'hour_consistency': hour_regularity,
                'day_consistency': day_regularity,
                'overall_consistency': (hour_regularity + day_regularity) / 2,
                'hour_standard_deviation': hour_std,
                'day_standard_deviation': day_std
            }
            
        except Exception as e:
            logger.error(f"Error calculating consistency metrics: {e}")
            return {}
    
    def _calculate_entropy(self, values: np.ndarray) -> float:
        """Calculate entropy of a distribution"""
        try:
            probabilities = values / values.sum()
            # Remove zero probabilities to avoid log(0)
            probabilities = probabilities[probabilities > 0]
            entropy = -np.sum(probabilities * np.log2(probabilities))
            return float(entropy)
        except:
            return 0.0 