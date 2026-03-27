"""
FastAPI Backend for Compliance Check System
Provides REST API endpoints for frontend consumption
"""

import os
import json
import tempfile
from pathlib import Path
from datetime import datetime
from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import shutil

# Import from src modules
import sys
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from path_utils import (
    GENERAL_RULES_FILE, ESG_RULES_FILE, PERFORMANCE_RULES_FILE,
    PROSPECTUS_RULES_FILE, STRUCTURE_RULES_FILE, VALUES_RULES_FILE,
    REGISTRATION_FILE, PROSPECTUS_FILE, EXTRACTED_DIR, get_sample_presentations
)
from test import PPTXFinancialExtractor
from check import check_document_compliance

# Ensure extracted directory exists
EXTRACTED_DIR.mkdir(parents=True, exist_ok=True)

# Initialize FastAPI app
app = FastAPI(
    title="Compliance Check API",
    description="AI-powered fund compliance checking system",
    version="1.0.0"
)

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change to specific domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# MODELS
# ============================================================================

class ExtractionStatus(BaseModel):
    """Status of document extraction"""
    status: str  # "processing", "completed", "error"
    task_id: str
    message: str
    progress: Optional[int] = None
    output_file: Optional[str] = None
    error: Optional[str] = None

class ViolationItem(BaseModel):
    """Single compliance violation"""
    rule_id: str
    section: str
    severity: str  # "critical", "warning", "info"
    rule_text: str
    message: str
    slide: Optional[int] = None
    suggested_fix: Optional[str] = None

class ComplianceReport(BaseModel):
    """Compliance check results"""
    document_name: str
    total_violations: int
    critical_count: int
    warning_count: int
    info_count: int
    violations: List[ViolationItem]
    metadata: Dict[str, Any]

class RuleDetail(BaseModel):
    """Detailed rule information"""
    rule_id: str
    section: str
    rule_text: str
    detailed_description: str
    severity: str
    keywords: List[str]
    applies_to: Dict[str, Any]

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def get_api_key() -> str:
    """Get API key from environment"""
    api_key = os.getenv('TOKENFACTORY_API_KEY')
    if not api_key:
        raise HTTPException(status_code=500, detail="API key not configured")
    return api_key

