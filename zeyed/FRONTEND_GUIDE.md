# Frontend Implementation Guide

## 🎨 Overview

A modern, professional React frontend for the PowerPoint Compliance Checker. The UI provides an intuitive workflow for uploading documents, monitoring processing, and reviewing compliance violations.

## ✨ Key Features

### 1. **Three-Stage Workflow**
- **Upload Stage**: Drag-and-drop file upload with validation
- **Processing Stage**: Real-time progress monitoring with job status
- **Results Stage**: Comprehensive violation display with filtering

### 2. **File Upload**
- PowerPoint (.pptx) - Required
- Metadata (.json) - Required  
- Prospectus (.docx) - Optional
- Visual feedback for each file type
- File validation before upload

### 3. **Real-Time Processing**
- Job status polling every 2 seconds
- Progress bar with percentage
- Status messages from backend
- Job ID tracking

### 4. **Results Dashboard**
- **Statistics Cards**: Total, Critical, Major, Minor violations
- **Advanced Filtering**: By severity and compliance module
- **Expandable Violations**: Click to see details
- **Color-Coded Severity**: Red (Critical), Orange (Major), Yellow (Minor)
- **Page References**: Shows which slide has the violation

### 5. **Export Options**
- Download full report (TXT format)
- Download violations (JSON format)
- Structured data for further processing

## 🏗️ Architecture

```
frontend/
├── public/
│   ├── index.html              # HTML template
│   └── sample_metadata.json    # Sample metadata file
├── src/
│   ├── App.js                  # Main application component
│   ├── App.css                 # Styles with Tailwind
│   ├── index.js                # React entry point
│   └── index.css               # Global styles
├── package.json                # Dependencies
└── README.md                   # Documentation
```

## 🔌 API Integration

### Endpoints Used

```javascript
// Upload files and start processing
POST /api/upload
Body: FormData with pptx_file, metadata_file, prospectus_file

// Check job status
GET /api/status/{job_id}
Response: { status, progress, message, results }

// Download text report
GET /api/download/{job_id}/report
Response: Text file

// Download JSON violations
GET /api/download/{job_id}/violations
Response: JSON file with all violations
```

### Data Flow

```
User Upload → Backend Processing → Status Polling → Results Display
     ↓              ↓                    ↓               ↓
  FormData    Job Created          Progress %      Violations
                                   Status Msg       Statistics
```

## 🎯 Component Structure

### Main App Component

```javascript
function App() {
  // State Management
  const [view, setView] = useState('upload');
  const [pptxFile, setPptxFile] = useState(null);
  const [metadataFile, setMetadataFile] = useState(null);
  const [prospectusFile, setProspectusFile] = useState(null);
  const [jobId, setJobId] = useState(null);
  const [jobStatus, setJobStatus] = useState(null);
  const [violations, setViolations] = useState([]);
  
  // Three main views
  return view === 'upload' ? <UploadView /> :
         view === 'processing' ? <ProcessingView /> :
         <ResultsView />;
}
```

### Upload View
- File upload zones for each file type
- Validation before submission
- Information about what's checked
- Visual feedback for selected files

### Processing View
- Animated spinner
- Progress bar
- Status messages
- Job ID display
- Estimated time remaining

### Results View
- Statistics dashboard
- Filter controls
- Violations list with expand/collapse
- Download buttons
- Reset button

## 🎨 UI/UX Design

