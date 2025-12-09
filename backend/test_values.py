#!/usr/bin/env python3
"""
Compliance Document Analyzer
Replicates Claude's hybrid analytical approach for regulatory compliance checking
Uses LLM with automatic fallback (TokenFactory -> Gemini)
"""

import json
import sys
import re
from typing import Dict, List, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum
from dotenv import load_dotenv
import os

# Import path utilities
from path_utils import ENV_FILE, ensure_directories

# Import LLM Manager with fallback support
from llm_manager import llm_manager

# Load environment variables from .env file
load_dotenv(str(ENV_FILE))


class Severity(Enum):
    CRITICAL = "critical"
    MAJOR = "major"
    MINOR = "minor"
    INFO = "info"


class ComplianceStatus(Enum):
    PASS = "✅ Pass"
    FAIL = "❌ FAIL"
    CAUTION = "⚠️ Caution"
    NOT_APPLICABLE = "N/A"


@dataclass
class Violation:
    rule_id: str
    rule_name: str
    severity: Severity
    location: str
    violation_text: str
    explanation: str
    remediation: str
    evidence: List[str] = field(default_factory=list)


@dataclass
class ComplianceResult:
    rule_id: str
    rule_name: str
    status: ComplianceStatus
    notes: str = ""
    violations: List[Violation] = field(default_factory=list)


class LLMClient:
    """Wrapper for LLM API with automatic fallback (TokenFactory -> Gemini)"""
    
    def __init__(self, api_key: str = None):
        # Use the global llm_manager with fallback support
        self.llm = llm_manager
    
    def chat(self, system_prompt: str, user_prompt: str, temperature: float = 0.3, max_tokens: int = 2000) -> str:
        """Send a chat completion request with automatic fallback"""
        result = self.llm.call_llm(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=temperature,
            max_tokens=max_tokens
        )
        if result:
            return result
        print(f"❌ Error calling LLM API: {self.llm.last_error}")
        return ""


