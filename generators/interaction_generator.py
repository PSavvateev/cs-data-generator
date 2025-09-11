"""
Interaction data generator.
"""

import random
import pandas as pd
from datetime import timedelta
from typing import List
from generators.base_generator import BaseGenerator
from models.entities import Interaction, ModelValidator
from utils.utils import (
    generate_cpc_for_symptom, generate_value_with_avg, 
    generate_daily_time, random_date
)


class InteractionGenerator(BaseGenerator):
    """Generates interaction data using Interaction model."""
    
    def generate(self, tickets_df: pd.DataFrame, users_df: pd.DataFrame, 
                 customers_df: pd.DataFrame) -> pd.DataFrame:
        """Generate interaction data using Interaction models."""
        interactions = []
        interaction_id_counter = 1
        validation_errors = []

        for idx, row in tickets_df.iterrows():
            ticket_id = row['ticket_id']
            channel = row['origin']
            fcr = row['fcr']
            ticket_symptom_cat = row['symptom_cat']

            num_interactions = generate_cpc_for_symptom(
                ticket_symptom_cat, fcr, self.config.SYMPTOM_CPC_PARAMS
            )

            ticket_created = pd.to_datetime(row['ticket_created'])
            # protect against NaT
            if pd.isna(ticket_created):
                ticket_created = random_date(self.config.START_DATE, self.config.END_DATE)

            # latest allowed interaction = ticket_created + MAX_INTERACTION_SPAN_HOURS
            latest_allowed = min(
                self.config.END_DATE, 
                ticket_created + timedelta(hours=self.config.MAX_INTERACTION_SPAN_HOURS)
            )

            for i in range(num_interactions):
                interaction_id = f"INT-{interaction_id_counter:06d}"
                interaction_id_counter += 1

                customer_id = random.randint(1, len(customers_df))
                handled_by = random.randint(1, len(users_df))

                # pick random second between created and latest_allowed (if equal, use created)
                if ticket_created >= latest_allowed:
                    interaction_created = ticket_created
                else:
                    total_seconds = int((latest_allowed - ticket_created).total_seconds())
                    rnd_seconds = random.randrange(total_seconds + 1)
                    interaction_created = ticket_created + timedelta(seconds=rnd_seconds)
                    # apply daily peak hour pattern (keeps date but sets hour/min/sec)
                    interaction_created = generate_daily_time(
                        interaction_created, 
                        self.config.PEAK_DISTRIBUTION,
                        self.config.ACTIVE_HOURS
                    )

                symptom_modifier = self.config.SYMPTOM_HANDLE_TIME_MODIFIERS[ticket_symptom_cat]
                handle_time = generate_value_with_avg(
                    self.config.HANDLE_TIME_PARAMS[channel], symptom_modifier
                )
                speed_answer = generate_value_with_avg(self.config.SPEED_ANSWER_PARAMS[channel])

                interaction_handled = interaction_created + timedelta(minutes=handle_time)

                # Create Interaction model
                interaction = Interaction(
                    interaction_id=interaction_id,
                    channel=channel,
                    customer_id=customer_id,
                    interaction_created=interaction_created,
                    handle_time=handle_time,
                    speed_of_answer=speed_answer,
                    interaction_handled=interaction_handled,
                    handled_by=handled_by,
                    subject="",
                    body="",
                    ticket_id=ticket_id
                )
                
                # Validate the interaction model
                errors = ModelValidator.validate_interaction(interaction)
                if errors:
                    validation_errors.extend([f"Interaction {interaction_id}: {error}" for error in errors])
                
                interactions.append(interaction)
        
        # Report validation errors if any
        if validation_errors:
            print(f"Warning: {len(validation_errors)} validation errors found:")
            for error in validation_errors[:5]:  # Show first 5 errors
                print(f"  - {error}")
            if len(validation_errors) > 5:
                print(f"  ... and {len(validation_errors) - 5} more")

        # Convert to DataFrame
        df = Interaction.to_dataframe(interactions)
        
        expected_columns = ['interaction_id', 'channel', 'customer_id', 'interaction_created', 
                           'handle_time', 'speed_of_answer', 'interaction_handled', 'handled_by', 
                           'subject', 'body', 'ticket_id']
        self._validate_output(df, expected_columns)
        self._log_generation_stats(df, "Interactions")
        
        return df
    
    def generate_models(self, tickets_df: pd.DataFrame, users_df: pd.DataFrame, 
                       customers_df: pd.DataFrame) -> List[Interaction]:
        """Generate interaction data and return as list of Interaction models."""
        # Generate DataFrame first, then convert to models
        df = self.generate(tickets_df, users_df, customers_df)
        
        interactions = []
        for _, row in df.iterrows():
            interaction = Interaction(
                interaction_id=row['interaction_id'],
                channel=row['channel'],
                customer_id=row['customer_id'],
                interaction_created=pd.to_datetime(row['interaction_created']),
                handle_time=row['handle_time'],
                speed_of_answer=row['speed_of_answer'],
                interaction_handled=pd.to_datetime(row['interaction_handled']),
                handled_by=row['handled_by'],
                subject=row['subject'],
                body=row['body'],
                ticket_id=row['ticket_id']
            )
            interactions.append(interaction)
        
        return interactions
    
    def analyze_channel_performance(self, interactions: List[Interaction]) -> dict:
        """Analyze performance metrics by channel using Interaction models."""
        channel_stats = {}
        
        for interaction in interactions:
            channel = interaction.channel
            if channel not in channel_stats:
                channel_stats[channel] = {
                    'total_interactions': 0,
                    'total_handle_time': 0.0,
                    'total_speed_answer': 0.0
                }
            
            channel_stats[channel]['total_interactions'] += 1
            channel_stats[channel]['total_handle_time'] += interaction.handle_time
            channel_stats[channel]['total_speed_answer'] += interaction.speed_of_answer
        
        # Calculate averages
        for channel, stats in channel_stats.items():
            count = stats['total_interactions']
            stats['avg_handle_time'] = stats['total_handle_time'] / count
            stats['avg_speed_answer'] = stats['total_speed_answer'] / count
        
        return channel_stats
    
    def get_interactions_by_channel(self, interactions: List[Interaction], channel: str) -> List[Interaction]:
        """Filter interactions by channel using Interaction models."""
        return [interaction for interaction in interactions if interaction.channel == channel]
    
    def get_email_interactions(self, interactions: List[Interaction]) -> List[Interaction]:
        """Get email interactions using Interaction model methods."""
        return [interaction for interaction in interactions if interaction.is_email()]
    
    def get_phone_interactions(self, interactions: List[Interaction]) -> List[Interaction]:
        """Get phone interactions using Interaction model methods."""
        return [interaction for interaction in interactions if interaction.is_phone()]
    
    def get_chat_interactions(self, interactions: List[Interaction]) -> List[Interaction]:
        """Get chat interactions using Interaction model methods."""
        return [interaction for interaction in interactions if interaction.is_chat()]