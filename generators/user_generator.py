"""
User data generator.
"""

import pandas as pd
from typing import List
from generators.base_generator import BaseGenerator
from models.entities import User, ModelValidator
from utils.utils import random_date_range, calculate_hourly_rate
from datetime import datetime


class UserGenerator(BaseGenerator):
    """Generates user/agent data using User model."""
    
    def generate(self, count: int = None) -> pd.DataFrame:
        """Generate user data using User models."""
        if count is None:
            count = self.config.UNIQUE_AGENTS
        
        users = []
        validation_errors = []
        
        for i in range(count):
            user_id = i + 1
            full_name = self.faker.name()
            first_name, last_name = full_name.split(' ', 1)
            
            # Most people have FTE = 1, 2-3 people have FTE = 0.75
            fte = 0.75 if i < 2 else 1.0
            
            position = 'support_agent'
            start_date = random_date_range(datetime(2022, 1, 1), datetime(2024, 12, 31))
            status = 'active'
            hourly_rate_eur = calculate_hourly_rate(start_date)
            
            # Create User model
            user = User(
                id=user_id,
                full_name=full_name,
                first_name=first_name,
                last_name=last_name,
                fte=fte,
                position=position,
                start_date=start_date.strftime('%Y-%m-%d'),
                status=status,
                hourly_rate_eur=hourly_rate_eur
            )
            
            # Validate the user model
            errors = ModelValidator.validate_user(user)
            if errors:
                validation_errors.extend([f"User {user_id}: {error}" for error in errors])
            
            users.append(user)
        
        # Report validation errors if any
        if validation_errors:
            print(f"Warning: {len(validation_errors)} validation errors found:")
            for error in validation_errors[:5]:  # Show first 5 errors
                print(f"  - {error}")
            if len(validation_errors) > 5:
                print(f"  ... and {len(validation_errors) - 5} more")
        
        # Convert to DataFrame
        df = User.to_dataframe(users)
        
        expected_columns = ['id', 'full_name', 'first_name', 'last_name', 'fte', 'position', 
                           'start_date', 'status', 'hourly_rate_eur']
        self._validate_output(df, expected_columns)
        self._log_generation_stats(df, "Users")
        
        return df
    
    def generate_models(self, count: int = None) -> List[User]:
        """Generate user data and return as list of User models."""
        if count is None:
            count = self.config.UNIQUE_AGENTS
        
        users = []
        for i in range(count):
            user_id = i + 1
            full_name = self.faker.name()
            first_name, last_name = full_name.split(' ', 1)
            
            fte = 0.75 if i < 2 else 1.0
            position = 'support_agent'
            start_date = random_date_range(datetime(2022, 1, 1), datetime(2024, 12, 31))
            status = 'active'
            hourly_rate_eur = calculate_hourly_rate(start_date)
            
            user = User(
                id=user_id,
                full_name=full_name,
                first_name=first_name,
                last_name=last_name,
                fte=fte,
                position=position,
                start_date=start_date.strftime('%Y-%m-%d'),
                status=status,
                hourly_rate_eur=hourly_rate_eur
            )
            
            users.append(user)
        
        print(f"Generated {len(users)} User models")
        return users