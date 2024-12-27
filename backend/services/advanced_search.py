from typing import List, Dict, Optional
import re
from pygments.lexers import guess_lexer
from pygments.util import ClassNotFound
import latex2mathml
from elasticsearch import Elasticsearch
from datetime import datetime

class AdvancedSearch:
    """Advanced search service with support for code and mathematical expressions."""
    
    def __init__(self, elasticsearch_url: str):
        self.es = Elasticsearch(elasticsearch_url)
        self._setup_indices()
    
    def _setup_indices(self):
        """Setup Elasticsearch indices with appropriate mappings."""
        # Note index mapping
        note_mapping = {
            "mappings": {
                "properties": {
                    "title": {"type": "text"},
                    "content": {"type": "text"},
                    "code_blocks": {
                        "type": "nested",
                        "properties": {
                            "code": {"type": "text"},
                            "language": {"type": "keyword"},
                            "tokens": {"type": "text"}
                        }
                    },
                    "latex_blocks": {
                        "type": "nested",
                        "properties": {
                            "latex": {"type": "text"},
                            "rendered": {"type": "text"}
                        }
                    },
                    "tags": {"type": "keyword"},
                    "folder_id": {"type": "keyword"},
                    "user_id": {"type": "keyword"},
                    "created_at": {"type": "date"},
                    "updated_at": {"type": "date"}
                }
            }
        }
        
        # Create indices if they don't exist
        if not self.es.indices.exists(index="notes"):
            self.es.indices.create(index="notes", body=note_mapping)
    
    def index_note(self, note: Dict):
        """Index a note with its code and latex content."""
        # Process code blocks
        code_blocks = self._process_code_blocks(note.get('content', ''))
        
        # Process LaTeX blocks
        latex_blocks = self._process_latex_blocks(note.get('content', ''))
        
        # Prepare document
        doc = {
            'title': note.get('title', ''),
            'content': note.get('content', ''),
            'code_blocks': code_blocks,
            'latex_blocks': latex_blocks,
            'tags': note.get('tags', []),
            'folder_id': str(note.get('folder_id')),
            'user_id': str(note.get('user_id')),
            'created_at': note.get('created_at', datetime.utcnow()),
            'updated_at': note.get('updated_at', datetime.utcnow())
        }
        
        # Index document
        self.es.index(index="notes", id=str(note.get('_id')), body=doc)
    
    def _process_code_blocks(self, content: str) -> List[Dict]:
        """Extract and process code blocks from content."""
        code_blocks = []
        pattern = r'```(\w+)?\n(.*?)```'
        matches = re.finditer(pattern, content, re.DOTALL)
        
        for match in matches:
            code = match.group(2).strip()
            lang = match.group(1) or self._detect_language(code)
            
            code_blocks.append({
                'code': code,
                'language': lang,
                'tokens': self._tokenize_code(code, lang)
            })
        
        return code_blocks
    
    def _detect_language(self, code: str) -> str:
        """Detect programming language of code snippet."""
        try:
            lexer = guess_lexer(code)
            return lexer.name.lower()
        except ClassNotFound:
            return 'text'
    
    def _tokenize_code(self, code: str, language: str) -> str:
        """Tokenize code for better searchability."""
        # Split camelCase and snake_case
        tokens = re.findall(r'[A-Z]?[a-z]+|[A-Z]{2,}(?=[A-Z][a-z]|\d|\W|$)|\d+', code)
        return ' '.join(tokens).lower()
    
    def _process_latex_blocks(self, content: str) -> List[Dict]:
        """Extract and process LaTeX blocks from content."""
        latex_blocks = []
        pattern = r'\$\$(.*?)\$\$|\$(.*?)\$'
        matches = re.finditer(pattern, content, re.DOTALL)
        
        for match in matches:
            latex = match.group(1) or match.group(2)
            try:
                rendered = latex2mathml.converter.convert(latex)
            except:
                rendered = latex
                
            latex_blocks.append({
                'latex': latex,
                'rendered': rendered
            })
        
        return latex_blocks
    
    def search(
        self,
        query: str,
        user_id: str,
        language: Optional[str] = None,
        tags: Optional[List[str]] = None,
        folder_id: Optional[str] = None
    ) -> List[Dict]:
        """
        Perform advanced search across notes.
        Supports code-aware search and mathematical expressions.
        """
        # Base query
        must = [{"term": {"user_id": user_id}}]
        
        # Add filters
        if language:
            must.append({
                "nested": {
                    "path": "code_blocks",
                    "query": {
                        "term": {"code_blocks.language": language}
                    }
                }
            })
        
        if tags:
            must.append({"terms": {"tags": tags}})
            
        if folder_id:
            must.append({"term": {"folder_id": folder_id}})
        
        # Build search query
        search_query = {
            "bool": {
                "must": must,
                "should": [
                    # Full text search
                    {"match": {"title": {"query": query, "boost": 2.0}}},
                    {"match": {"content": query}},
                    # Code search
                    {
                        "nested": {
                            "path": "code_blocks",
                            "query": {
                                "bool": {
                                    "should": [
                                        {"match": {"code_blocks.code": query}},
                                        {"match": {"code_blocks.tokens": query}}
                                    ]
                                }
                            },
                            "score_mode": "max"
                        }
                    },
                    # LaTeX search
                    {
                        "nested": {
                            "path": "latex_blocks",
                            "query": {
                                "match": {"latex_blocks.latex": query}
                            }
                        }
                    }
                ]
            }
        }
        
        # Execute search
        results = self.es.search(
            index="notes",
            body={
                "query": search_query,
                "highlight": {
                    "fields": {
                        "title": {},
                        "content": {},
                        "code_blocks.code": {},
                        "latex_blocks.latex": {}
                    }
                }
            }
        )
        
        # Process results
        processed_results = []
        for hit in results['hits']['hits']:
            result = hit['_source']
            result['score'] = hit['_score']
            if 'highlight' in hit:
                result['highlights'] = hit['highlight']
            processed_results.append(result)
        
        return processed_results
