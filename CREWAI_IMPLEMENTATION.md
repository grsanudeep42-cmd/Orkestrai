# OrkestrAI - CrewAI Implementation Guide

## CrewAI Agent Configurations

### 1. Product Strategy Agent Configuration

```python
# app/agents/strategy_agent.py
from crewai import Agent, Task
from app.agents.tools.idea_analyzer import IdeaAnalyzerTool
from app.agents.tools.feature_prioritizer import FeaturePrioritizerTool
from app.agents.tools.user_story_generator import UserStoryGeneratorTool

class ProductStrategyAgent:
    def __init__(self, llm):
        self.llm = llm
        
    def create_agent(self) -> Agent:
        return Agent(
            role="Product Strategy Manager",
            goal="Transform vague project ideas into structured product requirements with clear MVP scope",
            backstory="""You are a seasoned product strategist with 10+ years of experience 
            in building successful MVPs for hackathons and startups. You excel at identifying 
            core problems, defining target users, and prioritizing features for maximum impact 
            with minimal effort. You understand the constraints of hackathon timelines and 
            always focus on what can realistically be built in 36-48 hours.""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm,
            tools=[
                IdeaAnalyzerTool(),
                FeaturePrioritizerTool(),
                UserStoryGeneratorTool()
            ]
        )
    
    def create_task(self, agent: Agent, user_input: str) -> Task:
        return Task(
            description=f"""Analyze the following project idea and create a comprehensive 
            product strategy:
            
            USER INPUT: {user_input}
            
            Your analysis must include:
            1. Problem Statement: What problem does this solve?
            2. Target Users: Who will use this product?
            3. Core Value Proposition: Why would users choose this?
            4. MVP Features: List 5-8 features prioritized by impact/effort
            5. User Stories: Create detailed user stories for each feature
            6. Success Metrics: How will we measure success?
            7. Technical Constraints: Any specific requirements or limitations
            8. Hackathon Scope: What can realistically be built in 36-48 hours
            
            Output your analysis as structured JSON following this schema:
            {{
                "project_name": "string",
                "problem_statement": "string",
                "target_users": ["string"],
                "value_proposition": "string",
                "core_features": [
                    {{
                        "name": "string",
                        "priority": "high|medium|low",
                        "user_story": "As a [user], I want [feature] so that [benefit]",
                        "acceptance_criteria": ["string"],
                        "estimated_effort": "small|medium|large"
                    }}
                ],
                "success_metrics": ["string"],
                "technical_constraints": ["string"],
                "mvp_scope": ["string"],
                "out_of_scope": ["string"]
            }}
            """,
            expected_output="Structured JSON with complete product strategy",
            agent=agent
        )
```

### 2. Architecture Agent Configuration

