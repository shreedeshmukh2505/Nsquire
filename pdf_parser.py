import re
import PyPDF2
import pandas as pd
from typing import Dict, List, Tuple, Optional
import logging
import json

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class EnhancedCollegeParser:
    def __init__(self):
        # Pattern to match college code and name (e.g., "01002 - Government College of Engineering, Amravati")
        # College codes are typically 5 digits and appear at the start of a section
        self.college_name_pattern = r'^(\d{5})\s*-\s*(.+?)(?=\n|$)'
        
        # Pattern to match branch code and name (e.g., "0100219110 - Civil Engineering")
        # Branch codes are typically 10 digits
        self.branch_pattern = r'(\d{10})\s*-\s*(.+?)(?=\n|$)'
        
        # Pattern to match status (e.g., "Status: Government Autonomous")
        self.status_pattern = r'Status:\s*(.+?)(?=\n|$)'
        
        # Pattern to match stage (e.g., "Stage I", "Stage I-Non PWD", "Stage VII")
        self.stage_pattern = r'Stage\s*([IVX]+)(?:-Non PWD)?'
        
        # Pattern to match category and cutoff data (e.g., "GOPENS: 33717 (88.6037289)")
        self.category_pattern = r'([A-Z]+):\s*(\d+)\s*\(([\d.]+)\)'
        
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extract text content from PDF file."""
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text()
                return text
        except Exception as e:
            logger.error(f"Error reading PDF: {e}")
            return ""
    
    def extract_colleges(self, text: str) -> List[Dict]:
        """Extract all colleges from text."""
        colleges = []
        
        # Split text into lines for better processing
        lines = text.split('\n')
        
        # Find potential college lines (lines that start with 5-digit codes)
        college_lines = []
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
            
            # Look for lines that start with 5-digit codes followed by dash and college name
            match = re.match(r'^(\d{5})\s*-\s*(.+)$', line)
            if match:
                college_lines.append((i, match.group(1), match.group(2).strip()))
        
        logger.info(f"Found {len(college_lines)} potential college lines")
        
        # Process each college
        for i, (line_index, college_code, college_name) in enumerate(college_lines):
            try:
                # Find the section for this college (from this line to the next college or end)
                start_line = line_index
                end_line = len(lines)
                
                # Look for the next college line
                if i + 1 < len(college_lines):
                    end_line = college_lines[i + 1][0]
                
                # Extract the section for this college
                college_section_lines = lines[start_line:end_line]
                college_section = '\n'.join(college_section_lines)
                
                # Extract branches for this college
                branches = self.extract_branches_for_college(college_section)
                
                colleges.append({
                    'college_code': college_code,
                    'college_name': college_name,
                    'branches': branches,
                    'total_branches': len(branches)
                })
                
                logger.info(f"Found college: {college_code} - {college_name} with {len(branches)} branches")
                
            except Exception as e:
                logger.error(f"Error parsing college {college_code} - {college_name}: {e}")
                continue
        
        return colleges
    
    def extract_branches_for_college(self, college_section: str) -> List[Dict]:
        """Extract branch information for a specific college."""
        branches = []
        
        # Find all branch codes and names in this college section
        branch_matches = re.finditer(self.branch_pattern, college_section)
        
        for match in branch_matches:
            try:
                branch_code = match.group(1)
                branch_name = match.group(2).strip()
                
                # Find the section for this branch (from this match to the next branch or end)
                start_pos = match.end()
                next_match = re.search(self.branch_pattern, college_section[start_pos:])
                if next_match:
                    end_pos = start_pos + next_match.start()
                else:
                    end_pos = len(college_section)
                
                branch_section = college_section[start_pos:end_pos]
                
                # Extract status
                status_match = re.search(self.status_pattern, branch_section)
                status = status_match.group(1).strip() if status_match else "Unknown"
                
                # Extract cutoff data
                cutoff_data = self.extract_cutoff_data(branch_section)
                
                branches.append({
                    'branch_code': branch_code,
                    'branch_name': branch_name,
                    'status': status,
                    'cutoff_data': cutoff_data
                })
                
                logger.debug(f"Found branch: {branch_code} - {branch_name} with {len(cutoff_data)} cutoff entries")
                
            except Exception as e:
                logger.error(f"Error parsing branch {match.group(0)}: {e}")
                continue
        
        return branches
    
    def extract_cutoff_data(self, section_text: str) -> List[Dict]:
        """Extract cutoff data from a branch section in table format."""
        cutoff_data = []
        
        # Split into lines and process each line
        lines = section_text.split('\n')
        
        logger.debug(f"Processing section with {len(lines)} lines for cutoff data")
        
        # Look for the "State Level" line which indicates the start of cutoff data
        state_level_index = -1
        for i, line in enumerate(lines):
            if 'State Level' in line:
                state_level_index = i
                break
        
        if state_level_index == -1:
            logger.debug("No 'State Level' found in section")
            return cutoff_data
        
        logger.debug(f"Found 'State Level' at line {state_level_index}")
        
        # Look for the categories line (usually after State Level)
        categories = []
        categories_line_index = -1
        
        for i in range(state_level_index + 1, min(state_level_index + 5, len(lines))):
            line = lines[i].strip()
            if not line:
                continue
            
            # Look for category patterns like GOPENS, GSCS, GNT3S, etc.
            # These are typically 4-6 character codes
            potential_categories = re.findall(r'\b[A-Z]{4,6}\b', line)
            if len(potential_categories) >= 3:  # Need at least 3 categories to be valid
                categories = potential_categories
                categories_line_index = i
                logger.debug(f"Found categories at line {i}: {categories}")
                break
        
        if not categories:
            logger.debug("No categories found")
            return cutoff_data
        
        # Now look for the data rows (stages with ranks and percentages)
        for i in range(categories_line_index + 1, len(lines)):
            line = lines[i].strip()
            if not line:
                continue
            
            # Look for stage information (I, II, III, etc.)
            stage_match = re.search(r'\b([IVX]+)(?:-Non\s+PWD)?\b', line)
            if stage_match:
                stage = stage_match.group(1)
                logger.debug(f"Found stage: {stage} in line: {line[:100]}...")
                
                # The data format is complex - ranks and percentages are split across lines
                # We need to collect all the data for this stage
                stage_data = []
                
                logger.debug(f"Looking ahead for data for stage {stage} starting from line {i}")
                
                # Look ahead up to 20 lines to find all the data for this stage
                for j in range(i, min(i + 20, len(lines))):
                    next_line = lines[j].strip()
                    if not next_line:
                        continue
                    
                    logger.debug(f"  Line {j}: '{next_line[:50]}...'")
                    
                    # Stop if we hit another stage or section boundary
                    if (re.search(r'\b([IVX]+)(?:-Non\s+PWD)?\b', next_line) and j > i) or \
                       'Status:' in next_line or \
                       re.match(r'^\d{10}', next_line) or \
                       'Stage' in next_line:
                        logger.debug(f"  Stopping at line {j} due to boundary")
                        break
                    
                    # Look for individual ranks (numbers) and percentages (numbers in parentheses)
                    # We'll collect them separately and then pair them up
                    ranks = re.findall(r'\b(\d{4,6})\b', next_line)  # 4-6 digit numbers
                    percentages = re.findall(r'\(([\d.]+)\)', next_line)  # Numbers in parentheses
                    
                    if ranks:
                        logger.debug(f"  Found ranks: {ranks}")
                        stage_data.extend([(rank, None) for rank in ranks])
                    
                    if percentages:
                        logger.debug(f"  Found percentages: {percentages}")
                        # Pair percentages with the most recent ranks
                        # We need to work backwards to pair them correctly
                        for percentage in percentages:
                            # Find the most recent unpaired rank
                            for k in range(len(stage_data) - 1, -1, -1):
                                rank, existing_percentage = stage_data[k]
                                if existing_percentage is None:
                                    stage_data[k] = (rank, percentage)
                                    logger.debug(f"  Paired rank {rank} with percentage {percentage}")
                                    break
                            else:
                                # No unpaired rank found, just store the percentage
                                stage_data.append((None, percentage))
                
                logger.debug(f"Total data collected for stage {stage}: {len(stage_data)} entries")
                logger.debug(f"Data: {stage_data}")
                
                # Now match categories with the collected data
                if stage_data:
                    # Filter out incomplete entries (missing rank or percentage)
                    complete_data = [(rank, percentage) for rank, percentage in stage_data if rank and percentage]
                    logger.debug(f"Complete entries: {len(complete_data)}")
                    
                    # Match categories with rank-percentage pairs
                    for j, (rank, percentage) in enumerate(complete_data):
                        if j < len(categories):
                            category = categories[j]
                            try:
                                cutoff_data.append({
                                    'stage': stage,
                                    'category': category,
                                    'rank': int(rank),
                                    'percentage': float(percentage)
                                })
                                logger.debug(f"Added cutoff: Stage {stage}, {category}: {rank} ({percentage}%)")
                            except ValueError as e:
                                logger.warning(f"Could not parse rank/percentage: {rank}, {percentage}")
                                continue
                        else:
                            logger.warning(f"More rank-percentage pairs than categories: {len(complete_data)} vs {len(categories)}")
                            break
        
        logger.debug(f"Total cutoff entries extracted: {len(cutoff_data)}")
        return cutoff_data
    
    def parse_pdf(self, pdf_path: str) -> Dict:
        """Main method to parse PDF and extract all data."""
        try:
            text = self.extract_text_from_pdf(pdf_path)
            if not text:
                return {"error": "Could not extract text from PDF", "parsing_success": False}
            
            logger.info("Extracted text from PDF successfully")
            
            # Extract all colleges
            colleges = self.extract_colleges(text)
            
            if not colleges:
                return {"error": "Could not extract any colleges from PDF", "parsing_success": False}
            
            logger.info(f"Found {len(colleges)} colleges in PDF")
            
            # Calculate total statistics
            total_branches = sum(college['total_branches'] for college in colleges)
            total_cutoffs = sum(sum(len(branch['cutoff_data']) for branch in college['branches']) for college in colleges)
            
            return {
                "colleges": colleges,
                "total_colleges": len(colleges),
                "total_branches": total_branches,
                "total_cutoffs": total_cutoffs,
                "parsing_success": True
            }
            
        except Exception as e:
            logger.error(f"Error parsing PDF: {e}")
            return {"error": f"Error parsing PDF: {str(e)}", "parsing_success": False}

    def save_to_json(self, data: Dict, output_path: str) -> bool:
        """Save parsed data to JSON file."""
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            logger.info(f"Data saved to {output_path}")
            return True
        except Exception as e:
            logger.error(f"Error saving to JSON: {e}")
            return False

# Usage example and testing
if __name__ == "__main__":
    parser = EnhancedCollegeParser()
    
    # Example usage
    # result = parser.parse_pdf("path_to_your_pdf.pdf")
    # if result.get("parsing_success"):
    #     parser.save_to_json(result, "parsed_data.json")
    #     print("Parsing completed successfully!")
    #     print(f"Colleges found: {result['total_colleges']}")
    #     print(f"Total branches: {result['total_branches']}")
    #     print(f"Total cutoff entries: {result['total_cutoffs']}")
    # else:
    #     print(f"Parsing failed: {result.get('error')}")
