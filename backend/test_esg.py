#!/usr/bin/env python3
"""
ESG Compliance Analyzer
Replicates the exact constraint-based reasoning approach for ESG document validation.
Uses LLM with automatic fallback (TokenFactory -> Gemini)

Usage: python test.py exemple.json esg_rules.json
"""

import json
import sys
import os
from dotenv import load_dotenv

# Import path utilities
from path_utils import ENV_FILE, ensure_directories

# Import LLM Manager with fallback support
from llm_manager import llm_manager

# Load environment variables from .env file
load_dotenv(str(ENV_FILE))

def load_json(filepath):
    """Load and parse JSON file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {filepath}: {e}")
        sys.exit(1)

def call_llm(system_prompt, user_prompt, max_tokens=2000):
    """
    Call LLM with automatic fallback (TokenFactory -> Gemini).
    Returns parsed JSON response.
    """
    try:
        content = llm_manager.call_llm(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=0.3,
            max_tokens=max_tokens
        )
        
        if not content:
            raise Exception(f"LLM call failed: {llm_manager.last_error}")
        
        content = content.strip()
        
        # Clean up markdown code blocks if present
        content = content.replace("```json", "").replace("```", "").strip()
        
        # Parse JSON
        return json.loads(content)
    
    except json.JSONDecodeError as e:
        print(f"⚠️  JSON parsing error: {e}")
        print(f"Raw response: {content[:500]}...")
        raise
    except Exception as e:
        print(f"❌ API call error: {e}")
        raise

def phase_1_document_understanding(document):
    """
    Phase 1: Initial document scan to identify critical metadata and ESG content.
    Returns: Initial findings and red flags
    """
    print("\n" + "="*80)
    print("PHASE 1: DOCUMENT UNDERSTANDING")
    print("="*80)
    
    system_prompt = "You are an expert compliance analyst conducting initial document assessment. You provide precise, structured JSON responses following exact specifications."
    
    user_prompt = f"""You are conducting Phase 1 analysis: Initial Document Understanding.

DOCUMENT METADATA:
{json.dumps(document.get('document_metadata', {}), indent=2)}

TASK: Perform a quick initial scan following these steps:

1. **Metadata Analysis** - Identify RED FLAGS:
   - Is client_type specified? (empty = RED FLAG)
   - Is fund_esg_classification clear and singular? (ambiguous = RED FLAG)
   - Document type and target audience

2. **Quick Content Scan** - Look for ESG content presence:
   - Scan all slides for ESG-related keywords: ESG, SFDR, Article 6/8/9, sustainability, environmental, social, governance
   - Note which slides contain ESG content
   - Do NOT do deep analysis yet, just flag presence/absence

FULL DOCUMENT FOR SCANNING:
{json.dumps(document, indent=2)[:15000]}

OUTPUT FORMAT (JSON ONLY, NO OTHER TEXT):
{{
  "red_flags": [
    {{"issue": "description", "severity": "high/medium/low"}}
  ],
  "esg_content_found": {{
    "has_esg_content": true,
    "locations": ["slide_1", "slide_5"],
    "keywords_found": ["ESG", "SFDR"]
  }},
  "metadata_summary": {{
    "client_type": "value or MISSING",
    "esg_classification": "value or AMBIGUOUS",
    "document_type": "value"
  }},
  "mental_notes": ["key observations for next phase"]
}}

Respond with ONLY valid JSON, no preamble or explanation."""

    result = call_llm(system_prompt, user_prompt, max_tokens=2000)
    
    print("\n📋 Metadata Summary:")
    for key, value in result['metadata_summary'].items():
        print(f"   • {key}: {value}")
    
    print("\n🚩 Red Flags Identified:")
    for flag in result['red_flags']:
        print(f"   • [{flag['severity'].upper()}] {flag['issue']}")
    
    print("\n🔍 ESG Content Scan:")
    print(f"   • Has ESG Content: {result['esg_content_found']['has_esg_content']}")
    print(f"   • Locations: {', '.join(result['esg_content_found']['locations'])}")
    if result['esg_content_found']['keywords_found']:
        print(f"   • Keywords: {', '.join(result['esg_content_found']['keywords_found'][:5])}...")
    
    return result

def phase_2_rules_framework(rules):
    """
    Phase 2: Understand the rules structure and build decision tree.
    Returns: Rule hierarchy and decision logic
    """
    print("\n" + "="*80)
    print("PHASE 2: RULES FRAMEWORK LOADING")
    print("="*80)
    
    system_prompt = "You are an expert compliance analyst specializing in regulatory framework analysis. You provide precise, structured JSON responses."
    
    user_prompt = f"""You are conducting Phase 2 analysis: Rules Framework Understanding.