```python
# app/agents/architecture_agent.py
from crewai import Agent, Task
from app.agents.tools.tech_stack_recommender import TechStackRecommenderTool
from app.agents.tools.schema_designer import SchemaDesignerTool
from app.agents.tools.api_planner import APIPlanner Tool

class ArchitectureAgent:
    def __init__(self, llm):
        self.llm = llm
        
    def create_agent(self) -> Agent:
        return Agent(
            role="Senior Software Architect",
            goal="Design scalable, production-ready system architecture optimized for rapid development",
            backstory="""You are a full-stack architect with expertise in modern web technologies, 
            microservices, and cloud-native applications. You specialize in designing systems that 
            can be built quickly but scale effectively. You understand the trade-offs between 
            different tech stacks and always recommend the best tools for the job. You have deep 
            knowledge of Next.js, FastAPI, PostgreSQL, and modern deployment platforms.""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm,
            tools=[
                TechStackRecommenderTool(),
                SchemaDesignerTool(),
                APIPlanner Tool()
            ]
        )
    
    def create_task(self, agent: Agent, strategy_output: dict) -> Task:
        return Task(
            description=f"""Based on the product strategy, design a complete system architecture:
            
            PRODUCT STRATEGY:
            {strategy_output}
            
            Your architecture design must include:
            1. Tech Stack Recommendation:
               - Frontend framework and libraries
               - Backend framework and tools
               - Database choice and rationale
               - Deployment platforms
               - Third-party services/APIs
            
            2. Database Schema:
               - Tables with fields and types
               - Relationships and foreign keys
               - Indexes for performance
               - Sample data structure
            
            3. API Design:
               - RESTful endpoints (method, path, purpose)
               - Request/response schemas
               - Authentication strategy
               - Error handling approach
            
            4. Frontend Architecture:
               - Page structure and routing
               - Component hierarchy
               - State management approach
               - Data fetching strategy
            
            5. System Diagram:
               - Generate Mermaid diagram showing:
                 * Frontend-Backend communication
                 * Database relationships
                 * External service integrations
                 * Data flow
            
            6. Deployment Strategy:
               - Hosting recommendations
               - CI/CD pipeline suggestions
               - Environment configuration
            
            Output as structured JSON following this schema:
            {{
                "tech_stack": {{
                    "frontend": ["Next.js 14", "Tailwind CSS", "Zustand"],
                    "backend": ["FastAPI", "SQLAlchemy", "Pydantic"],
                    "database": "PostgreSQL",
                    "deployment": {{"frontend": "Vercel", "backend": "Railway"}},
                    "third_party": ["IBM watsonx", "GitHub API"]
                }},
                "database_schema": {{
                    "tables": [
                        {{
                            "name": "users",
                            "fields": [
                                {{"name": "id", "type": "UUID", "constraints": "PRIMARY KEY"}},
                                {{"name": "email", "type": "VARCHAR(255)", "constraints": "UNIQUE NOT NULL"}}
                            ],
                            "relationships": [],
                            "indexes": ["email"]
                        }}
                    ]
                }},
                "api_endpoints": [
                    {{
                        "method": "POST",
                        "path": "/api/v1/projects",
                        "description": "Create new project",
                        "request_body": {{}},
                        "response": {{}},
                        "authentication": "required"
                    }}
                ],
                "frontend_structure": {{
                    "pages": ["/", "/dashboard", "/project/[id]"],
                    "components": ["Header", "ProjectCard", "AgentPanel"],
                    "state_management": "Zustand",
                    "styling": "Tailwind CSS"
                }},
                "system_diagram": "mermaid diagram code",
                "deployment": {{
                    "frontend": {{"platform": "Vercel", "build_command": "npm run build"}},
                    "backend": {{"platform": "Railway", "dockerfile": true}}
                }}
            }}
            """,
            expected_output="Complete system architecture as structured JSON",
            agent=agent
        )
```

### 3. Code Builder Agent Configuration

