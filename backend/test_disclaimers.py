"""
Disclaimer Compliance Verification Tool
Implements the exact same logic used for manual compliance analysis
Uses LLM with automatic fallback (TokenFactory -> Gemini)
"""

import json
import csv
import sys
import os
from typing import Dict, List, Tuple, Any
from dotenv import load_dotenv
import re

# Import path utilities
from path_utils import ENV_FILE, ensure_directories

# Import LLM Manager with fallback support
from llm_manager import llm_manager

# Load environment variables from .env file
load_dotenv(str(ENV_FILE))


class DisclaimerComplianceChecker:
    """
    Compliance checker that follows the exact approach:
    1. Profile the document (metadata analysis)
    2. Identify applicable disclaimer template
    3. Extract actual disclaimers from document
    4. Text matching & gap analysis
    5. Contextual rule application
    6. Cross-reference additional rules
    7. Consistency check
    """
    
    def __init__(self, api_key: str = None):
        """Initialize the compliance checker - uses llm_manager with automatic fallback"""
        self.llm = llm_manager
        
        self.document = None
        self.disclaimers_db = None
        self.metadata = None
        self.violations = []
        self.compliant_items = []
        
    def load_files(self, document_path: str, disclaimers_path: str, metadata_path: str):
        """Load all required files"""
        print("📂 Loading files...")
        
        # Load document
        with open(document_path, 'r', encoding='utf-8') as f:
            self.document = json.load(f)
        print(f"  ✓ Loaded document: {document_path}")
        
        # Load disclaimers CSV
        with open(disclaimers_path, 'r', encoding='utf-8-sig') as f:  # utf-8-sig handles BOM
            reader = csv.DictReader(f)
            self.disclaimers_db = list(reader)
        
        # Debug: print column names
        if self.disclaimers_db:
            print(f"  ✓ Loaded disclaimers: {disclaimers_path}")
            print(f"  ✓ CSV columns: {list(self.disclaimers_db[0].keys())}")
        else:
            print(f"  ⚠ Warning: No data in disclaimers CSV")
        print()
        
        # Load metadata
        with open(metadata_path, 'r', encoding='utf-8') as f:
            self.metadata = json.load(f)
        print(f"  ✓ Loaded metadata: {metadata_path}")
        print()
    
    def step1_profile_document(self) -> Dict[str, Any]:
        """
        STEP 1: Profile the Document (Metadata Analysis)
        Extract key characteristics to determine which disclaimers apply
        """
        print("🔍 STEP 1: Profiling Document...")
        
        profile = {
            'management_company': self.metadata.get('Société de Gestion', ''),
            'is_sicav': self.metadata.get('Est ce que le produit fait partie de la Sicav d\'Oddo', False),
            'is_professional_client': self.metadata.get('Le client est-il un professionnel', False),
            'is_new_strategy': self.metadata.get('Le document fait-il référence à une nouvelle Stratégie', False),
            'is_new_product': self.metadata.get('Le document fait-il référence à un nouveau Produit', False),
            'client_type': 'professional' if self.metadata.get('Le client est-il un professionnel', False) else 'retail'
        }
        
        print(f"  Management Company: {profile['management_company']}")
        print(f"  Client Type: {profile['client_type']}")
        print(f"  Is SICAV: {profile['is_sicav']}")
        print(f"  New Product: {profile['is_new_product']}")
        print(f"  New Strategy: {profile['is_new_strategy']}")
        print()
        
        return profile
    
    def step2_identify_applicable_template(self, profile: Dict[str, Any]) -> Tuple[str, str]:
        """
        STEP 2: Identify the Applicable Disclaimer Template
        Based on profile, determine which row and column from CSV to use
        """
        print("📋 STEP 2: Identifying Applicable Disclaimer Template...")
        
        # Determine management company suffix
        mgmt_company = profile['management_company']
        if 'SAS' in mgmt_company:
            company_suffix = 'OBAM SAS'
        elif 'GmbH' in mgmt_company:
            company_suffix = 'OBAM GmbH'
        elif 'Lux' in mgmt_company:
            company_suffix = 'OBAM Lux'
        else:
            company_suffix = 'OBAM SAS'  # Default
        
        # Determine document type
        if profile['is_new_product'] and profile['is_new_strategy']:
            doc_type = f"New offer products (strategy mentioning funds track record)"
        elif profile['is_new_strategy']:
            doc_type = f"Commercial documentation (strategies) : management Company = {company_suffix}"
        else:
            doc_type = f"Commercial documentation : management company = {company_suffix}"
        
        # Determine column (retail vs professional)
        column = 'Professional_Disclaimer' if profile['is_professional_client'] else 'Retail_Disclaimer'
        
        print(f"  Document Type: {doc_type}")
        print(f"  Disclaimer Column: {column}")
        print()
        
        return doc_type, column
    
    def step3_extract_document_disclaimers(self) -> Dict[str, List[str]]:
        """
        STEP 3: Extract Actual Disclaimers from Document
        Scan the document for all disclaimer text
        """
        print("📄 STEP 3: Extracting Disclaimers from Document...")
        
        extracted = {
            'main_legal': '',
            'slide_disclaimers': [],
            'additional_disclaimers': [],
            'all_text': []
        }
        
        # Extract main legal mention from last page
        if 'page_de_fin' in self.document:
            content = self.document['page_de_fin'].get('content', {})
            # Handle both dict and list content structures
            if isinstance(content, dict):
                legal_text = content.get('legal_mention_sgp', {}).get('text', '')
                if legal_text:
                    extracted['main_legal'] = legal_text
                    extracted['all_text'].append(legal_text)
            elif isinstance(content, list):
                # Content is a list of text items from PPTX extraction
                for item in content:
                    if isinstance(item, dict) and item.get('type') == 'text':
                        text = item.get('text', '')
                        if text:
                            extracted['all_text'].append(text)
                    elif isinstance(item, str):
                        extracted['all_text'].append(item)
        
        # Extract disclaimers from all slides
        if 'pages_suivantes' in self.document:
            for slide in self.document['pages_suivantes']:
                slide_content = slide.get('content', {})
                # Handle both dict and list content structures
                if isinstance(slide_content, dict):
                    disclaimers = slide_content.get('disclaimers', [])
                    for disc in disclaimers:
                        text = disc.get('text', '')
                        if text:
                            extracted['slide_disclaimers'].append(text)
                            extracted['all_text'].append(text)
                elif isinstance(slide_content, list):
                    # Content is a list of text items from PPTX extraction
                    for item in slide_content:
                        if isinstance(item, dict) and item.get('type') == 'text':
                            text = item.get('text', '')
                            if text:
                                extracted['all_text'].append(text)
                        elif isinstance(item, str):
                            extracted['all_text'].append(item)
        
        # Extract from page_de_garde
        if 'page_de_garde' in self.document:
            content = self.document['page_de_garde'].get('content', {})
            if isinstance(content, dict):
                for key, value in content.items():
                    if isinstance(value, str) and len(value) > 50:
                        extracted['all_text'].append(value)
            elif isinstance(content, list):
                for item in content:
                    if isinstance(item, dict) and item.get('type') == 'text':
                        text = item.get('text', '')
                        if text and len(text) > 50:
                            extracted['all_text'].append(text)
                    elif isinstance(item, str) and len(item) > 50:
                        extracted['all_text'].append(item)
        
        # Extract additional disclaimers from last page
        if 'page_de_fin' in self.document:
            fin_content = self.document['page_de_fin'].get('content', {})
            if isinstance(fin_content, dict):
                add_disclaimers = fin_content.get('additional_disclaimers', [])
                extracted['additional_disclaimers'] = add_disclaimers
                extracted['all_text'].extend(add_disclaimers)
        
        print(f"  ✓ Found main legal text: {len(extracted['main_legal'])} chars")
        print(f"  ✓ Found {len(extracted['slide_disclaimers'])} slide disclaimers")
        print(f"  ✓ Found {len(extracted['additional_disclaimers'])} additional disclaimers")
        print()
        
        return extracted

    def step4_text_matching_gap_analysis(self, required_disclaimer: str, extracted: Dict[str, List[str]]) -> Dict[str, Any]:
        """
        STEP 4: Text Matching & Gap Analysis
        Use LLM to perform semantic comparison between required and actual disclaimers
        """
        print("🔎 STEP 4: Performing Text Matching & Gap Analysis...")
        
        # Combine all extracted text
        all_document_text = "\n\n".join(extracted['all_text'])
        
        # Create prompt for LLM analysis
        prompt = f"""You are a compliance analyst. Compare the REQUIRED disclaimer with the ACTUAL document text.

REQUIRED DISCLAIMER:
{required_disclaimer}

ACTUAL DOCUMENT TEXT:
{all_document_text}

Analyze if the required disclaimer is present in the document. Consider:
1. Semantic similarity (not exact word matching)
2. All key phrases must be present
3. The meaning must be preserved

Respond in JSON format:
{{
    "is_present": true/false,
    "coverage_percentage": 0-100,
    "missing_elements": ["list of missing key phrases"],
    "explanation": "brief explanation"
}}
"""
        
        result_text = self.llm.call_llm(
            system_prompt="You are a compliance analyst expert. Always respond with valid JSON.",
            user_prompt=prompt,
            temperature=0.3,
            max_tokens=1000
        )
        
        if not result_text:
            return {
                "is_present": False,
                "coverage_percentage": 0,
                "missing_elements": ["LLM call failed"],
                "explanation": f"Error: {self.llm.last_error}"
            }
        
        # Parse JSON response
        try:
            # Extract JSON from response (in case there's extra text)
            start_idx = result_text.find('{')
            end_idx = result_text.rfind('}') + 1
            json_str = result_text[start_idx:end_idx]
            result = json.loads(json_str)
        except:
            result = {
                "is_present": False,
                "coverage_percentage": 0,
                "missing_elements": ["Failed to parse LLM response"],
                "explanation": "Error in analysis"
            }
        
        print(f"  Coverage: {result.get('coverage_percentage', 0)}%")
        print(f"  Present: {result.get('is_present', False)}")
        print()
        
        return result
    
    def step5_contextual_rule_application(self, extracted: Dict[str, List[str]]) -> List[Dict[str, Any]]:
        """
        STEP 5: Contextual Rule Application
        Apply conditional disclaimers based on document content
        """
        print("⚙️ STEP 5: Applying Contextual Rules...")
        
        contextual_checks = []
        all_text = " ".join(extracted['all_text']).lower()
        
        # Check for SFDR mention
        if 'sfdr' in all_text or 'article 6' in all_text or 'article 8' in all_text or 'article 9' in all_text:
            sfdr_disclaimer = self._find_disclaimer_by_type('SFDR ART.6')
            if sfdr_disclaimer:
                contextual_checks.append({
                    'trigger': 'SFDR mentioned',
                    'required_disclaimer': sfdr_disclaimer,
                    'type': 'SFDR ART.6'
                })
        
        # Check for SRI/Risk indicator
        if 'sri' in all_text or 'summary risk indicator' in all_text or 'risk indicator' in all_text:
            sri_disclaimer = self._find_disclaimer_by_type('SRI in marketing Document')
            if sri_disclaimer:
                contextual_checks.append({
                    'trigger': 'SRI/Risk indicator shown',
                    'required_disclaimer': sri_disclaimer,
                    'type': 'SRI in marketing Document'
                })
        
        # Check for performance data
        if 'past performance' in all_text or 'performance' in all_text:
            perf_disclaimer = self._find_disclaimer_by_type('Performance')
            if perf_disclaimer:
                contextual_checks.append({
                    'trigger': 'Performance data present',
                    'required_disclaimer': perf_disclaimer,
                    'type': 'Performance'
                })
        
        # Check for company names/issuers mentioned
        if any(company in all_text for company in ['apple', 'microsoft', 'amazon', 'google', 'meta', 'tesla', 'nvidia']):
            issuer_disclaimer = self._find_disclaimer_by_type('Issuers mentioned')
            if issuer_disclaimer:
                contextual_checks.append({
                    'trigger': 'Company names mentioned',
                    'required_disclaimer': issuer_disclaimer,
                    'type': 'Issuers mentioned'
                })
        
        # Check for Switzerland distribution
        if 'switzerland' in all_text or 'swiss' in all_text:
            swiss_disclaimer = self._find_disclaimer_by_type('Additional Information for French domiciled mutual fund, that are registrered and distributed in Switzerland.')
            if swiss_disclaimer:
                contextual_checks.append({
                    'trigger': 'Switzerland in distribution countries',
                    'required_disclaimer': swiss_disclaimer,
                    'type': 'Switzerland-specific'
                })
        
        print(f"  ✓ Found {len(contextual_checks)} contextual rules to check")
        print()
        
        return contextual_checks
    
    def _find_disclaimer_by_type(self, doc_type: str) -> str:
        """Helper to find disclaimer text by document type"""
        for row in self.disclaimers_db:
            # Get the document type, handling potential key variations
            row_doc_type = row.get('Document_Type', row.get('Document Type', ''))
            
            if row_doc_type == doc_type:
                # Return retail or professional based on metadata
                if self.metadata.get('Le client est-il un professionnel', False):
                    return row.get('Professional_Disclaimer', row.get('Professional Disclaimer', ''))
                else:
                    return row.get('Retail_Disclaimer', row.get('Retail Disclaimer', ''))
        return ''
    
    def step6_cross_reference_additional_rules(self) -> List[Dict[str, Any]]:
        """
        STEP 6: Cross-Reference Additional Rules
        Check for special cases and additional requirements
        """
        print("🔗 STEP 6: Cross-Referencing Additional Rules...")
        
        additional_checks = []
        all_text = " ".join(self.step3_extract_document_disclaimers()['all_text']).lower()
        
        # Check for Germany-specific rules
        if 'germany' in all_text or 'deutschland' in all_text:
            german_disclaimer = self._find_disclaimer_by_type('Additional information for very specific marketing information produced for the German market')
            if german_disclaimer:
                additional_checks.append({
                    'rule': 'Germany-specific disclaimer',
                    'required': german_disclaimer
                })
        
        # Check for RAIF
        if 'raif' in all_text:
            raif_disclaimer = self._find_disclaimer_by_type('Commercial documentation (luxembourg funds-RAIF)')
            if raif_disclaimer:
                additional_checks.append({
                    'rule': 'RAIF-specific disclaimer',
                    'required': raif_disclaimer
                })
        
        # Check for Money Market Fund
        if 'money market' in all_text:
            mmf_disclaimer = self._find_disclaimer_by_type('Regulatory weekly factsheet for Money Market Fund')
            if mmf_disclaimer:
                additional_checks.append({
                    'rule': 'Money Market Fund disclaimer',
                    'required': mmf_disclaimer
                })
        
        # Check for YtM/YtW
        if 'ytm' in all_text or 'ytw' in all_text or 'yield to maturity' in all_text:
            ytm_disclaimer = self._find_disclaimer_by_type('YtM/YtW usage')
            if ytm_disclaimer:
                additional_checks.append({
                    'rule': 'YtM/YtW disclaimer',
                    'required': ytm_disclaimer
                })
        
        print(f"  ✓ Found {len(additional_checks)} additional rules to check")
        print()
        
        return additional_checks

    def step7_consistency_check(self) -> List[Dict[str, Any]]:
        """
        STEP 7: Consistency Check
        Verify metadata completeness and document consistency
        """
        print("✅ STEP 7: Performing Consistency Checks...")
        
        consistency_issues = []
        
        # Check metadata completeness
        doc_metadata = self.document.get('document_metadata', {})
        
        required_metadata_fields = ['client_type', 'language', 'country', 'fund_isin']
        for field in required_metadata_fields:
            value = doc_metadata.get(field, '')
            if not value or value == '':
                consistency_issues.append({
                    'type': 'incomplete_metadata',
                    'field': field,
                    'issue': f'Metadata field "{field}" is empty'
                })
        
        # Check for Belgium inconsistency
        extracted = self.step3_extract_document_disclaimers()
        all_text = " ".join(extracted['all_text']).lower()
        
        if 'belgium' in all_text:
            # Check if Belgium is in distribution countries
            if 'page_de_fin' in self.document:
                content = self.document['page_de_fin'].get('content', {})
                # Handle both dict and list content structures
                additional_text = ''
                if isinstance(content, dict):
                    additional_text = content.get('additional_text', '').lower()
                elif isinstance(content, list):
                    # Content is a list - join all text items
                    for item in content:
                        if isinstance(item, dict) and item.get('type') == 'text':
                            additional_text += ' ' + item.get('text', '').lower()
                        elif isinstance(item, str):
                            additional_text += ' ' + item.lower()
                
                if 'belgium' not in additional_text and 'belgique' not in additional_text:
                    consistency_issues.append({
                        'type': 'inconsistency',
                        'field': 'belgium_distribution',
                        'issue': 'Disclaimer mentions Belgium but Belgium not listed in distribution countries'
                    })
        
        # Check client type consistency
        metadata_professional = self.metadata.get('Le client est-il un professionnel', False)
        doc_client_type = doc_metadata.get('client_type', '').lower()
        
        if metadata_professional and 'professional' not in doc_client_type and doc_client_type != '':
            consistency_issues.append({
                'type': 'inconsistency',
                'field': 'client_type',
                'issue': 'Metadata indicates professional client but document metadata does not reflect this'
            })
        
        print(f"  ✓ Found {len(consistency_issues)} consistency issues")
        print()
        
        return consistency_issues
    
    def run_full_analysis(self) -> Dict[str, Any]:
        """
        Run the complete 7-step compliance analysis
        """
        print("=" * 80)
        print("🚀 STARTING DISCLAIMER COMPLIANCE VERIFICATION")
        print("=" * 80)
        print()
        
        # Step 1: Profile Document
        profile = self.step1_profile_document()
        
        # Step 2: Identify Template
        doc_type, column = self.step2_identify_applicable_template(profile)
        
        # Find the required disclaimer
        required_disclaimer = ''
        for row in self.disclaimers_db:
            # Get the document type, handling potential key variations
            row_doc_type = row.get('Document_Type', row.get('Document Type', ''))
            
            if row_doc_type == doc_type:
                required_disclaimer = row.get(column, '')
                break
        
        if not required_disclaimer:
            print(f"⚠️  WARNING: Could not find required disclaimer for type '{doc_type}'")
            print()
        
        # Step 3: Extract Document Disclaimers
        extracted = self.step3_extract_document_disclaimers()
        
        # Step 4: Text Matching & Gap Analysis
        if required_disclaimer:
            main_analysis = self.step4_text_matching_gap_analysis(required_disclaimer, extracted)
        else:
            main_analysis = {
                "is_present": False,
                "coverage_percentage": 0,
                "missing_elements": ["Required disclaimer template not found"],
                "explanation": "Could not determine required disclaimer"
            }
        
        # Step 5: Contextual Rules
        contextual_checks = self.step5_contextual_rule_application(extracted)
        contextual_results = []
        
        for check in contextual_checks:
            result = self.step4_text_matching_gap_analysis(check['required_disclaimer'], extracted)
            contextual_results.append({
                'trigger': check['trigger'],
                'type': check['type'],
                'result': result
            })
        
        # Step 6: Additional Rules
        additional_checks = self.step6_cross_reference_additional_rules()
        additional_results = []
        
        for check in additional_checks:
            result = self.step4_text_matching_gap_analysis(check['required'], extracted)
            additional_results.append({
                'rule': check['rule'],
                'result': result
            })
        
        # Step 7: Consistency Check
        consistency_issues = self.step7_consistency_check()
        
        # Compile final report
        report = {
            'profile': profile,
            'required_disclaimer_type': doc_type,
            'main_disclaimer_analysis': main_analysis,
            'contextual_checks': contextual_results,
            'additional_checks': additional_results,
            'consistency_issues': consistency_issues,
            'overall_compliant': self._determine_overall_compliance(
                main_analysis, contextual_results, additional_results, consistency_issues
            )
        }
        
        return report
    
    def _determine_overall_compliance(self, main_analysis, contextual_results, additional_results, consistency_issues):
        """Determine if document is overall compliant"""
        # Main disclaimer must be present
        if not main_analysis.get('is_present', False):
            return False
        
        # Check contextual rules
        for result in contextual_results:
            if not result['result'].get('is_present', False):
                return False
        
        # Additional checks are warnings, not failures
        # Consistency issues are warnings, not failures
        
        return True
    
    def generate_report(self, report: Dict[str, Any]) -> str:
        """
        Generate a human-readable compliance report
        """
        print("=" * 80)
        print("📊 COMPLIANCE VERIFICATION REPORT")
        print("=" * 80)
        print()
        
        output = []
        output.append("=" * 80)
        output.append("COMPLIANCE VERIFICATION REPORT")
        output.append("=" * 80)
        output.append("")
        
        # Document Profile
        output.append("📋 DOCUMENT PROFILE")
        output.append("-" * 80)
        profile = report['profile']
        output.append(f"Management Company: {profile['management_company']}")
        output.append(f"Client Type: {profile['client_type']}")
        output.append(f"Is SICAV: {profile['is_sicav']}")
        output.append(f"New Product: {profile['is_new_product']}")
        output.append(f"New Strategy: {profile['is_new_strategy']}")
        output.append("")
        
        # Main Disclaimer Analysis
        output.append("✅ MAIN DISCLAIMER COMPLIANCE")
        output.append("-" * 80)
        output.append(f"Required Disclaimer Type: {report['required_disclaimer_type']}")
        main = report['main_disclaimer_analysis']
        output.append(f"Present: {'✓ YES' if main.get('is_present') else '✗ NO'}")
        output.append(f"Coverage: {main.get('coverage_percentage', 0)}%")
        
        if main.get('missing_elements'):
            output.append("\nMissing Elements:")
            for elem in main['missing_elements']:
                output.append(f"  • {elem}")
        
        output.append(f"\nExplanation: {main.get('explanation', 'N/A')}")
        output.append("")
        
        # Contextual Checks
        output.append("⚙️ CONTEXTUAL DISCLAIMER CHECKS")
        output.append("-" * 80)
        if report['contextual_checks']:
            for check in report['contextual_checks']:
                output.append(f"\nTrigger: {check['trigger']}")
                output.append(f"Type: {check['type']}")
                result = check['result']
                output.append(f"Present: {'✓ YES' if result.get('is_present') else '✗ NO'}")
                output.append(f"Coverage: {result.get('coverage_percentage', 0)}%")
                if not result.get('is_present'):
                    output.append(f"Missing: {', '.join(result.get('missing_elements', []))}")
        else:
            output.append("No contextual checks required")
        output.append("")
        
        # Additional Checks
        output.append("🔗 ADDITIONAL RULE CHECKS")
        output.append("-" * 80)
        if report['additional_checks']:
            for check in report['additional_checks']:
                output.append(f"\nRule: {check['rule']}")
                result = check['result']
                output.append(f"Present: {'✓ YES' if result.get('is_present') else '✗ NO'}")
                output.append(f"Coverage: {result.get('coverage_percentage', 0)}%")
        else:
            output.append("No additional checks required")
        output.append("")
        
        # Consistency Issues
        output.append("⚠️ CONSISTENCY ISSUES")
        output.append("-" * 80)
        if report['consistency_issues']:
            for issue in report['consistency_issues']:
                output.append(f"\n• Type: {issue['type']}")
                output.append(f"  Field: {issue['field']}")
                output.append(f"  Issue: {issue['issue']}")
        else:
            output.append("No consistency issues found")
        output.append("")
        
        # Overall Compliance
        output.append("=" * 80)
        overall = report['overall_compliant']
        if overall:
            output.append("✅ OVERALL COMPLIANCE: PASSED")
        else:
            output.append("❌ OVERALL COMPLIANCE: FAILED")
        output.append("=" * 80)
        
        report_text = "\n".join(output)
        print(report_text)
        
        return report_text


