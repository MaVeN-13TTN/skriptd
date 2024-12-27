import mistune
import bleach
import latex2mathml
import pygments
from pygments.lexers import get_lexer_by_name, guess_lexer
from pygments.formatters import HtmlFormatter
import re
from typing import Dict, List, Optional, Tuple

class ContentProcessor:
    """Service for processing rich text content including markdown, code, and LaTeX."""
    
    def __init__(self):
        # Initialize Markdown renderer with syntax highlighting
        self.markdown = mistune.create_markdown(
            plugins=['strikethrough', 'footnotes', 'table'],
            renderer=mistune.HTMLRenderer()
        )
        
        # Configure HTML sanitizer
        self.allowed_tags = [
            'p', 'div', 'span', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
            'ul', 'ol', 'li', 'blockquote', 'code', 'pre', 'strong',
            'em', 'a', 'img', 'table', 'thead', 'tbody', 'tr', 'th', 'td',
            'math', 'semantics', 'mrow', 'mi', 'mn', 'mo', 'msup'
        ]
        self.allowed_attributes = {
            '*': ['class', 'id'],
            'a': ['href', 'title'],
            'img': ['src', 'alt', 'title'],
            'code': ['class', 'data-language']
        }
    
    def process_content(self, content: str) -> Dict:
        """Process mixed content containing markdown, code blocks, and LaTeX."""
        # Extract and process components
        code_blocks = self._extract_code_blocks(content)
        latex_blocks = self._extract_latex(content)
        
        # Replace blocks with placeholders
        processed_content = content
        for idx, block in enumerate(code_blocks):
            processed_content = processed_content.replace(block['original'], f'CODE_BLOCK_{idx}')
        for idx, block in enumerate(latex_blocks):
            processed_content = processed_content.replace(block['original'], f'LATEX_BLOCK_{idx}')
        
        # Convert markdown to HTML
        html_content = self.markdown(processed_content)
        
        # Restore code and latex blocks
        for idx, block in enumerate(code_blocks):
            html_content = html_content.replace(
                f'CODE_BLOCK_{idx}',
                self._highlight_code(block['code'], block['language'])
            )
        for idx, block in enumerate(latex_blocks):
            html_content = html_content.replace(
                f'LATEX_BLOCK_{idx}',
                self._render_latex(block['latex'])
            )
        
        # Sanitize final HTML
        sanitized_html = bleach.clean(
            html_content,
            tags=self.allowed_tags,
            attributes=self.allowed_attributes,
            strip=True
        )
        
        return {
            'html': sanitized_html,
            'code_blocks': code_blocks,
            'latex_blocks': latex_blocks
        }
    
    def _extract_code_blocks(self, content: str) -> List[Dict]:
        """Extract code blocks and detect their languages."""
        code_blocks = []
        pattern = r'```(\w+)?\n(.*?)```'
        matches = re.finditer(pattern, content, re.DOTALL)
        
        for match in matches:
            original = match.group(0)
            lang = match.group(1) or ''
            code = match.group(2).strip()
            
            if not lang:
                try:
                    lexer = guess_lexer(code)
                    lang = lexer.name.lower()
                except:
                    lang = 'text'
            
            code_blocks.append({
                'original': original,
                'language': lang,
                'code': code
            })
        
        return code_blocks
    
    def _highlight_code(self, code: str, language: str) -> str:
        """Apply syntax highlighting to code."""
        try:
            lexer = get_lexer_by_name(language, stripall=True)
        except:
            lexer = get_lexer_by_name('text', stripall=True)
        
        formatter = HtmlFormatter(
            style='monokai',
            linenos=True,
            cssclass=f'highlight language-{language}'
        )
        
        return pygments.highlight(code, lexer, formatter)
    
    def _extract_latex(self, content: str) -> List[Dict]:
        """Extract LaTeX expressions."""
        latex_blocks = []
        pattern = r'\$\$(.*?)\$\$|\$(.*?)\$'
        matches = re.finditer(pattern, content, re.DOTALL)
        
        for match in matches:
            original = match.group(0)
            latex = match.group(1) or match.group(2)
            latex_blocks.append({
                'original': original,
                'latex': latex
            })
        
        return latex_blocks
    
    def _render_latex(self, latex: str) -> str:
        """Convert LaTeX to MathML for web rendering."""
        try:
            return latex2mathml.converter.convert(latex)
        except:
            return f'<span class="latex-error">{latex}</span>'
    
    def export_to_pdf(self, content: Dict) -> bytes:
        """Export processed content to PDF."""
        # TODO: Implement PDF export using WeasyPrint or similar
        raise NotImplementedError("PDF export not yet implemented")
    
    def export_to_markdown(self, content: Dict) -> str:
        """Convert processed content back to markdown."""
        # TODO: Implement markdown export
        raise NotImplementedError("Markdown export not yet implemented")