```python
# app/agents/code_builder_agent.py
from crewai import Agent, Task
from app.agents.tools.code_generator import CodeGeneratorTool
from app.agents.tools.boilerplate_creator import BoilerplateCreatorTool

class CodeBuilderAgent:
    def __init__(self, llm):
        self.llm = llm
        
    def create_agent(self) -> Agent:
        return Agent(
            role="Senior Full-Stack Developer",
            goal="Generate production-quality, well-structured starter code that follows best practices",
            backstory="""You are an expert full-stack developer with mastery in Next.js, 
            FastAPI, and modern web development. You write clean, maintainable code that 
            follows industry best practices. You understand project structure, separation of 
            concerns, and how to create scalable codebases. You always include proper error 
            handling, type hints, and documentation. You can generate complete project 
            scaffolding with all necessary configuration files.""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm,
            tools=[
                CodeGeneratorTool(),
                BoilerplateCreatorTool()
            ]
        )
    
    def create_task(self, agent: Agent, architecture_output: dict) -> Task:
        return Task(
            description=f"""Generate complete starter code based on the architecture design:
            
            ARCHITECTURE:
            {architecture_output}
            
            Generate the following:
            
            1. Backend Code (FastAPI):
               - Main application file with FastAPI setup
               - Database models (SQLAlchemy)
               - API routes and endpoints
               - Pydantic schemas for validation
               - Configuration management
               - CORS middleware setup
               - Basic error handling
               - Requirements.txt with all dependencies
            
            2. Frontend Code (Next.js):
               - App router structure
               - Main pages (landing, dashboard, project view)
               - Reusable UI components
               - API client setup
               - State management (Zustand stores)
               - Tailwind configuration
               - Package.json with dependencies
            
            3. Configuration Files:
               - .env.example for both frontend and backend
               - Docker files (if needed)
               - README.md with setup instructions
               - .gitignore files
            
            4. Database Setup:
               - Alembic migration files
               - Initial schema creation
               - Seed data (optional)
            
            For each file, provide:
            - Full file path
            - Complete file content (no placeholders)
            - Brief description of purpose
            
            Output as structured JSON:
            {{
                "generated_files": [
                    {{
                        "path": "backend/app/main.py",
                        "content": "complete file content here",
                        "language": "python",
                        "description": "FastAPI application entry point"
                    }}
                ],
                "setup_instructions": [
                    "1. Install Python 3.11+",
                    "2. Run pip install -r requirements.txt",
                    "3. Setup .env file with credentials"
                ],
                "dependencies": {{
                    "frontend": ["next@14.1.0", "react@18.2.0"],
                    "backend": ["fastapi==0.109.0", "sqlalchemy==2.0.25"]
                }},
                "folder_structure": "visual representation of project structure"
            }}
            """,
            expected_output="Complete codebase with all files as structured JSON",
            agent=agent
        )
```

### 4. GitHub Management Agent Configuration

```python
# app/agents/github_agent.py
from crewai import Agent, Task
from app.agents.tools.github_client import GitHubClientTool

class GitHubManagementAgent:
    def __init__(self, llm):
        self.llm = llm
        
    def create_agent(self) -> Agent:
        return Agent(
            role="DevOps & Project Manager",
            goal="Automate GitHub workflow setup and create organized project management structure",
            backstory="""You are an experienced DevOps engineer and Agile coach who specializes 
            in developer productivity. You understand how to structure GitHub repositories for 
            maximum efficiency, create meaningful issues, and organize sprints. You know how to 
            write clear issue descriptions, acceptance criteria, and commit message conventions. 
            You excel at breaking down features into manageable tasks.""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm,
            tools=[GitHubClientTool()]
        )
    
    def create_task(self, agent: Agent, strategy_output: dict, code_output: dict) -> Task:
        return Task(
            description=f"""Create a complete GitHub project management structure:
            
            PRODUCT STRATEGY:
            {strategy_output}
            
            CODE STRUCTURE:
            {code_output}
            
            Create the following GitHub artifacts:
            
            1. Repository Setup:
               - Repository name and description
               - Topics/tags for discoverability
               - README.md structure
               - License recommendation
            
            2. Issues:
               - Create issues for each feature from product strategy
               - Include clear descriptions and acceptance criteria
               - Add appropriate labels (feature, bug, enhancement, etc.)
               - Assign to milestones
               - Estimate effort (story points or time)
            
            3. Milestones:
               - Sprint 1: Core functionality
               - Sprint 2: Polish and deployment
               - Include due dates and descriptions
            
            4. Project Board:
               - Columns: Backlog, In Progress, Review, Done
               - Organize issues into columns
               - Priority ordering
            
            5. Templates:
               - Issue template
               - Pull request template
               - Contributing guidelines
            
            6. Commit Convention:
               - Suggest commit message format
               - Branch naming strategy
            
            Output as structured JSON:
            {{
                "repository": {{
                    "name": "project-name",
                    "description": "Brief description",
                    "topics": ["hackathon", "ai", "nextjs"],
                    "private": false,
                    "license": "MIT"
                }},
                "issues": [
                    {{
                        "title": "Implement user authentication",
                        "body": "Detailed description with acceptance criteria",
                        "labels": ["feature", "backend", "high-priority"],
                        "milestone": "Sprint 1",
                        "assignees": [],
                        "estimate": "5 story points"
                    }}
                ],
                "milestones": [
                    {{
                        "title": "Sprint 1 - Core Features",
                        "description": "Build essential functionality",
                        "due_date": "2026-05-17",
                        "issues": ["issue-1", "issue-2"]
                    }}
                ],
                "project_board": {{
                    "name": "Development Board",
                    "columns": ["Backlog", "In Progress", "Review", "Done"],
                    "cards": [
                        {{"column": "Backlog", "issue": "issue-1"}}
                    ]
                }},
                "templates": {{
                    "issue": "issue template content",
                    "pull_request": "PR template content"
                }},
                "commit_convention": {{
                    "format": "type(scope): description",
                    "types": ["feat", "fix", "docs", "style", "refactor"],
                    "branch_naming": "type/short-description"
                }}
            }}
            """,
            expected_output="Complete GitHub project structure as JSON",
            agent=agent
        )
```

