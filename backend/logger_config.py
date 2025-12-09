"""
Enhanced logging configuration for compliance checker
"""

import logging
import sys
from datetime import datetime
from pathlib import Path

# Create logs directory
LOGS_DIR = Path(__file__).parent / "logs"
LOGS_DIR.mkdir(exist_ok=True)

# Configure logging
def setup_logger(name: str = "compliance_checker"):
    """Setup enhanced logger with file and console output"""
    
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    
    # Remove existing handlers
    logger.handlers = []
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    simple_formatter = logging.Formatter(
        '%(levelname)s: %(message)s'
    )
    
    # Console handler (INFO and above)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(simple_formatter)
    logger.addHandler(console_handler)
    
    # File handler (DEBUG and above)
    log_file = LOGS_DIR / f"compliance_{datetime.now().strftime('%Y%m%d')}.log"
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(detailed_formatter)
    logger.addHandler(file_handler)
    
    return logger

# Create default logger
logger = setup_logger()

def log_progress(job_id: str, step: str, progress: int, message: str):
    """Log progress with structured format"""
    logger.info(f"[{job_id[:8]}] [{progress}%] {step}: {message}")

def log_error(job_id: str, error: Exception, context: str = ""):
    """Log error with full traceback"""
    import traceback
    logger.error(f"[{job_id[:8]}] ERROR in {context}: {str(error)}")
    logger.debug(f"[{job_id[:8]}] Traceback:\n{traceback.format_exc()}")

def log_module_start(job_id: str, module_name: str):
    """Log module start"""
    logger.info(f"[{job_id[:8]}] 🔄 Starting module: {module_name}")

def log_module_complete(job_id: str, module_name: str, violations: int):
    """Log module completion"""
    logger.info(f"[{job_id[:8]}] ✅ Completed module: {module_name} - {violations} violations found")

def log_module_error(job_id: str, module_name: str, error: Exception):
    """Log module error"""
    logger.error(f"[{job_id[:8]}] ❌ Module {module_name} failed: {str(error)}")