class ComplianceAnalyzer:
    """
    Main compliance analyzer that replicates Claude's hybrid approach:
    1. Document structure mapping
    2. Rules framework loading
    3. Parallel pattern matching
    4. Rule-by-rule verification
    5. Cross-validation
    6. Structured reporting
    """
    
    def __init__(self, document_path: str, rules_path: str, api_key: str = None):
        self.document_path = document_path
        self.rules_path = rules_path
        self.llm = LLMClient()  # Uses llm_manager with fallback
        
        # Load data
        self.document = self._load_json(document_path)
        self.rules = self._load_json(rules_path)
        
        # Analysis results
        self.violations: List[Violation] = []
        self.compliance_results: List[ComplianceResult] = []
        self.document_text = ""
        
        # Pattern library (Phase 2: Rules Framework Loading)
        self.prohibited_patterns = self._build_prohibited_patterns()
        self.allowed_patterns = self._build_allowed_patterns()
    
    def _load_json(self, path: str) -> Dict:
        """Load JSON file"""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ Error loading {path}: {e}")
            sys.exit(1)
    
    def _build_prohibited_patterns(self) -> Dict[str, List[str]]:
        """Phase 2: Build prohibited patterns library from rules"""
        patterns = {
            'action_verbs': [],
            'valuation_opinions': [],
            'forward_looking': [],
            'opinion_markers': [],
            'preference_language': [],
            'comparative': []
        }
        
        for rule in self.rules.get('rules', []):
            if rule.get('category') == 'prohibition':
                prohibited = rule.get('prohibited_phrases', [])
                
                # Categorize by type
                if 'buy' in prohibited or 'sell' in prohibited:
                    patterns['action_verbs'].extend(prohibited)
                elif 'undervalued' in prohibited or 'overvalued' in prohibited:
                    patterns['valuation_opinions'].extend(prohibited)
                elif 'will grow' in prohibited or 'projected' in prohibited:
                    patterns['forward_looking'].extend(prohibited)
                elif 'in our view' in prohibited or 'we believe' in prohibited:
                    patterns['opinion_markers'].extend(prohibited)
                elif 'prefer' in prohibited or 'better than' in prohibited:
                    patterns['preference_language'].extend(prohibited)
                elif 'compared to' in prohibited or 'versus' in prohibited:
                    patterns['comparative'].extend(prohibited)
        
        return patterns
    
    def _build_allowed_patterns(self) -> List[str]:
        """Phase 2: Build allowed content patterns"""
        allowed = []
        for rule in self.rules.get('rules', []):
            if rule.get('category') == 'allowed':
                allowed.append(rule.get('rule_name', ''))
        return allowed
    
    def analyze(self) -> Dict[str, Any]:
        """
        Main analysis method following the 6-phase hybrid approach
        """
        print("🔍 Starting Compliance Analysis...")
        print("=" * 80)
        
        # Phase 1: Document Structure Mapping
        print("\n📋 Phase 1: Document Structure Mapping...")
        doc_structure = self._phase1_map_document_structure()
        
        # Phase 2: Rules Framework Loading (already done in __init__)
        print("📚 Phase 2: Rules Framework Loading...")
        print(f"   - Loaded {len(self.rules.get('rules', []))} rules")
        print(f"   - Prohibited patterns: {sum(len(v) for v in self.prohibited_patterns.values())}")
        
        # Phase 3: Hybrid Pattern Matching
        print("\n🎯 Phase 3: Parallel Pattern Matching...")
        pattern_violations = self._phase3_pattern_matching()
        
        # Phase 4: Rule-by-Rule Verification
        print("\n✓ Phase 4: Rule-by-Rule Verification...")
        self._phase4_rule_verification()
        
        # Phase 5: Cross-Validation
        print("\n🔄 Phase 5: Cross-Validation...")
        self._phase5_cross_validation()
        
        # Phase 6: Structured Reporting
        print("\n📊 Phase 6: Generating Report...")
        report = self._phase6_generate_report()
        
        return report
    
    def _phase1_map_document_structure(self) -> Dict[str, Any]:
        """Phase 1: Parse and understand document structure"""
        structure = {
            'document_type': self.document.get('document_metadata', {}).get('document_type', 'unknown'),
            'page_count': self.document.get('document_metadata', {}).get('page_count', 0),
            'slides': [],
            'has_disclaimers': False,
            'content_types': set()
        }
        
        # Extract all text content
        all_text = []
        
        # Cover page
        if 'page_de_garde' in self.document:
            slide_content = self._extract_slide_text(self.document['page_de_garde'])
            all_text.append(slide_content)
            structure['slides'].append({
                'number': 1,
                'title': 'Cover',
                'content': slide_content
            })
        
        # Following pages
        for page in self.document.get('pages_suivantes', []):
            slide_content = self._extract_slide_text(page)
            all_text.append(slide_content)
            structure['slides'].append({
                'number': page.get('slide_number'),
                'title': page.get('slide_title', ''),
                'content': slide_content
            })
        
        # End page
        if 'page_de_fin' in self.document:
            slide_content = self._extract_slide_text(self.document['page_de_fin'])
            all_text.append(slide_content)
            structure['slides'].append({
                'number': self.document['page_de_fin'].get('slide_number'),
                'title': 'End',
                'content': slide_content
            })
        
        self.document_text = "\n\n".join(all_text)
        
        # Check for disclaimers
        structure['has_disclaimers'] = any('disclaimer' in text.lower() for text in all_text)
        
        print(f"   - Document type: {structure['document_type']}")
        print(f"   - Pages analyzed: {len(structure['slides'])}")
        print(f"   - Disclaimers present: {structure['has_disclaimers']}")
        
        return structure
    
    def _extract_slide_text(self, slide: Dict) -> str:
        """Extract all text from a slide recursively"""
        text_parts = []
        
        def extract_recursive(obj):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    if key in ['text', 'main_text', 'slide_title']:
                        if value:
                            text_parts.append(str(value))
                    else:
                        extract_recursive(value)
            elif isinstance(obj, list):
                for item in obj:
                    extract_recursive(item)
            elif isinstance(obj, str):
                if obj and len(obj) > 10:  # Ignore very short strings
                    text_parts.append(obj)
        
        extract_recursive(slide)
        return " ".join(text_parts)
    
    def _phase3_pattern_matching(self) -> List[Dict]:
        """
        Phase 3: Parallel pattern matching with context evaluation
        This is the core of Claude's approach - simultaneous pattern recognition
        """
        flagged_items = []
        
        print("   🔎 Scanning for prohibited patterns...")
        
        # Use LLM for intelligent pattern matching
        system_prompt = """You are a regulatory compliance expert specializing in financial document analysis.
Your task is to identify potential violations of securities mention rules in fund presentations.

Focus on detecting:
1. Specific company names or security mentions
2. Favorable/unfavorable opinions about issuers
3. Narrow sector references (groups with few companies)
4. Opinion language ("in our view", "we believe")
5. Action verbs (buy, sell, hold)
6. Valuation opinions (undervalued, overvalued)
7. Forward-looking projections
8. Investment recommendations (direct or indirect)

For each finding, provide:
- Location (slide number)
- Problematic text
- Why it's concerning
- Potential rule violated

Be precise and cite specific text."""

        user_prompt = f"""Analyze this fund presentation document for potential securities mention violations:

DOCUMENT CONTENT:
{self.document_text[:4000]}  # Limit to avoid token issues

PROHIBITED PATTERNS TO WATCH FOR:
- Action verbs: {', '.join(self.prohibited_patterns['action_verbs'][:20])}
- Opinion markers: {', '.join(self.prohibited_patterns['opinion_markers'])}
- Valuation terms: {', '.join(self.prohibited_patterns['valuation_opinions'])}

Identify and list all potential violations with specific evidence."""

        print("   🤖 Consulting LLM for pattern analysis...")
        llm_response = self.llm.chat(system_prompt, user_prompt, temperature=0.2, max_tokens=2000)
        
        if llm_response:
            print(f"   ✓ LLM analysis complete ({len(llm_response)} chars)")
            flagged_items.append({
                'source': 'llm_pattern_matching',
                'findings': llm_response
            })
        
        # Also do regex-based pattern matching for critical terms
        critical_patterns = {
            'magnificent_7': r'\bmagnificent\s+7\b',
            'world_leading': r'\bworld[- ]leading\b',
            'we_believe': r'\bwe\s+believe\b',
            'in_our_view': r'\bin\s+our\s+view\b',
            'recommend': r'\brecommend\b',
            'undervalued': r'\bundervalued\b',
            'overvalued': r'\bovervalued\b',
        }
        
        for pattern_name, pattern in critical_patterns.items():
            matches = re.finditer(pattern, self.document_text, re.IGNORECASE)
            for match in matches:
                context_start = max(0, match.start() - 100)
                context_end = min(len(self.document_text), match.end() + 100)
                context = self.document_text[context_start:context_end]
                
                flagged_items.append({
                    'source': 'regex_pattern',
                    'pattern': pattern_name,
                    'match': match.group(),
                    'context': context
                })
                print(f"   ⚠️  Found pattern: {pattern_name} - '{match.group()}'")
        
        return flagged_items
    
    def _phase4_rule_verification(self):
        """
        Phase 4: Systematic rule-by-rule verification
        Go through each rule as a checklist
        """
        print("   📋 Verifying against each rule...")
        
        for rule in self.rules.get('rules', []):
            rule_id = rule.get('rule_id')
            rule_name = rule.get('rule_name')
            category = rule.get('category')
            
            print(f"   Checking {rule_id}: {rule_name}...")
            
            # Use LLM to verify specific rule
            result = self._verify_single_rule(rule)
            self.compliance_results.append(result)
            
            if result.status == ComplianceStatus.FAIL:
                print(f"      ❌ VIOLATION DETECTED")
    
    def _verify_single_rule(self, rule: Dict) -> ComplianceResult:
        """Verify a single rule against the document using LLM"""
        rule_id = rule.get('rule_id')
        rule_name = rule.get('rule_name')
        rule_text = rule.get('rule_text')
        detailed_desc = rule.get('detailed_description', '')
        violation_examples = rule.get('violation_examples', [])
        prohibited_phrases = rule.get('prohibited_phrases', [])
        
        # Construct focused prompt for this specific rule
        system_prompt = f"""You are verifying compliance with a specific regulatory rule.

RULE: {rule_id} - {rule_name}
REQUIREMENT: {rule_text}

DETAILS: {detailed_desc}

Your task: Determine if the document violates this specific rule.
- Answer with: COMPLIANT, VIOLATION, or BORDERLINE
- Provide brief justification
- Cite specific text if violation found"""

        user_prompt = f"""Does this document comply with the rule?

DOCUMENT EXCERPT (first 2000 chars):
{self.document_text[:2000]}

PROHIBITED PHRASES FOR THIS RULE:
{', '.join(prohibited_phrases[:10]) if prohibited_phrases else 'N/A'}

VIOLATION EXAMPLES TO WATCH FOR:
{chr(10).join(f'- {ex}' for ex in violation_examples[:5]) if violation_examples else 'N/A'}

Your assessment:"""

        response = self.llm.chat(system_prompt, user_prompt, temperature=0.1, max_tokens=500)
        
        # Parse LLM response
        if 'VIOLATION' in response.upper():
            status = ComplianceStatus.FAIL
            # Extract violation details and create violation object
            violation = Violation(
                rule_id=rule_id,
                rule_name=rule_name,
                severity=Severity(rule.get('severity', 'major')),
                location="Document-wide",
                violation_text=response[:200],
                explanation=response,
                remediation=f"Review and revise content to comply with {rule_id}"
            )
            self.violations.append(violation)
            
            return ComplianceResult(
                rule_id=rule_id,
                rule_name=rule_name,
                status=status,
                notes=response,
                violations=[violation]
            )
        elif 'BORDERLINE' in response.upper():
            return ComplianceResult(
                rule_id=rule_id,
                rule_name=rule_name,
                status=ComplianceStatus.CAUTION,
                notes=response
            )
        else:
            return ComplianceResult(
                rule_id=rule_id,
                rule_name=rule_name,
                status=ComplianceStatus.PASS,
                notes=response
            )
    
    def _phase5_cross_validation(self):
        """
        Phase 5: Cross-validate findings to reduce false positives
        """
        print("   🔍 Cross-validating violations...")
        
        critical_violations = [v for v in self.violations if v.severity == Severity.CRITICAL]
        
        if critical_violations:
            # For each critical violation, double-check with LLM
            for violation in critical_violations:
                system_prompt = """You are a senior compliance reviewer performing final validation.
Review this potential violation and confirm if it is:
1. TRUE VIOLATION - Clear regulatory breach
2. FALSE POSITIVE - Misinterpretation, actually compliant
3. BORDERLINE - Needs human review

Be conservative but accurate."""

                user_prompt = f"""Validate this flagged violation:

RULE: {violation.rule_id} - {violation.rule_name}
FLAGGED CONTENT: {violation.violation_text}
INITIAL ASSESSMENT: {violation.explanation}

Is this a true violation? Explain briefly."""

                validation = self.llm.chat(system_prompt, user_prompt, temperature=0.1)
                
                if 'FALSE POSITIVE' in validation.upper():
                    print(f"      ℹ️  Removing false positive: {violation.rule_id}")
                    self.violations.remove(violation)
                elif 'TRUE VIOLATION' in validation.upper():
                    print(f"      ✓ Confirmed violation: {violation.rule_id}")
                    violation.explanation += f"\n\nVALIDATION: {validation}"
    
    def _phase6_generate_report(self) -> Dict[str, Any]:
        """
        Phase 6: Generate structured compliance report
        """
        critical_count = len([v for v in self.violations if v.severity == Severity.CRITICAL])
        major_count = len([v for v in self.violations if v.severity == Severity.MAJOR])
        minor_count = len([v for v in self.violations if v.severity == Severity.MINOR])
        
        compliant_rules = [r for r in self.compliance_results if r.status == ComplianceStatus.PASS]
        
        overall_status = "✅ COMPLIANT" if critical_count == 0 else "❌ NOT COMPLIANT"
        
        report = {
            'overall_status': overall_status,
            'summary': {
                'critical_violations': critical_count,
                'major_violations': major_count,
                'minor_violations': minor_count,
                'total_violations': len(self.violations),
                'compliant_rules': len(compliant_rules),
                'total_rules_checked': len(self.compliance_results)
            },
            'violations': [
                {
                    'rule_id': v.rule_id,
                    'rule_name': v.rule_name,
                    'severity': v.severity.value,
                    'location': v.location,
                    'violation_text': v.violation_text,
                    'explanation': v.explanation,
                    'remediation': v.remediation
                }
                for v in self.violations
            ],
            'compliant_elements': [
                {
                    'rule_id': r.rule_id,
                    'rule_name': r.rule_name,
                    'notes': r.notes
                }
                for r in compliant_rules
            ],
            'compliance_checklist': [
                {
                    'rule_id': r.rule_id,
                    'rule_name': r.rule_name,
                    'status': r.status.value
                }
                for r in self.compliance_results
            ]
        }
        
        return report
    
    def print_report(self, report: Dict[str, Any]):
        """Print formatted compliance report"""
        print("\n" + "=" * 80)
        print("📊 COMPLIANCE ANALYSIS REPORT")
        print("=" * 80)
        
        print(f"\n🎯 Overall Status: {report['overall_status']}")
        
        print(f"\n📈 Summary:")
        summary = report['summary']
        print(f"   Critical Violations: {summary['critical_violations']}")
        print(f"   Major Violations: {summary['major_violations']}")
        print(f"   Minor Violations: {summary['minor_violations']}")
        print(f"   Total Rules Checked: {summary['total_rules_checked']}")
        print(f"   Compliant Rules: {summary['compliant_rules']}")
        
        if report['violations']:
            print(f"\n❌ VIOLATIONS FOUND ({len(report['violations'])}):")
            print("-" * 80)
            for v in report['violations']:
                print(f"\n🚨 {v['severity'].upper()}: {v['rule_id']} - {v['rule_name']}")
                print(f"   Location: {v['location']}")
                print(f"   Evidence: {v['violation_text'][:200]}...")
                print(f"   Explanation: {v['explanation'][:300]}...")
                print(f"   Remediation: {v['remediation']}")
        
        print(f"\n✅ COMPLIANT ELEMENTS ({len(report['compliant_elements'])}):")
        print("-" * 80)
        for elem in report['compliant_elements'][:10]:  # Show first 10
            print(f"   ✓ {elem['rule_id']}: {elem['rule_name']}")
        
        print("\n" + "=" * 80)
        
        # Save report to text file
        output_file = "values_validation_report.txt"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("VALUES COMPLIANCE ANALYSIS REPORT\n")
            f.write("=" * 80 + "\n\n")
            f.write(f"Overall Status: {report['overall_status']}\n\n")
            f.write(f"Summary:\n")
            f.write(f"  Critical Violations: {report['summary']['critical_violations']}\n")
            f.write(f"  Major Violations: {report['summary']['major_violations']}\n")
            f.write(f"  Minor Violations: {report['summary']['minor_violations']}\n")
            f.write(f"  Total Rules Checked: {report['summary']['total_rules_checked']}\n")
            f.write(f"  Compliant Rules: {report['summary']['compliant_rules']}\n\n")
            
            if report['violations']:
                f.write(f"VIOLATIONS FOUND ({len(report['violations'])}):\n")
                f.write("-" * 80 + "\n")
                for v in report['violations']:
                    f.write(f"\n{v['severity'].upper()}: {v['rule_id']} - {v['rule_name']}\n")
                    f.write(f"  Location: {v['location']}\n")
                    f.write(f"  Evidence: {v['violation_text']}\n")
                    f.write(f"  Explanation: {v['explanation']}\n")
                    f.write(f"  Remediation: {v['remediation']}\n")
            
            f.write(f"\nCOMPLIANT ELEMENTS ({len(report['compliant_elements'])}):\n")
            f.write("-" * 80 + "\n")
            for elem in report['compliant_elements']:
                f.write(f"  ✓ {elem['rule_id']}: {elem['rule_name']}\n")
        
        print(f"📄 Report saved to: {output_file}")


