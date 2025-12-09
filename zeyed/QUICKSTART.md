# 🚀 Quick Start Guide - PowerPoint Compliance Checker

## Overview

This application automatically validates PowerPoint presentations against regulatory compliance rules for financial documents.

## Architecture

```
new_approach/
├── backend/          # FastAPI backend (Python)
│   ├── main.py      # API server
│   ├── test_*.py    # Compliance modules
│   └── *.json       # Rule definitions
├── frontend/         # React frontend
│   └── src/
│       └── App.js   # Main UI
├── rules/           # Compliance rules (JSON)
└── documents/       # Sample documents
```

## Step 1: Install Backend Dependencies

```bash
# Navigate to project root
cd new_approach

# Install Python dependencies (if not already done)
pip install fastapi uvicorn python-multipart python-pptx python-dotenv openai httpx
```

## Step 2: Configure Backend

Create `.env` file in `backend/` directory:

```bash
cd backend
echo "TOKENFACTORY_API_KEY=your-api-key-here" > .env
```

**Note**: TokenFactory is currently down, but the system will still extract and structure data.

## Step 3: Start Backend Server

```bash
# From new_approach/backend directory
python main.py
```

The backend will start on `http://localhost:8000`

You should see:
```
🚀 Starting PowerPoint Compliance Checker API
📡 API URL: http://localhost:8000
📚 API docs: http://localhost:8000/docs
```

## Step 4: Install Frontend Dependencies

Open a **new terminal**:

```bash
cd new_approach/frontend
npm install
```

## Step 5: Start Frontend

```bash
npm start
```

The frontend will open automatically at `http://localhost:3000`

## Step 6: Test the Application

### Option A: Use Sample Files

1. Upload a PowerPoint file (.pptx)
2. Upload the metadata file: `frontend/public/sample_metadata.json`
3. (Optional) Upload a prospectus file (.docx)
4. Click "Start Compliance Check"

### Option B: Create Your Own Metadata

Create a JSON file with this structure:

```json
{
  "Le document fait-il référence à un nouveau Produit": false,
  "Le client est-il un professionnel": true,
  "Société de Gestion": "Your Company Name",
  "Est ce que le produit fait partie de la Sicav d'Oddo": false,
  "Le document fait-il référence à une nouvelle Stratégie": false
}
```

## What Happens During Processing

1. **Upload** (5-10 seconds)
   - Files are uploaded to backend
   - Unique job ID is created
   - Files are stored in `backend/uploads/{job_id}/`

2. **Extraction** (10-20 seconds)
   - PowerPoint content is extracted to JSON
   - Document structure is analyzed
   - Metadata is merged

3. **Compliance Check** (2-5 minutes)
   - 8 compliance modules run in sequence:
     - Structure
     - Registration
     - ESG
     - Disclaimers
     - Performance
     - Values
     - Prospectus
     - General Rules
   - Each module validates against specific rules
   - Violations are collected and categorized

4. **Results**
   - Violations are displayed by severity
   - Reports can be downloaded
   - Results are saved in `backend/results/{job_id}/`

## Understanding Results

### Severity Levels

- **Critical** 🔴: Must be fixed immediately (regulatory violations)
- **Major** 🟠: Important issues requiring attention
- **Minor** 🟡: Minor issues or recommendations

### Compliance Modules

- **Structure**: Document format, required sections, page layout
- **Registration**: Fund registration, authorization mentions
- **ESG**: ESG classification, sustainability disclosures
- **Disclaimers**: Required legal disclaimers and warnings
- **Performance**: Performance data presentation rules
- **Values**: Securities mention requirements
- **Prospectus**: Alignment with prospectus document
- **General**: General regulatory compliance rules

## Troubleshooting

### Backend won't start
```bash
# Check if port 8000 is in use
netstat -ano | findstr :8000

# Try a different port
uvicorn main:app --port 8001
```

### Frontend can't connect to backend
- Verify backend is running on port 8000
- Check `API_BASE_URL` in `frontend/src/App.js`
- Disable any firewall/antivirus temporarily

### "No module named 'openai'" error
```bash
pip install openai httpx python-dotenv
```

### Processing takes too long
- TokenFactory API might be slow/down
- Check backend console for errors
- Verify .env file has API key

### No violations found (but there should be)
- TokenFactory API is down (expected)
- The system still extracts and structures data
- Manual review of extracted JSON is possible

## API Documentation

Visit `http://localhost:8000/docs` for interactive API documentation (Swagger UI)

## File Locations

- **Uploads**: `backend/uploads/{job_id}/`
- **Results**: `backend/results/{job_id}/`
- **Reports**: 
  - `MASTER_COMPLIANCE_REPORT.txt`
  - `CONSOLIDATED_VIOLATIONS.json`
  - `pipeline_result.json`

## Next Steps

1. ✅ Test with sample files
2. ✅ Review generated reports
3. ✅ Customize rules in `rules/*.json`
4. ✅ Add more compliance modules
5. ✅ Deploy to production server

## Support

- Backend logs: Check terminal running `python main.py`
- Frontend logs: Check browser console (F12)
- API docs: http://localhost:8000/docs

## Production Deployment

### Backend
```bash
# Use production ASGI server
pip install gunicorn
gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app
```

### Frontend
```bash
cd frontend
npm run build
# Serve the build/ folder with nginx or similar
```

---

**Happy Compliance Checking! 🎉**