ESG RULES DOCUMENT:
{json.dumps(rules, indent=2)[:15000]}

TASK: Analyze the rules structure and build the decision tree logic:

1. **Identify Rule Hierarchy**:
   - Which rule is FOUNDATIONAL (must be checked first)?
   - Which rule is SCOPE-defining (professional vs retail)?
   - Which rules are CONDITIONAL (depend on classification)?

2. **Build Decision Tree**:
   - Map out the logical dependencies between rules
   - Identify which rules apply under which scenarios

3. **Identify Critical Paths**:
   - What's the order of analysis?
   - Which rules can short-circuit the analysis?

OUTPUT FORMAT (JSON ONLY, NO OTHER TEXT):
{{
  "foundational_rule": {{
    "rule_id": "ESG_001",
    "rule_name": "name",
    "why_first": "explanation",
    "severity": "critical"
  }},
  "scope_rule": {{
    "rule_id": "ESG_006",
    "determines": "what it determines",
    "exemptions": ["who is exempt"]
  }},
  "conditional_rules": [
    {{
      "rule_id": "ESG_002",
      "applies_when": "condition",
      "restriction": "what it restricts"
    }}
  ],
  "decision_tree": {{
    "step_1": "Check ESG_001 first because...",
    "step_2": "Then check ESG_006 because...",
    "step_3": "Build scenarios based on classification"
  }},
  "rule_dependencies": "explanation of dependencies"
}}

Respond with ONLY valid JSON, no preamble or explanation."""

    result = call_llm(system_prompt, user_prompt, max_tokens=2000)
    
    print("\n🎯 Foundational Rule:")
    print(f"   • {result['foundational_rule']['rule_id']}: {result['foundational_rule']['rule_name']}")
    print(f"   • Why First: {result['foundational_rule']['why_first']}")
    
    print("\n🔍 Scope Rule:")
    print(f"   • {result['scope_rule']['rule_id']}: {result['scope_rule']['determines']}")
    
    print("\n📊 Conditional Rules:")
    for rule in result['conditional_rules']:
        print(f"   • {rule['rule_id']}: Applies when {rule['applies_when']}")
    
    print("\n🌳 Decision Tree:")
    for step, description in result['decision_tree'].items():
        print(f"   • {step}: {description}")
    
    return result

def phase_3_critical_path_analysis(document, rules, phase1_result, phase2_result):
    """
    Phase 3: Apply critical path analysis using constraint-based reasoning.
    Returns: Violations found with scenario-based analysis
    """
    print("\n" + "="*80)
    print("PHASE 3: CRITICAL PATH ANALYSIS (Constraint-Based Reasoning)")
    print("="*80)
    
    system_prompt = "You are an expert compliance analyst conducting critical path analysis. You apply constraint-based reasoning and provide precise JSON responses with calculations."
    
    user_prompt = f"""You are conducting Phase 3: Critical Path Analysis using constraint-based reasoning.

PHASE 1 FINDINGS:
{json.dumps(phase1_result, indent=2)}

PHASE 2 FRAMEWORK:
{json.dumps(phase2_result, indent=2)}

DOCUMENT (TRUNCATED):
{json.dumps(document, indent=2)[:10000]}

RULES (KEY SECTIONS):
- ESG_001: Classification requirement (CRITICAL)
- ESG_006: Professional funds exempt
- ESG_002: Engaging = unlimited ESG (≥20% exclusion, ≥90% coverage)
- ESG_003: Reduced = <10% ESG content by volume
- ESG_004: Prospectus-Limited = NO ESG in retail docs
- ESG_005: Other = Only baseline exclusions

TASK: Apply constraint-based reasoning:

**STEP 1: Apply ESG_001 First**
- Check if classification is known and valid
- If missing/ambiguous: IMMEDIATE VIOLATION

**STEP 2: Apply ESG_006 Second**
- Check client_type
- If empty: assume RETAIL (more restrictive)

**STEP 3: Scenario Analysis**
Build three scenarios:

