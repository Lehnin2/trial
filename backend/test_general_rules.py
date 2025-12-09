#!/usr/bin/env python3
"""
Compliance Analysis Tool
Replicates the hybrid analytical approach for document compliance checking.
Uses LLM with automatic fallback (TokenFactory -> Gemini)
Usage: python test.py exemple.json general_rules.json
"""

import json
import sys
from typing import Dict, List, Any, Tuple
import os
from dotenv import load_dotenv

# Import path utilities
from path_utils import ENV_FILE, ensure_directories

# Import LLM Manager with fallback support
from llm_manager import llm_manager

# Load environment variables from .env file
load_dotenv(str(ENV_FILE))

class ComplianceAnalyzer:
    """
    Analyzes documents for compliance using a hybrid approach:
    1. Initial document scan
    2. Rules categorization
    3. Critical rules first
    4. Parallel pattern matching
    5. Cross-reference validation
    6. Evidence collection
    """
    
    def __init__(self, api_key: str = None):
        """Initialize the analyzer - uses llm_manager with automatic fallback"""
        self.llm = llm_manager
        
        # Check if any LLM provider is available
        if not self.llm.get_available_providers():
            raise ValueError("No LLM API keys found. Set TOKENFACTORY_API_KEY or GEMINI_API_KEY")
        
    def load_json(self, filepath: str) -> Dict:
        """Load JSON file."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading {filepath}: {e}")
            sys.exit(1)
    
    def _call_llm(self, prompt: str, max_tokens: int = 8000) -> str:
        """Helper method to call the LLM with automatic fallback."""
        result = self.llm.call_llm(
            system_prompt="You are a compliance analysis expert. You analyze documents for regulatory compliance and provide detailed, structured responses.",
            user_prompt=prompt,
            temperature=0.3,
            max_tokens=max_tokens
        )
        if not result:
            raise Exception(f"LLM call failed: {self.llm.last_error}")
        return result
    
    def phase1_document_scan(self, document: Dict) -> Dict[str, Any]:
        """
        Phase 1: Initial Document Scan (Rapid Assessment)
        - Quick structural understanding
        - Identify empty critical fields
        - Determine document type
        """
        prompt = f"""You are performing Phase 1: Initial Document Scan of a compliance analysis.

DOCUMENT METADATA:
{json.dumps(document.get('document_metadata', {}), indent=2)}

Your task is to rapidly assess:
1. Document type (fund presentation, strategy, etc.)
2. Target audience (retail/professional) - CHECK IF EMPTY!
3. Critical metadata fields that are empty or missing
4. Document structure (how many slides, what sections exist)

Provide a JSON response with:
{{
  "document_type": "...",
  "client_type": "retail/professional/EMPTY/MISSING",
  "critical_empty_fields": ["field1", "field2"],
  "structure_summary": "brief description",
  "immediate_red_flags": ["flag1", "flag2"]
}}

Be VERY specific about empty fields (like client_type: "", srri: "", etc.)."""

        result = self._call_llm(prompt, max_tokens=19500)
        
        # Extract JSON from response
        try:
            json_start = result.find('{')
            json_end = result.rfind('}') + 1
            return json.loads(result[json_start:json_end])
        except:
            return {"error": "Could not parse Phase 1 results", "raw": result}
    
    def phase2_categorize_rules(self, rules: Dict) -> Dict[str, List[Dict]]:
        """
        Phase 2: Rules Categorization (Mental Mapping)
        Categorize rules by type for efficient checking
        """
        prompt = f"""You are performing Phase 2: Rules Categorization.

RULES DOCUMENT:
{json.dumps(rules, indent=2)}

Categorize these rules into types:
- metadata_rules: Rules about client_type, disclaimers, document metadata
- content_rules: Rules about sources, dates, SRI, data presentation
- formatting_rules: Rules about bold, font size, visibility
- structure_rules: Rules about document order, glossary, page layout
- language_rules: Rules about softening, anglicisms, translations

Return JSON:
{{
  "metadata_rules": [list of rule_ids],
  "content_rules": [list of rule_ids],
  "formatting_rules": [list of rule_ids],
  "structure_rules": [list of rule_ids],
  "language_rules": [list of rule_ids]
}}"""

        result = self._call_llm(prompt, max_tokens=19500)
        
        try:
            json_start = result.find('{')
            json_end = result.rfind('}') + 1
            return json.loads(result[json_start:json_end])
        except:
            return {"error": "Could not parse Phase 2 results"}
    
    def phase3_prioritize_rules(self, rules: Dict, phase1_results: Dict) -> Dict[str, List[str]]:
        """
        Phase 3: Critical Rules First (Priority-Based)
        Prioritize rules by severity and relevance
        """
        prompt = f"""You are performing Phase 3: Rule Prioritization.

