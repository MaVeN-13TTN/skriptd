from typing import Dict, List, Optional, BinaryIO
import json
import os
from datetime import datetime
import pdfkit
import html2text
from jinja2 import Environment, FileSystemLoader
import zipfile
import io

class ExportService:
    """Service for exporting notes in various formats."""
    
    def __init__(self, templates_path: str):
        self.templates_path = templates_path
        self.jinja_env = Environment(loader=FileSystemLoader(templates_path))
        self.html2text = html2text.HTML2Text()
        self.html2text.body_width = 0  # Disable wrapping
        
        # Configure PDF options
        self.pdf_options = {
            'page-size': 'A4',
            'margin-top': '0.75in',
            'margin-right': '0.75in',
            'margin-bottom': '0.75in',
            'margin-left': '0.75in',
            'encoding': 'UTF-8',
            'custom-header': [
                ('Accept-Encoding', 'gzip')
            ],
            'no-outline': None,
            'enable-local-file-access': None
        }
    
    def export_to_pdf(self, note: Dict, include_metadata: bool = True) -> bytes:
        """Export a note to PDF format."""
        try:
            # Prepare HTML content
            template = self.jinja_env.get_template('note_template.html')
            html_content = template.render(
                title=note['title'],
                content=note['processed_content']['html'],
                metadata=note if include_metadata else None,
                export_date=datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
            )
            
            # Convert HTML to PDF
            pdf_content = pdfkit.from_string(
                html_content,
                False,  # Don't save to file
                options=self.pdf_options
            )
            
            return pdf_content
            
        except Exception as e:
            raise ExportError(f"Error exporting to PDF: {str(e)}")
    
    def export_to_html(self, note: Dict, include_metadata: bool = True) -> str:
        """Export a note to HTML format."""
        try:
            template = self.jinja_env.get_template('note_template.html')
            return template.render(
                title=note['title'],
                content=note['processed_content']['html'],
                metadata=note if include_metadata else None,
                export_date=datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
            )
            
        except Exception as e:
            raise ExportError(f"Error exporting to HTML: {str(e)}")
    
    def export_to_markdown(self, note: Dict) -> str:
        """Export a note to Markdown format."""
        try:
            # Convert HTML to Markdown
            markdown_content = self.html2text.handle(note['processed_content']['html'])
            
            # Add YAML frontmatter
            frontmatter = f"""---
title: {note['title']}
created: {note['created_at']}
updated: {note['updated_at']}
tags: {', '.join(note['tags'])}
---

"""
            return frontmatter + markdown_content
            
        except Exception as e:
            raise ExportError(f"Error exporting to Markdown: {str(e)}")
    
    def batch_export(
        self,
        notes: List[Dict],
        format: str,
        include_metadata: bool = True
    ) -> BinaryIO:
        """Export multiple notes as a zip archive."""
        try:
            # Create in-memory zip file
            zip_buffer = io.BytesIO()
            
            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                for note in notes:
                    filename = self._get_safe_filename(note['title'])
                    
                    if format == 'pdf':
                        content = self.export_to_pdf(note, include_metadata)
                        zip_file.writestr(f"{filename}.pdf", content)
                    
                    elif format == 'html':
                        content = self.export_to_html(note, include_metadata)
                        zip_file.writestr(f"{filename}.html", content)
                    
                    elif format == 'markdown':
                        content = self.export_to_markdown(note)
                        zip_file.writestr(f"{filename}.md", content)
                    
                    else:
                        raise ValueError(f"Unsupported format: {format}")
                
                # Add README
                readme_content = self._generate_readme(notes, format)
                zip_file.writestr('README.md', readme_content)
            
            zip_buffer.seek(0)
            return zip_buffer
            
        except Exception as e:
            raise ExportError(f"Error in batch export: {str(e)}")
    
    def _get_safe_filename(self, filename: str) -> str:
        """Convert a string to a safe filename."""
        # Remove invalid characters
        safe_name = "".join(c for c in filename if c.isalnum() or c in (' ', '-', '_'))
        # Replace spaces with underscores
        safe_name = safe_name.replace(' ', '_')
        return safe_name
    
    def _generate_readme(self, notes: List[Dict], format: str) -> str:
        """Generate README file for the export."""
        template = self.jinja_env.get_template('export_readme.md')
        return template.render(
            notes=notes,
            format=format,
            export_date=datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'),
            total_notes=len(notes)
        )


class ExportError(Exception):
    """Custom exception for export errors."""
    pass
