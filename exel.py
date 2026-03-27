import pandas as pd
import sys
import os

def extract_excel_content(file_path, output_file=None):
    """
    Extract content from an Excel file and format it for AI analysis.
    
    Args:
        file_path: Path to the Excel file
        output_file: Optional path to save the output text file
    """
    try:
        # Read the Excel file (supports .xlsx, .xls)
        excel_file = pd.ExcelFile(file_path)
        
        output = []
        output.append(f"=== Excel File: {os.path.basename(file_path)} ===\n")
        output.append(f"Number of sheets: {len(excel_file.sheet_names)}\n")
        output.append(f"Sheet names: {', '.join(excel_file.sheet_names)}\n")
        output.append("="*60 + "\n\n")
        
        # Process each sheet
        for sheet_name in excel_file.sheet_names:
            df = pd.read_excel(file_path, sheet_name=sheet_name)
            
            output.append(f"\n{'='*60}")
            output.append(f"\nSHEET: {sheet_name}")
            output.append(f"\n{'='*60}\n")
            output.append(f"Dimensions: {df.shape[0]} rows × {df.shape[1]} columns\n")
            output.append(f"Columns: {', '.join(df.columns.astype(str))}\n\n")
            
            # Display data in a readable format
            output.append("DATA:\n")
            output.append("-"*60 + "\n")
            output.append(df.to_string(index=False))
            output.append("\n" + "-"*60 + "\n")
            
            # Add summary statistics for numeric columns
            numeric_cols = df.select_dtypes(include=['number']).columns
            if len(numeric_cols) > 0:
                output.append("\nSUMMARY STATISTICS (numeric columns):\n")
                output.append(df[numeric_cols].describe().to_string())
                output.append("\n")
            
            # Show any null values
            null_counts = df.isnull().sum()
            if null_counts.sum() > 0:
                output.append("\nMISSING VALUES:\n")
                for col, count in null_counts[null_counts > 0].items():
                    output.append(f"  {col}: {count} missing values\n")
        
        # Combine all output
        result = ''.join(output)
        
        # Print to console
        print(result)
        
        # Save to file if specified
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(result)
            print(f"\n\n✓ Content saved to: {output_file}")
        
        return result
        
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        sys.exit(1)
    except Exception as e:
        print(f"Error processing file: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    # Check command line arguments
    if len(sys.argv) < 2:
        print("Usage: python excel_extractor.py <excel_file> [output_file]")
        print("\nExample:")
        print("  python excel_extractor.py data.xlsx")
        print("  python excel_extractor.py data.xlsx output.txt")
        sys.exit(1)
    
    excel_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    extract_excel_content(excel_file, output_file)