import docker
import tempfile
import os
import json
from typing import Dict, Optional
import subprocess
import shutil

class CodeExecutor:
    """Service for safely executing code snippets in isolated environments."""
    
    # Supported languages and their Docker images
    SUPPORTED_LANGUAGES = {
        'python': 'python:3.9-slim',
        'javascript': 'node:16-alpine',
        'java': 'openjdk:11-jdk-slim',
        'cpp': 'gcc:latest',
        'ruby': 'ruby:3.0-slim'
    }
    
    def __init__(self):
        self.client = docker.from_env()
        self._ensure_images()
    
    def _ensure_images(self):
        """Ensure required Docker images are available."""
        for image in self.SUPPORTED_LANGUAGES.values():
            try:
                self.client.images.pull(image)
            except docker.errors.ImageNotFound:
                raise RuntimeError(f"Failed to pull Docker image: {image}")
    
    def execute_code(self, code: str, language: str, timeout: int = 30) -> Dict:
        """Execute code in a sandboxed environment."""
        if language not in self.SUPPORTED_LANGUAGES:
            raise ValueError(f"Unsupported language: {language}")
        
        # Create temporary directory for code execution
        with tempfile.TemporaryDirectory() as temp_dir:
            # Prepare code file
            file_info = self._prepare_code_file(code, language, temp_dir)
            
            # Run code in container
            return self._run_in_container(
                code_file=file_info['file'],
                language=language,
                command=file_info['command'],
                work_dir=temp_dir,
                timeout=timeout
            )
    
    def _prepare_code_file(self, code: str, language: str, work_dir: str) -> Dict:
        """Prepare code file for execution."""
        file_configs = {
            'python': {'ext': '.py', 'command': ['python']},
            'javascript': {'ext': '.js', 'command': ['node']},
            'java': {'ext': '.java', 'command': ['javac', 'java']},
            'cpp': {'ext': '.cpp', 'command': ['g++', './']},
            'ruby': {'ext': '.rb', 'command': ['ruby']}
        }
        
        config = file_configs[language]
        filename = f'code{config["ext"]}'
        filepath = os.path.join(work_dir, filename)
        
        # Write code to file
        with open(filepath, 'w') as f:
            f.write(code)
        
        return {
            'file': filename,
            'command': config['command']
        }
    
    def _run_in_container(
        self,
        code_file: str,
        language: str,
        command: list,
        work_dir: str,
        timeout: int
    ) -> Dict:
        """Run code in Docker container."""
        try:
            container = self.client.containers.run(
                image=self.SUPPORTED_LANGUAGES[language],
                command=command + [code_file],
                volumes={
                    work_dir: {
                        'bind': '/code',
                        'mode': 'ro'
                    }
                },
                working_dir='/code',
                detach=True,
                mem_limit='100m',
                nano_cpus=1000000000,  # 1 CPU
                network_mode='none'  # Disable network access
            )
            
            try:
                container.wait(timeout=timeout)
                logs = container.logs()
                return {
                    'success': True,
                    'output': logs.decode('utf-8'),
                    'error': None
                }
            except Exception as e:
                return {
                    'success': False,
                    'output': None,
                    'error': str(e)
                }
            finally:
                container.remove(force=True)
                
        except Exception as e:
            return {
                'success': False,
                'output': None,
                'error': f"Execution error: {str(e)}"
            }
    
    def validate_code(self, code: str, language: str) -> Dict:
        """Validate code syntax without execution."""
        validators = {
            'python': self._validate_python,
            'javascript': self._validate_javascript,
            # Add more validators as needed
        }
        
        validator = validators.get(language)
        if not validator:
            return {'valid': True, 'errors': None}  # Skip validation for unsupported languages
            
        return validator(code)
    
    def _validate_python(self, code: str) -> Dict:
        """Validate Python code syntax."""
        try:
            compile(code, '<string>', 'exec')
            return {'valid': True, 'errors': None}
        except SyntaxError as e:
            return {
                'valid': False,
                'errors': {
                    'line': e.lineno,
                    'offset': e.offset,
                    'message': str(e)
                }
            }
    
    def _validate_javascript(self, code: str) -> Dict:
        """Validate JavaScript code syntax using Node.js."""
        with tempfile.NamedTemporaryFile(suffix='.js') as temp:
            temp.write(code.encode())
            temp.flush()
            
            try:
                subprocess.run(
                    ['node', '--check', temp.name],
                    capture_output=True,
                    text=True,
                    check=True
                )
                return {'valid': True, 'errors': None}
            except subprocess.CalledProcessError as e:
                return {
                    'valid': False,
                    'errors': {
                        'message': e.stderr
                    }
                }
