from agents.base_agent import BaseAgent
from config import ZMQ_PUBSUB_PORT, AGENT_PORTS
import logging

class ReportingAgent(BaseAgent):
    def __init__(self):
        super().__init__("reporting", ZMQ_PUBSUB_PORT, ["log_risks"], AGENT_PORTS["reporting"])
        logging.basicConfig(filename='risk_log.txt', level=logging.INFO)

    def process_message(self, message):
        if message.action == "log_risks":
            self.log_risks(message.data)

    def log_risks(self, risks):
        for risk in risks:
            logging.info(f"Risk detected: {risk['name']} - {risk['description']}")