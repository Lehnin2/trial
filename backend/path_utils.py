"""
Path utilities for the Compliance Check project
Handles relative paths from the backend directory
"""

import os
from pathlib import Path

# Get the backend directory (where this file is located)
BACKEND_DIR = Path(__file__).parent

# Get the project root (parent of backend directory)
PROJECT_ROOT = BACKEND_DIR.parent

# Define key paths
DOCUMENTS_DIR = PROJECT_ROOT / "documents"
RULES_DIR = PROJECT_ROOT / "rules"

# Backend subdirectories
UPLOADS_DIR = BACKEND_DIR / "uploads"
RESULTS_DIR = BACKEND_DIR / "results"

# Common document files
DISCLAIMERS_FILE = DOCUMENTS_DIR / "disclaimers.csv"
REGISTRATION_FILE = DOCUMENTS_DIR / "registration.csv"
PROSPECTUS_FILE = DOCUMENTS_DIR / "prospectus.docx"
METADATA_FILE = DOCUMENTS_DIR / "metadata.json"

# Rule files
GENERAL_RULES_FILE = RULES_DIR / "general_rules.json"
ESG_RULES_FILE = RULES_DIR / "esg_rules.json"
PERFORMANCE_RULES_FILE = RULES_DIR / "performance_rules.json"
PROSPECTUS_RULES_FILE = RULES_DIR / "prospectus_rules.json"
STRUCTURE_RULES_FILE = RULES_DIR / "structure_rules.json"
VALUES_RULES_FILE = RULES_DIR / "values_rules.json"

# Environment file
ENV_FILE = BACKEND_DIR / ".env"


def ensure_directories():
    """Ensure all necessary directories exist"""
    UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)


def get_rule_file(rule_type: str) -> Path:
    """
    Get the path to a specific rule file
    
    Args:
        rule_type: Type of rule (general, esg, performance, prospectus, structure, values)
        
    Returns:
        Path to the rule file
    """
    rule_files = {
        'general': GENERAL_RULES_FILE,
        'esg': ESG_RULES_FILE,
        'performance': PERFORMANCE_RULES_FILE,
        'prospectus': PROSPECTUS_RULES_FILE,
        'structure': STRUCTURE_RULES_FILE,
        'values': VALUES_RULES_FILE
    }
    
    if rule_type not in rule_files:
        raise ValueError(f"Unknown rule type: {rule_type}. Valid types: {list(rule_files.keys())}")
    
    return rule_files[rule_type]


def get_document_file(doc_type: str) -> Path:
    """
    Get the path to a specific document file
    
    Args:
        doc_type: Type of document (disclaimers, registration, prospectus, metadata)
        
    Returns:
        Path to the document file
    """
    doc_files = {
        'disclaimers': DISCLAIMERS_FILE,
        'registration': REGISTRATION_FILE,
        'prospectus': PROSPECTUS_FILE,
        'metadata': METADATA_FILE
    }
    
    if doc_type not in doc_files:
        raise ValueError(f"Unknown document type: {doc_type}. Valid types: {list(doc_files.keys())}")
    
    return doc_files[doc_type]


def ensure_env_loaded():
    """Ensure .env file exists and return its path"""
    if not ENV_FILE.exists():
        raise FileNotFoundError(
            f".env file not found at {ENV_FILE}\n"
            f"Please create a .env file in the backend directory with your API keys."
        )
    return str(ENV_FILE)


def verify_all_files_exist() -> dict:
    """
    Verify that all required files exist
    
    Returns:
        Dictionary with file paths and their existence status
    """
    files_to_check = {
        'env': ENV_FILE,
        'disclaimers': DISCLAIMERS_FILE,
        'registration': REGISTRATION_FILE,
        'prospectus': PROSPECTUS_FILE,
        'general_rules': GENERAL_RULES_FILE,
        'esg_rules': ESG_RULES_FILE,
        'performance_rules': PERFORMANCE_RULES_FILE,
        'prospectus_rules': PROSPECTUS_RULES_FILE,
        'structure_rules': STRUCTURE_RULES_FILE,
        'values_rules': VALUES_RULES_FILE
    }
    
    status = {}
    missing_files = []
    
    for name, path in files_to_check.items():
        exists = path.exists()
        status[name] = {
            'path': str(path),
            'exists': exists
        }
        if not exists:
            missing_files.append(f"  ❌ {name}: {path}")
    
    if missing_files:
        print("⚠️  Missing files detected:")
        print("\n".join(missing_files))
    else:
        print("✅ All required files found")
    
    return status


def get_job_directories(job_id: str) -> dict:
    """
    Get upload and result directories for a specific job
    
    Args:
        job_id: Unique job identifier
        
    Returns:
        Dictionary with upload_dir and results_dir paths
    """
    return {
        'upload_dir': UPLOADS_DIR / job_id,
        'results_dir': RESULTS_DIR / job_id
    }


if __name__ == "__main__":
    print("="*80)
    print("📁 Compliance Check Project Paths")
    print("="*80)
    print(f"Project Root: {PROJECT_ROOT}")
    print(f"Backend Dir:  {BACKEND_DIR}")
    print(f"Documents:    {DOCUMENTS_DIR}")
    print(f"Rules:        {RULES_DIR}")
    print(f"Uploads:      {UPLOADS_DIR}")
    print(f"Results:      {RESULTS_DIR}")
    print("\n" + "="*80)
    print("📋 File Verification")
    print("="*80)
    verify_all_files_exist()