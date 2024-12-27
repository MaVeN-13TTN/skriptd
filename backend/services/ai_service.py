from typing import Dict, List, Optional
import openai
from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqText
import torch
import nltk
from nltk.tokenize import sent_tokenize
import os

class AIService:
    """Service for AI-powered features like note summarization and code explanation."""
    
    def __init__(self):
        # Initialize OpenAI
        self.openai_client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
        # Download required NLTK data
        nltk.download('punkt')
        
        # Initialize local models
        self.summarizer = pipeline(
            "summarization",
            model="facebook/bart-large-cnn",
            device=0 if torch.cuda.is_available() else -1
        )
        
        # Initialize code explanation model
        self.code_explainer = pipeline(
            "text2text-generation",
            model="Salesforce/codet5-base",
            device=0 if torch.cuda.is_available() else -1
        )
    
    def summarize_note(self, content: str, max_length: Optional[int] = 150) -> str:
        """Generate a concise summary of the note content."""
        try:
            # For long content, split into chunks and summarize each
            if len(content) > 1000:
                sentences = sent_tokenize(content)
                chunks = self._create_chunks(sentences)
                summaries = []
                
                for chunk in chunks:
                    summary = self.summarizer(
                        chunk,
                        max_length=max_length // len(chunks),
                        min_length=20,
                        do_sample=False
                    )[0]['summary_text']
                    summaries.append(summary)
                
                return ' '.join(summaries)
            else:
                return self.summarizer(
                    content,
                    max_length=max_length,
                    min_length=20,
                    do_sample=False
                )[0]['summary_text']
                
        except Exception as e:
            return f"Error generating summary: {str(e)}"
    
    def explain_code(self, code: str, language: str) -> Dict:
        """Generate natural language explanation of code."""
        try:
            # Prepare prompt for code explanation
            prompt = f"Explain this {language} code:\n{code}"
            
            # Use OpenAI for detailed explanation
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a coding expert explaining code to CS students."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            # Get local model's simpler explanation
            local_explanation = self.code_explainer(
                f"explain: {code}",
                max_length=150,
                num_return_sequences=1
            )[0]['generated_text']
            
            return {
                'detailed_explanation': response.choices[0].message.content,
                'simple_explanation': local_explanation,
                'language': language
            }
            
        except Exception as e:
            return {
                'error': f"Error explaining code: {str(e)}",
                'language': language
            }
    
    def suggest_improvements(self, code: str, language: str) -> Dict:
        """Suggest improvements for the code."""
        try:
            prompt = f"""Analyze this {language} code and suggest improvements:
            {code}
            
            Focus on:
            1. Code quality and best practices
            2. Performance optimization
            3. Security considerations
            4. Readability and maintainability"""
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a senior developer reviewing code."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            return {
                'suggestions': response.choices[0].message.content,
                'language': language
            }
            
        except Exception as e:
            return {
                'error': f"Error generating suggestions: {str(e)}",
                'language': language
            }
    
    def generate_study_questions(self, content: str) -> List[Dict]:
        """Generate study questions based on note content."""
        try:
            prompt = f"""Generate 5 study questions based on this content:
            {content}
            
            Format each question with:
            1. The question
            2. The correct answer
            3. An explanation of why it's correct"""
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a CS professor creating study materials."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8,
                max_tokens=1000
            )
            
            # Parse the response into structured format
            raw_questions = response.choices[0].message.content.split('\n\n')
            questions = []
            
            for q in raw_questions:
                if q.strip():
                    parts = q.split('\n')
                    if len(parts) >= 3:
                        questions.append({
                            'question': parts[0].replace('Q: ', '').strip(),
                            'answer': parts[1].replace('A: ', '').strip(),
                            'explanation': parts[2].replace('Explanation: ', '').strip()
                        })
            
            return questions
            
        except Exception as e:
            return [{'error': f"Error generating questions: {str(e)}"}]
    
    def _create_chunks(self, sentences: List[str], max_chunk_size: int = 1000) -> List[str]:
        """Create chunks of text from sentences."""
        chunks = []
        current_chunk = []
        current_size = 0
        
        for sentence in sentences:
            sentence_size = len(sentence)
            if current_size + sentence_size > max_chunk_size:
                chunks.append(' '.join(current_chunk))
                current_chunk = [sentence]
                current_size = sentence_size
            else:
                current_chunk.append(sentence)
                current_size += sentence_size
        
        if current_chunk:
            chunks.append(' '.join(current_chunk))
        
        return chunks
