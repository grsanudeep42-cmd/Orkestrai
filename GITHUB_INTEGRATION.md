# OrkestrAI - GitHub Integration Workflow

## GitHub Integration Architecture

### Overview

The GitHub integration allows OrkestrAI to automatically:
1. Create repositories
2. Generate issues from features
3. Set up project boards
4. Push generated code
5. Create initial commits
6. Set up CI/CD workflows

## Authentication Flow

### OAuth 2.0 Implementation

```python
# app/api/v1/endpoints/github.py
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import RedirectResponse
from app.services.github_service import GitHubService
from app.config import settings
import secrets

router = APIRouter()

# Store state tokens temporarily (use Redis in production)
oauth_states = {}

@router.get("/auth")
async def github_auth():
    """Initiate GitHub OAuth flow"""
    state = secrets.token_urlsafe(32)
    oauth_states[state] = True
    
    github_auth_url = (
        f"https://github.com/login/oauth/authorize"
        f"?client_id={settings.GITHUB_CLIENT_ID}"
        f"&redirect_uri={settings.GITHUB_REDIRECT_URI}"
        f"&scope=repo,user,write:org"
        f"&state={state}"
    )
    
    return RedirectResponse(url=github_auth_url)

@router.get("/callback")
async def github_callback(code: str, state: str):
    """Handle GitHub OAuth callback"""
    # Verify state
    if state not in oauth_states:
        raise HTTPException(status_code=400, detail="Invalid state")
    
    # Exchange code for access token
    github_service = GitHubService()
    access_token = await github_service.exchange_code_for_token(code)
    
    # Get user info
    user_info = await github_service.get_user_info(access_token)
    
    # Store encrypted token (implement encryption)
    # Return to frontend with success
    
    return RedirectResponse(
        url=f"{settings.FRONTEND_URL}/dashboard?github_connected=true"
    )
```

## GitHub Service Implementation

