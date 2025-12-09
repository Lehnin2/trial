#!/usr/bin/env python3
"""
Compliance Analyzer - Replicates LLM-based document verification approach
Uses semantic analysis via LLM API to verify fund documents against registration database
Uses LLM with automatic fallback (TokenFactory -> Gemini)
"""

import json
import csv
import sys
from typing import Dict, List, Any, Tuple
from pathlib import Path
from dotenv import load_dotenv
import os
import re

# Import path utilities
from path_utils import ENV_FILE, ensure_directories

# Import LLM Manager with fallback support
from llm_manager import llm_manager

# Load environment variables from .env file
load_dotenv(str(ENV_FILE))


class ComplianceAnalyzer:
    """
    Analyzes fund presentation documents for compliance using LLM-based semantic reasoning
    Uses automatic fallback between TokenFactory and Gemini
    """
    
    def __init__(self, api_key: str = None):
        """Initialize the analyzer - uses llm_manager with automatic fallback"""
        self.llm = llm_manager
        
    def load_document(self, json_path: str) -> Dict[str, Any]:
        """Load the fund presentation document"""
        with open(json_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def load_metadata(self, metadata_path: str) -> Dict[str, Any]:
        """Load the document metadata"""
        with open(metadata_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def load_registration_csv(self, csv_path: str) -> List[Dict[str, str]]:
        """Load the registration database"""
        registrations = []
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                registrations.append(row)
        return registrations
    
    def analyze_csv_patterns(self, registrations: List[Dict[str, str]]) -> Dict[str, Any]:
        """Analyze patterns in the registration database"""
        patterns = {
            'total_funds': len(registrations),
            'fund_families': set(),
            'isin_prefixes': {},
            'common_countries': {},
            'fund_types': set()
        }
        
        for reg in registrations:
            patterns['fund_families'].add(reg.get('fund_family', ''))
            
            isin = reg.get('isin', '')
            if isin:
                prefix = isin[:2]
                patterns['isin_prefixes'][prefix] = patterns['isin_prefixes'].get(prefix, 0) + 1
            
            countries = reg.get('authorized_countries_list', '')
            for country in countries.split(','):
                country = country.strip()
                if country:
                    patterns['common_countries'][country] = patterns['common_countries'].get(country, 0) + 1
            
            fund_name = reg.get('fund_name', '')
            if 'ETF' in fund_name.upper():
                patterns['fund_types'].add('ETF')
            if 'SICAV' in fund_name.upper():
                patterns['fund_types'].add('SICAV')
        
        return patterns
    
    def search_fund_in_csv(self, document: Dict, registrations: List[Dict]) -> Tuple[bool, List[Dict]]:
        """Search for the fund in registration database"""
        fund_isin = None
        fund_name = None
        
        # Extract ISIN and fund name from document
        if 'document_metadata' in document:
            fund_isin = document['document_metadata'].get('fund_isin', '')
        
        if 'page_de_garde' in document:
            content = document['page_de_garde'].get('content', {})
            if isinstance(content, dict):
                fund_name = content.get('fund_name', '')
        
        # Also check in tables
        if 'page_de_fin' in document:
            content = document['page_de_fin'].get('content', {})
            tables = content.get('tables', []) if isinstance(content, dict) else []
            for table in tables:
                for row in table.get('rows', []):
                    if isinstance(row, dict):
                        cols = row.get('columns', [])
                        for i, col in enumerate(cols):
                            if col.get('text', '') == 'ISIN code' and i + 1 < len(cols):
                                fund_isin = cols[i + 1].get('text', '')
        
        # Search in CSV
        matches = []
        for reg in registrations:
            if fund_isin and reg.get('isin', '') == fund_isin:
                matches.append(reg)
            elif fund_name and reg.get('fund_name', '') == fund_name:
                matches.append(reg)
        
        return len(matches) > 0, matches
    
    def call_llm_analysis(self, prompt: str, temperature: float = 0.3) -> str:
        """Call the LLM API for semantic analysis with automatic fallback"""
        system_prompt = "You are a compliance analyst expert specializing in financial fund documentation. Provide precise, structured analysis."
        
        result = self.llm.call_llm(
            system_prompt=system_prompt,
            user_prompt=prompt,
            temperature=temperature,
            max_tokens=2000
        )
        
        if result:
            return result
        return f"Error calling LLM API: {self.llm.last_error}"
    
    def phase1_structural_analysis(self, document: Dict) -> Dict[str, Any]:
        """Phase 1: Analyze document structure and identify missing fields"""
        print("\n" + "="*80)
        print("PHASE 1: DOCUMENT STRUCTURE ANALYSIS")
        print("="*80)
        
        issues = {
            'missing_fields': [],
            'empty_fields': [],
            'present_fields': []
        }
        
        # Check metadata fields
        metadata = document.get('document_metadata', {})
        required_metadata = ['fund_isin', 'language', 'country', 'fund_esg_classification']
        
        for field in required_metadata:
            value = metadata.get(field, '')
            if not value or value == '':
                issues['empty_fields'].append(f"metadata.{field}")
            else:
                issues['present_fields'].append(f"metadata.{field}")
        
        # Check fund characteristics
        if 'page_de_fin' in document:
            content = document['page_de_fin'].get('content', {})
            # Handle both dict and list content structures
            if isinstance(content, dict):
                fund_chars = content.get('fund_characteristics', {})
                if fund_chars.get('srri', '') == '':
                    issues['empty_fields'].append('fund_characteristics.srri')
                if fund_chars.get('aum', '') == '':
                    issues['empty_fields'].append('fund_characteristics.aum')
            elif isinstance(content, list):
                # Content is a list of text items from PPTX extraction
                # Skip fund_characteristics check for this format
                pass
        
        print(f"\n✓ Present fields: {len(issues['present_fields'])}")
        print(f"⚠ Empty fields: {len(issues['empty_fields'])}")
        for field in issues['empty_fields']:
            print(f"  - {field}")
        
        return issues
    
    def phase2_csv_verification(self, document: Dict, registrations: List[Dict], 
                                patterns: Dict) -> Dict[str, Any]:
        """Phase 2: Verify fund against registration database"""
        print("\n" + "="*80)
        print("PHASE 2: REGISTRATION DATABASE VERIFICATION")
        print("="*80)
        
        found, matches = self.search_fund_in_csv(document, registrations)
        
        # Extract fund details
        page_de_garde_content = document.get('page_de_garde', {}).get('content', {})
        fund_name = page_de_garde_content.get('fund_name', 'Unknown') if isinstance(page_de_garde_content, dict) else 'Unknown'
        fund_isin = 'Unknown'
        
        # Try to find ISIN in tables
        if 'page_de_fin' in document:
            page_de_fin_content = document['page_de_fin'].get('content', {})
            tables = page_de_fin_content.get('tables', []) if isinstance(page_de_fin_content, dict) else []
            for table in tables:
                for row in table.get('rows', []):
                    if isinstance(row, dict):
                        cols = row.get('columns', [])
                        for i, col in enumerate(cols):
                            if col.get('text', '') == 'ISIN code' and i + 1 < len(cols):
                                fund_isin = cols[i + 1].get('text', '')
        
        print(f"\nFund Name: {fund_name}")
        print(f"Fund ISIN: {fund_isin}")
        print(f"\nDatabase Search Result: {'FOUND' if found else 'NOT FOUND'}")
        print(f"Matches: {len(matches)}")
        
        # Analyze patterns
        isin_prefix = fund_isin[:2] if len(fund_isin) >= 2 else 'Unknown'
        print(f"\nISIN Prefix: {isin_prefix}")
        print(f"Known ISIN prefixes in database: {list(patterns['isin_prefixes'].keys())}")
        print(f"ETF products in database: {'ETF' in patterns['fund_types']}")
        
        return {
            'found': found,
            'matches': matches,
            'fund_name': fund_name,
            'fund_isin': fund_isin,
            'isin_prefix': isin_prefix
        }
    
    def phase3_metadata_context(self, metadata: Dict) -> Dict[str, Any]:
        """Phase 3: Analyze metadata context"""
        print("\n" + "="*80)
        print("PHASE 3: METADATA CONTEXT ANALYSIS")
        print("="*80)
        
        is_new_product = metadata.get('Le document fait-il référence à un nouveau Produit', False)
        is_professional = metadata.get('Le client est-il un professionnel', False)
        is_sicav = metadata.get('Est ce que le produit fait partie de la Sicav d\'Oddo', False)
        management_company = metadata.get('Société de Gestion', 'Unknown')
        
        print(f"\nManagement Company: {management_company}")
        print(f"New Product: {is_new_product}")
        print(f"Professional Client: {is_professional}")
        print(f"Part of SICAV: {is_sicav}")
        
        context = {
            'is_new_product': is_new_product,
            'is_professional': is_professional,
            'is_sicav': is_sicav,
            'management_company': management_company,
            'target_audience': 'Professional' if is_professional else 'Retail',
            'registration_status': 'Pre-registration' if is_new_product else 'Should be registered'
        }
        
        if is_new_product:
            print("\n⚠ CONTEXT: This is a NEW PRODUCT (not yet in registration database)")
            print("   Analysis mode: Pre-registration compliance check")
        else:
            print("\n⚠ CONTEXT: This is an EXISTING PRODUCT")
            print("   Analysis mode: Full registration verification")
        
        return context
    
    def phase4_llm_disclaimer_check(self, document: Dict) -> Dict[str, Any]:
        """Phase 4: Use LLM to verify mandatory disclaimers"""
        print("\n" + "="*80)
        print("PHASE 4: MANDATORY DISCLAIMER VERIFICATION (LLM)")
        print("="*80)
        
        # Extract all text content from document
        text_content = json.dumps(document, ensure_ascii=False)
        
        prompt = f"""Analyze this fund presentation document and verify if it contains the following MANDATORY disclaimers and legal notices:

1. Risk of capital loss warning
2. Past performance disclaimer
3. SFDR classification disclosure (Articles 6, 8, or 9)
4. Risk indicator (SRI/SRRI) explanation
5. Investment recommendations disclaimer
6. KID/Prospectus consultation requirement
7. AMF approval mention
8. Investor rights summary reference
9. Complaints handling policy reference
10. Distribution withdrawal rights (Article 93a/32a)

Document content (JSON):
{text_content[:8000]}

Respond in JSON format:
{{
    "disclaimer_1_risk_capital_loss": {{"present": true/false, "evidence": "quote from document"}},
    "disclaimer_2_past_performance": {{"present": true/false, "evidence": "quote"}},
    "disclaimer_3_sfdr": {{"present": true/false, "evidence": "quote"}},
    "disclaimer_4_risk_indicator": {{"present": true/false, "evidence": "quote"}},
    "disclaimer_5_investment_recommendations": {{"present": true/false, "evidence": "quote"}},
    "disclaimer_6_kid_prospectus": {{"present": true/false, "evidence": "quote"}},
    "disclaimer_7_amf_approval": {{"present": true/false, "evidence": "quote"}},
    "disclaimer_8_investor_rights": {{"present": true/false, "evidence": "quote"}},
    "disclaimer_9_complaints": {{"present": true/false, "evidence": "quote"}},
    "disclaimer_10_distribution_withdrawal": {{"present": true/false, "evidence": "quote"}},
    "summary": "Brief summary of compliance"
}}"""
        
        print("\nCalling LLM for disclaimer analysis...")
        response = self.call_llm_analysis(prompt, temperature=0.2)
        
        try:
            # Try to parse JSON response
            result = json.loads(response)
            
            present_count = sum(1 for k, v in result.items() 
                              if k.startswith('disclaimer_') and v.get('present', False))
            total_count = sum(1 for k in result.keys() if k.startswith('disclaimer_'))
            
            print(f"\n✓ Disclaimers present: {present_count}/{total_count}")
            
            for key, value in result.items():
                if key.startswith('disclaimer_'):
                    status = "✓" if value.get('present', False) else "✗"
                    print(f"  {status} {key.replace('disclaimer_', '').replace('_', ' ').title()}")
            
            return result
        except json.JSONDecodeError:
            print("\n⚠ Could not parse LLM response as JSON")
            print(f"Raw response: {response[:500]}...")
            return {'error': 'Failed to parse LLM response', 'raw_response': response}
    
    def phase5_llm_country_analysis(self, document: Dict, csv_verification: Dict, 
                                   patterns: Dict, metadata_context: Dict) -> Dict[str, Any]:
        """Phase 5: Use LLM to analyze country distribution claims"""
        print("\n" + "="*80)
        print("PHASE 5: COUNTRY DISTRIBUTION ANALYSIS (LLM)")
        print("="*80)
        
        # Extract claimed countries from document
        claimed_countries = []
        if 'page_de_fin' in document:
            content = document['page_de_fin'].get('content', {})
            additional_text = ''
            if isinstance(content, dict):
                additional_text = content.get('additional_text', '')
            elif isinstance(content, list):
                # Content is a list - join all text items
                for item in content:
                    if isinstance(item, dict) and item.get('type') == 'text':
                        additional_text += ' ' + item.get('text', '')
                    elif isinstance(item, str):
                        additional_text += ' ' + item
            
            if 'Countries available for Sales' in additional_text:
                countries_text = additional_text.split('Countries available for Sales')[-1]
                claimed_countries = [c.strip() for c in countries_text.split(',')]
        
        # Get common countries from patterns
        top_countries = sorted(patterns['common_countries'].items(), 
                             key=lambda x: x[1], reverse=True)[:10]
        
        prompt = f"""Analyze the country distribution claims for this fund document:

CONTEXT:
- Fund: {csv_verification['fund_name']}
- ISIN: {csv_verification['fund_isin']}
- Is New Product: {metadata_context['is_new_product']}
- Found in Registration DB: {csv_verification['found']}

CLAIMED COUNTRIES:
{', '.join(claimed_countries)}

REGISTRATION DATABASE PATTERNS:
- Total funds in database: {patterns['total_funds']}
- Most common countries in database: {', '.join([f"{c[0]} ({c[1]} funds)" for c in top_countries])}
- ISIN prefixes in database: {', '.join(patterns['isin_prefixes'].keys())}
- Fund ISIN prefix: {csv_verification['isin_prefix']}

ANALYSIS REQUIRED:
1. Are the claimed countries reasonable for an ODDO BHF fund?
2. Do they match typical distribution patterns?
3. Is the ISIN prefix (country of domicile) appropriate?
4. What is the compliance status?

Respond in JSON format:
{{
    "claimed_countries": ["list"],
    "countries_reasonable": true/false,
    "matches_patterns": true/false,
    "isin_prefix_appropriate": true/false,
    "compliance_status": "COMPLIANT/PENDING/VIOLATION",
    "reasoning": "explanation",
    "recommendations": ["list of recommendations"]
}}"""
        
        print("\nCalling LLM for country analysis...")
        response = self.call_llm_analysis(prompt, temperature=0.3)
        
        try:
            result = json.loads(response)
            
            print(f"\nClaimed Countries: {', '.join(claimed_countries)}")
            print(f"Reasonable: {result.get('countries_reasonable', 'Unknown')}")
            print(f"Matches Patterns: {result.get('matches_patterns', 'Unknown')}")
            print(f"Compliance Status: {result.get('compliance_status', 'Unknown')}")
            print(f"\nReasoning: {result.get('reasoning', 'N/A')}")
            
            return result
        except json.JSONDecodeError:
            print("\n⚠ Could not parse LLM response as JSON")
            print(f"Raw response: {response[:500]}...")
            return {'error': 'Failed to parse LLM response', 'raw_response': response}
    
    def phase6_llm_final_assessment(self, all_results: Dict) -> str:
        """Phase 6: Use LLM to generate final compliance assessment"""
        print("\n" + "="*80)
        print("PHASE 6: FINAL COMPLIANCE ASSESSMENT (LLM)")
        print("="*80)
        
        prompt = f"""Based on all the analysis phases, provide a final compliance assessment:

PHASE 1 - STRUCTURAL ANALYSIS:
- Empty fields: {', '.join(all_results['phase1']['empty_fields'])}

PHASE 2 - CSV VERIFICATION:
- Fund found in database: {all_results['phase2']['found']}
- Fund name: {all_results['phase2']['fund_name']}
- Fund ISIN: {all_results['phase2']['fund_isin']}

PHASE 3 - METADATA CONTEXT:
- New product: {all_results['phase3']['is_new_product']}
- Target audience: {all_results['phase3']['target_audience']}
- Registration status: {all_results['phase3']['registration_status']}

PHASE 4 - DISCLAIMERS:
{json.dumps(all_results.get('phase4', {}), indent=2)}

PHASE 5 - COUNTRY ANALYSIS:
{json.dumps(all_results.get('phase5', {}), indent=2)}

Provide a comprehensive compliance report with:
1. Overall compliance status (COMPLIANT/CONDITIONALLY COMPLIANT/NON-COMPLIANT)
2. Critical issues that MUST be fixed before publication
3. Warnings that SHOULD be addressed
4. Positive findings
5. Final recommendation

Format as a clear, professional compliance report."""
        
        print("\nGenerating final assessment...")
        response = self.call_llm_analysis(prompt, temperature=0.4)
        
        print("\n" + "="*80)
        print("FINAL COMPLIANCE REPORT")
        print("="*80)
        print(response)
        
        return response
    
    def analyze(self, document_path: str, csv_path: str, metadata_path: str) -> Dict[str, Any]:
        """Main analysis workflow - replicates the exact LLM approach"""
        print("\n" + "="*80)
        print("COMPLIANCE ANALYZER - LLM-BASED SEMANTIC ANALYSIS")
        print("="*80)
        print(f"\nDocument: {document_path}")
        print(f"Registration DB: {csv_path}")
        print(f"Metadata: {metadata_path}")
        
        # Load all data
        document = self.load_document(document_path)
        metadata = self.load_metadata(metadata_path)
        registrations = self.load_registration_csv(csv_path)
        
        # Analyze CSV patterns
        patterns = self.analyze_csv_patterns(registrations)
        
        # Execute analysis phases
        results = {}
        
        # Phase 1: Structural Analysis
        results['phase1'] = self.phase1_structural_analysis(document)
        
        # Phase 2: CSV Verification
        results['phase2'] = self.phase2_csv_verification(document, registrations, patterns)
        
        # Phase 3: Metadata Context
        results['phase3'] = self.phase3_metadata_context(metadata)
        
        # Phase 4: LLM Disclaimer Check
        results['phase4'] = self.phase4_llm_disclaimer_check(document)
        
        # Phase 5: LLM Country Analysis
        results['phase5'] = self.phase5_llm_country_analysis(
            document, results['phase2'], patterns, results['phase3']
        )
        
        # Phase 6: LLM Final Assessment
        results['final_report'] = self.phase6_llm_final_assessment(results)
        
        return results


def main():
    """Main entry point"""
    if len(sys.argv) != 4:
        print("Usage: python compliance_analyzer.py <document.json> <registration.csv> <metadata.json>")
        print("\nExample:")
        print("  python compliance_analyzer.py exemple.json registration.csv metadata.json")
        sys.exit(1)
    
    document_path = sys.argv[1]
    csv_path = sys.argv[2]
    metadata_path = sys.argv[3]
    
    # Check if files exist
    for path in [document_path, csv_path, metadata_path]:
        if not Path(path).exists():
            print(f"Error: File not found: {path}")
            sys.exit(1)
    
    # Check available LLM providers
    available_providers = llm_manager.get_available_providers()
    if not available_providers:
        print("\n❌ Error: No LLM API keys found in .env file")
        print("Please create a .env file with at least one of:")
        print("  TOKENFACTORY_API_KEY=your-api-key")
        print("  GEMINI_API_KEY=your-gemini-api-key")
        sys.exit(1)
    
    print(f"📡 Available LLM providers: {', '.join(available_providers)}")
    
    # Run analysis
    analyzer = ComplianceAnalyzer()
    results = analyzer.analyze(document_path, csv_path, metadata_path)
    
    # Save results to text file
    output_file = 'registration_validation_report.txt'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("="*80 + "\n")
        f.write("REGISTRATION COMPLIANCE ANALYSIS REPORT\n")
        f.write("="*80 + "\n\n")
        f.write(f"Document: {document_path}\n")
        f.write(f"Registration DB: {csv_path}\n")
        f.write(f"Metadata: {metadata_path}\n\n")
        f.write("="*80 + "\n\n")
        f.write(results.get('final_report', 'No final report generated'))
        f.write("\n\n" + "="*80 + "\n")
        f.write("DETAILED PHASE RESULTS\n")
        f.write("="*80 + "\n\n")
        f.write(json.dumps(results, indent=2, ensure_ascii=False))
    
    print(f"\n\n{'='*80}")
    print(f"Report saved to: {output_file}")
    
    # Generate violation annotations JSON for highlighting
    document = analyzer.load_document(document_path)
    annotations = generate_registration_violation_annotations(results, document)
    annotations_file = "registration_violation_annotations.json"
    with open(annotations_file, 'w', encoding='utf-8') as f:
        json.dump(annotations, f, indent=2, ensure_ascii=False)
    
    print(f"💾 Violation annotations saved to: {annotations_file}")
    print(f"{'='*80}\n")


def generate_registration_violation_annotations(results, document):
    """
    Generate a JSON file with violation annotations for highlighting in the document.
    """
    annotations = {
        "document_annotations": [],
        "summary": {
            "total_violations": 0,
            "critical_violations": 0,
            "major_violations": 0,
            "minor_violations": 0
        },
        "instructions": "Use this file to highlight violations in the document. Each annotation contains the exact location, phrase, and violation details for commenting."
    }
    
    # Phase 1: Empty fields violations
    phase1 = results.get('phase1', {})
    for field in phase1.get('empty_fields', []):
        location = field.split('.')[0] if '.' in field else 'metadata'
        slide_number = get_slide_number_from_location_reg(location, document)
        
        annotation = {
            "rule_id": "REG_FIELD_MISSING",
            "severity": "major",
            "location": location,
            "page_number": slide_number,
            "exact_phrase": f"Field '{field}' is empty",
            "character_count": 0,
            "violation_comment": f"[REG_FIELD_MISSING] Required field '{field}' is missing or empty",
            "required_action": f"Populate the '{field}' field with appropriate data"
        }
        
        annotations["document_annotations"].append(annotation)
        annotations["summary"]["total_violations"] += 1
        annotations["summary"]["major_violations"] += 1
    
    # Phase 2: Registration database violations
    phase2 = results.get('phase2', {})
    if not phase2.get('found', False) and not results.get('phase3', {}).get('is_new_product', False):
        annotation = {
            "rule_id": "REG_NOT_FOUND",
            "severity": "critical",
            "location": "document_metadata",
            "page_number": None,
            "exact_phrase": f"Fund ISIN: {phase2.get('fund_isin', 'Unknown')}",
            "character_count": len(phase2.get('fund_isin', '')),
            "violation_comment": f"[REG_NOT_FOUND] Fund not found in registration database - ISIN: {phase2.get('fund_isin', 'Unknown')}",
            "required_action": "Verify fund is properly registered or update ISIN code"
        }
        
        annotations["document_annotations"].append(annotation)
        annotations["summary"]["total_violations"] += 1
        annotations["summary"]["critical_violations"] += 1
    
    # Phase 4: Missing disclaimers
    phase4 = results.get('phase4', {})
    if not phase4.get('error'):
        for key, value in phase4.items():
            if key.startswith('disclaimer_') and isinstance(value, dict):
                if not value.get('present', False):
                    disclaimer_name = key.replace('disclaimer_', '').replace('_', ' ').title()
                    
                    annotation = {
                        "rule_id": f"REG_{key.upper()}",
                        "severity": "major",
                        "location": "document-wide",
                        "page_number": None,
                        "exact_phrase": f"Missing: {disclaimer_name}",
                        "character_count": 0,
                        "violation_comment": f"[{key.upper()}] Mandatory disclaimer missing: {disclaimer_name}",
                        "required_action": f"Add the required {disclaimer_name} disclaimer to the document"
                    }
                    
                    annotations["document_annotations"].append(annotation)
                    annotations["summary"]["total_violations"] += 1
                    annotations["summary"]["major_violations"] += 1
    
    # Phase 5: Country distribution issues
    phase5 = results.get('phase5', {})
    if phase5.get('compliance_status') == 'VIOLATION':
        annotation = {
            "rule_id": "REG_COUNTRY_VIOLATION",
            "severity": "critical",
            "location": "page_de_fin",
            "page_number": get_slide_number_from_location_reg('page_de_fin', document),
            "exact_phrase": f"Countries: {', '.join(phase5.get('claimed_countries', []))}",
            "character_count": len(', '.join(phase5.get('claimed_countries', []))),
            "violation_comment": f"[REG_COUNTRY_VIOLATION] {phase5.get('reasoning', 'Country distribution claims do not match registration')}",
            "required_action": "Verify and correct country distribution claims"
        }
        
        annotations["document_annotations"].append(annotation)
        annotations["summary"]["total_violations"] += 1
        annotations["summary"]["critical_violations"] += 1
    
    return annotations


def get_slide_number_from_location_reg(location_string, document):
    """Get the actual slide number from the document structure based on location string."""
    location_map = {
        'page_de_garde': 'page_de_garde',
        'cover': 'page_de_garde',
        'slide_2': 'slide_2',
        'page_de_fin': 'page_de_fin',
        'fund_characteristics': 'page_de_fin',
        'back page': 'page_de_fin'
    }
    
    location_lower = location_string.lower().strip()
    
    # For metadata violations, metadata is typically shown on cover page or last page
    if 'metadata' in location_lower:
        # ISIN, language, country are typically on the last page in fund characteristics
        return document.get('page_de_fin', {}).get('slide_number', document.get('document_metadata', {}).get('page_count', 6))
    
    # For document-wide violations (like disclaimers), they're usually on the last page
    if 'document-wide' in location_lower or 'disclaimer' in location_lower:
        if 'page_de_fin' in document:
            return document['page_de_fin'].get('slide_number', document.get('document_metadata', {}).get('page_count'))
        return document.get('document_metadata', {}).get('page_count', 6)
    
    # Try direct mapping first
    for key, section_name in location_map.items():
        if key in location_lower:
            if section_name in document:
                slide_num = document[section_name].get('slide_number')
                if slide_num:
                    return slide_num
    
    # Check in pages_suivantes array
    if 'pages_suivantes' in document:
        for page in document['pages_suivantes']:
            slide_num = page.get('slide_number')
            if f'slide_{slide_num}' in location_lower or f'slide {slide_num}' in location_lower:
                return slide_num
    
    # Try to extract slide number from pattern
    match = re.search(r'(?:slide|page)[_\s]?(\d+)', location_lower)
    if match:
        return int(match.group(1))
    
    # Default to last page for unknown violations (most metadata/disclaimers are there)
    return document.get('document_metadata', {}).get('page_count', 6)


if __name__ == '__main__':
    main()
