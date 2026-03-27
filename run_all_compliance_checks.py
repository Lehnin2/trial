#!/usr/bin/env python3
"""
Master Compliance Validation Runner
Orchestrates all 8 compliance modules and consolidates violations into a single report
optimized for PowerPoint highlighting and commenting.

SETUP:
1. Save this file as: run_all_compliance_checks.py
2. Make sure all 8 test scripts are in the same directory:
   - test_structure.py
   - test_registration.py
   - test_esg.py
   - test_disclaimers.py
   - test_performance.py
   - test_values.py
   - test_prospectus.py
   - test_general_rules.py

3. Ensure database files are present:
   - disclaimers.csv
   - esg_rules.json
   - general_rules.json
   - performance_rules.json
   - prospectus_rules.json
   - registration.csv
   - structure_rules.json
   - values_rules.json

4. Create .env file with your API key:
   TOKENFACTORY_API_KEY=your-api-key-here

USAGE:
python run_all_compliance_checks.py document.json prospectus.docx metadata.json

EXAMPLE:
python run_all_compliance_checks.py exemple.json prospectus.docx metadata.json
"""

import json
import sys
import subprocess
import os
from pathlib import Path
from typing import Dict, List, Any
from dataclasses import dataclass, asdict
from datetime import datetime
import traceback

@dataclass
class ConsolidatedViolation:
    """Standardized violation format for PowerPoint highlighting"""
    rule_id: str
    module: str  # Which compliance module detected this
    severity: str  # critical, major, minor
    page_number: int  # Slide number in PowerPoint
    location: str  # Section within the slide
    exact_phrase: str  # Text to highlight in PowerPoint
    character_start: int  # For precise highlighting (if available)
    character_end: int  # For precise highlighting (if available)
    violation_comment: str  # Comment to add in PowerPoint
    required_action: str  # Remediation guidance
    evidence_context: str  # Surrounding text for context (100 chars before/after)
    rule_category: str  # disclaimers, esg, performance, etc.