SCENARIO A: IF "Prospectus-Limited" OR "Other"
  - Search for ANY ESG keywords (ESG, SFDR, Article 8/9, sustainability, environmental, social, governance)
  - If found: CRITICAL VIOLATION

SCENARIO B: IF "Reduced"
  - Calculate ESG content volume
  - Count ESG-related characters vs total
  - If ≥10%: MAJOR VIOLATION

SCENARIO C: IF "Engaging"
  - No restrictions
  - COMPLIANT

OUTPUT FORMAT (JSON ONLY):
{{
  "step_1_foundational": {{
    "rule_id": "ESG_001",
    "classification_stated": "what document says",
    "is_valid": false,
    "violation": {{
      "found": true,
      "severity": "critical",
      "reason": "explanation"
    }}
  }},
  "step_2_scope": {{
    "rule_id": "ESG_006",
    "client_type": "UNKNOWN",
    "assumption": "assumed retail",
    "rules_apply": true
  }},
  "step_3_scenarios": {{
    "scenario_a_prospectus_limited": {{
      "applicable": "if fund is this classification",
      "esg_content_search": {{
        "method": "keyword matching",
        "keywords_searched": ["ESG", "SFDR", "Article 8", "Article 9"],
        "matches_found": ["slide_1: SFDR explanation", "slide_5: ESG risks"],
        "violation": {{
          "found": true,
          "severity": "critical",
          "rules_violated": ["ESG_004"]
        }}
      }}
    }},
    "scenario_b_reduced": {{
      "applicable": "if fund is this classification",
      "volume_calculation": {{
        "esg_content_chars": 550,
        "total_document_chars": 9000,
        "percentage": 6.1,
        "threshold": "10%",
        "exceeds_threshold": false,
        "violation": {{
          "found": false,
          "severity": "major",
          "rule_violated": "ESG_003"
        }}
      }}
    }},
    "scenario_c_engaging": {{
      "applicable": "if fund is this classification",
      "restrictions": "none",
      "compliant": true
    }}
  }},
  "overall_assessment": "summary"
}}

Respond with ONLY valid JSON."""

    result = call_llm(system_prompt, user_prompt, max_tokens=4000)
    
    print("\n📍 STEP 1: Foundational Rule (ESG_001)")
    print(f"   • Classification Stated: {result['step_1_foundational']['classification_stated']}")
    print(f"   • Valid: {result['step_1_foundational']['is_valid']}")
    if result['step_1_foundational']['violation']['found']:
        print(f"   • ❌ VIOLATION: {result['step_1_foundational']['violation']['reason']}")
    
    print("\n📍 STEP 2: Scope Rule (ESG_006)")
    print(f"   • Client Type: {result['step_2_scope']['client_type']}")
    print(f"   • Rules Apply: {result['step_2_scope']['rules_apply']}")
    
    print("\n📍 STEP 3: Scenario Analysis")
    
    for scenario_key, scenario_data in result['step_3_scenarios'].items():
        scenario_name = scenario_key.replace('_', ' ').title()
        print(f"\n   🔹 {scenario_name}")
        print(f"      Applicable: {scenario_data['applicable']}")
        
        if 'esg_content_search' in scenario_data:
            search = scenario_data['esg_content_search']
            print(f"      Matches Found: {len(search.get('matches_found', []))}")
            if search['violation']['found']:
                print(f"      ❌ VIOLATION: {search['violation']['severity'].upper()}")
        
        if 'volume_calculation' in scenario_data:
            calc = scenario_data['volume_calculation']
            print(f"      ESG Content: {calc['esg_content_chars']} chars")
            print(f"      Total Document: {calc['total_document_chars']} chars")
            print(f"      Percentage: {calc['percentage']:.1f}%")
            if calc['violation']['found']:
                print(f"      ❌ VIOLATION: {calc['violation']['severity'].upper()}")
        
        if scenario_data.get('compliant'):
            print(f"      ✅ COMPLIANT")
    
    return result

def phase_4_targeted_content_search(document, phase3_result):
    """
    Phase 4: Deep targeted search for specific violations.
    Returns: Detailed violation evidence
    """
    print("\n" + "="*80)
    print("PHASE 4: TARGETED CONTENT SEARCH")
    print("="*80)
    
    system_prompt = "You are an expert compliance analyst extracting violation evidence. You provide precise quotes and measurements in JSON format."
    
    user_prompt = f"""You are conducting Phase 4: Targeted Content Search.