### Color Scheme
- **Primary**: Indigo (#4F46E5) - Actions, buttons
- **Critical**: Red (#DC2626) - Critical violations
- **Major**: Orange (#EA580C) - Major violations
- **Minor**: Yellow (#CA8A04) - Minor violations
- **Success**: Green (#16A34A) - Compliant items
- **Background**: Blue-Indigo gradient

### Typography
- **Headings**: Bold, large (text-4xl, text-2xl)
- **Body**: Regular, readable (text-base, text-sm)
- **Monospace**: Job IDs, technical info

### Icons (Lucide React)
- Upload, FileText - File operations
- Loader, Clock - Processing
- CheckCircle, AlertCircle, XCircle - Status
- Download - Export actions
- ChevronDown/Up - Expand/collapse

## 📊 Violation Display

### Violation Card Structure
```javascript
{
  rule_id: "STRUCT_001",
  module: "Structure",
  severity: "critical",
  page_number: 1,
  location: "page_de_garde",
  exact_phrase: "Missing fund name",
  violation_comment: "Fund name is required on cover page",
  required_action: "Add fund name to slide 1"
}
```

### Display Features
- Color-coded by severity
- Module badge
- Rule ID badge
- Page number reference
- Expandable details
- Required action guidance

## 🔧 Configuration

### API Base URL
```javascript
const API_BASE_URL = 'http://localhost:8000';
```

Change this for production deployment.

### Polling Interval
```javascript
const interval = setInterval(async () => {
  // Check status
}, 2000); // 2 seconds
```

Adjust based on expected processing time.

## 🚀 Running the Frontend

### Development
```bash
cd new_approach/frontend
npm install
npm start
```

Opens at `http://localhost:3000`

### Production Build
```bash
npm run build
```

Creates optimized build in `build/` folder.

### Deployment
```bash
# Serve with any static server
npx serve -s build

# Or use nginx, Apache, etc.
```

## 🧪 Testing

### Manual Testing Checklist
- [ ] Upload valid files
- [ ] Upload invalid file types
- [ ] Upload without required files
- [ ] Monitor processing progress
- [ ] View results with violations
- [ ] Filter by severity
- [ ] Filter by module
- [ ] Expand/collapse violations
- [ ] Download TXT report
- [ ] Download JSON report
- [ ] Reset and upload new files

### Test Files
- Use sample PowerPoint from `documents/`
- Use `sample_metadata.json` from `frontend/public/`
- Test with and without prospectus

## 🐛 Common Issues

### CORS Errors
**Problem**: Frontend can't connect to backend

**Solution**: 
- Backend has CORS middleware configured
- Check `allow_origins` in `main.py`
- For development, `["*"]` is used

### File Upload Fails
**Problem**: Files don't upload

**Solution**:
- Check file formats (.pptx, .json, .docx)
- Verify backend is running
- Check browser console for errors
- Verify FormData is correctly formatted

### Processing Stuck
**Problem**: Status never updates

**Solution**:
- Check backend console for errors
- Verify job ID is correct
- Check if backend process crashed
- Restart backend if needed

### No Violations Shown
**Problem**: Results page is empty

**Solution**:
- TokenFactory API might be down (expected)
- Check backend logs
- Verify violations JSON structure
- Check if modules ran successfully

## 📱 Responsive Design

The UI is fully responsive:
- **Desktop**: Full layout with side-by-side filters
- **Tablet**: Stacked layout, readable cards
- **Mobile**: Single column, touch-friendly

Breakpoints:
- `md:` - 768px and up
- `lg:` - 1024px and up

## 🎯 Future Enhancements

### Potential Features
1. **Job History**: View previous compliance checks
2. **Comparison Mode**: Compare two reports
3. **PDF Export**: Generate PDF reports
4. **Email Reports**: Send results via email
5. **User Authentication**: Multi-user support
6. **Dashboard**: Analytics and trends
7. **Rule Management**: Edit rules from UI
8. **Batch Processing**: Multiple files at once
9. **Real-time Collaboration**: Share results
10. **Mobile App**: Native mobile version

### Technical Improvements
1. **State Management**: Redux or Context API
2. **TypeScript**: Type safety
3. **Testing**: Jest + React Testing Library
4. **Accessibility**: ARIA labels, keyboard navigation
5. **Internationalization**: Multi-language support
6. **Dark Mode**: Theme switching
7. **Offline Mode**: Service workers
8. **Performance**: Code splitting, lazy loading

## 📚 Dependencies

```json
{
  "react": "^18.2.0",
  "react-dom": "^18.2.0",
  "axios": "^1.6.0",
  "lucide-react": "^0.300.0",
  "react-scripts": "5.0.1"
}
```

### Why These Libraries?

- **React**: Modern, component-based UI
- **Axios**: Promise-based HTTP client
- **Lucide React**: Beautiful, consistent icons
- **Tailwind CSS**: Utility-first styling (via CDN)

## 🔐 Security Considerations

### Current Implementation
- No authentication (development only)
- CORS allows all origins
- Files stored on server

### Production Recommendations
1. Add user authentication
2. Restrict CORS to specific domains
3. Implement file size limits
4. Add rate limiting
5. Sanitize file uploads
6. Use HTTPS
7. Implement CSRF protection
8. Add input validation

## 📖 Code Style

### Conventions
- Functional components with hooks
- camelCase for variables
- PascalCase for components
- Descriptive variable names
- Comments for complex logic
- Consistent indentation (2 spaces)

### Example
```javascript
const handleUpload = async () => {
  // Validate files before upload
  if (!pptxFile || !metadataFile) {
    setError('Please upload required files');
    return;
  }
  
  // Create form data
  const formData = new FormData();
  formData.append('pptx_file', pptxFile);
  // ... rest of implementation
};
```

## 🎓 Learning Resources

- [React Documentation](https://react.dev/)
- [Axios Documentation](https://axios-http.com/)
- [Tailwind CSS](https://tailwindcss.com/)
- [Lucide Icons](https://lucide.dev/)
- [FastAPI CORS](https://fastapi.tiangolo.com/tutorial/cors/)

---

**Built with ❤️ for compliance professionals**
