"""Configuration for the Scientific Knowledge Extraction Agent."""

from dataclasses import dataclass, field
import os
import hashlib
import json
from typing import Dict, List, Optional, Set
from pathlib import Path

from aurelian.dependencies.workdir import HasWorkdir


@dataclass
class ScientificKnowledgeExtractionDependencies(HasWorkdir):
    """Dependencies for the Scientific Knowledge Extraction Agent."""
    
    # Directory containing the PDF files to be processed
    pdf_directory: str = "."
    
    # Directory for caching processed files and results
    cache_directory: Optional[str] = None
    
    # Maximum number of PDFs to process in a single run (0 = no limit)
    max_pdfs: int = 0
    
    # Set of already processed file hashes (to avoid reprocessing)
    _processed_hashes: Set[str] = field(default_factory=set)
    
    # Cache of extracted knowledge/relations by file hash
    _knowledge_cache: Dict[str, List] = field(default_factory=dict)
    
    def __post_init__(self):
        """Initialize cache if cache_directory is provided."""
        # If no cache directory is specified, create a default one
        if not self.cache_directory:
            self.cache_directory = os.path.join(str(self.workdir.location), ".scientific_knowledge_cache")
        
        # Ensure cache directory exists
        os.makedirs(self.cache_directory, exist_ok=True)
        
        # Load existing cache if available
        self._load_cache()
    
    def _load_cache(self):
        """Load existing cache from the cache directory."""
        cache_file = os.path.join(self.cache_directory, "cache.json")
        
        if os.path.exists(cache_file):
            try:
                with open(cache_file, 'r') as f:
                    cache_data = json.load(f)
                    self._processed_hashes = set(cache_data.get("processed_hashes", []))
                    self._knowledge_cache = cache_data.get("knowledge_cache", {})
            except Exception as e:
                print(f"Warning: Failed to load cache: {e}")
    
    def save_cache(self):
        """Save the current cache to disk."""
        cache_file = os.path.join(self.cache_directory, "cache.json")
        
        try:
            cache_data = {
                "processed_hashes": list(self._processed_hashes),
                "knowledge_cache": self._knowledge_cache
            }
            
            with open(cache_file, 'w') as f:
                json.dump(cache_data, f, indent=2)
        except Exception as e:
            print(f"Warning: Failed to save cache: {e}")
    
    def get_file_hash(self, file_path: str) -> str:
        """Calculate a hash for a file to use as a cache key."""
        try:
            with open(file_path, 'rb') as f:
                file_hash = hashlib.md5(f.read()).hexdigest()
            return file_hash
        except Exception as e:
            print(f"Warning: Failed to hash file {file_path}: {e}")
            # Use filename and size as fallback
            return f"{os.path.basename(file_path)}_{os.path.getsize(file_path)}"
    
    def is_processed(self, file_path: str) -> bool:
        """Check if a file has already been processed based on its hash."""
        file_hash = self.get_file_hash(file_path)
        return file_hash in self._processed_hashes
    
    def mark_as_processed(self, file_path: str, knowledge: List = None):
        """Mark a file as processed and cache its extracted knowledge."""
        file_hash = self.get_file_hash(file_path)
        self._processed_hashes.add(file_hash)
        
        if knowledge:
            self._knowledge_cache[file_hash] = knowledge
        
        # Save cache after each update
        self.save_cache()
    
    def get_cached_knowledge(self, file_path: str) -> Optional[List]:
        """Get cached knowledge for a file if available."""
        file_hash = self.get_file_hash(file_path)
        return self._knowledge_cache.get(file_hash)
    
    def get_unprocessed_pdfs(self) -> List[str]:
        """Get a list of PDF files in the specified directory that haven't been processed yet."""
        pdf_files = []
        
        if not os.path.exists(self.pdf_directory):
            return pdf_files
        
        for filename in os.listdir(self.pdf_directory):
            if filename.lower().endswith('.pdf'):
                file_path = os.path.join(self.pdf_directory, filename)
                if not self.is_processed(file_path):
                    pdf_files.append(file_path)
        
        # Apply max_pdfs limit if specified
        if self.max_pdfs > 0:
            pdf_files = pdf_files[:self.max_pdfs]
            
        return pdf_files