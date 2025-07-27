import os
import json
from pathlib import Path
from src.pdf_processor import PDFProcessor
from src.heading_detector import HeadingDetector

def process_single_pdf(input_path: str, output_path: str):
    """Process a single PDF file"""
    try:
        # Initialize processors
        pdf_processor = PDFProcessor()
        heading_detector = HeadingDetector()
        
        # Extract text with font information
        text_blocks = pdf_processor.extract_text_with_fonts(input_path)
        
        # Detect title
        title = pdf_processor.detect_title(text_blocks)
        
        # Detect headings
        headings = heading_detector.detect_headings(text_blocks)
        
        # Create output JSON
        output_data = {
            "title": title,
            "outline": headings
        }
        
        # Write to output file
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        print(f"Successfully processed: {input_path}")
        
    except Exception as e:
        print(f"Error processing {input_path}: {str(e)}")

def main():
    """Main function to process all PDFs in input directory"""
    input_dir = Path("input")
    output_dir = Path("output")
    
    # Create output directory if it doesn't exist
    output_dir.mkdir(exist_ok=True)
    
    # Process all PDF files
    for pdf_file in input_dir.glob("*.pdf"):
        output_file = output_dir / f"{pdf_file.stem}.json"
        process_single_pdf(str(pdf_file), str(output_file))

if __name__ == "__main__":
    main()