def main():
    """Main entry point"""
    if len(sys.argv) != 3:
        print("Usage: python test_values.py <document.json> <rules.json>")
        print("Example: python test_values.py exemple.json values_rules.json")
        sys.exit(1)
    
    document_path = sys.argv[1]
    rules_path = sys.argv[2]
    
    # Check available LLM providers
    available_providers = llm_manager.get_available_providers()
    if not available_providers:
        print("❌ Error: No LLM API keys found in .env file")
        print("Please create a .env file with at least one of:")
        print("  TOKENFACTORY_API_KEY=your-api-key")
        print("  GEMINI_API_KEY=your-gemini-api-key")
        sys.exit(1)
    
    print("🚀 Compliance Analyzer Starting...")
    print(f"📄 Document: {document_path}")
    print(f"📋 Rules: {rules_path}")
    print(f"📡 Available LLM providers: {', '.join(available_providers)}")
    
    # Initialize analyzer
    analyzer = ComplianceAnalyzer(document_path, rules_path)
    
    # Run analysis
    report = analyzer.analyze()
    
    # Print results
    analyzer.print_report(report)
    
    # Generate violation annotations JSON for highlighting
    annotations = generate_values_violation_annotations(report, analyzer.document)
    annotations_file = "values_violation_annotations.json"
    with open(annotations_file, 'w', encoding='utf-8') as f:
        json.dump(annotations, f, indent=2, ensure_ascii=False)
    print(f"💾 Violation annotations saved to: {annotations_file}")
    
    # Exit with appropriate code
    if report['summary']['critical_violations'] > 0:
        sys.exit(1)  # Non-zero exit for violations
    else:
        sys.exit(0)


