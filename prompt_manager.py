"""
Prompt Manager Module

This module handles the generation and management of prompts for the TalentScout AI Assistant.
It includes role-specific configurations, prompt templates, and data privacy management.

Classes:
    PromptTemplate: Dataclass for storing prompt template information
    PromptManager: Manages prompt generation and role-specific configurations
    DataPrivacyManager: Handles data anonymization and storage
"""

from typing import List, Dict, Optional
from dataclasses import dataclass
import hashlib
import re
from datetime import datetime
import json
from pathlib import Path

# Role-specific configurations
ROLE_TECH_PRIORITIES = {
    "AI Intern": ["ai_ml", "languages", "tools"],
    "Software Engineer": ["languages", "frameworks", "tools"],
    "Data Scientist": ["ai_ml", "databases", "tools"],
    "DevOps Engineer": ["tools", "cloud", "frameworks"],
    "Full Stack Developer": ["languages", "frameworks", "databases"],
    "Backend Developer": ["languages", "databases", "frameworks"],
    "Frontend Developer": ["languages", "frameworks", "tools"],
    "Machine Learning Engineer": ["ai_ml", "languages", "tools"],
    "Data Engineer": ["databases", "tools", "languages"]
}

ROLE_FOCUS_AREAS = {
    'AI Intern': {
        'technical_focus': ['machine learning concepts', 'data preprocessing', 'model evaluation', 'basic algorithms'],
        'behavioral_focus': ['learning ability', 'problem-solving approach', 'teamwork in research']
    },
    'Software Engineer': {
        'technical_focus': ['system design', 'code quality', 'testing', 'performance optimization'],
        'behavioral_focus': ['problem-solving', 'team collaboration', 'code review practices']
    },
    'Data Scientist': {
        'technical_focus': ['statistical analysis', 'data modeling', 'experiment design', 'data visualization'],
        'behavioral_focus': ['research methodology', 'stakeholder communication', 'project management']
    },
    'DevOps Engineer': {
        'technical_focus': ['infrastructure as code', 'CI/CD', 'monitoring', 'security'],
        'behavioral_focus': ['incident response', 'team coordination', 'automation mindset']
    },
    'Full Stack Developer': {
        'technical_focus': ['frontend-backend integration', 'API design', 'database optimization', 'security'],
        'behavioral_focus': ['end-to-end thinking', 'cross-functional collaboration', 'user experience']
    },
    'Backend Developer': {
        'technical_focus': ['API design', 'database optimization', 'scalability', 'security'],
        'behavioral_focus': ['system architecture', 'performance optimization', 'code maintainability']
    },
    'Frontend Developer': {
        'technical_focus': ['UI/UX implementation', 'state management', 'performance optimization', 'accessibility'],
        'behavioral_focus': ['user-centric thinking', 'design collaboration', 'cross-browser compatibility']
    },
    'Machine Learning Engineer': {
        'technical_focus': ['model deployment', 'MLOps', 'model optimization', 'data pipeline'],
        'behavioral_focus': ['production ML systems', 'cross-team collaboration', 'model monitoring']
    },
    'Data Engineer': {
        'technical_focus': ['data pipeline design', 'ETL processes', 'data warehousing', 'data quality'],
        'behavioral_focus': ['data governance', 'cross-functional collaboration', 'data architecture']
    }
}

