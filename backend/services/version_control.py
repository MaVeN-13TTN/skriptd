from typing import Dict, List, Optional
import git
from git import Repo
import pygit2
import os
from datetime import datetime
import json
import shutil

class VersionControlService:
    """Service for Git integration and version control features."""
    
    def __init__(self, base_path: str):
        self.base_path = base_path
        self.repos_path = os.path.join(base_path, 'git_repos')
        os.makedirs(self.repos_path, exist_ok=True)
    
    def init_user_repo(self, user_id: str) -> Dict:
        """Initialize a Git repository for a user."""
        try:
            user_repo_path = os.path.join(self.repos_path, str(user_id))
            
            if not os.path.exists(user_repo_path):
                os.makedirs(user_repo_path)
                repo = Repo.init(user_repo_path)
                
                # Create initial structure
                notes_dir = os.path.join(user_repo_path, 'notes')
                os.makedirs(notes_dir)
                
                # Create .gitignore
                gitignore_content = """
                *.pyc
                __pycache__
                .DS_Store
                .env
                """
                with open(os.path.join(user_repo_path, '.gitignore'), 'w') as f:
                    f.write(gitignore_content.strip())
                
                # Initial commit
                repo.index.add(['.gitignore'])
                repo.index.commit('Initial commit')
                
                return {
                    'status': 'success',
                    'message': 'Repository initialized successfully',
                    'repo_path': user_repo_path
                }
            else:
                return {
                    'status': 'exists',
                    'message': 'Repository already exists',
                    'repo_path': user_repo_path
                }
                
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Error initializing repository: {str(e)}'
            }
    
    def save_note_version(self, user_id: str, note_id: str, content: Dict) -> Dict:
        """Save a new version of a note to Git."""
        try:
            repo_path = os.path.join(self.repos_path, str(user_id))
            repo = Repo(repo_path)
            
            # Create note file path
            note_path = os.path.join(repo_path, 'notes', f'{note_id}.json')
            
            # Save note content
            note_data = {
                'content': content,
                'updated_at': datetime.utcnow().isoformat()
            }
            
            with open(note_path, 'w') as f:
                json.dump(note_data, f, indent=2)
            
            # Commit changes
            repo.index.add([f'notes/{note_id}.json'])
            commit = repo.index.commit(f'Update note {note_id}')
            
            return {
                'status': 'success',
                'message': 'Note version saved successfully',
                'commit_hash': commit.hexsha
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Error saving note version: {str(e)}'
            }
    
    def get_note_history(self, user_id: str, note_id: str) -> List[Dict]:
        """Get the version history of a note."""
        try:
            repo_path = os.path.join(self.repos_path, str(user_id))
            repo = Repo(repo_path)
            
            note_path = f'notes/{note_id}.json'
            commits = list(repo.iter_commits(paths=note_path))
            
            history = []
            for commit in commits:
                # Get note content at this commit
                note_content = repo.git.show(f'{commit.hexsha}:{note_path}')
                
                history.append({
                    'commit_hash': commit.hexsha,
                    'message': commit.message,
                    'author': commit.author.name,
                    'date': commit.authored_datetime.isoformat(),
                    'content': json.loads(note_content)
                })
            
            return history
            
        except Exception as e:
            return [{
                'error': f'Error retrieving note history: {str(e)}'
            }]
    
    def restore_note_version(self, user_id: str, note_id: str, commit_hash: str) -> Dict:
        """Restore a note to a specific version."""
        try:
            repo_path = os.path.join(self.repos_path, str(user_id))
            repo = Repo(repo_path)
            
            note_path = f'notes/{note_id}.json'
            
            # Get content from specific commit
            note_content = repo.git.show(f'{commit_hash}:{note_path}')
            
            # Save as current version
            current_path = os.path.join(repo_path, 'notes', f'{note_id}.json')
            with open(current_path, 'w') as f:
                f.write(note_content)
            
            # Commit the restoration
            repo.index.add([note_path])
            commit = repo.index.commit(f'Restored note {note_id} to version {commit_hash}')
            
            return {
                'status': 'success',
                'message': 'Note version restored successfully',
                'commit_hash': commit.hexsha,
                'content': json.loads(note_content)
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Error restoring note version: {str(e)}'
            }
    
    def create_branch(self, user_id: str, branch_name: str) -> Dict:
        """Create a new branch for the user's repository."""
        try:
            repo_path = os.path.join(self.repos_path, str(user_id))
            repo = Repo(repo_path)
            
            current = repo.active_branch
            new_branch = repo.create_head(branch_name)
            new_branch.checkout()
            
            return {
                'status': 'success',
                'message': f'Branch {branch_name} created successfully',
                'previous_branch': current.name,
                'new_branch': branch_name
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Error creating branch: {str(e)}'
            }
    
    def merge_branches(self, user_id: str, source_branch: str, target_branch: str) -> Dict:
        """Merge two branches."""
        try:
            repo_path = os.path.join(self.repos_path, str(user_id))
            repo = Repo(repo_path)
            
            # Checkout target branch
            repo.git.checkout(target_branch)
            
            # Perform merge
            repo.git.merge(source_branch)
            
            return {
                'status': 'success',
                'message': f'Merged {source_branch} into {target_branch} successfully'
            }
            
        except git.GitCommandError as e:
            # Handle merge conflicts
            return {
                'status': 'conflict',
                'message': 'Merge conflicts detected',
                'conflicts': self._get_conflicts(repo)
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Error merging branches: {str(e)}'
            }
    
    def _get_conflicts(self, repo: Repo) -> List[Dict]:
        """Get information about merge conflicts."""
        conflicts = []
        for item in repo.index.unmerged_blobs():
            conflicts.append({
                'file': item,
                'status': 'conflict'
            })
        return conflicts
