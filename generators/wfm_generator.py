"""
WFM (Workforce Management) data generator.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List
from generators.base_generator import BaseGenerator
from models.entities import WfmEntry, ModelValidator


class WfmGenerator(BaseGenerator):
    """Generates Workforce Management data."""
    
    def generate(self, users_df: pd.DataFrame) -> pd.DataFrame:
        """Generate WFM data for all users across all calendar dates."""
        wfm_entries = []
        validation_errors = []
        
        # Get all calendar dates between START_DATE and END_DATE
        calendar_dates = self._get_calendar_dates()
        
        for _, user_row in users_df.iterrows():
            user_id = user_row['user_id']
            fte = user_row['fte']
            user_start_date = pd.to_datetime(user_row['start_date'])

            # Get dates starting from user's start date
            user_calendar_dates = self._get_calendar_dates_for_user(user_start_date)
            
            for date in user_calendar_dates:
                # Check if it's a working day (Monday-Friday, not bank holiday)
                is_working_day = self._is_working_day(date)
                
                if is_working_day:
                    # Calculate working day metrics with statistical variation
                    paid_time = fte * 8 * 60  # FTE x 8 hours x 60 minutes
                    scheduled_time = paid_time  # Paid time equals scheduled time
                    
                    # Generate WFM factors with statistical variation
                    shrinkage_factor = self._generate_wfm_factor('shrinkage')
                    occupancy_factor = self._generate_wfm_factor('occupancy')
                    utilization_factor = self._generate_wfm_factor('utilization')
                    
                    # Apply factors with variation
                    available_time = scheduled_time * shrinkage_factor
                    interactions_time = available_time * occupancy_factor
                    productive_time = scheduled_time * utilization_factor
                else:
                    # Weekend or bank holiday - all None except date
                    paid_time = None
                    scheduled_time = None
                    available_time = None
                    interactions_time = None
                    productive_time = None
                
                # Create WFM entry
                wfm_entry = WfmEntry(
                    date=date.strftime('%Y-%m-%d'),
                    user_id=user_id,
                    paid_time=paid_time,
                    scheduled_time=scheduled_time,
                    available_time=available_time,
                    interactions_time=interactions_time,
                    productive_time=productive_time
                )
                
                # Validate the entry
                errors = ModelValidator.validate_wfm_entry(wfm_entry)
                if errors:
                    validation_errors.extend([f"WFM {date.strftime('%Y-%m-%d')} User {user_id}: {error}" for error in errors])
                
                wfm_entries.append(wfm_entry)
        
        # Report validation errors if any
        if validation_errors:
            print(f"Warning: {len(validation_errors)} WFM validation errors found:")
            for error in validation_errors[:5]:  # Show first 5 errors
                print(f"  - {error}")
            if len(validation_errors) > 5:
                print(f"  ... and {len(validation_errors) - 5} more")
        
        # Convert to DataFrame
        df = WfmEntry.to_dataframe(wfm_entries)
        
        expected_columns = ['date', 'user_id', 'paid_time', 'scheduled_time', 
                           'available_time', 'interactions_time', 'productive_time']
        self._validate_output(df, expected_columns)
        self._log_generation_stats(df, "WFM")
        
        return df
    
    def generate_models(self, users_df: pd.DataFrame) -> List[WfmEntry]:
        """Generate WFM data and return as list of WfmEntry models."""
        # Generate DataFrame first, then convert to models
        df = self.generate(users_df)
        
        wfm_entries = []
        for _, row in df.iterrows():
            wfm_entry = WfmEntry(
                date=row['date'],
                user_id=row['user_id'],
                paid_time=row['paid_time'] if pd.notna(row['paid_time']) else None,
                scheduled_time=row['scheduled_time'] if pd.notna(row['scheduled_time']) else None,
                available_time=row['available_time'] if pd.notna(row['available_time']) else None,
                interactions_time=row['interactions_time'] if pd.notna(row['interactions_time']) else None,
                productive_time=row['productive_time'] if pd.notna(row['productive_time']) else None
            )
            wfm_entries.append(wfm_entry)
        
        return wfm_entries
    
    def _get_calendar_dates(self) -> List[datetime]:
        """Get all calendar dates between START_DATE and END_DATE."""
        dates = []
        current_date = self.config.START_DATE
        
        while current_date <= self.config.END_DATE:
            dates.append(current_date)
            current_date += timedelta(days=1)
        
        return dates
    
    def _is_working_day(self, date: datetime) -> bool:
        """
        Check if date is a working day (Monday-Friday, not bank holiday).
        Currently only checks for weekends. Bank holidays could be added here.
        """
        # Monday = 0, Sunday = 6
        weekday = date.weekday()
        
        # Weekend check (Saturday = 5, Sunday = 6)
        if weekday >= 5:
            return False
        
        # TODO: Add bank holiday logic here if needed
        # For now, only excluding weekends
        
        return True
    
    def analyze_utilization_by_user(self, wfm_entries: List[WfmEntry]) -> dict:
        """Analyze utilization metrics by user using WfmEntry models."""
        user_stats = {}
        
        for entry in wfm_entries:
            if not entry.is_working_day():
                continue  # Skip weekends/holidays
            
            user_id = entry.user_id
            if user_id not in user_stats:
                user_stats[user_id] = {
                    'total_scheduled': 0.0,
                    'total_available': 0.0,
                    'total_interactions': 0.0,
                    'total_productive': 0.0,
                    'working_days': 0
                }
            
            user_stats[user_id]['total_scheduled'] += entry.scheduled_time or 0
            user_stats[user_id]['total_available'] += entry.available_time or 0
            user_stats[user_id]['total_interactions'] += entry.interactions_time or 0
            user_stats[user_id]['total_productive'] += entry.productive_time or 0
            user_stats[user_id]['working_days'] += 1
        
        # Calculate averages
        for user_id, stats in user_stats.items():
            days = stats['working_days']
            if days > 0:
                stats['avg_scheduled_per_day'] = stats['total_scheduled'] / days
                stats['avg_available_per_day'] = stats['total_available'] / days
                stats['avg_interactions_per_day'] = stats['total_interactions'] / days
                stats['avg_productive_per_day'] = stats['total_productive'] / days
        
        return user_stats
    
    def get_working_days_count(self) -> int:
        """Get total number of working days in the date range."""
        calendar_dates = self._get_calendar_dates()
        working_days = [date for date in calendar_dates if self._is_working_day(date)]
        return len(working_days)
    
    def get_weekend_days_count(self) -> int:
        """Get total number of weekend days in the date range."""
        calendar_dates = self._get_calendar_dates()
        weekend_days = [date for date in calendar_dates if not self._is_working_day(date)]
        return len(weekend_days)
    
    def _generate_wfm_factor(self, factor_name: str) -> float:
        """Generate a WFM factor (shrinkage, occupancy, utilization) with statistical variation."""
        params = self.config.WFM_PARAMS[factor_name]
        mean = params['mean']
        deviation = params['deviation']
        
        # Generate using normal distribution with bounds to ensure realistic values
        factor = np.random.normal(mean, deviation / 3)  # /3 to ensure ~99% within mean ± deviation
        
        # Ensure factor stays within reasonable bounds (0.1 to 1.0)
        factor = max(0.1, min(1.0, factor))
        
        return factor
    
    def _get_calendar_dates_for_user(self, user_start_date: datetime) -> List[datetime]:
        """Get calendar dates starting from user's start date."""
        start_date = max(self.config.START_DATE, user_start_date)
        dates = []
        current_date = start_date
        
        while current_date <= self.config.END_DATE:
            dates.append(current_date)
            current_date += timedelta(days=1)
        
        return dates