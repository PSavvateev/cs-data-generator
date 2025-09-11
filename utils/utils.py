"""
Utility functions for data generation.
"""

import random
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Any


def random_date(start: datetime, end: datetime) -> datetime:
    """Generate a random datetime between start and end that is NOT Sunday."""
    while True:
        delta = end - start
        int_delta = delta.days * 24 * 60 * 60
        random_second = random.randrange(int_delta)
        dt = start + timedelta(seconds=random_second)
        if dt.weekday() != 6:  # skip Sunday
            return dt


def random_date_range(start: datetime, end: datetime) -> datetime:
    """Generate a random date (without time) between start and end."""
    delta = end - start
    int_delta = delta.days
    random_day = random.randrange(int_delta)
    return start + timedelta(days=random_day)


def weighted_choice(weight_dict: Dict[str, float]) -> str:
    """Select a random item based on weights."""
    return random.choices(list(weight_dict.keys()), weights=list(weight_dict.values()), k=1)[0]


def weighted_choice_from_list(weighted_list: List[Tuple[str, str, float]]) -> Tuple[str, str]:
    """Select a random item from a list of (category, item, weight) tuples."""
    weights = [weight for _, _, weight in weighted_list]
    idx = random.choices(range(len(weighted_list)), weights=weights, k=1)[0]
    return weighted_list[idx][0], weighted_list[idx][1]


def truncated_normal(mean: float, sd: float, low: float, high: float) -> float:
    """Generate a value from truncated normal distribution."""
    val = np.random.normal(mean, sd)
    while val < low or val > high:
        val = np.random.normal(mean, sd)
    return round(val, 2)


def generate_value_with_avg(params: Tuple[float, float, float], symptom_modifier: float = 1.0) -> float:
    """Generate a value using average-based parameters with symptom modifier."""
    low, high, avg = params
    # Apply symptom modifier to average
    modified_avg = avg * symptom_modifier
    # Ensure modified average stays within bounds
    modified_avg = max(low, min(high, modified_avg))
    
    sd = (high - low) / 6  # 99% values in range
    return truncated_normal(modified_avg, sd, low, high)


def generate_daily_time(base_date: datetime, peak_distribution: Dict, active_hours: Tuple[int, int]) -> datetime:
    """Generate time with bi-modal distribution for peak traffic hours."""
    if np.random.rand() < peak_distribution["morning"]["weight"]:
        hour = int(np.random.normal(peak_distribution["morning"]["mean"], peak_distribution["morning"]["sd"]))
    else:
        hour = int(np.random.normal(peak_distribution["evening"]["mean"], peak_distribution["evening"]["sd"]))
    
    hour = max(active_hours[0], min(active_hours[1], hour))
    minute = random.randint(0, 59)
    second = random.randint(0, 59)
    return base_date.replace(hour=hour, minute=minute, second=second)


def calculate_hourly_rate(start_date: datetime) -> float:
    """Calculate hourly rate based on start date - longer tenure = higher rate."""
    current_date = datetime(2025, 8, 21)
    years_experience = (current_date - start_date).days / 365.25
    
    # Base rate 12-16 EUR, with experience bonus
    base_rate = random.uniform(12, 14)  # Base range
    experience_bonus = min(years_experience * 0.5, 2)  # Max 2 EUR bonus for experience
    
    hourly_rate = base_rate + experience_bonus
    return round(min(hourly_rate, 16), 2)  # Cap at 16 EUR


def generate_fcr_for_symptom(symptom_cat: str, symptom_fcr_rates: Dict) -> int:
    """Generate FCR value based on symptom category with deviation."""
    fcr_config = symptom_fcr_rates[symptom_cat]
    mean_rate = fcr_config['mean']
    deviation = fcr_config['deviation']
    
    # Generate rate with normal distribution around mean
    rate = np.random.normal(mean_rate, deviation / 3)  # /3 to ensure ~99% within ±deviation
    rate = max(0.0, min(1.0, rate))  # Clamp between 0 and 1

    # Convert to binary FCR decision
    return 1 if np.random.random() < rate else 0


def generate_cpc_for_symptom(symptom_cat: str, fcr: int, symptom_cpc_params: Dict) -> int:
    """Generate Contacts Per Case based on symptom category and FCR status."""
    if fcr == 1:
        return 1  # FCR cases always have exactly 1 contact
    
    # For non-FCR cases, use symptom-specific parameters
    cpc_config = symptom_cpc_params[symptom_cat]
    min_cpc = cpc_config['min']
    max_cpc = cpc_config['max']
    mean_cpc = cpc_config['mean']
    std_cpc = cpc_config['std']
    
    # Generate using normal distribution
    cpc = int(round(np.random.normal(mean_cpc, std_cpc)))
    
    # Ensure within bounds
    cpc = max(min_cpc, min(max_cpc, cpc))
    
    return cpc


def generate_resolution_time(symptom_cat: str, symptom_resolution_time_params: Dict) -> float:
    """Generate realistic resolution times clustered around mean."""
    config = symptom_resolution_time_params[symptom_cat]
    
    # Use truncated normal to stay within min/max
    mean = config['mean']
    std = max(config['std'], (config['max'] - config['min']) / 6)  # ensure some spread
    low = config['min']
    high = config['max']
    
    val = np.random.normal(mean, std)
    val = max(low, min(high, val))  # truncate

    # Round to 0.5 hour to create natural buckets
    val = round(val * 2) / 2
    return val