# 🔧 Troubleshooting Guide

## Quick Diagnostics

Run these commands to check your setup:

```bash
# Check Python version
python --version  # Should be 3.8+

# Check if backend dependencies are installed
pip list | grep fastapi
pip list | grep openai

# Check if Node is installed
node --version  # Should be 14+
npm --version

# Check if ports are available
netstat -ano | findstr :8000  # Backend port
netstat -ano | findstr :3000  # Frontend port
```

---

## Backend Issues

### ❌ Problem: Backend won't start

**Error**: `ModuleNotFoundError: No module named 'fastapi'`

**Solution**:
```bash
cd new_approach/backend
pip install fastapi uvicorn python-multipart python-pptx python-dotenv openai httpx
```

---

### ❌ Problem: "No module named 'openai'"

**Error**: When running compliance checks

**Solution**: This was fixed! But if you still see it:
```bash
pip install openai httpx
```

**Verify the fix**:
Check `run_all_compliance_checks.py` line 233:
```python
# Should be:
cmd = [sys.executable, script] + args

# NOT:
cmd = ['python', script] + args
```

---

### ❌ Problem: Port 8000 already in use

**Error**: `Address already in use`

**Solution**:
```bash
# Find what's using port 8000
netstat -ano | findstr :8000

# Kill the process (Windows)
taskkill /PID <process_id> /F

# Or use a different port
python main.py --port 8001
# Then update frontend API_BASE_URL to http://localhost:8001
```

---

### ❌ Problem: ".env file not found"

**Error**: `TOKENFACTORY_API_KEY not found`

**Solution**:
```bash
cd new_approach/backend
echo "TOKENFACTORY_API_KEY=your-api-key-here" > .env
```

**Note**: TokenFactory is currently down, but the .env file is still needed.

---

### ❌ Problem: "File not found" errors

**Error**: `Missing database file: structure_rules.json`

**Solution**:
```bash
# Verify files exist
cd new_approach
ls rules/          # Should show all *_rules.json files
ls documents/      # Should show .csv files

# Run path verification
cd backend
python path_utils.py
```

---

### ❌ Problem: Backend starts but crashes immediately

**Check**:
1. Look at the terminal output for error messages
2. Verify all imports work:
```bash
python -c "import fastapi; import uvicorn; import pptx; print('OK')"
```

3. Check if .env file exists:
```bash
ls backend/.env
```

4. Try running in debug mode:
```bash
python -m pdb main.py
```

---

## Frontend Issues

### ❌ Problem: Frontend won't start

**Error**: `npm: command not found`

**Solution**:
Install Node.js from https://nodejs.org/

---

### ❌ Problem: "Module not found" errors

**Error**: Various module errors

**Solution**:
```bash
cd new_approach/frontend
rm -rf node_modules package-lock.json
npm install
```

---

### ❌ Problem: Port 3000 already in use

**Error**: `Port 3000 is already in use`

**Solution**:
```bash
# Option 1: Kill the process
netstat -ano | findstr :3000
taskkill /PID <process_id> /F

# Option 2: Use different port
# Set environment variable before starting
set PORT=3001
npm start
```

---

### ❌ Problem: Frontend can't connect to backend

**Error**: `Network Error` or `CORS policy`

**Symptoms**:
- Upload button doesn't work
- Status never updates
- Console shows CORS errors

**Solution**:

1. **Verify backend is running**:
```bash
# Open http://localhost:8000 in browser
# Should see: {"status": "healthy", ...}
```

2. **Check API_BASE_URL in frontend**:
```javascript
// File: frontend/src/App.js, line 9
const API_BASE_URL = 'http://localhost:8000';  // Verify this
```

3. **Check CORS settings in backend**:
```python
# File: backend/main.py, lines 28-34
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Should allow all for development
    ...
)
```

4. **Disable browser extensions**:
- Ad blockers can interfere
- Try in incognito mode

---

### ❌ Problem: Upload fails silently

**Symptoms**:
- Click upload, nothing happens
- No error message shown

**Solution**:

1. **Open browser console** (F12)
2. **Look for errors**
3. **Common causes**:
   - Wrong file format
   - File too large
   - Backend not running
   - CORS issue

