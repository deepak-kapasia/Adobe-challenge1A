import re
from typing import List, Dict

class HeadingDetector:
    def __init__(self):
        self.heading_patterns = [
            r'^\d+\.\s+',  # 1. 2. 3.
            r'^\d+\.\d+\s+',  # 1.1 1.2
            r'^\d+\.\d+\.\d+\s+',  # 1.1.1 1.1.2
            r'^[A-Z][A-Z\s]+$',  # ALL CAPS
            r'^Chapter\s+\d+',  # Chapter 1, Chapter 2
            r'^Section\s+\d+',  # Section 1, Section 2
        ]
    
    def analyze_font_hierarchy(self, text_blocks: List[Dict]) -> Dict[float, str]:
        """Analyze font sizes to determine heading levels"""
        font_sizes = {}
        for block in text_blocks:
            size = block["font_size"]
            if size not in font_sizes:
                font_sizes[size] = []
            font_sizes[size].append(block["text"])
        
        # Sort font sizes in descending order
        sorted_sizes = sorted(font_sizes.keys(), reverse=True)
        
        # Map font sizes to heading levels with better logic
        size_to_level = {}
        
        # Skip the largest font size (likely title)
        if len(sorted_sizes) > 0:
            # Second largest font size is usually H1
            if len(sorted_sizes) > 1:
                size_to_level[sorted_sizes[1]] = "H1"
            
            # Third largest font size is usually H2
            if len(sorted_sizes) > 2:
                size_to_level[sorted_sizes[2]] = "H2"
            
            # Fourth largest font size is usually H3
            if len(sorted_sizes) > 3:
                size_to_level[sorted_sizes[3]] = "H3"
            
            # Fifth largest font size is usually H4
            if len(sorted_sizes) > 4:
                size_to_level[sorted_sizes[4]] = "H4"
        
        return size_to_level
    
    def detect_headings(self, text_blocks: List[Dict]) -> List[Dict]:
        """Detect headings based on font size and patterns"""
        size_to_level = self.analyze_font_hierarchy(text_blocks)
        headings = []
        
        # Group text blocks by font size and proximity
        grouped_blocks = self.group_related_text_blocks(text_blocks)
        
        for group in grouped_blocks:
            if not group:
                continue
                
            # Combine text from the group
            combined_text = " ".join([block["text"].strip() for block in group if block["text"].strip()])
            font_size = group[0]["font_size"]
            page = group[0]["page"]
            
            # Skip empty, very short text, or text that's too long to be a heading
            if len(combined_text) < 3 or len(combined_text) > 200:
                continue
            
            # Skip text that looks like body text (contains too many words)
            if len(combined_text.split()) > 15:
                continue
            
            # Check if font size indicates heading
            if font_size in size_to_level:
                level = size_to_level[font_size]
                if level in ["H1", "H2", "H3"]:
                    headings.append({
                        "level": level,
                        "text": self.clean_heading_text(combined_text),
                        "page": page
                    })
            
            # Check pattern-based detection
            elif self.matches_heading_pattern(combined_text):
                level = self.determine_level_from_pattern(combined_text)
                headings.append({
                    "level": level,
                    "text": self.clean_heading_text(combined_text),
                    "page": page
                })
        
        return self.deduplicate_headings(headings)
    
    def matches_heading_pattern(self, text: str) -> bool:
        """Check if text matches common heading patterns"""
        for pattern in self.heading_patterns:
            if re.match(pattern, text):
                return True
        return False
    
    def determine_level_from_pattern(self, text: str) -> str:
        """Determine heading level based on numbering pattern"""
        if re.match(r'^\d+\.\d+\.\d+\s+', text):
            return "H3"
        elif re.match(r'^\d+\.\d+\s+', text):
            return "H2"
        elif re.match(r'^\d+\.\s+', text):
            return "H1"
        else:
            return "H2"  # Default
    
    def clean_heading_text(self, text: str) -> str:
        """Clean heading text by removing numbering"""
        # Remove common numbering patterns
        text = re.sub(r'^\d+\.\d+\.\d+\s*', '', text)
        text = re.sub(r'^\d+\.\d+\s*', '', text)
        text = re.sub(r'^\d+\.\s*', '', text)
        return text.strip()
    
    def group_related_text_blocks(self, text_blocks: List[Dict]) -> List[List[Dict]]:
        """Group text blocks that are likely part of the same heading or sentence"""
        if not text_blocks:
            return []
        
        # Sort blocks by page and vertical position
        sorted_blocks = sorted(text_blocks, key=lambda x: (x["page"], x["bbox"][1], x["bbox"][0]))
        
        groups = []
        current_group = []
        
        for i, block in enumerate(sorted_blocks):
            if not current_group:
                current_group = [block]
                continue
            
            prev_block = current_group[-1]
            
            # Check if blocks should be grouped together
            should_group = (
                # Same page
                block["page"] == prev_block["page"] and
                # Same font size (within small tolerance)
                abs(block["font_size"] - prev_block["font_size"]) < 0.5 and
                # Close vertical position (within 10 points)
                abs(block["bbox"][1] - prev_block["bbox"][1]) < 10 and
                # Not too far horizontally (within 100 points for more conservative grouping)
                abs(block["bbox"][0] - prev_block["bbox"][0]) < 100 and
                # Don't group if the combined text would be too long (likely not a heading)
                len(" ".join([b["text"] for b in current_group] + [block["text"]])) < 80
            )
            
            if should_group:
                current_group.append(block)
            else:
                if current_group:
                    groups.append(current_group)
                current_group = [block]
        
        # Add the last group
        if current_group:
            groups.append(current_group)
        
        return groups
    
    def deduplicate_headings(self, headings: List[Dict]) -> List[Dict]:
        """Remove duplicate headings"""
        seen = set()
        unique_headings = []
        
        for heading in headings:
            key = (heading["text"], heading["page"])
            if key not in seen:
                seen.add(key)
                unique_headings.append(heading)
        
        return unique_headings