```python
# app/services/github_service.py
from github import Github, GithubException
from typing import List, Dict, Optional
import httpx
from app.config import settings
from app.schemas.github import (
    RepositoryCreate,
    IssueCreate,
    MilestoneCreate,
    ProjectBoardCreate
)

class GitHubService:
    def __init__(self, access_token: Optional[str] = None):
        self.access_token = access_token
        self.client = Github(access_token) if access_token else None
    
    async def exchange_code_for_token(self, code: str) -> str:
        """Exchange OAuth code for access token"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://github.com/login/oauth/access_token",
                data={
                    "client_id": settings.GITHUB_CLIENT_ID,
                    "client_secret": settings.GITHUB_CLIENT_SECRET,
                    "code": code,
                    "redirect_uri": settings.GITHUB_REDIRECT_URI
                },
                headers={"Accept": "application/json"}
            )
            
            data = response.json()
            return data.get("access_token")
    
    async def get_user_info(self, access_token: str) -> Dict:
        """Get GitHub user information"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://api.github.com/user",
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Accept": "application/vnd.github.v3+json"
                }
            )
            return response.json()
    
    async def create_repository(
        self,
        repo_data: RepositoryCreate
    ) -> Dict:
        """Create a new GitHub repository"""
        try:
            user = self.client.get_user()
            repo = user.create_repo(
                name=repo_data.name,
                description=repo_data.description,
                private=repo_data.private,
                auto_init=False,  # We'll push code ourselves
                has_issues=True,
                has_projects=True,
                has_wiki=False
            )
            
            # Add topics
            if repo_data.topics:
                repo.replace_topics(repo_data.topics)
            
            return {
                "name": repo.name,
                "full_name": repo.full_name,
                "html_url": repo.html_url,
                "clone_url": repo.clone_url,
                "ssh_url": repo.ssh_url
            }
            
        except GithubException as e:
            raise Exception(f"Failed to create repository: {e.data}")
    
    async def create_issues(
        self,
        repo_full_name: str,
        issues: List[IssueCreate]
    ) -> List[Dict]:
        """Create multiple issues in a repository"""
        try:
            repo = self.client.get_repo(repo_full_name)
            created_issues = []
            
            for issue_data in issues:
                issue = repo.create_issue(
                    title=issue_data.title,
                    body=issue_data.body,
                    labels=issue_data.labels,
                    milestone=self._get_milestone(repo, issue_data.milestone) if issue_data.milestone else None
                )
                
                created_issues.append({
                    "number": issue.number,
                    "title": issue.title,
                    "html_url": issue.html_url,
                    "state": issue.state
                })
            
            return created_issues
            
        except GithubException as e:
            raise Exception(f"Failed to create issues: {e.data}")
    
    async def create_milestones(
        self,
        repo_full_name: str,
        milestones: List[MilestoneCreate]
    ) -> List[Dict]:
        """Create milestones in a repository"""
        try:
            repo = self.client.get_repo(repo_full_name)
            created_milestones = []
            
            for milestone_data in milestones:
                milestone = repo.create_milestone(
                    title=milestone_data.title,
                    description=milestone_data.description,
                    due_on=milestone_data.due_date
                )
                
                created_milestones.append({
                    "number": milestone.number,
                    "title": milestone.title,
                    "html_url": milestone.html_url
                })
            
            return created_milestones
            
        except GithubException as e:
            raise Exception(f"Failed to create milestones: {e.data}")
    
    async def create_project_board(
        self,
        repo_full_name: str,
        board_data: ProjectBoardCreate
    ) -> Dict:
        """Create a project board with columns"""
        try:
            repo = self.client.get_repo(repo_full_name)
            
            # Create project
            project = repo.create_project(
                name=board_data.name,
                body=board_data.description
            )
            
            # Create columns
            columns = []
            for column_name in board_data.columns:
                column = project.create_column(column_name)
                columns.append({
                    "id": column.id,
                    "name": column.name
                })
            
            return {
                "id": project.id,
                "name": project.name,
                "html_url": project.html_url,
                "columns": columns
            }
            
        except GithubException as e:
            raise Exception(f"Failed to create project board: {e.data}")
    
    async def push_code(
        self,
        repo_full_name: str,
        files: List[Dict[str, str]],
        commit_message: str = "Initial commit from OrkestrAI"
    ) -> Dict:
        """Push generated code to repository"""
        try:
            repo = self.client.get_repo(repo_full_name)
            
            # Create or update files
            for file_data in files:
                try:
                    # Try to get existing file
                    contents = repo.get_contents(file_data["path"])
                    repo.update_file(
                        path=file_data["path"],
                        message=commit_message,
                        content=file_data["content"],
                        sha=contents.sha
                    )
                except GithubException:
                    # File doesn't exist, create it
                    repo.create_file(
                        path=file_data["path"],
                        message=commit_message,
                        content=file_data["content"]
                    )
            
            # Get latest commit
            commits = repo.get_commits()
            latest_commit = commits[0]
            
            return {
                "commit_sha": latest_commit.sha,
                "commit_url": latest_commit.html_url,
                "files_pushed": len(files)
            }
            
        except GithubException as e:
            raise Exception(f"Failed to push code: {e.data}")
    
    async def create_issue_templates(
        self,
        repo_full_name: str,
        templates: Dict[str, str]
    ) -> Dict:
        """Create issue and PR templates"""
        try:
            repo = self.client.get_repo(repo_full_name)
            
            # Create .github directory structure
            github_dir = ".github"
            
            # Issue template
            if "issue" in templates:
                repo.create_file(
                    path=f"{github_dir}/ISSUE_TEMPLATE/feature_request.md",
                    message="Add issue template",
                    content=templates["issue"]
                )
            
            # PR template
            if "pull_request" in templates:
                repo.create_file(
                    path=f"{github_dir}/PULL_REQUEST_TEMPLATE.md",
                    message="Add PR template",
                    content=templates["pull_request"]
                )
            
            # Contributing guidelines
            if "contributing" in templates:
                repo.create_file(
                    path="CONTRIBUTING.md",
                    message="Add contributing guidelines",
                    content=templates["contributing"]
                )
            
            return {"status": "Templates created successfully"}
            
        except GithubException as e:
            raise Exception(f"Failed to create templates: {e.data}")
    
    async def setup_github_actions(
        self,
        repo_full_name: str,
        workflow_config: str
    ) -> Dict:
        """Set up GitHub Actions workflow"""
        try:
            repo = self.client.get_repo(repo_full_name)
            
            # Create workflow file
            repo.create_file(
                path=".github/workflows/ci.yml",
                message="Add CI/CD workflow",
                content=workflow_config
            )
            
            return {"status": "GitHub Actions configured"}
            
        except GithubException as e:
            raise Exception(f"Failed to setup GitHub Actions: {e.data}")
    
    def _get_milestone(self, repo, milestone_title: str):
        """Get milestone by title"""
        milestones = repo.get_milestones()
        for milestone in milestones:
            if milestone.title == milestone_title:
                return milestone
        return None
```

## Complete GitHub Integration Endpoint

