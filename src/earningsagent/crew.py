import yaml
from crewai import Agent, Task, Crew
from src.earningsagent.tools import SerperDevTool, ScrapeWebsiteTool, WebsiteSearchTool, custom_tool

class EarningsCrew:
    def __init__(self):
        with open("src/earningsagent/config/agents.yaml") as f:
            self.agents_config = yaml.safe_load(f)
        with open("src/earningsagent/config/tasks.yaml") as f:
            self.tasks_config = yaml.safe_load(f)

        # Instantiate tools
        serper_dev_tool = SerperDevTool()
        scrape_website_tool = ScrapeWebsiteTool()
        website_search_tool = WebsiteSearchTool()

        # Create agents with tools connected where relevant
        self.earnings_fetch_agent = Agent(
            config=self.agents_config["earnings_fetch_agent"],
            tools=[serper_dev_tool, scrape_website_tool, custom_tool],
            llm=self.agents_config["earnings_fetch_agent"].get("llm")
        )
        self.financial_analysis_agent = Agent(
            config=self.agents_config["financial_analysis_agent"],
            tools=[website_search_tool],
            llm=self.agents_config["financial_analysis_agent"].get("llm")
        )
        self.summary_writer_agent = Agent(
            config=self.agents_config["summary_writer_agent"],
            llm=self.agents_config["summary_writer_agent"].get("llm")
        )
        self.qa_agent = Agent(
            config=self.agents_config["qa_agent"]
        )

        # Setup tasks and their contexts
        self.fetch_earnings_task = Task(
            config=self.tasks_config["fetch_earnings"],
            agent=self.earnings_fetch_agent
        )
        self.analyze_financials_task = Task(
            config=self.tasks_config["analyze_financials"],
            agent=self.financial_analysis_agent,
            context=[self.fetch_earnings_task]
        )
        self.summarize_report_task = Task(
            config=self.tasks_config["summarize_report"],
            agent=self.summary_writer_agent,
            context=[self.analyze_financials_task]
        )
        self.quality_check_task = Task(
            config=self.tasks_config["quality_check"],
            agent=self.qa_agent,
            context=[self.summarize_report_task]
        )

        # Build crew with agents and tasks
        self.crew = Crew(
            agents=[
                self.earnings_fetch_agent,
                self.financial_analysis_agent,
                self.summary_writer_agent,
                self.qa_agent
            ],
            tasks=[
                self.fetch_earnings_task,
                self.analyze_financials_task,
                self.summarize_report_task,
                self.quality_check_task
            ],
            verbose=True
        )

    def kickoff(self, input_data):
        """Starts crew execution given input data."""
        return self.crew.kickoff(input_data)
