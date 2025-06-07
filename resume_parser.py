import fitz  # PyMuPDF
import pdfplumber
from docx import Document
import re
from typing import Dict, Optional, List, Union
import io

class ResumeParser:
    def __init__(self):
        # Common technology keywords for tech stack extraction
        self.tech_keywords = {
            'languages': ['python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'ruby', 'php', 'swift', 'kotlin', 'go', 'rust'],
            'frameworks': ['django', 'flask', 'spring', 'react', 'angular', 'vue', 'express', 'rails', 'laravel', 'asp.net'],
            'databases': ['mysql', 'postgresql', 'mongodb', 'redis', 'oracle', 'sql server', 'cassandra'],
            'cloud': ['aws', 'azure', 'gcp', 'heroku', 'digitalocean'],
            'tools': ['docker', 'kubernetes', 'jenkins', 'git', 'jira', 'confluence'],
            'ai_ml': ['tensorflow', 'pytorch', 'scikit-learn', 'pandas', 'numpy', 'keras']
        }

    def extract_text_from_pdf(self, file_content: bytes) -> str:
        """Extract text from PDF using both PyMuPDF and pdfplumber for better results."""
        text = ""
        
        # Try PyMuPDF first
        try:
            doc = fitz.open(stream=file_content, filetype="pdf")
            for page in doc:
                text += page.get_text()
            doc.close()
        except Exception as e:
            print(f"PyMuPDF extraction failed: {str(e)}")
            text = ""

        # If PyMuPDF didn't get good results, try pdfplumber
        if not text.strip():
            try:
                with pdfplumber.open(io.BytesIO(file_content)) as pdf:
                    for page in pdf.pages:
                        text += page.extract_text() or ""
            except Exception as e:
                print(f"pdfplumber extraction failed: {str(e)}")
                raise Exception("Failed to extract text from PDF")

        return text

    def extract_text_from_docx(self, file_content: bytes) -> str:
        """Extract text from DOCX file."""
        try:
            doc = Document(io.BytesIO(file_content))
            return "\n".join([paragraph.text for paragraph in doc.paragraphs])
        except Exception as e:
            raise Exception(f"Failed to extract text from DOCX: {str(e)}")

    def extract_email(self, text: str) -> Optional[str]:
        """Extract email address from text."""
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        match = re.search(email_pattern, text)
        return match.group(0) if match else None

    def extract_phone(self, text: str) -> Optional[str]:
        """Extract phone number from text."""
        # Match various phone number formats
        phone_patterns = [
            r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',  # 123-456-7890
            r'\+\d{1,3}[-.]?\d{3}[-.]?\d{3}[-.]?\d{4}\b',  # +1-123-456-7890
            r'\(\d{3}\)\s*\d{3}[-.]?\d{4}\b',  # (123) 456-7890
        ]
        
        for pattern in phone_patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(0)
        return None

    def extract_years_experience(self, text: str) -> Optional[int]:
        """Extract years of experience from text."""
        # Look for patterns like "X years of experience" or "X+ years"
        exp_patterns = [
            r'(\d+)\+?\s*(?:years?|yrs?)\s*(?:of)?\s*experience',
            r'experience:\s*(\d+)\+?\s*(?:years?|yrs?)',
            r'(\d+)\+?\s*(?:years?|yrs?)\s*(?:in)?\s*the\s*field'
        ]
        
        for pattern in exp_patterns:
            match = re.search(pattern, text.lower())
            if match:
                try:
                    return int(match.group(1))
                except ValueError:
                    continue
        return None

    def extract_tech_stack(self, text: str) -> List[str]:
        """Extract technology stack from text."""
        text_lower = text.lower()
        found_tech = set()
        
        # Check each category of technologies
        for category, keywords in self.tech_keywords.items():
            for tech in keywords:
                if tech in text_lower:
                    found_tech.add(tech)
        
        return sorted(list(found_tech))

    def parse_resume(self, file_content: bytes, file_type: str) -> Dict[str, Union[str, int, List[str]]]:
        """Parse resume and extract relevant information."""
        try:
            # Extract text based on file type
            if file_type.lower() == 'pdf':
                text = self.extract_text_from_pdf(file_content)
            elif file_type.lower() == 'docx':
                text = self.extract_text_from_docx(file_content)
            else:
                raise ValueError(f"Unsupported file type: {file_type}")

            # Extract information
            return {
                "email": self.extract_email(text),
                "phone": self.extract_phone(text),
                "years_experience": self.extract_years_experience(text),
                "tech_stack": self.extract_tech_stack(text)
            }
        except Exception as e:
            raise Exception(f"Failed to parse resume: {str(e)}") 