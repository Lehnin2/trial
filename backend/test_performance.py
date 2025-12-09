#!/usr/bin/env python3
"""
Performance Compliance Analyzer
Replicates the hybrid sequential-contextual analysis approach
Uses LLM with automatic fallback (TokenFactory -> Gemini)
Usage: python test_performance.py exemple.json performance_rules.json [metadata.json]
"""

import json
import sys
from dotenv import load_dotenv
import os
import re

# Import path utilities
from path_utils import ENV_FILE, ensure_directories

# Import LLM Manager with fallback support
from llm_manager import llm_manager

# Load environment variables from .env file
load_dotenv(str(ENV_FILE))

def load_json_file(filepath):
    """Load and parse JSON file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: File '{filepath}' not found.")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in '{filepath}': {e}")
        sys.exit(1)

def interpret_metadata(metadata):
    """Convert French metadata to English compliance context"""
    return {
        "management_company": metadata.get("Société de Gestion", ""),
        "is_oddo_sicav": metadata.get("Est ce que le produit fait partie de la Sicav d'Oddo", False),
        "is_professional_client": metadata.get("Le client est-il un professionnel", False),
        "is_new_strategy": metadata.get("Le document fait-il référence à une nouvelle Stratégie", False),
        "is_new_product": metadata.get("Le document fait-il référence à un nouveau Produit", False),
        "client_type": "professional" if metadata.get("Le client est-il un professionnel", False) else "retail",
        "document_type": "strategy" if metadata.get("Le document fait-il référence à une nouvelle Stratégie", False) else "fund"
    }

def build_analysis_prompt(document, rules, metadata_context):
    """Build the exact analysis prompt that replicates the approach"""
    
    prompt = f"""You are a compliance analyst performing a performance rules validation. Use the EXACT three-phase hybrid sequential-contextual approach:

# PHASE 1: DOCUMENT UNDERSTANDING & CONTEXT GATHERING

First, scan the document and extract:
- Document type and structure
- Target audience: {metadata_context['client_type']} client
- Document type: {metadata_context['document_type']}
- Fund/strategy characteristics (age, launch date, AUM)
- Presence/absence of actual performance data
- Geographic scope (country field)

# PHASE 2: RULE SET PRIORITIZATION

Use the rules file structure to prioritize checks:

## Priority 1: Critical Prohibitions & Prerequisites
Focus on "critical" severity rules first:
- PERF_011: Check if fund < 1 year (if so, NO performance allowed)
- PERF_001: Check if document begins with performance (prohibited)
- PERF_026: Check structure for strategy documents

## Priority 2: Metadata-Dependent Rules
Identify rules that depend on client_type or country:
- Client type is: {metadata_context['client_type']}
- Check retail-only rules (PERF_003, PERF_021, PERF_025, PERF_040, PERF_043, PERF_044)
- Check professional-only rules (PERF_026-PERF_035, PERF_042, PERF_055)
- Check country-specific rules (PERF_008, PERF_009, PERF_012 for Germany, PERF_055 for France)

## Priority 3: Content-Present Rules
Only check rules for content actually in the document:
- If benchmark present → check PERF_014, PERF_032, PERF_038
- If disclaimers present → check PERF_053, PERF_054
- If fees mentioned → check PERF_021, PERF_022
- If simulations present → check PERF_045-PERF_052

# PHASE 3: CONTEXTUAL CROSS-VALIDATION

Apply logical dependencies:
```
IF fund_age < 1 year (PERF_011):
  THEN no performance should be displayed
  THEN skip PERF_004, PERF_005, PERF_006, PERF_010, etc. (format rules)

IF no_performance_displayed:
  THEN performance format/comparison rules = NOT APPLICABLE
  THEN PERF_054 disclaimer = LESS CRITICAL

IF client_type known:
  THEN check client-specific restrictions
ELSE:
  THEN flag as CANNOT VERIFY
```

# YOUR TASK

Analyze the document following this exact approach and provide:

1. **CRITICAL COMPLIANCE ISSUES** (violations that block distribution)
   - Missing metadata
   - Fundamental prohibitions violated
   - Client-type violations

2. **STRUCTURAL COMPLIANCE ISSUES**
   - Document structure (PERF_001, PERF_026)
   - Performance prominence (PERF_002)

3. **BENCHMARK COMPLIANCE**
   - Benchmark disclosure and comparison rules

4. **DISCLAIMER COMPLIANCE**
   - Required disclaimers present/absent

5. **CONTENT-SPECIFIC COMPLIANCE**
   - Share class, fees, investment horizon, etc.

6. **SUMMARY OF FINDINGS**
   - Critical issues requiring immediate action
   - Compliant areas
   - Recommendations
   - Overall compliance status

For each finding, specify:
- Rule ID violated/checked
- Severity level
- Finding details
- Status (✅ COMPLIANT / ❌ NON-COMPLIANT / ⚠️ WARNING / ℹ️ NOT APPLICABLE)
- Remediation steps if non-compliant

