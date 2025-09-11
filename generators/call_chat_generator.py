"""
Call and Chat data generators.
"""

import random
import pandas as pd
import numpy as np
from datetime import timedelta
from typing import List
from generators.base_generator import BaseGenerator
from models.entities import Call, Chat
from utils.utils import random_date, generate_daily_time, truncated_normal


class CallGenerator(BaseGenerator):
    """Generates call data including abandoned calls using Call model."""
    
    def generate(self, interactions_df: pd.DataFrame) -> pd.DataFrame:
        """Generate call data based on phone interactions using Call models."""
        phone_interactions = interactions_df[interactions_df['channel'] == 'phone']
        calls = self._build_call_models('calls', phone_interactions, self.config.ABANDONED_PARAMS["calls"])
        
        # Convert to DataFrame
        df = Call.to_dataframe(calls)
        
        expected_columns = ['id', 'initialized', 'answered', 'abandoned', 'is_abandoned']
        self._validate_output(df, expected_columns)
        answered_count = len([c for c in calls if not c.was_abandoned()])
        abandoned_count = len([c for c in calls if c.was_abandoned()])
        print(f"Calls dataset: {len(df)} (answered={answered_count}, abandoned={abandoned_count})")
        
        return df
    
    def generate_models(self, interactions_df: pd.DataFrame) -> List[Call]:
        """Generate call data and return as list of Call models."""
        phone_interactions = interactions_df[interactions_df['channel'] == 'phone']
        return self._build_call_models('calls', phone_interactions, self.config.ABANDONED_PARAMS["calls"])
    
    def _build_call_models(self, channel: str, base_df: pd.DataFrame, params: dict) -> List[Call]:
        """Build call models with answered and abandoned calls."""
        calls = []
        
        # Abandoned rate sampling
        rate = np.random.normal(params["avg"], params["sd"])
        rate = max(params["low"], min(params["high"], rate))

        # Answered calls
        for _, row in base_df.iterrows():
            init_time = generate_daily_time(
                row['interaction_created'], 
                self.config.PEAK_DISTRIBUTION,
                self.config.ACTIVE_HOURS
            )
            ans_time = init_time + timedelta(seconds=row['speed_of_answer'])
            
            call = Call(
                id=f"{channel[:3].upper()}-{row['interaction_id']}",
                initialized=init_time,
                answered=ans_time,
                abandoned=None,
                is_abandoned=0
            )
            calls.append(call)

        # Abandoned calls
        num_abandoned = int(len(base_df) * rate)
        for i in range(num_abandoned):
            base_time = random_date(self.config.START_DATE, self.config.END_DATE)
            init_time = generate_daily_time(
                base_time, 
                self.config.PEAK_DISTRIBUTION,
                self.config.ACTIVE_HOURS
            )
            wait_time = int(truncated_normal(
                self.config.ABANDONED_WAIT_PARAMS["avg"],
                (self.config.ABANDONED_WAIT_PARAMS["high"] - self.config.ABANDONED_WAIT_PARAMS["low"]) / 6,
                self.config.ABANDONED_WAIT_PARAMS["low"],
                self.config.ABANDONED_WAIT_PARAMS["high"]
            ))
            abd_time = init_time + timedelta(seconds=wait_time)
            
            call = Call(
                id=f"{channel[:3].upper()}-ABD-{i+1:06d}",
                initialized=init_time,
                answered=None,
                abandoned=abd_time,
                is_abandoned=1
            )
            calls.append(call)

        return calls
    
    def analyze_abandonment_rates(self, calls: List[Call]) -> dict:
        """Analyze call abandonment rates using Call models."""
        total_calls = len(calls)
        abandoned_calls = len([call for call in calls if call.was_abandoned()])
        answered_calls = total_calls - abandoned_calls
        
        # Calculate average wait times for abandoned calls
        abandoned_wait_times = [
            call.get_wait_time_seconds() 
            for call in calls 
            if call.was_abandoned() and call.get_wait_time_seconds() is not None
        ]
        
        avg_abandoned_wait_time = sum(abandoned_wait_times) / len(abandoned_wait_times) if abandoned_wait_times else 0
        
        return {
            'total_calls': total_calls,
            'answered_calls': answered_calls,
            'abandoned_calls': abandoned_calls,
            'abandonment_rate': abandoned_calls / total_calls if total_calls > 0 else 0,
            'avg_abandoned_wait_time_seconds': avg_abandoned_wait_time
        }