class ComplianceOrchestrator:
    """Orchestrates all compliance validation modules"""
    
    # Fixed database files (always the same)
    DATABASE_FILES = {
        'disclaimers': 'disclaimers.csv',
        'esg_rules': 'esg_rules.json',
        'general_rules': 'general_rules.json',
        'performance_rules': 'performance_rules.json',
        'prospectus_rules': 'prospectus_rules.json',
        'registration': 'registration.csv',
        'structure_rules': 'structure_rules.json',
        'values_rules': 'values_rules.json'
    }
    
    # Module execution configuration
    MODULES = [
        {
            'name': 'Structure',
            'script': 'test_structure.py',
            'args_template': ['document.json', 'structure_rules.json', 'metadata.json'],
            'annotation_file': 'structure_violation_annotations.json',
            'category': 'structure',
            'priority': 1  # Run first - blocking issues
        },
        {
            'name': 'Registration',
            'script': 'test_registration.py',
            'args_template': ['document.json', 'registration.csv', 'metadata.json'],
            'annotation_file': 'registration_violation_annotations.json',
            'category': 'registration',
            'priority': 2
        },
        {
            'name': 'ESG',
            'script': 'test_esg.py',
            'args_template': ['document.json', 'esg_rules.json', 'metadata.json'],
            'annotation_file': 'esg_violation_annotations.json',
            'category': 'esg',
            'priority': 3
        },
        {
            'name': 'Disclaimers',
            'script': 'test_disclaimers.py',
            'args_template': ['document.json', 'disclaimers.csv', 'metadata.json'],
            'annotation_file': 'disclaimers_violation_annotations.json',
            'category': 'disclaimers',
            'priority': 4
        },
        {
            'name': 'Performance',
            'script': 'test_performance.py',
            'args_template': ['document.json', 'performance_rules.json', 'metadata.json'],
            'annotation_file': 'performance_violation_annotations.json',
            'category': 'performance',
            'priority': 5
        },
        {
            'name': 'Values',
            'script': 'test_values.py',
            'args_template': ['document.json', 'values_rules.json'],
            'annotation_file': 'values_violation_annotations.json',
            'category': 'securities_mention',
            'priority': 6
        },
        {
            'name': 'Prospectus',
            'script': 'test_prospectus.py',
            'args_template': ['document.json', 'prospectus.docx', 'prospectus_rules.json', 'metadata.json'],
            'annotation_file': 'prospectus_violation_annotations.json',
            'category': 'prospectus',
            'priority': 7
        },
        {
            'name': 'General',
            'script': 'test_general_rules.py',
            'args_template': ['document.json', 'general_rules.json', 'metadata.json'],
            'annotation_file': 'general_violation_annotations.json',
            'category': 'general',
            'priority': 8
        }
    ]
    
    def __init__(self, document_path: str, prospectus_path: str, metadata_path: str):
        self.document_path = document_path
        self.prospectus_path = prospectus_path
        self.metadata_path = metadata_path
        
        # Load document structure for slide mapping
        self.document = self._load_json(document_path)
        self.slide_map = self._build_slide_map()
        
        # Results storage
        self.module_results = {}
        self.all_violations = []
        self.execution_log = []
        
    def _load_json(self, path: str) -> Dict:
        """Load JSON file"""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ Error loading {path}: {e}")
            sys.exit(1)
    
    def _build_slide_map(self) -> Dict[str, int]:
        """Build mapping of document sections to slide numbers"""
        slide_map = {}
        
        # Cover page
        if 'page_de_garde' in self.document:
            slide_num = self.document['page_de_garde'].get('slide_number', 1)
            slide_map['page_de_garde'] = slide_num
            slide_map['cover'] = slide_num
        
        # Following slides
        if 'pages_suivantes' in self.document:
            for page in self.document['pages_suivantes']:
                slide_num = page.get('slide_number')
                if slide_num:
                    slide_map[f'slide_{slide_num}'] = slide_num
        
        # End page
        if 'page_de_fin' in self.document:
            slide_num = self.document['page_de_fin'].get('slide_number')
            if slide_num:
                slide_map['page_de_fin'] = slide_num
                slide_map['back_page'] = slide_num
                slide_map['end'] = slide_num
        
        return slide_map
    
    def validate_prerequisites(self) -> bool:
        """Validate all required files exist"""
        print("\n" + "="*80)
        print("🔍 VALIDATING PREREQUISITES")
        print("="*80)
        
        # Check input files
        required_files = [self.document_path, self.prospectus_path, self.metadata_path]
        for file_path in required_files:
            if not Path(file_path).exists():
                print(f"❌ Missing required file: {file_path}")
                return False
            print(f"✅ Found: {file_path}")
        
        # Check database files
        print("\n📚 Checking database files...")
        for db_name, db_file in self.DATABASE_FILES.items():
            if not Path(db_file).exists():
                print(f"⚠️  Missing database file: {db_file} (module may fail)")
            else:
                print(f"✅ Found: {db_file}")
        
        # Check module scripts
        print("\n🔧 Checking module scripts...")
        for module in self.MODULES:
            script_path = module['script']
            if not Path(script_path).exists():
                print(f"❌ Missing module script: {script_path}")
                return False
            print(f"✅ Found: {script_path}")
        
        # Check .env file
        if not Path('.env').exists():
            print("\n⚠️  Warning: .env file not found. Modules may fail without TOKENFACTORY_API_KEY")
        else:
            print("\n✅ Found .env file")
        
        return True
    
    def run_module(self, module: Dict) -> Dict[str, Any]:
        """Execute a single compliance module"""
        module_name = module['name']
        script = module['script']
        args_template = module['args_template']
        
        print(f"\n{'='*80}")
        print(f"🔄 Running: {module_name}")
        print(f"{'='*80}")
        
        # Replace template args with actual file paths
        args = []
        for arg in args_template:
            if arg == 'document.json':
                args.append(self.document_path)
            elif arg == 'prospectus.docx':
                args.append(self.prospectus_path)
            elif arg == 'metadata.json':
                args.append(self.metadata_path)
            else:
                args.append(arg)
        
        # Build command with UTF-8 encoding environment variable
        cmd = ['python', script] + args
        
        # Set UTF-8 encoding for Windows
        env = os.environ.copy()
        env['PYTHONIOENCODING'] = 'utf-8'
        
        try:
            # Run module
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout per module
                env=env,  # Pass UTF-8 environment
                encoding='utf-8',  # Force UTF-8 encoding
                errors='replace'  # Replace encoding errors instead of failing
            )
            
            # Log execution
            execution_result = {
                'module': module_name,
                'script': script,
                'return_code': result.returncode,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'success': result.returncode == 0 or result.returncode == 1  # 1 = violations found
            }
            
            self.execution_log.append(execution_result)
            
            # Print output (truncated for readability)
            if result.stdout:
                stdout_lines = result.stdout.split('\n')
                # Print first 50 and last 20 lines to avoid clutter
                if len(stdout_lines) > 70:
                    print('\n'.join(stdout_lines[:50]))
                    print(f"\n... ({len(stdout_lines) - 70} lines omitted) ...\n")
                    print('\n'.join(stdout_lines[-20:]))
                else:
                    print(result.stdout)
            
            if result.stderr:
                print(f"\n⚠️  Module stderr output:")
                stderr_lines = result.stderr.split('\n')
                for line in stderr_lines[:20]:  # Show first 20 error lines
                    if line.strip():
                        print(f"   {line}")
                if len(stderr_lines) > 20:
                    print(f"   ... ({len(stderr_lines) - 20} more error lines)")
            
            # Check if annotation file was created
            annotation_file = module['annotation_file']
            if Path(annotation_file).exists():
                # Verify it's valid JSON with content
                try:
                    with open(annotation_file, 'r', encoding='utf-8') as f:
                        ann_data = json.load(f)
                        violation_count = len(ann_data.get('document_annotations', []))
                        print(f"✅ {module_name} completed - {violation_count} violations found")
                        execution_result['annotation_file'] = annotation_file
                        execution_result['violation_count'] = violation_count
                except Exception as e:
                    print(f"⚠️  {module_name} annotation file exists but is invalid: {e}")
            else:
                print(f"⚠️  {module_name} completed but no annotations file found")
                print(f"   Expected: {annotation_file}")
                print(f"   Return code: {result.returncode}")
                
                # Debug: Check if module created any files
                print(f"   Files in directory: {', '.join([f.name for f in Path('.').glob('*.json')])}")
            
            return execution_result
            
        except subprocess.TimeoutExpired:
            print(f"❌ {module_name} timed out after 5 minutes")
            return {
                'module': module_name,
                'script': script,
                'success': False,
                'error': 'Timeout'
            }
        except Exception as e:
            print(f"❌ {module_name} failed: {e}")
            traceback.print_exc()
            return {
                'module': module_name,
                'script': script,
                'success': False,
                'error': str(e)
            }
    
    def run_all_modules(self):
        """Execute all compliance modules in priority order"""
        print("\n" + "="*80)
        print("🚀 STARTING COMPREHENSIVE COMPLIANCE VALIDATION")
        print("="*80)
        print(f"📅 Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Sort by priority
        sorted_modules = sorted(self.MODULES, key=lambda m: m['priority'])
        
        for i, module in enumerate(sorted_modules, 1):
            print(f"\n[{i}/{len(sorted_modules)}] {module['name']} Module")
            result = self.run_module(module)
            self.module_results[module['name']] = result
    
    def consolidate_violations(self) -> List[ConsolidatedViolation]:
        """Consolidate all violation annotations into standardized format"""
        print("\n" + "="*80)
        print("📊 CONSOLIDATING VIOLATION REPORTS")
        print("="*80)
        
        consolidated = []
        
        for module in self.MODULES:
            annotation_file = module['annotation_file']
            
            if not Path(annotation_file).exists():
                print(f"⚠️  Skipping {module['name']} - no annotation file found")
                continue
            
            try:
                with open(annotation_file, 'r', encoding='utf-8') as f:
                    annotations = json.load(f)
                
                doc_annotations = annotations.get('document_annotations', [])
                print(f"✅ {module['name']}: {len(doc_annotations)} violations")
                
                for annotation in doc_annotations:
                    # Normalize page number
                    page_number = annotation.get('page_number')
                    if page_number is None:
                        # Try to infer from location
                        location = annotation.get('location', '').lower()
                        page_number = self._resolve_page_number(location)
                    
                    # Create consolidated violation
                    violation = ConsolidatedViolation(
                        rule_id=annotation.get('rule_id', 'UNKNOWN'),
                        module=module['name'],
                        severity=annotation.get('severity', 'minor'),
                        page_number=page_number if page_number else 0,
                        location=annotation.get('location', 'unknown'),
                        exact_phrase=annotation.get('exact_phrase', ''),
                        character_start=0,  # Will be calculated later during highlighting
                        character_end=annotation.get('character_count', 0),
                        violation_comment=annotation.get('violation_comment', ''),
                        required_action=annotation.get('required_action', ''),
                        evidence_context='',  # Will be extracted during highlighting
                        rule_category=module['category']
                    )
                    
                    consolidated.append(violation)
                
            except Exception as e:
                print(f"❌ Error processing {annotation_file}: {e}")
        
        # Sort by page number, then severity
        severity_order = {'critical': 0, 'major': 1, 'minor': 2, 'warning': 3, 'info': 4}
        consolidated.sort(
            key=lambda v: (
                v.page_number if v.page_number else 999,
                severity_order.get(v.severity, 99)
            )
        )
        
        self.all_violations = consolidated
        return consolidated
    
    def _resolve_page_number(self, location: str) -> int:
        """Resolve page number from location string using slide map"""
        location_lower = location.lower().strip()
        
        # Check slide map
        for key, slide_num in self.slide_map.items():
            if key in location_lower:
                return slide_num
        
        # Try to extract number
        import re
        match = re.search(r'(?:slide|page)[_\s]?(\d+)', location_lower)
        if match:
            return int(match.group(1))
        
        # Default mappings
        if 'cover' in location_lower or 'garde' in location_lower:
            return 1
        if 'end' in location_lower or 'fin' in location_lower or 'back' in location_lower:
            return self.document.get('document_metadata', {}).get('page_count', 6)
        
        return 0  # Unknown
    
    def generate_master_report(self):
        """Generate comprehensive master compliance report"""
        print("\n" + "="*80)
        print("📝 GENERATING MASTER COMPLIANCE REPORT")
        print("="*80)
        
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Calculate statistics
        total_violations = len(self.all_violations)
        critical_count = sum(1 for v in self.all_violations if v.severity == 'critical')
        major_count = sum(1 for v in self.all_violations if v.severity == 'major')
        minor_count = sum(1 for v in self.all_violations if v.severity == 'minor')
        
        violations_by_page = {}
        for v in self.all_violations:
            page = v.page_number if v.page_number else 0
            if page not in violations_by_page:
                violations_by_page[page] = []
            violations_by_page[page].append(v)
        
        violations_by_module = {}
        for v in self.all_violations:
            if v.module not in violations_by_module:
                violations_by_module[v.module] = []
            violations_by_module[v.module].append(v)
        
        # Generate text report
        report_lines = [
            "=" * 100,
            "MASTER COMPLIANCE VALIDATION REPORT",
            "=" * 100,
            f"Generated: {timestamp}",
            f"Document: {self.document_path}",
            f"Prospectus: {self.prospectus_path}",
            f"Metadata: {self.metadata_path}",
            "",
            "=" * 100,
            "EXECUTIVE SUMMARY",
            "=" * 100,
            f"Total Violations Found: {total_violations}",
            f"  🔴 Critical: {critical_count}",
            f"  🟠 Major: {major_count}",
            f"  🟡 Minor: {minor_count}",
            "",
            f"Modules Executed: {len(self.MODULES)}",
            f"Pages with Violations: {len([p for p in violations_by_page.keys() if p > 0])}",
            "",
            "=" * 100,
            "VIOLATIONS BY MODULE",
            "=" * 100,
        ]
        
        for module_name in sorted(violations_by_module.keys()):
            viols = violations_by_module[module_name]
            crit = sum(1 for v in viols if v.severity == 'critical')
            maj = sum(1 for v in viols if v.severity == 'major')
            min_v = sum(1 for v in viols if v.severity == 'minor')
            report_lines.append(
                f"{module_name:20s} - Total: {len(viols):3d} "
                f"(Critical: {crit}, Major: {maj}, Minor: {min_v})"
            )
        
        report_lines.extend([
            "",
            "=" * 100,
            "VIOLATIONS BY PAGE (FOR POWERPOINT HIGHLIGHTING)",
            "=" * 100,
        ])
        
        for page_num in sorted(violations_by_page.keys()):
            if page_num == 0:
                report_lines.append("\n📄 Document-Wide / Unknown Location:")
            else:
                report_lines.append(f"\n📄 Slide {page_num}:")
            
            report_lines.append("-" * 100)
            
            for v in violations_by_page[page_num]:
                severity_icon = {
                    'critical': '🔴',
                    'major': '🟠',
                    'minor': '🟡',
                    'warning': '⚠️',
                    'info': 'ℹ️'
                }.get(v.severity, '•')
                
                report_lines.extend([
                    f"\n{severity_icon} {v.rule_id} [{v.module}] - {v.severity.upper()}",
                    f"   Location: {v.location}",
                    f"   Phrase: \"{v.exact_phrase[:100]}{'...' if len(v.exact_phrase) > 100 else ''}\"",
                    f"   Comment: {v.violation_comment[:200]}{'...' if len(v.violation_comment) > 200 else ''}",
                    f"   Action: {v.required_action[:150]}{'...' if len(v.required_action) > 150 else ''}",
                ])
        
        report_lines.extend([
            "",
            "=" * 100,
            "MODULE EXECUTION LOG",
            "=" * 100,
        ])
        
        for log_entry in self.execution_log:
            status = "✅ Success" if log_entry['success'] else "❌ Failed"
            report_lines.append(f"{log_entry['module']:20s} - {status}")
            if 'error' in log_entry:
                report_lines.append(f"   Error: {log_entry['error']}")
        
        report_lines.extend([
            "",
            "=" * 100,
            "END OF REPORT",
            "=" * 100,
        ])
        
        # Save text report
        report_text = "\n".join(report_lines)
        report_file = "MASTER_COMPLIANCE_REPORT.txt"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report_text)
        
        print(f"✅ Text report saved: {report_file}")
        
        # Save consolidated JSON for PowerPoint processing
        json_output = {
            "metadata": {
                "generated_at": timestamp,
                "document": self.document_path,
                "prospectus": self.prospectus_path,
                "total_violations": total_violations,
                "critical_violations": critical_count,
                "major_violations": major_count,
                "minor_violations": minor_count
            },
            "violations_by_page": {
                str(page): [asdict(v) for v in viols]
                for page, viols in violations_by_page.items()
            },
            "all_violations": [asdict(v) for v in self.all_violations],
            "execution_log": self.execution_log
        }
        
        json_file = "CONSOLIDATED_VIOLATIONS.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(json_output, f, indent=2, ensure_ascii=False)
        
        print(f"✅ JSON output saved: {json_file}")
        
        # Print summary
        print("\n" + "=" * 80)
        print("📊 VALIDATION SUMMARY")
        print("=" * 80)
        print(f"Total Violations: {total_violations}")
        print(f"  🔴 Critical: {critical_count}")
        print(f"  🟠 Major: {major_count}")
        print(f"  🟡 Minor: {minor_count}")
        print(f"\nPages affected: {len([p for p in violations_by_page.keys() if p > 0])}")
        print(f"Modules with violations: {len(violations_by_module)}")
        
        return report_text, json_output
    
    def test_single_module(self, module_name: str):
        """Test a single module execution (diagnostic mode)"""
        module = next((m for m in self.MODULES if m['name'] == module_name), None)
        if not module:
            print(f"❌ Module '{module_name}' not found")
            return
        
        print(f"\n🧪 TESTING MODULE: {module_name}")
        print("="*80)
        
        result = self.run_module(module)
        
        print("\n📋 DIAGNOSTIC RESULTS:")
        print(f"   Return code: {result.get('return_code')}")
        print(f"   Success: {result.get('success')}")
        print(f"   Annotation file expected: {module['annotation_file']}")
        print(f"   Annotation file exists: {Path(module['annotation_file']).exists()}")
        
        if result.get('stderr'):
            print(f"\n⚠️  Stderr (first 500 chars):")
            print(result['stderr'][:500])
        
        return result
    
    def run(self):
        """Main execution workflow"""
        print("\n" + "="*80)
        print("🏁 MASTER COMPLIANCE ORCHESTRATOR")
        print("="*80)
        
        # Validate prerequisites
        if not self.validate_prerequisites():
            print("\n❌ Prerequisites check failed. Aborting.")
            sys.exit(1)
        
        # Run all modules
        self.run_all_modules()
        
        # Consolidate results
        self.consolidate_violations()
        
        # Generate master report
        self.generate_master_report()
        
        print("\n" + "="*80)
        print("✅ MASTER VALIDATION COMPLETE")
        print("="*80)
        print(f"\n📁 Output files:")
        print("   • MASTER_COMPLIANCE_REPORT.txt - Human-readable report")
        print("   • CONSOLIDATED_VIOLATIONS.json - Structured data for PowerPoint highlighting")
        
        # Show diagnostic info if no violations found
        if len(self.all_violations) == 0:
            print("\n⚠️  WARNING: No violations were found!")
            print("   This could mean:")
            print("   1. The document is perfectly compliant (unlikely)")
            print("   2. The individual test scripts are not generating annotation files")
            print("   3. There's an encoding or execution error")
            print("\n💡 Try running individual modules manually to diagnose:")
            print(f"   python test_structure.py {self.document_path} structure_rules.json {self.metadata_path}")
            print("\n   Then check if 'structure_violation_annotations.json' is created")
        else:
            print("\n💡 Next step: Use CONSOLIDATED_VIOLATIONS.json to highlight and comment")
            print("   violations in your PowerPoint presentation")


