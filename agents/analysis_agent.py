from agents.base_agent import BaseAgent
from config import OPENAI_API_KEY, ZMQ_PUBSUB_PORT, AGENT_PORTS
from langchain import PromptTemplate, LLMChain
from langchain.llms import OpenAI


class AnalysisAgent(BaseAgent):
    def __init__(self):
        super().__init__("analysis", ZMQ_PUBSUB_PORT,
                         ["analyze_metrics", "update_knowledge", "aupdate_vulnerability_knowledge", "penetest_results"], 
                         AGENT_PORTS["analysis"])
        self.llm = OpenAI(api_key=OPENAI_API_KEY, temperature=0.7)
        self.knowledge_base = ""
        self.vulnerability_knowledge_base = ""
        # self.vulnerability_knowledge_base = []
        self.penetest_results = []

    def process_message(self, message):
        if message.action == "analyze_metrics":
            risks = self.analyze_risks(message.data)
            self.send_message("notification", "notify_risks", risks)
            self.send_message("reporting", "log_risks", risks)
            # Suggest actions based on reasoning
            # actions = self.suggest_actions(reasoning)
            # self.send_message("notification", "suggest_actions", actions)
        elif message.action == "update_knowledge":
            self.update_vulnerability_knowledge(message.data["results"])
        elif message.action == "pentest_results":
            self.update_penetest_results(message.data["results"])
            self.compare_kri_and_penetest()


    def update_knowledge(self, docs):
        self.knowledge_base = "\n".join(docs)

    
    def update_vulnerability_knowledge(self, results):
        self.vulnerability_knowledge_base = results

    def update_penetest_results(self, results):
        self.penetest_results = results

    def analyze_risks(self, metrics):
        template = """
         Given the following web service metrics, security knowledge, and 
         known vulnerabilities:

         Metrics:
         {metrics}

         Security Knowledge:
         {knowledge_base}

         Known Vulnerabilities:
         {vulnerabilities}

         Analyze the metrics and identify potential risks. For each risk, provide
         1. Risk name
         2. Severity (Low, Medium, High)
         3. Description
         4. Recommended mitigation steps

         Format the output as a JSON list of risk objects.
        """

        prompt = PromptTemplate(template=template, input_variables=
                ["metrics", "knowledge_base", "vulnerabilities"])
        llm_chain = LLMChain(prompt=prompt, llm=self.llm)

        vulnerabilities_str = "\n".join([f"{v['cve_id']}:
         {v['description']}" for v in self.vulnerability_knowledge])
        risk_json = llm_chain.run({"metrics": metrics, 
            "knowledge_base": self.knowledge_base, 
            "vulnerabilities": vulnerabilities_str})
        return eval(risk_json) # Convert the JSON string to a Python list of dictionary
    

    def compare_kri_and_penetest(self):
        template = """
         Compare the following key Risk Indicators (KRI) detected from system
         logs and penetration testing results:

         KRI from system logs:
         {kri_logs}

         Penetration testing results:
         {penetest_results}

         Provide an analysis of the comparison, highlighting:
         1. Consistencies between KRI and penetration testing findings
         2. Discrepancies or potential blind spots in either approach
         3. Recommendations for improving overall risk detection and assessment

         Format the output as a JSON object with 'consistencies', 'discrepancies',
         and 'recommendations' keys.
        """
        prompt = PromptTemplate(template=template, input_variables=
                ["kri_logs", "penetest_results"])
        llm_chain = LLMChain(prompt=prompt, llm=self.llm)

        kri_logs_str = "\n".join([f"{risk['name']}:
         {risk['description']}" for risk in self.analyze_risks({})])
        pentest_results_str = "\n".join([f"{result['name']}:
         {result['description']}" for result in self.penetest_results])
        
        comparison_json = llm_chain.run({"kri_logs": kri_logs_str, 
            "penetest_results": pentest_results_str})
        comparison = eval(comparison_json)

        self.send_message("reporting", "log_comparison", {"comparison": comparison})

        