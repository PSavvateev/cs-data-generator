"""
QA (Quality Assurance) data generator.
"""

import pandas as pd
import numpy as np
import random
from typing import List
from generators.base_generator import BaseGenerator
from models.entities import QaEntry, ModelValidator


class QaGenerator(BaseGenerator):
    """Generates Quality Assurance evaluation data."""
    
    def generate(self, interactions_df: pd.DataFrame) -> pd.DataFrame:
        """Generate QA data based on sample of interactions."""
        qa_entries = []
        validation_errors = []
        
        # Calculate number of evaluations based on sample size
        total_interactions = len(interactions_df)
        num_evaluations = int(total_interactions * self.config.SAMPLE_SIZE)
        
        if num_evaluations == 0:
            print("Warning: No QA evaluations generated due to small sample size")
            return pd.DataFrame(columns=['eval_id', 'interaction_id', 'qa_score', 
                                       'customer_critical', 'business_critical', 'compliance_critical'])
        
        # Sample interactions for QA evaluation (random sampling distributed across timeline)
        sampled_interactions = self._sample_interactions_across_timeline(interactions_df, num_evaluations)
        
        for i, interaction_row in sampled_interactions.iterrows():
            eval_id = f"QA-{i+1:06d}"
            interaction_id = interaction_row['interaction_id']
            
            # Generate critical flags independently
            customer_critical = self._generate_critical_flag(self.config.CUSTOMER_CRITICAL_PROB)
            business_critical = self._generate_critical_flag(self.config.BUSINESS_CRITICAL_PROB)
            compliance_critical = self._generate_critical_flag(self.config.COMPLIANCE_CRITICAL_PROB)
            
            # Generate QA score based on critical flags
            if any([customer_critical, business_critical, compliance_critical]):
                qa_score = 0.0  # Rule: if any critical flag exists, qa_score = 0
            else:
                qa_score = self._generate_qa_score()
            
            # Create QA entry
            qa_entry = QaEntry(
                eval_id=eval_id,
                interaction_id=interaction_id,
                qa_score=qa_score,
                customer_critical=customer_critical,
                business_critical=business_critical,
                compliance_critical=compliance_critical
            )
            
            # Validate the entry
            errors = ModelValidator.validate_qa_entry(qa_entry)
            if errors:
                validation_errors.extend([f"QA {eval_id}: {error}" for error in errors])
            
            qa_entries.append(qa_entry)
        
        # Report validation errors if any
        if validation_errors:
            print(f"Warning: {len(validation_errors)} QA validation errors found:")
            for error in validation_errors[:5]:  # Show first 5 errors
                print(f"  - {error}")
            if len(validation_errors) > 5:
                print(f"  ... and {len(validation_errors) - 5} more")
        
        # Convert to DataFrame
        df = QaEntry.to_dataframe(qa_entries)
        
        expected_columns = ['eval_id', 'interaction_id', 'qa_score', 
                           'customer_critical', 'business_critical', 'compliance_critical']
        self._validate_output(df, expected_columns)
        self._log_generation_stats(df, "QA")
        
        return df
    
    def generate_models(self, interactions_df: pd.DataFrame) -> List[QaEntry]:
        """Generate QA data and return as list of QaEntry models."""
        # Generate DataFrame first, then convert to models
        df = self.generate(interactions_df)
        
        qa_entries = []
        for _, row in df.iterrows():
            qa_entry = QaEntry(
                eval_id=row['eval_id'],
                interaction_id=row['interaction_id'],
                qa_score=row['qa_score'],
                customer_critical=row['customer_critical'],
                business_critical=row['business_critical'],
                compliance_critical=row['compliance_critical']
            )
            qa_entries.append(qa_entry)
        
        return qa_entries
    
    def _sample_interactions_across_timeline(self, interactions_df: pd.DataFrame, 
                                           num_evaluations: int) -> pd.DataFrame:
        """
        Sample interactions randomly but distributed across the timeline.
        This ensures QA evaluations are spread throughout the time period.
        """
        # Sort interactions by creation time
        sorted_interactions = interactions_df.sort_values('interaction_created').reset_index(drop=True)
        
        # Use random sampling for simplicity while maintaining some timeline distribution
        sampled_indices = sorted(random.sample(range(len(sorted_interactions)), num_evaluations))
        
        return sorted_interactions.iloc[sampled_indices].reset_index(drop=True)
    
    def _generate_critical_flag(self, probability: float) -> int:
        """Generate a critical flag (0 or 1) based on probability."""
        return 1 if random.random() < probability else 0
    
    def _generate_qa_score(self) -> float:
        """Generate QA score using normal distribution with constraints."""
        params = self.config.QA_SCORE_PARAMS
        mean = params['mean']
        std = params['std']
        min_score = params.get('min', 0.0)
        max_score = params['max']
        
        # Generate score using truncated normal distribution
        score = np.random.normal(mean, std)
        
        # Ensure score stays within bounds
        score = max(min_score, min(max_score, score))
        
        # Round to 2 decimal places for realistic scoring
        return round(score, 2)
    
    def analyze_qa_metrics(self, qa_entries: List[QaEntry]) -> dict:
        """Analyze QA metrics using QaEntry models."""
        if not qa_entries:
            return {}
        
        total_evaluations = len(qa_entries)
        
        # Critical flags analysis
        customer_critical_count = sum(1 for entry in qa_entries if entry.customer_critical)
        business_critical_count = sum(1 for entry in qa_entries if entry.business_critical)
        compliance_critical_count = sum(1 for entry in qa_entries if entry.compliance_critical)
        any_critical_count = sum(1 for entry in qa_entries if entry.has_critical_flags())
        
        # Score analysis (excluding critical evaluations)
        non_critical_entries = [entry for entry in qa_entries if not entry.has_critical_flags()]
        
        if non_critical_entries:
            avg_score_non_critical = sum(entry.qa_score for entry in non_critical_entries) / len(non_critical_entries)
            perfect_scores = sum(1 for entry in non_critical_entries if entry.is_perfect_score())
        else:
            avg_score_non_critical = 0.0
            perfect_scores = 0
        
        overall_avg_score = sum(entry.qa_score for entry in qa_entries) / total_evaluations
        
        return {
            'total_evaluations': total_evaluations,
            'customer_critical_rate': customer_critical_count / total_evaluations,
            'business_critical_rate': business_critical_count / total_evaluations,
            'compliance_critical_rate': compliance_critical_count / total_evaluations,
            'any_critical_rate': any_critical_count / total_evaluations,
            'overall_avg_score': overall_avg_score,
            'avg_score_non_critical': avg_score_non_critical,
            'perfect_score_count': perfect_scores,
            'critical_evaluations_count': any_critical_count,
            'non_critical_evaluations_count': len(non_critical_entries)
        }
    
    def get_critical_evaluations(self, qa_entries: List[QaEntry]) -> List[QaEntry]:
        """Get all QA evaluations that have any critical flags."""
        return [entry for entry in qa_entries if entry.has_critical_flags()]
    
    def get_perfect_scores(self, qa_entries: List[QaEntry]) -> List[QaEntry]:
        """Get all QA evaluations with perfect scores (1.0)."""
        return [entry for entry in qa_entries if entry.is_perfect_score()]
    
    def get_evaluations_by_score_range(self, qa_entries: List[QaEntry], 
                                     min_score: float, max_score: float) -> List[QaEntry]:
        """Get QA evaluations within a specific score range."""
        return [entry for entry in qa_entries 
                if min_score <= entry.qa_score <= max_score]