```python
# app/api/v1/endpoints/github.py (continued)

@router.post("/projects/{project_id}/github/create-repo")
async def create_github_repo(
    project_id: str,
    repo_data: RepositoryCreate,
    github_service: GitHubService = Depends(get_github_service)
):
    """Create GitHub repository from project"""
    try:
        # Get project data
        project = await get_project(project_id)
        
        # Create repository
        repo_info = await github_service.create_repository(repo_data)
        
        # Create milestones
        if project.github_output.get("milestones"):
            milestones = await github_service.create_milestones(
                repo_info["full_name"],
                project.github_output["milestones"]
            )
        
        # Create issues
        if project.github_output.get("issues"):
            issues = await github_service.create_issues(
                repo_info["full_name"],
                project.github_output["issues"]
            )
        
        # Create project board
        if project.github_output.get("project_board"):
            board = await github_service.create_project_board(
                repo_info["full_name"],
                project.github_output["project_board"]
            )
        
        # Push generated code
        if project.code_output.get("generated_files"):
            files = [
                {
                    "path": file["path"],
                    "content": file["content"]
                }
                for file in project.code_output["generated_files"]
            ]
            
            commit_info = await github_service.push_code(
                repo_info["full_name"],
                files,
                "Initial commit: Project scaffolding from OrkestrAI"
            )
        
        # Create templates
        if project.github_output.get("templates"):
            await github_service.create_issue_templates(
                repo_info["full_name"],
                project.github_output["templates"]
            )
        
        # Setup CI/CD (optional)
        if repo_data.setup_ci:
            workflow = generate_ci_workflow(project)
            await github_service.setup_github_actions(
                repo_info["full_name"],
                workflow
            )
        
        # Update project with GitHub info
        await update_project_github_info(project_id, {
            "repo_url": repo_info["html_url"],
            "repo_name": repo_info["full_name"],
            "issues_created": len(issues) if issues else 0,
            "initial_commit": commit_info["commit_sha"] if commit_info else None
        })
        
        return {
            "status": "success",
            "repository": repo_info,
            "issues_created": len(issues) if issues else 0,
            "milestones_created": len(milestones) if milestones else 0,
            "files_pushed": commit_info["files_pushed"] if commit_info else 0
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

## GitHub Workflow Templates

### CI/CD Workflow Generator

```python
# app/utils/github_workflows.py

def generate_ci_workflow(project: Project) -> str:
    """Generate GitHub Actions workflow based on project tech stack"""
    
    tech_stack = project.architecture_output.get("tech_stack", {})
    
    # Frontend workflow
    frontend_workflow = ""
    if "Next.js" in tech_stack.get("frontend", []):
        frontend_workflow = """
  frontend-test:
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: ./frontend
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
      - run: npm ci
      - run: npm run build
      - run: npm test
"""
    
    # Backend workflow
    backend_workflow = ""
    if "FastAPI" in tech_stack.get("backend", []):
        backend_workflow = """
  backend-test:
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: ./backend
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt
      - run: pytest
"""
    
    workflow = f"""
name: CI/CD Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
{frontend_workflow}
{backend_workflow}

  deploy:
    needs: [frontend-test, backend-test]
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v3
      - name: Deploy to production
        run: echo "Deploy to production"
"""
    
    return workflow

def generate_issue_template() -> str:
    """Generate issue template"""
    return """---
name: Feature Request
about: Suggest a new feature for this project
title: '[FEATURE] '
labels: enhancement
assignees: ''
---

## Feature Description
A clear and concise description of the feature.

## Problem Statement
What problem does this feature solve?

## Proposed Solution
How should this feature work?

## Acceptance Criteria
- [ ] Criterion 1
- [ ] Criterion 2
- [ ] Criterion 3

## Additional Context
Add any other context or screenshots about the feature request.
"""

def generate_pr_template() -> str:
    """Generate PR template"""
    return """## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Related Issues
Closes #(issue number)

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] Manual testing completed

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Comments added for complex code
- [ ] Documentation updated
- [ ] No new warnings generated
"""
```

## Frontend GitHub Integration

### GitHub Connection Component

```tsx
// components/github/github-connect.tsx
'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Github } from 'lucide-react';

export function GitHubConnect() {
  const [connecting, setConnecting] = useState(false);
  
  const handleConnect = () => {
    setConnecting(true);
    // Redirect to GitHub OAuth
    window.location.href = `${process.env.NEXT_PUBLIC_API_URL}/api/v1/github/auth`;
  };
  
  return (
    <Button
      onClick={handleConnect}
      disabled={connecting}
      className="flex items-center gap-2"
    >
      <Github className="w-4 h-4" />
      {connecting ? 'Connecting...' : 'Connect GitHub'}
    </Button>
  );
}
```

### Repository Creation Component

```tsx
// components/github/create-repo-dialog.tsx
'use client';

