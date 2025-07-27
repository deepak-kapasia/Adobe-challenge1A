import fitz  # PyMuPDF
import json
import re
from typing import List, Dict, Tuple

class PDFProcessor:
    def __init__(self):
        self.font_sizes = {}
        self.headings = []
    
    def extract_text_with_fonts(self, pdf_path: str) -> List[Dict]:
        """Extract text with font information from PDF"""
        doc = fitz.open(pdf_path)
        text_blocks = []
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            blocks = page.get_text("dict")
            
            for block in blocks["blocks"]:
                if "lines" in block:
                    for line in block["lines"]:
                        for span in line["spans"]:
                            text_blocks.append({
                                "text": span["text"].strip(),
                                "font_size": span["size"],
                                "font_flags": span["flags"],
                                "page": page_num + 1,
                                "bbox": span["bbox"]
                            })
        
        doc.close()
        return text_blocks
    
    def detect_title(self, text_blocks: List[Dict]) -> str:
        """Detect document title - usually largest font on first page"""
        first_page_blocks = [b for b in text_blocks if b["page"] == 1]
        if not first_page_blocks:
            return "Untitled Document"
        
        # Filter out non-title candidates (dashes, single characters, etc.)
        def is_title_candidate(text: str) -> bool:
            text = text.strip()
            # Skip if it's just dashes
            if text == '-' * len(text):
                return False
            # Skip if it's empty
            if not text:
                return False
            # Skip if it's just repeated characters (like "RRRR")
            if len(set(text)) == 1 and len(text) > 2:
                return False
            # Skip if it's just repeated words
            words = text.split()
            if len(words) > 1 and len(set(words)) == 1:
                return False
            return True
        
        # Try to find a complete title by combining large font text blocks
        def find_complete_title():
            # First, try to find a good subtitle (usually more reliable)
            subtitle_blocks = [
                block for block in first_page_blocks 
                if block["font_size"] >= 20 and block["font_size"] <= 28 and is_title_candidate(block["text"])
            ]
            
            if len(subtitle_blocks) >= 2:
                # Group by vertical position (within 15 points)
                vertical_groups = {}
                for block in subtitle_blocks:
                    y_pos = round(block["bbox"][1] / 15) * 15  # Round to nearest 15
                    if y_pos not in vertical_groups:
                        vertical_groups[y_pos] = []
                    vertical_groups[y_pos].append(block)
                
                # Find the group with the most blocks (likely the subtitle)
                best_group = max(vertical_groups.values(), key=len)
                if len(best_group) >= 2:  # Need at least 2 parts for a good title
                    # Sort by horizontal position to maintain reading order
                    best_group.sort(key=lambda x: x["bbox"][0])
                    
                    # Remove duplicate text blocks at the same position
                    unique_blocks = []
                    seen_positions = set()
                    for block in best_group:
                        pos_key = (round(block["bbox"][0]), round(block["bbox"][1]))
                        if pos_key not in seen_positions:
                            seen_positions.add(pos_key)
                            unique_blocks.append(block)
                    
                    combined_title = " ".join([block["text"].strip() for block in unique_blocks])
                    if len(combined_title) > 20:  # Ensure it's substantial
                        return clean_title_text(combined_title)
            
            # Fallback to original method
            large_font_blocks = [
                block for block in first_page_blocks 
                if block["font_size"] >= 18 and is_title_candidate(block["text"])
            ]
            
            if len(large_font_blocks) >= 2:
                # Group by vertical position (within 15 points)
                vertical_groups = {}
                for block in large_font_blocks:
                    y_pos = round(block["bbox"][1] / 15) * 15  # Round to nearest 15
                    if y_pos not in vertical_groups:
                        vertical_groups[y_pos] = []
                    vertical_groups[y_pos].append(block)
                
                # Find the group with the most blocks (likely the title)
                best_group = max(vertical_groups.values(), key=len)
                if len(best_group) >= 2:  # Need at least 2 parts for a good title
                    # Sort by horizontal position to maintain reading order
                    best_group.sort(key=lambda x: x["bbox"][0])
                    
                    # Remove duplicate text blocks at the same position
                    unique_blocks = []
                    seen_positions = set()
                    for block in best_group:
                        pos_key = (round(block["bbox"][0]), round(block["bbox"][1]))
                        if pos_key not in seen_positions:
                            seen_positions.add(pos_key)
                            unique_blocks.append(block)
                    
                    combined_title = " ".join([block["text"].strip() for block in unique_blocks])
                    if len(combined_title) > 10:  # Ensure it's substantial
                        return clean_title_text(combined_title)
            
            return None
        
        def clean_title_text(text: str) -> str:
            """Clean up title text by removing repetitions and fixing common issues"""
            # Remove repeated characters (like "RRRR" -> "R")
            import re
            text = re.sub(r'(.)\1{2,}', r'\1', text)
            
            # Remove repeated words
            words = text.split()
            cleaned_words = []
            for i, word in enumerate(words):
                if i == 0 or word != words[i-1]:
                    cleaned_words.append(word)
            
            # Fix common OCR issues
            text = " ".join(cleaned_words)
            text = re.sub(r'eee+', 'e', text)  # Fix "Reeeequest" -> "Request"
            text = re.sub(r'ooo+', 'o', text)  # Fix "foooor" -> "for"
            text = re.sub(r'rr+', 'r', text)   # Fix "rr" -> "r"
            

            
            return text
        
        # Try to find a complete title first
        complete_title = find_complete_title()
        if complete_title:
            return complete_title
        
        # Fallback to single largest font size
        max_font_size = max(block["font_size"] for block in first_page_blocks)
        title_candidates = [
            block for block in first_page_blocks 
            if block["font_size"] == max_font_size and is_title_candidate(block["text"])
        ]
        
        if title_candidates:
            return title_candidates[0]["text"]
        
        # If no good candidates at max font size, try second largest
        font_sizes = sorted(set(block["font_size"] for block in first_page_blocks), reverse=True)
        if len(font_sizes) > 1:
            second_largest = font_sizes[1]
            title_candidates = [
                block for block in first_page_blocks 
                if block["font_size"] == second_largest and is_title_candidate(block["text"])
            ]
            if title_candidates:
                return title_candidates[0]["text"]
        
        return "Untitled Document"
