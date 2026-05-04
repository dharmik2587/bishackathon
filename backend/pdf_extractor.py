#!/usr/bin/env python3
"""
Extract BIS standards from SP 21:2005 PDF
Converts PDF to structured JSON format for RAG engine
"""

import pdfplumber
import json
import re
import sys
from typing import List, Dict
from pathlib import Path


class BISStandardsExtractor:
    """Extract Indian Standards from SP 21:2005 document"""
    
    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        self.standards = []
        self.current_section = None
        self.section_counter = 0
        
    def extract(self) -> List[Dict]:
        """Main extraction method"""
        print(f"Reading PDF: {self.pdf_path}")
        
        with pdfplumber.open(self.pdf_path) as pdf:
            total_pages = len(pdf.pages)
            print(f"Total pages: {total_pages}")
            
            full_text_lines = []
            for page_num, page in enumerate(pdf.pages):
                if page_num % 100 == 0:
                    print(f"  Processing page {page_num + 1}/{total_pages}...")
                
                text = page.extract_text()
                if text:
                    for line in text.split('\n'):
                        full_text_lines.append(line.strip())
        
        print(f"  Total lines extracted: {len(full_text_lines)}")
        self._parse_all_lines(full_text_lines)
        
        print(f"Extraction complete: Found {len(self.standards)} standards")
        return self.standards
    
    def _parse_all_lines(self, lines: List[str]):
        """Parse all lines for sections and standards"""
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            # Detect section headers - "SECTION X" or "SECTION X Title"
            section_match = re.match(
                r'^SECTION\s+(\d+(?:\.\d+)?)\s*[.:\-]?\s*(.*?)$',
                line,
                re.IGNORECASE
            )
            if section_match:
                self.section_counter += 1
                sec_num = section_match.group(1)
                sec_title = section_match.group(2).strip()
                # If title is empty, try next line
                if not sec_title and i + 1 < len(lines):
                    next_line = lines[i + 1].strip()
                    if next_line and not re.match(r'^(IS\s+\d|SECTION)', next_line):
                        sec_title = next_line
                
                self.current_section = {
                    'number': sec_num,
                    'title': sec_title
                }
                i += 1
                continue
            
            # Detect IS standards with various formats
            # Try to match IS codes with parts and years
            standard_patterns = [
                # IS 2185 (Part 2): 1983 - Title
                r'^(IS\s+\d{1,5}\s*\(Part\s*\d+\)\s*:\s*\d{4})\s*[-–:,]\s*(.*?)$',
                # IS 269: 1989 - Title  
                r'^(IS\s+\d{1,5}\s*:\s*\d{4})\s*[-–:,]\s*(.*?)$',
                # IS 2185 (Part 2): 1983 Title (no dash)
                r'^(IS\s+\d{1,5}\s*\(Part\s*\d+\)\s*:\s*\d{4})\s+(.*?)$',
                # IS 269: 1989 Title (no dash, just space)
                r'^(IS\s+\d{1,5}\s*:\s*\d{4})\s+(.*?)$',
                # IS 1489 (Part 2) without year followed by dash/colon
                r'^(IS\s+\d{1,5}\s*\(Part\s*\d+\))\s*[-–:]\s*(.*?)$',
            ]
            
            matched = False
            for pattern in standard_patterns:
                standard_match = re.match(pattern, line)
                if standard_match:
                    standard_code = standard_match.group(1).strip()
                    title = standard_match.group(2).strip()
                    
                    # Clean trailing section numbers from title (e.g., "1.5", "1.10")
                    title = re.sub(r'\s+\d+\.\d+\s*$', '', title)
                    title = re.sub(r'\s+\d+\s*$', '', title)
                    
                    if not title or len(title) < 3:
                        i += 1
                        matched = True
                        break
                    
                    # Get description from next lines
                    description = self._extract_description(lines, i)
                    
                    normalized_code = self._normalize_code(standard_code)
                    
                    std_id = normalized_code.lower().replace(' ', '-').replace(':', '-').replace('(', '').replace(')', '')
                    
                    standard_obj = {
                        'id': f"is-{std_id}",
                        'standardNumber': normalized_code,
                        'title': title,
                        'section': self._get_section_label(),
                        'category': self._get_category(),
                        'description': description,
                        'keywords': self._extract_keywords(title + ' ' + description + ' ' + normalized_code),
                        'contextChunks': [f"{normalized_code}: {title}"]
                    }
                    
                    # Avoid duplicates
                    if not any(s['standardNumber'] == standard_obj['standardNumber'] for s in self.standards):
                        self.standards.append(standard_obj)
                    
                    matched = True
                    break
            
            # Handle multi-part standards split across lines
            if not matched and self.current_section:
                # Pattern: "IS 1489 : Portland pozzolana cement" or "IS 2185 Concrete masonry units:"
                # followed by "(Part 1) : 1991 Fly ash based ..."
                #            "(Part 2) : 1991 Calcined clay based ..."
                is_header_match = re.match(r'^(IS\s+\d{1,5})\s*[:\s]+(.*?)$', line)
                if is_header_match:
                    base_code = is_header_match.group(1).strip()
                    base_title = is_header_match.group(2).strip().rstrip(':')
                    
                    # Look ahead for (Part X) lines
                    j = i + 1
                    found_parts = False
                    while j < min(i + 10, len(lines)):
                        next_line = lines[j].strip()
                        part_match = re.match(r'^\(Part\s*(\d+)\)\s*:\s*(\d{4})\s*(.*?)$', next_line)
                        if part_match:
                            found_parts = True
                            part_num = part_match.group(1)
                            year = part_match.group(2)
                            part_title = part_match.group(3).strip()
                            # Clean trailing numbers
                            part_title = re.sub(r'\s+\d+\.\d+\s*$', '', part_title)
                            part_title = re.sub(r'\s+\d+\s*$', '', part_title)
                            
                            full_code = f"{base_code} (Part {part_num}): {year}"
                            full_title = f"{base_title} - {part_title}" if part_title else base_title
                            full_title = full_title.strip(' -')
                            
                            if full_title and len(full_title) >= 3:
                                normalized_code = self._normalize_code(full_code)
                                std_id = normalized_code.lower().replace(' ', '-').replace(':', '-').replace('(', '').replace(')', '')
                                
                                description = self._extract_description(lines, j)
                                
                                standard_obj = {
                                    'id': f"is-{std_id}",
                                    'standardNumber': normalized_code,
                                    'title': full_title,
                                    'section': self._get_section_label(),
                                    'category': self._get_category(),
                                    'description': description,
                                    'keywords': self._extract_keywords(full_title + ' ' + description + ' ' + normalized_code),
                                    'contextChunks': [f"{normalized_code}: {full_title}"]
                                }
                                
                                if not any(s['standardNumber'] == standard_obj['standardNumber'] for s in self.standards):
                                    self.standards.append(standard_obj)
                            j += 1
                        elif found_parts:
                            # Stop if we found parts and now hit non-part line
                            break
                        else:
                            # Check if next line is empty or continuation
                            if not next_line or re.match(r'^(IS\s+\d|SECTION)', next_line, re.IGNORECASE):
                                break
                            j += 1
                    
                    if found_parts:
                        i = j
                        continue
            
            i += 1
    
    def _get_section_label(self) -> str:
        if self.current_section:
            title = self.current_section['title']
            num = self.current_section['number']
            if title:
                return f"{num}. {title}"
            return f"Section {num}"
        return "General"
    
    def _get_category(self) -> str:
        if self.current_section:
            return self._map_to_category(
                self.current_section['title'], 
                self.current_section['number']
            )
        return 'Building Materials'
    
    def _normalize_code(self, code: str) -> str:
        """Normalize standard code format to match expected format like 'IS 269: 1989'"""
        code = re.sub(r'\s+', ' ', code).strip()
        # Ensure format with single space after colon: IS 269: 1989
        code = re.sub(r'\s*:\s*', ': ', code)
        # Normalize Part formatting
        code = re.sub(r'\(\s*Part\s*', '(Part ', code)
        code = re.sub(r'\s*\)', ')', code)
        return code
    
    def _extract_description(self, lines: List[str], start_idx: int) -> str:
        """Extract description from following lines"""
        description_lines = []
        
        for j in range(start_idx + 1, min(start_idx + 10, len(lines))):
            line = lines[j].strip()
            
            if not line or len(line) < 5:
                continue
            if re.match(r'^(IS\s+\d|SECTION)', line, re.IGNORECASE):
                break
            # Skip page headers/footers
            if "SP 21" in line or re.match(r'^\d+$', line):
                continue
            
            description_lines.append(line)
            if len(description_lines) >= 4:
                break
        
        description = ' '.join(description_lines)
        return description[:500] if description else ''
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract keywords from title and description"""
        keywords = set()
        
        material_keywords = [
            'cement', 'concrete', 'steel', 'wood', 'timber', 'brick', 'stone',
            'pipe', 'cable', 'wire', 'glass', 'plastic', 'gypsum', 'lime', 'mortar',
            'bitumen', 'tar', 'tile', 'panel', 'paint', 'varnish', 'plaster',
            'water', 'sanitary', 'fixture', 'hardware', 'bolt', 'fastener', 'nail',
            'adhesive', 'sealant', 'insulation', 'roofing', 'waterproofing',
            'aggregate', 'sand', 'gravel', 'asbestos', 'portland', 'slag',
            'pozzolana', 'masonry', 'reinforcement', 'precast', 'prestressed',
            'hollow', 'block', 'sheet', 'corrugated', 'flat', 'floor', 'wall',
            'door', 'window', 'shutter', 'fitting', 'valve', 'tank', 'cistern',
            'rope', 'chain', 'rivet', 'screw', 'hinge', 'lock', 'handle',
            'aluminium', 'aluminum', 'copper', 'zinc', 'iron', 'lead', 'alloy',
            'galvanized', 'coated', 'plated', 'welding', 'electrode',
            'structural', 'reinforced', 'deformed', 'bar', 'rod', 'section',
            'angle', 'channel', 'beam', 'column', 'plate', 'strip',
            'conductor', 'pvc', 'xlpe', 'polyethylene', 'rubber',
            'enamel', 'lacquer', 'primer', 'putty', 'polish', 'distemper',
            'marble', 'granite', 'slate', 'limestone', 'sandstone',
            'plywood', 'particle', 'fibre', 'board', 'veneer', 'bamboo',
            'clay', 'ceramic', 'porcelain', 'earthenware', 'stoneware',
            'terrazzo', 'mosaic', 'linoleum', 'carpet', 'felt',
            'white', 'ordinary', 'rapid', 'sulphate', 'supersulphated',
            'marine', 'decorative', 'architectural',
            'specification', 'grade', 'lightweight', 'heavyweight',
            'density', 'absorption', 'tensile', 'compression',
            'strength', 'resistance', 'fire', 'thermal', 'acoustic',
            'corrosion', 'durability', 'hardness', 'impact',
        ]
        
        text_lower = text.lower()
        
        for keyword in material_keywords:
            if len(keyword) > 2 and keyword in text_lower:
                keywords.add(keyword)
        
        return sorted(list(keywords))[:15]
    
    def _map_to_category(self, section_title: str, section_number: str) -> str:
        """Map section title/number to category"""
        section_lower = (section_title or '').lower()
        sec_num = section_number.strip()
        
        # Use section number as primary mapping for SP 21:2005
        section_num_map = {
            '1': 'Cement & Concrete',
            '2': 'Building Limes',
            '3': 'Stones',
            '4': 'Clay Products',
            '5': 'Gypsum Products',
            '6': 'Wood & Timber',
            '7': 'Bitumen & Tar',
            '8': 'Flooring & Finishes',
            '9': 'Waterproofing',
            '10': 'Plumbing & Water',
            '11': 'Hardware & Fasteners',
            '12': 'Wood Products',
            '13': 'Doors & Windows',
            '14': 'Steel & Metals',
            '15': 'Steel & Metals',
            '16': 'Steel & Metals',
            '17': 'Steel & Metals',
            '18': 'Welding',
            '19': 'Hardware & Fasteners',
            '20': 'Steel & Metals',
            '21': 'Glass',
            '22': 'Chemical Products',
            '23': 'Building Materials',
            '24': 'Plastics',
            '25': 'Electrical',
            '26': 'Electrical',
            '27': 'Building Materials',
        }
        
        if sec_num in section_num_map:
            return section_num_map[sec_num]
        
        # Fallback to keyword-based
        if any(w in section_lower for w in ['cement', 'concrete', 'aggregate']):
            return 'Cement & Concrete'
        elif any(w in section_lower for w in ['lime']):
            return 'Building Limes'
        elif any(w in section_lower for w in ['stone']):
            return 'Stones'
        elif any(w in section_lower for w in ['wood', 'timber', 'plywood', 'bamboo']):
            return 'Wood & Timber'
        elif any(w in section_lower for w in ['gypsum']):
            return 'Gypsum Products'
        elif any(w in section_lower for w in ['bitumen', 'tar', 'waterproof']):
            return 'Bitumen & Tar'
        elif any(w in section_lower for w in ['steel', 'metal', 'aluminum', 'aluminium', 'iron']):
            return 'Steel & Metals'
        elif any(w in section_lower for w in ['cable', 'conductor', 'wire', 'electrical']):
            return 'Electrical'
        elif any(w in section_lower for w in ['water', 'sanitary', 'pipe', 'plumbing']):
            return 'Plumbing & Water'
        elif any(w in section_lower for w in ['paint', 'varnish', 'coating', 'enamel', 'lacquer']):
            return 'Paints & Coatings'
        elif any(w in section_lower for w in ['door', 'window', 'shutter']):
            return 'Doors & Windows'
        elif any(w in section_lower for w in ['floor', 'wall', 'roof', 'tile', 'ceiling']):
            return 'Flooring & Finishes'
        elif any(w in section_lower for w in ['hardware', 'fastener', 'bolt', 'rivet', 'screw']):
            return 'Hardware & Fasteners'
        elif any(w in section_lower for w in ['glass']):
            return 'Glass'
        elif any(w in section_lower for w in ['plastic', 'pvc', 'polymer']):
            return 'Plastics'
        else:
            return 'Building Materials'


def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Extract BIS standards from SP 21:2005 PDF'
    )
    
    parser.add_argument('--input', type=str, required=True, help='Path to input PDF file')
    parser.add_argument('--output', type=str, default='standards.json', help='Output JSON file')
    parser.add_argument('--verbose', action='store_true', help='Print verbose output')
    
    args = parser.parse_args()
    
    if not Path(args.input).exists():
        print(f"Error: Input file not found: {args.input}")
        sys.exit(1)
    
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        extractor = BISStandardsExtractor(args.input)
        standards = extractor.extract()
        
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(standards, f, indent=2, ensure_ascii=False)
        
        print(f"\nSuccessfully extracted {len(standards)} standards")
        print(f"Saved to: {args.output}")
        
        categories = {}
        for std in standards:
            cat = std['category']
            categories[cat] = categories.get(cat, 0) + 1
        
        print(f"\nCategory breakdown:")
        for cat, count in sorted(categories.items()):
            print(f"  {cat}: {count}")
        
        if standards:
            print(f"\nSample standards:")
            for std in standards[:5]:
                print(f"  {std['standardNumber']}: {std['title'][:80]}")
        
        sys.exit(0)
        
    except Exception as e:
        print(f"Error during extraction: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
