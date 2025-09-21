from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List
from .tools.image_to_json_tool import ImageToJSONTool
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# If you want to run a snippet of code before or after the crew starts,
# you can use the @before_kickoff and @after_kickoff decorators
# https://docs.crewai.com/concepts/crews#example-crew-class-with-decorators


@CrewBase
class SmartShop:
    """SmartShop crew"""

    agents: List[BaseAgent]
    tasks: List[Task]

    def __init__(self):
        """Initialize the crew and validate environment setup."""
        super().__init__()
        self._validate_environment()

    def _validate_environment(self):
        """Validate that required environment variables are set."""
        required_vars = ['GOOGLE_AI_API_KEY']
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

    # Learn more about YAML configuration files here:
    # Agents: https://docs.crewai.com/concepts/agents#yaml-configuration-recommended
    # Tasks: https://docs.crewai.com/concepts/tasks#yaml-configuration-recommended

    # If you would like to add tools to your agents, you can learn more about it here:
    # https://docs.crewai.com/concepts/agents#agent-tools
    @agent
    def image_to_json_convertor(self) -> Agent:
        return Agent(
            config=self.agents_config["image_to_json_convertor"],  # type: ignore[index]
            verbose=True,
        )

    @agent
    def inventory_manager(self) -> Agent:
        return Agent(
            config=self.agents_config["inventory_manager"],  # type: ignore[index]
            verbose=True,
        )

    @agent
    def snapshot_manager(self) -> Agent:
        return Agent(
            config=self.agents_config["snapshot_manager"],  # type: ignore[index]
            verbose=True,
        )

    @agent
    def shopping_recommender(self) -> Agent:
        return Agent(
            config=self.agents_config["shopping_recommender"],  # type: ignore[index]
            verbose=True,
        )

    @agent
    def image_processor(self) -> Agent:
        return Agent(
            config=self.agents_config['image_processor'], # type: ignore[index]
            tools=[ImageToJSONTool()],
            verbose=True
        )

    # To learn more about structured task outputs,
    # task dependencies, and task callbacks, check out the documentation:
    # https://docs.crewai.com/concepts/tasks#overview-of-a-task
    @task
    def image_to_json_task(self) -> Task:
        return Task(
            config=self.tasks_config["image_to_json_task"],  # type: ignore[index]
            output_file="latest_purchases.json",
        )

    @task
    def inventory_managing_task(self) -> Task:
        return Task(
            config=self.tasks_config["inventory_managing_task"],  # type: ignore[index]
            output_file="inventory.json",
        )

    @task
    def snapshot_managering_task(self) -> Task:
        return Task(
            config=self.tasks_config["snapshot_managering_task"],  # type: ignore[index]
            output_file="inventory_snapshot.json",
        )

    @task
    def shopping_recommendation_task(self) -> Task:
        return Task(
            config=self.tasks_config["shopping_recommendation_task"],  # type: ignore[index]
            output_file="shopping_recommendation.json",
        )

    @task
    def image_processing_task(self) -> Task:
        return Task(
            config=self.tasks_config['image_processing_task'], # type: ignore[index]
            output_file='image_analysis.json'
        )

    @crew
    def crew(self) -> Crew:
        """Creates the SmartShop crew"""
        # To learn how to add knowledge sources to your crew, check out the documentation:
        # https://docs.crewai.com/concepts/knowledge#what-is-knowledge

        return Crew(
            agents=self.agents,  # Automatically created by the @agent decorator
            tasks=self.tasks,  # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=True,
            # process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com /how-to/Hierarchical/
        )