PHASE 3 FINDINGS:
{json.dumps(phase3_result, indent=2)}

DOCUMENT (FULL):
{json.dumps(document, indent=2)[:12000]}

TASK: Extract exact violation evidence:

1. **For each violation in Phase 3**: Extract EXACT text from document
2. **Keyword Matching**: Find all ESG keyword occurrences
3. **Character Counting**: Measure ESG vs total content

OUTPUT FORMAT (JSON ONLY):
{{
  "violations_with_evidence": [
    {{
      "rule_id": "ESG_001",
      "severity": "critical",
      "location": "metadata",
      "quoted_text": "exact text",
      "character_count": 50,
      "explanation": "why this violates"
    }}
  ],
  "keyword_occurrences": [
    {{
      "keyword": "SFDR",
      "location": "slide_1",
      "context": "surrounding text"
    }}
  ],
  "volume_analysis": {{
    "esg_text_blocks": [
      {{
        "location": "slide_1",
        "text": "SFDR explanation text...",
        "char_count": 450
      }}
    ],
    "total_esg_chars": 550,
    "total_document_chars": 9000,
    "percentage": 6.1
  }}
}}

Respond with ONLY valid JSON."""

    result = call_llm(system_prompt, user_prompt, max_tokens=4000)
    
    print("\n🎯 Violations with Evidence:")
    for v in result['violations_with_evidence']:
        print(f"\n   ❌ {v['rule_id']} [{v['severity'].upper()}]")
        print(f"      Location: {v['location']}")
        print(f"      Quote: \"{v['quoted_text'][:100]}...\"")
        print(f"      Explanation: {v['explanation']}")
    
    if result.get('volume_analysis'):
        va = result['volume_analysis']
        print(f"\n📊 Volume Analysis:")
        print(f"   • Total ESG Characters: {va['total_esg_chars']}")
        print(f"   • Total Document Characters: {va['total_document_chars']}")
        print(f"   • Percentage: {va['percentage']:.2f}%")
    
    return result

def generate_final_report(document, rules, phase1, phase2, phase3, phase4):
    """
    Generate comprehensive compliance report with actionable recommendations.
    """
    print("\n" + "="*80)
    print("GENERATING FINAL COMPLIANCE REPORT")
    print("="*80)
    
    system_prompt = "You are an expert compliance analyst generating comprehensive final reports. You provide actionable recommendations in structured JSON format."
    
    user_prompt = f"""Generate final comprehensive compliance report.

ALL PHASE RESULTS:
Phase 1: {json.dumps(phase1, indent=2)}
Phase 2: {json.dumps(phase2, indent=2)}
Phase 3: {json.dumps(phase3, indent=2)}
Phase 4: {json.dumps(phase4, indent=2)}

TASK: Generate comprehensive report with:

1. Executive Summary
2. Document Information
3. Critical Findings
4. Violations Summary Table
5. Required Actions
6. Final Recommendation

OUTPUT FORMAT (JSON ONLY):
{{
  "executive_summary": "brief overview",
  "document_info": {{
    "name": "ODDO BHF US Equity Active UCITS ETF",
    "type": "fund_presentation",
    "esg_classification": "Article 6, Article 8, Article 9",
    "client_type": "MISSING"
  }},
  "critical_findings": [
    {{"issue": "Missing ESG classification", "impact": "Cannot validate compliance"}}
  ],
  "violations_table": [
    {{
      "rule_id": "ESG_001",
      "rule_name": "ESG Fund Classification Requirement",
      "severity": "critical",
      "status": "VIOLATED",
      "condition": "Classification ambiguous/missing"
    }}
  ],
  "scenario_results": {{
    "prospectus_limited": {{"status": "CRITICAL_VIOLATIONS", "violations": ["ESG content found"]}},
    "reduced": {{"status": "COMPLIANT", "violations": []}},
    "engaging": {{"status": "COMPLIANT", "violations": []}}
  }},
  "required_actions": {{
    "immediate": ["Retrieve ESG classification from ESG Mapping", "Clarify client type"],
    "if_retail_prospectus_limited": ["Remove all ESG content"],
    "if_retail_reduced": ["Verify 10% threshold not exceeded"],
    "if_retail_engaging": ["Approve document"],
    "if_professional": ["Approve - rules don't apply"]
  }},
  "final_recommendation": {{
    "status": "CANNOT_APPROVE",
    "risk_level": "HIGH",
    "next_steps": ["Confirm classification", "Re-evaluate based on confirmed data"],
    "justification": "Missing critical classification information"
  }}
}}

