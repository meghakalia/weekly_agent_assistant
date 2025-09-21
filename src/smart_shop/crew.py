from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List

# If you want to run a snippet of code before or after the crew starts,
# you can use the @before_kickoff and @after_kickoff decorators
# https://docs.crewai.com/concepts/crews#example-crew-class-with-decorators


@CrewBase
class SmartShop:
    """SmartShop crew"""

    agents: List[BaseAgent]
    tasks: List[Task]

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