class ChatGenerator(BaseGenerator):
    """Generates chat data including abandoned chats using Chat model."""
    
    def generate(self, interactions_df: pd.DataFrame) -> pd.DataFrame:
        """Generate chat data based on chat interactions using Chat models."""
        chat_interactions = interactions_df[interactions_df['channel'] == 'chat']
        chats = self._build_chat_models('chats', chat_interactions, self.config.ABANDONED_PARAMS["chats"])
        
        # Convert to DataFrame
        df = Chat.to_dataframe(chats)
        
        expected_columns = ['id', 'initialized', 'answered', 'abandoned', 'is_abandoned']
        self._validate_output(df, expected_columns)
        answered_count = len([c for c in chats if not c.was_abandoned()])
        abandoned_count = len([c for c in chats if c.was_abandoned()])
        print(f"Chats dataset: {len(df)} (answered={answered_count}, abandoned={abandoned_count})")
        
        return df
    
    def generate_models(self, interactions_df: pd.DataFrame) -> List[Chat]:
        """Generate chat data and return as list of Chat models."""
        chat_interactions = interactions_df[interactions_df['channel'] == 'chat']
        return self._build_chat_models('chats', chat_interactions, self.config.ABANDONED_PARAMS["chats"])
    
    def _build_chat_models(self, channel: str, base_df: pd.DataFrame, params: dict) -> List[Chat]:
        """Build chat models with answered and abandoned chats."""
        chats = []
        
        # Abandoned rate sampling
        rate = np.random.normal(params["avg"], params["sd"])
        rate = max(params["low"], min(params["high"], rate))

        # Answered chats
        for _, row in base_df.iterrows():
            init_time = generate_daily_time(
                row['interaction_created'], 
                self.config.PEAK_DISTRIBUTION,
                self.config.ACTIVE_HOURS
            )
            ans_time = init_time + timedelta(seconds=row['speed_of_answer'])
            
            chat = Chat(
                id=f"{channel[:3].upper()}-{row['interaction_id']}",
                initialized=init_time,
                answered=ans_time,
                abandoned=None,
                is_abandoned=0
            )
            chats.append(chat)

        # Abandoned chats
        num_abandoned = int(len(base_df) * rate)
        for i in range(num_abandoned):
            base_time = random_date(self.config.START_DATE, self.config.END_DATE)
            init_time = generate_daily_time(
                base_time, 
                self.config.PEAK_DISTRIBUTION,
                self.config.ACTIVE_HOURS
            )
            wait_time = int(truncated_normal(
                self.config.ABANDONED_WAIT_PARAMS["avg"],
                (self.config.ABANDONED_WAIT_PARAMS["high"] - self.config.ABANDONED_WAIT_PARAMS["low"]) / 6,
                self.config.ABANDONED_WAIT_PARAMS["low"],
                self.config.ABANDONED_WAIT_PARAMS["high"]
            ))
            abd_time = init_time + timedelta(seconds=wait_time)
            
            chat = Chat(
                id=f"{channel[:3].upper()}-ABD-{i+1:06d}",
                initialized=init_time,
                answered=None,
                abandoned=abd_time,
                is_abandoned=1
            )
            chats.append(chat)

        return chats
    
    def analyze_abandonment_rates(self, chats: List[Chat]) -> dict:
        """Analyze chat abandonment rates using Chat models."""
        total_chats = len(chats)
        abandoned_chats = len([chat for chat in chats if chat.was_abandoned()])
        answered_chats = total_chats - abandoned_chats
        
        # Calculate average wait times for abandoned chats
        abandoned_wait_times = [
            chat.get_wait_time_seconds() 
            for chat in chats 
            if chat.was_abandoned() and chat.get_wait_time_seconds() is not None
        ]
        
        avg_abandoned_wait_time = sum(abandoned_wait_times) / len(abandoned_wait_times) if abandoned_wait_times else 0
        
        return {
            'total_chats': total_chats,
            'answered_chats': answered_chats,
            'abandoned_chats': abandoned_chats,
            'abandonment_rate': abandoned_chats / total_chats if total_chats > 0 else 0,
            'avg_abandoned_wait_time_seconds': avg_abandoned_wait_time
        }
    
    def compare_abandonment_with_calls(self, chats: List[Chat], calls: List[Call]) -> dict:
        """Compare chat and call abandonment rates using models."""
        chat_stats = self.analyze_abandonment_rates(chats)
        call_gen = CallGenerator(self.config)
        call_stats = call_gen.analyze_abandonment_rates(calls)
        
        return {
            'chat_abandonment_rate': chat_stats['abandonment_rate'],
            'call_abandonment_rate': call_stats['abandonment_rate'],
            'chat_avg_wait_time': chat_stats['avg_abandoned_wait_time_seconds'],
            'call_avg_wait_time': call_stats['avg_abandoned_wait_time_seconds'],
            'difference_in_rates': chat_stats['abandonment_rate'] - call_stats['abandonment_rate']
        }