Respond with ONLY valid JSON."""

    result = call_llm(system_prompt, user_prompt, max_tokens=3000)
    
    # Print formatted report
    print("\n" + "="*80)
    print("FINAL COMPLIANCE REPORT")
    print("="*80)
    
    print("\n📋 EXECUTIVE SUMMARY")
    print(f"   {result['executive_summary']}")
    
    print("\n📄 DOCUMENT INFORMATION")
    for key, value in result['document_info'].items():
        print(f"   • {key.replace('_', ' ').title()}: {value}")
    
    print("\n🚨 CRITICAL FINDINGS")
    for finding in result['critical_findings']:
        print(f"   • {finding['issue']}")
        print(f"     Impact: {finding['impact']}")
    
    print("\n📊 VIOLATIONS SUMMARY")
    print(f"   {'Rule ID':<12} {'Rule Name':<40} {'Severity':<10} {'Status':<15}")
    print(f"   {'-'*12} {'-'*40} {'-'*10} {'-'*15}")
    for v in result['violations_table']:
        status_symbol = "❌" if "VIOLATED" in v['status'] else "⚠️" if "POTENTIAL" in v['status'] else "✅"
        print(f"   {v['rule_id']:<12} {v['rule_name'][:38]:<40} {v['severity']:<10} {status_symbol} {v['status']:<13}")
    
    print("\n🎯 REQUIRED ACTIONS")
    print("\n   IMMEDIATE:")
    for action in result['required_actions']['immediate']:
        print(f"   ✅ {action}")
    
    for key, actions in result['required_actions'].items():
        if key != 'immediate' and actions:
            print(f"\n   {key.replace('_', ' ').upper()}:")
            for action in actions:
                print(f"   • {action}")
    
    print("\n🏁 FINAL RECOMMENDATION")
    print(f"   Status: {result['final_recommendation']['status']}")
    print(f"   Risk Level: {result['final_recommendation']['risk_level']}")
    print(f"   Justification: {result['final_recommendation']['justification']}")
    print("\n   Next Steps:")
    for i, step in enumerate(result['final_recommendation']['next_steps'], 1):
        print(f"   {i}. {step}")
    
    return result

def generate_violation_annotations(phase4_result, final_report, document):
    """
    Generate a JSON file with violation annotations for highlighting in the document.
    Each annotation includes: location, page, exact phrase, violation rule, and comment.
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
    
    # Extract violations from phase4 evidence
    violations_with_evidence = phase4_result.get('violations_with_evidence', [])
    
    for violation in violations_with_evidence:
        location = violation.get('location', 'unknown')
        annotation = {
            "rule_id": violation.get('rule_id', 'UNKNOWN'),
            "severity": violation.get('severity', 'unknown'),
            "location": location,
            "page_number": get_slide_number_from_document(location, document),
            "exact_phrase": violation.get('quoted_text', ''),
            "character_count": violation.get('character_count', 0),
            "violation_comment": f"[{violation.get('rule_id', 'UNKNOWN')}] {violation.get('explanation', 'Violation detected')}",
            "required_action": get_required_action_for_rule(violation.get('rule_id', ''), final_report)
        }
        
        annotations["document_annotations"].append(annotation)
        
        # Update summary counts
        annotations["summary"]["total_violations"] += 1
        if violation.get('severity') == 'critical':
            annotations["summary"]["critical_violations"] += 1
        elif violation.get('severity') == 'major':
            annotations["summary"]["major_violations"] += 1
        elif violation.get('severity') == 'minor':
            annotations["summary"]["minor_violations"] += 1
    
    # Add keyword occurrences as potential violations
    keyword_occurrences = phase4_result.get('keyword_occurrences', [])
    for keyword in keyword_occurrences:
        location = keyword.get('location', 'unknown')
        annotation = {
            "rule_id": "ESG_CONTENT_DETECTED",
            "severity": "warning",
            "location": location,
            "page_number": get_slide_number_from_document(location, document),
            "exact_phrase": keyword.get('context', keyword.get('keyword', '')),
            "character_count": len(keyword.get('context', '')),
            "violation_comment": f"ESG keyword '{keyword.get('keyword', '')}' detected - May violate ESG content restrictions depending on fund classification",
            "required_action": "Review if this ESG content is allowed based on fund classification"
        }
        
        annotations["document_annotations"].append(annotation)
    
    # Add volume analysis blocks if ESG content exceeds threshold
    volume_analysis = phase4_result.get('volume_analysis', {})
    if volume_analysis:
        for block in volume_analysis.get('esg_text_blocks', []):
            location = block.get('location', 'unknown')
            annotation = {
                "rule_id": "ESG_003",
                "severity": "major",
                "location": location,
                "page_number": get_slide_number_from_document(location, document),
                "exact_phrase": block.get('text', '')[:200] + "..." if len(block.get('text', '')) > 200 else block.get('text', ''),
                "character_count": block.get('char_count', 0),
                "violation_comment": f"[ESG_003] ESG content block ({block.get('char_count', 0)} chars) - Contributes to total ESG volume of {volume_analysis.get('percentage', 0):.1f}%",
                "required_action": "Reduce ESG content if total exceeds 10% threshold for 'Reduced' classification"
            }
            
            annotations["document_annotations"].append(annotation)
    
    return annotations

