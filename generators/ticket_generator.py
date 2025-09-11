"""
Ticket data generator.
"""

import random
import pandas as pd
import numpy as np
from datetime import timedelta
from typing import List
from generators.base_generator import BaseGenerator
from models.entities import Ticket, ModelValidator
from utils.utils import (
    weighted_choice, weighted_choice_from_list, random_date,
    generate_fcr_for_symptom, generate_resolution_time
)


class TicketGenerator(BaseGenerator):
    """Generates ticket data using Ticket model."""
    
    def generate(self, customers_df: pd.DataFrame, users_df: pd.DataFrame, 
                 count: int = None) -> pd.DataFrame:
        """Generate ticket data using Ticket models."""
        if count is None:
            count = self.config.NUM_TICKETS
        
        tickets = []
        validation_errors = []
        
        for i in range(count):
            ticket_id = f"TKT-{i+1:05d}"
            ticket_owner_id = random.randint(1, len(users_df))
            customer_id = random.randint(1, len(customers_df))

            origin = weighted_choice(self.config.CHANNELS)
            product = weighted_choice(self.config.PRODUCTS)
            status = weighted_choice(self.config.STATUSES)
            
            # Get customer's country and map to language
            customer_country = customers_df.iloc[customer_id - 1]['country']
            language = self.config.COUNTRY_LANGUAGE_MAPPING[customer_country]
            
            symptom_cat, symptom = weighted_choice_from_list(self.config.SYMPTOMS)

            # Generate FCR based on symptom category
            fcr = generate_fcr_for_symptom(symptom_cat, self.config.SYMPTOM_FCR_RATES)
            escalated = 0
            if fcr == 0:
                escalated = np.random.choice([1, 0], p=[self.config.ESCALATION_RATE, 1-self.config.ESCALATION_RATE])

            created = random_date(self.config.START_DATE, self.config.END_DATE)
            closed = created + timedelta(days=random.randint(0, 10)) if status == 'closed' else None

            # Create Ticket model
            ticket = Ticket(
                ticket_id=ticket_id,
                origin=origin,
                symptom_cat=symptom_cat,
                symptom=symptom,
                status=status,
                product=product,
                ticket_owner=ticket_owner_id,
                language=language,
                fcr=fcr,
                escalated=escalated,
                ticket_created=created,
                ticket_closed=closed
            )
            
            # Validate the ticket model
            errors = ModelValidator.validate_ticket(ticket)
            if errors:
                validation_errors.extend([f"Ticket {ticket_id}: {error}" for error in errors])
            
            tickets.append(ticket)
        
        # Report validation errors if any
        if validation_errors:
            print(f"Warning: {len(validation_errors)} validation errors found:")
            for error in validation_errors[:5]:  # Show first 5 errors
                print(f"  - {error}")
            if len(validation_errors) > 5:
                print(f"  ... and {len(validation_errors) - 5} more")

        # Convert to DataFrame
        df = Ticket.to_dataframe(tickets)
        
        expected_columns = ['ticket_id', 'origin', 'symptom_cat', 'symptom',
                           'status', 'product', 'ticket_owner', 'language', 'fcr', 'escalated',
                           'ticket_created', 'ticket_closed']
        self._validate_output(df, expected_columns)
        self._log_generation_stats(df, "Tickets")
        
        return df
    
    def generate_models(self, customers_df: pd.DataFrame, users_df: pd.DataFrame, 
                       count: int = None) -> List[Ticket]:
        """Generate ticket data and return as list of Ticket models."""
        # Generate DataFrame first, then convert to models
        df = self.generate(customers_df, users_df, count)
        
        tickets = []
        for _, row in df.iterrows():
            ticket = Ticket(
                ticket_id=row['ticket_id'],
                origin=row['origin'],
                symptom_cat=row['symptom_cat'],
                symptom=row['symptom'],
                status=row['status'],
                product=row['product'],
                ticket_owner=row['ticket_owner'],
                language=row['language'],
                fcr=row['fcr'],
                escalated=row['escalated'],
                ticket_created=pd.to_datetime(row['ticket_created']),
                ticket_closed=pd.to_datetime(row['ticket_closed']) if pd.notna(row['ticket_closed']) else None
            )
            tickets.append(ticket)
        
        return tickets
    
    def update_closure_times(self, tickets_df: pd.DataFrame, 
                           interactions_df: pd.DataFrame) -> pd.DataFrame:
        """Update ticket closure times based on interactions."""
        # Ensure datetime types
        tickets_df['ticket_created'] = pd.to_datetime(tickets_df['ticket_created'])
        # Prepare new columns to inspect behaviour
        tickets_df['last_interaction_time'] = pd.NaT
        tickets_df['resolution_after_last_interaction_hours'] = np.nan
        tickets_df['lifecycle_hours'] = np.nan  # created -> closed

        for idx, row in tickets_df.iterrows():
            if row['status'] != 'closed':
                continue

            ticket_id = row['ticket_id']
            symptom_cat = row['symptom_cat']
            ticket_created_ts = pd.to_datetime(row['ticket_created'])

            # interactions for ticket
            ticket_interactions = interactions_df[interactions_df['ticket_id'] == ticket_id]

            if len(ticket_interactions) > 0:
                last_interaction_time = pd.to_datetime(ticket_interactions['interaction_handled']).max()
                if pd.isna(last_interaction_time):
                    last_interaction_time = ticket_created_ts
            else:
                # no interactions -> use creation as last_interaction_time
                last_interaction_time = ticket_created_ts

            # sample resolution hours once per ticket
            resolution_hours = generate_resolution_time(symptom_cat, self.config.SYMPTOM_RESOLUTION_TIME_PARAMS)

            # determine closed_time according to chosen policy
            if self.config.ANCHOR_CLOSURE_TO == 'last_interaction':
                closed_time = last_interaction_time + timedelta(hours=resolution_hours)
            elif self.config.ANCHOR_CLOSURE_TO == 'from_creation':
                closed_time = ticket_created_ts + timedelta(hours=resolution_hours)
            else:
                # safe fallback
                closed_time = last_interaction_time + timedelta(hours=resolution_hours)

            # safety: never close before creation
            if closed_time < ticket_created_ts:
                closed_time = ticket_created_ts + timedelta(hours=max(1.0, resolution_hours))

            # write back
            tickets_df.at[idx, 'ticket_closed'] = closed_time
            tickets_df.at[idx, 'last_interaction_time'] = last_interaction_time
            tickets_df.at[idx, 'resolution_after_last_interaction_hours'] = resolution_hours
            tickets_df.at[idx, 'lifecycle_hours'] = (pd.to_datetime(closed_time) - ticket_created_ts).total_seconds() / 3600.0

        print("Updated ticket closure times based on interactions")
        return tickets_df
    
    def analyze_fcr_by_symptom(self, tickets: List[Ticket]) -> dict:
        """Analyze FCR rates by symptom category using Ticket models."""
        symptom_fcr = {}
        
        for ticket in tickets:
            if ticket.symptom_cat not in symptom_fcr:
                symptom_fcr[ticket.symptom_cat] = {'total': 0, 'fcr_count': 0}
            
            symptom_fcr[ticket.symptom_cat]['total'] += 1
            if ticket.is_fcr():
                symptom_fcr[ticket.symptom_cat]['fcr_count'] += 1
        
        # Calculate FCR rates
        fcr_rates = {}
        for symptom, data in symptom_fcr.items():
            fcr_rates[symptom] = data['fcr_count'] / data['total'] if data['total'] > 0 else 0
        
        return fcr_rates