### 5. Pitch & Demo Agent Configuration

```python
# app/agents/pitch_agent.py
from crewai import Agent, Task
from app.agents.tools.pitch_generator import PitchGeneratorTool
from app.agents.tools.demo_scripter import DemoScripterTool

class PitchAgent:
    def __init__(self, llm):
        self.llm = llm
        
    def create_agent(self) -> Agent:
        return Agent(
            role="Presentation Coach & Marketing Strategist",
            goal="Create compelling pitch materials that win hackathons and impress judges",
            backstory="""You are a former startup founder who has won multiple pitch competitions 
            and hackathons. You understand what judges look for: technical innovation, business 
            impact, presentation quality, and team execution. You know how to craft narratives 
            that resonate, highlight key achievements, and create memorable demos. You excel at 
            distilling complex technical projects into clear, compelling stories.""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm,
            tools=[
                PitchGeneratorTool(),
                DemoScripterTool()
            ]
        )
    
    def create_task(self, agent: Agent, all_outputs: dict) -> Task:
        return Task(
            description=f"""Create comprehensive pitch and demo materials:
            
            PROJECT CONTEXT:
            {all_outputs}
            
            Create the following materials:
            
            1. Elevator Pitch (30 seconds):
               - Hook that grabs attention
               - Problem statement
               - Solution overview
               - Unique value proposition
            
            2. Demo Script (3-5 minutes):
               - Timed segments with talking points
               - What to show on screen
               - Key features to highlight
               - Transition phrases
               - Backup plan if demo fails
            
            3. Judge Talking Points:
               - Technical Innovation: What's technically impressive?
               - Business Impact: Who benefits and how?
               - Scalability: How can this grow?
               - Execution: What did you accomplish?
            
            4. Slide Deck Outline:
               - Slide-by-slide structure
               - Key points for each slide
               - Visual suggestions
            
            5. README Content:
               - Project overview
               - Features list
               - Tech stack
               - Setup instructions
               - Screenshots/demo links
               - Team information
            
            6. Social Media Posts:
               - Twitter/X announcement
               - LinkedIn post
               - Hackathon submission description
            
            Output as structured JSON:
            {{
                "elevator_pitch": "30-second pitch text",
                "demo_script": [
                    {{
                        "timestamp": "0:00-0:30",
                        "action": "Show landing page",
                        "talking_points": [
                            "Introduce the problem",
                            "Show the solution"
                        ],
                        "screen": "Landing page with hero section"
                    }}
                ],
                "judge_talking_points": {{
                    "technical_innovation": [
                        "Multi-agent AI orchestration using CrewAI",
                        "Real-time WebSocket visualization"
                    ],
                    "business_impact": [
                        "Reduces hackathon planning from 8 hours to 5 minutes",
                        "Makes hackathons accessible to non-technical founders"
                    ],
                    "scalability": [
                        "Can expand to enterprise project planning",
                        "Marketplace for custom agents"
                    ],
                    "execution": [
                        "Built complete full-stack application in 36 hours",
                        "5 AI agents working in harmony"
                    ]
                }},
                "slide_outline": [
                    {{
                        "slide_number": 1,
                        "title": "The Problem",
                        "content": ["Bullet points"],
                        "visual": "Image suggestion"
                    }}
                ],
                "readme_content": "Complete README.md content",
                "social_media": {{
                    "twitter": "Tweet text with hashtags",
                    "linkedin": "LinkedIn post",
                    "hackathon_submission": "Submission description"
                }}
            }}
            """,
            expected_output="Complete pitch and demo materials as JSON",
            agent=agent
        )
```

