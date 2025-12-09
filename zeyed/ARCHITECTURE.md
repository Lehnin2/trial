# 🏗️ System Architecture

## Overview

The PowerPoint Compliance Checker is a full-stack application with a React frontend, FastAPI backend, and modular compliance validation system.

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER BROWSER                             │
│                                                                  │
│  ┌────────────────────────────────────────────────────────┐   │
│  │              React Frontend (Port 3000)                 │   │
│  │                                                          │   │
│  │  • File Upload UI                                       │   │
│  │  • Progress Monitoring                                  │   │
│  │  • Results Dashboard                                    │   │
│  │  • Filtering & Export                                   │   │
│  └────────────────────────────────────────────────────────┘   │
│                            │                                     │
│                            │ HTTP/REST API                       │
│                            ▼                                     │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                    FastAPI Backend (Port 8000)                   │
│                                                                  │
│  ┌────────────────────────────────────────────────────────┐   │
│  │                    main.py (API Server)                 │   │
│  │                                                          │   │
│  │  • POST /api/upload          - Upload files            │   │
│  │  • GET  /api/status/{id}     - Check progress          │   │
│  │  • GET  /api/download/{id}/* - Download results        │   │
│  │  • GET  /api/jobs            - List all jobs           │   │
│  └────────────────────────────────────────────────────────┘   │
│                            │                                     │
│                            ▼                                     │
│  ┌────────────────────────────────────────────────────────┐   │
│  │           compliance_backend.py (Processor)             │   │
│  │                                                          │   │
│  │  1. Extract PPTX → JSON                                │   │
│  │  2. Merge metadata                                      │   │
│  │  3. Run compliance orchestrator                         │   │
│  │  4. Consolidate violations                              │   │
│  │  5. Generate reports                                    │   │
│  └────────────────────────────────────────────────────────┘   │
│                            │                                     │
│                            ▼                                     │
│  ┌────────────────────────────────────────────────────────┐   │
│  │    run_all_compliance_checks.py (Orchestrator)          │   │
│  │                                                          │   │
│  │  Runs 8 modules in sequence:                            │   │
│  │  1. Structure      → test_structure.py                  │   │
│  │  2. Registration   → test_registration.py               │   │
│  │  3. ESG            → test_esg.py                        │   │
│  │  4. Disclaimers    → test_disclaimers.py                │   │
│  │  5. Performance    → test_performance.py                │   │
│  │  6. Values         → test_values.py                     │   │
│  │  7. Prospectus     → test_prospectus.py                 │   │
│  │  8. General        → test_general_rules.py              │   │
│  └────────────────────────────────────────────────────────┘   │
│                            │                                     │
│                            ▼                                     │
│  ┌────────────────────────────────────────────────────────┐   │
│  │              Compliance Modules (test_*.py)             │   │
│  │                                                          │   │
│  │  Each module:                                           │   │
│  │  • Loads rules from JSON                                │   │
│  │  • Validates document                                   │   │
│  │  • Calls TokenFactory API (LLM)                         │   │
│  │  • Generates violation annotations                      │   │
│  │  • Saves results to JSON                                │   │
│  └────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                         Data Storage                             │
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │   uploads/   │  │   results/   │  │    rules/    │         │
│  │              │  │              │  │              │         │
│  │  • PPTX      │  │  • Reports   │  │  • JSON      │         │
│  │  • Metadata  │  │  • JSON      │  │  • Rules     │         │
│  │  • Prospectus│  │  • Logs      │  │              │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                      External Services                           │
│                                                                  │
│  ┌────────────────────────────────────────────────────────┐   │
│  │         TokenFactory API (LLM - Currently Down)         │   │
│  │                                                          │   │
│  │  • Llama-3.1-70B-Instruct                              │   │
│  │  • Rule-based validation                                │   │
│  │  • Natural language analysis                            │   │
│  └────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

## Data Flow

### 1. Upload Phase

```
User → Frontend → Backend API → File System
                                      │
                                      ▼
                              uploads/{job_id}/
                                • presentation.pptx
                                • metadata.json
                                • prospectus.docx
```

### 2. Processing Phase

```
Backend → compliance_backend.py
              │
              ├─→ Extract PPTX to JSON
              │   (python-pptx library)
              │
              ├─→ Merge metadata
              │   (document_metadata)
              │
              └─→ run_all_compliance_checks.py
                      │
                      ├─→ Module 1: Structure
                      │   ├─→ Load structure_rules.json
                      │   ├─→ Call TokenFactory API
                      │   └─→ Save structure_violation_annotations.json
                      │
                      ├─→ Module 2: Registration
                      │   ├─→ Load registration.csv
                      │   ├─→ Call TokenFactory API
                      │   └─→ Save registration_violation_annotations.json
                      │
                      ├─→ ... (6 more modules)
                      │
                      └─→ Consolidate all violations
                          ├─→ MASTER_COMPLIANCE_REPORT.txt
                          └─→ CONSOLIDATED_VIOLATIONS.json
```

### 3. Results Phase

```
Backend → Frontend
    │
    ├─→ Job Status (polling)
    │   • status: pending/processing/completed/failed
    │   • progress: 0-100%
    │   • message: "Running ESG module..."
    │
    └─→ Results
        • violations array
        • statistics
        • download links
```

## Component Interactions

### Frontend → Backend

```javascript
// Upload
POST /api/upload
FormData {
  pptx_file: File,
  metadata_file: File,
  prospectus_file: File (optional)
}
→ Response: { job_id, status, message }

// Status Check (polling)
GET /api/status/{job_id}
→ Response: { 
    job_id, 
    status, 
    progress, 
    message, 
    results 
  }

// Download
GET /api/download/{job_id}/violations
→ Response: JSON file with all violations
```

### Backend → Compliance Modules

```python
# Orchestrator calls each module
subprocess.run([
    sys.executable,  # Python interpreter
    'test_structure.py',
    'document.json',
    'structure_rules.json',
    'metadata.json'
])

# Module processes and saves
{
  "document_annotations": [
    {
      "rule_id": "STRUCT_001",
      "severity": "critical",
      "location": "page_de_garde",
      "violation_comment": "...",
      "required_action": "..."
    }
  ],
  "summary": {
    "total_violations": 5,
    "critical_violations": 2,
    "major_violations": 2,
    "minor_violations": 1
  }
}
```

## File Structure

### Input Files

```
uploads/{job_id}/
├── presentation.pptx          # User's PowerPoint
├── metadata.json              # Document metadata
└── prospectus.docx (optional) # Reference document
```

### Processing Files

```
results/{job_id}/
├── extracted_document.json    # Extracted PPTX content
├── structure_violation_annotations.json
├── registration_violation_annotations.json
├── esg_violation_annotations.json
├── disclaimers_violation_annotations.json
├── performance_violation_annotations.json
├── values_violation_annotations.json
├── prospectus_violation_annotations.json
├── general_violation_annotations.json
├── MASTER_COMPLIANCE_REPORT.txt
├── CONSOLIDATED_VIOLATIONS.json
└── pipeline_result.json
```

### Rule Files

```
rules/
├── structure_rules.json       # Structure validation rules
├── esg_rules.json            # ESG compliance rules
├── performance_rules.json    # Performance disclosure rules
├── prospectus_rules.json     # Prospectus alignment rules
├── general_rules.json        # General regulatory rules
└── values_rules.json         # Securities mention rules

documents/
├── disclaimers.csv           # Required disclaimers database
└── registration.csv          # Registration requirements
```

## Technology Stack

### Frontend
- **React 18** - UI framework
- **Axios** - HTTP client
- **Lucide React** - Icons
- **Tailwind CSS** - Styling (CDN)

### Backend
- **FastAPI** - Web framework
- **Uvicorn** - ASGI server
- **Python-PPTX** - PowerPoint extraction
- **OpenAI SDK** - TokenFactory API client
- **Python-dotenv** - Environment variables

### External
- **TokenFactory** - LLM API (Llama-3.1-70B)

## Scalability Considerations

### Current Architecture (Single Server)
```
Frontend (3000) ←→ Backend (8000) ←→ File System
                        ↓
                  TokenFactory API
```

### Production Architecture (Scalable)
```
                    Load Balancer
                         │
        ┌────────────────┼────────────────┐
        ▼                ▼                ▼
    Backend 1        Backend 2        Backend 3
        │                │                │
        └────────────────┼────────────────┘
                         │
                    ┌────┴────┐
                    │         │
                  Redis    S3/Blob
                (Queue)   (Storage)
                    │
                    ▼
              Worker Pool
                    │
                    ▼
            TokenFactory API
```

### Improvements for Scale
1. **Job Queue**: Redis/RabbitMQ for async processing
2. **Worker Pool**: Multiple workers for parallel processing
3. **Cloud Storage**: S3/Azure Blob for file storage
4. **Database**: PostgreSQL for job tracking
5. **Caching**: Redis for status caching
6. **CDN**: CloudFront/Azure CDN for frontend
7. **Load Balancer**: Nginx/AWS ALB for distribution

## Security Architecture

### Current (Development)
```
User → Frontend → Backend → File System
       (HTTP)     (HTTP)    (Local)
```

### Production (Recommended)
```
User → Frontend → API Gateway → Backend → Cloud Storage
       (HTTPS)    (Auth/Rate)   (HTTPS)   (Encrypted)
                      │
                      ├─→ JWT Validation
                      ├─→ Rate Limiting
                      ├─→ Input Sanitization
                      └─→ Logging/Monitoring
```

## Performance Metrics

### Expected Processing Times
- **Upload**: 5-10 seconds
- **Extraction**: 10-20 seconds
- **Compliance Check**: 2-5 minutes (8 modules)
- **Total**: 3-6 minutes per document

### Bottlenecks
1. **TokenFactory API**: External API calls (slowest)
2. **PPTX Extraction**: Large files take longer
3. **Sequential Processing**: Modules run one at a time

### Optimization Opportunities
1. **Parallel Modules**: Run independent modules concurrently
2. **Caching**: Cache rule files and API responses
3. **Batch Processing**: Process multiple documents together
4. **Async I/O**: Use async file operations
5. **Connection Pooling**: Reuse HTTP connections

## Monitoring & Logging

### Current Logging
- **Frontend**: Browser console
- **Backend**: Terminal stdout
- **Modules**: File-based logs

### Production Logging (Recommended)
```
Application → Structured Logs → Log Aggregator → Dashboard
                                 (ELK/Splunk)    (Grafana)
```

### Key Metrics to Track
- Request rate (requests/second)
- Processing time (seconds)
- Error rate (%)
- Queue depth (jobs)
- API latency (ms)
- Storage usage (GB)

## Deployment Architecture

### Development
```
Local Machine
├── Backend (Python)
└── Frontend (Node.js)
```

### Production
```
Cloud Provider (AWS/Azure/GCP)
├── Frontend
│   └── Static Hosting (S3 + CloudFront)
├── Backend
│   ├── Container (Docker)
│   ├── Orchestration (Kubernetes/ECS)
│   └── Auto-scaling
├── Storage
│   └── Object Storage (S3/Blob)
├── Database
│   └── Managed DB (RDS/Azure SQL)
└── Monitoring
    └── CloudWatch/Azure Monitor
```

## Error Handling Flow

```
Error Occurs
    │
    ├─→ Frontend Error
    │   ├─→ Display user-friendly message
    │   ├─→ Log to console
    │   └─→ Allow retry
    │
    ├─→ Backend Error
    │   ├─→ Return error response
    │   ├─→ Log to file/service
    │   ├─→ Update job status to 'failed'
    │   └─→ Clean up resources
    │
    └─→ Module Error
        ├─→ Log error details
        ├─→ Continue with other modules
        ├─→ Mark module as failed
        └─→ Include in final report
```

## Backup & Recovery

### Data to Backup
1. **Uploaded Files**: uploads/{job_id}/
2. **Results**: results/{job_id}/
3. **Rules**: rules/*.json
4. **Configuration**: .env, config files

### Recovery Strategy
1. **Automatic Backups**: Daily snapshots
2. **Retention**: 30 days
3. **Disaster Recovery**: Cross-region replication
4. **Testing**: Monthly recovery drills

---

**This architecture supports the current development setup and provides a clear path to production scaling.**
