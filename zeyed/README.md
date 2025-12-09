# 📊 PowerPoint Compliance Checker

**Automated regulatory compliance validation for financial presentations**

A full-stack application that validates PowerPoint presentations against 140+ compliance rules across 8 regulatory modules.

---

## 🚀 Quick Start

### 1. Start Backend
```bash
cd backend
python main.py
```

### 2. Start Frontend (new terminal)
```bash
cd frontend
npm install
npm start
```

### 3. Open Browser
Go to `http://localhost:3000` and upload your files!

📖 **Detailed Guide**: See [QUICKSTART.md](QUICKSTART.md)

---

## ✨ Features

### 🆕 New Enhanced Features
- 📖 **PowerPoint Preview**: View slides before running checks
- 🎯 **Selective Module Checking**: Choose which compliance modules to run
- 👁️ **Side-by-Side View**: See slides with violations highlighted
- 📍 **Slide-Specific Violations**: Violations mapped to exact slides
- 🎨 **Visual Indicators**: Color-coded slide thumbnails

### Core Features
- 📤 **Multi-File Upload**: PowerPoint, metadata, and optional prospectus
- 🔄 **Real-Time Processing**: Live progress updates during validation
- 📊 **Comprehensive Dashboard**: View violations by severity and module
- 🔍 **Advanced Filtering**: Filter by severity (Critical/Major/Minor) and compliance module
- 📥 **Export Options**: Download reports in TXT or JSON format
- 🎨 **Modern UI**: Clean, professional interface with responsive design

---

## 📁 Project Structure

```
new_approach/
├── backend/              # FastAPI Python backend
│   ├── main.py          # API server
│   ├── test_*.py        # 8 compliance modules
│   └── *.json           # Rule definitions
├── frontend/            # React frontend
│   └── src/App.js       # Main UI component
├── rules/               # Compliance rules (JSON)
├── documents/           # Sample documents
└── docs/                # Documentation
```

---

## 🎯 Compliance Modules

The system validates against 8 compliance modules:

1. **Structure** - Document format and layout
2. **Registration** - Fund registration requirements
3. **ESG** - ESG classification and disclosures
4. **Disclaimers** - Required legal disclaimers
5. **Performance** - Performance data rules
6. **Values** - Securities mention requirements
7. **Prospectus** - Alignment with prospectus
8. **General** - General regulatory rules

---

## 📚 Documentation

### 🆕 New Features
- **[WHATS_NEW.md](WHATS_NEW.md)** - ⭐ What's new in v2.0
- **[ENHANCED_FEATURES.md](ENHANCED_FEATURES.md)** - Detailed feature guide

### Getting Started
- **[QUICKSTART.md](QUICKSTART.md)** - Get started in 3 steps
- **[COMPLETE_SETUP.md](COMPLETE_SETUP.md)** - Detailed installation guide

### Technical Docs
- **[FRONTEND_GUIDE.md](FRONTEND_GUIDE.md)** - Frontend documentation
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - System architecture
- **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** - Common issues and solutions
- **[SUMMARY.md](SUMMARY.md)** - Project summary

---

## 🔧 Requirements

### Backend
- Python 3.8+
- FastAPI, Uvicorn, Python-PPTX, OpenAI SDK

### Frontend
- Node.js 14+
- React 18, Axios, Lucide React

---

## 📊 How It Works

```
1. Upload Files → 2. Extract Content → 3. Validate Rules → 4. View Results
     ↓                    ↓                    ↓                ↓
  PPTX + JSON      PowerPoint → JSON    8 Modules Check    Violations
  + Prospectus     Metadata Merge       140+ Rules         + Reports
```

---

## 🐛 Known Issues

- **TokenFactory API Down**: LLM validation temporarily unavailable
  - System still extracts and structures data
  - Will work automatically when API returns

---

## 🚀 Next Steps

1. ✅ Test with sample files
2. ✅ Review generated reports
3. ✅ Customize rules for your organization
4. ✅ Deploy to production

---

## 📞 Support

- **Issues**: Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- **API Docs**: http://localhost:8000/docs
- **Logs**: Backend terminal + Browser console (F12)

---

**Built with ❤️ for compliance professionals**
