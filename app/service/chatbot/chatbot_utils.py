"""
Utility functions for chatbot documentation loading and processing
"""

import os
import logging
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
import re

logger = logging.getLogger(__name__)


class DocumentationLoader:
    """Load and manage project documentation"""
    
    def __init__(self, project_root: Optional[Path] = None):
        """Initialize documentation loader
        
        Args:
            project_root: Root path of the project (defaults to project root)
        """
        if project_root is None:
            # Find project root by going up from this file
            current = Path(__file__).parent
            while current != current.parent:
                if (current / "main.py").exists():
                    project_root = current
                    break
                current = current.parent
        
        self.project_root = project_root or Path.cwd()
        self.documentation = {}
        self.raw_content = ""
        self.sections = {}
        self.last_loaded = None
        
        logger.info(f"Documentation loader initialized at: {self.project_root}")
    
    def load_documentation(self) -> Dict[str, str]:
        """Load all documentation files
        
        Returns:
            Dictionary with documentation content
        """
        try:
            doc_files = {
                "README": self.project_root / "README.md",
                "requirements": self.project_root / "requirements.txt",
                "Dockerfile": self.project_root / "Dockerfile",
                "docker-compose": self.project_root / "docker-compose.yml",
            }
            
            for name, filepath in doc_files.items():
                if filepath.exists():
                    with open(filepath, "r", encoding="utf-8") as f:
                        content = f.read()
                        self.documentation[name] = content
                        logger.info(f"Loaded {name}: {len(content)} characters")
            
            # Combine all documentation
            self.raw_content = "\n\n---\n\n".join(
                f"## {name} Documentation\n\n{content}"
                for name, content in self.documentation.items()
            )
            
            self.last_loaded = datetime.now().isoformat()
            self._extract_sections()
            
            return self.documentation
            
        except Exception as e:
            logger.error(f"Error loading documentation: {e}")
            return {}
    
    def _extract_sections(self):
        """Extract major sections from documentation"""
        # Extract markdown headers (h1, h2, h3)
        header_pattern = r"^#{1,3}\s+(.+)$"
        
        sections = {}
        current_section = None
        current_content = []
        
        for line in self.raw_content.split("\n"):
            match = re.match(header_pattern, line)
            if match:
                if current_section:
                    sections[current_section] = "\n".join(current_content).strip()
                current_section = match.group(1).strip()
                current_content = []
            else:
                current_content.append(line)
        
        if current_section:
            sections[current_section] = "\n".join(current_content).strip()
        
        self.sections = sections
        logger.info(f"Extracted {len(sections)} documentation sections")
    
    def get_relevant_context(self, query: str, max_chars: int = 4000) -> tuple[str, List[str]]:
        """Get relevant documentation context for a query
        
        Args:
            query: User's question
            max_chars: Maximum characters to return
            
        Returns:
            Tuple of (context_text, relevant_sections)
        """
        if not self.raw_content:
            self.load_documentation()
        
        # Simple relevance matching - can be improved with semantic search
        query_words = set(query.lower().split())
        
        scored_sections = []
        for section_name, section_content in self.sections.items():
            section_text = f"{section_name}\n{section_content}".lower()
            
            # Count word matches
            score = sum(
                section_text.count(word) 
                for word in query_words 
                if len(word) > 3
            )
            
            if score > 0:
                scored_sections.append((section_name, section_content, score))
        
        # Sort by relevance score
        scored_sections.sort(key=lambda x: x[2], reverse=True)
        
        # Build context up to max_chars
        context_parts = []
        relevant_sections = []
        current_length = 0
        
        for section_name, content, score in scored_sections:
            section_text = f"## {section_name}\n{content}\n"
            if current_length + len(section_text) <= max_chars:
                context_parts.append(section_text)
                relevant_sections.append(section_name)
                current_length += len(section_text)
            else:
                break
        
        # If no relevant sections found, include general context
        if not context_parts and self.raw_content:
            context_parts = [self.raw_content[:max_chars]]
            relevant_sections = ["General Documentation"]
        
        context = "\n".join(context_parts) if context_parts else self.raw_content[:max_chars]
        
        return context, relevant_sections
    
    def get_full_content(self) -> str:
        """Get complete documentation content"""
        if not self.raw_content:
            self.load_documentation()
        return self.raw_content
    
    def get_summary(self) -> Dict[str, any]:
        """Get documentation summary"""
        return {
            "total_chars": len(self.raw_content),
            "total_sections": len(self.sections),
            "section_names": list(self.sections.keys()),
            "last_loaded": self.last_loaded,
            "loaded_files": list(self.documentation.keys())
        }


# Global documentation loader instance
_loader_instance: Optional[DocumentationLoader] = None


def get_documentation_loader() -> DocumentationLoader:
    """Get or create global documentation loader instance"""
    global _loader_instance
    if _loader_instance is None:
        _loader_instance = DocumentationLoader()
    return _loader_instance


def refresh_documentation():
    """Refresh documentation from disk"""
    global _loader_instance
    _loader_instance = DocumentationLoader()
    _loader_instance.load_documentation()


def get_documentation_context(query: str, max_chars: int = 4000) -> tuple[str, List[str]]:
    """Convenience function to get context"""
    loader = get_documentation_loader()
    if not loader.raw_content:
        loader.load_documentation()
    return loader.get_relevant_context(query, max_chars)
