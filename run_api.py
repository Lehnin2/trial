"""
Startup script for the Compliance Check API
"""

import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

# Check environment
print("\n" + "="*80)
print("🔍 PRE-FLIGHT CHECKS")
print("="*80)

# Check .env file
env_file = Path(__file__).parent / 'config' / '.env'
if env_file.exists():
    print("✓ .env file found")
    from dotenv import load_dotenv
    load_dotenv(env_file)
else:
    print("⚠️  .env file not found at", env_file)

# Check API key
if os.getenv('TOKENFACTORY_API_KEY'):
    print("✓ TOKENFACTORY_API_KEY configured")
else:
    print("⚠️  TOKENFACTORY_API_KEY not set - extraction will fail")

# Check required files
required_files = [
    'data/rules/general_rules.json',
    'data/rules/esg_rules.json',
    'data/references/prospectus.docx',
    'config/.env'
]

missing = []
for file in required_files:
    if not Path(file).exists():
        missing.append(file)

if missing:
    print(f"⚠️  Missing files: {', '.join(missing)}")
else:
    print("✓ All required files present")

print("="*80 + "\n")

# Start API
if __name__ == "__main__":
    import uvicorn
    
    print("Starting API server on http://localhost:8000")
    print("📖 API docs available at http://localhost:8000/docs")
    print("Press Ctrl+C to stop\n")
    
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