RULES:
{json.dumps(rules, indent=2)}

PHASE 1 FINDINGS:
{json.dumps(phase1_results, indent=2)}

Prioritize rules into three tiers based on severity and Phase 1 red flags:

Tier 1 (BLOCKING - prevents distribution): critical severity, especially those related to Phase 1 red flags
Tier 2 (MAJOR - legal risk): major severity
Tier 3 (QUALITY - best practices): minor severity

Return JSON:
{{
  "tier1_blocking": [list of rule_ids with brief reason],
  "tier2_major": [list of rule_ids],
  "tier3_quality": [list of rule_ids]
}}"""

        result = self._call_llm(prompt, max_tokens=19500)
        
        try:
            json_start = result.find('{')
            json_end = result.rfind('}') + 1
            return json.loads(result[json_start:json_end])
        except:
            return {"error": "Could not parse Phase 3 results"}
    
    def phase4_check_rules_parallel(self, document: Dict, rules: Dict, 
                                   prioritized_rules: Dict) -> Dict[str, Any]:
        """
        Phase 4: Parallel Pattern Matching
        Check each rule against relevant document sections only
        """
        violations = {"critical": [], "major": [], "minor": [], "compliant": []}
        
        # Process Tier 1 (Blocking) first
        print("\n🔍 Checking Tier 1 (Blocking Issues)...")
        for rule_id in prioritized_rules.get('tier1_blocking', []):
            violation = self._check_single_rule(document, rules, rule_id)
            if violation:
                violations['critical'].append(violation)
        
        # Process Tier 2 (Major)
        print("🔍 Checking Tier 2 (Major Issues)...")
        for rule_id in prioritized_rules.get('tier2_major', []):
            violation = self._check_single_rule(document, rules, rule_id)
            if violation:
                violations['major'].append(violation)
        
        # Process Tier 3 (Quality)
        print("🔍 Checking Tier 3 (Quality Issues)...")
        for rule_id in prioritized_rules.get('tier3_quality', []):
            violation = self._check_single_rule(document, rules, rule_id)
            if violation:
                violations['minor'].append(violation)
        
        return violations
    
    def _check_single_rule(self, document: Dict, rules: Dict, rule_id: str) -> Dict:
        """Check a single rule against the document."""
        # Find the rule
        rule = None
        for r in rules.get('rules', []):
            if r['rule_id'] == rule_id:
                rule = r
                break
        
        if not rule:
            return None
        
        prompt = f"""You are checking a SINGLE compliance rule against a document.

RULE TO CHECK:
{json.dumps(rule, indent=2)}

FULL DOCUMENT:
{json.dumps(document, indent=2)}

Your task:
1. Scan ONLY the relevant sections of the document for this rule
2. Check for PRESENCE/ABSENCE/FORMAT as required
3. Determine if this is a VIOLATION or COMPLIANT

Return JSON:
{{
  "rule_id": "{rule_id}",
  "status": "VIOLATION" or "COMPLIANT",
  "severity": "critical/major/minor",
  "evidence": "exact quote or field showing the issue",
  "explanation": "why this is a violation or compliant",
  "location": "where in document (e.g., 'slide 1', 'metadata', 'page_de_garde')",
  "required_action": "what needs to be fixed (if violation)"
}}

If COMPLIANT, still provide evidence of compliance.
Be specific with evidence - quote exact fields or text."""

        try:
            result = self._call_llm(prompt, max_tokens=19500)
            
            json_start = result.find('{')
            json_end = result.rfind('}') + 1
            check_result = json.loads(result[json_start:json_end])
            
            # Only return if it's a violation
            if check_result.get('status') == 'VIOLATION':
                return check_result
            elif check_result.get('status') == 'COMPLIANT':
                return None  # We'll track compliant separately
            
        except Exception as e:
            print(f"Error checking rule {rule_id}: {e}")
            return None
    
    def phase5_cross_reference(self, document: Dict, violations: Dict) -> List[Dict]:
        """
        Phase 5: Cross-Reference Validation
        Check consistency across sections
        """
        prompt = f"""You are performing Phase 5: Cross-Reference Validation.

