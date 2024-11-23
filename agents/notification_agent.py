from agents.base_agent import BaseAgent
from config import ZMQ_PUBSUB_PORT, AGENT_PORTS



class NotificationAgent(BaseAgent):
    def __init__(self):
        super().__init__("notification", ZMQ_PUBSUB_PORT, ["notify_risks"], AGENT_PORTS["notification"])

    def process_message(self, message):
        if message.action == "notify_risks":
            self.send_notifications(message.data)

    def send_notifications(self, risks):
        for risk in risks:
            print(f"ALERT: {risk['name']} - {risk['description']}")
        # Implement actual notification logic (e.g., email, SMS)