def get_slide_number_from_document(location_string, document):
    """
    Get the actual slide number from the document structure based on location string.
    Maps location names like 'page_de_garde', 'slide_2', etc. to actual slide numbers.
    """
    import re
    
    # Direct mapping for known sections
    location_map = {
        'page_de_garde': 'page_de_garde',
        'slide_2': 'slide_2',
        'slide_3': 'slide_3',
        'slide_4': 'slide_4',
        'slide_5': 'slide_5',
        'page_de_fin': 'page_de_fin',
        'metadata': 'document_metadata'
    }
    
    # Normalize location string
    location_lower = location_string.lower().strip()
    
    # Try direct mapping first
    for key, section_name in location_map.items():
        if key in location_lower:
            # Get slide number from document
            if section_name in document:
                return document[section_name].get('slide_number')
    
    # Check in pages_suivantes array
    if 'pages_suivantes' in document:
        for page in document['pages_suivantes']:
            slide_num = page.get('slide_number')
            if f'slide_{slide_num}' in location_lower or f'slide {slide_num}' in location_lower:
                return slide_num
    
    # Try to extract slide number from pattern like "slide_3" or "slide 3"
    match = re.search(r'(?:slide|page)[_\s]?(\d+)', location_lower)
    if match:
        return int(match.group(1))
    
    # Try to extract any number
    match = re.search(r'(\d+)', location_string)
    if match:
        return int(match.group(1))
    
    return None

def get_required_action_for_rule(rule_id, final_report):
    """Get the required action for a specific rule from the final report."""
    violations_table = final_report.get('violations_table', [])
    for violation in violations_table:
        if violation.get('rule_id') == rule_id:
            return violation.get('required_action', 'Review and correct violation')
    
    # Default actions based on rule ID
    rule_actions = {
        'ESG_001': 'Specify clear ESG classification in document metadata',
        'ESG_002': 'Ensure ESG content meets Engaging criteria (≥20% exclusion, ≥90% coverage)',
        'ESG_003': 'Reduce ESG content to less than 10% of total document volume',
        'ESG_004': 'Remove all ESG content from retail document (Prospectus-Limited)',
        'ESG_005': 'Limit ESG content to baseline exclusions only',
        'ESG_006': 'Clarify if document is for professional or retail clients'
    }
    
    return rule_actions.get(rule_id, 'Review and correct violation')