4. **Test backend directly**:
```bash
# Use curl or Postman
curl -X POST http://localhost:8000/api/upload \
  -F "pptx_file=@test.pptx" \
  -F "metadata_file=@metadata.json"
```

---

### ❌ Problem: Processing stuck at 0%

**Symptoms**:
- Progress bar doesn't move
- Status never changes from "pending"

**Solution**:

1. **Check backend terminal** for errors
2. **Verify job was created**:
```bash
# Check uploads directory
ls backend/uploads/
# Should see a folder with job_id
```

3. **Check backend logs**:
- Look for Python errors
- Check if modules are running

4. **Restart backend**:
```bash
# Stop: Ctrl+C
# Start: python main.py
```

---

## Processing Issues

### ❌ Problem: "No violations found" but there should be

**Reason**: TokenFactory API is down (expected)

**What happens**:
- ✅ Files upload successfully
- ✅ PPTX is extracted
- ✅ Structure is analyzed
- ❌ LLM validation skipped

**Workaround**:
1. Check extracted JSON:
```bash
cat backend/results/{job_id}/extracted_document.json
```

2. Manual review possible
3. Wait for TokenFactory to return

---

### ❌ Problem: Processing takes too long

**Expected**: 3-6 minutes per document

**If longer**:
1. **Check backend terminal** for stuck modules
2. **Check TokenFactory API** status
3. **Verify file size** isn't too large
4. **Check system resources** (CPU, memory)

**Optimization**:
- Close other applications
- Use smaller test files first
- Check internet connection (for API calls)

---

### ❌ Problem: Module fails with error

**Symptoms**:
- One module shows error
- Others complete successfully

**Solution**:

1. **Check module-specific logs**:
```bash
cat backend/results/{job_id}/*_validation_report.txt
```

2. **Run module manually**:
```bash
cd backend
python test_structure.py document.json structure_rules.json metadata.json
```

3. **Check rule files**:
```bash
# Verify JSON is valid
python -m json.tool rules/structure_rules.json
```

---

## Results Issues

### ❌ Problem: Results page is empty

**Symptoms**:
- Processing completes
- Results page shows 0 violations
- But violations should exist

**Solution**:

1. **Check violations file**:
```bash
cat backend/results/{job_id}/CONSOLIDATED_VIOLATIONS.json
```

2. **Verify file structure**:
```json
{
  "all_violations": [...]  // Should have violations here
}
```

3. **Check browser console** for JavaScript errors

4. **Verify API response**:
```bash
curl http://localhost:8000/api/download/{job_id}/violations
```

---

### ❌ Problem: Can't download reports

**Symptoms**:
- Click download button
- Nothing happens or error shown

**Solution**:

1. **Check if files exist**:
```bash
ls backend/results/{job_id}/
# Should see:
# - MASTER_COMPLIANCE_REPORT.txt
# - CONSOLIDATED_VIOLATIONS.json
```

2. **Check browser console** for errors

3. **Try direct download**:
```
http://localhost:8000/api/download/{job_id}/report
http://localhost:8000/api/download/{job_id}/violations
```

4. **Check file permissions**:
```bash
# Files should be readable
ls -la backend/results/{job_id}/
```

---

## File Issues

### ❌ Problem: "Invalid file format"

**Solution**:
- **PowerPoint**: Must be .pptx (not .ppt)
- **Metadata**: Must be .json (valid JSON)
- **Prospectus**: Must be .docx (not .doc)

**Verify JSON**:
```bash
python -m json.tool metadata.json
```

---

### ❌ Problem: "File too large"

**Current limits**: No explicit limit set

**Solution**:
1. **Compress PowerPoint**:
   - Remove unused slides
   - Compress images
   - Remove embedded fonts

2. **Add size limit** in backend:
```python
# In main.py
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
```

---

## Environment Issues

### ❌ Problem: Virtual environment not activated

**Symptoms**:
- Packages not found
- Wrong Python version

**Solution**:
```bash
# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate

# Verify
which python  # Should point to venv
```

---

### ❌ Problem: Python version too old

**Error**: `SyntaxError` or version warnings

**Solution**:
```bash
# Check version
python --version  # Need 3.8+

# Upgrade Python
# Download from python.org
# Or use pyenv/conda
```

---

## Network Issues

### ❌ Problem: Can't reach TokenFactory API

**Error**: `Connection timeout` or `API error`

