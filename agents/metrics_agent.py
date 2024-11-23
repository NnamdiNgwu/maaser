from agents.base_agent import BaseAgent
from config import JUICE_SHOP_URL, JUICE_SHOP_API_KEY, ZMQ_PUBSUB_PORT, AGENT_PORTS
import requests

class MetricsAgent(BaseAgent):
    def __init__(self):
        super().__init__("metrics", ZMQ_PUBSUB_PORT, ["collect_metrics"], AGENT_PORTS["metrics"])

    def process_message(self, message):
        if message.action == "collect_metrics":
            metrics = self.collect_metrics()
            #self.send_message("analysis", "analyze_metrics", metrics)

            # Adjust prompt dynamically based on previous metrics or context if necessary
            if metrics['failed_logins'] > 10:
                context_info = "High failed login attempts detected."
            else:
                context_info = "Normal login activity."
                
            self.send_message("analysis", "analyze_metrics", {"metrics": metrics, "context_info": context_info})


    def collect_metrics(self):
        # Implement actual metrics collection from Juice Shop
        return {
            "failed_logins": 5,
            "sql_injection_attempts": 2,
            "xss_submissions": 1,
            "api_requests": 80,
            "data_accesses": 30
        }