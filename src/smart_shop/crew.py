from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List
from .tools.image_to_json_tool import ImageToJSONTool
from .tools.inventory_creator_tool import InventoryCreatorTool
import os
from dotenv import load_dotenv
from crewai.llm import LLM

# Load environment variables from .env file
load_dotenv()


@CrewBase
class SmartShop():
    """SmartShop crew"""

    agents: List[BaseAgent]
    tasks: List[Task]

    def __init__(self):
        """Initialize the crew and validate environment setup."""
        super().__init__()
        self._validate_environment()

    def _validate_environment(self):
        """Validate that required environment variables are set."""
        required_vars = ['GEMINI_API_KEY']
        missing_vars = []
        
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            raise ValueError(
                f"Missing required environment variables: {', '.join(missing_vars)}\n"
                f"Please set these variables in your .env file or environment.\n"
                f"See env_template.txt for reference."
            )

    def _get_llm(self):
        """Configure LLM to use Google's Gemini model."""
        return LLM(
            model="gemini/gemini-2.5-flash",
            api_key=os.getenv('GEMINI_API_KEY'),
            temperature=0.1
        )

    # Learn more about YAML configuration files here:
    # Agents: https://docs.crewai.com/concepts/agents#yaml-configuration-recommended
    # Tasks: https://docs.crewai.com/concepts/tasks#yaml-configuration-recommended
    
    # If you would like to add tools to your agents, you can learn more about it here:
    # https://docs.crewai.com/concepts/agents#agent-tools
    @agent
    def image_processor(self) -> Agent:
        return Agent(
            config=self.agents_config['image_processor'], # type: ignore[index]
            tools=[ImageToJSONTool()],
            llm=self._get_llm(),
            verbose=True
        )
    
    @agent
    def inventory_manager(self) -> Agent:
        return Agent(
            config=self.agents_config["inventory_manager"],  # type: ignore[index]
            tools=[InventoryCreatorTool()],
            llm=self._get_llm(),
            verbose=True,
        )

    # To learn more about structured task outputs,
    # task dependencies, and task callbacks, check out the documentation:
    # https://docs.crewai.com/concepts/tasks#overview-of-a-task
    @task
    def image_processing_task(self) -> Task:
        # Generate unique filename with timestamp
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_filename = f'image_analysis_{timestamp}.json'
        
        return Task(
            config=self.tasks_config['image_processing_task'], # type: ignore[index]
            agent=self.image_processor(),  # Explicitly assign to image_processor agent
            output_file=unique_filename
        )
    
    @task
    def inventory_managing_task(self) -> Task:
        # Generate unique filename with timestamp for inventory
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        inventory_filename = f'inventory_{timestamp}.json'
        
        return Task(
            config=self.tasks_config["inventory_managing_task"],  # type: ignore[index]
            agent=self.inventory_manager(),  # Explicitly assign to inventory_manager agent
            output_file=inventory_filename
        )

    @crew
    def crew(self) -> Crew:
        """Creates the SmartShop crew"""
        # To learn how to add knowledge sources to your crew, check out the documentation:
        # https://docs.crewai.com/concepts/knowledge#what-is-knowledge

        return Crew(
            agents=self.agents, # Automatically created by the @agent decorator
            tasks=self.tasks, # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=True,
        )
