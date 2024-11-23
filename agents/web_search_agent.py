from agents.base_agent import BaseAgent
from config import ZMQ_PUBSUB_PORT, AGENT_PORTS
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import requests


class WebSearchAgent(BaseAgent):
    def __init__(self):
        """
        Initialize the WebSearchAgent.

        This function initializes the WebSearchAgent by calling the constructor of the BaseAgent class.
        It also sets up a headless Chrome driver for web scraping.

        Parameters:
        None

        Returns:
        None
        """
        super().__init__("WebSearchAgent", ZMQ_PUBSUB_PORT,
                         ["search_vulnerabilities"], AGENT_PORTS["web_search"])
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        self.driver = webdriver.Chrome(options=chrome_options)


    def process_message(self, message):
        """
        Processes incoming messages and performs actions based on the message content.

        This function checks the action in the incoming message and performs the corresponding action.
        If the action is "search_vulnerabilities", it calls the search_vulnerabilities function with the query from the message data,
        and sends an update_vulnerability_knowledge message to the "analysis" agent with the search results.

        Parameters:
        message (object): The incoming message containing the action and data.

        Returns:
        None
        """
        if message.action == "search_vulnerabilities":
            results = self.search_vulnerabilities(message.data["query"])
            self.send_message("analysis", "update_vulnerability_knowledge", {"results": results})


    def search_vulnerabilities(self, querry):
        """
        Performs a web search for vulnerabilities using the provided query.

        This function uses a headless Chrome driver to navigate to the CVE Mitre website and search for vulnerabilities based on the given query.
        It then parses the search results using BeautifulSoup and extracts the CVE ID and vulnerability description for each result.

        Parameters:
        querry (str): The search query for vulnerabilities.

        Returns:
        list: A list of dictionaries, where each dictionary contains the "cve_id" and "description" of a vulnerability.
        """
        self.driver.get(f"https://cve.mitre.org/cgi-bin/cvekey.cgi?keyword={querry}")
        soup = BeautifulSoup(self.driver.page_source, "html.parser")
        results = []
        for item in soup.find_all('div', class_='row'):
            cve_id = item.find('a', href=True).text
            description = item.find('td', attrs={'nowrap': 'nowrap'}).text
            results.append({"cve_id": cve_id, "description": description})
        return results

    def __del__(self):
        self.driver.quit()    