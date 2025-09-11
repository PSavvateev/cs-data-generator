"""
Data exporter that saves files to exports/ folder.
"""

import os
import pandas as pd
from typing import Dict


class DataExporter:
    """Handles data export functionality."""
    
    def __init__(self):
        """Initialize DataExporter and create exports directory."""
        self.export_dir = "exports"
        if not os.path.exists(self.export_dir):
            os.makedirs(self.export_dir)
    
    def export_to_csv(self, datasets: Dict[str, pd.DataFrame]) -> None:
        """Export all datasets to CSV files in exports/ folder."""
        file_mapping = {
            'users': 'users_table.csv',
            'customers': 'customers_table.csv',
            'tickets': 'tickets_table.csv',
            'interactions': 'interactions_table.csv',
            'calls': 'calls_table.csv',
            'chats': 'chats_table.csv'
        }
        
        print(f"\n--- EXPORTING DATA TO CSV FILES (exports/) ---")
        
        for dataset_name, filename in file_mapping.items():
            if dataset_name in datasets:
                filepath = os.path.join(self.export_dir, filename)
                df = datasets[dataset_name]
                df.to_csv(filepath, index=False)
                print(f"✓ Exported {len(df)} records to {filepath}")
        
        print("Export completed!")
    
    def export_to_excel(self, datasets: Dict[str, pd.DataFrame], 
                       filename: str = 'customer_support_data.xlsx') -> None:
        """Export all datasets to Excel file in exports/ folder."""
        filepath = os.path.join(self.export_dir, filename)
        
        try:
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                for dataset_name, df in datasets.items():
                    df.to_excel(writer, sheet_name=dataset_name, index=False)
            
            print(f"✓ Exported Excel file to {filepath}")
        except Exception as e:
            print(f"✗ Failed to export Excel: {e}")