"""
GitHub Agent - Generates repository structure, creates a real GitHub repo, and pushes code
"""
from typing import Dict, Any, Callable, Optional, List
from datetime import datetime
from pydantic import BaseModel
import structlog
import json
import os
import zipfile
import tempfile
import uuid
from github import Github, GithubException
import requests
import base64
import yaml
from app.config import settings
from app.llm.provider_router import router as llm_router
from app.agents.base_agent import BaseAgent

from app.db.models.user import User

logger = structlog.get_logger()

class GithubWorkflow(BaseModel):
    name: str
    content: str

class GithubOutputPlan(BaseModel):
    repository_name: str
    repository_description: str
    workflows: List[GithubWorkflow]
    issues: List[Dict[str, str]]

class GitHubAgent(BaseAgent):
    """GitHub Agent for creating repos and pushing code"""
    
    def __init__(self):
        self.system_prompt = """You are an elite DevOps Engineer and Open Source Maintainer.
Your goal is to define the ideal repository setup and automation for a new project.

CORE RESPONSIBILITIES:
1) Repository Name & Description - Professional, SEO-friendly, and descriptive.
2) CI/CD Workflows - Practical GitHub Action YAMLs for testing, linting, and deployment.
3) Issue Backlog - 5-10 detailed, actionable issues covering immediate next steps.
4) Branching Strategy - Define a clear main/develop/feature workflow.

CRITICAL INSTRUCTIONS:
- Do NOT use generic placeholders.
- Ensure YAML workflows use correct paths and tools based on the actual file tree.
- Issues must have clear titles and descriptive bodies.
- Output should be structured and ready for direct API integration or manual setup."""
    
    async def generate_github_recommendations(
        self, 
        strategy_output: Dict[str, Any] | str,
        architecture_output: Dict[str, Any] | str,
        implementation_output: Dict[str, Any],
        user_input: str,
        preferences: Optional[Dict[str, Any]] = None,
        memory: Optional[Dict[str, Any]] = None,
        event_callback: Optional[Callable] = None,
        current_user: Optional[User] = None
    ) -> Dict[str, Any]:
        """
        Create a GitHub repository, push code, and set up workflows/issues
        """
        start_time = datetime.utcnow()
        
        try:
            if event_callback:
                await event_callback({
                    "type": "agent_start",
                    "agent": "GitHubAgent",
                    "timestamp": start_time.isoformat()
                })
            
            memory_context = self.format_memory(memory)
            safe_input = self.sanitize_input(user_input)
            
            strategy_text = strategy_output if isinstance(strategy_output, str) else json.dumps(strategy_output)
            
            shared_context = memory.get("shared_context", {}) if memory else {}
            arch_context = shared_context.get("architecture", architecture_output)
            arch_text = arch_context if isinstance(arch_context, str) else json.dumps(arch_context)
            
            impl_context = shared_context.get("implementation", implementation_output)
            file_tree = impl_context.get("file_tree", [])
            file_tree_str = "\n".join(file_tree)

            user_prompt = f"""Based on the project strategy, architecture, and implementation plan, generate GitHub repository details:

PROJECT IDEA:
{safe_input}

PRODUCT STRATEGY:
{strategy_text[:1000]}

SYSTEM ARCHITECTURE:
{arch_text[:1000]}

PROJECT FILE TREE:
{file_tree_str}

IMPLEMENTATION SUMMARY:
{implementation_output.get("message", "Generated code.")}

CRITICAL CI/CD INSTRUCTIONS:
- Use correct working directories that match the actual folder structure from the Architecture output and Project File Tree.
- Only reference tools and package managers that exist in the generated files (e.g., use 'npm' only if 'package.json' exists, use 'pip' only if 'requirements.txt' exists).

Create comprehensive GitHub details including:
1. **Repository Name**: A suitable, slugified name for the project (e.g., 'nexus-core-app')
2. **Repository Description**: A short description
3. **Workflows**: CI/CD pipeline YAML contents (e.g., ci.yml, cd.yml). Must be valid YAML.
4. **Issues**: 5-10 real GitHub Issues based on the implementation phases (each with 'title' and 'body')
"""
            
            if event_callback:
                await event_callback({
                    "type": "agent_thinking",
                    "agent": "GitHubAgent",
                    "message": "Generating repository metadata and GitHub workflows...",
                    "timestamp": datetime.utcnow().isoformat()
                })
            
            logger.info("Calling LLM Provider Router for GitHubAgent")
            
            github_plan = await self.generate_structured_with_fallback(
                system_prompt=self.system_prompt,
                user_prompt=user_prompt,
                response_model=GithubOutputPlan,
                agent_name="GitHubAgent",
                temperature=0.4,
                event_callback=event_callback,
                fallback_func=self._create_fallback_github,
                fallback_args=(strategy_output, architecture_output, implementation_output)
            )

            if event_callback:
                await event_callback({
                    "type": "agent_thinking",
                    "agent": "GitHubAgent",
                    "message": "Authenticating with GitHub and creating repository...",
                    "timestamp": datetime.utcnow().isoformat()
                })

            repo_url = ""
            issues_created = 0
            workflows_created = 0

            # Use user's token from database first, fallback to settings ONLY for testing
            github_token = current_user.github_token if current_user and current_user.github_token else settings.GITHUB_TOKEN
            
            if github_token and github_token != "your_github_personal_access_token_here":
                try:
                    g = Github(github_token)
                    user = g.get_user()
                    
                    repo_name = github_plan.get("repository_name", f"project-{uuid.uuid4().hex[:8]}")
                    
                    try:
                        repo = user.create_repo(
                            name=repo_name,
                            description=github_plan.get("repository_description", "Generated by OrkestrAI"),
                            private=False,
                            auto_init=True
                        )
                    except GithubException as ge:
                        if ge.status == 422:
                            repo_name = f"{repo_name}-{uuid.uuid4().hex[:6]}"
                            repo = user.create_repo(
                                name=repo_name,
                                description=github_plan.get("repository_description", "Generated by OrkestrAI"),
                                private=False,
                                auto_init=True
                            )
                        else:
                            raise ge

                    repo_url = repo.html_url

                    # Push code from Builder output in shared execution memory via GitHub API
                    builder_output = shared_context.get("implementation", implementation_output) if 'shared_context' in locals() else implementation_output
                    files = builder_output.get("files", [])
                    
                    for file_obj in files:
                        path = file_obj.get("path")
                        content = file_obj.get("content", "")
                        
                        try:
                            encoded_content = base64.b64encode(content.encode("utf-8")).decode("utf-8")
                            api_url = f"https://api.github.com/repos/{user.login}/{repo.name}/contents/{path}"
                            headers = {
                                "Authorization": f"token {github_token}",
                                "Accept": "application/vnd.github.v3+json"
                            }
                            payload = {
                                "message": f"Add {path}",
                                "content": encoded_content,
                                "branch": "main"
                            }
                            
                            response = requests.put(api_url, headers=headers, json=payload)
                            response.raise_for_status()
                        except Exception as req_e:
                            logger.warning(f"Could not create file {path} via API: {req_e}")
                            # fallback to PyGithub
                            try:
                                repo.create_file(
                                    path=path,
                                    message=f"Add {path}",
                                    content=content,
                                    branch="main"
                                )
                            except GithubException as ge:
                                logger.warning(f"Could not create file {path} via PyGithub: {ge}")

                    # Add workflows after pushing code
                    for wf in github_plan.get("workflows", []):
                        try:
                            yaml.safe_load(wf['content'])
                            repo.create_file(
                                path=f".github/workflows/{wf['name']}.yml",
                                message=f"Add {wf['name']} workflow",
                                content=wf['content'],
                                branch="main"
                            )
                            workflows_created += 1
                        except yaml.YAMLError as ye:
                            logger.warning(f"Invalid YAML for workflow {wf['name']}: {ye}")
                        except Exception as e:
                            logger.warning(f"Failed to add workflow {wf['name']}: {e}")

                    # Create Develop branch
                    try:
                        main_ref = repo.get_git_ref("heads/main")
                        repo.create_git_ref(ref="refs/heads/develop", sha=main_ref.object.sha)
                    except Exception as e:
                        logger.warning(f"Failed to create develop branch: {e}")

                    # Branch protection
                    try:
                        main_branch = repo.get_branch("main")
                        main_branch.edit_protection(
                            enforce_admins=True,
                            dismiss_stale_reviews=True,
                            required_approving_review_count=1
                        )
                    except Exception as e:
                        logger.warning(f"Failed to add branch protection: {e}")

                    # Create Issues
                    for issue in github_plan.get("issues", []):
                        repo.create_issue(
                            title=issue.get("title", "Task"),
                            body=issue.get("body", "Description")
                        )
                        issues_created += 1

                except Exception as github_err:
                    logger.error(f"GitHub API Error: {github_err}")
                    if event_callback:
                        await event_callback({
                            "type": "error",
                            "agent": "GitHubAgent",
                            "error": str(github_err),
                            "details": "Failed to push to GitHub due to API error or invalid token.",
                            "timestamp": datetime.utcnow().isoformat()
                        })
            else:
                if event_callback:
                    await event_callback({
                        "type": "agent_thinking",
                        "agent": "GitHubAgent",
                        "message": "GITHUB_TOKEN not configured. Skipping actual repository creation.",
                        "timestamp": datetime.utcnow().isoformat()
                    })

            output_data = {
                "repository_name": github_plan.get("repository_name", "project"),
                "repository_url": repo_url or "https://github.com/setup-pending",
                "issues_created": issues_created,
                "workflows_created": workflows_created,
                "deployment": "Pending GitHub Actions",
                "branch_strategy": {
                    "main_branch": "main",
                    "development_branch": "develop",
                    "feature_branches": "feature/*"
                }
            }
            
            end_time = datetime.utcnow()
            duration_ms = int((end_time - start_time).total_seconds() * 1000)
            
            if event_callback:
                await event_callback({
                    "type": "agent_output",
                    "agent": "GitHubAgent",
                    "data": output_data,
                    "timestamp": end_time.isoformat()
                })
            
            if event_callback:
                await event_callback({
                    "type": "agent_complete",
                    "agent": "GitHubAgent",
                    "duration_ms": duration_ms,
                    "timestamp": end_time.isoformat()
                })
            
            logger.info("GitHub setup complete", duration_ms=duration_ms)
            return output_data
            
        except Exception as e:
            logger.error("GitHub recommendations failed", error=str(e))
            if event_callback:
                await event_callback({
                    "type": "error",
                    "agent": "GitHubAgent",
                    "error": str(e),
                    "details": "Failed to generate GitHub recommendations",
                    "timestamp": datetime.utcnow().isoformat()
                })
            
            return self._create_fallback_github(strategy_output, architecture_output, implementation_output, f"Error: {str(e)}")
    
    def _create_fallback_github(
        self, 
        strategy_output: Dict[str, Any] | str,
        architecture_output: Dict[str, Any] | str,
        implementation_output: Dict[str, Any],
        raw_output: str = ""
    ) -> Dict[str, Any]:
        """Create fallback GitHub recommendations"""
        return {
            "repository_name": "fallback-project",
            "repository_description": "A fallback project generation",
            "workflows": [
                {
                    "name": "ci",
                    "content": "name: CI\non: [push]\njobs:\n  build:\n    runs-on: ubuntu-latest\n    steps:\n    - uses: actions/checkout@v2\n"
                }
            ],
            "issues": [
                {"title": "Setup basic structure", "body": "Initialize backend and frontend."}
            ]
        }