"""
Configuration settings for the data generator.
"""

from datetime import datetime
from dataclasses import dataclass
from typing import Dict, List, Tuple

@dataclass
class Config:
    """Main configuration class containing all generation parameters."""
    
    # Basic counts
    NUM_TICKETS: int = 25000
    UNIQUE_CUSTOMERS: int = 6000
    UNIQUE_AGENTS: int = 12
    
    # Date range
    START_DATE: datetime = datetime(2023, 9, 15)
    END_DATE: datetime = datetime(2025, 8, 21)
    
    # Behavior settings
    MAX_INTERACTION_SPAN_HOURS: int = 6
    ESCALATION_RATE: float = 0.12
    ANCHOR_CLOSURE_TO: str = 'last_interaction'  # or 'from_creation'
    
    # Random seed for reproducibility
    RANDOM_SEED: int = 42
    
    # Channels distribution
    CHANNELS: Dict[str, float] = None
    
    # Countries distribution
    COUNTRIES: Dict[str, float] = None
    
    # Country to language mapping
    COUNTRY_LANGUAGE_MAPPING: Dict[str, str] = None
    
    # Abandoned call/chat configuration
    ABANDONED_PARAMS: Dict[str, Dict[str, float]] = None
    
    # Abandoned wait times (seconds)
    ABANDONED_WAIT_PARAMS: Dict[str, int] = None
    
    # Daily peak call/chat times (24h format)
    PEAK_DISTRIBUTION: Dict[str, Dict[str, float]] = None
    ACTIVE_HOURS: Tuple[int, int] = (8, 22)
    
    # FCR rates by symptom category
    SYMPTOM_FCR_RATES: Dict[str, Dict[str, float]] = None
    
    # CPC parameters by symptom category
    SYMPTOM_CPC_PARAMS: Dict[str, Dict[str, float]] = None
    
    # Resolution time parameters by symptom
    SYMPTOM_RESOLUTION_TIME_PARAMS: Dict[str, Dict[str, float]] = None
    
    # Product distribution
    PRODUCTS: Dict[str, float] = None
    
    # Status distribution
    STATUSES: Dict[str, float] = None
    
    # Symptoms distribution
    SYMPTOMS: List[Tuple[str, str, float]] = None
    
    # Handle time parameters
    HANDLE_TIME_PARAMS: Dict[str, Tuple[float, float, float]] = None
    
    # Symptom category modifiers for handle time
    SYMPTOM_HANDLE_TIME_MODIFIERS: Dict[str, float] = None
    
    # Speed of answer parameters
    SPEED_ANSWER_PARAMS: Dict[str, Tuple[float, float, float]] = None
    
    def __post_init__(self):
        """Initialize default values that can't be set as class defaults."""
        if self.CHANNELS is None:
            self.CHANNELS = {'email': 0.3, 'phone': 0.4, 'chat': 0.3}
        
        if self.COUNTRIES is None:
            self.COUNTRIES = {
                'United Kingdom': 0.30,
                'Germany': 0.18,
                'Austria': 0.12,
                'Netherlands': 0.10,
                'France': 0.15,
                'Belgium': 0.05
            }
        
        if self.COUNTRY_LANGUAGE_MAPPING is None:
            self.COUNTRY_LANGUAGE_MAPPING = {
                'United Kingdom': 'english',
                'Netherlands': 'english',
                'France': 'french',
                'Belgium': 'french',
                'Germany': 'german',
                'Austria': 'german'
            }
        
        if self.ABANDONED_PARAMS is None:
            self.ABANDONED_PARAMS = {
                "calls": {"avg": 0.07, "sd": 0.03, "low": 0.0, "high": 0.17},
                "chats": {"avg": 0.10, "sd": 0.03, "low": 0.0, "high": 0.17}
            }
        
        if self.ABANDONED_WAIT_PARAMS is None:
            self.ABANDONED_WAIT_PARAMS = {"low": 3, "high": 180, "avg": 60}
        
        if self.PEAK_DISTRIBUTION is None:
            self.PEAK_DISTRIBUTION = {
                "morning": {"mean": 9.5, "sd": 0.5, "weight": 0.6},
                "evening": {"mean": 20, "sd": 0.7, "weight": 0.4}
            }
        
        if self.SYMPTOM_FCR_RATES is None:
            self.SYMPTOM_FCR_RATES = {
                'troubleshooting': {'mean': 0.50, 'deviation': 0.03},
                'finance': {'mean': 0.00, 'deviation': 0.01},
                'logistics': {'mean': 0.43, 'deviation': 0.04},
                'rma': {'mean': 0.10, 'deviation': 0.12},
                'product': {'mean': 1.00, 'deviation': 0.12},
                'complaint': {'mean': 0.20, 'deviation': 0.12}
            }
        
        if self.SYMPTOM_CPC_PARAMS is None:
            self.SYMPTOM_CPC_PARAMS = {
                'troubleshooting': {'min': 1, 'max': 3, 'mean': 1.5, 'std': 0.5},
                'finance': {'min': 1, 'max': 4, 'mean': 2.3, 'std': 1.2},
                'logistics': {'min': 1, 'max': 4, 'mean': 1.8, 'std': 1.1},
                'rma': {'min': 1, 'max': 11, 'mean': 4.1, 'std': 2.0},
                'product': {'min': 1, 'max': 3, 'mean': 1.2, 'std': 0.4},
                'complaint': {'min': 1, 'max': 2, 'mean': 1.1, 'std': 0.1}
            }
        
        if self.SYMPTOM_RESOLUTION_TIME_PARAMS is None:
            self.SYMPTOM_RESOLUTION_TIME_PARAMS = {
                'troubleshooting': {'min': 4, 'max': 52, 'mean': 38, 'std': 10},
                'finance': {'min': 3, 'max': 72, 'mean': 50, 'std': 12},
                'logistics': {'min': 6, 'max': 68, 'mean': 49, 'std': 16},
                'rma': {'min': 8, 'max': 168, 'mean': 73, 'std': 32},
                'product': {'min': 2, 'max': 34, 'mean': 28, 'std': 10},
                'complaint': {'min': 1, 'max': 68, 'mean': 54, 'std': 24}
            }
        
        if self.PRODUCTS is None:
            self.PRODUCTS = {
                'on-ear_headphones': 0.25,
                'eardrop_headphones': 0.30,
                'speaker_20wt': 0.15,
                'speaker_40wt': 0.10,
                'speaker_flagship': 0.03,
                'amplifier': 0.10,
                'turntable': 0.07
            }
        
        if self.STATUSES is None:
            self.STATUSES = {'new': 0.02, 'open': 0.08, 'closed': 0.90}
        
        if self.SYMPTOMS is None:
            self.SYMPTOMS = [
                ('troubleshooting', 'bluetooth connection', 0.08),
                ('troubleshooting', 'power supply', 0.14),
                ('troubleshooting', 'firmware', 0.02),
                ('troubleshooting', 'sound resolution', 0.06),
                ('logistics', 'status of the order', 0.15),
                ('logistics', 'lost package', 0.05),
                ('rma', 'replacement', 0.12),
                ('rma', 'return', 0.08),
                ('finance', 'unsuccessful payment', 0.04),
                ('finance', 'payment details', 0.06),
                ('product', 'product consulting / information', 0.10),
                ('complaint', 'product complaint', 0.08),
                ('complaint', 'service complaint', 0.02)
            ]
        
        if self.HANDLE_TIME_PARAMS is None:
            self.HANDLE_TIME_PARAMS = {
                'email': (0.5, 45, 7),
                'phone': (0.7, 8, 5.5),
                'chat': (1, 60, 13)
            }
        
        if self.SYMPTOM_HANDLE_TIME_MODIFIERS is None:
            self.SYMPTOM_HANDLE_TIME_MODIFIERS = {
                'troubleshooting': 1.40,
                'logistics': 1.00,
                'rma': 1.15,
                'finance': 0.80,
                'product': 0.50,
                'complaint': 0.60
            }
        
        if self.SPEED_ANSWER_PARAMS is None:
            self.SPEED_ANSWER_PARAMS = {
                'email': (0.1, 50, 17),  # hours
                'phone': (3, 360, 60),   # seconds
                'chat': (5, 360, 85)     # seconds
            }