**Solution**:
1. **Check internet connection**
2. **Verify API endpoint**:
```bash
curl https://tokenfactory.esprit.tn/api
```

3. **Check firewall/antivirus**
4. **Try VPN** if blocked

**Note**: API is currently down, this is expected.

---

### ❌ Problem: Localhost not accessible

**Error**: `ERR_CONNECTION_REFUSED`

**Solution**:
1. **Check if server is running**:
```bash
# Backend
curl http://localhost:8000

# Frontend
curl http://localhost:3000
```

2. **Try 127.0.0.1 instead**:
```
http://127.0.0.1:8000
http://127.0.0.1:3000
```

3. **Check hosts file**:
```bash
# Windows: C:\Windows\System32\drivers\etc\hosts
# Should have: 127.0.0.1 localhost
```

---

## Data Issues

### ❌ Problem: Metadata format incorrect

**Error**: `Invalid metadata structure`

**Correct format**:
```json
{
  "Le document fait-il référence à un nouveau Produit": false,
  "Le client est-il un professionnel": true,
  "Société de Gestion": "Company Name",
  "Est ce que le produit fait partie de la Sicav d'Oddo": false,
  "Le document fait-il référence à une nouvelle Stratégie": false
}
```

**Validate**:
```bash
python -m json.tool metadata.json
```

---

### ❌ Problem: Rules not loading

**Error**: `Rule file not found`

**Solution**:
```bash
# Verify rules exist
ls new_approach/rules/

# Should see:
# - structure_rules.json
# - esg_rules.json
# - performance_rules.json
# - prospectus_rules.json
# - general_rules.json
# - values_rules.json

# Validate JSON
python -m json.tool rules/structure_rules.json
```

---

## Performance Issues

### ❌ Problem: System is slow

**Symptoms**:
- High CPU usage
- Long processing times
- UI lag

**Solution**:

1. **Close other applications**
2. **Check system resources**:
```bash
# Windows
taskmgr

# Check Python processes
tasklist | findstr python
```

3. **Reduce file size**
4. **Use smaller test files first**

---

## Debugging Tips

### Enable Verbose Logging

**Backend**:
```python
# In main.py
import logging
logging.basicConfig(level=logging.DEBUG)
```

**Frontend**:
```javascript
// In App.js
console.log('Debug:', variable);
```

### Check API Directly

```bash
# Health check
curl http://localhost:8000/

# Upload test
curl -X POST http://localhost:8000/api/upload \
  -F "pptx_file=@test.pptx" \
  -F "metadata_file=@metadata.json"

# Status check
curl http://localhost:8000/api/status/{job_id}
```

### Inspect Files

```bash
# Check uploads
ls -la backend/uploads/{job_id}/

# Check results
ls -la backend/results/{job_id}/

# View extracted JSON
cat backend/results/{job_id}/extracted_document.json | python -m json.tool
```

### Browser DevTools

1. **Open DevTools**: F12
2. **Network Tab**: See API calls
3. **Console Tab**: See JavaScript errors
4. **Application Tab**: See local storage

---

## Getting Help

### Before Asking for Help

1. ✅ Check this troubleshooting guide
2. ✅ Review error messages carefully
3. ✅ Check backend terminal output
4. ✅ Check browser console
5. ✅ Try the quick diagnostics at the top

### Information to Provide

When reporting issues, include:
- Error message (full text)
- Steps to reproduce
- Backend terminal output
- Browser console output
- Python version
- Node version
- Operating system

### Useful Commands

```bash
# System info
python --version
node --version
npm --version

# Package versions
pip list
npm list

# Check processes
tasklist | findstr python
tasklist | findstr node

# Check ports
netstat -ano | findstr :8000
netstat -ano | findstr :3000
```

---

## Emergency Reset

If everything is broken:

```bash
# 1. Stop all processes
# Ctrl+C in both terminals

# 2. Clean backend
cd new_approach/backend
rm -rf uploads/* results/* __pycache__

# 3. Clean frontend
cd ../frontend
rm -rf node_modules package-lock.json

# 4. Reinstall
pip install -r requirements.txt  # If you have one
npm install

# 5. Restart
# Terminal 1:
python main.py

# Terminal 2:
npm start
```

---

**Still stuck? Check the documentation files or review the code comments for more details.**
