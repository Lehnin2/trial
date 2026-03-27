#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple command-line compliance checker
Usage: python check.py <json_file>
"""

import sys
import os
import io
from pathlib import Path

# Import path utilities
from path_utils import ENV_FILE, SRC_DIR

# Fix encoding for ALL output streams
if sys.platform == 'win32':
    # Windows-specific fix
    import locale
    try:
        locale.setlocale(locale.LC_ALL, 'fr_FR.UTF-8')
    except:
        try:
            locale.setlocale(locale.LC_ALL, '')
        except:
            pass
    
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace', line_buffering=True)
else:
    # Unix/Linux
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

# Set environment encoding
os.environ['PYTHONIOENCODING'] = 'utf-8'

from dotenv import load_dotenv

# Load environment
load_dotenv(str(ENV_FILE))

if not ENV_FILE.exists():
    print("ERROR: .env file not found! Run: python setup.py")
    sys.exit(1)

# Load the agent
print("Loading agent...")
agent_file = SRC_DIR / 'agent_local.py'
with open(agent_file, encoding='utf-8') as f:
    exec(f.read())
def check_document_compliance(json_file_path_or_dict):
    """
    Full document compliance checker
    
    Args:
        json_file_path_or_dict: Either a path to JSON document (str) OR a dict with document data
    
    Returns:
        dict with violations list
    """
    try:
        # Handle both file path (str) and dict input
        if isinstance(json_file_path_or_dict, dict):
            # Direct dict input (from API)
            doc = json_file_path_or_dict
            file_display_name = doc.get('document_metadata', {}).get('document_name', 'Document')
        else:
            # File path input (from CLI)
            import json
            with open(json_file_path_or_dict, 'r', encoding='utf-8') as f:
                doc = json.load(f)
            file_display_name = json_file_path_or_dict

        violations = []

        # Extract metadata
        doc_metadata = doc.get('document_metadata', {})
        fund_isin = doc_metadata.get('fund_isin')
        client_type = doc_metadata.get('client_type', 'retail')
        doc_type = doc_metadata.get('document_type', 'fund_presentation')
        fund_status = doc_metadata.get('fund_status', 'active')
        esg_classification = doc_metadata.get('fund_esg_classification', 'other')
        country_code = doc_metadata.get('country_code', None)
        fund_age_years = doc_metadata.get('fund_age_years', None)

        print(f"\n{'='*70}")
        print(f"📄 COMPLIANCE REPORT")
        print(f"{'='*70}")
        print(f"File: {file_display_name}")
        print(f"Fund ISIN: {fund_isin or 'Not specified'}")
        print(f"Client Type: {client_type.upper()}")
        print(f"Document Type: {doc_type}")
        print(f"Fund Status: {fund_status}")
        print(f"ESG Classification: {esg_classification}")
        print(f"{'='*70}\n")
        
        # ====================================================================
        # CHECK 1: DISCLAIMERS
        # ====================================================================
        if 'disclaimers_db' in globals() and disclaimers_db:
            doc_type_mapping = {
                'fund_presentation': 'OBAM Presentation',
                'commercial_doc': 'Commercial documentation',
                'fact_sheet': 'OBAM Presentation'
            }

            disclaimer_type = doc_type_mapping.get(doc_type, 'OBAM Presentation')

            if disclaimer_type in disclaimers_db:
                client_key = 'professional' if client_type.lower() == 'professional' else 'retail'
                required_disclaimer = disclaimers_db[disclaimer_type].get(client_key)

                if required_disclaimer and len(required_disclaimer) > 50:
                    all_slides_text = extract_all_text_from_doc(doc)

                    if 'tokenfactory_client' in globals() and tokenfactory_client:
                        result = check_disclaimer_in_document(all_slides_text, required_disclaimer)

                        if result.get('status') == 'MISSING':
                            violations.append({
                                'rule_id': 'DISC_001',
                                'section': 'general',
                                'severity': 'critical',
                                'rule_text': f'Required {client_key} disclaimer',
                                'message': f"Required disclaimer not found: {result.get('explanation', '')}",
                                'slide': None,
                                'suggested_fix': f"Add the required {client_key} disclaimer to the document"
                            })

        # ====================================================================
        # CHECK 2: REGISTRATION
        # ====================================================================
        if fund_isin and 'funds_db' in globals() and funds_db:
            fund_info = None
            for fund in funds_db:
                if fund['isin'] == fund_isin:
                    fund_info = fund
                    break

            if fund_info:
                authorized_countries = fund_info['authorized_countries']
                print(f"✓ Fund: {fund_info['fund_name']}")
                print(f"✓ Authorized in {len(authorized_countries)} countries\n")

                # Use enhanced LLM-based registration check
                if 'check_registration_rules_enhanced' in globals():
                    reg_violations = check_registration_rules_enhanced(
                        doc,
                        fund_isin,
                        authorized_countries
                    )
                    violations.extend(reg_violations)

                    if not reg_violations:
                        print("✓ Registration compliance: OK\n")
            else:
                print(f"⚠️  Fund {fund_isin} not found in registration database\n")

        # CHECK 3: STRUCTURE
        if 'structure_rules' in globals() and structure_rules:
            print("Checking structure...")
            try:
                if 'check_structure_rules_enhanced' in globals():
                    structure_violations = check_structure_rules_enhanced(doc, client_type, fund_status)
                    violations.extend(structure_violations)
                    if not structure_violations:
                        print("✓ Structure: OK\n")
            except Exception as e:
                print(f"⚠️  Structure check error: {e}\n")

        # CHECK 4: GENERAL RULES
        if 'general_rules' in globals() and general_rules:
            print("Checking general rules...")
            try:
                if 'check_general_rules_enhanced' in globals():
                    gen_violations = check_general_rules_enhanced(doc, client_type, country_code)
                    violations.extend(gen_violations)
                    if not gen_violations:
                        print("✓ General rules: OK\n")
            except Exception as e:
                print(f"⚠️  General rules check error: {e}\n")

        # CHECK 5: VALUES/SECURITIES
        if 'values_rules' in globals() and values_rules:
            print("Checking securities/values...")
            try:
                if 'check_values_rules_enhanced' in globals():
                    values_violations = check_values_rules_enhanced(doc)
                    violations.extend(values_violations)
                    if not values_violations:
                        print("✓ Securities/Values: OK\n")
            except Exception as e:
                print(f"⚠️  Values check error: {e}\n")

        # CHECK 6: ESG
        if 'esg_rules' in globals() and esg_rules:
            print("Checking ESG rules...")
            try:
                if 'check_esg_rules_enhanced' in globals():
                    esg_violations = check_esg_rules_enhanced(doc, esg_classification, client_type)
                    violations.extend(esg_violations)
                    if not esg_violations:
                        print("✓ ESG: OK\n")
            except Exception as e:
                print(f"⚠️  ESG check error: {e}\n")

        # CHECK 7: PERFORMANCE
        if 'performance_rules' in globals() and performance_rules:
            print("Checking performance rules...")
            try:
                if 'check_performance_rules_enhanced' in globals():
                    perf_violations = check_performance_rules_enhanced(doc, client_type, fund_age_years)
                    violations.extend(perf_violations)
                    if not perf_violations:
                        print("✓ Performance: OK\n")
            except Exception as e:
                print(f"⚠️  Performance check error: {e}\n")

        # CHECK 8: PROSPECTUS
        if 'prospectus_data' in globals() and 'prospectus_rules' in globals() and prospectus_data and prospectus_rules:
            print("Checking prospectus compliance...")
            try:
                if 'check_prospectus_compliance' in globals():
                    prosp_violations = check_prospectus_compliance(doc, prospectus_data)
                    violations.extend(prosp_violations)
                    if not prosp_violations:
                        print("✓ Prospectus: OK\n")
            except Exception as e:
                print(f"⚠️  Prospectus check error: {e}\n")

        # FINAL REPORT
        print(f"\n{'='*70}")
        if len(violations) == 0:
            print("✅ NO VIOLATIONS FOUND - Document is compliant!")
        else:
            print(f"⚠️  {len(violations)} VIOLATION(S) FOUND")
        print(f"{'='*70}\n")

        # Display violations (only in CLI mode)
        if not isinstance(json_file_path_or_dict, dict):
            for i, v in enumerate(violations, 1):
                print(f"{'='*70}")
                print(f"[{v.get('severity', 'unknown').upper()}] {v.get('section', 'general').upper()} Violation #{i}")
                print(f"{'='*70}")
                print(f"📋 Rule: {v.get('rule_text', 'N/A')}")
                print(f"⚠️  Issue: {v.get('message', 'N/A')}")
                if v.get('slide'):
                    print(f"📍 Slide: {v.get('slide')}")
                if v.get('suggested_fix'):
                    print(f"\n💡 Suggested Fix:")
                    print(f"   {v.get('suggested_fix')}")
                print()

            # Summary
            if violations:
                print(f"\n{'='*70}")
                print(f"SUMMARY")
                print(f"{'='*70}")

                # By section
                section_counts = {}
                for v in violations:
                    section = v.get('section', 'unknown')
                    section_counts[section] = section_counts.get(section, 0) + 1

                print(f"\nViolations by section:")
                for section, count in sorted(section_counts.items()):
                    print(f"   {section}: {count}")

                # By severity
                severity_counts = {}
                for v in violations:
                    sev = v.get('severity', 'unknown')
                    severity_counts[sev] = severity_counts.get(sev, 0) + 1

                print(f"\nViolations by severity:")
                for sev in ['critical', 'warning', 'info']:
                    if sev in severity_counts:
                        print(f"   {sev.upper()}: {severity_counts[sev]}")

        return {
            'total_violations': len(violations),
            'violations': violations,
            'fund_isin': fund_isin,
            'client_type': client_type
        }

    except FileNotFoundError:
        print(f"\n❌ File '{json_file_path_or_dict}' not found")
        return {'error': 'File not found', 'violations': []}
    except Exception as e:
        print(f"\n❌ Error checking document: {e}")
        import traceback
        traceback.print_exc()
        return {'error': str(e), 'violations': []}


def main():
    """Main function"""
    if len(sys.argv) < 2:
        print("\n" + "="*70)
        print("FUND COMPLIANCE CHECKER")
        print("="*70)
        print("\nUsage:")
        print("  python check.py <json_file>")
        print("\nExample:")
        print("  python check.py exemple.json")
        print("\nThe JSON file should contain:")
        print("  - document_metadata with fund_isin, client_type, etc.")
        print("  - page_de_garde, slide_2, pages_suivantes, page_de_fin")
        print("="*70)
        sys.exit(1)

    json_file = sys.argv[1]
    
    if not os.path.exists(json_file):
        print(f"\n File '{json_file}' not found")
        print(f" Current directory: {os.getcwd()}")
        print(f"„ Available JSON files:")
        json_files = [f for f in os.listdir('.') if f.endswith('.json')]
        if json_files:
            for f in json_files:
                print(f"  - {f}")
        else:
            print("  (none found)")
        sys.exit(1)

    result = check_document_compliance(json_file)
    
    if 'error' not in result:
        print(f"\n{'='*70}")
        print("Š CHECK COMPLETE")
        print(f"{'='*70}")
        
        if result['total_violations'] == 0:
            print("\nðŸŽ‰ Document is fully compliant!")
            sys.exit(0)
        else:
            print(f"\n¸  Please review and fix {result['total_violations']} violation(s)")
            sys.exit(1)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()