DOCUMENT:
{json.dumps(document, indent=2)}

VIOLATIONS FOUND SO FAR:
{json.dumps(violations, indent=2)}

Check for consistency issues across sections:
1. Is validation responsible consistent with management company?
2. Are dates consistent across all sections?
3. Any contradictions between different slides?
4. Translation consistency (if multilingual)?

Return JSON array of additional issues found:
[
  {{
    "issue_type": "consistency",
    "severity": "major/minor",
    "description": "what's inconsistent",
    "locations": ["section1", "section2"],
    "evidence": "specific examples"
  }}
]

Return empty array [] if no consistency issues found."""

        try:
            result = self._call_llm(prompt, max_tokens=19500)
            
            json_start = result.find('[')
            json_end = result.rfind(']') + 1
            if json_start != -1 and json_end > json_start:
                return json.loads(result[json_start:json_end])
            return []
        except:
            return []
    
    def phase6_generate_report(self, document: Dict, rules: Dict, 
                              phase1: Dict, violations: Dict, 
                              cross_ref: List[Dict]) -> str:
        """
        Phase 6: Evidence Collection and Report Generation
        Create comprehensive compliance report
        """
        prompt = f"""You are generating the FINAL COMPLIANCE REPORT.

DOCUMENT METADATA:
{json.dumps(document.get('document_metadata', {}), indent=2)}

PHASE 1 SCAN:
{json.dumps(phase1, indent=2)}

ALL VIOLATIONS:
{json.dumps(violations, indent=2)}

CROSS-REFERENCE ISSUES:
{json.dumps(cross_ref, indent=2)}

Generate a comprehensive compliance report in MARKDOWN format following this EXACT structure:

# Compliance Analysis Report: [Fund Name]

## Document Overview
- **Fund Name:** ...
- **Document Type:** ...
- **Date:** ...
- **Target Audience:** ...
- **Pages:** ...

---

## CRITICAL VIOLATIONS

### 1. **[RULE_ID]: [Brief Title]**
- **Severity:** CRITICAL
- **Issue:** [Detailed explanation]
- **Evidence:** [Exact quote or field]
- **Location:** [Where in document]
- **Required Action:** [What to fix]

[Continue for all critical violations]

---

## MAJOR VIOLATIONS

[Same format as critical]

---

## MINOR VIOLATIONS

[Same format]

---

## POSITIVE COMPLIANCE POINTS

✅ **[RULE_ID]:** [What was done correctly]

[List all compliant rules]

---

## RECOMMENDATIONS

### Immediate Actions Required:
1. [Action]
2. [Action]
...

### If Retail Document:
[Specific retail actions]

### Document Quality:
[General improvements]

---

## COMPLIANCE SCORE

**Critical Issues:** [count]
**Major Issues:** [count]
**Minor Issues:** [count]

**Overall Assessment:** **COMPLIANT** or **NON-COMPLIANT - REQUIRES REVISION**

[Final verdict paragraph]

---