## Agent Tools Implementation

### 1. Idea Analyzer Tool

```python
# app/agents/tools/idea_analyzer.py
from crewai_tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field

class IdeaAnalyzerInput(BaseModel):
    """Input for IdeaAnalyzerTool"""
    user_input: str = Field(..., description="The user's project idea description")

class IdeaAnalyzerTool(BaseTool):
    name: str = "Idea Analyzer"
    description: str = "Analyzes project ideas to extract key concepts, problems, and opportunities"
    args_schema: Type[BaseModel] = IdeaAnalyzerInput
    
    def _run(self, user_input: str) -> dict:
        """
        Analyze the user's idea and extract structured information
        """
        # Use LLM to analyze the idea
        analysis_prompt = f"""
        Analyze this project idea and extract:
        1. Core problem being solved
        2. Target audience
        3. Key features mentioned
        4. Technical requirements implied
        5. Potential challenges
        
        Idea: {user_input}
        
        Return as JSON.
        """
        
        # Call LLM and parse response
        # Implementation depends on your LLM setup
        return {
            "problem": "extracted problem",
            "audience": ["user type 1", "user type 2"],
            "features": ["feature 1", "feature 2"],
            "tech_requirements": ["requirement 1"],
            "challenges": ["challenge 1"]
        }
```

### 2. Tech Stack Recommender Tool

```python
# app/agents/tools/tech_stack_recommender.py
from crewai_tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field

class TechStackInput(BaseModel):
    """Input for TechStackRecommenderTool"""
    features: list = Field(..., description="List of required features")
    constraints: list = Field(default=[], description="Technical constraints")

class TechStackRecommenderTool(BaseTool):
    name: str = "Tech Stack Recommender"
    description: str = "Recommends optimal technology stack based on project requirements"
    args_schema: Type[BaseModel] = TechStackInput
    
    def _run(self, features: list, constraints: list = []) -> dict:
        """
        Recommend tech stack based on features and constraints
        """
        # Logic to recommend tech stack
        # Can use rules-based system or LLM
        
        recommendations = {
            "frontend": {
                "framework": "Next.js 14",
                "reasoning": "Server-side rendering, great DX, fast deployment",
                "alternatives": ["React + Vite", "SvelteKit"]
            },
            "backend": {
                "framework": "FastAPI",
                "reasoning": "Fast, async, great for AI/ML integration",
                "alternatives": ["Express.js", "Django"]
            },
            "database": {
                "choice": "PostgreSQL",
                "reasoning": "Reliable, scalable, great for structured data",
                "alternatives": ["MongoDB", "Supabase"]
            }
        }
        
        return recommendations
```

### 3. Code Generator Tool