def format_text_report(final_report, phase1, phase2, phase3, phase4):
    """Format the analysis results into a human-readable text report."""
    report = []
    
    # Executive Summary
    report.append("EXECUTIVE SUMMARY")
    report.append("="*80)
    report.append(final_report.get('executive_summary', 'N/A'))
    report.append("\n")
    
    # Document Information
    report.append("DOCUMENT INFORMATION")
    report.append("="*80)
    doc_info = final_report.get('document_info', {})
    for key, value in doc_info.items():
        report.append(f"• {key.replace('_', ' ').title()}: {value}")
    report.append("\n")
    
    # Critical Findings
    report.append("CRITICAL FINDINGS")
    report.append("="*80)
    for finding in final_report.get('critical_findings', []):
        report.append(f"• {finding.get('issue', 'N/A')}")
        report.append(f"  Impact: {finding.get('impact', 'N/A')}")
    report.append("\n")
    
    # Violations Summary Table
    report.append("VIOLATIONS SUMMARY")
    report.append("="*80)
    report.append(f"{'Rule ID':<12} {'Rule Name':<40} {'Severity':<10} {'Status':<15}")
    report.append(f"{'-'*12} {'-'*40} {'-'*10} {'-'*15}")
    for v in final_report.get('violations_table', []):
        status_symbol = "❌" if "VIOLATED" in v.get('status', '') else "⚠️" if "POTENTIAL" in v.get('status', '') else "✅"
        report.append(f"{v.get('rule_id', 'N/A'):<12} {v.get('rule_name', 'N/A')[:38]:<40} {v.get('severity', 'N/A'):<10} {status_symbol} {v.get('status', 'N/A'):<13}")
    report.append("\n")
    
    # Scenario Results
    report.append("SCENARIO ANALYSIS RESULTS")
    report.append("="*80)
    scenario_results = final_report.get('scenario_results', {})
    for scenario_key, scenario_data in scenario_results.items():
        scenario_name = scenario_key.replace('_', ' ').title()
        report.append(f"\n{scenario_name}:")
        report.append(f"  Status: {scenario_data.get('status', 'N/A')}")
        if scenario_data.get('violations'):
            report.append(f"  Violations:")
            for violation in scenario_data['violations']:
                report.append(f"    - {violation}")
    report.append("\n")
    
    # Required Actions
    report.append("REQUIRED ACTIONS")
    report.append("="*80)
    actions = final_report.get('required_actions', {})
    
    if actions.get('immediate'):
        report.append("\nIMMEDIATE:")
        for action in actions['immediate']:
            report.append(f"  ✅ {action}")
    
    for key, action_list in actions.items():
        if key != 'immediate' and action_list:
            report.append(f"\n{key.replace('_', ' ').upper()}:")
            for action in action_list:
                report.append(f"  • {action}")
    report.append("\n")
    
    # Final Recommendation
    report.append("FINAL RECOMMENDATION")
    report.append("="*80)
    recommendation = final_report.get('final_recommendation', {})
    report.append(f"Status: {recommendation.get('status', 'N/A')}")
    report.append(f"Risk Level: {recommendation.get('risk_level', 'N/A')}")
    report.append(f"Justification: {recommendation.get('justification', 'N/A')}")
    
    if recommendation.get('next_steps'):
        report.append("\nNext Steps:")
        for i, step in enumerate(recommendation['next_steps'], 1):
            report.append(f"  {i}. {step}")
    report.append("\n")
    
    # Phase Details (Optional - for transparency)
    report.append("="*80)
    report.append("DETAILED ANALYSIS PHASES")
    report.append("="*80)
    
    report.append("\nPHASE 1: Document Understanding")
    report.append("-"*80)
    report.append(f"Red Flags: {len(phase1.get('red_flags', []))}")
    report.append(f"ESG Content Found: {phase1.get('esg_content_found', {}).get('has_esg_content', False)}")
    
    report.append("\nPHASE 2: Rules Framework")
    report.append("-"*80)
    report.append(f"Foundational Rule: {phase2.get('foundational_rule', {}).get('rule_id', 'N/A')}")
    report.append(f"Conditional Rules: {len(phase2.get('conditional_rules', []))}")
    
    report.append("\nPHASE 3: Critical Path Analysis")
    report.append("-"*80)
    step1 = phase3.get('step_1_foundational', {})
    report.append(f"Classification Valid: {step1.get('is_valid', 'N/A')}")
    step2 = phase3.get('step_2_scope', {})
    report.append(f"Client Type: {step2.get('client_type', 'N/A')}")
    
    report.append("\nPHASE 4: Targeted Content Search")
    report.append("-"*80)
    report.append(f"Violations with Evidence: {len(phase4.get('violations_with_evidence', []))}")
    if phase4.get('volume_analysis'):
        va = phase4['volume_analysis']
        report.append(f"ESG Content Volume: {va.get('percentage', 0):.2f}%")
    
    return "\n".join(report)

