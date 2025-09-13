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
    full_name: str
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

@dataclass
class WfmEntry:
    """Model for Workforce Management data."""
    date: str  # YYYY-MM-DD format
    user_id: int
    paid_time: Optional[float]
    scheduled_time: Optional[float]
    available_time: Optional[float]
    interactions_time: Optional[float]
    productive_time: Optional[float]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for DataFrame creation."""
        return asdict(self)
    
    @classmethod
    def to_dataframe(cls, wfm_entries: List['WfmEntry']) -> pd.DataFrame:
        """Convert list of WfmEntry objects to DataFrame."""
        return pd.DataFrame([entry.to_dict() for entry in wfm_entries])
    
    def is_working_day(self) -> bool:
        """Check if this entry is for a working day (has scheduled time)."""
        return self.scheduled_time is not None
    
    def is_weekend_or_holiday(self) -> bool:
        """Check if this entry is for a weekend or holiday."""
        return self.scheduled_time is None
    
@dataclass
class QaEntry:
    """Model for Quality Assurance evaluation data."""
    eval_id: str
    interaction_id: str  # Foreign key to interactions_table.interaction_id
    qa_score: float
    customer_critical: int  # 1/0 flag
    business_critical: int  # 1/0 flag
    compliance_critical: int  # 1/0 flag
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for DataFrame creation."""
        return asdict(self)
    
    @classmethod
    def to_dataframe(cls, qa_entries: List['QaEntry']) -> pd.DataFrame:
        """Convert list of QaEntry objects to DataFrame."""
        return pd.DataFrame([entry.to_dict() for entry in qa_entries])
    
    def has_critical_flags(self) -> bool:
        """Check if any critical flags are set."""
        return any([self.customer_critical, self.business_critical, self.compliance_critical])
    
    def is_perfect_score(self) -> bool:
        """Check if QA score is perfect (1.0)."""
        return self.qa_score == 1.0
    
    def get_critical_types(self) -> List[str]:
        """Get list of critical flag types that are set."""
        critical_types = []
        if self.customer_critical:
            critical_types.append('customer')
        if self.business_critical:
            critical_types.append('business')
        if self.compliance_critical:
            critical_types.append('compliance')
        return critical_types

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
    
    @staticmethod
    def validate_wfm_entry(wfm_entry: WfmEntry) -> List[str]:
        """Validate WFM entry data and return list of errors."""
        errors = []
        
        # Check if working day data is consistent
        if wfm_entry.is_working_day():
            if wfm_entry.paid_time is None:
                errors.append("Working day missing paid_time")
            if wfm_entry.available_time is None:
                errors.append("Working day missing available_time")
            if wfm_entry.interactions_time is None:
                errors.append("Working day missing interactions_time")
            if wfm_entry.productive_time is None:
                errors.append("Working day missing productive_time")
        else:
            # Weekend/holiday should have None for all time fields except date
            if wfm_entry.paid_time is not None:
                errors.append("Weekend/holiday should have None for paid_time")
            if wfm_entry.available_time is not None:
                errors.append("Weekend/holiday should have None for available_time")
            if wfm_entry.interactions_time is not None:
                errors.append("Weekend/holiday should have None for interactions_time")
            if wfm_entry.productive_time is not None:
                errors.append("Weekend/holiday should have None for productive_time")
        
        return errors
    
    @staticmethod
    def validate_qa_entry(qa_entry: QaEntry) -> List[str]:
        """Validate QA entry data and return list of errors."""
        errors = []
        
        # Check QA score is within valid range
        if qa_entry.qa_score < 0.0 or qa_entry.qa_score > 1.0:
            errors.append(f"Invalid qa_score: {qa_entry.qa_score}. Must be between 0.0 and 1.0.")
        
        # Check critical flags are 0 or 1
        for field_name, field_value in [
            ('customer_critical', qa_entry.customer_critical),
            ('business_critical', qa_entry.business_critical),
            ('compliance_critical', qa_entry.compliance_critical)
        ]:
            if field_value not in [0, 1]:
                errors.append(f"Invalid {field_name}: {field_value}. Must be 0 or 1.")
        
        # Check business rule: if any critical flag is set, qa_score must be 0
        if qa_entry.has_critical_flags() and qa_entry.qa_score != 0.0:
            errors.append("QA score must be 0.0 when any critical flag is set.")
        
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
    
    @staticmethod
    def create_wfm_entry_from_dict(data: Dict[str, Any]) -> WfmEntry:
        """Create WfmEntry model from dictionary."""
        return WfmEntry(**data)
    
    @staticmethod
    def create_qa_entry_from_dict(data: Dict[str, Any]) -> QaEntry:
        """Create QaEntry model from dictionary."""
        return QaEntry(**data)