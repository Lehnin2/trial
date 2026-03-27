# InterTRIAL Projects

This repository contains multiple projects for compliance checking, UI components, and ERP system management.

## 📁 Project Structure

### 1. **react-bits-test** (`fun/react-bits-test/`)
A Next.js-based React application featuring advanced 3D components and interactive UI elements.

**Tech Stack:**
- Next.js 16.1.6
- React 19.2.3
- Three.js (3D rendering)
- React Three Fiber (3D components)
- Tailwind CSS
- Radix UI

**Getting Started:**
```bash
cd fun/react-bits-test
npm install
npm run dev
```

**Available Scripts:**
- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm start` - Start production server
- `npm run lint` - Run ESLint

---

### 2. **Compliance Checker** (`new_approach/`)
A comprehensive compliance checking system for financial documents with backend and frontend components.

#### Backend (`new_approach/backend/`)
**Tech Stack:**
- Python 3.x
- FastAPI
- python-pptx (PowerPoint processing)
- python-docx (Word document processing)
- OpenAI API
- Google Generative AI

**Setup:**
```bash
cd new_approach/backend
# Create virtual environment
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

**Running:**
```bash
python main.py
```

**Features:**
- PowerPoint (.pptx) and Word (.docx) document processing
- ESG, Performance, Prospectus, and Structure validation
- Disclaimers and Registration checks
- PDF conversion support

#### Frontend (`new_approach/frontend/`)
**Tech Stack:**
- React 18.2.0
- Create React App
- Axios
- Lucide React (Icons)

**Setup:**
```bash
cd new_approach/frontend
npm install
npm start
```

**Available Scripts:**
- `npm start` - Start development server
- `npm run build` - Build for production
- `npm test` - Run tests

---

### 3. **ODOO** (`ODOO-main/`)
Enterprise Resource Planning (ERP) system based on ODOO.

**Getting Started:**
Refer to the README in `ODOO-main/` for specific setup instructions.

---

## 🛠️ Development Setup

### Prerequisites
- Node.js 18+ (for React projects)
- Python 3.8+ (for backend)
- Git

### Installation

1. **Clone the repository:**
```bash
git clone <repository-url>
cd interTRIAL
```

2. **Setup by project:**
   - For React projects: `npm install` in the project directory
   - For Python backend: Create virtual environment and `pip install -r requirements.txt`

---

## 📋 Git Configuration

This repository includes a comprehensive `.gitignore` that excludes:
- Virtual environments (`venv/`, `env/`)
- Python cache files (`__pycache__/`, `*.pyc`)
- Node modules (`node_modules/`)
- Office documents (`.pptx`, `.docx`, `.xlsx`, `.xls`)
- Build artifacts and logs
- IDE configuration (`.vscode/`, `.cursor/`, `.idea/`)

---

## 🚀 Recommended Workflow

1. **Before pushing:**
   - Run linting: `npm run lint` (for React projects)
   - Test your changes
   - Check `.gitignore` to ensure no sensitive files are committed

2. **Office Documents:**
   - Store in `documents/` or project-specific folders
   - Use version control with Git LFS if needed for large files
   - Remember to `.gitignore` them to prevent bloating repo

3. **Virtual Environments:**
   - Always use virtual environments for Python
   - Never commit `venv/` directory
   - Ensure `requirements.txt` is up to date

---

## 📝 Notes

- Each project has its own configuration files (package.json, tsconfig.json, etc.)
- Backend validation rules are stored in JSON files in `new_approach/rules/`
- Test files are included in each project for validation

---

## 📧 Support

For issues or questions, please refer to individual project documentation or contact the development team.
