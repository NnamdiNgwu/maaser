import multiprocessing
from agents.metrics_agent import MetricsAgent
from agents.analysis_agent import AnalysisAgent
from agents.notification_agent import NotificationAgent
from agents.reporting_agent import ReportingAgent
from agents.documentation_agent import DocumentationAgent
from agents.report_generation_agent import ReportGenerationAgent
from utils.zmq_utils import create_publisher, create_rep_socket
from config import ZMQ_PUBSUB_PORT, ZMQ_COORDINATOR_PORT
import time

def start_agent(agent_class):
    agent = agent_class()
    agent.run()

def coordinator():
    pub_socket = create_publisher(ZMQ_PUBSUB_PORT)
    rep_socket = create_rep_socket(ZMQ_COORDINATOR_PORT)

    while True:
        message = rep_socket.recv_json()
        pub_socket.send_string(message['receiver'], flags=zmq.SNDMORE)
        pub_socket.send_json(message)
        rep_socket.send_string("ACK")

        if message['action'] == 'collect_metrics':
            time.sleep(60)  # Wait for 60 seconds before next metrics collection

if __name__ == "__main__":
    processes = []
    
    for agent_class in [MetricsAgent, AnalysisAgent, NotificationAgent, ReportingAgent, DocumentationAgent, ReportGenerationAgent]:
        p = multiprocessing.Process(target=start_agent, args=(agent_class,))
        processes.append(p)
        p.start()

    coordinator_process = multiprocessing.Process(target=coordinator)
    coordinator_process.start()

    # Start the monitoring loop
    while True:
        time.sleep(60)
        pub_socket = create_publisher(ZMQ_PUBSUB_PORT)
        pub_socket.send_string("metrics", flags=zmq.SNDMORE)
        pub_socket.send_json({"action": "collect_metrics", "data": {}})

        # Scrape documentation every 24 hours
        if time.time() % (24 * 60 * 60) < 60:
            pub_socket.send_string("documentation", flags=zmq.SNDMORE)
            pub_socket.send_json({"action": "scrape_docs", "data": {}})

        # Generate report every 6 hours
        if time.time() % (6 * 60 * 60) < 60:
            pub_socket.send_string("report_generation", flags=zmq.SNDMORE)
            pub_socket.send_json({"action": "generate_report", "data": {"metrics": {}, "risks": []}})

    for p in processes:
        p.join()
    coordinator_process.join()