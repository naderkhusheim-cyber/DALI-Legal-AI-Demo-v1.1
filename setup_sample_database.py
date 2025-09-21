"""
Sample Legal Database Setup for DALI Enhancement
Creates MySQL database with realistic legal practice data
"""

import mysql.connector
from mysql.connector import Error
import pandas as pd
from datetime import datetime, timedelta
import random
import os

def create_sample_legal_database():
    """Create comprehensive sample legal database"""
    
    print("🗄️ Creating sample legal database...")
    
    # MySQL connection configuration
    config = {
        'host': 'localhost',
        'port': 3306,
        'user': 'dali_user',
        'password': 'dali_password',
        'database': 'dali_legal_ai'
    }
    
    try:
        # Connect to MySQL database
        conn = mysql.connector.connect(**config)
        cursor = conn.cursor()
        
        # Create tables
        print("📋 Creating database tables...")
        create_tables(cursor)
        
        # Insert sample data
        print("📊 Inserting sample data...")
        insert_sample_data(cursor)
        
        # Create indexes for performance
        print("⚡ Creating database indexes...")
        create_indexes(cursor)
        
        conn.commit()
        print("✅ Sample legal database created successfully in MySQL!")
        verify_database(config)
        
    except Error as e:
        print(f"❌ Error creating database: {e}")
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