TECH_CATEGORIES = {
    'languages': ['python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'ruby', 'php', 'swift', 'kotlin', 'go', 'rust'],
    'frameworks': ['django', 'flask', 'spring', 'react', 'angular', 'vue', 'express', 'rails', 'laravel', 'asp.net'],
    'databases': ['mysql', 'postgresql', 'mongodb', 'redis', 'oracle', 'sql server', 'cassandra'],
    'cloud': ['aws', 'azure', 'gcp', 'heroku', 'digitalocean'],
    'tools': ['docker', 'kubernetes', 'jenkins', 'git', 'jira', 'confluence'],
    'ai_ml': ['tensorflow', 'pytorch', 'scikit-learn', 'pandas', 'numpy', 'keras']
}

@dataclass
class PromptTemplate:
    """
    A dataclass representing a prompt template with its variables and optional context.
    
    Attributes:
        template (str): The template string with placeholders
        variables (List[str]): List of variable names used in the template
        context (Optional[str]): Optional context information for the template
    """
    template: str
    variables: List[str]
    context: Optional[str] = None

class PromptManager:
    """
    Manages the generation of prompts for different types of questions and role-specific configurations.
    
    This class handles:
    - Technical question generation
    - Follow-up question generation
    - Behavioral question generation
    - Answer analysis
    - Role-specific focus areas
    - Technology categorization
    """
    
    def __init__(self):
        """Initialize the PromptManager with role configurations and prompt templates."""
        self.tech_categories = TECH_CATEGORIES
        self.role_focus = ROLE_FOCUS_AREAS
        
        # Initialize prompt templates
        self.templates = {
            'technical_question': PromptTemplate(
                template="""Generate a clear, concise technical question about {technology} for a {position} role with {years_experience} years of experience.
                Difficulty Level: {difficulty_level} (on a scale of 1 to 10, where 10 is hardest)

                The question should:
                1. Focus on {role_focus} aspects relevant to the role
                2. Be appropriate for their experience level and the role
                3. Include both theoretical and practical aspects
                4. Consider industry best practices
                5. Test their understanding of {technology} in the context of {position} responsibilities

                Return ONLY the question, nothing else, no extra text or context.""",
                variables=['technology', 'position', 'years_experience', 'difficulty_level', 'role_focus']
            ),
            'follow_up': PromptTemplate(
                template="""Based on this answer about {technology} for a {position} role: "{previous_answer}"
                Generate a follow-up question for someone with {years_experience} years of experience.
                Difficulty Level: {difficulty_level} (on a scale of 1 to 10, where 10 is hardest)

                The question should:
                1. Probe deeper into their understanding of {role_focus} aspects
                2. Focus on specific aspects they mentioned
                3. Challenge their knowledge appropriately
                4. Maintain professional tone
                5. Be relevant to {position} responsibilities

                Return ONLY the question, nothing else, no extra text or context.""",
                variables=['technology', 'position', 'previous_answer', 'years_experience', 'difficulty_level', 'role_focus']
            ),
            'behavioral': PromptTemplate(
                template="""Generate a behavioral question for a {position} role with {years_experience} years of experience.
                Tech Stack: {tech_stack}
                Focus Area: {focus_area}
                
                The question should:
                1. Focus on {role_focus} aspects relevant to the role
                2. Include specific scenarios relevant to their tech stack
                3. Assess both technical and soft skills
                4. Consider their experience level
                5. Evaluate their approach to {position} responsibilities
                6. Specifically target the {focus_area} aspect
                
                Return ONLY the question, nothing else, no extra text or context.""",
                variables=['position', 'years_experience', 'tech_stack', 'role_focus', 'focus_area']
            ),
            'system_design': PromptTemplate(
                template="""Generate a system design question for a {position} role with {years_experience} years of experience.
                Tech Stack: {tech_stack}
                Difficulty Level: {difficulty_level}
                
                The question should:
                1. Focus on architectural decisions and trade-offs
                2. Consider scalability, reliability, and performance
                3. Include real-world constraints and requirements
                4. Test understanding of distributed systems concepts
                5. Evaluate ability to make technical decisions
                
                Return ONLY the question, nothing else, no extra text or context.""",
                variables=['position', 'years_experience', 'tech_stack', 'difficulty_level']
            ),
            'coding_practice': PromptTemplate(
                template="""Generate a coding practice question for a {position} role with {years_experience} years of experience.
                Tech Stack: {tech_stack}
                Difficulty Level: {difficulty_level}
                
                The question should:
                1. Focus on clean code principles and best practices
                2. Include edge cases and error handling
                3. Test understanding of data structures and algorithms
                4. Consider performance optimization
                5. Evaluate code organization and maintainability
                
                Return ONLY the question, nothing else, no extra text or context.""",
                variables=['position', 'years_experience', 'tech_stack', 'difficulty_level']
            ),
            'answer_analysis': PromptTemplate(
                template="""Analyze the following candidate's answer to the question. Provide a concise assessment of its completeness and relevance. Explain why it is satisfactory or incomplete.
                Question: "{question}"
                Candidate's Answer: "{answer}"
                
                Assessment:""",
                variables=['question', 'answer']
            )
        }

    def categorize_tech_stack(self, tech_stack: List[str]) -> Dict[str, List[str]]:
        """
        Categorize technologies into different types based on predefined categories.
        
        Args:
            tech_stack (List[str]): List of technologies to categorize
            
        Returns:
            Dict[str, List[str]]: Dictionary mapping categories to lists of technologies
        """
        categorized = {category: [] for category in self.tech_categories.keys()}
        
        for tech in tech_stack:
            tech_lower = tech.lower()
            for category, keywords in self.tech_categories.items():
                if tech_lower in keywords:
                    categorized[category].append(tech)
                    break
        
        return categorized

    def get_role_focus(self, position: str) -> str:
        """
        Get the technical focus areas for a specific role.
        
        Args:
            position (str): The role position to get focus areas for
            
        Returns:
            str: Comma-separated list of technical focus areas
        """
        role_info = self.role_focus.get(position, self.role_focus['Software Engineer'])
        return ', '.join(role_info['technical_focus'])

    def get_behavioral_focus(self, position: str) -> str:
        """
        Get the behavioral focus areas for a specific role.
        
        Args:
            position (str): The role position to get focus areas for
            
        Returns:
            str: Comma-separated list of behavioral focus areas
        """
        role_info = self.role_focus.get(position, self.role_focus['Software Engineer'])
        return ', '.join(role_info['behavioral_focus'])

    def generate_technical_question(self, tech: str, position: str, years_experience: int, difficulty_level: int) -> str:
        """
        Generate a technical question based on technology, position, experience level, and difficulty.
        
        Args:
            tech (str): The technology to ask about
            position (str): The candidate's desired position
            years_experience (int): Years of experience
            difficulty_level (int): Question difficulty (1-10)
            
        Returns:
            str: Generated technical question prompt
        """
        template = self.templates['technical_question']
        role_focus = self.get_role_focus(position)
        
        prompt = template.template.format(
            technology=tech,
            position=position,
            years_experience=years_experience,
            difficulty_level=difficulty_level,
            role_focus=role_focus
        )
        
        return prompt

    def generate_follow_up(self, tech: str, position: str, previous_answer: str, years_experience: int, difficulty_level: int) -> str:
        """
        Generate a follow-up question based on previous answer, position and difficulty.
        
        Args:
            tech (str): The technology being discussed
            position (str): The candidate's desired position
            previous_answer (str): The candidate's previous answer
            years_experience (int): Years of experience
            difficulty_level (int): Question difficulty (1-10)
            
        Returns:
            str: Generated follow-up question prompt
        """
        template = self.templates['follow_up']
        role_focus = self.get_role_focus(position)
        
        prompt = template.template.format(
            technology=tech,
            position=position,
            previous_answer=previous_answer,
            years_experience=years_experience,
            difficulty_level=difficulty_level,
            role_focus=role_focus
        )
        
        return prompt

    def generate_behavioral_question(self, position: str, years_experience: int, tech_stack: List[str], focus_area: str = "problem_solving") -> str:
        """
        Generate a behavioral question based on position and experience.
        
        Args:
            position (str): The candidate's desired position
            years_experience (int): Years of experience
            tech_stack (List[str]): List of technologies in candidate's stack
            focus_area (str): Specific focus area for the behavioral question
            
        Returns:
            str: Generated behavioral question prompt
        """
        template = self.templates['behavioral']
        role_focus = self.get_behavioral_focus(position)
        
        prompt = template.template.format(
            position=position,
            years_experience=years_experience,
            tech_stack=', '.join(tech_stack),
            role_focus=role_focus,
            focus_area=focus_area
        )
        
        return prompt

    def generate_system_design_question(self, position: str, years_experience: int, tech_stack: List[str], difficulty_level: int) -> str:
        """
        Generate a system design question based on position and experience.
        
        Args:
            position (str): The candidate's desired position
            years_experience (int): Years of experience
            tech_stack (List[str]): List of technologies in candidate's stack
            difficulty_level (int): Question difficulty (1-10)
            
        Returns:
            str: Generated system design question prompt
        """
        template = self.templates['system_design']
        
        prompt = template.template.format(
            position=position,
            years_experience=years_experience,
            tech_stack=', '.join(tech_stack),
            difficulty_level=difficulty_level
        )
        
        return prompt

    def generate_coding_practice_question(self, position: str, years_experience: int, tech_stack: List[str], difficulty_level: int) -> str:
        """
        Generate a coding practice question based on position and experience.
        
        Args:
            position (str): The candidate's desired position
            years_experience (int): Years of experience
            tech_stack (List[str]): List of technologies in candidate's stack
            difficulty_level (int): Question difficulty (1-10)
            
        Returns:
            str: Generated coding practice question prompt
        """
        template = self.templates['coding_practice']
        
        prompt = template.template.format(
            position=position,
            years_experience=years_experience,
            tech_stack=', '.join(tech_stack),
            difficulty_level=difficulty_level
        )
        
        return prompt

    def analyze_answer(self, question: str, answer: str) -> str:
        """
        Generate a prompt to analyze a candidate's answer.
        
        Args:
            question (str): The original question
            answer (str): The candidate's answer
            
        Returns:
            str: Generated analysis prompt
        """
        template = self.templates['answer_analysis']
        
        prompt = template.template.format(
            question=question,
            answer=answer
        )
        
        return prompt

class DataPrivacyManager:
    """
    Manages data privacy and anonymization for candidate information.
    
    This class handles:
    - Data anonymization
    - Secure storage of candidate information
    - Generation of unique candidate IDs
    """
    
    def __init__(self):
        """Initialize the DataPrivacyManager with a candidates directory."""
        self.candidate_dir = Path("candidates")
        self.candidate_dir.mkdir(exist_ok=True)
        
    def anonymize_data(self, data: Dict) -> Dict:
        """
        Anonymize sensitive candidate data.
        
        Args:
            data (Dict): Dictionary containing candidate information
            
        Returns:
            Dict: Anonymized version of the input data
        """
        anonymized = data.copy()
        
        # Hash sensitive fields
        if 'email' in anonymized:
            anonymized['email'] = self._hash_email(anonymized['email'])
        if 'phone' in anonymized:
            anonymized['phone'] = self._hash_phone(anonymized['phone'])
        if 'full_name' in anonymized:
            anonymized['full_name'] = self._hash_name(anonymized['full_name'])
        
        return anonymized
    
    def _hash_email(self, email: str) -> str:
        """
        Hash email address while preserving domain for analysis.
        
        Args:
            email (str): Email address to hash
            
        Returns:
            str: Hashed email address
        """
        username, domain = email.split('@')
        hashed_username = hashlib.sha256(username.encode()).hexdigest()[:8]
        return f"{hashed_username}@{domain}"
    
    def _hash_phone(self, phone: str) -> str:
        """
        Hash phone number while preserving country code.
        
        Args:
            phone (str): Phone number to hash
            
        Returns:
            str: Hashed phone number
        """
        # Remove any non-digit characters
        digits = re.sub(r'\D', '', phone)
        if len(digits) > 10:
            country_code = digits[:-10]
            number = digits[-10:]
            hashed_number = hashlib.sha256(number.encode()).hexdigest()[:6]
            return f"+{country_code}-XXX-{hashed_number}"
        else:
            hashed_number = hashlib.sha256(digits.encode()).hexdigest()[:6]
            return f"XXX-{hashed_number}"
    
    def _hash_name(self, name: str) -> str:
        """
        Hash full name while preserving initials.
        
        Args:
            name (str): Full name to hash
            
        Returns:
            str: Hashed name with preserved initials
        """
        parts = name.split()
        if len(parts) >= 2:
            first_initial = parts[0][0]
            last_initial = parts[-1][0]
            hashed_middle = hashlib.sha256(' '.join(parts[1:-1]).encode()).hexdigest()[:4]
            return f"{first_initial}.{hashed_middle}.{last_initial}."
        else:
            return hashlib.sha256(name.encode()).hexdigest()[:8]
    
    def save_anonymized_data(self, data: Dict, candidate_id: str):
        """
        Save anonymized candidate data to a JSON file.
        
        Args:
            data (Dict): Candidate data to anonymize and save
            candidate_id (str): Unique identifier for the candidate
        """
        anonymized_data = self.anonymize_data(data)
        anonymized_data['candidate_id'] = candidate_id
        anonymized_data['timestamp'] = datetime.utcnow().isoformat()
        
        file_path = self.candidate_dir / f"{candidate_id}_anonymized.json"
        with open(file_path, "w") as f:
            json.dump(anonymized_data, f, indent=2)
    
    def generate_candidate_id(self, data: Dict) -> str:
        """
        Generate a unique candidate ID based on anonymized data.
        
        Args:
            data (Dict): Candidate data to generate ID from
            
        Returns:
            str: Unique candidate ID
        """
        # Use a combination of hashed email and timestamp
        email_hash = hashlib.sha256(data.get('email', '').encode()).hexdigest()[:8]
        timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
        return f"CAND_{email_hash}_{timestamp}" 