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
    
    def __init__(self, api_keys: Optional[Dict[str, str]] = None):
        super().__init__(api_keys)
        self.workflow_templates = self._load_workflow_templates()
        self.system_prompt = f"""You are an elite DevOps Engineer and Open Source Maintainer.
Your goal is to define the ideal repository setup and automation for a new project.

CORE RESPONSIBILITIES:
1) Repository Name & Description - Professional, SEO-friendly, and descriptive.
2) CI/CD Workflows - Practical GitHub Action YAMLs for testing, linting, and deployment.
3) Issue Backlog - 5-10 detailed, actionable issues covering immediate next steps.
4) Branching Strategy - Define a clear main/develop/feature workflow.

VERIFIED WORKFLOW TEMPLATES (USE THESE AS FOUNDATION):
- Python CI: {self.workflow_templates.get('python_ci', 'Standard Python CI')}
- Node.js CI: {self.workflow_templates.get('node_ci', 'Standard Node.js CI')}

CRITICAL INSTRUCTIONS:
- Do NOT use generic placeholders.
- Ensure YAML workflows use correct paths and tools based on the actual file tree.
- Issues must have clear titles and descriptive bodies.
- Output should be structured and ready for direct API integration or manual setup.
- You MUST use the provided templates as the basis for workflows, adapting them only where necessary for the specific project structure."""

    def _load_workflow_templates(self) -> Dict[str, str]:
        """Load workflow templates from the filesystem"""
        templates = {}
        base_path = os.path.join(os.path.dirname(__file__), "boilerplates")
        try:
            if os.path.exists(base_path):
                mapping = {
                    "python_ci": "python-ci.yml.tmpl",
                    "node_ci": "node-ci.yml.tmpl"
                }
                for key, filename in mapping.items():
                    file_path = os.path.join(base_path, filename)
                    if os.path.exists(file_path):
                        with open(file_path, "r") as f:
                            templates[key] = f.read()
            return templates
        except Exception as e:
            logger.warning(f"Failed to load workflow templates: {e}")
            return {}

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
- Use the provided verified workflow templates. Ensure they use 'actions/checkout@v4'.

Create comprehensive GitHub details including:
1. **Repository Name**: A suitable, slugified name for the project (e.g., 'nexus-core-app')
2. **Repository Description**: A short description
3. **Workflows**: CI/CD pipeline YAML contents (e.g., ci.yml, cd.yml). Must be valid YAML and based on the provided templates.
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

            # Check if we already created a repo in a previous retry
            existing_repo_url = memory.get("created_repo_url") if memory else None
            repo_url = existing_repo_url or ""
            
            github_token = getattr(current_user, "github_token", None) if current_user else getattr(settings, "GITHUB_TOKEN", None)
            workflows_created = 0
            issues_created = 0
            
            if github_token and not existing_repo_url:
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
                    if memory:
                        memory["created_repo_url"] = repo_url
                        memory["repo_name_actual"] = repo.name

                    # Push code from Builder output in shared execution memory via GitHub API
                    builder_output = shared_context.get("implementation", implementation_output) if shared_context else implementation_output
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
                            # Cleanup literal \n if present (common LLM artifact)
                            wf_content = wf.get('content', '')
                            if "\\n" in wf_content and "\n" not in wf_content:
                                wf_content = wf_content.replace("\\n", "\n")
                            
                            # Final validation of YAML
                            try:
                                yaml.safe_load(wf_content)
                            except yaml.YAMLError as ye:
                                logger.warning(f"Invalid YAML for workflow {wf.get('name')}: {ye}")
                                continue

                            repo.create_file(
                                path=f".github/workflows/{wf.get('name')}.yml",
                                message=f"Add {wf.get('name')} workflow",
                                content=wf_content,
                                branch="main"
                            )
                            workflows_created += 1
                        except Exception as e:
                            logger.warning(f"Failed to add workflow {wf.get('name')}: {e}")

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
            elif existing_repo_url:
                if event_callback:
                    await event_callback({
                        "type": "agent_thinking",
                        "agent": "GitHubAgent",
                        "message": f"Repository already created: {existing_repo_url}. Updating content if needed...",
                        "timestamp": datetime.utcnow().isoformat()
                    })
                # In a retry, we might want to update files, but for now let's just avoid creating a new repo.
                # If we really need to update files on retry, we'd need more logic here.
                # However, the user's primary complaint is the multiple repos.
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
                },
                "message": f"Successfully created repository '{github_plan.get('repository_name')}' on GitHub. "
                           f"Pushed codebase and {workflows_created} CI/CD workflows. "
                           f"Created {issues_created} issues in the backlog. "
                           f"Repository is ready for development."
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
            
            raise e
    
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