def generate_values_violation_annotations(report, document):
    """
    Generate a JSON file with violation annotations for highlighting in the document.
    """
    annotations = {
        "document_annotations": [],
        "summary": {
            "total_violations": report['summary']['total_violations'],
            "critical_violations": report['summary']['critical_violations'],
            "major_violations": report['summary']['major_violations'],
            "minor_violations": report['summary']['minor_violations']
        },
        "instructions": "Use this file to highlight violations in the document. Each annotation contains the exact location, phrase, and violation details for commenting."
    }
    
    # Process each violation from the report
    for violation in report['violations']:
        # Extract slide number from location if possible
        slide_number = get_slide_number_from_location_values(violation['location'], document)
        
        annotation = {
            "rule_id": violation['rule_id'],
            "severity": violation['severity'],
            "location": violation['location'],
            "page_number": slide_number,
            "exact_phrase": violation['violation_text'][:500] if len(violation['violation_text']) > 500 else violation['violation_text'],
            "character_count": len(violation['violation_text']),
            "violation_comment": f"[{violation['rule_id']}] {violation['rule_name']} - {violation['explanation'][:200]}",
            "required_action": violation['remediation']
        }
        
        annotations["document_annotations"].append(annotation)
    
    return annotations


def get_slide_number_from_location_values(location_string, document):
    """Get the actual slide number from the document structure based on location string."""
    location_map = {
        'page_de_garde': 'page_de_garde',
        'cover': 'page_de_garde',
        'slide_2': 'slide_2',
        'page_de_fin': 'page_de_fin',
        'end': 'page_de_fin',
        'metadata': 'document_metadata'
    }
    
    location_lower = location_string.lower().strip()
    
    # Check for document-wide violations
    if 'document-wide' in location_lower or 'entire document' in location_lower:
        return None
    
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


if __name__ == "__main__":
    main()