# crew.py (Modification Suggestions)
from pydantic import BaseModel, Field
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List, Optional
from crewai_tools import MCPServerAdapter
import logging

# Set up logging
logger = logging.getLogger(__name__)

class TaskOutput(BaseModel):
    """Task output model"""
    project_key: str = Field(..., description="Unique project identifier")
    summary: str = Field(..., description="Task summary")
    issue_type: str = Field(..., description="Issue type")
    description: str = Field(..., description="Detailed description")
    priority: str = Field(..., description="Priority level")

class TaskList(BaseModel):
    """Task list model"""
    tasks: List[TaskOutput] = Field(..., description="List of tasks")

@CrewBase
class AiAgents:
    """AI agent team responsible for project management and system design"""

    def __init__(self):
        """Initialize MCP tools"""
        self.mcp_server_params = {"url": "http://localhost:9000/sse"}
        self.mcp_adapter: Optional[MCPServerAdapter] = None
        self.mcp_tools = []
        self._initialize_mcp_tools()

    def _initialize_mcp_tools(self):
        """Initialize MCP tool connection"""
        try:
            self.mcp_adapter = MCPServerAdapter(
                self.mcp_server_params, 
                connect_timeout=60
            )
            self.mcp_tools = self.mcp_adapter.__enter__()
            logger.info(f"Available tools: {[tool.name for tool in self.mcp_tools]}")
        except Exception as e:
            logger.error(f"MCP tool initialization failed: {e}")
            self.mcp_tools = []

    def __del__(self):
        """Clean up MCP resources"""
        if self.mcp_adapter:
            try:
                self.mcp_adapter.__exit__(None, None, None)
            except Exception as e:
                logger.error(f"MCP resource cleanup failed: {e}")

    @agent
    def project_manager(self) -> Agent:
        return Agent(
            config=self.agents_config['project_manager'],
            verbose=True
        )

    @agent
    def system_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config['system_analyst'],
            verbose=True
        )

    @agent
    def architect(self) -> Agent:
        return Agent(
            config=self.agents_config['architect'],
            verbose=True
        )

    @agent
    def fullstack_engineer(self) -> Agent:
        return Agent(
            config=self.agents_config['fullstack_engineer'],
            verbose=True
        )

    @task
    def requirements_analysis(self) -> Task:
        return Task(
            config=self.tasks_config['requirements_analysis'],
        )

    @task
    def requirements_specification(self) -> Task:
        return Task(
            config=self.tasks_config['requirements_specification'],
        )

    @task
    def system_design(self) -> Task:
        return Task(
            config=self.tasks_config['system_design'],
        )

    @task
    def project_task_planning(self) -> Task:
        return Task(
            config=self.tasks_config['project_task_planning'],
            output_json=TaskList  # Using a more appropriate name
        )

    @task
    def jira_task_creation(self) -> Task:
        # Add tool availability check
        tools = self.mcp_tools if self.mcp_tools else []
        if not tools:
            logger.warning("MCP tools unavailable, JIRA task creation may be limited")
            
        return Task(
            config=self.tasks_config['jira_task_creation'],
            tools=tools
        )

    @task
    def write_code(self) -> Task:
        return Task(
            config=self.tasks_config['write_code'],
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,  # CrewBase will handle these automatically
            tasks=self.tasks,    # CrewBase will handle these automatically
            process=Process.sequential,
            verbose=True,
        )