# PowerPoint Compliance Checker - Frontend

Modern React frontend for automated PowerPoint compliance validation.

## Features

- 📤 **File Upload**: Upload PowerPoint (.pptx), metadata (.json), and optional prospectus (.docx)
- 🔄 **Real-time Progress**: Live job status updates during processing
- 📊 **Detailed Results**: View violations by severity, module, and page
- 🔍 **Advanced Filtering**: Filter violations by severity and compliance module
- 📥 **Export Options**: Download reports in TXT or JSON format
- 🎨 **Modern UI**: Clean, professional interface with Tailwind CSS

## Prerequisites

- Node.js 14+ and npm
- Backend API running on `http://localhost:8000`

## Installation

```bash
cd new_approach/frontend
npm install
```

## Running the Application

```bash
npm start
```

The app will open at `http://localhost:3000`

## Backend Connection

The frontend connects to the backend API at `http://localhost:8000`. Make sure the backend is running:

```bash
cd new_approach/backend
python main.py
```

## File Requirements

### PowerPoint File (.pptx)
- Financial presentation to be validated
- Must be in .pptx format

### Metadata File (.json)
Required metadata about the document. Example structure:
```json
{
  "Le document fait-il référence à un nouveau Produit": false,
  "Le client est-il un professionnel": true,
  "Société de Gestion": "ODDO BHF Asset Management",
  "Est ce que le produit fait partie de la Sicav d'Oddo": true,
  "Le document fait-il référence à une nouvelle Stratégie": false
}
```

### Prospectus File (.docx) - Optional
- Reference prospectus document for cross-validation
- Must be in .docx format

## Compliance Modules

The system validates against 8 compliance modules:

1. **Structure** - Document structure and format
2. **Registration** - Registration requirements
3. **ESG** - ESG compliance rules
4. **Disclaimers** - Required disclaimers and legal text
5. **Performance** - Performance disclosure rules
6. **Values** - Securities mention requirements
7. **Prospectus** - Prospectus alignment
8. **General** - General regulatory rules

## Severity Levels

- 🔴 **Critical**: Must be fixed immediately
- 🟠 **Major**: Important issues requiring attention
- 🟡 **Minor**: Minor issues or recommendations

## Build for Production

```bash
npm run build
```

This creates an optimized production build in the `build/` folder.

## Technology Stack

- **React 18** - UI framework
- **Axios** - HTTP client
- **Lucide React** - Icon library
- **Tailwind CSS** - Styling (via CDN)

## API Endpoints Used

- `POST /api/upload` - Upload files and start processing
- `GET /api/status/{job_id}` - Check job status
- `GET /api/download/{job_id}/report` - Download text report
- `GET /api/download/{job_id}/violations` - Download JSON violations
- `GET /api/download/{job_id}/result` - Download full results

## Troubleshooting

### Backend Connection Error
- Ensure backend is running on port 8000
- Check CORS settings in backend
- Verify API_BASE_URL in App.js

### File Upload Fails
- Check file formats (.pptx, .json, .docx)
- Verify file sizes are reasonable
- Check backend logs for errors

### Processing Stuck
- Check backend console for errors
- Verify TokenFactory API key is configured
- Check backend .env file

## Support

For issues or questions, check the backend logs and ensure all dependencies are installed correctly.
