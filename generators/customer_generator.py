"""
Customer data generator.
"""

import pandas as pd
from typing import List
from generators.base_generator import BaseGenerator
from models.entities import Customer
from utils.utils import weighted_choice


class CustomerGenerator(BaseGenerator):
    """Generates customer data using Customer model."""
    
    def generate(self, count: int = None) -> pd.DataFrame:
        """Generate customer data using Customer models."""
        if count is None:
            count = self.config.UNIQUE_CUSTOMERS
        
        customers = []
        
        for i in range(count):
            customer_id = i + 1
            name = self.faker.name()
            email = self.faker.email()
            phone = self.faker.phone_number()
            country = weighted_choice(self.config.COUNTRIES)
            
            # Create Customer model
            customer = Customer(
                customer_id=customer_id,
                name=name,
                email=email,
                phone=phone,
                country=country
            )
            
            customers.append(customer)

        # Convert to DataFrame
        df = Customer.to_dataframe(customers)
        
        expected_columns = ['customer_id', 'name', 'email', 'phone', 'country']
        self._validate_output(df, expected_columns)
        self._log_generation_stats(df, "Customers")
        
        return df
    
    def generate_models(self, count: int = None) -> List[Customer]:
        """Generate customer data and return as list of Customer models."""
        if count is None:
            count = self.config.UNIQUE_CUSTOMERS
        
        customers = []
        
        for i in range(count):
            customer_id = i + 1
            name = self.faker.name()
            email = self.faker.email()
            phone = self.faker.phone_number()
            country = weighted_choice(self.config.COUNTRIES)
            
            customer = Customer(
                customer_id=customer_id,
                name=name,
                email=email,
                phone=phone,
                country=country
            )
            
            customers.append(customer)
        
        print(f"Generated {len(customers)} Customer models")
        return customers
    
    def get_customers_by_country(self, customers: List[Customer], country: str) -> List[Customer]:
        """Filter customers by country using Customer models."""
        return [customer for customer in customers if customer.country == country]
    
    def analyze_country_distribution(self, customers: List[Customer]) -> dict:
        """Analyze customer distribution by country using Customer models."""
        country_counts = {}
        
        for customer in customers:
            if customer.country not in country_counts:
                country_counts[customer.country] = 0
            country_counts[customer.country] += 1
        
        total_customers = len(customers)
        country_percentages = {
            country: (count / total_customers) * 100 
            for country, count in country_counts.items()
        }
        
        return country_percentages