def main():
    """Main execution flow replicating the exact analytical approach."""
    
    if len(sys.argv) < 3 or len(sys.argv) > 4:
        print("Usage: python test_esg.py <document.json> <esg_rules.json> [metadata.json]")
        print("Example: python test_esg.py exemple.json esg_rules.json")
        print("Example with metadata: python test_esg.py exemple.json esg_rules.json metadata.json")
        sys.exit(1)
    
    document_file = sys.argv[1]
    rules_file = sys.argv[2]
    metadata_file = sys.argv[3] if len(sys.argv) == 4 else None
    
    print("="*80)
    print("ESG COMPLIANCE ANALYZER")
    print("Constraint-Based Reasoning Approach")
    print("Using: LLM with automatic fallback (TokenFactory -> Gemini)")
    print("="*80)
    
    # Check available LLM providers
    available_providers = llm_manager.get_available_providers()
    if not available_providers:
        print("\n❌ Error: No LLM API keys found in .env file")
        print("   Please create a .env file with at least one of:")
        print("   TOKENFACTORY_API_KEY=your-api-key")
        print("   GEMINI_API_KEY=your-gemini-api-key")
        sys.exit(1)
    
    print(f"\n📡 Available LLM providers: {', '.join(available_providers)}")
    
    # Load files
    print("\n📂 Loading files...")
    document = load_json(document_file)
    rules = load_json(rules_file)
    print(f"   ✓ Loaded {document_file}")
    print(f"   ✓ Loaded {rules_file}")
    
    # Load and merge metadata if provided
    if metadata_file:
        metadata = load_json(metadata_file)
        print(f"   ✓ Loaded {metadata_file}")
        
        # Merge metadata into document
        if 'document_metadata' not in document:
            document['document_metadata'] = {}
        
        # Map metadata fields to document_metadata
        if "Le document fait-il référence à un nouveau Produit" in metadata:
            document['document_metadata']['fund_status'] = 'pre-commercialisation' if metadata["Le document fait-il référence à un nouveau Produit"] else 'active'
        
        if "Le client est-il un professionnel" in metadata:
            document['document_metadata']['client_type'] = 'professional' if metadata["Le client est-il un professionnel"] else 'retail'
        
        # Add ESG classification if available
        if "Classification ESG du fonds" in metadata:
            document['document_metadata']['fund_esg_classification'] = metadata["Classification ESG du fonds"]
        
        # Add other metadata fields
        document['document_metadata']['management_company'] = metadata.get("Société de Gestion", "")
        document['document_metadata']['is_oddo_sicav'] = metadata.get("Est ce que le produit fait partie de la Sicav d'Oddo", False)
        document['document_metadata']['is_new_strategy'] = metadata.get("Le document fait-il référence à une nouvelle Stratégie", False)
        document['document_metadata']['is_new_product'] = metadata.get("Le document fait-il référence à un nouveau Produit", False)
        
        print(f"   ✓ Merged metadata into document (client_type: {document['document_metadata'].get('client_type', 'N/A')}, ESG classification: {document['document_metadata'].get('fund_esg_classification', 'N/A')})")
    
    # Execute analysis phases
    try:
        phase1_result = phase_1_document_understanding(document)
        phase2_result = phase_2_rules_framework(rules)
        phase3_result = phase_3_critical_path_analysis(document, rules, phase1_result, phase2_result)
        phase4_result = phase_4_targeted_content_search(document, phase3_result)
        final_report = generate_final_report(document, rules, phase1_result, phase2_result, phase3_result, phase4_result)
        
        # Generate formatted text report
        report_text = format_text_report(final_report, phase1_result, phase2_result, phase3_result, phase4_result)
        
        # Save report as text file
        output_file = "esg_validation_report.txt"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("ESG COMPLIANCE VALIDATION REPORT\n")
            f.write("="*80 + "\n\n")
            f.write(f"Generated using TokenFactory API (Llama-3.1-70B-Instruct)\n")
            f.write(f"Document: {document_file}\n")
            f.write(f"Rules: {rules_file}\n")
            if metadata_file:
                f.write(f"Metadata: {metadata_file}\n")
            f.write("="*80 + "\n\n")
            f.write(report_text)
        
        print(f"\n💾 Report saved to: {output_file}")
        
        # Generate violation annotations JSON for highlighting
        annotations = generate_violation_annotations(phase4_result, final_report, document)
        annotations_file = "esg_violation_annotations.json"
        with open(annotations_file, 'w', encoding='utf-8') as f:
            json.dump(annotations, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Violation annotations saved to: {annotations_file}")
        print("\n" + "="*80)
        print("ANALYSIS COMPLETE")
        print("="*80)
        
    except Exception as e:
        print(f"\n❌ Analysis failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()