import fitz  # PyMuPDF
import csv
import re

def extract_salary_data_from_pdf(pdf_path, year):
    """Extract salary data from PDF with columnar layout."""
    
    # Common job title keywords to help identify where name ends
    job_keywords = {
        'Professor', 'Associate', 'Assistant', 'Lecturer', 'Instructor',
        'Director', 'Dean', 'Manager', 'Coordinator', 'Specialist',
        'Technician', 'Engineer', 'Officer', 'Worker', 'Administrator',
        'Professional', 'Analyst', 'Senior', 'Clinical', 'Research',
        'Administrative', 'Student', 'Business', 'Information', 'Health',
        'Vice', 'Chief', 'President', 'Provost', 'Custodial', 'Maintenance',
        'Support', 'Outreach', 'Enrollment', 'Academic', 'Services',
        'Facilities', 'Equipment', 'Lab', 'Library', 'Communications',
        'Post', 'Pre', 'Doctoral', 'Extension', 'Grounds', 'Safety'
    }
    
    doc = fitz.open(pdf_path)
    employees = []
    
    for page_num in range(len(doc)):
        page = doc[page_num]
        
        # Extract text blocks with position information
        blocks = page.get_text("dict")["blocks"]
        
        # Collect all text items with their positions
        lines_with_pos = []
        for block in blocks:
            if "lines" in block:
                for line in block["lines"]:
                    for span in line["spans"]:
                        text = span["text"].strip()
                        if text:
                            lines_with_pos.append({
                                'text': text,
                                'y': span["bbox"][1],
                                'x': span["bbox"][0]
                            })
        
        # Sort by y position, then x position
        lines_with_pos.sort(key=lambda item: (round(item['y']), item['x']))
        
        # Group items by y position (same line)
        current_y = None
        current_line = []
        tolerance = 2
        
        grouped_lines = []
        for item in lines_with_pos:
            if current_y is None or abs(item['y'] - current_y) > tolerance:
                if current_line:
                    grouped_lines.append(current_line)
                current_line = [item]
                current_y = item['y']
            else:
                current_line.append(item)
        
        if current_line:
            grouped_lines.append(current_line)
        
        # Process each line
        for line_items in grouped_lines:
            line_text = ' '.join([item['text'] for item in line_items])
            
            # Skip headers and non-data lines
            if not line_text or 'University of Vermont' in line_text:
                continue
            if 'Name Primary Job Title Base Pay' in line_text:
                continue
            if line_text.startswith('Page ') or line_text.startswith('Release Date'):
                continue
            
            # Look for salary pattern
            salary_pattern = r'\$[\d,]+'
            salary_match = re.search(salary_pattern, line_text)
            
            if salary_match:
                salary = salary_match.group()
                before_salary = line_text[:salary_match.start()].strip()
                
                # Split by comma to get last name
                parts = before_salary.split(',', 1)
                
                if len(parts) == 2:
                    last_name = parts[0].strip()
                    remainder = parts[1].strip()
                    
                    # Find where the job title starts by looking for job keywords
                    words = remainder.split()
                    first_name_parts = []
                    job_title_parts = []
                    found_job_title = False
                    
                    for word in words:
                        if not found_job_title:
                            # Check if this word starts a job title
                            if word in job_keywords or word.rstrip('s') in job_keywords:
                                found_job_title = True
                                job_title_parts.append(word)
                            else:
                                first_name_parts.append(word)
                        else:
                            job_title_parts.append(word)
                    
                    first_name = ' '.join(first_name_parts)
                    job_title = ' '.join(job_title_parts)
                    
                    # Fallback: if we didn't find a job title, assume first word is first name
                    if not first_name and job_title_parts:
                        first_name = job_title_parts[0]
                        job_title = ' '.join(job_title_parts[1:])
                    
                    # Only include professors, exclude COM and Clinical professors
                    if ('professor' in job_title.lower() and
                        '(com)' not in job_title.lower() and
                        'emeritus' not in job_title.lower() and
                        'Extension' not in job_title.lower() and
                        'clinical professor' not in job_title.lower()):
                        employees.append({
                            'payroll_name': f"{last_name},{first_name}",
                            'payroll_year': year,
                            'position': job_title,
                            'oa_display_name': None,
                            'is_prof': None,
                            'perceived_as_male': None,
                            'host_dept': None,
                            'has_research_group': None,
                            'group_size': None,
                            'oa_uid': None,
                            'group_url': None,
                            'first_pub_year': None,
                            'inst_ipeds_id': None,
                            'notes': None,
                            'last_updated': None,
                            'college': None
                        })
    
    doc.close()
    return employees

# Extract from PDF
YEAR = 2024
employees = extract_salary_data_from_pdf('../input/Final_FY23_Base_Pay.pdf', YEAR)

# Save to CSV
fieldnames = [
    'payroll_name', 'payroll_year', 'position', 'oa_display_name', 'is_prof',
    'perceived_as_male', 'host_dept', 'has_research_group', 'group_size',
    'oa_uid', 'group_url', 'first_pub_year', 'inst_ipeds_id', 'notes',
    'last_updated', 'college'
]

with open(f'uvm_salaries_{YEAR}.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(employees)