from agents.base_agent import BaseAgent
from config import ZMQ_PUBSUB_PORT, AGENT_PORTS
from langchain import PromptTemplate, LLMChain
from langchain.llms import OpenAI

class ReportGenerationAgent(BaseAgent):
    def __init__(self):
        super().__init__("report_generation", ZMQ_PUBSUB_PORT, ["generate_report"], AGENT_PORTS["report_generation"])
        self.llm = OpenAI(temperature=0.7)

    def process_message(self, message):
        if message.action == "generate_report":
            report = self.generate_report(message.data)
            self.send_message("reporting", "save_report", {"report": report})

    def generate_report(self, data):
        template = """
        Generate a comprehensive security report based on the following data:

        Metrics:
        {metrics}

        Detected Risks:
        {risks}

        The report should include:
        1. Executive Summary
        2. Detailed Metrics Analysis
        3. Risk Assessment
        4. Recommendations
        5. Conclusion

        Format the report in Markdown.
        """
        prompt = PromptTemplate(template=template, input_variables=["metrics", "risks"])
        llm_chain = LLMChain(prompt=prompt, llm=self.llm)
        
        report = llm_chain.run(data)
        return report