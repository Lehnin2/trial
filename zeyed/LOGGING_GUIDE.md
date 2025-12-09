# 📝 Logging & Debugging Guide

## New Logging Features

Your backend now has **comprehensive logging** to help you understand what's happening during processing!

---

## 🎯 What's Logged

### 1. **Progress Updates**
Every step of the process is logged with progress percentage:
```
INFO: [job_id] [10%] Initialize: Setting up compliance backend
INFO: [job_id] [20%] Extract: Extracting PowerPoint content
INFO: [job_id] [30%] Module: Starting Structure validation
INFO: [job_id] [50%] Module: Starting ESG validation
INFO: [job_id] [90%] Save: Saving results
```

### 2. **Module Execution**
Each compliance module logs its start and completion:
```
INFO: [job_id] 🔄 Starting module: Structure
INFO: [job_id] ✅ Completed module: Structure - 5 violations found
INFO: [job_id] 🔄 Starting module: ESG
INFO: [job_id] ✅ Completed module: ESG - 2 violations found
```

### 3. **Errors & Exceptions**
Full error details with stack traces:
```
ERROR: [job_id] ERROR in process_compliance_check: File not found
DEBUG: [job_id] Traceback:
  File "main.py", line 123, in process_compliance_check
    ...
```

### 4. **Slide Extraction**
Detailed logging of PowerPoint extraction:
```
INFO: Extracting slides from: presentation.pptx
INFO: Found 10 slides
DEBUG: Processing slide 1
DEBUG: Slide 1 rendered to image
DEBUG: Slide 1 extracted: 5 elements
```

---

## 📂 Log Files

### Location
```
new_approach/backend/logs/
└── compliance_YYYYMMDD.log
```

### Example
```
new_approach/backend/logs/
└── compliance_20241202.log  # Today's log
```

### Log Rotation
- New log file created each day
- Old logs are kept for reference
- Logs include full debug information

---

## 🔍 How to View Logs

### Real-Time (Console)
When you run the backend, you'll see logs in the terminal:

```bash
cd new_approach/backend
python main.py

# You'll see:
INFO: [12345678] Starting compliance check
INFO: [12345678] [10%] Initialize: Setting up compliance backend
INFO: [12345678] [20%] Extract: Extracting PowerPoint content
...
```

### Log File (Detailed)
For full details, check the log file:

```bash
# View today's log
cat logs/compliance_20241202.log

# Or tail it in real-time
tail -f logs/compliance_20241202.log

# Search for errors
grep ERROR logs/compliance_20241202.log

# Search for specific job
grep "12345678" logs/compliance_20241202.log
```

---

## 🐛 Debugging with Logs

### Problem: Upload Fails

**Check logs for:**
```bash
grep "upload" logs/compliance_*.log
```

**Look for:**
- File validation errors
- Permission issues
- Path problems

### Problem: Module Fails

**Check logs for:**
```bash
grep "Module.*failed" logs/compliance_*.log
```

**Look for:**
- Module name
- Error message
- Stack trace

### Problem: Slow Processing

**Check logs for:**
```bash
grep "Starting module" logs/compliance_*.log
```

**Look for:**
- Which module is slow
- Time between start and complete
- Any stuck modules

### Problem: No Violations Found

**Check logs for:**
```bash
grep "violations found" logs/compliance_*.log
```

**Look for:**
- Module completion messages
- Violation counts
- API call errors

---

## 📊 Log Levels

### INFO (Console + File)
- Progress updates
- Module start/complete
- Important events
- User-facing messages

### DEBUG (File Only)
- Detailed processing steps
- Slide extraction details
- Internal state changes
- Function calls

### ERROR (Console + File)
- Exceptions
- Failed operations
- Stack traces
- Critical issues

---

## 🎨 Slide Rendering Logs

### What's Logged
```
INFO: Extracting slides from: presentation.pptx
INFO: Found 10 slides
DEBUG: Processing slide 1
DEBUG: Slide 1 rendered to image
DEBUG: Slide 1 extracted: 5 elements
INFO: Successfully extracted 10 slides
```

