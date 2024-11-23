from agents.base_agent import BaseAgent
from config import ZMQ_PUBSUB_PORT, AGENT_PORTS
from zapv2 import ZAPv2


class PenetrationTestingAgent(BaseAgent):
    def __init__(self):
        super().__init__("PenetrationTestingAgent", ZMQ_PUBSUB_PORT,
                         ["run_pentest"], AGENT_PORTS["penetration_testing"])
        self.zap = ZAPv2()

    
    def process_message(self, message):
        if message.action == "run_pentest":
           result = self.run_pentest(message.data["target_url"])
           self.send_message("analysis", "pentest_results", {"results": result})


    def run_pentest(self, target_url):
        self.zap.urlopen(target_url)
        self.zap.spider.scan(target_url)
        self.zap.active_scan.scan(target_url)

        alerts = self.zap.core.alerts()
        return [{"risk": alert["risk"], "name": alert["name"],
                  "description": alert["description"]} for alert in alerts]