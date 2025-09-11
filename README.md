# Customer Support Data Generator

## 1. Overview

This application generates realistic synthetic customer support data for demo analytics and testing purposes. It creates a comprehensive dataset that simulates a customer support operation for an audio equipment company, including support tickets, customer interactions, agent performance data, and communication channel metrics.

The generator produces statistically realistic data with configurable business rules, ensuring that relationships between entities (customers, tickets, interactions) follow real-world patterns. This makes it ideal for:

- Testing and demo customer support analytics dashboards
- Training machine learning models on support data
- Demonstrating customer service KPIs and metrics
- Creating sample datasets for business intelligence tools

## 2. Output Structure

The application generates 6 CSV files in the `exports/` folder:

### 2.1 Users Table (`users_table.csv`)
Contains support agent information.

**Columns:**
- `id`: Unique agent identifier (1-12)
- `first_name`: Agent's first name
- `last_name`: Agent's last name  
- `fte`: Full-time equivalent (0.75 or 1.0)
- `position`: Job position (always "support_agent")
- `start_date`: Agent start date (YYYY-MM-DD)
- `status`: Employment status (always "active")
- `hourly_rate_eur`: Hourly rate in EUR (12-16 EUR based on experience)

### 2.2 WFM Tabe (`wfm_table.csv`)
Contains agents specific working time metrics

**Columns:**
-`date`: calendar date within agent's working period
- `user_id`: unique agent identifier
- `paid_time`: paid time based on the number of FTEs of each agent (in minutes)
- `scheduled_time`: scheduled work time (in minutes)
- `available_time`: time of agent being actually available to work (scheduled time - breaks - non presence) (in minutes)
- `interactions_time`: time spend on interactions with customer and post-work (in minutes)
- `productive_time`: interactions time + other productive activities (meetings, training, admin work)

### 2.2 Customers Table (`customers_table.csv`)
Contains customer information.

**Columns:**
- `id`: Unique customer identifier (1-6000)
- `name`: Customer full name
- `email`: Customer email address
- `phone`: Customer phone number
- `country`: Customer country (UK, Germany, Austria, Netherlands, France, Belgium)

### 2.3 Tickets Table (`tickets_table.csv`)
Contains support ticket information.

**Columns:**
- `ticket_id`: Unique ticket identifier (TKT-XXXXX format)
- `origin`: Communication channel (email, phone, chat)
- `symptom_cat`: Issue category (troubleshooting, finance, logistics, rma, product, complaint)
- `symptom`: Specific issue description
- `status`: Ticket status (new, open, closed)
- `product`: Product involved (headphones, speakers, amplifiers, turntables)
- `ticket_owner`: Agent ID responsible for ticket
- `language`: Customer language (english, french, german)
- `fcr`: First Contact Resolution flag (0 or 1)
- `escalated`: Escalation flag (0 or 1)
- `ticket_created`: Ticket creation timestamp
- `ticket_closed`: Ticket closure timestamp (if closed)
- `last_interaction_time`: Last interaction timestamp
- `resolution_after_last_interaction_hours`: Hours from last interaction to closure
- `lifecycle_hours`: Total ticket lifecycle in hours

### 2.4 Interactions Table (`interactions_table.csv`)
Contains individual customer-agent interactions.

**Columns:**
- `interaction_id`: Unique interaction identifier (INT-XXXXXX format)
- `channel`: Communication channel (email, phone, chat)
- `customer_id`: Customer identifier
- `interaction_created`: Interaction start timestamp
- `handle_time`: Duration in minutes
- `speed_of_answer`: Response time (hours for email, seconds for phone/chat)
- `interaction_handled`: Interaction completion timestamp
- `handled_by`: Agent ID who handled the interaction
- `subject`: Interaction subject (currently empty)
- `body`: Interaction content (currently empty)
- `ticket_id`: Associated ticket identifier

### 2.5 Calls Table (`calls_table.csv`)
Contains phone call data including abandoned calls.