def main():
    """Main entry point for the compliance checker"""
    if len(sys.argv) != 4:
        print("Usage: python test_disclaimers.py <document.json> <disclaimers.csv> <metadata.json>")
        print("Example: python test_disclaimers.py exemple.json disclaimers.csv metadata.json")
        sys.exit(1)
    
    document_path = sys.argv[1]
    disclaimers_path = sys.argv[2]
    metadata_path = sys.argv[3]
    
    # Check available LLM providers
    available_providers = llm_manager.get_available_providers()
    if not available_providers:
        print("❌ ERROR: No LLM API keys found in .env file")
        print("Please create a .env file with at least one of:")
        print("  TOKENFACTORY_API_KEY=your-api-key")
        print("  GEMINI_API_KEY=your-gemini-api-key")
        sys.exit(1)
    
    print(f"📡 Available LLM providers: {', '.join(available_providers)}")
    
    # Initialize checker
    checker = DisclaimerComplianceChecker()
    
    # Load files
    try:
        checker.load_files(document_path, disclaimers_path, metadata_path)
    except Exception as e:
        print(f"❌ ERROR loading files: {e}")
        sys.exit(1)
    
    # Run analysis
    try:
        report = checker.run_full_analysis()
    except Exception as e:
        print(f"❌ ERROR during analysis: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    # Generate report
    report_text = checker.generate_report(report)
    
    # Save report to file
    output_file = 'disclaimers_validation_report.txt'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(report_text)
    
    print(f"\n📄 Report saved to: {output_file}")
    
    # Generate violation annotations JSON for highlighting
    annotations = generate_disclaimers_violation_annotations(report, checker.document)
    annotations_file = "disclaimers_violation_annotations.json"
    with open(annotations_file, 'w', encoding='utf-8') as f:
        json.dump(annotations, f, indent=2, ensure_ascii=False)
    
    print(f"💾 Violation annotations saved to: {annotations_file}")
    
    # Exit with appropriate code
    sys.exit(0 if report['overall_compliant'] else 1)


def generate_disclaimers_violation_annotations(report, document):
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
    
    # Main disclaimer violations
    main_analysis = report.get('main_disclaimer_analysis', {})
    if not main_analysis.get('is_present', False):
        # Main disclaimer is missing - critical violation
        missing_elements = main_analysis.get('missing_elements', [])
        
        annotation = {
            "rule_id": "DISC_MAIN_MISSING",
            "severity": "critical",
            "location": "page_de_fin",
            "page_number": get_slide_number_from_location_disc('page_de_fin', document),
            "exact_phrase": f"Missing main disclaimer: {report.get('required_disclaimer_type', 'Unknown')}",
            "character_count": 0,
            "violation_comment": f"[DISC_MAIN_MISSING] Required main disclaimer is missing or incomplete. Coverage: {main_analysis.get('coverage_percentage', 0)}%. Missing: {', '.join(missing_elements[:3])}",
            "required_action": f"Add the complete required disclaimer for: {report.get('required_disclaimer_type', 'Unknown')}"
        }
        
        annotations["document_annotations"].append(annotation)
        annotations["summary"]["total_violations"] += 1
        annotations["summary"]["critical_violations"] += 1
    
    # Contextual disclaimer violations
    for check in report.get('contextual_checks', []):
        result = check.get('result', {})
        if not result.get('is_present', False):
            # Determine location based on trigger type
            location = 'page_de_garde' if 'SFDR' in check['type'] or 'SRI' in check['type'] else 'document-wide'
            
            annotation = {
                "rule_id": f"DISC_CONTEXT_{check['type'].replace(' ', '_').upper()}",
                "severity": "major",
                "location": location,
                "page_number": get_slide_number_from_location_disc(location, document),
                "exact_phrase": f"Missing contextual disclaimer: {check['type']}",
                "character_count": 0,
                "violation_comment": f"[DISC_CONTEXT] Contextual disclaimer missing for: {check['trigger']}. Coverage: {result.get('coverage_percentage', 0)}%",
                "required_action": f"Add required disclaimer for {check['type']} since document contains: {check['trigger']}"
            }
            
            annotations["document_annotations"].append(annotation)
            annotations["summary"]["total_violations"] += 1
            annotations["summary"]["major_violations"] += 1
    
    # Additional rule violations
    for check in report.get('additional_checks', []):
        result = check.get('result', {})
        if not result.get('is_present', False):
            annotation = {
                "rule_id": f"DISC_ADDITIONAL_{check['rule'].replace(' ', '_').upper()[:20]}",
                "severity": "major",
                "location": "page_de_fin",
                "page_number": get_slide_number_from_location_disc('page_de_fin', document),
                "exact_phrase": f"Missing additional disclaimer: {check['rule']}",
                "character_count": 0,
                "violation_comment": f"[DISC_ADDITIONAL] Additional disclaimer missing: {check['rule']}. Coverage: {result.get('coverage_percentage', 0)}%",
                "required_action": f"Add required disclaimer for: {check['rule']}"
            }
            
            annotations["document_annotations"].append(annotation)
            annotations["summary"]["total_violations"] += 1
            annotations["summary"]["major_violations"] += 1
    
    # Consistency issues
    for issue in report.get('consistency_issues', []):
        severity = 'critical' if issue['type'] == 'incomplete_metadata' else 'minor'
        
        # Determine location based on issue type
        if 'metadata' in issue['type']:
            location = 'metadata'
        elif 'belgium' in issue['field']:
            location = 'page_de_fin'
        else:
            location = 'document-wide'
        
        annotation = {
            "rule_id": f"DISC_CONSISTENCY_{issue['type'].upper()}",
            "severity": severity,
            "location": location,
            "page_number": get_slide_number_from_location_disc(location, document),
            "exact_phrase": f"Consistency issue: {issue['field']}",
            "character_count": 0,
            "violation_comment": f"[DISC_CONSISTENCY] {issue['issue']}",
            "required_action": f"Fix consistency issue in field: {issue['field']}"
        }
        
        annotations["document_annotations"].append(annotation)
        annotations["summary"]["total_violations"] += 1
        if severity == 'critical':
            annotations["summary"]["critical_violations"] += 1
        else:
            annotations["summary"]["minor_violations"] += 1
    
    return annotations


def get_slide_number_from_location_disc(location_string, document):
    """Get the actual slide number from the document structure based on location string."""
    location_map = {
        'page_de_garde': 'page_de_garde',
        'cover': 'page_de_garde',
        'slide_2': 'slide_2',
        'page_de_fin': 'page_de_fin',
        'back page': 'page_de_fin',
        'end': 'page_de_fin'
    }
    
    location_lower = location_string.lower().strip()
    
    # For metadata violations, they're typically shown on the last page
    if 'metadata' in location_lower:
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
    
    # Default to last page for disclaimer violations
    return document.get('document_metadata', {}).get('page_count', 6)


if __name__ == "__main__":
    main()
