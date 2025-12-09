#!/usr/bin/env python3
"""
Document Compliance Validator
Uses LLM with automatic fallback (TokenFactory -> Gemini) to validate documents against structure rules
Usage: python test.py exemple.json structure_rules.json
"""

import json
import sys

# Import path utilities
from path_utils import ENV_FILE, ensure_directories

# Import LLM Manager with fallback support
from llm_manager import llm_manager

def load_json_file(filepath):
    """Load and parse a JSON file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: File '{filepath}' not found")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in '{filepath}': {e}")
        sys.exit(1)

def validate_document(document_json, rules_json, metadata_json):
    """
    Validate document against structure rules using LLM with automatic fallback
    Replicates the exact rule-by-rule validation approach
    """
    
    # Construct the validation prompt that mirrors the analytical approach
    system_prompt = """You are a compliance validation analyst. You must validate documents against compliance rules using a systematic rule-driven approach.

CRITICAL: You must be thorough, precise, and follow the exact validation methodology described."""

    # Merge metadata into document if provided
    if metadata_json:
        if 'document_metadata' not in document_json:
            document_json['document_metadata'] = {}
        
        # Map metadata fields to document_metadata
        if "Le document fait-il référence à un nouveau Produit" in metadata_json:
            document_json['document_metadata']['fund_status'] = 'pre-commercialisation' if metadata_json["Le document fait-il référence à un nouveau Produit"] else 'active'
        
        if "Le client est-il un professionnel" in metadata_json:
            document_json['document_metadata']['client_type'] = 'professional' if metadata_json["Le client est-il un professionnel"] else 'retail'
        
        # Add other metadata fields
        document_json['document_metadata']['management_company'] = metadata_json.get("Société de Gestion", "")
        document_json['document_metadata']['is_oddo_sicav'] = metadata_json.get("Est ce que le produit fait partie de la Sicav d'Oddo", False)
        document_json['document_metadata']['is_new_strategy'] = metadata_json.get("Le document fait-il référence à une nouvelle Stratégie", False)
        document_json['document_metadata']['is_new_product'] = metadata_json.get("Le document fait-il référence à un nouveau Produit", False)
    
    user_prompt = f"""I need you to validate a document against compliance rules using a **rule-driven approach**.

IMPORTANT: Follow this EXACT validation logic:

## STEP-BY-STEP VALIDATION PROCESS:

### Step 1: Rule Inventory
- Review all rules in the structure_rules.json
- Categorize by section, severity, and validation type
- Note: There are 11 rules total (STRUCT_001 through STRUCT_011)

### Step 2: Rule-by-Rule Validation
For EACH rule systematically:
1. Check if rule is applicable (based on client_type, document_type, fund_status in the document metadata)
2. If applicable:
   - Navigate to the relevant JSON path in the document
   - Extract the field value
   - Apply the validation_type logic
   - Determine: COMPLIANT ✅ / VIOLATION ❌ / NEEDS_VERIFICATION ⚠️
3. If not applicable: Mark as N/A

### Step 3: Validation Types
- **presence_check**: Check if field exists and is not empty (not "", not null, not [])
- **presence_check_with_format**: Check presence AND formatting requirements (color, bold, etc.)
- **conditional_presence_check**: Only check if condition is met
- **presence_check_with_customization**: Check presence and verify customization fields
- **conformity_check**: Verify against external reference (flag for manual verification)
- **data_conformity_check**: Verify against reference data file (flag for manual verification)

### Step 4: Critical Rules to Check Carefully
- STRUCT_001: Fund name in page_de_garde.fund_name
- STRUCT_002: Date in page_de_garde.date
- STRUCT_003: Promotional document mention in page_de_garde.promotional_document_mention
- STRUCT_004: Target audience in page_de_garde.target_audience
- STRUCT_005: Pre-commercialisation warning (check document_metadata.fund_status)
- STRUCT_006: "Do not disclose" mention (only if professional)
- STRUCT_007: Client name (only if client-specific)
- STRUCT_008: Standard disclaimer on slide_2
- STRUCT_009: Complete risk profile on slide_2.all_risks_listed
- STRUCT_010: Commercialisation countries on slide_2
- STRUCT_011: SGP legal mention on page_de_fin.legal_mention_sgp