**Columns:**
- `id`: Unique call identifier
- `initialized`: Call start timestamp
- `answered`: Call answer timestamp (null if abandoned)
- `abandoned`: Call abandonment timestamp (null if answered)
- `is_abandoned`: Abandonment flag (0 or 1)

### 2.6 Chats Table (`chats_table.csv`)
Contains chat session data including abandoned chats.

**Columns:**
- `id`: Unique chat identifier
- `initialized`: Chat start timestamp
- `answered`: Chat answer timestamp (null if abandoned)
- `abandoned`: Chat abandonment timestamp (null if answered)
- `is_abandoned`: Abandonment flag (0 or 1)


### 2.7 Data Relationships

```
CUSTOMERS (1) ←→ (∞) INTERACTIONS
    ↓                    ↓    
 Country             Channel              
 Language            Handle Time               
                     Speed of Answer                  

TICKETS (1) ←→ (∞) INTERACTIONS
    ↓                    ↓                    
 Product              Channel
 Status               Handle Time
 FCR                  Speed of Answer
 Origin
                     
USERS (1) ←→ (∞) TICKETS
  ↓              ↓
 Agent            Owner
          
              
USERS (1) ←→ (∞) INTERACTIONS
  ↓              ↓
 Agent         Handler

USERS (1) ←→ (∞) WFM_ENTRIES
  ↓              ↓
 FTE          Scheduled Time
                            


CALLS (phone channel only) - independent
CHATS (chat channel only) - independent
```

**Key Relationships:**
- Each **ticket** belongs is owned by one **user**
- Each **interaction** belongs to one **ticket** and is handled by one **user**
- Each **customer** belongs to one **interaction**
- Each **wfm entry** belongs to one **user**
- **Calls** and **chats** are generated from phone and chat **interactions** respectively
- **FCR tickets** have exactly 1 interaction; others have multiple based on symptom category
- **Abandoned calls/chats** are additional records not linked to tickets

## 3. Parameters

### 3.1 Basic Configuration
- `NUM_TICKETS`: Number of tickets to generate (default: 25,000)
- `UNIQUE_CUSTOMERS`: Number of unique customers (default: 6,000)
- `UNIQUE_AGENTS`: Number of support agents (default: 12)
- `START_DATE`: Data generation start date (default: 2023-09-15)
- `END_DATE`: Data generation end date (default: 2025-08-21)

### 3.2 Business Rules
- `MAX_INTERACTION_SPAN_HOURS`: Maximum time span for interactions per ticket (default: 6 hours)
- `ESCALATION_RATE`: Probability of ticket escalation (default: 0.12)
- `ANCHOR_CLOSURE_TO`: Closure time calculation method ('last_interaction' or 'from_creation')

### 3.3 Channel Distribution
- `CHANNELS`: Communication channel weights (email: 30%, phone: 40%, chat: 30%)

### 3.4 Geographic Distribution
- `COUNTRIES`: Customer country distribution (UK: 30%, Germany: 18%, Austria: 12%, Netherlands: 10%, France: 15%, Belgium: 5%)

### 3.5 Symptom Categories and FCR Rates
- `troubleshooting`: 50% FCR rate, 1.5 avg contacts per case
- `finance`: 0% FCR rate, 2.3 avg contacts per case
- `logistics`: 43% FCR rate, 1.8 avg contacts per case
- `rma`: 10% FCR rate, 4.1 avg contacts per case
- `product`: 100% FCR rate, 1.2 avg contacts per case
- `complaint`: 20% FCR rate, 1.1 avg contacts per case

### 3.6 Abandonment Rates
- **Calls**: 7% average abandonment rate (±3%)
- **Chats**: 10% average abandonment rate (±3%)

## 4. Installation and Usage

### 4.1 Prerequisites
- Python 3.7 or higher
- pip package manager

### 4.2 Installation

1. **Clone or download the project files**

2. **Install dependencies:**
```bash
pip install pandas numpy faker openpyxl
```

