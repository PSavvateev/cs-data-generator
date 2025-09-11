"""
Base generator class for all data generators.
"""

from abc import ABC, abstractmethod
from faker import Faker
import pandas as pd
from config.settings import Config


class BaseGenerator(ABC):
    """Abstract base class for all data generators."""
    
    def __init__(self, config: Config):
        """Initialize the generator with configuration."""
        self.config = config
        self.faker = Faker()
    
    @abstractmethod
    def generate(self, *args, **kwargs) -> pd.DataFrame:
        """Generate data and return as DataFrame."""
        pass
    
    def _validate_output(self, df: pd.DataFrame, expected_columns: list) -> None:
        """Validate that the generated DataFrame has expected structure."""
        missing_columns = set(expected_columns) - set(df.columns)
        if missing_columns:
            raise ValueError(f"Missing columns in generated data: {missing_columns}")
        
        if df.empty:
            raise ValueError("Generated DataFrame is empty")
    
    def _log_generation_stats(self, df: pd.DataFrame, entity_name: str) -> None:
        """Log statistics about generated data."""
        print(f"{entity_name} dataset: {len(df)} records")