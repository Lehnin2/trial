"""
Path utilities for the Compliance Check project
Handles relative paths from the src directory
"""

import os
from pathlib import Path

# Get the project root (parent of src directory)
SRC_DIR = Path(__file__).parent
PROJECT_ROOT = SRC_DIR.parent

# Define key paths
DATA_DIR = PROJECT_ROOT / "data"
CONFIG_DIR = PROJECT_ROOT / "config"
DOCS_DIR = PROJECT_ROOT / "docs"

# Data subdirectories
RULES_DIR = DATA_DIR / "rules"
SAMPLES_DIR = DATA_DIR / "samples"
REFERENCES_DIR = DATA_DIR / "references"
EXTRACTED_DIR = DATA_DIR / "extracted"

# Common file paths
ENV_FILE = CONFIG_DIR / ".env"
METADATA_FILE = EXTRACTED_DIR / "metadata.json"
METADATA3_FILE = EXTRACTED_DIR / "metadata3.json"
PROSPECTUS_FILE = REFERENCES_DIR / "prospectus.docx"
REGISTRATION_FILE = REFERENCES_DIR / "registration.csv"

# Rule files
GENERAL_RULES_FILE = RULES_DIR / "general_rules.json"
ESG_RULES_FILE = RULES_DIR / "esg_rules.json"
PERFORMANCE_RULES_FILE = RULES_DIR / "performance_rules.json"
PROSPECTUS_RULES_FILE = RULES_DIR / "prospectus_rules.json"
STRUCTURE_RULES_FILE = RULES_DIR / "structure_rules.json"
VALUES_RULES_FILE = RULES_DIR / "values_rules.json"

def get_sample_presentations():
    """Get list of all sample PPTX files"""
    return sorted(SAMPLES_DIR.glob("*.pptx"))

def get_extracted_jsons():
    """Get list of all extracted JSON files"""
    return sorted(EXTRACTED_DIR.glob("extracted_data*.json"))

def ensure_env_loaded():
    """Ensure .env file is loaded, exit if not found"""
    if not ENV_FILE.exists():
        raise FileNotFoundError(f".env file not found at {ENV_FILE}")
    return str(ENV_FILE)
