"""
Orchestrator - all sequence and logic of tables creation.
"""

import random
from typing import Dict, List, Union, Any
import pandas as pd
from config.settings import Config
from generators.user_generator import UserGenerator
from generators.customer_generator import CustomerGenerator
from generators.ticket_generator import TicketGenerator
from generators.interaction_generator import InteractionGenerator
from generators.call_chat_generator import CallGenerator, ChatGenerator
from generators.wfm_generator import WfmGenerator
from generators.qa_generator import QaGenerator
from analysis.metrics import DataAnalyzer
from utils.data_exporter import DataExporter
from models.entities import User, Customer, Ticket, Interaction, Call, Chat, WfmEntry, QaEntry


class DataGenerationOrchestrator:
    """Orchestrates the entire data generation process with model support."""
    
    def __init__(self, config: Config):
        self.config = config
        self._setup_random_seed()
        self._initialize_generators()
        self.analyzer = DataAnalyzer(config)
        self.exporter = DataExporter()
    
    def _setup_random_seed(self) -> None:
        """Set random seed for reproducibility."""
        random.seed(self.config.RANDOM_SEED)
    
    def _initialize_generators(self) -> None:
        """Initialize all data generators."""
        self.user_generator = UserGenerator(self.config)
        self.customer_generator = CustomerGenerator(self.config)
        self.ticket_generator = TicketGenerator(self.config)
        self.interaction_generator = InteractionGenerator(self.config)
        self.call_generator = CallGenerator(self.config)
        self.chat_generator = ChatGenerator(self.config)
        self.wfm_generator = WfmGenerator(self.config)
        self.qa_generator = QaGenerator(self.config)

    
    def generate_all(self, output_format: str = 'dataframe') -> Dict[str, Union[pd.DataFrame, List[Any]]]:
        """
        Generate all datasets in the correct dependency order.
        
        Args:
            output_format: 'dataframe' for pandas DataFrames, 'models' for dataclass objects
        
        Returns:
            Dictionary containing generated data in specified format
        """
        print("Starting data generation process...")
        
        if output_format not in ['dataframe', 'models']:
            raise ValueError("output_format must be 'dataframe' or 'models'")
        
        if output_format == 'dataframe':
            return self._generate_dataframes()
        else:
            return self._generate_models()
    
    def _generate_dataframes(self) -> Dict[str, pd.DataFrame]:
        """Generate all datasets as DataFrames."""
        # Step 1: Generate independent datasets
        print("\n1. Generating users...")
        users_df = self.user_generator.generate()
        
        print("2. Generating customers...")
        customers_df = self.customer_generator.generate()
        
        # Step 2: Generate tickets (depends on users and customers)
        print("3. Generating tickets...")
        tickets_df = self.ticket_generator.generate(customers_df, users_df)
        
        # Step 3: Generate interactions (depends on tickets, users, customers)
        print("4. Generating interactions...")
        interactions_df = self.interaction_generator.generate(tickets_df, users_df, customers_df)
        
        # Step 4: Update ticket closure times (depends on interactions)
        print("5. Updating ticket closure times...")
        tickets_df = self.ticket_generator.update_closure_times(tickets_df, interactions_df)
        
        # Step 5: Generate calls and chats (depends on interactions)
        print("6. Generating calls...")
        calls_df = self.call_generator.generate(interactions_df)
        
        print("7. Generating chats...")
        chats_df = self.chat_generator.generate(interactions_df)
        
        datasets = {
            'users': users_df,
            'customers': customers_df,
            'tickets': tickets_df,
            'interactions': interactions_df,
            'calls': calls_df,
            'chats': chats_df
        }

        print("8. Generating WFM data...")
        wfm_df = self.wfm_generator.generate(users_df)

        datasets = {
            'users': users_df,
            'customers': customers_df,
            'tickets': tickets_df,
            'interactions': interactions_df,
            'calls': calls_df,
            'chats': chats_df,
            'wfm': wfm_df
        }

        print("9. Generating QA data...")
        qa_df = self.qa_generator.generate(interactions_df)

        datasets = {
            'users': users_df,
            'customers': customers_df,
            'tickets': tickets_df,
            'interactions': interactions_df,
            'calls': calls_df,
            'chats': chats_df,
            'wfm': wfm_df,
            'qa': qa_df
        }


        
        print("\nData generation completed!")
        return datasets
    
    def _generate_models(self) -> Dict[str, List[Any]]:
        """Generate all datasets as dataclass models."""
        # Step 1: Generate independent datasets
        print("\n1. Generating users...")
        users = self.user_generator.generate_models()
        users_df = User.to_dataframe(users)
        
        print("2. Generating customers...")
        customers = self.customer_generator.generate_models()
        customers_df = Customer.to_dataframe(customers)
        
        # Step 2: Generate tickets (depends on users and customers)
        print("3. Generating tickets...")
        tickets = self.ticket_generator.generate_models(customers_df, users_df)
        tickets_df = Ticket.to_dataframe(tickets)
        
        # Step 3: Generate interactions (depends on tickets, users, customers)
        print("4. Generating interactions...")
        interactions = self.interaction_generator.generate_models(tickets_df, users_df, customers_df)
        interactions_df = Interaction.to_dataframe(interactions)
        
        # Step 4: Update ticket closure times (depends on interactions)
        print("5. Updating ticket closure times...")
        tickets_df = self.ticket_generator.update_closure_times(tickets_df, interactions_df)
        # Re-create ticket models with updated closure times
        tickets = self.ticket_generator.generate_models(customers_df, users_df)
        
        # Step 5: Generate calls and chats (depends on interactions)
        print("6. Generating calls...")
        calls = self.call_generator.generate_models(interactions_df)
        
        print("7. Generating chats...")
        chats = self.chat_generator.generate_models(interactions_df)
        
        datasets = {
            'users': users,
            'customers': customers,
            'tickets': tickets,
            'interactions': interactions,
            'calls': calls,
            'chats': chats
        }

        print("8. Generating WFM data...")
        wfm = self.wfm_generator.generate_models(users_df)

        datasets = {
            'users': users,
            'customers': customers,
            'tickets': tickets,
            'interactions': interactions,
            'calls': calls,
            'chats': chats,
            'wfm': wfm
        }

        print("9. Generating QA data...")
        qa = self.qa_generator.generate_models(interactions_df)

        datasets = {
            'users': users,
            'customers': customers,
            'tickets': tickets,
            'interactions': interactions,
            'calls': calls,
            'chats': chats,
            'wfm': wfm,
            'qa': qa
        }
        
        print("\nData generation completed!")
        return datasets
    
    def generate_hybrid(self) -> Dict[str, Union[pd.DataFrame, List[Any]]]:
        """
        Generate datasets with mixed output formats.
        Use models for business logic, DataFrames for analysis.
        """
        print("Generating hybrid datasets (models + DataFrames)...")
        
        # Generate models for business logic
        models = self._generate_models()
        
        # Convert to DataFrames for analysis
        dataframes = {
            'users': User.to_dataframe(models['users']),
            'customers': Customer.to_dataframe(models['customers']),
            'tickets': Ticket.to_dataframe(models['tickets']),
            'interactions': Interaction.to_dataframe(models['interactions']),
            'calls': Call.to_dataframe(models['calls']),
            'chats': Chat.to_dataframe(models['chats']),
            'wfm': WfmEntry.to_dataframe(models['wfm']),
            'qa': QaEntry.to_dataframe(models['qa'])

        }
        
        return {
            'models': models,
            'dataframes': dataframes
        }
    
    def export_data(self, datasets: Dict[str, Union[pd.DataFrame, List[Any]]], 
                   data_format: str = 'dataframe') -> None:
        """Export datasets to files."""
        print("\nExporting data to CSV files...")
        
        if data_format == 'models':
            # Convert models to DataFrames for export
            dataframes = {}
            for name, models_list in datasets.items():
                if name == 'users':
                    dataframes[name] = User.to_dataframe(models_list)
                elif name == 'customers':
                    dataframes[name] = Customer.to_dataframe(models_list)
                elif name == 'tickets':
                    dataframes[name] = Ticket.to_dataframe(models_list)
                elif name == 'interactions':
                    dataframes[name] = Interaction.to_dataframe(models_list)
                elif name == 'calls':
                    dataframes[name] = Call.to_dataframe(models_list)
                elif name == 'chats':
                    dataframes[name] = Chat.to_dataframe(models_list)
                elif name == 'wfm':
                    dataframes[name] = WfmEntry.to_dataframe(models_list)
                elif name == 'qa':
                    dataframes[name] = QaEntry.to_dataframe(models_list)
            
            self.exporter.export_to_csv(dataframes)
        else:
            self.exporter.export_to_csv(datasets)
    
    def generate_analysis_reports(self, datasets: Dict[str, Union[pd.DataFrame, List[Any]]], 
                                data_format: str = 'dataframe') -> None:
        """Generate and display analysis reports."""
        print("\nGenerating analysis reports...")
        
        if data_format == 'models':
            # Use model-based analysis methods
            self._generate_model_based_analysis(datasets)
        else:
            # Use traditional DataFrame analysis
            self.analyzer.generate_all_reports(datasets)
    
    def _generate_model_based_analysis(self, datasets: Dict[str, List[Any]]) -> None:
        """Generate analysis using dataclass models."""
        users = datasets['users']
        customers = datasets['customers']
        tickets = datasets['tickets']
        interactions = datasets['interactions']
        calls = datasets['calls']
        chats = datasets['chats']
        wfm = datasets['wfm']

        print("\n--- MODEL-BASED ANALYSIS ---")
        
        # FCR Analysis using Ticket models
        print("\n--- FCR ANALYSIS BY SYMPTOM CATEGORY (using models) ---")
        fcr_rates = self.ticket_generator.analyze_fcr_by_symptom(tickets)
        for symptom, rate in fcr_rates.items():
            target_rate = self.config.SYMPTOM_FCR_RATES[symptom]['mean']
            print(f"{symptom}: {rate:.1%} (target: {target_rate:.1%})")
        
        overall_fcr = sum(1 for ticket in tickets if ticket.is_fcr()) / len(tickets)
        print(f"Overall FCR: {overall_fcr:.1%}")
        
        # Channel Performance Analysis using Interaction models
        print("\n--- CHANNEL PERFORMANCE ANALYSIS (using models) ---")
        channel_performance = self.interaction_generator.analyze_channel_performance(interactions)
        for channel, stats in channel_performance.items():
            print(f"{channel.upper()} Channel:")
            print(f"  Total interactions: {stats['total_interactions']}")
            print(f"  Avg handle time: {stats['avg_handle_time']:.2f} min")
            print(f"  Avg speed of answer: {stats['avg_speed_answer']:.2f}")
        
        # Abandonment Analysis using Call and Chat models
        print("\n--- ABANDONMENT ANALYSIS (using models) ---")
        call_stats = self.call_generator.analyze_abandonment_rates(calls)
        chat_stats = self.chat_generator.analyze_abandonment_rates(chats)
        
        print(f"Call abandonment rate: {call_stats['abandonment_rate']:.1%}")
        print(f"Chat abandonment rate: {chat_stats['abandonment_rate']:.1%}")
        print(f"Avg abandoned call wait time: {call_stats['avg_abandoned_wait_time_seconds']:.1f} seconds")
        print(f"Avg abandoned chat wait time: {chat_stats['avg_abandoned_wait_time_seconds']:.1f} seconds")
        
        # Country Distribution Analysis using Customer models
        print("\n--- CUSTOMER DISTRIBUTION BY COUNTRY (using models) ---")
        country_distribution = self.customer_generator.analyze_country_distribution(customers)
        for country, percentage in country_distribution.items():
            print(f"{country}: {percentage:.1f}%")
        
        # User FTE Analysis using User models
        print("\n--- USER FTE ANALYSIS (using models) ---")
        full_time_users = [user for user in users if user.fte == 1.0]
        part_time_users = [user for user in users if user.fte < 1.0]
        
        print(f"Full-time users: {len(full_time_users)}")
        print(f"Part-time users: {len(part_time_users)}")
        
        if part_time_users:
            avg_part_time_fte = sum(user.fte for user in part_time_users) / len(part_time_users)
            print(f"Average part-time FTE: {avg_part_time_fte:.2f}")
        
        # Sample data using models
        print("\n--- SAMPLE DATA (using models) ---")
        print("Sample User:")
        if users:
            user = users[0]
            print(f"  {user.first_name} {user.last_name} - {user.position} - {user.fte} FTE - €{user.hourly_rate_eur}/hr")
        
        print("Sample Customer:")
        if customers:
            customer = customers[0]
            print(f"  {customer.name} - {customer.email} - {customer.country}")
        
        print("Sample Ticket:")
        if tickets:
            ticket = tickets[0]
            status = "FCR" if ticket.is_fcr() else "Multi-contact"
            escalation = "Escalated" if ticket.is_escalated() else "Not escalated"
            print(f"  {ticket.ticket_id} - {ticket.symptom_cat} - {status} - {escalation}")

        # WFM Analysis using WfmEntry models
        print("\n--- WFM ANALYSIS (using models) ---")
        wfm_working_days = [entry for entry in wfm if entry.is_working_day()]
        wfm_weekends = [entry for entry in wfm if entry.is_weekend_or_holiday()]

        print(f"Total WFM entries: {len(wfm)}")
        print(f"Working day entries: {len(wfm_working_days)}")
        print(f"Weekend/holiday entries: {len(wfm_weekends)}")

        if wfm_working_days:
            avg_scheduled = sum(entry.scheduled_time for entry in wfm_working_days) / len(wfm_working_days)
            avg_available = sum(entry.available_time for entry in wfm_working_days) / len(wfm_working_days)
            avg_interactions = sum(entry.interactions_time for entry in wfm_working_days) / len(wfm_working_days)
            avg_productive = sum(entry.productive_time for entry in wfm_working_days) / len(wfm_working_days)
            
            print(f"Average scheduled time per working day: {avg_scheduled:.1f} minutes")
            print(f"Average available time per working day: {avg_available:.1f} minutes")
            print(f"Average interactions time per working day: {avg_interactions:.1f} minutes")
            print(f"Average productive time per working day: {avg_productive:.1f} minutes")

        utilization_stats = self.wfm_generator.analyze_utilization_by_user(wfm)
        print(f"\nWFM data generated for {len(utilization_stats)} users")

        qa = datasets['qa']

        # QA Analysis using QaEntry models
        print("\n--- QA ANALYSIS (using models) ---")
        qa_metrics = self.qa_generator.analyze_qa_metrics(qa)

        if qa_metrics:
            print(f"Total QA evaluations: {qa_metrics['total_evaluations']}")
            print(f"Customer critical rate: {qa_metrics['customer_critical_rate']:.1%}")
            print(f"Business critical rate: {qa_metrics['business_critical_rate']:.1%}")
            print(f"Compliance critical rate: {qa_metrics['compliance_critical_rate']:.1%}")
            print(f"Any critical flags rate: {qa_metrics['any_critical_rate']:.1%}")
            print(f"Overall average QA score: {qa_metrics['overall_avg_score']:.2f}")
            print(f"Average score (non-critical): {qa_metrics['avg_score_non_critical']:.2f}")
            print(f"Perfect scores: {qa_metrics['perfect_score_count']}")
        else:
            print("No QA evaluations generated")
            
            def validate_data_integrity(self, datasets: Dict[str, Union[pd.DataFrame, List[Any]]], 
                                    data_format: str = 'dataframe') -> bool:
                """Validate data integrity across all datasets."""
                print("\nValidating data integrity...")
                
                try:
                    if data_format == 'models':
                        self._validate_model_integrity(datasets)
                    else:
                        # Check foreign key relationships
                        self._validate_foreign_keys(datasets)
                        
                        # Check data consistency
                        self._validate_data_consistency(datasets)
                    
                    print("✓ Data integrity validation passed")
                    return True
                    
                except Exception as e:
                    print(f"✗ Data integrity validation failed: {e}")
                    return False
    
    def _validate_model_integrity(self, datasets: Dict[str, List[Any]]) -> None:
        """Validate data integrity using dataclass models."""
        users = datasets['users']
        customers = datasets['customers']
        tickets = datasets['tickets']
        interactions = datasets['interactions']
        
        # Check that ticket owners exist in users
        user_ids = {user.id for user in users}
        for ticket in tickets:
            if ticket.ticket_owner not in user_ids:
                raise ValueError(f"Ticket {ticket.ticket_id} has invalid owner {ticket.ticket_owner}")
        
        # Check that interaction handlers exist in users
        for interaction in interactions:
            if interaction.handled_by not in user_ids:
                raise ValueError(f"Interaction {interaction.interaction_id} has invalid handler {interaction.handled_by}")
        
        # Check that interaction tickets exist
        ticket_ids = {ticket.ticket_id for ticket in tickets}
        for interaction in interactions:
            if interaction.ticket_id not in ticket_ids:
                raise ValueError(f"Interaction {interaction.interaction_id} references invalid ticket {interaction.ticket_id}")
        
        # Check FCR consistency using model methods
        for ticket in tickets:
            if ticket.is_fcr():
                ticket_interactions = [i for i in interactions if i.ticket_id == ticket.ticket_id]
                if len(ticket_interactions) != 1:
                    raise ValueError(f"FCR ticket {ticket.ticket_id} has {len(ticket_interactions)} interactions instead of 1")
        
        # Check closed tickets have closure dates
        for ticket in tickets:
            if ticket.is_closed() and ticket.ticket_closed is None:
                raise ValueError(f"Closed ticket {ticket.ticket_id} missing closure date")
    
    def _validate_foreign_keys(self, datasets: Dict[str, pd.DataFrame]) -> None:
        """Validate foreign key relationships."""
        tickets_df = datasets['tickets']
        interactions_df = datasets['interactions']
        users_df = datasets['users']
        customers_df = datasets['customers']
        
        # Check ticket_owner references
        invalid_owners = ~tickets_df['ticket_owner'].isin(users_df['id'])
        if invalid_owners.any():
            raise ValueError("Invalid ticket owners found")
        
        # Check interaction ticket references
        invalid_tickets = ~interactions_df['ticket_id'].isin(tickets_df['ticket_id'])
        if invalid_tickets.any():
            raise ValueError("Invalid ticket references in interactions")
        
        # Check interaction handled_by references
        invalid_handlers = ~interactions_df['handled_by'].isin(users_df['id'])
        if invalid_handlers.any():
            raise ValueError("Invalid handlers in interactions")
    
    def _validate_data_consistency(self, datasets: Dict[str, pd.DataFrame]) -> None:
        """Validate data consistency rules."""
        tickets_df = datasets['tickets']
        
        # Check that closed tickets have closure dates
        closed_tickets = tickets_df[tickets_df['status'] == 'closed']
        if closed_tickets['ticket_closed'].isna().any():
            raise ValueError("Closed tickets missing closure dates")
        
        # Check FCR consistency
        fcr_tickets = tickets_df[tickets_df['fcr'] == 1]
        interactions_df = datasets['interactions']
        
        for ticket_id in fcr_tickets['ticket_id']:
            ticket_interactions = interactions_df[interactions_df['ticket_id'] == ticket_id]
            if len(ticket_interactions) != 1:
                raise ValueError(f"FCR ticket {ticket_id} has {len(ticket_interactions)} interactions instead of 1")
    
    def demonstrate_model_benefits(self) -> None:
        """Demonstrate the benefits of using dataclass models."""
        print("\n--- DEMONSTRATING MODEL BENEFITS ---")
        
        # Generate a small sample with models
        config = self.config
        config.NUM_TICKETS = 10
        config.UNIQUE_CUSTOMERS = 5
        config.UNIQUE_AGENTS = 3
        
        print("Generating sample data with models...")
        datasets = self.generate_all(output_format='models')
        
        users = datasets['users']
        tickets = datasets['tickets']
        interactions = datasets['interactions']
        
        print("\n1. Type Safety and Clear Methods:")
        if tickets:
            ticket = tickets[0]
            print(f"   Ticket {ticket.ticket_id}:")
            print(f"   - Is FCR: {ticket.is_fcr()}")
            print(f"   - Is closed: {ticket.is_closed()}")
            print(f"   - Is escalated: {ticket.is_escalated()}")
        
        print("\n2. Business Logic Encapsulation:")
        if interactions:
            interaction = interactions[0]
            print(f"   Interaction {interaction.interaction_id}:")
            print(f"   - Is email: {interaction.is_email()}")
            print(f"   - Is phone: {interaction.is_phone()}")
            print(f"   - Duration: {interaction.get_duration_minutes():.1f} minutes")
        
        print("\n3. Easy Filtering and Analysis:")
        fcr_tickets = [t for t in tickets if t.is_fcr()]
        print(f"   FCR tickets: {len(fcr_tickets)} out of {len(tickets)}")
        
        email_interactions = [i for i in interactions if i.is_email()]
        print(f"   Email interactions: {len(email_interactions)} out of {len(interactions)}")
        
        part_time_users = [u for u in users if u.fte < 1.0]
        print(f"   Part-time users: {len(part_time_users)} out of {len(users)}")
        
        print("\n4. Data Validation:")
        print("   All models are automatically validated during creation!")
        print("   Business rules are enforced at the model level.")
        
        print("\nModel-based approach provides:")
        print("✓ Type safety and IDE support")
        print("✓ Self-documenting code")
        print("✓ Business logic encapsulation")
        print("✓ Easy testing and validation")
        print("✓ Flexibility between DataFrames and objects")