# IMPORTANT ANALYSIS PRINCIPLES

1. **Don't check all 58 rules sequentially** - use the prioritization approach
2. **Skip rules that don't apply** due to document characteristics
3. **Use logical dependencies** to avoid redundant checks
4. **Flag metadata gaps** that prevent full validation
5. **Focus on what's actually in the document**

---

# DOCUMENT TO ANALYZE

{json.dumps(document, indent=2, ensure_ascii=False)}

---

# PERFORMANCE RULES KNOWLEDGE BASE

{json.dumps(rules, indent=2, ensure_ascii=False)}

---

# METADATA CONTEXT

- Management Company: {metadata_context['management_company']}
- Client Type: {metadata_context['client_type']}
- Document Type: {metadata_context['document_type']}
- Is ODDO SICAV: {metadata_context['is_oddo_sicav']}
- Is New Strategy: {metadata_context['is_new_strategy']}
- Is New Product: {metadata_context['is_new_product']}

---

Begin your analysis following the three-phase approach exactly as described."""

    return prompt

def analyze_compliance(document, rules, metadata):
    """Perform compliance analysis using LLM with automatic fallback"""
    
    # Check available LLM providers
    available_providers = llm_manager.get_available_providers()
    
    if not available_providers:
        print("⚠️  No LLM API keys found in .env file")
        print("Please create a .env file with at least one of:")
        print("  TOKENFACTORY_API_KEY=your-api-key")
        print("  GEMINI_API_KEY=your-gemini-api-key")
        sys.exit(1)
    
    # Interpret metadata
    metadata_context = interpret_metadata(metadata)
    
    # Build analysis prompt
    prompt = build_analysis_prompt(document, rules, metadata_context)
    
    print("🔍 Starting Compliance Analysis...")
    print(f"📋 Client Type: {metadata_context['client_type']}")
    print(f"📋 Document Type: {metadata_context['document_type']}")
    print(f"📡 Available LLM providers: {', '.join(available_providers)}")
    print(f"🤖 Using LLM with automatic fallback (TokenFactory -> Gemini)...\n")
    
    # Call LLM with automatic fallback
    system_prompt = "You are an expert compliance analyst specializing in financial performance documentation. Provide detailed, structured analysis following the given methodology."
    
    analysis_result = llm_manager.call_llm(
        system_prompt=system_prompt,
        user_prompt=prompt,
        temperature=0.3,
        max_tokens=8000
    )
    
    if not analysis_result:
        print(f"❌ Error calling LLM: {llm_manager.last_error}")
        print("\nTroubleshooting:")
        print("1. Verify your API keys are correct")
        print("2. Check your internet connection")
        print("3. Ensure LLM services are accessible")
        sys.exit(1)
    
    print(f"✅ Response received from: {llm_manager.get_current_provider()}")
    return analysis_result

def format_output(analysis_result, metadata_context):
    """Format the analysis output"""
    
    output = "=" * 80 + "\n"
    output += "PERFORMANCE COMPLIANCE ANALYSIS REPORT\n"
    output += "=" * 80 + "\n\n"
    
    output += f"📊 Analysis Metadata:\n"
    output += f"  • Client Type: {metadata_context['client_type'].upper()}\n"
    output += f"  • Document Type: {metadata_context['document_type'].upper()}\n"
    output += f"  • Management Company: {metadata_context['management_company']}\n"
    output += f"  • New Product: {'Yes' if metadata_context['is_new_product'] else 'No'}\n"
    output += f"  • New Strategy: {'Yes' if metadata_context['is_new_strategy'] else 'No'}\n"
    output += "\n" + "-" * 80 + "\n\n"
    
    output += analysis_result
    
    output += "\n\n" + "=" * 80 + "\n"
    output += "END OF COMPLIANCE REPORT\n"
    output += "=" * 80 + "\n"
    
    return output

def generate_performance_violation_annotations(analysis_result, document, rules):
    """
    Generate a JSON file with violation annotations for highlighting in the document.
    Parses the analysis result to extract violations with locations and details.
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
    
    # Parse the analysis result to extract violations
    # Look for patterns like "PERF_001", "NON-COMPLIANT", "VIOLATION", etc.
    
    # Split by rule sections
    rule_sections = re.split(r'(?=PERF_\d+)', analysis_result)
    
    for section in rule_sections:
        if not section.strip():
            continue
        
        # Extract rule ID
        rule_match = re.search(r'(PERF_\d+)', section)
        if not rule_match:
            continue
        
        rule_id = rule_match.group(1)
        
        # Check if it's a violation (not compliant or not applicable)
        is_violation = any(keyword in section for keyword in ['❌', 'NON-COMPLIANT', 'VIOLATION', 'VIOLATED'])
        
        if not is_violation:
            continue
        
        # Extract severity
        severity = 'minor'
        if 'CRITICAL' in section or 'critical' in section.lower():
            severity = 'critical'
        elif 'MAJOR' in section or 'major' in section.lower():
            severity = 'major'
        
        # Extract location
        location = 'unknown'
        location_match = re.search(r'(?:Location|Found in|Section|Page)[:\s]+([^\n]+)', section, re.IGNORECASE)
        if location_match:
            location = location_match.group(1).strip()
        
        # Extract finding details or evidence
        finding = ''
        finding_match = re.search(r'(?:Finding|Details|Issue|Problem)[:\s]+([^\n]+)', section, re.IGNORECASE)
        if finding_match:
            finding = finding_match.group(1).strip()
        
        # Extract remediation
        remediation = ''
        remediation_match = re.search(r'(?:Remediation|Action|Fix|Required)[:\s]+([^\n]+)', section, re.IGNORECASE)
        if remediation_match:
            remediation = remediation_match.group(1).strip()
        
        # Get slide number from location
        slide_number = get_slide_number_from_location_perf(location, document)
        
        # Get rule details from rules JSON
        rule_details = get_rule_details_perf(rule_id, rules)
        
        annotation = {
            "rule_id": rule_id,
            "severity": severity,
            "location": location,
            "page_number": slide_number,
            "exact_phrase": finding,
            "character_count": len(finding),
            "violation_comment": f"[{rule_id}] {finding if finding else rule_details.get('description', 'Violation detected')}",
            "required_action": remediation if remediation else rule_details.get('required_action', 'Review and correct violation')
        }
        
        annotations["document_annotations"].append(annotation)
        
        # Update summary counts
        annotations["summary"]["total_violations"] += 1
        if severity == 'critical':
            annotations["summary"]["critical_violations"] += 1
        elif severity == 'major':
            annotations["summary"]["major_violations"] += 1
        elif severity == 'minor':
            annotations["summary"]["minor_violations"] += 1
    
    return annotations

