# Automated Compliance Check

A comprehensive workflow that validates marketing presentations and documents against multiple compliance rules. The tool automatically reviews documents, identifies infractions, and highlights violations for human review.

## Overview

This project provides an automated compliance validation system designed to:
- Parse marketing presentations and JSON documents
- Validate content against 8 different compliance modules
- Generate consolidated violation reports
- Highlight specific infractions for review

## Features

- **Multi-Module Validation**: 8 comprehensive compliance checkers
  - Structure Validation
  - Registration Requirements
  - ESG (Environmental, Social, Governance) Rules
  - Disclaimers Compliance
  - Performance Disclosure
  - Value Proposition Rules
  - Prospectus Compliance
  - General Regulatory Rules

- **AI-Powered Analysis**: Uses TokenFactory API with Llama-3.1-70B-Instruct
- **Consolidated Reporting**: Consolidates all violations into a single report
- **PowerPoint Integration**: Optimized for highlighting and commenting in presentations
- **JSON-based Rules**: Easy to modify and extend compliance rules

## Project Structure

```
├── run_all_compliance_checks.py   # Master compliance runner orchestrating all modules
├── test_structure.py              # Document structure validation
├── test_registration.py           # Registration compliance checks
├── test_esg.py                    # ESG rules validation
├── test_disclaimers.py            # Disclaimers compliance
├── test_performance.py            # Performance disclosure validation
├── test_values.py                 # Value proposition checks
├── test_prospectus.py             # Prospectus compliance
├── test_general_rules.py          # General regulatory rules
├── load_env.py                    # Environment variable loader
├── esg_rules.json                 # ESG compliance rules
├── general_rules.json             # General regulatory rules
├── performance_rules.json         # Performance disclosure rules
├── prospectus_rules.json          # Prospectus compliance rules
├── structure_rules.json           # Structure validation rules
├── values_rules.json              # Value proposition rules
├── disclaimers.csv                # Disclaimer requirements database
├── registration.csv               # Registration requirements database
├── metadata.json                  # Document metadata template
├── exemple.json                   # Example document for testing
└── README.md                      # This file
```

## Prerequisites

- Python 3.7+
- `httpx` library for HTTP requests
- `openai` library for API integration
- Valid TokenFactory API key

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Automated-Compliance-Check
   ```

2. **Create a Python virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install httpx openai
   ```

4. **Configure API credentials**
   Create a `.env` file in the project root:
   ```
   TOKENFACTORY_API_KEY=your-api-key-here
   ```

## Usage

### Basic Compliance Check

```bash
python run_all_compliance_checks.py <document.json> <presentation.docx> <metadata.json>
```

### Example

```bash
python run_all_compliance_checks.py exemple.json prospectus.docx metadata.json
```

### Input Files

1. **Document JSON** (`exemple.json`): Contains the document content to validate
2. **Presentation** (`prospectus.docx`): The source presentation for highlighted violations
3. **Metadata** (`metadata.json`): Document metadata and context

### Output

The tool generates a consolidated violation report containing:
- Document identifiers
- Violation details (category, severity, description)
- Location information for highlighting
- Consolidated violations across all 8 compliance modules

## Configuration

### Compliance Rules

Each compliance module uses JSON rule files:

- **esg_rules.json**: ESG disclosure requirements
- **general_rules.json**: General regulatory compliance
- **performance_rules.json**: Performance disclosure requirements
- **prospectus_rules.json**: Prospectus filing requirements
- **structure_rules.json**: Document structure requirements
- **values_rules.json**: Value proposition guidelines

### Disclaimer & Registration Databases

- **disclaimers.csv**: Required disclaimer statements
- **registration.csv**: Registration required fields and checks

## API Integration

The project uses **TokenFactory API** with the **Llama-3.1-70B-Instruct** model for NLP-based compliance validation.

### API Configuration

See `load_env.py` for environment variable loading mechanism.

## Testing

The project includes individual test scripts for each compliance module:

```bash
python test_structure.py
python test_registration.py
python test_esg.py
python test_disclaimers.py
python test_performance.py
python test_values.py
python test_prospectus.py
python test_general_rules.py
```

## Workflow

1. **Document Parsing**: Load JSON document and metadata
2. **Multi-Module Validation**: Run through all 8 compliance checkers
3. **Violation Detection**: Identify infractions against each rule set
4. **Report Consolidation**: Merge violations from all modules
5. **PowerPoint Output**: Generate highlighted violations for presentation

## Error Handling

The system includes comprehensive error handling:
- File validation (JSON parsing, encoding)
- API connectivity checks
- Rule validation
- Detailed error reporting with traceback information

## Development

To add a new compliance module:

1. Create a `test_<module_name>.py` file
2. Implement the validation logic
3. Return violations in the standard format
4. Update `run_all_compliance_checks.py` to include the new module
5. Add corresponding rule file (`<module_name>_rules.json`)

## Contributing

When contributing to this project:
- Ensure all 8 compliance modules are tested
- Update rule files as needed
- Follow the existing code structure and naming conventions
- Test with the example documents before submitting

## Environment Variables

Required environment variables (in `.env` file):
- `TOKENFACTORY_API_KEY`: Your TokenFactory API key for accessing the Llama model

## Troubleshooting

### Common Issues

1. **Missing .env file**: Create a `.env` file with your API key
2. **Missing rule files**: Ensure all JSON rule files are in the project directory
3. **CSV encoding errors**: Ensure CSV files are UTF-8 encoded
4. **API errors**: Verify your TokenFactory API key is valid and has active quota

## License

[Add your license information here]

## Source

**GitHub Repository**: [Add your repository URL here]

## Support

For issues, questions, or suggestions, please [add contact information or issue template here].

## Changelog

### Version 1.0
- Initial release with 8 compliance modules
- Consolidated violation reporting
- PowerPoint integration support