```python
# app/agents/tools/code_generator.py
from crewai_tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
import os

class CodeGeneratorInput(BaseModel):
    """Input for CodeGeneratorTool"""
    file_type: str = Field(..., description="Type of file to generate (api, model, component, etc.)")
    specifications: dict = Field(..., description="Specifications for the code")

class CodeGeneratorTool(BaseTool):
    name: str = "Code Generator"
    description: str = "Generates code files based on specifications and templates"
    args_schema: Type[BaseModel] = CodeGeneratorInput
    
    def _run(self, file_type: str, specifications: dict) -> str:
        """
        Generate code based on file type and specifications
        """
        templates = {
            "fastapi_route": self._generate_fastapi_route,
            "sqlalchemy_model": self._generate_sqlalchemy_model,
            "nextjs_page": self._generate_nextjs_page,
            "react_component": self._generate_react_component
        }
        
        generator = templates.get(file_type)
        if generator:
            return generator(specifications)
        else:
            return f"# Template for {file_type} not found"
    
    def _generate_fastapi_route(self, specs: dict) -> str:
        """Generate FastAPI route code"""
        return f"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.{specs['resource']} import {specs['resource'].title()}Create, {specs['resource'].title()}Response

router = APIRouter()

@router.post("/{specs['path']}", response_model={specs['resource'].title()}Response)
async def create_{specs['resource']}(
    {specs['resource']}: {specs['resource'].title()}Create,
    db: Session = Depends(get_db)
):
    # Implementation here
    pass

@router.get("/{specs['path']}/{{id}}", response_model={specs['resource'].title()}Response)
async def get_{specs['resource']}(
    id: str,
    db: Session = Depends(get_db)
):
    # Implementation here
    pass
"""
    
    def _generate_sqlalchemy_model(self, specs: dict) -> str:
        """Generate SQLAlchemy model code"""
        fields = "\n    ".join([
            f"{field['name']} = Column({field['type']}, {field.get('constraints', '')})"
            for field in specs['fields']
        ])
        
        return f"""
from sqlalchemy import Column, String, DateTime
from sqlalchemy.dialects.postgresql import UUID
from app.db.base import Base
import uuid
from datetime import datetime

class {specs['name']}(Base):
    __tablename__ = "{specs['table_name']}"
    
    {fields}
"""
```

## Orchestrator Implementation

