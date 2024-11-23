from agents.base_agent import BaseAgent
from config import OPENAI_API_KEY, ZMQ_PUBSUB_PORT, AGENT_PORTS
from langchain import PromptTemplate, LLMChain
from langchain.llms import OpenAI

class AnalysisAgent(BaseAgent):
    def __init__(self):
        super().__init__("analysis", ZMQ_PUBSUB_PORT, ["analyze_metrics", "update_knowledge", "update_vulnerability_knowledge", "pentest_results"], AGENT_PORTS["analysis"])
        self.llm = OpenAI(api_key=OPENAI_API_KEY, temperature=0.7)
        self.knowledge_base = ""
        self.vulnerability_knowledge = []
        self.pentest_results = []

    def process_message(self, message):
        if message.action == "analyze_metrics":
            risks, reasoning = self.analyze_risks(message.data)
            self.send_message("notification", "notify_risks", risks)
            self.send_message("reporting", "log_risks", risks)
            # Suggest actions based on reasoning
            actions = self.suggest_actions(reasoning)
            self.send_message("notification", "suggest_actions", actions)
        elif message.action == "update_knowledge":
            self.update_knowledge_base(message.data["docs"])
        elif message.action == "update_vulnerability_knowledge":
            self.update_vulnerability_knowledge(message.data["results"])
        elif message.action == "pentest_results":
            self.update_pentest_results(message.data["results"])
            self.compare_kri_and_pentest()

    def analyze_risks(self, metrics):
        template = """
        Given the following web service metrics, security knowledge, and known vulnerabilities:

        Metrics:
        {metrics}

        Security Knowledge:
        {knowledge_base}

        Known Vulnerabilities:
        {vulnerabilities}

        Analyze the metrics step-by-step and identify potential risks. For each risk, provide:
        1. Risk name
        2. Severity (Low, Medium, High)
        3. Description
        4. Recommended mitigation steps
        5. Reasoning behind the analysis

        Format the output as a JSON list of risk objects with their reasoning.
        """
        
        prompt = PromptTemplate(template=template, input_variables=["metrics", "knowledge_base", "vulnerabilities"])
        llm_chain = LLMChain(prompt=prompt, llm=self.llm)

        vulnerabilities_str = "\n".join([f"{v['cve_id']}: {v['description']}" for v in self.vulnerability_knowledge])
        
        # Analyze risks and get reasoning
        response_json = llm_chain.run({"metrics": metrics, "knowledge_base": self.knowledge_base, "vulnerabilities": vulnerabilities_str})
        
        # Parse response into risks and reasoning
        response_data = eval(response_json)  # Convert JSON string to Python object
        risks = [{"name": risk["name"], "severity": risk["severity"], "description": risk["description"], "mitigation": risk["mitigation"]} for risk in response_data]
        
        reasoning = "\n".join([risk.get("reasoning") for risk in response_data])  # Collect reasoning for actions
        
        return risks, reasoning

    def suggest_actions(self, reasoning):
        # Generate action suggestions based on reasoning
        action_template = """
        Based on the following reasoning about potential risks:

        {reasoning}

        Suggest immediate actions to mitigate these risks.
        
        Format the output as a list of actionable items.
        """
        
        prompt = PromptTemplate(template=action_template, input_variables=["reasoning"])
        llm_chain = LLMChain(prompt=prompt, llm=self.llm)

        actions_json = llm_chain.run({"reasoning": reasoning})
        
        return eval(actions_json)  # Convert JSON string to Python list of actions

    # Other methods remain unchanged...