3. **Set up directory structure:**
```
data_generator/
├── main.py
├── orchestrator.py
├── utils.py
├── config/
│   ├── __init__.py
│   └── settings.py
├── generators/
│   ├── __init__.py
│   ├── base_generator.py
│   ├── user_generator.py
│   ├── customer_generator.py
│   ├── ticket_generator.py
│   ├── interaction_generator.py
│   └── call_chat_generator.py
├── models/
│   ├── __init__.py
│   └── entities.py
└── analysis/
    ├── __init__.py
    └── metrics.py
```

### 4.3 How to Change Parameters

Edit the configuration in `config/settings.py`:

```python
@dataclass
class Config:
    # Change basic counts
    NUM_TICKETS: int = 25000        # Modify this value
    UNIQUE_CUSTOMERS: int = 6000    # Modify this value
    UNIQUE_AGENTS: int = 12         # Modify this value
    
    # Change date range
    START_DATE: datetime = datetime(2023, 9, 15)  # Modify dates
    END_DATE: datetime = datetime(2025, 8, 21)
    
    # Modify other parameters in __post_init__ method
```

### 4.4 How to Run

**Basic execution:**
```bash
python main.py
```

**Output:**
- Creates `exports/` folder automatically
- Generates 6 CSV files in `exports/` folder
- Displays generation statistics and analysis in console
- Typical runtime: 30-60 seconds for default dataset size

## 5. Project Structure

```
data_generator/
├── main.py                     # Entry point - run this file
├── orchestrator.py            # Main coordination logic
├── utils.py                   
|   ├── __init__.py
|   ├── utils.py               # Utility functions (date generation, statistics)
|   ├── data_exporter         # Data export class
├── config/
│   ├── __init__.py
│   └── settings.py            # All configuration parameters
├── generators/                # Data generation classes
│   ├── __init__.py
│   ├── base_generator.py      # Abstract base class
│   ├── user_generator.py      # Support agent data
│   ├── customer_generator.py  # Customer data
│   ├── ticket_generator.py    # Support ticket data
│   ├── interaction_generator.py # Customer-agent interactions
│   └── call_chat_generator.py # Call and chat channel data
|   |__ wfm_generator          # WFM data
├── models/                    # Data model definitions
│   ├── __init__.py
│   └── entities.py            # Dataclass models for type safety
├── analysis/                  # Export and analysis functionality
│   ├── __init__.py
│   └── metrics.py             # Metrics calculators
└── exports/                   # Generated output files (created automatically)
    ├── users_table.csv
    ├── customers_table.csv
    ├── tickets_table.csv
    ├── interactions_table.csv
    ├── calls_table.csv
    └── chats_table.csv
```

### 5.1 Key Components

- **Orchestrator**: Manages generation workflow and dependencies between data tables
- **Generators**: Individual classes responsible for generating each data type
- **Models**: Dataclass definitions providing type safety and business logic methods
- **Config**: Centralized configuration management
- **Utils**: Shared utility functions for date/time generation and statistics
- **Analysis**: Export functionality and data validation

## 6. Tech Stack

### 6.1 Core Dependencies
- **Python 3.7+**: Programming language
- **pandas**: Data manipulation and CSV export
- **numpy**: Statistical distributions and numerical operations
- **faker**: Realistic fake data generation (names, emails, addresses)
- **openpyxl**: Excel file export support (optional)

### 6.2 Design Patterns
- **Factory Pattern**: For creating data models
- **Strategy Pattern**: For different closure time calculation methods
- **Builder Pattern**: For orchestrating complex data generation workflows
- **Dependency Injection**: For passing required data between generators

### 6.3 Key Features
- **Type Safety**: Dataclass models with type hints
- **Data Validation**: Built-in integrity checks and business rule validation
- **Configurable**: All parameters centralized and easily modifiable
- **Extensible**: Easy to add new data tables or modify existing ones
- **Reproducible**: Configurable random seed for consistent results
- **Realistic**: Statistical distributions based on real customer support patterns