Make the report detailed, professional, and actionable. Use emojis sparingly (✅ for compliant, 🚨 for critical).
"""

        return self._call_llm(prompt, max_tokens=19500)
    
    def analyze(self, document_path: str, rules_path: str, metadata_path: str = None) -> str:
        """
        Main analysis orchestrator - follows the exact hybrid approach
        """
        print("=" * 80)
        print("COMPLIANCE ANALYSIS TOOL - Hybrid Approach (Token Factory)")
        print("=" * 80)
        
        # Load files
        print("\n📂 Loading files...")
        document = self.load_json(document_path)
        rules = self.load_json(rules_path)
        print(f"✓ Loaded document: {document_path}")
        print(f"✓ Loaded rules: {rules_path}")
        
        # Load and merge metadata if provided
        if metadata_path:
            metadata = self.load_json(metadata_path)
            print(f"✓ Loaded metadata: {metadata_path}")
            
            # Merge metadata into document
            if 'document_metadata' not in document:
                document['document_metadata'] = {}
            
            # Map metadata fields to document_metadata
            if "Le document fait-il référence à un nouveau Produit" in metadata:
                document['document_metadata']['fund_status'] = 'pre-commercialisation' if metadata["Le document fait-il référence à un nouveau Produit"] else 'active'
            
            if "Le client est-il un professionnel" in metadata:
                document['document_metadata']['client_type'] = 'professional' if metadata["Le client est-il un professionnel"] else 'retail'
            
            # Add other metadata fields
            document['document_metadata']['management_company'] = metadata.get("Société de Gestion", "")
            document['document_metadata']['is_oddo_sicav'] = metadata.get("Est ce que le produit fait partie de la Sicav d'Oddo", False)
            document['document_metadata']['is_new_strategy'] = metadata.get("Le document fait-il référence à une nouvelle Stratégie", False)
            document['document_metadata']['is_new_product'] = metadata.get("Le document fait-il référence à un nouveau Produit", False)
            
            print(f"✓ Merged metadata into document")
        
        # Phase 1: Initial Scan
        print("\n" + "=" * 80)
        print("PHASE 1: Initial Document Scan (Rapid Assessment)")
        print("=" * 80)
        phase1 = self.phase1_document_scan(document)
        print(f"✓ Document type: {phase1.get('document_type', 'unknown')}")
        print(f"✓ Client type: {phase1.get('client_type', 'unknown')}")
        if phase1.get('critical_empty_fields'):
            print(f"🚨 Empty critical fields: {', '.join(phase1['critical_empty_fields'])}")
        
        # Phase 2: Categorize Rules
        print("\n" + "=" * 80)
        print("PHASE 2: Rules Categorization (Mental Mapping)")
        print("=" * 80)
        phase2 = self.phase2_categorize_rules(rules)
        print(f"✓ Categorized {len(rules.get('rules', []))} rules into 5 types")
        
        # Phase 3: Prioritize
        print("\n" + "=" * 80)
        print("PHASE 3: Critical Rules First (Priority-Based)")
        print("=" * 80)
        phase3 = self.phase3_prioritize_rules(rules, phase1)
        print(f"✓ Tier 1 (Blocking): {len(phase3.get('tier1_blocking', []))} rules")
        print(f"✓ Tier 2 (Major): {len(phase3.get('tier2_major', []))} rules")
        print(f"✓ Tier 3 (Quality): {len(phase3.get('tier3_quality', []))} rules")
        
        # Phase 4: Check Rules in Parallel
        print("\n" + "=" * 80)
        print("PHASE 4: Parallel Pattern Matching")
        print("=" * 80)
        violations = self.phase4_check_rules_parallel(document, rules, phase3)
        print(f"\n✓ Found {len(violations['critical'])} critical violations")
        print(f"✓ Found {len(violations['major'])} major violations")
        print(f"✓ Found {len(violations['minor'])} minor violations")
        
        # Phase 5: Cross-Reference
        print("\n" + "=" * 80)
        print("PHASE 5: Cross-Reference Validation")
        print("=" * 80)
        cross_ref = self.phase5_cross_reference(document, violations)
        print(f"✓ Found {len(cross_ref)} consistency issues")
        
        # Phase 6: Generate Report
        print("\n" + "=" * 80)
        print("PHASE 6: Evidence Collection & Report Generation")
        print("=" * 80)
        report = self.phase6_generate_report(document, rules, phase1, violations, cross_ref)
        print("✓ Report generated")
        
        return report


def generate_general_violation_annotations(report, document, rules):
    """
    Generate a JSON file with violation annotations for highlighting in the document.
    Parses the markdown report to extract violations with locations and details.
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
    
    # Parse the markdown report to extract violations
    # Look for violation sections (CRITICAL, MAJOR, MINOR)
    
    # Split by rule sections - look for patterns like "**RULE_ID:**" or "### RULE_ID"
    rule_sections = re.split(r'(?=(?:\*\*|###)\s*[A-Z_]+_\d+)', report)
    
    for section in rule_sections:
        if not section.strip():
            continue
        
        # Extract rule ID
        rule_match = re.search(r'([A-Z_]+_\d+)', section)
        if not rule_match:
            continue
        
        rule_id = rule_match.group(1)
        
        # Check if it's a violation (not in positive compliance section)
        if 'POSITIVE COMPLIANCE' in section or '✅' in section.split(rule_id)[0]:
            continue
        
        # Check if this is actually a violation
        is_violation = any(keyword in section.lower() for keyword in ['violation', 'non-compliant', 'missing', 'absent', 'incorrect'])
        
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
        location_match = re.search(r'(?:Location|Found in|Section)[:\s]+([^\n]+)', section, re.IGNORECASE)
        if location_match:
            location = location_match.group(1).strip()
        
        # Extract evidence/quote
        evidence = ''
        evidence_match = re.search(r'(?:Evidence|Quote|Found)[:\s]+["\']?([^"\'\n]+)["\']?', section, re.IGNORECASE)
        if evidence_match:
            evidence = evidence_match.group(1).strip()
        
        # Extract issue description
        issue = ''
        issue_match = re.search(r'(?:Issue|Problem|Violation)[:\s]+([^\n]+)', section, re.IGNORECASE)
        if issue_match:
            issue = issue_match.group(1).strip()
        
        # Extract required action
        action = ''
        action_match = re.search(r'(?:Required Action|Action|Fix)[:\s]+([^\n]+)', section, re.IGNORECASE)
        if action_match:
            action = action_match.group(1).strip()
        
        # Get slide number from location
        slide_number = get_slide_number_from_location(location, document)
        
        # Get rule details from rules JSON
        rule_details = get_rule_details_general(rule_id, rules)
        
        annotation = {
            "rule_id": rule_id,
            "severity": severity,
            "location": location,
            "page_number": slide_number,
            "exact_phrase": evidence,
            "character_count": len(evidence),
            "violation_comment": f"[{rule_id}] {issue if issue else rule_details.get('description', 'Violation detected')}",
            "required_action": action if action else rule_details.get('required_action', 'Review and correct violation')
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
    
    location_map = {
        'page_de_garde': 'page_de_garde',
        'slide_2': 'slide_2',
        'page_de_fin': 'page_de_fin',
        'metadata': 'document_metadata'
    }
    
    location_lower = location_string.lower().strip()
    
    for key, section_name in location_map.items():
        if key in location_lower:
            if section_name in document:
                return document[section_name].get('slide_number')
    
    if 'pages_suivantes' in document:
        for page in document['pages_suivantes']:
            slide_num = page.get('slide_number')
            if f'slide_{slide_num}' in location_lower or f'slide {slide_num}' in location_lower:
                return slide_num
    
    match = re.search(r'(?:slide|page)[_\s]?(\d+)', location_lower)
    if match:
        return int(match.group(1))
    
    return None

def get_rule_details_general(rule_id, rules):
    """Get rule details from the rules JSON."""
    for rule in rules.get('rules', []):
        if rule.get('rule_id') == rule_id:
            return {
                'description': rule.get('description', ''),
                'required_action': rule.get('remediation', 'Review and correct violation')
            }
    return {'description': '', 'required_action': 'Review and correct violation'}

def main():
    """Main entry point."""
    if len(sys.argv) < 3 or len(sys.argv) > 4:
        print("Usage: python test_general_rules.py <document.json> <rules.json> [metadata.json]")
        print("Example: python test_general_rules.py exemple.json general_rules.json")
        print("Example with metadata: python test_general_rules.py exemple.json general_rules.json metadata.json")
        sys.exit(1)
    
    document_path = sys.argv[1]
    rules_path = sys.argv[2]
    metadata_path = sys.argv[3] if len(sys.argv) == 4 else None
    
    # Check if API key is set
    if not os.environ.get('TOKEN_FACTORY_API_KEY'):
        print("ERROR: TOKEN_FACTORY_API_KEY not found in .env file")
        print("Please create a .env file with: TOKEN_FACTORY_API_KEY=your-api-key")
        sys.exit(1)
    
    try:
        analyzer = ComplianceAnalyzer()
        
        # Load document and rules for annotations
        document = analyzer.load_json(document_path)
        rules = analyzer.load_json(rules_path)
        
        report = analyzer.analyze(document_path, rules_path, metadata_path)
        
        # Print report
        print("\n" + "=" * 80)
        print("FINAL COMPLIANCE REPORT")
        print("=" * 80)
        print(report)
        
        # Save report to file (use basename to avoid path issues)
        from pathlib import Path
        doc_basename = Path(document_path).stem  # Get filename without extension
        output_file = f"compliance_report_{doc_basename}.md"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"\n✓ Report saved to: {output_file}")
        
        # Generate violation annotations JSON for highlighting
        annotations = generate_general_violation_annotations(report, document, rules)
        annotations_file = "general_violation_annotations.json"
        with open(annotations_file, 'w', encoding='utf-8') as f:
            json.dump(annotations, f, indent=2, ensure_ascii=False)
        print(f"💾 Violation annotations saved to: {annotations_file}")
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()