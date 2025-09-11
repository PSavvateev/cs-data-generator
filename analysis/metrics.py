"""
Analysis and reporting module for generated data.
"""

import pandas as pd
from typing import Dict


class DataAnalyzer:
    """Performs analysis on generated datasets."""
    
    def __init__(self, config):
        self.config = config
    
    def generate_handle_time_analysis(self, interactions_df: pd.DataFrame, 
                                    tickets_df: pd.DataFrame) -> None:
        """Display handle time analysis by symptom category."""
        print("\n--- HANDLE TIME ANALYSIS BY SYMPTOM CATEGORY ---")
        
        for channel in ['email', 'phone', 'chat']:
            channel_data = interactions_df[interactions_df['channel'] == channel]
            if len(channel_data) > 0:
                print(f"\n{channel.upper()} Channel:")
                symptom_analysis = channel_data.merge(
                    tickets_df[['ticket_id', 'symptom_cat']], on='ticket_id'
                )
                
                for symptom in self.config.SYMPTOM_HANDLE_TIME_MODIFIERS.keys():
                    symptom_data = symptom_analysis[symptom_analysis['symptom_cat'] == symptom]
                    if len(symptom_data) > 0:
                        avg_handle = symptom_data['handle_time'].mean()
                        modifier = self.config.SYMPTOM_HANDLE_TIME_MODIFIERS[symptom]
                        print(f"  {symptom}: {avg_handle:.2f} min (modifier: {modifier})")
                
                overall_avg = channel_data['handle_time'].mean()
                print(f"  Overall {channel} average: {overall_avg:.2f} min")
    
    def generate_fcr_analysis(self, tickets_df: pd.DataFrame) -> None:
        """Display FCR analysis by symptom category."""
        print("\n--- FCR ANALYSIS BY SYMPTOM CATEGORY ---")
        
        for symptom in self.config.SYMPTOM_FCR_RATES.keys():
            symptom_tickets = tickets_df[tickets_df['symptom_cat'] == symptom]
            if len(symptom_tickets) > 0:
                actual_fcr = symptom_tickets['fcr'].mean()
                target_fcr = self.config.SYMPTOM_FCR_RATES[symptom]['mean']
                print(f"{symptom}: {actual_fcr:.1%} (target: {target_fcr:.1%})")
        
        overall_fcr = tickets_df['fcr'].mean()
        print(f"Overall FCR: {overall_fcr:.1%}")
    
    def generate_cpc_analysis(self, tickets_df: pd.DataFrame, 
                            interactions_df: pd.DataFrame) -> None:
        """Display CPC analysis by symptom category."""
        print("\n--- CONTACTS PER CASE (CPC) ANALYSIS BY SYMPTOM CATEGORY ---")
        
        ticket_interaction_count = interactions_df.groupby('ticket_id').size().reset_index(name='interaction_count')
        ticket_cpc_analysis = tickets_df.merge(ticket_interaction_count, on='ticket_id')
        
        for symptom in self.config.SYMPTOM_CPC_PARAMS.keys():
            symptom_tickets = ticket_cpc_analysis[ticket_cpc_analysis['symptom_cat'] == symptom]
            if len(symptom_tickets) > 0:
                actual_cpc = symptom_tickets['interaction_count'].mean()
                target_cpc = self.config.SYMPTOM_CPC_PARAMS[symptom]['mean']
                min_cpc = symptom_tickets['interaction_count'].min()
                max_cpc = symptom_tickets['interaction_count'].max()
                print(f"{symptom}: {actual_cpc:.2f} avg (target: {target_cpc:.1f}, range: {min_cpc}-{max_cpc})")
        
        overall_cpc = ticket_cpc_analysis['interaction_count'].mean()
        print(f"Overall CPC: {overall_cpc:.2f}")
    
    def display_sample_data(self, datasets: Dict[str, pd.DataFrame]) -> None:
        """Display sample data from each dataset."""
        print("\n--- SAMPLE DATA ---")
        
        print("Users table sample:")
        print(datasets['users'].head(3))
        
        print("\nCustomers table sample:")
        print(datasets['customers'].head(3))
        
        print("\nTickets table sample:")
        print(datasets['tickets'].head(3))
        
        print("\nInteractions table sample:")
        print(datasets['interactions'].head(3))
    
    def generate_all_reports(self, datasets: Dict[str, pd.DataFrame]) -> None:
        """Generate all analysis reports."""
        self.generate_handle_time_analysis(datasets['interactions'], datasets['tickets'])
        self.generate_fcr_analysis(datasets['tickets'])
        self.generate_cpc_analysis(datasets['tickets'], datasets['interactions'])
        self.display_sample_data(datasets)


