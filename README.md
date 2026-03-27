# Automated Compliance Check

An AI-powered automated compliance checking system for marketing documents in Asset Management. Uses GenAI to facilitate reviews performed by Compliance teams on documents issued by Marketing, with a "Human in the Loop" approach.

## 📋 Project Overview

This project implements an automated solution for compliance control of marketing documents, including:

- **Document Analysis**: Support for PowerPoint presentations and Word documents
- **Rule-Based Validation**: Checks against a comprehensive corpus of compliance rules
- **AI-Powered Review**: Uses GenAI to analyze document content
- **Human Verification**: Compliance team can review and correct AI suggestions
- **Interactive Dashboard**: Web-based interface for visualization and management

### Key Features

- 🤖 **Generative AI Integration**: Leverages GenAI for intelligent document analysis
- 📝 **Rule Engine**: Validates documents against multiple compliance rule sets:
  - General compliance rules
  - ESG (Environmental, Social, Governance) rules
  - Performance disclosure rules
  - Prospectus consistency rules
  - Structure and format rules
  - Value-related rules
- 🎯 **Multi-Rule Support**: Handles disclaimers, mandated statements, and regulatory requirements
- 👥 **Human-in-the-Loop**: Annotation system for compliance team feedback
- 📊 **Reference Data**: Includes fund registration and product metadata

## 🏗️ Project Structure

```
.
├── api.py                      # FastAPI application
├── run_api.py                  # API entry point
├── requirements_api.txt        # Python dependencies
│
├── frontend/                   # React web application
│   ├── src/                   # React components and styling
│   ├── public/                # Static assets
│   └── package.json           # Node dependencies
│
├── src/                        # Python source code
│   ├── pipeline.py            # Main processing pipeline
│   ├── check.py               # Compliance checking logic
│   ├── agent_local.py         # Local AI agent
│   ├── path_utils.py          # Utility functions
│   └── test.py                # Tests
│
├── data/                       # Data files
│   ├── extracted/             # Extracted document data
│   ├── references/            # Reference files (registrations, etc.)
│   ├── rules/                 # Compliance rule definitions (JSON)
│   │   ├── general_rules.json
│   │   ├── esg_rules.json
│   │   ├── performance_rules.json
│   │   ├── prospectus_rules.json
│   │   ├── structure_rules.json
│   │   └── values_rules.json
│   └── samples/               # Sample documents
│
├── docs/                       # Documentation
│   └── context_projet+regles.md    # Project context and compliance rules
│
├── config/                     # Configuration files
└── kamel/                      # Dashboard utilities
```

## 🚀 Getting Started

### Prerequisites

- Python 3.8+ 
- Node.js 14+
- npm or yarn

### Backend Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements_api.txt
```

3. Configure environment variables:
Create a `.env` file with necessary API keys and configuration.

4. Run the API:
```bash
python run_api.py
# or
uvicorn api:app --reload
```

The API will start at `http://localhost:8000`

### Frontend Setup

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start development server:
```bash
npm start
```

The application will open at `http://localhost:3000`

## 📚 Compliance Rules

The system validates documents against multiple rule categories:

- **General Rules**: Disclaimer requirements, data attribution, glossary inclusion
- **ESG Rules**: ESG-specific compliance and disclaimers
- **Performance Rules**: Performance disclosure and historical data requirements
- **Prospectus Rules**: Consistency with fund prospectus documents
- **Structure Rules**: Document format and structure requirements
- **Values Rules**: Value-related disclosures and requirements

Rules are stored as JSON configurations in `data/rules/` and can be customized per deployment.

## 🔧 Configuration

Configuration files are located in the `config/` directory. Adjust settings for:
- Document processing parameters
- AI model selection and parameters
- Rule strictness levels
- Output formatting

## 📖 API Documentation

Once the API is running, access the interactive documentation at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 🧪 Testing

Run tests with:
```bash
python -m pytest src/
```

## 🛠️ Technology Stack

### Backend
- **FastAPI**: Modern Python web framework
- **Pydantic**: Data validation
- **OpenAI**: Generative AI integration
- **python-pptx**: PowerPoint reading and manipulation
- **python-docx**: Word document processing
- **pandas**: Data manipulation
- **openpyxl**: Excel file handling

### Frontend
- **React**: JavaScript UI framework
- **lucide-react**: Icon library
- **React Scripts**: Build tools

## 📝 Document Support

Supported document formats:
- PowerPoint (.pptx)
- Word documents (.docx)
- PDF (with additional processing)
- Structured data (JSON, CSV)

## 🔐 Data Management

- **Extracted Data**: Processed document content stored in `data/extracted/`
- **Reference Data**: Registration files and product metadata in `data/references/`
- **Metadata**: Document metadata and processing information

## 🤝 Contributing

1. Create a feature branch
2. Make your changes
3. Test thoroughly
4. Submit a pull request

## 📄 License

[Specify your license here]

## 📧 Contact

For questions or support, please contact the development team.

---

**Note**: This project uses GenAI capabilities. Ensure compliance with applicable regulations and data protection laws when processing marketing documents.