### If Rendering Fails
```
ERROR: Failed to render slide 1: Font not found
ERROR: Error rendering slide to image: PIL error
```

**Solution**: Install required fonts or use fallback text display

---

## 💡 Tips for Using Logs

### 1. Monitor in Real-Time
```bash
# Terminal 1: Run backend
python main.py

# Terminal 2: Watch logs
tail -f logs/compliance_$(date +%Y%m%d).log
```

### 2. Search for Specific Job
```bash
# Get job ID from frontend (first 8 chars)
# Then search logs
grep "12345678" logs/compliance_*.log
```

### 3. Find All Errors
```bash
grep -i error logs/compliance_*.log
```

### 4. Track Module Performance
```bash
# See how long each module takes
grep "Starting module\|Completed module" logs/compliance_*.log
```

### 5. Debug API Issues
```bash
# Look for API-related errors
grep -i "api\|token" logs/compliance_*.log
```

---

## 🔧 Troubleshooting Common Issues

### Issue: No Logs Appearing

**Check:**
1. Logs directory exists: `ls backend/logs/`
2. Permissions: `ls -la backend/logs/`
3. Logger is imported: Check `main.py` imports

**Fix:**
```bash
cd backend
mkdir -p logs
chmod 755 logs
```

### Issue: Log File Too Large

**Solution:**
```bash
# Archive old logs
cd backend/logs
gzip compliance_20241201.log

# Or delete old logs
rm compliance_202411*.log
```

### Issue: Can't Find Error

**Try:**
```bash
# Search all logs
grep -r "error text" logs/

# Case-insensitive
grep -ri "error text" logs/

# With context (5 lines before/after)
grep -A 5 -B 5 "error text" logs/compliance_*.log
```

---

## 📈 Log Analysis

### Count Violations by Module
```bash
grep "violations found" logs/compliance_*.log | \
  awk '{print $NF, $(NF-2)}' | \
  sort | uniq -c
```

### Find Slowest Modules
```bash
# Compare timestamps between start and complete
grep "Starting module\|Completed module" logs/compliance_*.log
```

### Error Rate
```bash
# Count errors
grep -c ERROR logs/compliance_*.log

# Count total operations
grep -c "Starting compliance check" logs/compliance_*.log
```

---

## 🎯 Best Practices

### 1. Always Check Logs First
Before asking for help, check the logs for error messages.

### 2. Include Log Excerpts
When reporting issues, include relevant log lines.

### 3. Monitor During Development
Keep a terminal open with `tail -f` to watch logs in real-time.

### 4. Clean Up Old Logs
Periodically delete or archive old log files to save space.

### 5. Use Grep Effectively
Learn basic grep commands to search logs efficiently.

---

## 📚 Log Format

### Standard Format
```
YYYY-MM-DD HH:MM:SS | LEVEL    | logger_name | message
2024-12-02 14:30:15 | INFO     | compliance_checker | [12345678] Starting compliance check
```

### Components
- **Timestamp**: When the event occurred
- **Level**: INFO, DEBUG, ERROR
- **Logger**: Which component logged it
- **Message**: The actual log message

### Job ID Format
- Full: `12345678-1234-1234-1234-123456789012`
- Short (in logs): `12345678` (first 8 characters)

---

## 🚀 Quick Reference

### View Today's Logs
```bash
cat backend/logs/compliance_$(date +%Y%m%d).log
```

### Watch Logs Live
```bash
tail -f backend/logs/compliance_$(date +%Y%m%d).log
```

### Find Errors
```bash
grep ERROR backend/logs/compliance_*.log
```

### Search for Job
```bash
grep "JOB_ID" backend/logs/compliance_*.log
```

### Count Violations
```bash
grep "violations found" backend/logs/compliance_*.log
```

---

**With comprehensive logging, debugging is now much easier!** 🎉
