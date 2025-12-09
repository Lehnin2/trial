# PowerPoint Compliance Checker

AI-powered compliance validation for financial PowerPoint presentations.

## Requirements

- Python 3.9+
- Node.js 16+
- API Keys (at least one):
  - TokenFactory API key
  - Gemini API key (fallback)

## Quick Start

### 1. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate it
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file with your API keys
copy .env.example .env
# Edit .env and add your API keys

# Run the server
python main.py
```

Backend runs at: http://localhost:8000

### 2. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Run the app
npm start
```

Frontend runs at: http://localhost:3000

## Usage

1. Open http://localhost:3000
2. Upload a PowerPoint file (.pptx) and metadata file (.json)
3. Select compliance modules to run
4. Click "Run Check"
5. Review violations and download report

## Compliance Modules

- Structure - Document format validation
- Registration - Fund registration requirements
- ESG - Environmental, Social, Governance compliance
- Disclaimers - Required disclaimer checks
- Performance - Performance data rules
- Values - Securities mention validation
- Prospectus - Prospectus alignment
- General - General compliance rules
