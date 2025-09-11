"""
Data models for the customer support system.
"""

from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Optional, List, Dict, Any
import pandas as pd


@dataclass
class User:
    """Model for support agent/user data."""
    id: int
    first_name: str
    last_name: str
    fte: float
    position: str
    start_date: str  # YYYY-MM-DD format
    status: str
    hourly_rate_eur: float
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for DataFrame creation."""
        return asdict(self)
    
    @classmethod
    def to_dataframe(cls, users: List['User']) -> pd.DataFrame:
        """Convert list of User objects to DataFrame."""
        return pd.DataFrame([user.to_dict() for user in users])


@dataclass
class Customer:
    """Model for customer data."""
    id: int
    name: str
    email: str
    phone: str
    country: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for DataFrame creation."""
        return asdict(self)
    
    @classmethod
    def to_dataframe(cls, customers: List['Customer']) -> pd.DataFrame:
        """Convert list of Customer objects to DataFrame."""
        return pd.DataFrame([customer.to_dict() for customer in customers])


@dataclass
class Ticket:
    """Model for ticket data."""
    ticket_id: str
    origin: str
    symptom_cat: str
    symptom: str
    status: str
    product: str
    ticket_owner: int
    language: str
    fcr: int
    escalated: int
    ticket_created: datetime
    ticket_closed: Optional[datetime] = None
    last_interaction_time: Optional[datetime] = None
    resolution_after_last_interaction_hours: Optional[float] = None
    lifecycle_hours: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for DataFrame creation."""
        return asdict(self)
    
    @classmethod
    def to_dataframe(cls, tickets: List['Ticket']) -> pd.DataFrame:
        """Convert list of Ticket objects to DataFrame."""
        return pd.DataFrame([ticket.to_dict() for ticket in tickets])
    
    def is_closed(self) -> bool:
        """Check if ticket is closed."""
        return self.status == 'closed'
    
    def is_fcr(self) -> bool:
        """Check if ticket is First Contact Resolution."""
        return self.fcr == 1
    
    def is_escalated(self) -> bool:
        """Check if ticket was escalated."""
        return self.escalated == 1


@dataclass
class Interaction:
    """Model for interaction data."""
    interaction_id: str
    channel: str
    customer_id: int
    interaction_created: datetime
    handle_time: float
    speed_of_answer: float
    interaction_handled: datetime
    handled_by: int
    subject: str
    body: str
    ticket_id: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for DataFrame creation."""
        return asdict(self)
    
    @classmethod
    def to_dataframe(cls, interactions: List['Interaction']) -> pd.DataFrame:
        """Convert list of Interaction objects to DataFrame."""
        return pd.DataFrame([interaction.to_dict() for interaction in interactions])
    
    def get_duration_minutes(self) -> float:
        """Get interaction duration in minutes."""
        return self.handle_time
    
    def is_email(self) -> bool:
        """Check if interaction is email."""
        return self.channel == 'email'
    
    def is_phone(self) -> bool:
        """Check if interaction is phone."""
        return self.channel == 'phone'
    
    def is_chat(self) -> bool:
        """Check if interaction is chat."""
        return self.channel == 'chat'


@dataclass
class Call:
    """Model for call data."""
    id: str
    initialized: datetime
    answered: Optional[datetime]
    abandoned: Optional[datetime]
    is_abandoned: int
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for DataFrame creation."""
        return asdict(self)
    
    @classmethod
    def to_dataframe(cls, calls: List['Call']) -> pd.DataFrame:
        """Convert list of Call objects to DataFrame."""
        return pd.DataFrame([call.to_dict() for call in calls])
    
    def was_abandoned(self) -> bool:
        """Check if call was abandoned."""
        return self.is_abandoned == 1
    
    def get_wait_time_seconds(self) -> Optional[float]:
        """Get wait time in seconds for abandoned calls."""
        if self.was_abandoned() and self.abandoned:
            return (self.abandoned - self.initialized).total_seconds()
        return None


@dataclass
class Chat:
    """Model for chat data."""
    id: str
    initialized: datetime
    answered: Optional[datetime]
    abandoned: Optional[datetime]
    is_abandoned: int
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for DataFrame creation."""
        return asdict(self)
    
    @classmethod
    def to_dataframe(cls, chats: List['Chat']) -> pd.DataFrame:
        """Convert list of Chat objects to DataFrame."""
        return pd.DataFrame([chat.to_dict() for chat in chats])
    
    def was_abandoned(self) -> bool:
        """Check if chat was abandoned."""
        return self.is_abandoned == 1
    
    def get_wait_time_seconds(self) -> Optional[float]:
        """Get wait time in seconds for abandoned chats."""
        if self.was_abandoned() and self.abandoned:
            return (self.abandoned - self.initialized).total_seconds()
        return None


