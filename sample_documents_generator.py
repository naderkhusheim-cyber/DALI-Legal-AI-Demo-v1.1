#!/usr/bin/env python3
"""
DALI Legal AI - Sample Legal Documents Generator
Creates realistic sample legal documents for testing the system
"""

import os
import json
from datetime import datetime, timedelta
from pathlib import Path
import random


class SampleDocumentGenerator:
    """Generates sample legal documents for testing DALI Legal AI"""
    
    def __init__(self, output_dir: str = "sample_documents"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Sample legal content templates
        self.document_templates = {
            "contract": self._get_contract_template(),
            "regulation": self._get_regulation_template(),
            "case_law": self._get_case_law_template(),
            "legal_opinion": self._get_legal_opinion_template(),
            "compliance_guide": self._get_compliance_guide_template()
        }
    
    def _get_contract_template(self):
        return """
COMMERCIAL SERVICES AGREEMENT

This Commercial Services Agreement ("Agreement") is entered into on {date} between {party_a} ("Service Provider"), a company incorporated under the laws of Saudi Arabia, and {party_b} ("Client"), a company incorporated under the laws of Saudi Arabia.

WHEREAS, Service Provider desires to provide {service_type} services to Client; and
WHEREAS, Client desires to engage Service Provider to provide such services;

NOW, THEREFORE, in consideration of the mutual covenants contained herein, the parties agree as follows:

1. SERVICES
Service Provider shall provide {service_description} in accordance with the specifications set forth in Exhibit A attached hereto and incorporated herein by reference.

2. TERM
This Agreement shall commence on {start_date} and shall continue for a period of {duration}, unless earlier terminated in accordance with the provisions hereof.

3. COMPENSATION
In consideration for the services provided hereunder, Client shall pay Service Provider a total fee of SAR {amount} payable in accordance with the payment schedule set forth in Exhibit B.

4. CONFIDENTIALITY
Each party acknowledges that it may have access to confidential information of the other party. Each party agrees to maintain the confidentiality of such information and not to disclose it to third parties without prior written consent.

5. GOVERNING LAW
This Agreement shall be governed by and construed in accordance with the laws of the Kingdom of Saudi Arabia. Any disputes arising hereunder shall be resolved through arbitration in Riyadh, Saudi Arabia.

6. COMPLIANCE
Both parties shall comply with all applicable laws and regulations of Saudi Arabia, including but not limited to the Commercial Law, Labor Law, and any relevant regulatory requirements.

IN WITNESS WHEREOF, the parties have executed this Agreement as of the date first written above.

{party_a}                           {party_b}
By: _________________              By: _________________
Name: {signatory_a}                Name: {signatory_b}
Title: {title_a}                   Title: {title_b}
Date: {date}                       Date: {date}
"""
    
    def _get_regulation_template(self):
        return """
MINISTRY OF {ministry} REGULATION NO. {reg_number}
REGARDING {regulation_subject}

Issued on: {issue_date}
Effective Date: {effective_date}

CHAPTER 1: GENERAL PROVISIONS

Article 1: Definitions
For the purposes of this regulation, the following terms shall have the meanings assigned to them:
1. "{term_1}": means {definition_1}
2. "{term_2}": means {definition_2}
3. "Authority": means the {authority_name}
4. "Kingdom": means the Kingdom of Saudi Arabia

Article 2: Scope of Application
This regulation applies to all {scope_description} operating within the Kingdom of Saudi Arabia.

Article 3: Objectives
The objectives of this regulation are:
1. To ensure {objective_1}
2. To promote {objective_2}
3. To protect {objective_3}

CHAPTER 2: REQUIREMENTS AND OBLIGATIONS

Article 4: Licensing Requirements
Any entity seeking to {activity_description} must obtain a license from the Authority in accordance with the following requirements:
1. Submit a complete application form
2. Provide evidence of {requirement_1}
3. Demonstrate compliance with {requirement_2}
4. Pay the prescribed fees

Article 5: Ongoing Obligations
Licensed entities must:
1. Maintain {obligation_1}
2. Submit periodic reports as specified by the Authority
3. Comply with all applicable laws and regulations
4. Notify the Authority of any material changes

CHAPTER 3: ENFORCEMENT AND PENALTIES

Article 6: Violations
Violations of this regulation may result in:
1. Warning notices
2. Monetary penalties up to SAR {penalty_amount}
3. Suspension of license
4. Revocation of license

Article 7: Appeals
Any person aggrieved by a decision of the Authority may appeal to the {appeal_body} within {appeal_period} days of notification.

This regulation shall come into effect {effective_period} after its publication in the Official Gazette.

Minister of {ministry}
{minister_name}
Date: {issue_date}
"""
    
    def _get_case_law_template(self):
        return """
KINGDOM OF SAUDI ARABIA
{court_name}
Case No. {case_number}/{year}

{plaintiff} v. {defendant}

JUDGMENT

Date of Hearing: {hearing_date}
Date of Judgment: {judgment_date}

BEFORE: {judge_name}, Judge

FACTS:
The plaintiff, {plaintiff}, filed this action against the defendant, {defendant}, seeking {relief_sought}. The dispute arose from {dispute_background}.

The plaintiff alleges that {plaintiff_allegations}.

The defendant contends that {defendant_contentions}.

LEGAL ANALYSIS:
The court has considered the evidence presented and the applicable law, including:
1. The Commercial Law of Saudi Arabia
2. The {applicable_law}
3. Relevant judicial precedents

The key legal issues in this case are:
1. {legal_issue_1}
2. {legal_issue_2}

FINDINGS:
After careful consideration of the evidence and legal arguments, the court finds:

1. {finding_1}
2. {finding_2}
3. {finding_3}

RULING:
Based on the foregoing analysis and in accordance with Islamic Sharia principles and Saudi Arabian law, the court hereby:

1. {ruling_1}
2. {ruling_2}
3. Orders the defendant to pay court costs

This judgment is final and binding. Either party may appeal this decision to the Court of Appeal within {appeal_period} days of notification.

{judge_name}
Judge
{court_name}
Date: {judgment_date}
"""
    
    def _get_legal_opinion_template(self):
        return """
LEGAL OPINION

TO: {client_name}
FROM: {law_firm_name}
DATE: {opinion_date}
RE: {matter_description}

EXECUTIVE SUMMARY:
This legal opinion addresses {legal_question} under Saudi Arabian law. Based on our analysis, we conclude that {conclusion_summary}.

FACTUAL BACKGROUND:
{factual_background}

LEGAL ANALYSIS:

1. Applicable Law
The relevant legal framework includes:
- {applicable_law_1}
- {applicable_law_2}
- {applicable_law_3}

2. Key Legal Principles
Under Saudi Arabian law, the following principles apply:
- {principle_1}
- {principle_2}
- {principle_3}

3. Analysis of Specific Issues

Issue 1: {issue_1}
{analysis_1}

Issue 2: {issue_2}
{analysis_2}

Issue 3: {issue_3}
{analysis_3}

CONCLUSION:
Based on the foregoing analysis, it is our opinion that:

1. {conclusion_1}
2. {conclusion_2}
3. {conclusion_3}

RECOMMENDATIONS:
We recommend the following course of action:
1. {recommendation_1}
2. {recommendation_2}
3. {recommendation_3}

LIMITATIONS:
This opinion is based on Saudi Arabian law as it exists on the date hereof and is subject to the following limitations:
- {limitation_1}
- {limitation_2}

This opinion is confidential and prepared solely for the use of {client_name}.

{lawyer_name}
Partner
{law_firm_name}
Saudi Bar Association License No. {license_number}
"""
    
    def _get_compliance_guide_template(self):
        return """
COMPLIANCE GUIDE: {compliance_topic}

Prepared by: {authority_name}
Version: {version}
Last Updated: {update_date}

1. INTRODUCTION

This guide provides practical guidance on compliance with {regulation_name} for {target_audience}. It is designed to help organizations understand their obligations and implement effective compliance programs.

2. REGULATORY OVERVIEW

{regulation_name} requires organizations to:
- {requirement_1}
- {requirement_2}
- {requirement_3}

Key deadlines:
- {deadline_1}: {deadline_1_desc}
- {deadline_2}: {deadline_2_desc}

3. COMPLIANCE CHECKLIST

Phase 1: Initial Assessment
□ Review current {process_area}
□ Identify gaps in compliance
□ Develop implementation timeline
□ Assign compliance responsibilities

Phase 2: Implementation
□ {implementation_step_1}
□ {implementation_step_2}
□ {implementation_step_3}
□ Train relevant personnel

Phase 3: Monitoring and Review
□ Establish monitoring procedures
□ Conduct regular compliance audits
□ Update policies as needed
□ Report to relevant authorities

4. COMMON COMPLIANCE ISSUES

Issue 1: {common_issue_1}
Solution: {solution_1}

Issue 2: {common_issue_2}
Solution: {solution_2}

Issue 3: {common_issue_3}
Solution: {solution_3}

5. PENALTIES FOR NON-COMPLIANCE

Violations may result in:
- Administrative penalties up to SAR {penalty_amount}
- {penalty_type_1}
- {penalty_type_2}

6. RESOURCES AND CONTACTS

For additional guidance:
- Website: {authority_website}
- Email: {contact_email}
- Phone: {contact_phone}

This guide is for informational purposes only and does not constitute legal advice. Organizations should consult with qualified legal counsel for specific compliance questions.

© {year} {authority_name}. All rights reserved.
"""
    
    def generate_sample_documents(self, num_documents: int = 20):
        """Generate sample legal documents"""
        documents = []
        
        for i in range(num_documents):
            doc_type = random.choice(list(self.document_templates.keys()))
            doc_data = self._generate_document_data(doc_type, i + 1)
            
            # Generate document content
            template = self.document_templates[doc_type]
            content = template.format(**doc_data['variables'])
            
            # Save document
            filename = f"{doc_type}_{i+1:03d}_{doc_data['variables'].get('date', '').replace('-', '')}.txt"
            file_path = self.output_dir / filename
            
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(content)
            
            doc_info = {
                'filename': filename,
                'type': doc_type,
                'title': doc_data['title'],
                'metadata': doc_data['metadata'],
                'file_path': str(file_path),
                'content_length': len(content)
            }
            
            documents.append(doc_info)
        
        # Save document index
        index_file = self.output_dir / "document_index.json"
        with open(index_file, 'w', encoding='utf-8') as file:
            json.dump({
                'generated_date': datetime.now().isoformat(),
                'total_documents': len(documents),
                'documents': documents
            }, file, indent=2, ensure_ascii=False)
        
        return documents
    
    def _generate_document_data(self, doc_type: str, doc_number: int):
        """Generate realistic data for document templates"""
        base_date = datetime.now() - timedelta(days=random.randint(1, 365))
        
        companies = [
            "Al-Rajhi Trading Company", "Saudi Tech Solutions Ltd.", "Riyadh Commercial Services",
            "Jeddah Investment Group", "Dammam Industrial Corp.", "Makkah Business Center",
            "Medina Consulting Services", "Tabuk Development Co.", "Abha Trading House"
        ]
        
        people = [
            "Ahmed Al-Mahmoud", "Fatima Al-Zahra", "Mohammed Al-Rashid", "Aisha Al-Fahad",
            "Omar Al-Saud", "Nora Al-Otaibi", "Khalid Al-Mutairi", "Layla Al-Dosari"
        ]
        
        if doc_type == "contract":
            return {
                'title': f"Commercial Services Agreement {doc_number}",
                'variables': {
                    'date': base_date.strftime('%Y-%m-%d'),
                    'party_a': random.choice(companies),
                    'party_b': random.choice(companies),
                    'service_type': random.choice(['consulting', 'technology', 'marketing', 'logistics']),
                    'service_description': 'comprehensive business consulting services',
                    'start_date': base_date.strftime('%Y-%m-%d'),
                    'duration': random.choice(['12 months', '24 months', '36 months']),
                    'amount': f"{random.randint(100000, 1000000):,}",
                    'signatory_a': random.choice(people),
                    'signatory_b': random.choice(people),
                    'title_a': 'Chief Executive Officer',
                    'title_b': 'General Manager'
                },
                'metadata': {
                    'document_type': 'contract',
                    'jurisdiction': 'Saudi Arabia',
                    'practice_area': 'commercial_law',
                    'date_created': base_date.isoformat()
                }
            }
        
        elif doc_type == "regulation":
            ministries = ['Commerce', 'Justice', 'Interior', 'Finance', 'Health', 'Education']
            return {
                'title': f"Regulation on {random.choice(['Commercial Activities', 'Data Protection', 'Consumer Rights'])}",
                'variables': {
                    'ministry': random.choice(ministries),
                    'reg_number': f"{random.randint(100, 999)}/{base_date.year}",
                    'regulation_subject': 'Commercial Activities Licensing',
                    'issue_date': base_date.strftime('%Y-%m-%d'),
                    'effective_date': (base_date + timedelta(days=30)).strftime('%Y-%m-%d'),
                    'term_1': 'Commercial Activity',
                    'definition_1': 'any business activity conducted for profit',
                    'term_2': 'License',
                    'definition_2': 'official authorization to conduct commercial activities',
                    'authority_name': f'Ministry of {random.choice(ministries)}',
                    'scope_description': 'commercial entities',
                    'objective_1': 'regulatory compliance',
                    'objective_2': 'consumer protection',
                    'objective_3': 'market integrity',
                    'activity_description': 'engage in commercial activities',
                    'requirement_1': 'financial capability',
                    'requirement_2': 'technical competence',
                    'obligation_1': 'proper records',
                    'penalty_amount': f"{random.randint(10000, 100000):,}",
                    'appeal_body': 'Administrative Court',
                    'appeal_period': '30',
                    'effective_period': '30 days',
                    'minister_name': random.choice(people)
                },
                'metadata': {
                    'document_type': 'regulation',
                    'jurisdiction': 'Saudi Arabia',
                    'practice_area': 'regulatory_law',
                    'date_created': base_date.isoformat()
                }
            }
        
        elif doc_type == "case_law":
            return {
                'title': f"Commercial Dispute Case {doc_number}",
                'variables': {
                    'court_name': 'Commercial Court of Riyadh',
                    'case_number': f"{random.randint(1000, 9999)}",
                    'year': base_date.year,
                    'plaintiff': random.choice(companies),
                    'defendant': random.choice(companies),
                    'hearing_date': base_date.strftime('%Y-%m-%d'),
                    'judgment_date': (base_date + timedelta(days=30)).strftime('%Y-%m-%d'),
                    'judge_name': random.choice(people),
                    'relief_sought': 'damages for breach of contract',
                    'dispute_background': 'a commercial services agreement',
                    'plaintiff_allegations': 'the defendant failed to perform its contractual obligations',
                    'defendant_contentions': 'it performed all obligations in accordance with the agreement',
                    'applicable_law': 'Law of Commercial Transactions',
                    'legal_issue_1': 'interpretation of contractual terms',
                    'legal_issue_2': 'calculation of damages',
                    'finding_1': 'the defendant breached the agreement',
                    'finding_2': 'the plaintiff is entitled to damages',
                    'finding_3': 'the amount of damages is SAR 150,000',
                    'ruling_1': 'Judgment in favor of the plaintiff',
                    'ruling_2': f'Defendant to pay SAR {random.randint(50000, 500000):,} in damages',
                    'appeal_period': '30'
                },
                'metadata': {
                    'document_type': 'case_law',
                    'jurisdiction': 'Saudi Arabia',
                    'practice_area': 'commercial_litigation',
                    'date_created': base_date.isoformat()
                }
            }
        
        elif doc_type == "legal_opinion":
            return {
                'title': f"Legal Opinion on {random.choice(['Corporate Governance', 'Contract Interpretation', 'Regulatory Compliance'])}",
                'variables': {
                    'client_name': random.choice(companies),
                    'law_firm_name': 'Al-Riyadh Legal Consultancy',
                    'opinion_date': base_date.strftime('%Y-%m-%d'),
                    'matter_description': 'Corporate Governance Compliance',
                    'legal_question': 'compliance with new corporate governance regulations',
                    'conclusion_summary': 'the company can achieve compliance through specific measures',
                    'factual_background': 'The client is a publicly listed company seeking guidance on compliance.',
                    'applicable_law_1': 'Companies Law',
                    'applicable_law_2': 'Capital Market Law',
                    'applicable_law_3': 'Corporate Governance Regulations',
                    'principle_1': 'Board independence requirements',
                    'principle_2': 'Disclosure obligations',
                    'principle_3': 'Shareholder rights protection',
                    'issue_1': 'Board composition requirements',
                    'analysis_1': 'The company must ensure at least one-third independent directors.',
                    'issue_2': 'Audit committee establishment',
                    'analysis_2': 'An audit committee with specific qualifications is required.',
                    'issue_3': 'Disclosure requirements',
                    'analysis_3': 'Regular disclosure of material information is mandatory.',
                    'conclusion_1': 'The company can achieve compliance',
                    'conclusion_2': 'Specific structural changes are required',
                    'conclusion_3': 'Implementation timeline should be 6 months',
                    'recommendation_1': 'Appoint additional independent directors',
                    'recommendation_2': 'Establish qualified audit committee',
                    'recommendation_3': 'Implement disclosure procedures',
                    'limitation_1': 'Based on current law as of opinion date',
                    'limitation_2': 'Subject to regulatory interpretation',
                    'lawyer_name': random.choice(people),
                    'license_number': f"{random.randint(1000, 9999)}"
                },
                'metadata': {
                    'document_type': 'legal_opinion',
                    'jurisdiction': 'Saudi Arabia',
                    'practice_area': 'corporate_law',
                    'date_created': base_date.isoformat()
                }
            }
        
        elif doc_type == "compliance_guide":
            return {
                'title': f"Compliance Guide: {random.choice(['Data Protection', 'Anti-Money Laundering', 'Consumer Protection'])}",
                'variables': {
                    'compliance_topic': 'Data Protection Law Compliance',
                    'authority_name': 'Saudi Data & AI Authority',
                    'version': '2.0',
                    'update_date': base_date.strftime('%Y-%m-%d'),
                    'regulation_name': 'Personal Data Protection Law',
                    'target_audience': 'data controllers and processors',
                    'requirement_1': 'Obtain valid consent for data processing',
                    'requirement_2': 'Implement appropriate security measures',
                    'requirement_3': 'Respect data subject rights',
                    'deadline_1': (base_date + timedelta(days=90)).strftime('%Y-%m-%d'),
                    'deadline_1_desc': 'Initial compliance assessment',
                    'deadline_2': (base_date + timedelta(days=180)).strftime('%Y-%m-%d'),
                    'deadline_2_desc': 'Full implementation',
                    'process_area': 'data processing activities',
                    'implementation_step_1': 'Conduct data mapping exercise',
                    'implementation_step_2': 'Update privacy policies',
                    'implementation_step_3': 'Implement technical safeguards',
                    'common_issue_1': 'Unclear consent mechanisms',
                    'solution_1': 'Implement clear, specific consent forms',
                    'common_issue_2': 'Inadequate security measures',
                    'solution_2': 'Conduct security risk assessment',
                    'common_issue_3': 'Lack of data subject procedures',
                    'solution_3': 'Establish data subject request handling process',
                    'penalty_amount': f"{random.randint(100000, 1000000):,}",
                    'penalty_type_1': 'Suspension of data processing activities',
                    'penalty_type_2': 'Public disclosure of violations',
                    'authority_website': 'https://sdaia.gov.sa',
                    'contact_email': 'info@sdaia.gov.sa',
                    'contact_phone': '+966-11-XXXXXXX',
                    'year': base_date.year
                },
                'metadata': {
                    'document_type': 'compliance_guide',
                    'jurisdiction': 'Saudi Arabia',
                    'practice_area': 'data_protection',
                    'date_created': base_date.isoformat()
                }
            }
        
        return {'title': f'Document {doc_number}', 'variables': {}, 'metadata': {}}


def main():
    """Generate sample legal documents"""
    print("🏗️ DALI Legal AI - Sample Document Generator")
    print("=" * 50)
    
    generator = SampleDocumentGenerator()
    
    print("📄 Generating sample legal documents...")
    documents = generator.generate_sample_documents(20)
    
    print(f"✅ Generated {len(documents)} sample documents")
    print(f"📁 Documents saved to: {generator.output_dir}")
    
    # Print summary
    doc_types = {}
    for doc in documents:
        doc_type = doc['type']
        doc_types[doc_type] = doc_types.get(doc_type, 0) + 1
    
    print("\n📊 Document Summary:")
    for doc_type, count in doc_types.items():
        print(f"   {doc_type}: {count} documents")
    
    print(f"\n📋 Document index saved to: {generator.output_dir}/document_index.json")
    print("\n🚀 Ready for testing with DALI Legal AI system!")


if __name__ == "__main__":
    main()