import { useState } from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Checkbox } from '@/components/ui/checkbox';
import { createGitHubRepo } from '@/lib/api/github';

interface CreateRepoDialogProps {
  projectId: string;
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export function CreateRepoDialog({ projectId, open, onOpenChange }: CreateRepoDialogProps) {
  const [repoName, setRepoName] = useState('');
  const [isPrivate, setIsPrivate] = useState(false);
  const [createIssues, setCreateIssues] = useState(true);
  const [pushCode, setPushCode] = useState(true);
  const [setupCI, setSetupCI] = useState(false);
  const [loading, setLoading] = useState(false);
  
  const handleCreate = async () => {
    setLoading(true);
    try {
      const result = await createGitHubRepo(projectId, {
        name: repoName,
        private: isPrivate,
        create_issues: createIssues,
        push_code: pushCode,
        setup_ci: setupCI
      });
      
      // Show success message
      alert(`Repository created: ${result.repository.html_url}`);
      onOpenChange(false);
    } catch (error) {
      alert('Failed to create repository');
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Create GitHub Repository</DialogTitle>
        </DialogHeader>
        
        <div className="space-y-4">
          <div>
            <label className="text-sm font-medium">Repository Name</label>
            <Input
              value={repoName}
              onChange={(e) => setRepoName(e.target.value)}
              placeholder="my-awesome-project"
            />
          </div>
          
          <div className="space-y-2">
            <div className="flex items-center gap-2">
              <Checkbox
                checked={isPrivate}
                onCheckedChange={setIsPrivate}
              />
              <label className="text-sm">Private repository</label>
            </div>
            
            <div className="flex items-center gap-2">
              <Checkbox
                checked={createIssues}
                onCheckedChange={setCreateIssues}
              />
              <label className="text-sm">Create issues from features</label>
            </div>
            
            <div className="flex items-center gap-2">
              <Checkbox
                checked={pushCode}
                onCheckedChange={setPushCode}
              />
              <label className="text-sm">Push generated code</label>
            </div>
            
            <div className="flex items-center gap-2">
              <Checkbox
                checked={setupCI}
                onCheckedChange={setSetupCI}
              />
              <label className="text-sm">Setup CI/CD workflow</label>
            </div>
          </div>
          
          <Button
            onClick={handleCreate}
            disabled={!repoName || loading}
            className="w-full"
          >
            {loading ? 'Creating...' : 'Create Repository'}
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
}
```

## Security Considerations

### Token Storage

```python
# app/core/security.py
from cryptography.fernet import Fernet
from app.config import settings

class TokenEncryption:
    def __init__(self):
        self.cipher = Fernet(settings.ENCRYPTION_KEY.encode())
    
    def encrypt_token(self, token: str) -> str:
        """Encrypt GitHub access token"""
        return self.cipher.encrypt(token.encode()).decode()
    
    def decrypt_token(self, encrypted_token: str) -> str:
        """Decrypt GitHub access token"""
        return self.cipher.decrypt(encrypted_token.encode()).decode()
```

### Rate Limiting

```python
# app/middleware/rate_limit.py
from fastapi import Request, HTTPException
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@limiter.limit("10/minute")
async def github_rate_limit(request: Request):
    """Rate limit GitHub API calls"""
    pass
```

## Error Handling

```python
# app/core/exceptions.py

class GitHubIntegrationError(Exception):
    """Base exception for GitHub integration errors"""
    pass

class GitHubAuthError(GitHubIntegrationError):
    """GitHub authentication failed"""
    pass

class GitHubAPIError(GitHubIntegrationError):
    """GitHub API request failed"""
    pass

class RepositoryExistsError(GitHubIntegrationError):
    """Repository already exists"""
    pass
```

## Testing GitHub Integration

```python
# tests/test_github_service.py
import pytest
from app.services.github_service import GitHubService
from unittest.mock import Mock, patch

@pytest.fixture
def github_service():
    return GitHubService(access_token="test_token")

@pytest.mark.asyncio
async def test_create_repository(github_service):
    """Test repository creation"""
    with patch.object(github_service.client, 'get_user') as mock_user:
        mock_repo = Mock()
        mock_repo.name = "test-repo"
        mock_repo.html_url = "https://github.com/user/test-repo"
        mock_user.return_value.create_repo.return_value = mock_repo
        
        result = await github_service.create_repository({
            "name": "test-repo",
            "description": "Test repository",
            "private": False
        })
        
        assert result["name"] == "test-repo"
        assert "html_url" in result

@pytest.mark.asyncio
async def test_create_issues(github_service):
    """Test issue creation"""
    # Test implementation
    pass