---

## DOCUMENT TO VALIDATE:
```json
{json.dumps(document_json, indent=2, ensure_ascii=False)}
```

## STRUCTURE RULES:
```json
{json.dumps(rules_json, indent=2, ensure_ascii=False)}
```

---

## YOUR TASK:

Validate the document against ALL 11 rules in structure_rules.json using the rule-by-rule approach described above.

For each rule, provide:
1. **Rule ID** (e.g., STRUCT_001)
2. **Section** (Cover Page, Slide 2, or Back Page)
3. **Applicability**: Is this rule applicable to this document?
4. **JSON Path Checked**: Where you looked in the document
5. **Value Found**: What you found at that path
6. **Validation Result**: COMPLIANT ✅ / VIOLATION ❌ / N/A / NEEDS_VERIFICATION ⚠️
7. **Explanation**: Why it passed or failed

Then provide a **SUMMARY** section with:
- **CRITICAL VIOLATIONS** (severity: critical)
- **MAJOR ISSUES** (severity: major)
- **MINOR ISSUES** (severity: minor)
- **COMPLIANT ELEMENTS**
- **Total Violations Count**
- **Detailed Remediation Steps** for each violation

Format your response clearly with headers and emojis for readability.
Be systematic and check EVERY rule - do not skip any."""

    # Call LLM with automatic fallback (TokenFactory -> Gemini)
    print("🔍 Analyzing document compliance using LLM (with Gemini fallback)...")
    print(f"📡 Available providers: {', '.join(llm_manager.get_available_providers())}")
    print("⏳ This may take a moment...\n")
    
    response_text = llm_manager.call_llm(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        temperature=0.3,
        max_tokens=8000
    )
    
    if not response_text:
        print(f"❌ Error: All LLM providers failed")
        print(f"   Last error: {llm_manager.last_error}")
        sys.exit(1)
    
    print(f"✅ Response received from: {llm_manager.get_current_provider()}")
    return response_text

def generate_structure_violation_annotations(validation_result, document, rules):
    """
    Generate a JSON file with violation annotations for highlighting in the document.
    Parses the LLM validation result to extract violations with locations and details.
    """
    import re
    
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
    
    # Parse the validation result text to extract violations
    # Look for patterns like "STRUCT_001", "VIOLATION", "COMPLIANT", etc.
    
    # Split by rule sections
    rule_sections = re.split(r'(?=STRUCT_\d+)', validation_result)
    
    for section in rule_sections:
        if not section.strip():
            continue
        
        # Extract rule ID
        rule_match = re.search(r'(STRUCT_\d+)', section)
        if not rule_match:
            continue
        
        rule_id = rule_match.group(1)
        
        # Check if it's a violation
        is_violation = 'VIOLATION' in section and 'COMPLIANT' not in section.split('VIOLATION')[0]
        
        if not is_violation:
            continue
        
        # Extract severity
        severity = 'minor'
        if 'critical' in section.lower():
            severity = 'critical'
        elif 'major' in section.lower():
            severity = 'major'
        
        # Extract location/path
        location = 'unknown'
        path_match = re.search(r'(?:JSON Path|Path|Location)[:\s]+([^\n]+)', section, re.IGNORECASE)
        if path_match:
            location = path_match.group(1).strip()
        
        # Extract value found or evidence
        value_found = ''
        value_match = re.search(r'(?:Value Found|Found|Evidence)[:\s]+([^\n]+)', section, re.IGNORECASE)
        if value_match:
            value_found = value_match.group(1).strip()
        
        # Extract explanation
        explanation = ''
        expl_match = re.search(r'(?:Explanation|Reason)[:\s]+([^\n]+)', section, re.IGNORECASE)
        if expl_match:
            explanation = expl_match.group(1).strip()
        
        # Get slide number from location
        slide_number = get_slide_number_from_location(location, document)
        
        # Get rule details from rules JSON
        rule_details = get_rule_details(rule_id, rules)
        
        annotation = {
            "rule_id": rule_id,
            "severity": severity,
            "location": location,
            "page_number": slide_number,
            "exact_phrase": value_found,
            "character_count": len(value_found),
            "violation_comment": f"[{rule_id}] {explanation if explanation else rule_details.get('description', 'Violation detected')}",
            "required_action": rule_details.get('required_action', 'Review and correct violation')
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

def get_slide_number_from_location(location_string, document):
    """Get the actual slide number from the document structure based on location string."""
    import re
    
    # Direct mapping for known sections
    location_map = {
        'page_de_garde': 'page_de_garde',
        'slide_2': 'slide_2',
        'page_de_fin': 'page_de_fin',
        'metadata': 'document_metadata'
    }
    
    location_lower = location_string.lower().strip()
    
    # Try direct mapping first
    for key, section_name in location_map.items():
        if key in location_lower:
            if section_name in document:
                return document[section_name].get('slide_number')
    
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
    
    return None

def get_rule_details(rule_id, rules):
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
        print("Usage: python test_structure.py <document.json> <rules.json> [metadata.json]")
        print("Example: python test_structure.py exemple.json structure_rules.json")
        print("Example with metadata: python test_structure.py exemple.json structure_rules.json metadata.json")
        sys.exit(1)
    
    document_file = sys.argv[1]
    rules_file = sys.argv[2]
    metadata_file = sys.argv[3] if len(sys.argv) == 4 else None
    
    # Load files
    print(f"📄 Loading document: {document_file}")
    document = load_json_file(document_file)
    
    print(f"📋 Loading rules: {rules_file}")
    rules = load_json_file(rules_file)
    
    # Load metadata if provided
    metadata = None
    if metadata_file:
        print(f"📊 Loading metadata: {metadata_file}")
        metadata = load_json_file(metadata_file)
    
    # Check available LLM providers
    available_providers = llm_manager.get_available_providers()
    
    if not available_providers:
        print("\n❌ Error: No LLM API keys found in .env file")
        print("Please create a .env file with at least one of:")
        print("  TOKENFACTORY_API_KEY=your-api-key")
        print("  GEMINI_API_KEY=your-gemini-api-key")
        sys.exit(1)
    
    print(f"✅ Available LLM providers: {', '.join(available_providers)}")
    print(f"🤖 Primary: TokenFactory (Llama-3.1-70B), Fallback: Gemini\n")
    print("="*80)
    
    # Validate document
    validation_result = validate_document(document, rules, metadata)
    
    # Display results
    print("\n" + "="*80)
    print("COMPLIANCE VALIDATION REPORT")
    print("="*80 + "\n")
    print(validation_result)
    print("\n" + "="*80)
    
    # Save results to file
    output_file = "validation_report.txt"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("COMPLIANCE VALIDATION REPORT\n")
        f.write("="*80 + "\n\n")
        f.write(f"Generated using TokenFactory API (Llama-3.1-70B-Instruct)\n")
        f.write(f"Document: {document_file}\n")
        f.write(f"Rules: {rules_file}\n")
        if metadata_file:
            f.write(f"Metadata: {metadata_file}\n")
        f.write("="*80 + "\n\n")
        f.write(validation_result)
    
    print(f"\n✅ Report saved to: {output_file}")
    
    # Generate violation annotations JSON for highlighting
    annotations = generate_structure_violation_annotations(validation_result, document, rules)
    annotations_file = "structure_violation_annotations.json"
    with open(annotations_file, 'w', encoding='utf-8') as f:
        json.dump(annotations, f, indent=2, ensure_ascii=False)
    
    print(f"💾 Violation annotations saved to: {annotations_file}")
    print(f"📊 Validation complete!")

if __name__ == "__main__":
    main()