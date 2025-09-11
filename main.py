#!/usr/bin/env python3
"""
Main entry point for the data generator.
"""

from orchestrator import DataGenerationOrchestrator
from config.settings import Config

def main():
    """Main function to run the data generation process."""
    print("--- Data Generation Workflow ---")
    
    # Load configuration
    config = Config()
    
    # Create and run orchestrator
    orchestrator = DataGenerationOrchestrator(config)
    datasets = orchestrator.generate_all()
    
    # Export data
    orchestrator.export_data(datasets)
    
    # Generate analysis reports
    orchestrator.generate_analysis_reports(datasets)
    
    print("\nData generation completed successfully!")

if __name__ == '__main__':
    main()