def get_slide_number_from_location_perf(location_string, document):
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
    
    # For unknown or document-wide violations, try to infer from context
    # Performance data is typically on page_de_garde (slide 1) or in pages_suivantes
    if 'unknown' in location_lower or 'document-wide' in location_lower:
        # Check if it's about performance data - usually on cover or first pages
        if 'performance' in location_lower or 'benchmark' in location_lower:
            return 1  # Typically on cover page
        # Check if it's about disclaimers - usually on last page
        if 'disclaimer' in location_lower:
            if 'page_de_fin' in document:
                return document['page_de_fin'].get('slide_number', document.get('document_metadata', {}).get('page_count'))
        # Default to first page for unknown violations
        return 1
    
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
    
    # If still no match, return first page as default
    return 1

def get_rule_details_perf(rule_id, rules):
    """Get rule details from the rules JSON."""
    for rule in rules.get('rules', []):
        if rule.get('rule_id') == rule_id:
            return {
                'description': rule.get('description', ''),
                'required_action': rule.get('remediation', 'Review and correct violation')
            }
    return {'description': '', 'required_action': 'Review and correct violation'}

def main():
    """Main execution function"""
    
    # Check command line arguments
    if len(sys.argv) < 3 or len(sys.argv) > 4:
        print("Usage: python test_performance.py <document.json> <performance_rules.json> [metadata.json]")
        print("\nExample:")
        print("  python test_performance.py exemple.json performance_rules.json metadata.json")
        print("  python test_performance.py exemple.json performance_rules.json")
        sys.exit(1)
    
    document_file = sys.argv[1]
    rules_file = sys.argv[2]
    metadata_file = sys.argv[3] if len(sys.argv) == 4 else None
    
    # Load files
    print("📂 Loading files...")
    document = load_json_file(document_file)
    rules = load_json_file(rules_file)
    
    # Load metadata if provided
    metadata = {}
    if metadata_file:
        print(f"📊 Loading metadata: {metadata_file}")
        metadata = load_json_file(metadata_file)
    
    # Interpret metadata
    metadata_context = interpret_metadata(metadata)
    
    # Perform analysis
    analysis_result = analyze_compliance(document, rules, metadata)
    
    # Format and display output
    output = format_output(analysis_result, metadata_context)
    print(output)
    
    # Save report to file
    output_filename = "performance_validation_report.txt"
    with open(output_filename, 'w', encoding='utf-8') as f:
        f.write(output)
    
    print(f"\n💾 Report saved to: {output_filename}")
    
    # Generate violation annotations JSON for highlighting
    annotations = generate_performance_violation_annotations(analysis_result, document, rules)
    annotations_file = "performance_violation_annotations.json"
    with open(annotations_file, 'w', encoding='utf-8') as f:
        json.dump(annotations, f, indent=2, ensure_ascii=False)
    
    print(f"💾 Violation annotations saved to: {annotations_file}")

if __name__ == "__main__":
    main()