def create_tables(cursor):
    """Create all necessary tables"""
    
    # Clients table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS clients (
        client_id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        company VARCHAR(255),
        contact_email VARCHAR(255),
        phone VARCHAR(50),
        address TEXT,
        client_type VARCHAR(100),
        industry VARCHAR(100),
        created_date DATE,
        status VARCHAR(50) DEFAULT 'Active',
        total_value DECIMAL(15,2)
    )
    ''')
    
    # Attorneys table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS attorneys (
        attorney_id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        practice_area VARCHAR(100),
        years_experience INT,
        hourly_rate DECIMAL(10,2),
        office_location VARCHAR(255),
        hire_date DATE,
        status VARCHAR(50) DEFAULT 'Active',
        bar_number VARCHAR(100),
        email VARCHAR(255)
    )
    ''')
    
    # Cases table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS cases (
        case_id INT AUTO_INCREMENT PRIMARY KEY,
        case_number VARCHAR(100) UNIQUE,
        client_id INT,
        attorney_id INT,
        case_type VARCHAR(100),
        case_status VARCHAR(50),
        filing_date DATE,
        resolution_date DATE,
        case_value DECIMAL(15,2),
        outcome VARCHAR(100),
        description TEXT,
        FOREIGN KEY (client_id) REFERENCES clients (client_id),
        FOREIGN KEY (attorney_id) REFERENCES attorneys (attorney_id)
    )
    ''')
    
    # Contracts table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS contracts (
        contract_id INT AUTO_INCREMENT PRIMARY KEY,
        client_id INT,
        contract_type VARCHAR(100),
        contract_value DECIMAL(15,2),
        start_date DATE,
        end_date DATE,
        status VARCHAR(50),
        created_date DATE,
        FOREIGN KEY (client_id) REFERENCES clients (client_id)
    )
    ''')
    
    # Billable hours table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS billable_hours (
        entry_id INT AUTO_INCREMENT PRIMARY KEY,
        attorney_id INT,
        client_id INT,
        case_id INT,
        work_date DATE,
        hours_worked DECIMAL(4,2),
        hourly_rate DECIMAL(10,2),
        total_amount DECIMAL(10,2),
        work_description TEXT,
        task_category VARCHAR(100),
        billed_status VARCHAR(50) DEFAULT 'Pending',
        FOREIGN KEY (attorney_id) REFERENCES attorneys (attorney_id),
        FOREIGN KEY (client_id) REFERENCES clients (client_id)
    )
    ''')
    
    # Legal documents table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS legal_documents (
        doc_id INT AUTO_INCREMENT PRIMARY KEY,
        case_id INT,
        client_id INT,
        document_type VARCHAR(100),
        title VARCHAR(255),
        file_path VARCHAR(500),
        upload_date DATE,
        file_size INT,
        status VARCHAR(50) DEFAULT 'Active',
        description TEXT,
        FOREIGN KEY (case_id) REFERENCES cases (case_id),
        FOREIGN KEY (client_id) REFERENCES clients (client_id)
    )
    ''')
    
    # Court appearances table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS court_appearances (
        appearance_id INT AUTO_INCREMENT PRIMARY KEY,
        case_id INT,
        attorney_id INT,
        court_name VARCHAR(255),
        appearance_date DATE,
        appearance_type VARCHAR(100),
        duration_hours DECIMAL(4,2),
        notes TEXT,
        outcome VARCHAR(100),
        FOREIGN KEY (case_id) REFERENCES cases (case_id),
        FOREIGN KEY (attorney_id) REFERENCES attorneys (attorney_id)
    )
    ''')

def insert_sample_data(cursor):
    """Insert comprehensive sample data"""
    
    # Clear existing data first to avoid conflicts
    print("  Clearing existing data...")
    cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
    cursor.execute("DELETE FROM court_appearances")
    cursor.execute("DELETE FROM legal_documents")
    cursor.execute("DELETE FROM billable_hours")
    cursor.execute("DELETE FROM cases")
    cursor.execute("DELETE FROM contracts")
    cursor.execute("DELETE FROM attorneys")
    cursor.execute("DELETE FROM clients")
    cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
    
    # Sample clients data - 8 clients
    clients_data = [
        ('TechCorp Inc.', 'TechCorp Inc.', 'legal@techcorp.com', '555-0101', '123 Tech St', 'Corporate', 'Technology', '2023-01-15', 'Active', 250000.00),
        ('Smith Industries', 'Smith Industries', 'contact@smith.com', '555-0102', '456 Industry Ave', 'Corporate', 'Manufacturing', '2023-02-20', 'Active', 180000.00),
        ('Johnson LLC', 'Johnson LLC', 'info@johnson.com', '555-0103', '789 Business Blvd', 'LLC', 'Consulting', '2023-03-10', 'Active', 120000.00),
        ('Davis Enterprises', 'Davis Enterprises', 'legal@davis.com', '555-0104', '321 Commerce Dr', 'Corporate', 'Retail', '2023-04-05', 'Active', 90000.00),
        ('Wilson Holdings', 'Wilson Holdings', 'admin@wilson.com', '555-0105', '654 Finance St', 'Holdings', 'Finance', '2023-05-12', 'Active', 340000.00),
        ('Green Energy Co.', 'Green Energy Co.', 'contracts@greenenergy.com', '555-0106', '987 Solar Way', 'Corporate', 'Energy', '2023-06-18', 'Active', 420000.00),
        ('Healthcare Plus', 'Healthcare Plus', 'legal@healthplus.com', '555-0107', '258 Medical Dr', 'Corporate', 'Healthcare', '2023-07-22', 'Active', 280000.00),
        ('Martinez Retail', 'Martinez Retail', 'admin@martinez.com', '555-0108', '147 Shopping Plaza', 'Corporate', 'Retail', '2023-08-30', 'Active', 75000.00)
    ]
    
    cursor.executemany('''
    INSERT INTO clients (name, company, contact_email, phone, address, client_type, industry, created_date, status, total_value)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    ''', clients_data)
    
    # Sample attorneys data - 7 attorneys
    attorneys_data = [
        ('Sarah Johnson', 'Corporate Law', 8, 450.00, 'New York', '2020-03-15', 'Active', 'NY123456', 'sarah.johnson@firm.com'),
        ('Michael Chen', 'Litigation', 12, 525.00, 'Los Angeles', '2018-07-20', 'Active', 'CA789012', 'michael.chen@firm.com'),
        ('Emily Davis', 'Intellectual Property', 6, 400.00, 'San Francisco', '2021-09-10', 'Active', 'CA345678', 'emily.davis@firm.com'),
        ('Robert Wilson', 'Employment Law', 15, 475.00, 'Chicago', '2016-01-05', 'Active', 'IL901234', 'robert.wilson@firm.com'),
        ('Lisa Anderson', 'Real Estate', 10, 425.00, 'Miami', '2019-11-30', 'Active', 'FL567890', 'lisa.anderson@firm.com'),
        ('David Park', 'Tax Law', 14, 500.00, 'New York', '2017-04-12', 'Active', 'NY246810', 'david.park@firm.com'),
        ('Jennifer Lee', 'Healthcare Law', 9, 460.00, 'Houston', '2020-08-25', 'Active', 'TX135792', 'jennifer.lee@firm.com')
    ]
    
    cursor.executemany('''
    INSERT INTO attorneys (name, practice_area, years_experience, hourly_rate, office_location, hire_date, status, bar_number, email)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    ''', attorneys_data)
    
    # Generate sample cases - 30 cases
    case_types = ['Contract Dispute', 'Employment Law', 'IP Infringement', 'Corporate Merger', 'Real Estate', 'Tax Matter', 'Compliance Issue']
    case_statuses = ['Open', 'In Progress', 'Closed', 'Settled', 'On Hold']
    outcomes = ['Won', 'Lost', 'Settled', 'Ongoing', 'Dismissed']
    
    # Get actual client and attorney IDs from the database
    cursor.execute("SELECT client_id FROM clients")
    client_ids = [row[0] for row in cursor.fetchall()]
    
    cursor.execute("SELECT attorney_id FROM attorneys")
    attorney_ids = [row[0] for row in cursor.fetchall()]
    
    cases_data = []
    for i in range(30):
        filing_date = datetime.now() - timedelta(days=random.randint(30, 730))
        resolution_date = None
        if random.choice([True, False, False]):  # 1/3 chance of being resolved
            resolution_date = filing_date + timedelta(days=random.randint(30, 365))
        
        case_data = (
            f'CASE-2024-{i+1:03d}',
            random.choice(client_ids),  # Use actual client_id
            random.choice(attorney_ids),  # Use actual attorney_id
            random.choice(case_types),
            random.choice(case_statuses),
            filing_date.date(),
            resolution_date.date() if resolution_date else None,
            random.uniform(25000, 750000),
            random.choice(outcomes),
            f'Legal matter involving {random.choice(case_types).lower()}'
        )
        cases_data.append(case_data)
    
    cursor.executemany('''
    INSERT INTO cases (case_number, client_id, attorney_id, case_type, case_status, 
                      filing_date, resolution_date, case_value, outcome, description)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    ''', cases_data)
    
    # Generate sample contracts - 20 contracts
    contract_types = ['Service Agreement', 'Employment Contract', 'NDA', 'Licensing Agreement', 'Partnership Agreement']
    contract_statuses = ['Active', 'Expired', 'Pending', 'Terminated']
    
    contracts_data = []
    for i in range(20):
        start_date = datetime.now() - timedelta(days=random.randint(30, 1095))
        end_date = start_date + timedelta(days=random.randint(365, 1095))
        
        contract_data = (
            random.choice(client_ids),  # Use actual client_id
            random.choice(contract_types),
            random.uniform(10000, 500000),
            start_date.date(),
            end_date.date(),
            random.choice(contract_statuses),
            start_date.date()
        )
        contracts_data.append(contract_data)
    
    cursor.executemany('''
    INSERT INTO contracts (client_id, contract_type, contract_value, start_date, end_date, status, created_date)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    ''', contracts_data)
    
    # Generate sample billable hours - 150 entries
    task_categories = ['Research', 'Client Meetings', 'Court Appearances', 'Document Review', 'Drafting', 'Negotiations']
    bill_statuses = ['Billed', 'Pending', 'Paid', 'Overdue']
    
    # Get case IDs for billable hours
    cursor.execute("SELECT case_id FROM cases")
    case_ids = [row[0] for row in cursor.fetchall()]
    
    billable_data = []
    for i in range(150):
        work_date = datetime.now() - timedelta(days=random.randint(1, 365))
        attorney_id = random.choice(attorney_ids)
        client_id = random.choice(client_ids)
        hours = round(random.uniform(0.5, 8.0), 2)
        rate = random.choice([400, 425, 450, 460, 475, 500, 525])
        
        billable_entry = (
            attorney_id,
            client_id,
            random.choice(case_ids) if random.choice([True, False]) else None,  # case_id (optional)
            work_date.date(),
            hours,
            rate,
            round(hours * rate, 2),
            f'{random.choice(task_categories)} work performed for client matter.',
            random.choice(task_categories),
            random.choice(bill_statuses)
        )
        billable_data.append(billable_entry)
    
    cursor.executemany('''
    INSERT INTO billable_hours (attorney_id, client_id, case_id, work_date, hours_worked, 
                               hourly_rate, total_amount, work_description, task_category, billed_status)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    ''', billable_data)
    
    # Generate sample legal documents - 50 documents
    doc_types = ['Contract', 'Brief', 'Motion', 'Discovery', 'Settlement Agreement', 'Court Order', 'Correspondence']
    doc_statuses = ['Active', 'Archived', 'Under Review', 'Draft']
    
    legal_docs_data = []
    for i in range(50):
        upload_date = datetime.now() - timedelta(days=random.randint(1, 365))
        case_id = random.choice(case_ids) if random.choice([True, False]) else None
        client_id = random.choice(client_ids)
        
        doc_data = (
            case_id,
            client_id,
            random.choice(doc_types),
            f'{random.choice(doc_types)} Document {i+1}',
            f'documents/case_{case_id or "general"}/doc_{i+1}.pdf',
            upload_date.date(),
            random.randint(1024, 10485760),  # 1KB to 10MB
            random.choice(doc_statuses),
            f'Legal document related to {random.choice(doc_types).lower()}'
        )
        legal_docs_data.append(doc_data)
    
    cursor.executemany('''
    INSERT INTO legal_documents (case_id, client_id, document_type, title, file_path, 
                                upload_date, file_size, status, description)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    ''', legal_docs_data)
    
    # Generate sample court appearances - 25 appearances
    appearance_types = ['Hearing', 'Trial', 'Deposition', 'Mediation', 'Settlement Conference']
    courts = ['Supreme Court', 'District Court', 'Circuit Court', 'Family Court', 'Bankruptcy Court']
    outcomes = ['Favorable', 'Unfavorable', 'Continued', 'Settled', 'Dismissed']
    
    appearances_data = []
    for i in range(25):
        appearance_date = datetime.now() - timedelta(days=random.randint(1, 180))
        case_id = random.choice(case_ids)
        attorney_id = random.choice(attorney_ids)
        
        appearance_data = (
            case_id,
            attorney_id,
            random.choice(courts),
            appearance_date.date(),
            random.choice(appearance_types),
            round(random.uniform(1.0, 6.0), 2),
            f'Court appearance for {random.choice(appearance_types).lower()}',
            random.choice(outcomes)
        )
        appearances_data.append(appearance_data)
    
    cursor.executemany('''
    INSERT INTO court_appearances (case_id, attorney_id, court_name, appearance_date, 
                                  appearance_type, duration_hours, notes, outcome)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    ''', appearances_data)

def create_indexes(cursor):
    """Create indexes for better query performance"""
    indexes = [
        'CREATE INDEX idx_clients_status ON clients(status)',
        'CREATE INDEX idx_clients_industry ON clients(industry)',
        'CREATE INDEX idx_cases_status ON cases(case_status)',
        'CREATE INDEX idx_cases_date ON cases(filing_date)',
        'CREATE INDEX idx_cases_attorney ON cases(attorney_id)',
        'CREATE INDEX idx_contracts_client ON contracts(client_id)',
        'CREATE INDEX idx_contracts_status ON contracts(status)',
        'CREATE INDEX idx_billable_attorney_date ON billable_hours(attorney_id, work_date)',
        'CREATE INDEX idx_billable_client ON billable_hours(client_id)',
        'CREATE INDEX idx_attorneys_practice ON attorneys(practice_area)',
        'CREATE INDEX idx_documents_case ON legal_documents(case_id)',
        'CREATE INDEX idx_documents_type ON legal_documents(document_type)',
        'CREATE INDEX idx_appearances_date ON court_appearances(appearance_date)',
        'CREATE INDEX idx_appearances_case ON court_appearances(case_id)'
    ]
    
    for index_sql in indexes:
        try:
            cursor.execute(index_sql)
        except Error as e:
            # Index might already exist, continue
            print(f"  Note: Index creation skipped - {e}")

def verify_database(config):
    """Verify database was created correctly"""
    try:
        conn = mysql.connector.connect(**config)
        cursor = conn.cursor()
        
        tables = ['clients', 'attorneys', 'cases', 'contracts', 'billable_hours', 'legal_documents', 'court_appearances']
        
        print("\n📊 Database Statistics:")
        for table in tables:
            cursor.execute(f'SELECT COUNT(*) FROM {table}')
            count = cursor.fetchone()[0]
            print(f"  {table.title()}: {count} records")
        
        # Test a sample query
        cursor.execute('''
        SELECT c.name, COUNT(cs.case_id) as case_count, COALESCE(SUM(bh.total_amount), 0) as total_billed
        FROM clients c
        LEFT JOIN cases cs ON c.client_id = cs.client_id
        LEFT JOIN billable_hours bh ON c.client_id = bh.client_id
        GROUP BY c.client_id
        ORDER BY total_billed DESC
        LIMIT 3
        ''')
        
        results = cursor.fetchall()
        print("\n🏆 Top 3 Clients by Revenue:")
        for i, (name, cases, revenue) in enumerate(results, 1):
            print(f"  {i}. {name}: {cases} cases, ${revenue:,.2f} billed")
        
        # Test attorney performance query
        cursor.execute('''
        SELECT a.name, a.practice_area, COUNT(cs.case_id) as cases_handled, 
               COALESCE(AVG(cs.case_value), 0) as avg_case_value
        FROM attorneys a
        LEFT JOIN cases cs ON a.attorney_id = cs.attorney_id
        GROUP BY a.attorney_id
        ORDER BY cases_handled DESC
        LIMIT 3
        ''')
        
        results = cursor.fetchall()
        print("\n⚖️ Top 3 Attorneys by Case Load:")
        for i, (name, practice, cases, avg_value) in enumerate(results, 1):
            print(f"  {i}. {name} ({practice}): {cases} cases, avg value ${avg_value:,.2f}")
        
    except Error as e:
        print(f"❌ Error verifying database: {e}")
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

if __name__ == "__main__":
    create_sample_legal_database()
