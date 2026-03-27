# PowerPoint Compliance Extractor

An intelligent PowerPoint extraction tool that uses LLM-powered parsing to extract compliance-relevant content from financial presentation documents.

## Overview

This project extracts structured data from PowerPoint presentations (specifically ODDO BHF fund presentations) and prepares it for compliance checking. It uses a two-stage approach:

1. **Raw Extraction**: Extracts all text, tables, charts, and formatting from PowerPoint files
2. **Intelligent Parsing**: Uses LLM to identify and extract only compliance-relevant raw text (no judgments)

## Features

- Extract text with formatting (bold, font size, color, position)
- Parse tables and identify headers
- Count visual elements (charts, images)
- LLM-powered intelligent parsing for compliance categories:
  - Cover page elements
  - Disclaimers and mandatory mentions
  - Performance sections
  - ESG content
  - Risk warnings (bold text)
  - Source citations
  - Fund characteristics

## Project Structure

```
.
├── app.py                  # Main extraction application
├── exel.py                 # Excel content extractor utility
├── index.html              # Spotify AI marketing presentation (demo)
├── metadata.json           # Document metadata configuration
├── metadata2.json          # Alternative metadata configuration
├── output/                 # Generated JSON extractions
│   ├── compliance_ready_extraction.json
│   └── compliance_ready_extraction2.json
├── Registration.xlsx       # Registration data
└── *.pptx                  # PowerPoint source files
```

## Requirements

```bash
pip install python-pptx openai httpx pandas openpyxl
```

## Usage

### PowerPoint Extraction

```python
from app import process_document

result = process_document(
    pptx_path="your-presentation.pptx",
    metadata_file="metadata.json",
    output_path="output/extraction.json",
    use_llm_parser=True,
    api_key="your-api-key"
)
```

### Excel Content Extraction

```bash
python exel.py Registration.xlsx output.txt
```

## Configuration

### Metadata File Format

```json
{
  "Société de Gestion": "ODDO BHF ASSET MANAGEMENT SAS",
  "Est ce que le produit fait partie de la Sicav d'Oddo": false,
  "Le client est-il un professionnel": false,
  "Le document fait-il référence à une nouvelle Stratégie": false,
  "Le document fait-il référence à un nouveau Produit": true
}
```

## Output Format

The tool generates structured JSON with:

- **document_info**: Filename, page count, extraction timestamp
- **cover_page**: Fund name, date, promotional mentions, warnings
- **slide_2_disclaimers**: Disclaimers, risk profiles, SRI mentions
- **content_pages**: Page-by-page parsed content
- **performance_sections**: All performance-related text
- **esg_content**: ESG and sustainability mentions
- **all_bold_text**: Risk warnings and emphasis
- **all_sources_citations**: Source attributions
- **user_metadata**: Custom metadata from config file

## LLM Integration

The tool uses a custom LLM endpoint for intelligent parsing:

- **Model**: Llama-3.1-70B-Instruct
- **Purpose**: Extract raw text only (no compliance judgments)
- **Temperature**: 0.1 (deterministic)
- **Max Tokens**: 2000

## Key Classes

### RawExtractor
Pure PowerPoint extraction without interpretation

### IntelligentParser
LLM-powered parsing to identify compliance-relevant sections

## Notes

- The tool extracts RAW TEXT ONLY - no compliance decisions are made
- Output is designed to feed into a separate compliance rule engine
- Supports French financial document formats
- Handles complex formatting, tables, and visual elements

## License

Internal use only