# Utility functions for model validation
class ModelValidator:
    """Validates data models for business rules."""
    
    @staticmethod
    def validate_user(user: User) -> List[str]:
        """Validate user data and return list of errors."""
        errors = []
        
        if user.fte < 0 or user.fte > 1:
            errors.append(f"Invalid FTE value: {user.fte}. Must be between 0 and 1.")
        
        if user.hourly_rate_eur < 0:
            errors.append(f"Invalid hourly rate: {user.hourly_rate_eur}. Must be positive.")
        
        if user.status not in ['active', 'inactive']:
            errors.append(f"Invalid status: {user.status}. Must be 'active' or 'inactive'.")
        
        return errors
    
    @staticmethod
    def validate_ticket(ticket: Ticket) -> List[str]:
        """Validate ticket data and return list of errors."""
        errors = []
        
        if ticket.fcr not in [0, 1]:
            errors.append(f"Invalid FCR value: {ticket.fcr}. Must be 0 or 1.")
        
        if ticket.escalated not in [0, 1]:
            errors.append(f"Invalid escalated value: {ticket.escalated}. Must be 0 or 1.")
        
        if ticket.status not in ['new', 'open', 'closed']:
            errors.append(f"Invalid status: {ticket.status}. Must be 'new', 'open', or 'closed'.")
        
        if ticket.is_closed() and ticket.ticket_closed is None:
            errors.append("Closed ticket must have a closure date.")
        
        if ticket.ticket_closed and ticket.ticket_closed < ticket.ticket_created:
            errors.append("Ticket closure date cannot be before creation date.")
        
        return errors
    
    @staticmethod
    def validate_interaction(interaction: Interaction) -> List[str]:
        """Validate interaction data and return list of errors."""
        errors = []
        
        if interaction.handle_time < 0:
            errors.append(f"Invalid handle time: {interaction.handle_time}. Must be positive.")
        
        if interaction.speed_of_answer < 0:
            errors.append(f"Invalid speed of answer: {interaction.speed_of_answer}. Must be positive.")
        
        if interaction.channel not in ['email', 'phone', 'chat']:
            errors.append(f"Invalid channel: {interaction.channel}. Must be 'email', 'phone', or 'chat'.")
        
        if interaction.interaction_handled < interaction.interaction_created:
            errors.append("Interaction handled time cannot be before creation time.")
        
        return errors


# Factory classes for creating models
class ModelFactory:
    """Factory for creating data models from raw data."""
    
    @staticmethod
    def create_user_from_dict(data: Dict[str, Any]) -> User:
        """Create User model from dictionary."""
        return User(**data)
    
    @staticmethod
    def create_ticket_from_dict(data: Dict[str, Any]) -> Ticket:
        """Create Ticket model from dictionary."""
        return Ticket(**data)
    
    @staticmethod
    def create_interaction_from_dict(data: Dict[str, Any]) -> Interaction:
        """Create Interaction model from dictionary."""
        return Interaction(**data)
    
    @staticmethod
    def create_models_from_dataframe(df: pd.DataFrame, model_class) -> List:
        """Create list of model objects from DataFrame."""
        return [model_class(**row.to_dict()) for _, row in df.iterrows()]