def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print("Usage: python run_all_compliance_checks.py <document.json> <prospectus.docx> <metadata.json>")
        print("   or: python run_all_compliance_checks.py --test <module_name> <document.json> <prospectus.docx> <metadata.json>")
        print("\nStandard mode example:")
        print("  python run_all_compliance_checks.py exemple.json prospectus.docx metadata.json")
        print("\nTest single module example:")
        print("  python run_all_compliance_checks.py --test Structure exemple.json prospectus.docx metadata.json")
        print("\nNote: Database files must be in the same directory:")
        print("  • disclaimers.csv")
        print("  • esg_rules.json")
        print("  • general_rules.json")
        print("  • performance_rules.json")
        print("  • prospectus_rules.json")
        print("  • registration.csv")
        print("  • structure_rules.json")
        print("  • values_rules.json")
        sys.exit(1)
    
    # Check for test mode
    if sys.argv[1] == '--test' and len(sys.argv) == 6:
        module_name = sys.argv[2]
        document_path = sys.argv[3]
        prospectus_path = sys.argv[4]
        metadata_path = sys.argv[5]
        
        orchestrator = ComplianceOrchestrator(document_path, prospectus_path, metadata_path)
        orchestrator.test_single_module(module_name)
        sys.exit(0)
    
    # Standard mode
    if len(sys.argv) != 4:
        print("Error: Incorrect number of arguments")
        print("Usage: python run_all_compliance_checks.py <document.json> <prospectus.docx> <metadata.json>")
        sys.exit(1)
    
    document_path = sys.argv[1]
    prospectus_path = sys.argv[2]
    metadata_path = sys.argv[3]
    
    # Run orchestrator
    orchestrator = ComplianceOrchestrator(document_path, prospectus_path, metadata_path)
    orchestrator.run()


if __name__ == "__main__":
    main()