```python
# app/agents/orchestrator.py
from crewai import Crew, Process
from app.agents.strategy_agent import ProductStrategyAgent
from app.agents.architecture_agent import ArchitectureAgent
from app.agents.code_builder_agent import CodeBuilderAgent
from app.agents.github_agent import GitHubManagementAgent
from app.agents.pitch_agent import PitchAgent
from app.core.events import EventEmitter
import asyncio

class OrkestrAICrew:
    def __init__(self, watsonx_llm):
        self.llm = watsonx_llm
        self.event_emitter = EventEmitter()
        
        # Initialize agents
        self.strategy_agent_class = ProductStrategyAgent(self.llm)
        self.architecture_agent_class = ArchitectureAgent(self.llm)
        self.code_builder_agent_class = CodeBuilderAgent(self.llm)
        self.github_agent_class = GitHubManagementAgent(self.llm)
        self.pitch_agent_class = PitchAgent(self.llm)
    
    async def run_orchestration(
        self,
        user_input: str,
        project_id: str,
        preferences: dict = None,
        event_callback = None
    ) -> dict:
        """
        Run the complete multi-agent orchestration
        """
        try:
            # Create agents
            strategy_agent = self.strategy_agent_class.create_agent()
            architecture_agent = self.architecture_agent_class.create_agent()
            code_builder_agent = self.code_builder_agent_class.create_agent()
            github_agent = self.github_agent_class.create_agent()
            pitch_agent = self.pitch_agent_class.create_agent()
            
            # Create tasks
            strategy_task = self.strategy_agent_class.create_task(strategy_agent, user_input)
            
            # Create crew
            crew = Crew(
                agents=[
                    strategy_agent,
                    architecture_agent,
                    code_builder_agent,
                    github_agent,
                    pitch_agent
                ],
                tasks=[],  # Tasks will be added dynamically
                process=Process.sequential,
                verbose=True,
                memory=True,
                embedder={
                    "provider": "ibm-watsonx",
                    "config": {
                        "model": "ibm/granite-embedding-125m"
                    }
                }
            )
            
            # Execute strategy agent
            await self._emit_event(event_callback, {
                "type": "agent_start",
                "agent": "ProductStrategyAgent",
                "project_id": project_id
            })
            
            strategy_output = await self._execute_task(strategy_task, event_callback, project_id)
            
            # Execute architecture agent
            architecture_task = self.architecture_agent_class.create_task(
                architecture_agent,
                strategy_output
            )
            architecture_output = await self._execute_task(architecture_task, event_callback, project_id)
            
            # Execute code builder agent
            code_task = self.code_builder_agent_class.create_task(
                code_builder_agent,
                architecture_output
            )
            code_output = await self._execute_task(code_task, event_callback, project_id)
            
            # Execute GitHub agent
            github_task = self.github_agent_class.create_task(
                github_agent,
                strategy_output,
                code_output
            )
            github_output = await self._execute_task(github_task, event_callback, project_id)
            
            # Execute pitch agent
            all_outputs = {
                "strategy": strategy_output,
                "architecture": architecture_output,
                "code": code_output,
                "github": github_output
            }
            pitch_task = self.pitch_agent_class.create_task(pitch_agent, all_outputs)
            pitch_output = await self._execute_task(pitch_task, event_callback, project_id)
            
            # Return all outputs
            return {
                "strategy": strategy_output,
                "architecture": architecture_output,
                "code": code_output,
                "github": github_output,
                "pitch": pitch_output
            }
            
        except Exception as e:
            await self._emit_event(event_callback, {
                "type": "error",
                "error": str(e),
                "project_id": project_id
            })
            raise
    
    async def _execute_task(self, task, event_callback, project_id):
        """Execute a single task with event emission"""
        agent_name = task.agent.role
        
        await self._emit_event(event_callback, {
            "type": "agent_thinking",
            "agent": agent_name,
            "message": f"Processing {task.description[:50]}...",
            "project_id": project_id
        })
        
        # Execute task
        result = task.execute()
        
        await self._emit_event(event_callback, {
            "type": "agent_output",
            "agent": agent_name,
            "data": result,
            "project_id": project_id
        })
        
        await self._emit_event(event_callback, {
            "type": "agent_complete",
            "agent": agent_name,
            "project_id": project_id
        })
        
        return result
    
    async def _emit_event(self, callback, event):
        """Emit event to callback if provided"""
        if callback:
            await callback(event)
```

## IBM watsonx Integration

```python
# app/core/watsonx_client.py
from ibm_watsonx_ai import Credentials
from ibm_watsonx_ai.foundation_models import ModelInference
from app.config import settings

class WatsonxLLM:
    def __init__(self):
        self.credentials = Credentials(
            url=settings.WATSONX_URL,
            api_key=settings.WATSONX_API_KEY
        )
        
        self.model = ModelInference(
            model_id="ibm/granite-13b-chat-v2",
            credentials=self.credentials,
            project_id=settings.WATSONX_PROJECT_ID,
            params={
                "decoding_method": "greedy",
                "max_new_tokens": 2000,
                "temperature": 0.7,
                "top_p": 0.9
            }
        )
    
    def generate(self, prompt: str) -> str:
        """Generate text using watsonx"""
        response = self.model.generate_text(prompt=prompt)
        return response
    
    def generate_stream(self, prompt: str):
        """Stream generation for real-time updates"""
        for chunk in self.model.generate_text_stream(prompt=prompt):
            yield chunk
```

## Event System for Real-time Updates

```python
# app/core/events.py
from typing import Callable, Dict, List
import asyncio

class EventEmitter:
    def __init__(self):
        self.listeners: Dict[str, List[Callable]] = {}
    
    def on(self, event_type: str, callback: Callable):
        """Register event listener"""
        if event_type not in self.listeners:
            self.listeners[event_type] = []
        self.listeners[event_type].append(callback)
    
    async def emit(self, event_type: str, data: dict):
        """Emit event to all listeners"""
        if event_type in self.listeners:
            for callback in self.listeners[event_type]:
                if asyncio.iscoroutinefunction(callback):
                    await callback(data)
                else:
                    callback(data)