def create_document_workspace(filename: str) -> Path:
    """
    Create a dedicated workspace directory for an uploaded document
    Returns: Path to the workspace directory
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_filename = "".join(c for c in filename if c.isalnum() or c in ('_', '-'))
    workspace_name = f"{timestamp}_{safe_filename}"
    
    workspace_dir = EXTRACTED_DIR / workspace_name
    workspace_dir.mkdir(parents=True, exist_ok=True)
    
    return workspace_dir

def save_document_metadata(workspace_dir: Path, metadata: Dict, original_filename: str):
    """Save document metadata to workspace"""
    metadata_with_tracking = {
        "original_filename": original_filename,
        "upload_timestamp": datetime.now().isoformat(),
        "workspace_path": str(workspace_dir),
        **metadata
    }
    
    metadata_path = workspace_dir / "metadata.json"
    with open(metadata_path, 'w', encoding='utf-8') as f:
        json.dump(metadata_with_tracking, f, indent=2, ensure_ascii=False)
    
    return metadata_path

def load_all_rules() -> Dict[str, List]:
    """Load all compliance rules"""
    rules = {}
    
    for rule_file, category in [
        (GENERAL_RULES_FILE, 'general'),
        (ESG_RULES_FILE, 'esg'),
        (PERFORMANCE_RULES_FILE, 'performance'),
        (PROSPECTUS_RULES_FILE, 'prospectus'),
        (STRUCTURE_RULES_FILE, 'structure'),
        (VALUES_RULES_FILE, 'values'),
    ]:
        try:
            if rule_file.exists():
                with open(rule_file) as f:
                    data = json.load(f)
                    rules[category] = data.get('rules', [])
                print(f"✓ Loaded {category} rules from {rule_file}")
            else:
                print(f"⚠️  {category} rules not found at {rule_file}")
                rules[category] = []
        except Exception as e:
            print(f"⚠️  Warning: Could not load {category} rules: {e}")
            rules[category] = []
    
    return rules

def normalize_violation(v: Dict) -> Dict:
    """
    Normalize violation format from old format to new API format
    Handles various field name variations and data types
    """
    # Map old field names to new ones
    rule_id = v.get('rule_id') or v.get('rule') or 'UNKNOWN'
    section = v.get('section') or v.get('type', '').lower() or 'general'
    severity = (v.get('severity') or 'warning').lower()
    rule_text = v.get('rule_text') or v.get('rule') or 'Compliance rule'
    message = v.get('message') or v.get('evidence') or 'Violation detected'
    
    # Handle slide number - convert to int or None
    slide_raw = v.get('slide') or v.get('location')
    slide = None
    if slide_raw:
        if isinstance(slide_raw, int):
            slide = slide_raw
        elif isinstance(slide_raw, str):
            # Try to extract number from strings like "Slide 3" or "3"
            import re
            match = re.search(r'\d+', slide_raw)
            if match:
                slide = int(match.group())
    
    suggested_fix = v.get('suggested_fix') or v.get('recommendation')
    
    return {
        'rule_id': rule_id,
        'section': section,
        'severity': severity,
        'rule_text': rule_text,
        'message': message,
        'slide': slide,
        'suggested_fix': suggested_fix
    }

# ============================================================================
# ENDPOINTS - HEALTH & INFO
# ============================================================================

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Compliance Check API",
        "version": "1.0.0"
    }

@app.get("/info")
async def info():
    """Get system information"""
    rules = load_all_rules()
    samples = get_sample_presentations()
    
    # Check for reference files
    reference_files = {
        "prospectus": PROSPECTUS_FILE.exists(),
        "registration": REGISTRATION_FILE.exists()
    }
    
    return {
        "service": "Compliance Check API",
        "rules": {
            category: len(rule_list) 
            for category, rule_list in rules.items()
        },
        "total_rules": sum(len(r) for r in rules.values()),
        "sample_presentations": [s.name for s in samples],
        "api_key_configured": bool(os.getenv('TOKENFACTORY_API_KEY')),
        "reference_files": reference_files,
        "extracted_dir": str(EXTRACTED_DIR)
    }

# ============================================================================
# ENDPOINTS - FILE OPERATIONS
# ============================================================================

@app.post("/upload")
async def upload_pptx(file: UploadFile = File(...)):
    """
    Upload and extract PPTX file
    Creates a workspace directory and saves all related files
    Returns: Extracted JSON structure and workspace info
    """
    if not file.filename.endswith('.pptx'):
        raise HTTPException(status_code=400, detail="Only .pptx files are supported")
    
    try:
        api_key = get_api_key()
        
        # Create workspace for this document
        workspace_dir = create_document_workspace(file.filename)
        print(f"📁 Created workspace: {workspace_dir}")
        
        # Save uploaded file to workspace
        pptx_path = workspace_dir / file.filename
        contents = await file.read()
        with open(pptx_path, 'wb') as f:
            f.write(contents)
        print(f"💾 Saved PPTX to workspace")
        
        # Extract PPTX
        print(f"📄 Extracting {file.filename}...")
        extractor = PPTXFinancialExtractor(api_key=api_key)
        raw_data = extractor.extract_raw_pptx(str(pptx_path))
        
        print("🤖 Structuring with LLM...")
        structured = extractor.extract_with_llm_batched(raw_data)
        
        # Save extracted data to workspace
        extracted_json_path = workspace_dir / "extracted_data.json"
        with open(extracted_json_path, 'w', encoding='utf-8') as f:
            json.dump(structured, f, indent=2, ensure_ascii=False)
        print(f"💾 Saved extracted data to workspace")
        
        # Save metadata separately
        metadata = structured.get('document_metadata', {})
        metadata_path = save_document_metadata(workspace_dir, metadata, file.filename)
        print(f"💾 Saved metadata to workspace")
        
        return {
            "status": "success",
            "filename": file.filename,
            "workspace_dir": str(workspace_dir),
            "extracted_file": str(extracted_json_path),
            "metadata_file": str(metadata_path),
            "document_metadata": metadata,
            "total_slides": metadata.get('page_count', 0)
        }
    
    except Exception as e:
        import traceback
        print(f"❌ Extraction failed: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Extraction failed: {str(e)}")

@app.post("/check")
async def check_compliance(
    json_file_path: Optional[str] = None, 
    extracted_data: Optional[Dict] = None
):
    """
    Check document compliance
    Accepts either file path or extracted JSON data
    """
    try:
        # Load the document data
        if extracted_data:
            # Use provided data directly
            doc = extracted_data
        elif json_file_path:
            # Load from file
            json_path = Path(json_file_path)
            if not json_path.exists():
                raise HTTPException(status_code=400, detail=f"File not found: {json_file_path}")
            
            with open(json_path, 'r', encoding='utf-8') as f:
                doc = json.load(f)
        else:
            raise HTTPException(
                status_code=400, 
                detail="Either json_file_path or extracted_data required"
            )
        
        # Run compliance check - pass the document data directly
        print("✓ Running compliance checks...")
        result = check_document_compliance(doc)  # Pass doc, not file path
        
        # Save compliance report to workspace if path was provided
        if json_file_path:
            json_path = Path(json_file_path)
            workspace_dir = json_path.parent
            report_path = workspace_dir / "compliance_report.json"
            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            print(f"💾 Saved compliance report to {report_path}")
        
        # Format response
        raw_violations = result.get('violations', [])
        metadata = doc.get('document_metadata', {})
        
        # Normalize all violations to match API schema
        normalized_violations = []
        for v in raw_violations[:500]:  # Limit to 500
            try:
                normalized = normalize_violation(v)
                normalized_violations.append(ViolationItem(**normalized))
            except Exception as e:
                print(f"⚠️  Warning: Could not normalize violation: {e}")
                print(f"   Raw violation: {v}")
                # Create a fallback violation
                normalized_violations.append(ViolationItem(
                    rule_id=str(v.get('rule_id', 'UNKNOWN')),
                    section=str(v.get('section', 'general')).lower(),
                    severity=str(v.get('severity', 'warning')).lower(),
                    rule_text=str(v.get('rule_text', 'Compliance rule')),
                    message=str(v.get('message', 'Violation detected')),
                    slide=None,
                    suggested_fix=None
                ))
        
        return ComplianceReport(
            document_name=metadata.get('document_name', 'Unknown'),
            total_violations=len(normalized_violations),
            critical_count=sum(1 for v in normalized_violations if v.severity == 'critical'),
            warning_count=sum(1 for v in normalized_violations if v.severity == 'warning'),
            info_count=sum(1 for v in normalized_violations if v.severity == 'info'),
            violations=normalized_violations,
            metadata=metadata
        )
    
    except Exception as e:
        import traceback
        print(f"\n⚠️ Error checking document: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=500, 
            detail=f"Compliance check failed: {str(e)}"
        )

@app.get("/workspaces")
async def list_workspaces():
    """List all document workspaces"""
    try:
        workspaces = []
        for workspace_dir in sorted(EXTRACTED_DIR.iterdir()):
            if workspace_dir.is_dir():
                metadata_file = workspace_dir / "metadata.json"
                if metadata_file.exists():
                    with open(metadata_file) as f:
                        metadata = json.load(f)
                    workspaces.append({
                        "workspace_name": workspace_dir.name,
                        "workspace_path": str(workspace_dir),
                        "original_filename": metadata.get('original_filename'),
                        "upload_timestamp": metadata.get('upload_timestamp'),
                        "has_compliance_report": (workspace_dir / "compliance_report.json").exists()
                    })
        
        return {
            "total": len(workspaces),
            "workspaces": workspaces
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# ENDPOINTS - RULES & REFERENCE DATA
# ============================================================================

@app.get("/rules")
async def get_all_rules():
    """Get all compliance rules"""
    try:
        rules = load_all_rules()
        
        return {
            "total": sum(len(r) for r in rules.values()),
            "by_category": {
                category: {
                    "count": len(rule_list),
                    "rules": [
                        {
                            "rule_id": r.get('rule_id'),
                            "section": r.get('section'),
                            "rule_text": r.get('rule_text'),
                            "severity": r.get('severity')
                        }
                        for r in rule_list
                    ]
                }
                for category, rule_list in rules.items()
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not load rules: {str(e)}")

@app.get("/rules/{category}")
async def get_rules_by_category(category: str):
    """Get rules for specific category"""
    try:
        rules = load_all_rules()
        
        if category not in rules:
            raise HTTPException(status_code=404, detail=f"Category '{category}' not found")
        
        return {
            "category": category,
            "count": len(rules[category]),
            "rules": rules[category]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/rules/{category}/{rule_id}")
async def get_rule_detail(category: str, rule_id: str):
    """Get detailed information about a specific rule"""
    try:
        rules = load_all_rules()
        
        if category not in rules:
            raise HTTPException(status_code=404, detail=f"Category '{category}' not found")
        
        rule = next((r for r in rules[category] if r.get('rule_id') == rule_id), None)
        
        if not rule:
            raise HTTPException(status_code=404, detail=f"Rule '{rule_id}' not found")
        
        return rule
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# ENDPOINTS - SAMPLES & REFERENCE
# ============================================================================

@app.get("/samples")
async def get_sample_files():
    """Get list of available sample presentations"""
    try:
        samples = get_sample_presentations()
        return {
            "total": len(samples),
            "samples": [
                {
                    "filename": s.name,
                    "size_mb": round(s.stat().st_size / (1024 * 1024), 2),
                    "path": str(s)
                }
                for s in samples
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# STARTUP
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Initialize on startup"""
    print("="*80)
    print("🚀 COMPLIANCE CHECK API STARTING")
    print("="*80)
    
    # Verify configuration
    if os.getenv('TOKENFACTORY_API_KEY'):
        print("✓ API Key configured")
    else:
        print("⚠️  API Key NOT configured - LLM features will be disabled")
    
    # Ensure directories exist
    EXTRACTED_DIR.mkdir(parents=True, exist_ok=True)
    print(f"✓ Extracted directory: {EXTRACTED_DIR}")
    
    # Load rules with detailed feedback
    rules = load_all_rules()
    print(f"✓ Loaded {sum(len(r) for r in rules.values())} compliance rules total")
    
    # Check reference files
    print(f"{'✓' if PROSPECTUS_FILE.exists() else '⚠️ '} Prospectus file: {PROSPECTUS_FILE}")
    print(f"{'✓' if REGISTRATION_FILE.exists() else '⚠️ '} Registration file: {REGISTRATION_FILE}")
    
    # Check samples
    samples = get_sample_presentations()
    print(f"✓ Found {len(samples)} sample presentations")
    
    print("="*80)

# ============================================================================
# RUN
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )